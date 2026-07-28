"""End-to-end Official Exam Intelligence pipeline (M27)."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from app.services.exam_intelligence.parser.answer_key_locator import extract_answer_key
from app.services.exam_intelligence.parser.difficulty_estimator import estimate_difficulty
from app.services.exam_intelligence.parser.layout_analyzer import analyze_layout
from app.services.exam_intelligence.parser.metadata_writer import (
    write_metadata,
    write_report,
    write_style_profile,
    write_style_stats,
)
from app.services.exam_intelligence.parser.page_reader import infer_identity
from app.services.exam_intelligence.parser.pdf_loader import load_pdf
from app.services.exam_intelligence.parser.question_locator import (
    locate_questions,
)
from app.services.exam_intelligence.parser.reading_estimator import (
    estimate_reading_time_sec,
)
from app.services.exam_intelligence.parser.style_dna_builder import build_style_dna
from app.services.exam_intelligence.parser.style_extractor import build_style_stats
from app.services.exam_intelligence.parser.subject_detector import (
    detect_subject_topic,
    detect_subjects_from_pages,
)
from app.services.exam_intelligence.parser.topic_detector import (
    assign_blueprint,
    expected_question_count,
    subject_order_for_exam,
)
from app.services.exam_intelligence.parser.types import ParseResult, QuestionMeta
from app.services.exam_intelligence.parser.validation import validate_result


def _ensure_question_coverage(
    located: list,
    *,
    exam_code: str,
    answer_key: dict[str, str],
    expected: int | None,
    text_weak: bool,
) -> list:
    """Fill 1..N shells so booklet size matches catalog / answer key."""
    from app.services.exam_intelligence.parser.question_locator import LocatedQuestion

    by_num = {q.number: q for q in located}
    max_located = max(by_num) if by_num else 0
    key_nums = [int(k) for k in answer_key if str(k).isdigit()]
    max_key = max(key_nums) if key_nums else 0
    exam = (exam_code or "").lower()
    fixed = exam in {"tyt", "ydt", "yds", "yokdil", "dgs", "ags"}

    target = 0
    if expected and fixed:
        target = expected
        if max_key >= int(expected * 0.85) and len(key_nums) >= int(expected * 0.85):
            target = max(target, max_key)
    elif expected:
        # Variable booklet exams (KPSS / ALES / LGS / AYT): prefer observed size
        if max_located >= 15:
            target = max_located
            if max_key >= max_located and len(key_nums) >= int(max_located * 0.8):
                target = max_key
        elif max_key >= 15:
            target = max_key
        elif text_weak:
            target = expected
        else:
            target = max_located or expected
    elif max_key >= 10:
        target = max_key
    elif max_located:
        target = max_located

    if target <= 0:
        return located

    if len(by_num) >= int(target * 0.95) and max_located >= target - 1:
        return [by_num[n] for n in sorted(by_num) if n <= target]

    out: list[LocatedQuestion] = []
    for num in range(1, target + 1):
        if num in by_num:
            out.append(by_num[num])
        else:
            out.append(
                LocatedQuestion(
                    number=num,
                    page=None,
                    _transient_text="",
                    word_count=0,
                    sentence_count=0,
                    option_lengths=[],
                    symbol_count=0,
                    equation_count=0,
                    has_table=False,
                    has_visual_hint=False,
                    multi_step=False,
                )
            )
    return out


class ExamIntelligencePipeline:
    def __init__(self, data_root: Path | str) -> None:
        self.data_root = Path(data_root)
        self.exams_root = self.data_root / "official_exams"

    def discover_pdfs(self) -> list[Path]:
        if not self.exams_root.exists():
            return []
        return sorted(self.exams_root.rglob("*.pdf"))

    def parse_pdf(self, pdf_path: Path) -> ParseResult:
        loaded = load_pdf(pdf_path)
        identity = infer_identity(pdf_path, repo_root=self.data_root.parent)

        located = locate_questions(loaded.pages)
        answer_key = extract_answer_key(loaded.pages)
        extractable_chars = sum(len(p or "") for p in loaded.pages)
        text_weak = extractable_chars < 500

        # Prefer answer-key cardinality / catalog size when locator is weak
        expected = expected_question_count(identity.exam_code, identity.pack)
        located = _ensure_question_coverage(
            located,
            exam_code=identity.exam_code,
            answer_key=answer_key,
            expected=expected,
            text_weak=text_weak,
        )

        layout = analyze_layout(loaded.pages, located)
        subject_order = detect_subjects_from_pages(identity.exam_code, loaded.pages)
        if not subject_order:
            subject_order = subject_order_for_exam(identity.exam_code, identity.pack)

        questions: list[QuestionMeta] = []
        subject_dist: dict[str, int] = defaultdict(int)
        topic_dist: dict[str, int] = defaultdict(int)
        skill_dist: dict[str, int] = defaultdict(int)
        q_total = len(located)

        for loc in located:
            det = detect_subject_topic(identity.exam_code, loc._transient_text)
            bp = assign_blueprint(
                identity.exam_code,
                loc.number,
                pack=identity.pack,
                question_count=q_total,
            )
            prefer_blueprint = bool(
                bp
                and (
                    not det.subject_code
                    or det.confidence < 0.35
                    or loc.word_count < 25
                    or text_weak
                )
            )
            if prefer_blueprint and bp:
                subject_code = bp.subject_code
                topic_code = bp.topic_code
                conf = bp.confidence
                skill = bp.skill_type
            else:
                subject_code = det.subject_code
                topic_code = det.topic_code
                conf = det.confidence
                skill = det.skill_type
                if (
                    bp
                    and not topic_code
                    and subject_code
                    and bp.subject_code == subject_code
                ):
                    topic_code = bp.topic_code
                    conf = max(conf, bp.confidence * 0.8)
                elif bp and not subject_code:
                    subject_code = bp.subject_code
                    topic_code = bp.topic_code
                    conf = bp.confidence
                    skill = bp.skill_type

            diff = estimate_difficulty(loc)
            read_sec = estimate_reading_time_sec(loc)
            # Shell questions: use catalog-ish defaults so DNA is usable
            if loc.word_count == 0 and bp:
                read_sec = max(read_sec, 18 if "paragraf" in (topic_code or "") else 12)
                diff = max(diff, 55 if skill == "problem_solving" else 48)

            opt_avg = (
                sum(loc.option_lengths) / len(loc.option_lengths)
                if loc.option_lengths
                else 0.0
            )
            qm = QuestionMeta(
                number=loc.number,
                subject_code=subject_code,
                topic_code=topic_code,
                topic_confidence=conf,
                page=loc.page,
                estimated_reading_length_words=loc.word_count,
                estimated_reading_time_sec=read_sec,
                estimated_difficulty=diff,
                skill_type=skill,
                sentence_count=loc.sentence_count,
                option_length_avg=round(opt_avg, 2),
                symbol_count=loc.symbol_count,
                equation_count=loc.equation_count,
                has_table=loc.has_table,
                has_visual_hint=loc.has_visual_hint,
                multi_step=loc.multi_step,
            )
            questions.append(qm)
            if subject_code:
                subject_dist[subject_code] += 1
            if topic_code:
                topic_dist[topic_code] += 1
            skill_dist[skill] += 1
            # Clear reference to help GC (defensive)
            loc._transient_text = ""

        n = max(len(questions), 1)
        skill_ratio = {k: round(v / n, 3) for k, v in skill_dist.items()}
        easy = sum(1 for q in questions if q.estimated_difficulty < 45) / n
        med = sum(1 for q in questions if 45 <= q.estimated_difficulty < 70) / n
        hard = sum(1 for q in questions if q.estimated_difficulty >= 70) / n
        read_avg = (
            sum(q.estimated_reading_time_sec for q in questions) / n if questions else 0.0
        )

        topic_order: list[str] = []
        for q in questions:
            if q.topic_code and q.topic_code not in topic_order:
                topic_order.append(q.topic_code)

        result = ParseResult(
            exam_code=identity.exam_code,
            year=identity.year,
            language=identity.language,
            page_count=loaded.page_count,
            question_count=len(questions),
            answer_key=answer_key,
            duration_minutes=identity.duration_minutes,
            booklet_type=identity.booklet_type,
            pack=identity.pack,
            session_id=identity.session_id,
            source_pdf=identity.relative_source,
            subject_order=subject_order or list(subject_dist.keys()),
            topic_order=topic_order,
            subject_distribution=dict(subject_dist),
            topic_distribution=dict(topic_dist),
            skill_distribution=skill_ratio,
            difficulty_estimation={
                "easy": round(easy, 3),
                "medium": round(med, 3),
                "hard": round(hard, 3),
            },
            reading_time_sec_avg=round(read_avg, 1),
            questions=questions,
            layout=layout,
        )
        result.validation = validate_result(result)
        if text_weak:
            issues = list(result.validation.get("issues") or [])
            if "text_extract_weak" not in issues:
                issues.append("text_extract_weak")
            result.validation["issues"] = issues
            if not questions:
                result.validation["passed"] = False
        result.report_lines = self._build_report(result)
        return result

    def _build_report(self, r: ParseResult) -> list[str]:
        label = f"{r.year or '?'} {r.exam_code.upper()}"
        if r.pack:
            label += f" ({r.pack})"
        lines = [
            label,
            f"{r.question_count} question",
            f"{len(r.answer_key)} answer key",
            f"{len(r.subject_distribution)} subjects",
            f"{len(r.topic_distribution)} topics",
            f"Difficulty avg {round(sum(q.estimated_difficulty for q in r.questions) / max(len(r.questions), 1), 1)}",
            f"Paragraph avg {r.layout.paragraph_length_avg} words",
            f"Reading avg {r.reading_time_sec_avg} sec",
            "Style Profile Generated",
            "Metadata OK" if r.validation.get("passed") else "Metadata WARNINGS",
        ]
        if r.validation.get("issues"):
            lines.append("Issues: " + ", ".join(r.validation["issues"]))
        return lines

    def write_result(self, result: ParseResult) -> dict[str, Any]:
        meta_path = write_metadata(self.data_root, result)
        stats_map = build_style_stats(result)
        stats_paths = write_style_stats(self.data_root, result.exam_code, stats_map)
        report_path = write_report(self.data_root, result)
        return {
            "metadata": str(meta_path),
            "stats": [str(p) for p in stats_paths],
            "report": str(report_path),
        }

    def run_all(self, *, limit: int | None = None) -> dict[str, Any]:
        pdfs = self.discover_pdfs()
        if limit is not None:
            pdfs = pdfs[:limit]
        results: list[ParseResult] = []
        written: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []

        for pdf in pdfs:
            try:
                result = self.parse_pdf(pdf)
                paths = self.write_result(result)
                results.append(result)
                written.append({"pdf": str(pdf), **paths, "exam": result.exam_code})
                print("\n".join(result.report_lines))
                print("---")
            except Exception as e:
                errors.append({"pdf": str(pdf), "error": str(e)[:400]})
                print(f"FAIL {pdf.name}: {e}")

        # Aggregate Style DNA per exam
        exams = sorted({r.exam_code for r in results})
        dna_paths: list[str] = []
        for exam in exams:
            dna = build_style_dna(results, exam)
            dna_paths.append(str(write_style_profile(self.data_root, exam, dna)))

        return {
            "parsed": len(results),
            "failed": len(errors),
            "errors": errors,
            "written": written,
            "style_profiles": dna_paths,
        }
