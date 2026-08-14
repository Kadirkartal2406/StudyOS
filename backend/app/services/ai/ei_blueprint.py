"""
RC2 M22.2 — Exam Intelligence → Assessment Blueprint bridge.

Mevcut Assessment mantığını değiştirmez; yalnızca section plan
veri kaynağını EI Catalog metadata'sından okur.
Hard-coded blueprint'e fallback korunur.
"""

from __future__ import annotations

import math
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exam_identity import catalog_exam_and_branch
from app.services.ai.exam_question_blueprint import (
    BlueprintSection,
    ExamBlueprint,
    get_exam_blueprint,
)
from app.services.exam_catalog_service import ExamCatalogService


def _legacy_or_code(subject) -> str:
    return (subject.legacy_subject_code or subject.code or "").strip()


def _topic_legacy_or_code(topic) -> str:
    # Native exam_catalog code first (SSOT); legacy only if native missing.
    return (topic.code or topic.legacy_topic_code or "").strip()


def _flatten_packs(packs: list) -> list:
    flat: list = []
    stack = list(packs or [])
    while stack:
        p = stack.pop()
        flat.append(p)
        stack.extend(p.children or [])
    return flat


def _filter_packs_for_exam(flat_packs: list, exam_type: str, branch: str | None) -> list:
    """Filter packs by branch_key; TYT uses pack code when branch is None."""
    et = (exam_type or "").strip().lower()
    br = (branch or "").strip().lower() or None
    catalog_root, cat_br = catalog_exam_and_branch(et, br)
    br = cat_br if cat_br is not None else br

    if et == "tyt" or (catalog_root == "yks" and et == "tyt"):
        tyt_only = [p for p in flat_packs if (p.code or "").lower() == "tyt"]
        return tyt_only or flat_packs

    if br:
        branched = [p for p in flat_packs if (p.branch_key or "").lower() == br]
        if branched:
            return branched
        # YDT English: pack code ydt_ingilizce under ydt parent
        if br in {"en", "dil"}:
            en_packs = [
                p
                for p in flat_packs
                if (p.code or "").lower() in {"ydt_ingilizce", "ydt"}
                or (p.branch_key or "").lower() in {"en", "dil"}
            ]
            if en_packs:
                return en_packs
    return flat_packs


async def build_ei_blueprint(
    db: AsyncSession,
    exam_type: str,
    branch: str | None = None,
) -> ExamBlueprint | None:
    """
    EI subjects → BlueprintSection(count = round(sum avg_q)).

    Pack filtreleme: branch_key eşleşmesi; yoksa tüm aktif pack'ler.
    Konu yoksa None → caller hard-coded blueprint'e düşer.
    """
    exam = (exam_type or "").strip().lower()
    if not exam:
        return None

    catalog_root, cat_br = catalog_exam_and_branch(exam, branch)
    svc = ExamCatalogService(db)
    try:
        await svc.ensure_synced()
        tree = await svc.get_exam_tree(catalog_root)
    except Exception:
        return None

    flat_packs = _filter_packs_for_exam(
        _flatten_packs(list(tree.packs or [])), exam, branch or cat_br
    )

    # subject_code → (name, total_avg_q, topics sorted by importance)
    subject_totals: dict[str, float] = defaultdict(float)
    subject_names: dict[str, str] = {}
    subject_topics: dict[str, list[tuple[str, str, float, float]]] = defaultdict(list)

    for pack in flat_packs:
        for subj in pack.subjects or []:
            if not subj.is_active:
                continue
            sc = _legacy_or_code(subj)
            if not sc:
                continue
            subject_names[sc] = subj.name
            for topic in subj.topics or []:
                if not topic.is_active:
                    continue
                tc = _topic_legacy_or_code(topic)
                avg = float(topic.average_question_count or 0)
                imp = float(topic.importance_score or 0)
                subject_totals[sc] += avg
                subject_topics[sc].append((tc, topic.name, avg, imp))

    if not subject_totals:
        return None

    sections: list[BlueprintSection] = []
    for sc, total_avg in sorted(
        subject_totals.items(),
        key=lambda kv: subject_names.get(kv[0], kv[0]),
    ):
        count = max(1, int(round(total_avg)))
        # Cap runaway averages; hard-coded blueprint scale as soft upper bound
        count = min(count, 80)
        sections.append(BlueprintSection(subject_code=sc, count=count))

    if not sections:
        return None
    return ExamBlueprint(exam_type=exam, sections=tuple(sections))


