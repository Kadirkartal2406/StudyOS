"""Aggregate layout / style heuristics from located questions."""

from __future__ import annotations

from app.services.exam_intelligence.parser.question_locator import LocatedQuestion
from app.services.exam_intelligence.parser.types import LayoutStats


def analyze_layout(
    pages: list[str],
    questions: list[LocatedQuestion],
) -> LayoutStats:
    if not questions:
        words = sum(len((p or "").split()) for p in pages)
        ppc = (words / max(len(pages), 1)) if pages else 0.0
        return LayoutStats(words_per_page_avg=round(ppc, 1), page_layout="sparse_or_image")

    para = [q.word_count for q in questions]
    sents = [q.sentence_count for q in questions]
    opts = [o for q in questions for o in q.option_lengths]
    n = len(questions)
    table_r = sum(1 for q in questions if q.has_table) / n
    visual_r = sum(1 for q in questions if q.has_visual_hint) / n
    multi_r = sum(1 for q in questions if q.multi_step) / n
    words_pages = sum(len((p or "").split()) for p in pages) / max(len(pages), 1)

    layout = "two_column_likely" if words_pages > 350 else "single_column_or_sparse"
    return LayoutStats(
        paragraph_length_avg=round(sum(para) / n, 1),
        sentence_count_avg=round(sum(sents) / n, 2),
        option_length_avg=round(sum(opts) / max(len(opts), 1), 2) if opts else 0.0,
        page_layout=layout,
        table_usage_ratio=round(table_r, 3),
        visual_usage_ratio=round(visual_r, 3),
        multi_step_ratio=round(multi_r, 3),
        words_per_page_avg=round(words_pages, 1),
    )
