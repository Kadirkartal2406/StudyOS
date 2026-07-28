"""Markdown + structured validation report builders."""

from __future__ import annotations

from typing import Any


def build_markdown_report(payload: dict[str, Any]) -> str:
    summary = payload.get("summary") or {}
    scores = payload.get("quality_scores") or {}
    sim = payload.get("similarity_report") or {}
    clusters = payload.get("cluster_report") or {}
    diff = payload.get("difficulty_report") or {}
    warnings = payload.get("warnings") or []

    best = scores.get("best_contract") or {}
    worst = scores.get("worst_contract") or {}
    exam_table = scores.get("by_exam") or {}

    lines: list[str] = [
        "# StudyOS Style Validation Report (M27.6)",
        "",
        "## Summary",
        "",
        f"- Contracts checked: **{summary.get('contracts_checked', 0)}**",
        f"- Contract failures: **{summary.get('contract_failures', 0)}**",
        f"- Overall ready for M28: **{summary.get('m28_ready', False)}**",
        f"- Mean quality score: **{scores.get('mean_score', 0)}**",
        "",
        "## Exam Quality Scores",
        "",
        "| Exam | Mean Score | Contracts | Warnings |",
        "|------|------------|-----------|----------|",
    ]
    for exam, row in sorted(exam_table.items()):
        lines.append(
            f"| {exam.upper()} | {row.get('mean_score', 0)} | "
            f"{row.get('count', 0)} | {row.get('warnings', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Best / Weakest Contracts",
            "",
            f"- Best: `{best.get('topic_code')}` — **{best.get('score')}**",
            f"- Weakest: `{worst.get('topic_code')}` — **{worst.get('score')}**",
            "",
            "## Clusters",
            "",
        ]
    )
    sizes = clusters.get("cluster_sizes") or {}
    for name, size in sorted(sizes.items(), key=lambda x: -x[1]):
        lines.append(f"- `{name}`: {size}")
    if clusters.get("issues"):
        lines.append("")
        lines.append("### Cluster issues")
        for issue in clusters["issues"][:20]:
            lines.append(f"- {issue}")
    else:
        lines.append("")
        lines.append("Cluster structure: **OK**")

    lines.extend(["", "## Similarity", ""])
    for r in sim.get("results") or []:
        status = "PASS" if r.get("passed") else "WARN"
        lines.append(
            f"- [{status}] `{r.get('a')}` ↔ `{r.get('b')}` "
            f"= {r.get('score')} ({r.get('expectation')})"
        )
    for r in sim.get("relative_results") or []:
        status = "PASS" if r.get("passed") else "FAIL"
        lines.append(
            f"- [{status}] relative Δ={r.get('delta')} "
            f"{r.get('higher_pair')} ≥ {r.get('lower_pair')}"
        )
    if sim.get("relative_failures"):
        lines.append("")
        lines.append("### Relative ranking failures")
        for r in sim["relative_failures"]:
            lines.append(f"- {r}")
    if sim.get("unexpected"):
        lines.append("")
        lines.append("### Absolute band advisories")
        for r in sim["unexpected"]:
            lines.append(f"- {r}")

    lines.extend(
        [
            "",
            "## Difficulty",
            "",
            f"- Checked: {diff.get('checked', 0)}",
            f"- Failed: {diff.get('failed', 0)}",
            f"- Avg max jump: {diff.get('avg_max_jump', 0)}",
            "",
            "## Warnings (sample)",
            "",
        ]
    )
    if not warnings:
        lines.append("_No warnings._")
    else:
        for w in warnings[:40]:
            lines.append(f"- {w}")

    lines.extend(
        [
            "",
            "## Suggestions",
            "",
        ]
    )
    for s in payload.get("suggestions") or ["None"]:
        lines.append(f"- {s}")

    lines.append("")
    return "\n".join(lines)
