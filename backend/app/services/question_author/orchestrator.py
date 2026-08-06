"""M29 Question Author Engine — multi-step authoring pipeline."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.services.qie.types import GenerateContext, QuestionPlan
from app.services.question_author.author_planner import build_author_plan
from app.services.question_author.calibration_author import (
    enforce_calibration_diversity,
    mark_author_plan_calibration,
)
from app.services.question_author.distractor_author import author_distractors
from app.services.question_author.diversity_controller import DiversityController
from app.services.question_author.human_examiner import examine_question
from app.services.question_author.naturalizer import naturalize_question
from app.services.question_author.question_writer import write_question
from app.services.question_author.rewrite_engine import rewrite_question, should_rewrite
from app.services.question_author.self_critic import critique_question
from app.services.question_author.stub_guard import looks_like_author_stub
from app.services.question_author.types import AuthoredQuestion, MAX_REWRITE

logger = logging.getLogger("studyos.question_author")


def _default_data_root() -> Path:
    # backend/app/services/question_author/orchestrator.py → repo/data
    return Path(__file__).resolve().parents[4] / "data"


class QuestionAuthorEngine:
    """
    Pipeline:
      Author Plan → Writer → Distractors → Critic → Rewrite* → Naturalizer → Examiner
    Then caller runs frozen QIE Quality/Difficulty/Similarity gates.
    """

    def __init__(
        self,
        *,
        data_root: Path | str | None = None,
        diversity: DiversityController | None = None,
        use_llm: bool = True,
        separate_distractors: bool = True,
    ) -> None:
        self.data_root = Path(data_root) if data_root else _default_data_root()
        self.diversity = diversity or DiversityController(capacity=500)
        self.use_llm = use_llm
        self.separate_distractors = separate_distractors

    async def author_one(
        self,
        qie_plan: QuestionPlan,
        *,
        preferred: str | None = None,
        model: str | None = None,
        calibration: bool = False,
        asset_uri: str | None = None,
        db: Any | None = None,
    ) -> AuthoredQuestion:
        """Author a single question. If asset_uri is provided and db is given,
        EAE Visual Grounding Context is injected into the QIE prompt chain.
        """
        # EAE Sprint 4+2 — Inject visual asset grounding context into prompt
        eae_node_ids: list[str] | None = None
        eae_grounding_context: str | None = None
        if asset_uri and db is not None:
            try:
                from app.services.question_author.eae_grounding_builder import EAEGroundingPromptBuilder
                builder = EAEGroundingPromptBuilder(db)
                # build_grounding_dto is async; use base prompt as placeholder
                grounding_dto = await builder.context_engine.build_grounding_dto(asset_uri)
                eae_grounding_context = builder.context_engine.build_prompt_context_string(grounding_dto)
                eae_node_ids = grounding_dto.available_node_ids
                logger.info(
                    "EAE grounding injected asset_uri=%s node_count=%d",
                    asset_uri,
                    len(eae_node_ids),
                )
            except Exception as exc:
                logger.warning("EAE grounding failed asset_uri=%s: %s", asset_uri, exc)

        plan = await build_author_plan(
            qie_plan,
            data_root=self.data_root,
            preferred=preferred,
            model=model,
            use_llm=self.use_llm,
        )
        if calibration:
            plan = mark_author_plan_calibration(plan)

        # Writer: stem (+ optional full choices)
        raw = await write_question(
            plan,
            preferred=preferred,
            model=model,
            use_llm=self.use_llm,
            correct_only=self.separate_distractors,
            eae_grounding_context=eae_grounding_context,
        )
        provider = raw.pop("_provider", None)
        model_name = raw.pop("_model", None)

        if self.separate_distractors:
            correct_key = "A"
            correct_text = str(raw.get("correct_answer_text") or raw.get("stem") or "")[:200]
            if isinstance(raw.get("choices"), dict) and raw.get("correct_key"):
                correct_key = str(raw["correct_key"]).upper()
                correct_text = str(raw["choices"].get(correct_key) or correct_text)
            stem = str(raw.get("stem") or "")
            choices = await author_distractors(
                stem=stem,
                correct_key=correct_key,
                correct_text=correct_text if correct_text else "Doğru seçenek",
                plan=plan,
                preferred=preferred,
                model=model,
                use_llm=self.use_llm,
            )
            # If writer also returned choices, keep correct text from distractor layer
            question = {
                "stem": stem,
                "choices": choices,
                "correct_key": correct_key,
                "explanation": raw.get("rationale") or raw.get("explanation"),
            }
        else:
            question = {
                "stem": str(raw.get("stem") or ""),
                "choices": dict(raw.get("choices") or {}),
                "correct_key": str(raw.get("correct_key") or "A").upper(),
                "explanation": raw.get("explanation"),
            }

        critic = await critique_question(
            question, plan, preferred=preferred, model=model, use_llm=self.use_llm
        )
        rewrite_count = 0
        while should_rewrite(critic, rewrite_count):
            question = await rewrite_question(
                question,
                plan,
                critic,
                preferred=preferred,
                model=model,
                use_llm=self.use_llm,
            )
            rewrite_count += 1
            critic = await critique_question(
                question, plan, preferred=preferred, model=model, use_llm=self.use_llm
            )

        question = await naturalize_question(
            question,
            exam=plan.exam,
            preferred=preferred,
            model=model,
            use_llm=self.use_llm,
        )

        # Diversity vs last 500
        diverse_ok = self.diversity.accept(
            stem=str(question.get("stem") or ""),
            stem_type=plan.option_strategy,
            outcome=plan.measured_outcome,
        )
        if not diverse_ok and rewrite_count < MAX_REWRITE:
            question = await rewrite_question(
                question,
                plan,
                critic,
                preferred=preferred,
                model=model,
                use_llm=self.use_llm,
            )
            rewrite_count += 1
            question = await naturalize_question(
                question,
                exam=plan.exam,
                preferred=preferred,
                model=model,
                use_llm=self.use_llm,
            )
            self.diversity.accept(
                stem=str(question.get("stem") or ""),
                stem_type=plan.option_strategy,
                outcome=plan.measured_outcome,
            )

        examiner = await examine_question(
            question,
            exam=plan.exam,
            preferred=preferred,
            model=model,
            use_llm=self.use_llm,
        )

        authored = AuthoredQuestion(
            stem=str(question.get("stem") or ""),
            choices={str(k): str(v) for k, v in (question.get("choices") or {}).items()},
            correct_key=str(question.get("correct_key") or "A").upper(),
            explanation=question.get("explanation"),
            author_plan=plan,
            author_score=critic.average,
            critic_score=critic.average,
            critic=critic,
            rewrite_count=rewrite_count,
            exam_feeling=critic.exam_feeling,
            style_score=critic.style,
            difficulty_score=critic.difficulty,
            naturalness=critic.naturalness,
            reasoning_score=critic.reasoning,
            distractor_score=critic.distractors,
            reading_time=plan.reading_duration_sec,
            ai_confidence=round(min(0.99, critic.average / 100.0), 3),
            examiner=examiner,
            provider=provider,
            model=model_name,
            rejected=not examiner.accepted,
            reject_reason=None if examiner.accepted else "human_examiner_below_85",
        )
        if self.use_llm and looks_like_author_stub(authored.stem, authored.choices):
            authored.rejected = True
            authored.reject_reason = "author_stub_template"
            logger.warning(
                "Author stub template blocked topic=%s",
                plan.topic_code,
            )

        # EAE Sprint 4+2 — P_EAE hard gate: verify node IDs in authored question
        if eae_node_ids is not None and not authored.rejected:
            from app.services.question_intelligence.eae_node_verifier import EAENodeVerifier
            verification = EAENodeVerifier().verify_question_grounding(
                question_payload={
                    "choices": authored.choices,
                    "target_node_id": authored.author_plan.to_dict().get("target_node_id"),
                },
                available_node_ids=eae_node_ids,
            )
            if not verification.is_valid:
                authored.rejected = True
                authored.reject_reason = f"eae_node_hallucination:{verification.missing_node_ids}"
                logger.warning(
                    "EAE node hallucination blocked topic=%s missing=%s",
                    plan.topic_code,
                    verification.missing_node_ids,
                )

        return authored


    async def author_batch(
        self,
        plans: list[QuestionPlan],
        *,
        ctx: GenerateContext | None = None,
        preferred: str | None = None,
        model: str | None = None,
    ) -> list[AuthoredQuestion]:
        calibration = bool(ctx and ctx.kind == "calibration")
        use_plans = (
            enforce_calibration_diversity(plans) if calibration else list(plans)
        )
        preferred = preferred or (ctx.preferred_provider if ctx else None)
        model = model or (ctx.preferred_model if ctx else None)

        # Seed diversity from existing stems
        if ctx and ctx.existing_stems:
            self.diversity.remember_many(
                [{"stem": s, "stem_type": "", "outcome": ""} for s in ctx.existing_stems[-500:]]
            )

        out: list[AuthoredQuestion] = []
        for plan in use_plans:
            try:
                q = await self.author_one(
                    plan,
                    preferred=preferred,
                    model=model,
                    calibration=calibration,
                )
                if q.rejected:
                    logger.info(
                        "Author rejected plan_index=%s reason=%s",
                        plan.index,
                        q.reject_reason,
                    )
                    continue
                out.append(q)
            except Exception as e:
                logger.warning("Author failed plan_index=%s: %s", plan.index, e)
        return out
