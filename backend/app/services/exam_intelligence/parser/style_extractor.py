"""Build exam_style_stats aggregates — no question text."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.services.exam_intelligence.parser.types import ParseResult


def build_style_stats(result: ParseResult) -> dict[tuple[str, str], dict[str, Any]]:
    """Return map (subject_code, topic_key) → stats dict."""
    buckets: dict[tuple[str, str], list] = defaultdict(list)
    for q in result.questions:
        sub = q.subject_code or "unknown"
        topic = q.topic_code or f"{sub}__general"
        buckets[(sub, topic)].append(q)

    out: dict[tuple[str, str], dict[str, Any]] = {}
    for (sub, topic), items in buckets.items():
        n = len(items)
        para = sum(i.estimated_reading_length_words for i in items) / n
        sent = sum(i.sentence_count for i in items) / n
        diff = sum(i.estimated_difficulty for i in items) / n
        read = sum(i.estimated_reading_time_sec for i in items) / n
        opt = sum(i.option_length_avg for i in items) / n
        skills = defaultdict(int)
        for i in items:
            skills[i.skill_type] += 1
        top_skill = max(skills.items(), key=lambda x: x[1])[0] if skills else "general"
        out[(sub, topic)] = {
            "exam_code": result.exam_code,
            "subject_code": sub,
            "topic_code": topic,
            "sample_size": n,
            "paragraph_avg": round(para, 1),
            "sentence_avg": round(sent, 2),
            "difficulty_avg": round(diff, 1),
            "reading_avg": round(read, 1),
            "option_length": round(opt, 2),
            "reasoning_avg": round(
                sum(1 for i in items if i.skill_type in ("inference", "problem_solving"))
                / n,
                3,
            ),
            "distractor_pattern": "heuristic_balanced",
            "skill_type": top_skill,
            "bloom_proxy": "analyze" if diff >= 65 else ("apply" if diff >= 50 else "understand"),
            "question_flow": "mixed",
            "source": "m27_parser",
            "style_version": "m27_v1",
        }
    return out
