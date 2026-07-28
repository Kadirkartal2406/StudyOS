"""Exam Style Learning Engine — M27.5 orchestration (no LLM, no stems)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.services.exam_intelligence.style_learning.bloom_distribution import (
    build_bloom_distribution,
)
from app.services.exam_intelligence.style_learning.difficulty_curve_builder import (
    build_difficulty_curve,
)
from app.services.exam_intelligence.style_learning.question_intent_analyzer import (
    analyze_question_intent,
)
from app.services.exam_intelligence.style_learning.reading_load_analyzer import (
    analyze_reading_load,
)
from app.services.exam_intelligence.style_learning.reasoning_pattern_analyzer import (
    analyze_reasoning,
)
from app.services.exam_intelligence.style_learning.style_cluster import cluster_topics
from app.services.exam_intelligence.style_learning.style_profile_builder import (
    build_topic_contract,
)
from app.services.exam_intelligence.style_learning.style_similarity import (
    style_similarity,
)
from app.services.exam_intelligence.style_learning.trap_pattern_analyzer import (
    analyze_trap_patterns,
)
from app.services.exam_intelligence.style_learning.types import FORBIDDEN_FIELDS


class StyleLearningEngine:
    def __init__(self, data_root: Path | str) -> None:
        self.data_root = Path(data_root)
        self.meta_root = self.data_root / "parsed_metadata"
        self.stats_root = self.data_root / "exam_style_stats"
        self.dna_root = self.data_root / "exam_style_profiles"
        self.contracts_root = self.data_root / "exam_style_contracts"
        self.learned_root = self.data_root / "exam_style_profiles_learned"

    def _assert_safe(self, obj: Any, path: str = "$") -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                lk = str(k).lower()
                if lk in FORBIDDEN_FIELDS or "stem" in lk:
                    raise ValueError(f"Forbidden field: {path}.{k}")
                self._assert_safe(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                self._assert_safe(v, f"{path}[{i}]")

    def _write_json(self, path: Path, data: dict[str, Any]) -> Path:
        self._assert_safe(data)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    def _load_dna(self) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        if not self.dna_root.exists():
            return out
        for p in self.dna_root.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            code = str(data.get("exam_code") or p.stem).lower()
            out[code] = data
        return out

    def _load_stats(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        if not self.stats_root.exists():
            return rows
        for p in self.stats_root.rglob("stats.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if data.get("exam_code") and data.get("topic_code"):
                rows.append(data)
        return rows

    def _load_metadata_index(self) -> dict[str, list[dict[str, Any]]]:
        """exam_code → list of session metadata dicts."""
        by_exam: dict[str, list[dict[str, Any]]] = defaultdict(list)
        if not self.meta_root.exists():
            return by_exam
        for p in self.meta_root.rglob("*.json"):
            if p.name.startswith("_") or "schema" in p.name:
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            exam = str(data.get("exam_code") or "").lower()
            if exam:
                by_exam[exam].append(data)
        return by_exam

    def _topic_questions(
        self,
        sessions: list[dict[str, Any]],
        topic_code: str,
    ) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for s in sessions:
            for q in s.get("questions") or []:
                if isinstance(q, dict) and q.get("topic_code") == topic_code:
                    # Strip anything except numeric/heuristic fields
                    out.append(
                        {
                            "number": q.get("number"),
                            "estimated_difficulty": q.get("estimated_difficulty"),
                            "estimated_reading_time_sec": q.get(
                                "estimated_reading_time_sec"
                            ),
                            "skill_type": q.get("skill_type"),
                        }
                    )
        return out

    def learn_all(self) -> dict[str, Any]:
        dna_map = self._load_dna()
        stats_rows = self._load_stats()
        meta_index = self._load_metadata_index()

        contracts: list[dict[str, Any]] = []
        written: list[str] = []
        validation_issues: list[dict[str, Any]] = []

        for stats in stats_rows:
            exam = str(stats.get("exam_code") or "").lower()
            sessions = meta_index.get(exam, [])
            layout = (sessions[0].get("layout") if sessions else None) or {}
            topic_code = str(stats.get("topic_code") or "")
            tq = self._topic_questions(sessions, topic_code)
            contract = build_topic_contract(
                stats=stats,
                exam_dna=dna_map.get(exam),
                topic_questions=tq,
                layout=layout if isinstance(layout, dict) else {},
            )
            contracts.append(contract)
            sub = contract["subject_slug"]
            top = contract["topic_slug"]
            path = (
                self.contracts_root
                / exam
                / sub
                / top
                / "style_contract.json"
            )
            written.append(str(self._write_json(path, contract)))
            if not (contract.get("validation") or {}).get("passed", True):
                validation_issues.append(
                    {
                        "topic_code": topic_code,
                        "issues": (contract.get("validation") or {}).get("issues"),
                    }
                )

        clusters = cluster_topics(contracts)
        exam_profiles = self._build_exam_profiles(
            contracts, meta_index, dna_map, clusters
        )
        profile_paths: list[str] = []
        for exam, profile in exam_profiles.items():
            path = self.learned_root / f"{exam.upper()}.json"
            profile_paths.append(str(self._write_json(path, profile)))

        # Similarity samples for report (reading vs reasoning pairs)
        sim_samples = self._similarity_samples(contracts)

        summary = {
            "contracts_written": len(written),
            "exams": sorted(exam_profiles.keys()),
            "clusters": [
                {"cluster": c["cluster"], "size": c["size"]} for c in clusters
            ],
            "validation_failures": len(validation_issues),
            "validation_issues": validation_issues[:50],
            "similarity_samples": sim_samples,
            "style_version": "m27_5_v1",
            "notes": "No question text stored. Contracts are LLM-facing thinking specs.",
        }
        report_path = self.contracts_root / "_reports" / "style_learning_summary.json"
        self._write_json(report_path, summary)
        return summary

    def _build_exam_profiles(
        self,
        contracts: list[dict[str, Any]],
        meta_index: dict[str, list[dict[str, Any]]],
        dna_map: dict[str, dict[str, Any]],
        clusters: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        by_exam: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for c in contracts:
            by_exam[str(c.get("exam_code") or "").lower()].append(c)

        out: dict[str, dict[str, Any]] = {}
        for exam, items in by_exam.items():
            sessions = meta_index.get(exam, [])
            dna = dna_map.get(exam, {})
            all_q: list[dict[str, Any]] = []
            for s in sessions:
                for q in s.get("questions") or []:
                    if isinstance(q, dict):
                        all_q.append(
                            {
                                "number": q.get("number"),
                                "estimated_difficulty": q.get("estimated_difficulty"),
                            }
                        )
            # Aggregate reading / bloom from contracts
            if items:
                para = sum(
                    float((c.get("reading_load") or {}).get("paragraph_length") or 0)
                    for c in items
                ) / len(items)
                read = sum(
                    float(
                        (c.get("reading_load") or {}).get("average_reading_time_sec")
                        or 0
                    )
                    for c in items
                ) / len(items)
                diff = sum(
                    float((c.get("difficulty") or {}).get("avg") or 50) for c in items
                ) / len(items)
                skill = (items[0].get("language_style") or {}).get("skill_type")
            else:
                para = read = diff = 0.0
                skill = None

            reading = analyze_reading_load(
                paragraph_avg=para,
                reading_avg_sec=read,
                exam_dna=dna,
                layout=(sessions[0].get("layout") if sessions else None) or {},
            )
            reasoning = analyze_reasoning(
                exam_code=exam,
                difficulty_avg=diff,
                exam_dna=dna,
                reasoning_avg=float(dna.get("reasoning_ratio") or 0),
                multi_step_ratio=float(dna.get("multi_step_ratio") or 0),
            )
            traps = analyze_trap_patterns(
                exam_code=exam,
                distractor_style=str(dna.get("distractor_style") or "") or None,
            )
            bloom = build_bloom_distribution(
                difficulty_avg=diff,
                skill_type=skill,
                exam_dna=dna,
                reasoning_avg=float(dna.get("reasoning_ratio") or 0),
                multi_step_ratio=float(dna.get("multi_step_ratio") or 0),
            )
            intents = {
                c["topic_code"]: (c.get("intent") or {}).get("intents")
                for c in items
                if c.get("topic_code")
            }
            exam_clusters = [
                c
                for c in clusters
                if any(m.get("exam_code") == exam for m in c.get("members") or [])
            ]
            out[exam] = {
                "exam_code": exam,
                "name": exam.upper(),
                "style_version": "m27_5_v1",
                "source": "m27_5_style_learning",
                "topic_count": len(items),
                "reading_profile": reading,
                "reasoning": reasoning,
                "trap_patterns": traps,
                "bloom": bloom,
                "difficulty_curve": build_difficulty_curve(
                    all_q,
                    difficulty_estimation=(
                        sessions[0].get("difficulty_estimation") if sessions else None
                    ),
                ),
                "intents": intents,
                "clusters": [
                    {
                        "cluster": c["cluster"],
                        "size": sum(
                            1
                            for m in c.get("members") or []
                            if m.get("exam_code") == exam
                        ),
                    }
                    for c in exam_clusters
                    if sum(
                        1 for m in c.get("members") or [] if m.get("exam_code") == exam
                    )
                    > 0
                ],
                "notes": "Learned exam thinking profile. No question text.",
            }
        return out

    def _similarity_samples(
        self, contracts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        by_topic = {c["topic_code"]: c for c in contracts if c.get("topic_code")}
        pairs = [
            ("kpss_turkce__paragraf", "yds_ingilizce__reading"),
            ("kpss_turkce__paragraf", "yokdil_ingilizce__fen"),
            ("tyt_matematik__problemler", "ales_matematik__problemler"),
            ("tyt_matematik__problemler", "dgs_matematik__problemler"),
        ]
        samples: list[dict[str, Any]] = []
        for a, b in pairs:
            if a in by_topic and b in by_topic:
                samples.append(
                    {
                        "a": a,
                        "b": b,
                        "similarity": style_similarity(by_topic[a], by_topic[b]),
                    }
                )
        return samples
