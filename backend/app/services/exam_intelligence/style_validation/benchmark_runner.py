"""Benchmark runner — validate all Style Contracts (no LLM)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.services.exam_intelligence.style_learning.style_similarity import (
    style_similarity,
)
from app.services.exam_intelligence.style_validation.bloom_validator import (
    validate_bloom,
    validate_bloom_batch,
)
from app.services.exam_intelligence.style_validation.cluster_validator import (
    validate_clusters,
)
from app.services.exam_intelligence.style_validation.contract_validator import (
    validate_contract,
)
from app.services.exam_intelligence.style_validation.difficulty_validator import (
    validate_difficulty_batch,
    validate_difficulty_curve,
)
from app.services.exam_intelligence.style_validation.quality_score import score_contract
from app.services.exam_intelligence.style_validation.reading_validator import (
    validate_reading,
    validate_reading_batch,
)
from app.services.exam_intelligence.style_validation.reasoning_validator import (
    validate_reasoning,
    validate_reasoning_batch,
)
from app.services.exam_intelligence.style_validation.similarity_validator import (
    validate_similarity,
)
from app.services.exam_intelligence.style_validation.trap_validator import (
    validate_trap,
    validate_trap_batch,
)
from app.services.exam_intelligence.style_validation.validation_report import (
    build_markdown_report,
)

EXAMS = (
    "kpss",
    "tyt",
    "ayt",
    "ales",
    "yds",
    "yokdil",
    "lgs",
    "ags",
    "dgs",
    "ydt",
)


class BenchmarkRunner:
    def __init__(self, data_root: Path | str) -> None:
        self.data_root = Path(data_root)
        self.contracts_root = self.data_root / "exam_style_contracts"
        self.out_root = self.data_root / "style_validation"

    def _load_contracts(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        if not self.contracts_root.exists():
            return rows
        for path in sorted(self.contracts_root.rglob("style_contract.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                data["_path"] = str(path)
                rows.append(data)
        return rows

    def _write(self, name: str, payload: Any) -> Path:
        self.out_root.mkdir(parents=True, exist_ok=True)
        path = self.out_root / name
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        return path

    def run(self) -> dict[str, Any]:
        contracts = self._load_contracts()
        by_topic = {
            str(c.get("topic_code")): c
            for c in contracts
            if c.get("topic_code")
        }

        contract_rows = [validate_contract(c) for c in contracts]
        contract_failures = [r for r in contract_rows if not r["passed"]]

        similarity_report = validate_similarity(by_topic, style_similarity)
        cluster_report = validate_clusters(contracts)
        difficulty_report = validate_difficulty_batch(contracts)
        reasoning_report = validate_reasoning_batch(contracts)
        trap_report = validate_trap_batch(contracts)
        reading_report = validate_reading_batch(contracts)
        bloom_report = validate_bloom_batch(contracts)

        sim_pass_rate = (
            (similarity_report["passed"] / similarity_report["tested"])
            if similarity_report.get("tested")
            else 0.0
        )

        scored: list[dict[str, Any]] = []
        warning_lines: list[str] = []
        for c in contracts:
            c_res = validate_contract(c)
            r_res = validate_reading(c)
            reason_res = validate_reasoning(c)
            t_res = validate_trap(c)
            d_res = validate_difficulty_curve(c)
            b_res = validate_bloom(c)
            row = score_contract(
                c,
                contract_result=c_res,
                reading_result=r_res,
                reasoning_result=reason_res,
                trap_result=t_res,
                difficulty_result=d_res,
                bloom_result=b_res,
                similarity_bonus=sim_pass_rate,
            )
            scored.append(row)
            for src, res in (
                ("reading", r_res),
                ("reasoning", reason_res),
                ("trap", t_res),
                ("difficulty", d_res),
                ("bloom", b_res),
            ):
                for w in res.get("warnings") or []:
                    warning_lines.append(f"{c.get('topic_code')}: [{src}] {w}")
                for issue in res.get("issues") or []:
                    warning_lines.append(f"{c.get('topic_code')}: [{src}] FAIL {issue}")

        for issue in cluster_report.get("issues") or []:
            warning_lines.append(f"cluster: {issue}")
        for u in similarity_report.get("unexpected") or []:
            warning_lines.append(f"similarity: unexpected {u}")

        by_exam: dict[str, dict[str, Any]] = {}
        exam_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in scored:
            exam_groups[str(row.get("exam_code") or "unknown").lower()].append(row)

        exam_warnings: dict[str, int] = defaultdict(int)
        for line in warning_lines:
            for exam in EXAMS:
                if line.lower().startswith(exam) or f"_{exam}_" in line or line.startswith(f"{exam}_"):
                    exam_warnings[exam] += 1

        for exam in EXAMS:
            rows = exam_groups.get(exam, [])
            if not rows:
                by_exam[exam] = {
                    "mean_score": 0,
                    "count": 0,
                    "warnings": exam_warnings.get(exam, 0),
                    "present": False,
                }
                continue
            mean = round(sum(r["score"] for r in rows) / len(rows), 1)
            by_exam[exam] = {
                "mean_score": mean,
                "count": len(rows),
                "warnings": exam_warnings.get(exam, 0),
                "present": True,
                "best": max(rows, key=lambda r: r["score"]),
                "worst": min(rows, key=lambda r: r["score"]),
            }

        scored_sorted = sorted(scored, key=lambda r: r["score"], reverse=True)
        mean_score = round(
            sum(r["score"] for r in scored) / max(len(scored), 1), 1
        )
        quality_scores = {
            "mean_score": mean_score,
            "best_contract": scored_sorted[0] if scored_sorted else {},
            "worst_contract": scored_sorted[-1] if scored_sorted else {},
            "by_exam": by_exam,
            "contracts": scored_sorted,
        }

        hard_failures = (
            len(contract_failures)
            + difficulty_report.get("failed", 0)
            + bloom_report.get("failed", 0)
            + reading_report.get("failed", 0)
            + reasoning_report.get("failed", 0)
            + trap_report.get("failed", 0)
            + (0 if similarity_report.get("passed_all") else 1)
            + (0 if cluster_report.get("passed") else 1)
        )

        suggestions: list[str] = []
        if contract_failures:
            suggestions.append("Fix missing Style Contract fields before M28.")
        if not similarity_report.get("passed_all"):
            suggestions.append("Review unexpected similarity pairs; adjust Style Learning clustering if needed.")
        if cluster_report.get("issues"):
            suggestions.append("Inspect misclustered reading/reasoning topics.")
        if mean_score < 70:
            suggestions.append("Mean quality < 70 — strengthen weak analyzers before Question Author AI.")
        if not suggestions:
            suggestions.append("Style layer looks healthy — safe to proceed to M28 Question Author AI.")

        m28_ready = (
            len(contract_failures) == 0
            and similarity_report.get("passed_all", False)
            and cluster_report.get("passed", False)
            and difficulty_report.get("passed", False)
            and bloom_report.get("passed", False)
            and reading_report.get("passed", False)
            and reasoning_report.get("passed", False)
            and trap_report.get("passed", False)
            and mean_score >= 70
            and len(contracts) > 0
        )

        summary = {
            "style_version": "m27_6_v1",
            "contracts_checked": len(contracts),
            "contract_failures": len(contract_failures),
            "hard_failures": hard_failures,
            "m28_ready": m28_ready,
            "mean_quality_score": mean_score,
            "exams_present": sorted(e for e, v in by_exam.items() if v.get("present")),
            "exams_missing": sorted(e for e, v in by_exam.items() if not v.get("present")),
        }

        payload = {
            "summary": summary,
            "quality_scores": quality_scores,
            "similarity_report": similarity_report,
            "cluster_report": cluster_report,
            "difficulty_report": difficulty_report,
            "warnings": warning_lines,
            "suggestions": suggestions,
            "reasoning_report": {
                "failed": reasoning_report.get("failed"),
                "warned": reasoning_report.get("warned"),
                "passed": reasoning_report.get("passed"),
            },
            "trap_report": {
                "failed": trap_report.get("failed"),
                "warned": trap_report.get("warned"),
                "passed": trap_report.get("passed"),
            },
            "reading_report": {
                "failed": reading_report.get("failed"),
                "warned": reading_report.get("warned"),
                "passed": reading_report.get("passed"),
            },
            "bloom_report": {
                "failed": bloom_report.get("failed"),
                "warned": bloom_report.get("warned"),
                "passed": bloom_report.get("passed"),
                "avg_sum": bloom_report.get("avg_sum"),
            },
        }

        written = {
            "summary": str(self._write("summary.json", summary)),
            "quality_scores": str(self._write("quality_scores.json", quality_scores)),
            "cluster_report": str(self._write("cluster_report.json", cluster_report)),
            "similarity_report": str(
                self._write("similarity_report.json", similarity_report)
            ),
            "difficulty_report": str(
                self._write("difficulty_report.json", difficulty_report)
            ),
            "warnings": str(
                self._write("warnings.json", {"count": len(warning_lines), "warnings": warning_lines})
            ),
            "validation_md": str(
                self._write("validation.md", build_markdown_report(payload))
            ),
        }
        summary["artifacts"] = written
        self._write("summary.json", summary)
        return {
            "summary": summary,
            "quality_scores": quality_scores,
            "similarity_report": similarity_report,
            "cluster_report": cluster_report,
            "m28_ready": m28_ready,
            "artifacts": written,
        }