async def build_section_plan_from_ei(
    db: AsyncSession,
    exam_type: str,
    branch: str | None = None,
) -> tuple[list[dict], int] | None:
    """
    Full section plan from EI: subjects + topic allocation by importance × avg_q.

    Returns None if catalog empty → caller uses legacy path.
    Section *counts* come from official hard blueprint when available.
    """
    exam = (exam_type or "").strip().lower()
    catalog_root, cat_br = catalog_exam_and_branch(exam, branch)
    svc = ExamCatalogService(db)
    try:
        await svc.ensure_synced()
        tree = await svc.get_exam_tree(catalog_root)
    except Exception:
        return None

    flat_packs = _filter_packs_for_exam(
        _flatten_packs(list(tree.packs or [])), exam, branch or cat_br
    )

    # Prefer official hard-coded section sizes; EI drives topic mix only.
    # Estimated topic avg_q sums must not silently override booklet quotas.
    hard_bp = get_exam_blueprint(exam, branch)
    ei_bp = await build_ei_blueprint(db, exam, branch)
    count_by_subject = {s.subject_code: s.count for s in hard_bp.sections}
    if ei_bp is not None:
        for s in ei_bp.sections:
            count_by_subject.setdefault(s.subject_code, s.count)

    sections: list[dict] = []
    total = 0
    seen: set[str] = set()

    for pack in sorted(flat_packs, key=lambda p: p.display_order):
        for subj in sorted(pack.subjects or [], key=lambda s: s.display_order):
            if not subj.is_active:
                continue
            # Prefer native subject code for blueprint match; fall back to legacy
            native = (subj.code or "").strip()
            legacy = (subj.legacy_subject_code or "").strip()
            sc = native or legacy
            if not sc or sc in seen:
                continue
            seen.add(sc)
            topics = [t for t in (subj.topics or []) if t.is_active]
            if not topics:
                continue

            # Weighted allocation by importance * avg_q
            weights = []
            for t in topics:
                w = max(
                    0.01,
                    float(t.importance_score or 0.5)
                    * float(t.average_question_count or 1.0),
                )
                weights.append(w)
            target = (
                count_by_subject.get(native)
                or count_by_subject.get(legacy)
                or count_by_subject.get(sc)
                or max(
                    1,
                    int(
                        round(
                            sum(float(t.average_question_count or 0) for t in topics)
                        )
                    ),
                )
            )
            target = max(1, min(int(target), 80))

            raw = [w / sum(weights) * target for w in weights]
            alloc_counts = [max(0, int(math.floor(x))) for x in raw]
            # Distribute remainder to highest-importance topics
            rem = target - sum(alloc_counts)
            order = sorted(
                range(len(topics)),
                key=lambda i: float(topics[i].importance_score or 0),
                reverse=True,
            )
            i = 0
            while rem > 0 and order:
                alloc_counts[order[i % len(order)]] += 1
                rem -= 1
                i += 1

            topic_meta = []
            for t, n in zip(topics, alloc_counts, strict=False):
                if n <= 0:
                    continue
                topic_meta.append(
                    {
                        "topic_code": _topic_legacy_or_code(t),
                        "topic_name": t.name,
                        "count": n,
                        "importance_score": float(t.importance_score or 0),
                        "difficulty_score": float(t.difficulty_score or 0),
                        "average_question_count": float(t.average_question_count or 0),
                    }
                )
            if not topic_meta:
                continue
            sections.append(
                {
                    "subject_code": sc,
                    "subject_name": subj.name,
                    "count": sum(tm["count"] for tm in topic_meta),
                    "topics": topic_meta,
                    "source": "exam_intelligence",
                }
            )
            total += sections[-1]["count"]

    if not sections:
        return None
    return sections, total
