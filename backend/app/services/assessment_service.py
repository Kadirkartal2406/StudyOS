"""
Sprint 18 — Assessment Service (LOS §11 Sense).
Topic Quiz altyapısını orkestre eder; Decision/Living Plan üretmez.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from sqlalchemy import select

from app.models.assessment import (
    AssessmentKind,
    AssessmentQuestion,
    AssessmentSession,
    AssessmentSessionStatus,
    DailyChallenge,
    DailyChallengeScore,
    SharedDailyBooklet,
    SharedDailyBookletQuestion,
)
from app.models.user import User
from app.repositories.assessment_repository import AssessmentRepository
from app.schemas.assessment import (
    AssessmentOverview,
    AssessmentProgressItem,
    AssessmentQuestionPublic,
    AssessmentQuestionReview,
    AssessmentSessionRead,
    AssessmentStartRequest,
    AssessmentSubjectBreakdown,
    AssessmentSubmitRequest,
    AssessmentSubmitResult,
    AssessmentTopicBreakdown,
    BranchChallengeRead,
    DailyChallengeBundle,
    DailyChallengeRead,
    DailySubjectOption,
    DailySubjectsBundle,
    EstimatedScoreRead,
    LeaderboardEntry,
    LeaderboardRead,
    RankingRead,
)
from app.schemas.topic_quiz import QuizAnswerItem, QuizGenerateRequest, QuizSubmitRequest
from app.services.learning_profile_service import LearningProfileService
from app.services.score_estimation_service import ScoreEstimationService
from app.services.topic_quiz_service import TopicQuizService


def _commentary(kind: str, accuracy: float, subject_name: str | None) -> str:
    name = subject_name or "Bu alan"
    pct = round(accuracy * 100)
    if accuracy >= 0.75:
        return f"{name}: %{pct} — güçlü bir başlangıç."
    if accuracy >= 0.5:
        return f"{name}: %{pct} — gelişme alanı var; düzenli pratik yardımcı olur."
    return f"{name}: %{pct} — öncelikli destek gerekebilir."


class AssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AssessmentRepository(db)
        self.quiz = TopicQuizService(db)
        self.profile = LearningProfileService(db)
        self.scores = ScoreEstimationService(db)

    async def _active_exam(self, user_id: uuid.UUID) -> str:
        effective, _, _ = await self.profile.resolve_active_scope(user_id)
        if not effective:
            targets = await self.profile.repo.list_exam_targets(user_id)
            if targets:
                return str(targets[0].exam_type)
            return "kpss"
        return effective

    async def _exam_subject_codes(self, user_id: uuid.UUID, exam: str) -> list[tuple[str, str]]:
        """Active exam → all catalog subjects (code, name), seeded into user profile."""
        from app.services.ai.subject_catalog_seed import codes_for_exam

        targets = await self.profile.repo.list_exam_targets(user_id)
        await self.profile._seed_subjects_for_exams(user_id, targets)
        target = next((t for t in targets if str(t.exam_type) == exam), None)
        branch = target.branch if target else None
        allowed = codes_for_exam(exam, branch)
        catalog = await self.profile.repo.list_catalog(exam_type=exam)
        if allowed is not None:
            catalog = [c for c in catalog if c.code in allowed and c.is_active]
        else:
            catalog = [c for c in catalog if c.is_active]
        catalog.sort(key=lambda c: (c.sort_order, c.name))
        return [(c.code, c.name) for c in catalog]

    async def _pick_topic(
        self, user_id: uuid.UUID, subject_code: str, topic_code: str | None
    ) -> tuple[str, str, str | None, str | None]:
        from app.services.confidence_engine import ConfidenceEngine

        cat = await self.profile.repo.get_catalog_by_code(subject_code)
        sub_name = cat.name if cat else subject_code
        topics = await self.profile.list_topics_for_subject(subject_code)
        if topic_code:
            top = next((t for t in topics if t.code == topic_code), None)
            if top is None and topics:
                top = topics[0]
            if top is None:
                raise ValidationError("Bu ders için konu bulunamadı")
            return subject_code, top.code, sub_name, top.name
        if not topics:
            raise ValidationError("Bu ders için konu kataloğu boş")

        # Prefer low-confidence topic for this subject; else rotate by date
        try:
            low = await ConfidenceEngine(self.db).list_low_confidence_topics(
                user_id, limit=40
            )
            topic_codes = {t.code for t in topics}
            for conf in low:
                if conf.topic_code in topic_codes:
                    top = next(t for t in topics if t.code == conf.topic_code)
                    return subject_code, top.code, sub_name, top.name
        except Exception:
            pass

        day_idx = datetime.now(UTC).timetuple().tm_yday
        top = topics[day_idx % len(topics)]
        return subject_code, top.code, sub_name, top.name

    def _to_read(
        self, session: AssessmentSession, *, include_answers: bool = False
    ) -> AssessmentSessionRead:
        from sqlalchemy import inspect as sa_inspect

        name_by_code: dict[str, str] = {}
        for sec in (session.section_plan or {}).get("sections", []) or []:
            if isinstance(sec, dict) and sec.get("subject_code"):
                name_by_code[str(sec["subject_code"])] = str(
                    sec.get("subject_name") or sec["subject_code"]
                )
        # Async'te lazy-load yasak — yüklenmemişse boş liste
        state = sa_inspect(session)
        raw_questions = (
            []
            if "questions" in state.unloaded
            else list(session.questions or [])
        )
        questions: list[AssessmentQuestionPublic] = []
        for q in raw_questions:
            questions.append(
                AssessmentQuestionPublic(
                    id=q.id,
                    ord_index=q.ord_index,
                    stem=q.stem,
                    choices=dict(q.choices or {}),
                    subject_code=q.subject_code,
                    topic_code=q.topic_code,
                    subject_name=name_by_code.get(q.subject_code or ""),
                )
            )
        return AssessmentSessionRead(
            id=session.id,
            exam_type=session.exam_type,
            kind=session.kind,
            subject_code=session.subject_code,
            topic_code=session.topic_code,
            subject_name=session.subject_name,
            topic_name=session.topic_name,
            status=session.status,
            difficulty=session.difficulty,
            requested_count=session.requested_count,
            challenge_date=session.challenge_date,
            quiz_generation_id=session.quiz_generation_id,
            correct_count=session.correct_count,
            wrong_count=session.wrong_count,
            blank_count=session.blank_count,
            accuracy=session.accuracy,
            commentary=session.commentary,
            is_booklet=bool(getattr(session, "is_booklet", False)),
            section_plan=dict(session.section_plan or {}),
            generation_progress=int(getattr(session, "generation_progress", 0) or 0),
            questions=questions,
            created_at=session.created_at,
        )

    async def overview(self, user_id: uuid.UUID) -> AssessmentOverview:
        exam = await self._active_exam(user_id)
        subjects = await self.profile.list_my_subjects(user_id)
        items: list[AssessmentProgressItem] = []
        completed = 0
        for s in subjects:
            cal = await self.repo.find_calibration(user_id, exam, s.subject_code)
            done = cal is not None
            if done:
                completed += 1
            items.append(
                AssessmentProgressItem(
                    subject_code=s.subject_code,
                    subject_name=s.subject_name,
                    completed=done,
                    accuracy=float(cal.accuracy) if cal and cal.accuracy is not None else None,
                    session_id=cal.id if cal else None,
                )
            )
        total = max(len(subjects), 1)
        pct = round((completed / total) * 100, 1) if subjects else 0.0
        if pct >= 100:
            msg = "Sistem seni tanımaya başladı."
        elif pct >= 50:
            msg = "Kalibrasyon ilerliyor — birkaç ders daha yeterli."
        elif completed == 0:
            msg = "İlk mini assessment ile seviyeni tanıyalım."
        else:
            msg = f"Kalibrasyon %{pct:.0f} tamamlandı."

        coach_summary = None
        coach_critical = None
        coach_next = None
        coach_rank = None
        try:
            est = await self.scores.refresh(user_id, exam) if completed else None
            if est is None:
                est = await self.repo.latest_score_snapshot(user_id, exam)
            ranking = await self.ranking(user_id)
            coach_rank = ranking.label
            if est:
                coach_critical = est.weakest_subject
                coach_next = (
                    f"Hedefe uzak: {est.weakest_subject}"
                    if est.weakest_subject
                    else "Kalibrasyonu tamamla"
                )
                coach_summary = (
                    f"{ranking.commentary} "
                    f"Tahmini başarı %{est.estimated_success_pct:.0f}."
                )
            else:
                coach_summary = ranking.commentary
                coach_next = "İlk branş kalibrasyonunu başlat"
        except Exception:
            pass

        return AssessmentOverview(
            exam_type=exam,
            progress_pct=pct,
            completed_subjects=completed,
            total_subjects=len(subjects),
            message=msg,
            subjects=items,
            coach_summary=coach_summary,
            coach_critical_subject=coach_critical,
            coach_next_target=coach_next,
            coach_rank_label=coach_rank,
        )

    async def start(
        self, user_id: uuid.UUID, data: AssessmentStartRequest
    ) -> AssessmentSessionRead:
        kind = (data.kind or "").strip().lower()
        if kind not in {k.value for k in AssessmentKind}:
            raise ValidationError("Geçersiz assessment kind")
        exam = await self._active_exam(user_id)
        today = datetime.now(UTC).date()

        if kind in {
            AssessmentKind.DAILY_CHALLENGE,
            "daily_challenge",
            "daily",
            "gunun_denemesi",
        }:
            # Kitapçık — subject_code zorunlu değil
            return await self._start_daily(user_id, exam, today, data)
        if kind == AssessmentKind.BRANCH_QUESTION:
            if not data.subject_code:
                raise ValidationError(
                    "Branş sorusu için subject_code gerekli",
                    field="subject_code",
                )
            return await self._start_branch(user_id, exam, today, data)
        # initial_calibration
        if not data.subject_code:
            raise ValidationError(
                "Kalibrasyon için subject_code gerekli",
                field="subject_code",
            )
        return await self._start_calibration(user_id, exam, data)

    async def _generate_linked_session(
        self,
        user_id: uuid.UUID,
        *,
        exam: str,
        kind: str,
        subject_code: str,
        topic_code: str,
        subject_name: str | None,
        topic_name: str | None,
        count: int,
        difficulty: str,
        challenge_date: date | None,
        plans: list | None = None,
        qie_meta: dict | None = None,
        generate_kind: str = "topic_quiz",
    ) -> AssessmentSession:
        quiz_read = await self.quiz.generate(
            user_id,
            subject_code,
            topic_code,
            QuizGenerateRequest(
                count=count, difficulty=difficulty, exam_type=exam
            ),
            plans=plans,
            kind=generate_kind,
        )
        session = AssessmentSession(
            user_id=user_id,
            exam_type=exam,
            kind=kind,
            subject_code=subject_code,
            topic_code=topic_code,
            subject_name=subject_name,
            topic_name=topic_name,
            status=AssessmentSessionStatus.READY,
            difficulty=difficulty,
            requested_count=count,
            challenge_date=challenge_date,
            quiz_generation_id=quiz_read.id,
            qie_meta=dict(qie_meta or {}),
        )
        self.db.add(session)
        await self.db.flush()

        from app.models.topic_quiz import TopicQuizGeneration
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        gen = (
            await self.db.execute(
                select(TopicQuizGeneration)
                .options(selectinload(TopicQuizGeneration.items))
                .where(TopicQuizGeneration.id == quiz_read.id)
            )
        ).scalar_one()
        for item in gen.items:
            self.db.add(
                AssessmentQuestion(
                    session_id=session.id,
                    quiz_item_id=item.id,
                    ord_index=item.ord_index,
                    stem=item.stem,
                    choices=dict(item.choices or {}),
                    correct_key=item.correct_key,
                    explanation=item.explanation,
                    subject_code=subject_code,
                    topic_code=topic_code,
                    qie_card=dict(getattr(item, "qie_card", None) or {}),
                )
            )
        await self.db.flush()
        session = await self.repo.get_session(session.id, user_id)
        assert session is not None
        if not session.questions:
            raise ValidationError(
                "Soru üretilemedi — lütfen tekrar dene",
                field="count",
            )
        return session

    async def _start_calibration(
        self, user_id: uuid.UUID, exam: str, data: AssessmentStartRequest
    ) -> AssessmentSessionRead:
        sub, top, sn, tn = await self._pick_topic(
            user_id, data.subject_code or "", data.topic_code
        )
        if data.count is None:
            e = (exam or "").lower()
            if e in ("kpss", "ags", "ales"):
                count = 12
            elif e in ("yds", "yokdil"):
                count = 15
            else:
                count = 10
        else:
            count = data.count

        shared = await self._try_shared_level_test_session(
            user_id,
            exam=exam,
            subject_code=sub,
            subject_name=sn,
            topic_code=top,
            topic_name=tn,
            count=count,
            difficulty=data.difficulty or "medium",
        )
        if shared is not None:
            return shared

        from app.services.qie.calibration_planner import CalibrationPlanner

        initial_batch = min(4, count)
        all_plans = CalibrationPlanner().plan(
            exam=exam,
            subject_code=sub,
            subject_name=sn or sub,
            topic_code=top or sub,
            topic_name=tn or top or sn or sub,
            count=count,
            difficulty_band=data.difficulty or "medium",
        )
        first_plans = all_plans[:initial_batch]
        qie_meta = {
            "adaptive": count > initial_batch,
            "total_count": count,
            "initial_batch": initial_batch,
            "phase": "awaiting_early_answers" if count > initial_batch else "complete",
            "planned_skills": [p.skill for p in all_plans],
            "remaining_skills": [p.skill for p in all_plans[initial_batch:]],
        }
        session = await self._generate_linked_session(
            user_id,
            exam=exam,
            kind=AssessmentKind.INITIAL_CALIBRATION,
            subject_code=sub,
            topic_code=top,
            subject_name=sn,
            topic_name=tn,
            count=initial_batch,
            difficulty=data.difficulty,
            challenge_date=None,
            plans=first_plans,
            qie_meta=qie_meta,
            generate_kind="calibration",
        )
        session.requested_count = count
        await self.db.flush()
        return self._to_read(session)

    async def continue_adaptive_calibration(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        *,
        early_answers_correct: int | None = None,
        early_answers_total: int | None = None,
    ) -> AssessmentSessionRead:
        """Fill remaining calibration slots after first batch (QIE adaptive)."""
        session = await self.repo.get_session(session_id, user_id)
        if session is None:
            raise NotFoundError("Assessment", str(session_id))
        if session.kind != AssessmentKind.INITIAL_CALIBRATION:
            raise ValidationError("Yalnızca seviye testi için adaptive devam")
        meta = dict(session.qie_meta or {})
        if not meta.get("adaptive") or meta.get("phase") == "complete":
            return self._to_read(session)

        total_count = int(meta.get("total_count") or session.requested_count or 12)
        have = len(session.questions or [])
        remaining = max(0, total_count - have)
        if remaining <= 0:
            meta["phase"] = "complete"
            session.qie_meta = meta
            await self.db.flush()
            return self._to_read(session)

        if early_answers_total and early_answers_total > 0:
            acc = (early_answers_correct or 0) / early_answers_total
        else:
            answered = [
                q for q in (session.questions or []) if q.selected_key is not None
            ]
            if len(answered) >= int(meta.get("initial_batch") or 4):
                correct = sum(1 for q in answered if q.selected_key == q.correct_key)
                acc = correct / max(len(answered), 1)
            else:
                acc = 0.55

        from app.services.qie.adaptive_calibration import AdaptiveCalibrationPlanner

        used_skills = [
            (q.qie_card or {}).get("skill")
            for q in (session.questions or [])
            if (q.qie_card or {}).get("skill")
        ]
        plans = AdaptiveCalibrationPlanner().plan_remaining(
            exam=session.exam_type,
            subject_code=session.subject_code or "",
            subject_name=session.subject_name or session.subject_code or "",
            topic_code=session.topic_code or session.subject_code or "",
            topic_name=session.topic_name or "",
            total_count=total_count,
            already_done=have,
            used_skills=[s for s in used_skills if isinstance(s, str)],
            early_accuracy=acc,
        )
        quiz_read = await self.quiz.generate(
            user_id,
            session.subject_code or "general",
            session.topic_code or session.subject_code or "general",
            QuizGenerateRequest(
                count=len(plans),
                difficulty=session.difficulty,
                exam_type=session.exam_type,
            ),
            plans=plans,
            kind="adaptive_calibration",
        )
        from app.models.topic_quiz import TopicQuizGeneration
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        gen = (
            await self.db.execute(
                select(TopicQuizGeneration)
                .options(selectinload(TopicQuizGeneration.items))
                .where(TopicQuizGeneration.id == quiz_read.id)
            )
        ).scalar_one()
        base_ord = have
        for i, item in enumerate(gen.items):
            self.db.add(
                AssessmentQuestion(
                    session_id=session.id,
                    quiz_item_id=item.id,
                    ord_index=base_ord + i,
                    stem=item.stem,
                    choices=dict(item.choices or {}),
                    correct_key=item.correct_key,
                    explanation=item.explanation,
                    subject_code=session.subject_code,
                    topic_code=session.topic_code,
                    qie_card=dict(getattr(item, "qie_card", None) or {}),
                )
            )
        meta["phase"] = "complete"
        meta["early_accuracy"] = round(acc, 3)
        session.qie_meta = meta
        session.requested_count = total_count
        await self.db.flush()
        session = await self.repo.get_session(session_id, user_id)
        assert session is not None
        return self._to_read(session)

    async def _try_shared_level_test_session(
        self,
        user_id: uuid.UUID,
        *,
        exam: str,
        subject_code: str,
        subject_name: str | None,
        topic_code: str | None,
        topic_name: str | None,
        count: int,
        difficulty: str,
    ) -> AssessmentSessionRead | None:
        """Seviye testi: sınava özel ortak soru bankası / kitapçık."""
        from app.core.constants import LEVEL_TEST_PACK_DATE

        targets = await self.profile.repo.list_exam_targets(user_id)
        target = next((t for t in targets if str(t.exam_type) == exam), None)
        branch = target.branch if target else None
        try:
            booklet = await self.ensure_shared_booklet(
                exam,
                LEVEL_TEST_PACK_DATE,
                branch=branch,
                difficulty=difficulty,
                fill_now=True,
            )
            booklet = await self.repo.get_shared_booklet_by_id(booklet.id)
        except Exception:
            return None
        if booklet is None or not self._shared_pack_usable(booklet):
            return None

        qs = [
            q
            for q in (booklet.questions or [])
            if (q.subject_code or "") == subject_code
        ]
        if len(qs) < max(4, count // 3):
            # Ders eşleşmesi zayıfsa tüm paketten karışık al
            qs = list(booklet.questions or [])
        if not qs:
            return None
        picked = qs[:count]

        session = AssessmentSession(
            user_id=user_id,
            exam_type=exam,
            kind=AssessmentKind.INITIAL_CALIBRATION,
            subject_code=subject_code,
            topic_code=topic_code,
            subject_name=subject_name,
            topic_name=topic_name,
            status=AssessmentSessionStatus.READY,
            difficulty=difficulty,
            requested_count=len(picked),
            challenge_date=LEVEL_TEST_PACK_DATE,
            is_booklet=False,
            section_plan={
                "source": "shared_level_test",
                "booklet_id": str(booklet.id),
            },
            generation_progress=len(picked),
            quiz_generation_id=None,
        )
        self.db.add(session)
        await self.db.flush()
        for i, sq in enumerate(picked):
            self.db.add(
                AssessmentQuestion(
                    session_id=session.id,
                    quiz_item_id=None,
                    ord_index=i,
                    stem=sq.stem,
                    choices=dict(sq.choices or {}),
                    correct_key=sq.correct_key,
                    explanation=sq.explanation,
                    subject_code=sq.subject_code or subject_code,
                    topic_code=sq.topic_code or topic_code,
                )
            )
        await self.db.flush()
        loaded = await self.repo.get_session(session.id, user_id)
        return self._to_read(loaded or session)

    async def _build_section_plan(
        self, user_id: uuid.UUID, exam: str
    ) -> tuple[list[dict], int]:
        targets = await self.profile.repo.list_exam_targets(user_id)
        target = next((t for t in targets if str(t.exam_type) == exam), None)
        branch = target.branch if target else None
        return await self._build_section_plan_for_exam(exam, branch)

    async def _build_section_plan_for_exam(
        self, exam: str, branch: str | None = None
    ) -> tuple[list[dict], int]:
        """RC2 M22.2 — EI Catalog blueprint; legacy catalog fallback."""
        from app.services.ai.ei_blueprint import build_section_plan_from_ei
        from app.services.ai.exam_question_blueprint import (
            allocate_topics,
            filter_blueprint_to_available,
            get_exam_blueprint,
        )
        from app.services.ai.subject_catalog_seed import codes_for_exam

        # Prefer Exam Intelligence (importance / avg_q / difficulty)
        ei_plan = await build_section_plan_from_ei(self.db, exam, branch)
        if ei_plan is not None:
            return ei_plan

        # Fallback: legacy subject/topic catalog + hard-coded blueprint
        await self.profile.ensure_topic_catalog_synced()

        allowed = codes_for_exam(exam, branch)
        catalog = await self.profile.repo.list_catalog(exam_type=exam)
        if allowed is not None:
            catalog = [c for c in catalog if c.code in allowed and c.is_active]
        else:
            catalog = [c for c in catalog if c.is_active]
        catalog.sort(key=lambda c: (c.sort_order, c.name))
        available = {c.code for c in catalog}
        names = {c.code: c.name for c in catalog}
        if not available:
            bp0 = get_exam_blueprint(exam, branch)
            available = {s.subject_code for s in bp0.sections}
            names = {c: c for c in available}

        blueprint = filter_blueprint_to_available(
            get_exam_blueprint(exam, branch), available
        )
        sections: list[dict] = []
        total = 0
        for sec in blueprint.sections:
            topic_rows = await self.profile.repo.list_topics(
                subject_code=sec.subject_code, active_only=True
            )
            topic_codes = [t.code for t in topic_rows]
            if not topic_codes:
                topic_codes = [f"{sec.subject_code}__general"]
            alloc = allocate_topics(topic_codes, sec.count)
            topic_meta = []
            for code, n in alloc:
                tname = next((t.name for t in topic_rows if t.code == code), code)
                topic_meta.append(
                    {"topic_code": code, "topic_name": tname, "count": n}
                )
            sections.append(
                {
                    "subject_code": sec.subject_code,
                    "subject_name": names.get(sec.subject_code, sec.subject_code),
                    "count": sec.count,
                    "topics": topic_meta,
                }
            )
            total += sec.count
        return sections, total

    def _branch_key(self, branch: str | None) -> str:
        return (branch or "").strip().lower()

    def _shared_pack_usable(self, booklet: SharedDailyBooklet | None) -> bool:
        if booklet is None:
            return False
        if booklet.status != "ready" or not (booklet.questions or []):
            return False
        gen = str((booklet.section_plan or {}).get("generator") or "")
        return gen in ("gemini", "bank", "mixed")

    async def _resolve_ready_shared_booklet(
        self,
        exam: str,
        challenge_date: date,
        *,
        branch: str | None = None,
    ) -> SharedDailyBooklet | None:
        """Branş pack yoksa / hazır değilse varsayılan (branch='') pack'e düş."""
        branch_key = self._branch_key(branch)
        shared = await self.repo.get_shared_booklet(
            exam, challenge_date, branch_key=branch_key
        )
        if self._shared_pack_usable(shared):
            return shared
        if branch_key:
            fallback = await self.repo.get_shared_booklet(
                exam, challenge_date, branch_key=""
            )
            if self._shared_pack_usable(fallback):
                return fallback
        return shared

    def _use_synthetic(self, data: AssessmentStartRequest | None = None) -> bool:
        from app.core.config import settings

        if data is not None and data.synthetic:
            return True
        if settings.ASSESSMENT_BOOKLET_SYNTHETIC:
            return True
        if (settings.AI_PROVIDER or "null").lower() in {"", "null", "none"}:
            return True
        return False

    async def ensure_shared_booklet(
        self,
        exam: str,
        challenge_date: date,
        *,
        branch: str | None = None,
        difficulty: str = "medium",
        fill_now: bool = True,
    ) -> SharedDailyBooklet:
        """Get or create today's shared booklet; optionally fill synchronously."""
        branch_key = self._branch_key(branch)
        existing = await self.repo.get_shared_booklet(
            exam, challenge_date, branch_key=branch_key
        )
        if existing and existing.status == "ready" and (existing.questions or []):
            from app.services.ai.booklet_prompt_builder import BOOKLET_CONTENT_VERSION

            plan_meta = existing.section_plan or {}
            ver = str(plan_meta.get("content_version") or "")
            gen = str(plan_meta.get("generator") or "")
            # Gemini hazır → kullan. Bank hazır → kullanıcıya ver; fill_now ile
            # gece job Gemini yükseltmeyi dener.
            if ver == BOOKLET_CONTENT_VERSION and gen == "gemini":
                return existing
            if (
                ver == BOOKLET_CONTENT_VERSION
                and gen in ("bank", "mixed")
                and not fill_now
            ):
                return existing
            existing.status = "pending"
            await self.db.flush()
            booklet = existing
        elif existing and existing.status == "failed":
            # Sorular korunur — fill kaldığı yerden devam eder
            existing.status = "pending"
            existing.error_message = None
            await self.db.flush()
            booklet = existing
        elif existing:
            booklet = existing
        else:
            sections, total = await self._build_section_plan_for_exam(exam, branch)
            from app.services.ai.booklet_prompt_builder import BOOKLET_CONTENT_VERSION

            booklet = SharedDailyBooklet(
                exam_type=exam,
                branch_key=branch_key,
                challenge_date=challenge_date,
                status="pending",
                difficulty=difficulty or "medium",
                requested_count=total,
                section_plan={
                    "sections": sections,
                    "content_version": BOOKLET_CONTENT_VERSION,
                },
                generation_progress=0,
            )
            self.db.add(booklet)
            try:
                await self.db.flush()
            except Exception:
                # Race: başka worker aynı günü oluşturmuş olabilir
                await self.db.rollback()
                existing2 = await self.repo.get_shared_booklet(
                    exam, challenge_date, branch_key=branch_key
                )
                if existing2 is None:
                    raise
                booklet = existing2

        # fill_now yalnızca gece job / catch-up çağırır; kullanıcı HTTP'si False geçmeli
        if fill_now and booklet.status != "ready":
            await self.fill_shared_booklet(booklet, synthetic=False)
        return booklet

    async def _ai_booklet_chunk(
        self,
        *,
        exam_type: str,
        subject_name: str,
        topic_name: str,
        count: int,
        difficulty: str,
        subject_code: str | None = None,
        existing_stems: list[str] | None = None,
    ) -> list:
        """QIE chunk — planner + style + difficulty + similarity + quality gate."""
        from app.services.qie import GenerateContext, QieOrchestrator

        ctx = GenerateContext(
            exam=(exam_type or "kpss").lower(),
            subject_code=subject_code or "general",
            subject_name=subject_name,
            topic_code=subject_code or "general",
            topic_name=topic_name,
            count=count,
            difficulty_band=difficulty or "medium",
            existing_stems=list(existing_stems or []),
            kind="daily_booklet",
        )
        cards, _, _ = await QieOrchestrator(self.db).generate_batch(ctx)
        from app.services.ai.quiz_quality_gate import ValidatedQuizItem

        return [
            ValidatedQuizItem(
                stem=c.stem,
                choices=c.choices,
                correct_key=c.correct_key,
                explanation=c.explanation,
            )
            for c in cards
        ][:count]

    async def _renumber_booklet_questions(
        self,
        booklet: SharedDailyBooklet,
        plan: list,
    ) -> None:
        """Devam eden üretim sıralamayı bozar — plan düzenine göre yeniden numarala."""
        order_key: dict[tuple[str, str], int] = {}
        idx = 0
        for sec in plan:
            subject_code = str(sec.get("subject_code") or "")
            for topic in sec.get("topics") or []:
                order_key[(subject_code, str(topic.get("topic_code") or ""))] = idx
                idx += 1

        refreshed = await self.repo.get_shared_booklet_by_id(booklet.id)
        questions = list((refreshed or booklet).questions or [])
        questions.sort(
            key=lambda q: (
                order_key.get((q.subject_code or "", q.topic_code or ""), 10**6),
                q.ord_index,
            )
        )
        for position, question in enumerate(questions):
            if question.ord_index != position:
                question.ord_index = position
        await self.db.flush()

    async def fill_shared_booklet_from_bank(
        self,
        booklet: SharedDailyBooklet,
    ) -> SharedDailyBooklet:
        """Yerel bankadan doldur — Gemini kotası / AI kapalıyken günlük pack."""
        from sqlalchemy import delete

        from app.services.ai.booklet_prompt_builder import BOOKLET_CONTENT_VERSION
        from app.services.ai.booklet_question_bank import make_booklet_question

        booklet = await self.repo.get_shared_booklet_by_id(booklet.id) or booklet
        plan_meta = dict(booklet.section_plan or {})
        plan = plan_meta.get("sections") or []
        if not plan:
            sections, total = await self._build_section_plan_for_exam(
                booklet.exam_type,
                booklet.branch_key or None,
            )
            plan = sections
            plan_meta = {
                "sections": sections,
                "content_version": BOOKLET_CONTENT_VERSION,
            }
            booklet.section_plan = plan_meta
            booklet.requested_count = total

        await self.db.execute(
            delete(SharedDailyBookletQuestion).where(
                SharedDailyBookletQuestion.booklet_id == booklet.id
            )
        )
        await self.db.flush()

        ord_index = 0
        for sec in plan:
            subject_code = str(sec.get("subject_code") or "")
            subject_name = str(sec.get("subject_name") or subject_code)
            for topic in sec.get("topics") or []:
                topic_code = str(topic.get("topic_code") or "")
                topic_name = str(topic.get("topic_name") or topic_code)
                need = int(topic.get("count") or 0)
                for _ in range(need):
                    item = make_booklet_question(
                        exam_type=booklet.exam_type,
                        challenge_date=booklet.challenge_date,
                        ord_index=ord_index,
                        subject_code=subject_code,
                        subject_name=subject_name,
                        topic_code=topic_code,
                        topic_name=topic_name,
                    )
                    self.db.add(
                        SharedDailyBookletQuestion(
                            booklet_id=booklet.id,
                            ord_index=ord_index,
                            stem=item.stem,
                            choices=dict(item.choices),
                            correct_key=item.correct_key,
                            explanation=item.explanation,
                            subject_code=subject_code,
                            topic_code=topic_code,
                        )
                    )
                    ord_index += 1

        plan_meta["content_version"] = BOOKLET_CONTENT_VERSION
        plan_meta["generator"] = "bank"
        booklet.section_plan = plan_meta
        booklet.requested_count = ord_index
        booklet.generation_progress = ord_index
        booklet.status = "ready"
        booklet.error_message = (
            "Gemini kotası dolu — bugün yerel banka kullanıldı; "
            "kota açılınca gece Gemini ile yenilenecek"
        )
        await self.db.flush()
        refreshed = await self.repo.get_shared_booklet_by_id(booklet.id)
        return refreshed or booklet

    async def fill_shared_booklet(
        self,
        booklet: SharedDailyBooklet,
        *,
        synthetic: bool | None = None,
        allow_bank_fallback: bool = True,
    ) -> SharedDailyBooklet:
        """Yalnızca Gemini — bank/sentetik yok. Kaldığı yerden devam eder."""
        from sqlalchemy import delete

        from app.core.config import settings
        from app.core.exceptions import (
            AIQuotaExceededError,
            AIRateLimitError,
            ValidationError,
        )
        from app.services.ai.booklet_prompt_builder import (
            BOOKLET_CHUNK_SIZE,
            BOOKLET_CONTENT_VERSION,
        )

        provider = (settings.AI_PROVIDER or "null").lower()
        if provider in {"", "null", "none"}:
            if allow_bank_fallback:
                return await self.fill_shared_booklet_from_bank(booklet)
            booklet.status = "failed"
            booklet.error_message = "AI_PROVIDER kapalı — Günün Denemesi Gemini gerektirir"
            await self.db.flush()
            return booklet

        # M32: auto booklet Gemini kapalıysa banka düş (kota koruması)
        from app.services.ai_cost.flags import auto_booklet_enabled, background_ai_enabled

        if not auto_booklet_enabled() and not background_ai_enabled():
            if allow_bank_fallback:
                return await self.fill_shared_booklet_from_bank(booklet)
            booklet.status = "failed"
            booklet.error_message = "M32: ENABLE_AUTO_BOOKLET=false — Gemini booklet kapalı"
            await self.db.flush()
            return booklet

        # synthetic bilinçli test hariç yok sayılır
        if synthetic:
            booklet.status = "failed"
            booklet.error_message = "Sentetik soru kapalı — yalnızca Gemini"
            await self.db.flush()
            return booklet

        booklet = await self.repo.get_shared_booklet_by_id(booklet.id) or booklet
        plan_meta = dict(booklet.section_plan or {})
        ver = str(plan_meta.get("content_version") or "")
        gen = str(plan_meta.get("generator") or "")
        if (
            booklet.status == "ready"
            and (booklet.questions or [])
            and ver == BOOKLET_CONTENT_VERSION
            and gen == "gemini"
        ):
            return booklet

        booklet.status = "pending"
        plan = plan_meta.get("sections") or []
        if not plan:
            sections, total = await self._build_section_plan_for_exam(
                booklet.exam_type,
                booklet.branch_key or None,
            )
            plan = sections
            plan_meta = {
                "sections": sections,
                "content_version": BOOKLET_CONTENT_VERSION,
            }
            booklet.section_plan = plan_meta
            booklet.requested_count = total

        # Gemini kısmi üretimi devam; bank/eski pack silinip Gemini denenir
        existing = list(booklet.questions or [])
        had_bank = gen == "bank" and bool(existing)
        if existing and (ver != BOOKLET_CONTENT_VERSION or gen != "gemini"):
            await self.db.execute(
                delete(SharedDailyBookletQuestion).where(
                    SharedDailyBookletQuestion.booklet_id == booklet.id
                )
            )
            await self.db.flush()
            existing = []
        plan_meta["content_version"] = BOOKLET_CONTENT_VERSION
        # Kısmi pack de gemini etiketli olmalı ki sonraki tur devralabilsin
        plan_meta["generator"] = "gemini"
        booklet.section_plan = plan_meta

        # Kaldığı yerden devam: konu başına elde olan soru sayısı
        have: dict[tuple[str, str], int] = {}
        for q in existing:
            key = (q.subject_code or "", q.topic_code or "")
            have[key] = have.get(key, 0) + 1
        ord_index = max((q.ord_index for q in existing), default=-1) + 1
        produced = len(existing)
        accepted_stems = [q.stem for q in existing if q.stem]
        expected_total = int(booklet.requested_count or 0)
        booklet.generation_progress = produced
        await self.db.flush()

        try:
            for sec in plan:
                subject_code = str(sec.get("subject_code") or "")
                subject_name = str(sec.get("subject_name") or subject_code)
                topics = sec.get("topics") or []
                for topic in topics:
                    topic_code = str(topic.get("topic_code") or "")
                    topic_name = str(topic.get("topic_name") or topic_code)
                    need = int(topic.get("count") or 0) - have.get(
                        (subject_code, topic_code), 0
                    )
                    strikes = 0
                    while need > 0:
                        n = min(need, BOOKLET_CHUNK_SIZE)
                        items = await self._ai_booklet_chunk(
                            exam_type=booklet.exam_type,
                            subject_name=subject_name,
                            topic_name=topic_name,
                            count=n,
                            difficulty=booklet.difficulty or "medium",
                            subject_code=subject_code or None,
                            existing_stems=accepted_stems,
                        )
                        if not items:
                            strikes += 1
                            if strikes >= 2:
                                raise ValidationError(
                                    f"Gemini soru üretemedi: "
                                    f"{subject_name}/{topic_name}"
                                )
                            continue
                        strikes = 0
                        added = 0
                        for item in items[:n]:
                            from app.services.ai.duplicate_checker import (
                                is_near_duplicate,
                            )

                            if is_near_duplicate(item.stem, accepted_stems):
                                continue
                            self.db.add(
                                SharedDailyBookletQuestion(
                                    booklet_id=booklet.id,
                                    ord_index=ord_index,
                                    stem=item.stem,
                                    choices=dict(item.choices),
                                    correct_key=item.correct_key,
                                    explanation=item.explanation,
                                    subject_code=subject_code,
                                    topic_code=topic_code,
                                )
                            )
                            accepted_stems.append(item.stem)
                            ord_index += 1
                            produced += 1
                            need -= 1
                            added += 1
                        if added == 0:
                            strikes += 1
                            if strikes >= 2:
                                raise ValidationError(
                                    f"Gemini yinelenen soru üretti: "
                                    f"{subject_name}/{topic_name}"
                                )
                            continue
                        booklet.generation_progress = produced
                        await self.db.flush()

            if expected_total and produced < expected_total:
                raise ValidationError(
                    f"Gemini pack eksik: {produced}/{expected_total}"
                )

            await self._renumber_booklet_questions(booklet, plan)
            plan_meta["generator"] = "gemini"
            booklet.section_plan = plan_meta
            booklet.requested_count = produced
            booklet.generation_progress = produced
            booklet.status = "ready"
            booklet.error_message = None
            await self.db.flush()
        except Exception as e:
            quota = isinstance(e, AIQuotaExceededError | AIRateLimitError)
            # Kota + hiç Gemini sorusu yok → bankaya düş ki gün boş kalmasın
            if allow_bank_fallback and produced == 0 and (quota or had_bank):
                return await self.fill_shared_booklet_from_bank(booklet)
            # Üretilen Gemini soruları korunur; sonraki tur kaldığı yerden devam eder
            booklet.status = "pending"
            booklet.error_message = (
                "AI kotası doldu — üretim kaldığı yerden devam edecek"
                if quota
                else str(e)[:400]
            )
            booklet.generation_progress = produced
            await self.db.flush()
            return booklet

        booklet_id = booklet.id
        refreshed = await self.repo.get_shared_booklet_by_id(booklet_id)
        return refreshed or booklet

    async def _clone_shared_to_user(
        self,
        user_id: uuid.UUID,
        booklet: SharedDailyBooklet,
    ) -> AssessmentSession:
        from app.services.ai.exam_question_blueprint import BOOKLET_SUBJECT_CODE

        session = AssessmentSession(
            user_id=user_id,
            exam_type=booklet.exam_type,
            kind=AssessmentKind.DAILY_CHALLENGE,
            subject_code=BOOKLET_SUBJECT_CODE,
            topic_code=None,
            subject_name="Günün Denemesi",
            topic_name=None,
            status=AssessmentSessionStatus.READY,
            difficulty=booklet.difficulty or "medium",
            requested_count=booklet.requested_count,
            challenge_date=booklet.challenge_date,
            is_booklet=True,
            section_plan=dict(booklet.section_plan or {}),
            generation_progress=booklet.requested_count,
            quiz_generation_id=None,
        )
        self.db.add(session)
        await self.db.flush()
        for sq in booklet.questions or []:
            self.db.add(
                AssessmentQuestion(
                    session_id=session.id,
                    quiz_item_id=None,
                    ord_index=sq.ord_index,
                    stem=sq.stem,
                    choices=dict(sq.choices or {}),
                    correct_key=sq.correct_key,
                    explanation=sq.explanation,
                    subject_code=sq.subject_code,
                    topic_code=sq.topic_code,
                )
            )
        await self.db.flush()
        loaded = await self.repo.get_session(session.id, user_id)
        return loaded or session

    async def _start_daily(
        self,
        user_id: uuid.UUID,
        exam: str,
        today: date,
        data: AssessmentStartRequest,
    ) -> AssessmentSessionRead:
        """Ortak günlük kitapçıktan kullanıcı oturumu klonla."""
        from app.services.ai.exam_question_blueprint import BOOKLET_SUBJECT_CODE

        targets = await self.profile.repo.list_exam_targets(user_id)
        target = next((t for t in targets if str(t.exam_type) == exam), None)
        branch = target.branch if target else None

        existing = await self.repo.get_daily_challenge(user_id, exam, today)
        if existing and existing.session_id:
            session = await self.repo.get_session(existing.session_id, user_id)
            if session and session.status == AssessmentSessionStatus.SUBMITTED:
                return self._to_read(session)
            if (
                session
                and session.is_booklet
                and session.status == AssessmentSessionStatus.READY
                and session.questions
            ):
                from app.services.ai.booklet_prompt_builder import BOOKLET_CONTENT_VERSION

                ver = str((session.section_plan or {}).get("content_version") or "")
                gen = str((session.section_plan or {}).get("generator") or "")
                if ver == BOOKLET_CONTENT_VERSION and gen in ("gemini", "bank", "mixed"):
                    return self._to_read(session)

        # Kullanıcı isteğinde sync/AI üretimi yok — gece job + catch-up üretir
        booklet = await self._resolve_ready_shared_booklet(
            exam, today, branch=branch
        )
        if booklet is None or not self._shared_pack_usable(booklet):
            # Branş pack yoksa oluşturmayı dene; yine hazır değilse fallback zaten yok
            created = await self.ensure_shared_booklet(
                exam,
                today,
                branch=branch,
                difficulty=data.difficulty or "medium",
                fill_now=False,
            )
            booklet = await self._resolve_ready_shared_booklet(
                exam, today, branch=branch
            ) or created

        booklet = (
            await self.repo.get_shared_booklet_by_id(booklet.id)
            if booklet
            else None
        )
        gemini_ready = self._shared_pack_usable(booklet)

        if gemini_ready:
            session = await self._clone_shared_to_user(user_id, booklet)
            if existing is None:
                self.db.add(
                    DailyChallenge(
                        user_id=user_id,
                        exam_type=exam,
                        challenge_date=today,
                        subject_code=BOOKLET_SUBJECT_CODE,
                        status="available",
                        session_id=session.id,
                        title=f"Günün Denemesi — {session.requested_count} soru",
                    )
                )
            else:
                existing.session_id = session.id
                existing.subject_code = BOOKLET_SUBJECT_CODE
                existing.status = "available"
                existing.title = f"Günün Denemesi — {session.requested_count} soru"
            await self.db.flush()
            return self._to_read(session)

        # Pack henüz Gemini ile hazır değil — soru yok
        if (
            existing
            and existing.session_id
            and (session := await self.repo.get_session(existing.session_id, user_id))
            and session.status == AssessmentSessionStatus.PENDING
        ):
            session.generation_progress = (
                booklet.generation_progress if booklet else 0
            ) or 0
            session.requested_count = (
                booklet.requested_count if booklet else session.requested_count
            ) or session.requested_count
            await self.db.flush()
            return self._to_read(session)

        pending = AssessmentSession(
            user_id=user_id,
            exam_type=exam,
            kind=AssessmentKind.DAILY_CHALLENGE,
            subject_code=BOOKLET_SUBJECT_CODE,
            subject_name="Günün Denemesi",
            status=AssessmentSessionStatus.PENDING,
            difficulty=data.difficulty or "medium",
            requested_count=(booklet.requested_count if booklet else 0) or 0,
            challenge_date=today,
            is_booklet=True,
            section_plan=dict(plan),
            generation_progress=(booklet.generation_progress if booklet else 0) or 0,
        )
        self.db.add(pending)
        await self.db.flush()
        if existing is None:
            self.db.add(
                DailyChallenge(
                    user_id=user_id,
                    exam_type=exam,
                    challenge_date=today,
                    subject_code=BOOKLET_SUBJECT_CODE,
                    status="generating",
                    session_id=pending.id,
                    title="Günün denemesi henüz hazır değil (gece Gemini üretimi)",
                )
            )
        else:
            existing.session_id = pending.id
            existing.status = "generating"
            existing.title = "Günün denemesi henüz hazır değil (gece Gemini üretimi)"
        await self.db.flush()
        return self._to_read(pending)

    async def fill_booklet_session(
        self,
        session: AssessmentSession,
        *,
        synthetic: bool | None = None,
    ) -> AssessmentSession:
        """Legacy per-user fill — prefer shared pack when possible."""
        if session.challenge_date and session.is_booklet:
            targets = await self.profile.repo.list_exam_targets(session.user_id)
            target = next(
                (t for t in targets if str(t.exam_type) == session.exam_type), None
            )
            branch = target.branch if target else None
            booklet = await self.ensure_shared_booklet(
                session.exam_type,
                session.challenge_date,
                branch=branch,
                difficulty=session.difficulty or "medium",
                fill_now=True,
            )
            if booklet.status == "ready" and booklet.questions:
                for q in list(session.questions or []):
                    await self.db.delete(q)
                await self.db.flush()
                for sq in booklet.questions:
                    self.db.add(
                        AssessmentQuestion(
                            session_id=session.id,
                            quiz_item_id=None,
                            ord_index=sq.ord_index,
                            stem=sq.stem,
                            choices=dict(sq.choices or {}),
                            correct_key=sq.correct_key,
                            explanation=sq.explanation,
                            subject_code=sq.subject_code,
                            topic_code=sq.topic_code,
                        )
                    )
                session.requested_count = booklet.requested_count
                session.generation_progress = booklet.requested_count
                session.section_plan = dict(booklet.section_plan or {})
                session.status = AssessmentSessionStatus.READY
                session.error_message = None
                dc = await self.repo.get_daily_challenge(
                    session.user_id,
                    session.exam_type,
                    session.challenge_date,
                )
                if dc:
                    dc.status = "available"
                    dc.session_id = session.id
                    dc.title = f"Günün Denemesi — {booklet.requested_count} soru"
                await self.db.flush()
                return session

        # Fallback: mark failed rather than hang
        session.status = AssessmentSessionStatus.FAILED
        session.error_message = "Ortak kitapçık hazır değil"
        await self.db.flush()
        return session

    async def _start_branch(
        self,
        user_id: uuid.UUID,
        exam: str,
        today: date,
        data: AssessmentStartRequest,
    ) -> AssessmentSessionRead:
        existing = await self.repo.find_branch_today(
            user_id, exam, data.subject_code or "", today
        )
        if existing and existing.status != AssessmentSessionStatus.FAILED:
            return self._to_read(existing)
        sub, top, sn, tn = await self._pick_topic(
            user_id, data.subject_code or "", data.topic_code
        )
        session = await self._generate_linked_session(
            user_id,
            exam=exam,
            kind=AssessmentKind.BRANCH_QUESTION,
            subject_code=sub,
            topic_code=top,
            subject_name=sn,
            topic_name=tn,
            count=data.count or 1,
            difficulty=data.difficulty,
            challenge_date=today,
        )
        return self._to_read(session)

    async def get_session(
        self, user_id: uuid.UUID, session_id: uuid.UUID
    ) -> AssessmentSessionRead:
        session = await self.repo.get_session(session_id, user_id)
        if session is None:
            raise NotFoundError("Assessment", str(session_id))
        # Pending booklet burada üretilmez — poll hızlı kalsın; worker doldurur.
        return self._to_read(session)

    async def submit(
        self, user_id: uuid.UUID, session_id: uuid.UUID, data: AssessmentSubmitRequest
    ) -> AssessmentSubmitResult:
        session = await self.repo.get_session(session_id, user_id)
        if session is None:
            raise NotFoundError("Assessment", str(session_id))
        if session.status == AssessmentSessionStatus.SUBMITTED:
            raise ValidationError("Bu assessment zaten gönderildi")
        if session.status != AssessmentSessionStatus.READY:
            raise ValidationError("Assessment henüz hazır değil")

        by_aq = {q.id: q for q in session.questions}
        answers_map = {a.question_id: a.selected_key for a in data.answers}

        # Booklet / adaptive multi-generation: grade locally (scoring algorithm unchanged)
        meta = dict(session.qie_meta or {})
        use_local = (
            session.is_booklet
            or not session.quiz_generation_id
            or bool(meta.get("adaptive"))
        )

        # Booklet (or any session without full quiz bridge): grade locally
        if use_local:
            correct = wrong = blank = 0
            for aq in session.questions:
                selected = answers_map.get(aq.id)
                aq.selected_key = selected
                if not selected:
                    aq.is_correct = None
                    blank += 1
                elif selected == aq.correct_key:
                    aq.is_correct = True
                    correct += 1
                else:
                    aq.is_correct = False
                    wrong += 1
            total = max(correct + wrong + blank, 1)
            accuracy = correct / total
            session.correct_count = correct
            session.wrong_count = wrong
            session.blank_count = blank
            session.accuracy = round(accuracy, 4)
            session.commentary = _commentary(
                session.kind, accuracy, session.subject_name
            )
            session.status = AssessmentSessionStatus.SUBMITTED
            session.submitted_at = datetime.now(UTC)
            await self.db.flush()
        else:
            quiz_answers: list[QuizAnswerItem] = []
            for ans in data.answers:
                aq = by_aq.get(ans.question_id)
                if aq is None or aq.quiz_item_id is None:
                    continue
                quiz_answers.append(
                    QuizAnswerItem(
                        item_id=aq.quiz_item_id, selected_key=ans.selected_key
                    )
                )

            quiz_result = await self.quiz.submit(
                user_id,
                session.quiz_generation_id,
                QuizSubmitRequest(answers=quiz_answers),
            )

            review_by_quiz = {r.id: r for r in quiz_result.review_items}
            for aq in session.questions:
                if aq.quiz_item_id and aq.quiz_item_id in review_by_quiz:
                    r = review_by_quiz[aq.quiz_item_id]
                    aq.selected_key = r.selected_key
                    aq.is_correct = r.is_correct

            total = max(
                quiz_result.correct_count
                + quiz_result.wrong_count
                + quiz_result.blank_count,
                1,
            )
            accuracy = quiz_result.correct_count / total
            session.correct_count = quiz_result.correct_count
            session.wrong_count = quiz_result.wrong_count
            session.blank_count = quiz_result.blank_count
            session.accuracy = round(accuracy, 4)
            session.commentary = _commentary(
                session.kind, accuracy, session.subject_name
            )
            session.status = AssessmentSessionStatus.SUBMITTED
            session.submitted_at = datetime.now(UTC)
            await self.db.flush()

        # Evidence — Assessment source (extra to quiz ingest); Decision yok
        try:
            from app.services.evidence_service import EvidenceService

            await EvidenceService(self.db).ingest_assessment_session(session)
        except Exception:
            pass

        # Daily challenge mark completed + leaderboard score
        if session.kind == AssessmentKind.DAILY_CHALLENGE and session.challenge_date:
            dc = await self.repo.get_daily_challenge(
                user_id,
                session.exam_type,
                session.challenge_date,
            )
            if dc:
                dc.status = "completed"
                await self.db.flush()
            await self._upsert_daily_score(user_id, session)

        est = await self.scores.refresh(user_id, session.exam_type)

        reviews = [
            AssessmentQuestionReview(
                id=aq.id,
                ord_index=aq.ord_index,
                stem=aq.stem,
                choices=dict(aq.choices or {}),
                correct_key=aq.correct_key,
                explanation=aq.explanation,
                selected_key=aq.selected_key,
                is_correct=aq.is_correct,
            )
            for aq in sorted(session.questions, key=lambda x: x.ord_index)
        ]

        from app.services.exam_net import compute_exam_score

        score = compute_exam_score(
            correct=int(session.correct_count or 0),
            wrong=int(session.wrong_count or 0),
            blank=int(session.blank_count or 0),
            exam_type=session.exam_type,
            total_questions=len(session.questions),
        )
        by_subject, by_topic = self._result_breakdown(session)

        return AssessmentSubmitResult(
            session=self._to_read(session),
            review_items=reviews,
            commentary=session.commentary or "",
            estimated_success_pct=est.estimated_success_pct if est else score.success_pct,
            net=float(score.net),
            score_formula=score.formula,
            by_subject=by_subject,
            by_topic=by_topic,
        )

    def _result_breakdown(
        self, session: AssessmentSession
    ) -> tuple[list[AssessmentSubjectBreakdown], list[AssessmentTopicBreakdown]]:
        """Ders / konu bazlı doğru-yanlış-net."""
        from app.services.exam_net import compute_exam_score

        # subject_code → display name from section_plan
        name_by_subject: dict[str, str] = {}
        name_by_topic: dict[str, str] = {}
        for sec in (session.section_plan or {}).get("sections") or []:
            sc = str(sec.get("subject_code") or "")
            if sc:
                name_by_subject[sc] = str(sec.get("subject_name") or sc)
            for topic in sec.get("topics") or []:
                tc = str(topic.get("topic_code") or "")
                if tc:
                    name_by_topic[tc] = str(topic.get("topic_name") or tc)

        sub: dict[str, dict] = {}
        top: dict[str, dict] = {}
        for aq in session.questions:
            sc = aq.subject_code or session.subject_code or "unknown"
            sn = name_by_subject.get(sc) or session.subject_name or sc
            tc = aq.topic_code or session.topic_code or "general"
            tn = name_by_topic.get(tc) or session.topic_name or tc
            s = sub.setdefault(
                sc, {"name": sn, "correct": 0, "wrong": 0, "blank": 0, "total": 0}
            )
            t = top.setdefault(
                tc,
                {
                    "name": tn,
                    "subject_code": sc,
                    "correct": 0,
                    "wrong": 0,
                    "blank": 0,
                    "total": 0,
                },
            )
            s["total"] += 1
            t["total"] += 1
            if aq.is_correct is True:
                s["correct"] += 1
                t["correct"] += 1
            elif aq.is_correct is False:
                s["wrong"] += 1
                t["wrong"] += 1
            else:
                s["blank"] += 1
                t["blank"] += 1

        by_subject = []
        for code, d in sorted(sub.items(), key=lambda x: x[1]["name"]):
            sc_res = compute_exam_score(
                correct=d["correct"],
                wrong=d["wrong"],
                blank=d["blank"],
                exam_type=session.exam_type,
                total_questions=d["total"],
            )
            by_subject.append(
                AssessmentSubjectBreakdown(
                    subject_code=code,
                    subject_name=d["name"],
                    correct=d["correct"],
                    wrong=d["wrong"],
                    blank=d["blank"],
                    net=float(sc_res.net),
                    total=d["total"],
                )
            )
        by_topic = [
            AssessmentTopicBreakdown(
                topic_code=code,
                topic_name=d["name"],
                subject_code=d["subject_code"],
                correct=d["correct"],
                wrong=d["wrong"],
                blank=d["blank"],
                total=d["total"],
            )
            for code, d in sorted(top.items(), key=lambda x: x[1]["name"])
        ]
        return by_subject, by_topic

    async def daily_bundle(self, user_id: uuid.UUID) -> DailyChallengeBundle:
        """Today feed card — booklet hub."""
        from app.services.ai.exam_question_blueprint import BOOKLET_SUBJECT_CODE

        exam = await self._active_exam(user_id)
        today = datetime.now(UTC).date()
        targets = await self.profile.repo.list_exam_targets(user_id)
        target = next((t for t in targets if str(t.exam_type) == exam), None)
        branch = target.branch if target else None

        dc = await self.repo.get_daily_challenge(user_id, exam, today)
        session = None
        preview_total: int | None = None
        if dc and dc.session_id:
            session = await self.repo.get_session(dc.session_id, user_id)

        shared = await self._resolve_ready_shared_booklet(
            exam, today, branch=branch
        )
        if shared is None:
            # Pack yoksa arka planda üret; GET'i yavaşlatma
            try:
                await self.ensure_shared_booklet(
                    exam, today, branch=branch, fill_now=False
                )
                shared = await self._resolve_ready_shared_booklet(
                    exam, today, branch=branch
                )
            except Exception:
                shared = None

        if session and session.status == AssessmentSessionStatus.SUBMITTED:
            status = "completed"
            title = (
                f"Günün Denemesi tamamlandı "
                f"({session.correct_count or 0}/{session.requested_count})"
            )
        elif session and session.status == AssessmentSessionStatus.READY:
            status = "available"
            title = f"Günün Denemesi — {session.requested_count} soru"
        elif self._shared_pack_usable(shared):
            status = "available"
            preview_total = shared.requested_count
            title = f"Günün Denemesi — {preview_total} soru"
        elif shared and shared.status in ("pending", "failed"):
            # Branş pending ama default ready olabilir — yukarıda resolve denendi
            status = "generating"
            if "kota" in (shared.error_message or "").lower():
                title = "AI kotası doldu — üretim daha sonra devam edecek"
            else:
                title = (
                    "Günün denemesi hazırlanıyor "
                    f"({shared.generation_progress or 0}/{shared.requested_count})"
                )
            preview_total = shared.requested_count
        else:
            try:
                _, preview_total = await self._build_section_plan_for_exam(exam, branch)
                title = "Günün denemesi henüz hazır değil (gece Gemini)"
            except Exception:
                preview_total = None
                title = "Günün Denemesi"
            status = "generating"
            session = None

        daily_read = DailyChallengeRead(
            id=dc.id if dc else uuid.uuid4(),
            exam_type=exam,
            challenge_date=today,
            status=status,
            title=title,
            session_id=session.id if session else None,
            subject_code=BOOKLET_SUBJECT_CODE,
            topic_code=None,
            deep_link_hint="/assessment/daily",
            requested_count=(
                session.requested_count
                if session
                else (shared.requested_count if shared else preview_total)
            ),
            generation_progress=(
                session.generation_progress
                if session
                else (shared.generation_progress if shared else None)
            ),
            pdf_ready=bool(
                session
                and session.status
                in (
                    AssessmentSessionStatus.READY,
                    AssessmentSessionStatus.SUBMITTED,
                )
                and (session.questions or [])
            ),
            is_booklet=True,
        )

        exam_subjects = await self._exam_subject_codes(user_id, exam)
        branches: list[BranchChallengeRead] = []
        for code, name in exam_subjects[:8]:
            existing = await self.repo.find_branch_today(
                user_id, exam, code, today
            )
            status_b = "available"
            sid = None
            topic_code = None
            topic_name = None
            if existing:
                status_b = (
                    "completed"
                    if existing.status == AssessmentSessionStatus.SUBMITTED
                    else "available"
                )
                sid = existing.id
                topic_code = existing.topic_code
                topic_name = existing.topic_name
            branches.append(
                BranchChallengeRead(
                    subject_code=code,
                    subject_name=name,
                    topic_code=topic_code,
                    topic_name=topic_name,
                    status=status_b,
                    session_id=sid,
                    deep_link_hint=(
                        f"/assessment/session/{sid}"
                        if sid
                        else f"/assessment/branch/start?subject_code={code}"
                    ),
                )
            )
        return DailyChallengeBundle(
            exam_type=exam,
            challenge_date=today,
            daily=daily_read,
            branches=branches,
        )

    async def estimated_score(self, user_id: uuid.UUID) -> EstimatedScoreRead:
        exam = await self._active_exam(user_id)
        snap = await self.repo.latest_score_snapshot(user_id, exam)
        if snap is None:
            snap = await self.scores.refresh(user_id, exam)
        return EstimatedScoreRead(
            exam_type=exam,
            estimated_score=snap.estimated_score,
            estimated_success_pct=snap.estimated_success_pct,
            estimated_rank_pct=snap.estimated_rank_pct,
            peer_sample_size=snap.peer_sample_size,
            strongest_subject=snap.strongest_subject,
            weakest_subject=snap.weakest_subject,
            commentary=snap.commentary,
            above_average=snap.estimated_rank_pct <= 50,
        )

    async def ranking(self, user_id: uuid.UUID) -> RankingRead:
        est = await self.estimated_score(user_id)
        pct = est.estimated_rank_pct
        if est.peer_sample_size < 2:
            label = "Henüz yeterli karşılaştırma yok"
            commentary = "Aynı sınavı çözen daha fazla kullanıcı oldukça sıralama netleşir."
        elif pct <= 25:
            label = "Üst dilimdesin"
            commentary = f"Aynı sınavdaki kullanıcıların yaklaşık %{100 - pct:.0f}'inden iyisin (tahmini)."
        elif pct <= 50:
            label = "Ortalamanın üstündesin"
            commentary = "İstikrarlı ilerleme; hedefe uzak derslere odaklan."
        else:
            label = "Gelişim alanı"
            commentary = "Kalibrasyon ve günlük denemeler Confidence'ı hızla iyileştirir."
        return RankingRead(
            exam_type=est.exam_type,
            estimated_rank_pct=pct,
            peer_sample_size=est.peer_sample_size,
            label=label,
            commentary=commentary,
        )

    def _nickname(self, user: User) -> str:
        name = (user.first_name or "").strip()
        if name:
            return name[:120]
        return f"Öğrenci {str(user.id)[:4]}"

    async def _upsert_daily_score(
        self, user_id: uuid.UUID, session: AssessmentSession
    ) -> None:
        user = await self.db.get(User, user_id)
        nickname = self._nickname(user) if user else f"Öğrenci {str(user_id)[:4]}"
        score_val = float(session.correct_count or 0) * 10.0 + float(
            session.accuracy or 0
        ) * 100.0
        duration = 0
        if session.submitted_at and session.created_at:
            duration = max(
                0, int((session.submitted_at - session.created_at).total_seconds())
            )
        from app.services.ai.exam_question_blueprint import BOOKLET_SUBJECT_CODE

        subject_key = (
            BOOKLET_SUBJECT_CODE
            if session.is_booklet
            else (session.subject_code or "")
        )
        existing = await self.db.execute(
            select(DailyChallengeScore).where(
                DailyChallengeScore.user_id == user_id,
                DailyChallengeScore.exam_type == session.exam_type,
                DailyChallengeScore.challenge_date == session.challenge_date,
                DailyChallengeScore.subject_code == subject_key,
            )
        )
        row = existing.scalar_one_or_none()
        if row is None:
            row = DailyChallengeScore(
                user_id=user_id,
                exam_type=session.exam_type,
                challenge_date=session.challenge_date,
                subject_code=subject_key,
                session_id=session.id,
                nickname=nickname,
            )
            self.db.add(row)
        row.correct_count = session.correct_count or 0
        row.wrong_count = session.wrong_count or 0
        row.blank_count = session.blank_count or 0
        row.accuracy = float(session.accuracy or 0)
        row.score = score_val
        row.duration_seconds = duration
        row.nickname = nickname
        await self.db.flush()

    async def daily_subjects(self, user_id: uuid.UUID) -> DailySubjectsBundle:
        """Deprecated picker — returns single booklet card for compatibility."""
        from app.services.ai.exam_question_blueprint import BOOKLET_SUBJECT_CODE

        exam = await self._active_exam(user_id)
        today = datetime.now(UTC).date()
        bundle = await self.daily_bundle(user_id)
        daily = bundle.daily
        status = "available"
        session_id = daily.session_id if daily else None
        if daily and daily.status == "completed":
            status = "completed"
        elif daily and daily.status == "generating":
            status = "in_progress"
        options = [
            DailySubjectOption(
                subject_code=BOOKLET_SUBJECT_CODE,
                subject_name=daily.title if daily else "Günün Denemesi",
                status=status,
                session_id=session_id,
                deep_link_hint="/assessment/daily",
            )
        ]
        completed = 1 if status == "completed" else 0
        return DailySubjectsBundle(
            exam_type=exam,
            challenge_date=today,
            subjects=options,
            completed_count=completed,
            total_count=1,
            overall_ready=completed >= 1,
        )

    async def leaderboard(
        self,
        user_id: uuid.UUID,
        *,
        subject_code: str | None = None,
        challenge_date: date | None = None,
    ) -> LeaderboardRead:
        exam = await self._active_exam(user_id)
        day = challenge_date or datetime.now(UTC).date()
        if subject_code:
            result = await self.db.execute(
                select(DailyChallengeScore)
                .where(
                    DailyChallengeScore.exam_type == exam,
                    DailyChallengeScore.challenge_date == day,
                    DailyChallengeScore.subject_code == subject_code,
                )
                .order_by(
                    DailyChallengeScore.score.desc(),
                    DailyChallengeScore.duration_seconds.asc(),
                )
            )
            rows = list(result.scalars().all())
            scope = "subject"
        else:
            # Overall: sum scores across subjects per user
            result = await self.db.execute(
                select(DailyChallengeScore).where(
                    DailyChallengeScore.exam_type == exam,
                    DailyChallengeScore.challenge_date == day,
                )
            )
            all_rows = list(result.scalars().all())
            agg: dict[uuid.UUID, dict] = {}
            for r in all_rows:
                a = agg.setdefault(
                    r.user_id,
                    {"score": 0.0, "accuracy": 0.0, "n": 0, "nickname": r.nickname},
                )
                a["score"] += r.score
                a["accuracy"] += r.accuracy
                a["n"] += 1
                a["nickname"] = r.nickname
            rows = sorted(
                [
                    type(
                        "R",
                        (),
                        {
                            "user_id": uid,
                            "nickname": v["nickname"],
                            "score": v["score"],
                            "accuracy": (v["accuracy"] / v["n"]) if v["n"] else 0,
                        },
                    )()
                    for uid, v in agg.items()
                ],
                key=lambda x: (-x.score, -x.accuracy),
            )
            scope = "overall"

        entries: list[LeaderboardEntry] = []
        my_rank = None
        my_score = None
        for i, r in enumerate(rows, start=1):
            is_me = r.user_id == user_id
            if is_me:
                my_rank = i
                my_score = float(r.score)
            entries.append(
                LeaderboardEntry(
                    rank=i,
                    nickname=r.nickname,
                    user_id=r.user_id if is_me else None,
                    score=float(r.score),
                    accuracy=float(r.accuracy),
                    is_me=is_me,
                )
            )
        return LeaderboardRead(
            exam_type=exam,
            challenge_date=day,
            subject_code=subject_code,
            scope=scope,
            entries=entries[:50],
            my_rank=my_rank,
            my_score=my_score,
            total_participants=len(rows),
        )
