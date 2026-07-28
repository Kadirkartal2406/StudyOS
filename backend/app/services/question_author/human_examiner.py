"""M29.7 Human Examiner — ÖSYM commission-style final verdict."""

from __future__ import annotations

from typing import Any

from app.services.question_author.llm_utils import clamp_score, default_llm, parse_json_obj
from app.services.question_author.prompt_library import examiner_messages
from app.services.question_author.types import ExaminerVerdict, MIN_EXAMINER


def _heuristic_examiner(question: dict[str, Any]) -> ExaminerVerdict:
    stem = str(question.get("stem") or "")
    choices = question.get("choices") or {}
    words = len(stem.split())
    natural = 90 if 25 <= words <= 320 else (82 if words >= 18 else 68)
    balanced = 90 if len(choices) >= 4 else 60
    strong = 88 if len(choices) >= 4 else 55
    osym = min(natural, balanced, 92)
    score_parts = {
        "exam_ready": osym,
        "paragraph_natural": natural,
        "options_balanced": balanced,
        "answer_not_guessable": 86,
        "distractors_strong": strong,
        "osym_feel": osym,
    }
    verdict = ExaminerVerdict(
        **{k: clamp_score(v) for k, v in score_parts.items()},
        notes="heuristic",
    )
    verdict.accepted = verdict.score >= MIN_EXAMINER
    return verdict


async def examine_question(
    question: dict[str, Any],
    *,
    exam: str,
    preferred: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
) -> ExaminerVerdict:
    base = _heuristic_examiner(question)
    if not use_llm:
        return base
    try:
        result = await default_llm(
            examiner_messages(
                {
                    "stem": question.get("stem"),
                    "choices": question.get("choices"),
                    "correct_key": question.get("correct_key"),
                },
                exam,
            ),
            context={"kind": "author_examiner", "exam": exam},
            preferred=preferred,
            model=model,
        )
        data = parse_json_obj(result.text)
        if not data:
            return base
        verdict = ExaminerVerdict(
            exam_ready=clamp_score(data.get("exam_ready"), base.exam_ready),
            paragraph_natural=clamp_score(
                data.get("paragraph_natural"), base.paragraph_natural
            ),
            options_balanced=clamp_score(
                data.get("options_balanced"), base.options_balanced
            ),
            answer_not_guessable=clamp_score(
                data.get("answer_not_guessable"), base.answer_not_guessable
            ),
            distractors_strong=clamp_score(
                data.get("distractors_strong"), base.distractors_strong
            ),
            osym_feel=clamp_score(data.get("osym_feel"), base.osym_feel),
            notes=str(data.get("notes") or ""),
        )
        verdict.accepted = verdict.score >= MIN_EXAMINER
        return verdict
    except Exception:
        return base
