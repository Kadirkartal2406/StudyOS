"""
StudyOS — Learning Profile / Onboarding / Subjects API (Sprint-3.0)
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.learning_profile import (
    ActiveExamUpdate,
    ExamTargetCreate,
    ExamTargetRead,
    ExamTargetUpdate,
    LearningProfileRead,
    LearningProfileUpdate,
    OnboardingCompleteRequest,
    OnboardingStatusRead,
    SubjectCatalogRead,
    SubjectHubDetail,
    TopicCatalogRead,
    UserSubjectRead,
)
from app.schemas.topic_work_surface import TopicWorkSurfaceProjection
from app.services.learning_profile_service import LearningProfileService
from app.services.welcome_tone_service import (
    WelcomeToneRequest,
    WelcomeToneResponse,
    WelcomeToneService,
)
from app.services.ai.question_generation_service import (
    QuestionGenerationService, QuizGenerateRequest, QuizGenerateResponse,
    GeneratedQuestionAnswerRequest, GeneratedQuestionAnswerResponse,
    GeneratedQuestionRead,
)
from app.services.ai.topic_notebook_service import TopicNotebookService, TopicNotebookSummary
from app.services.ai.topic_explain_service import TopicExplainService, ExplainRequest, ExplainResponse


router = APIRouter()


@router.get("/me", response_model=SuccessResponse[LearningProfileRead])
async def get_learning_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[LearningProfileRead]:
    data = await LearningProfileService(db).get_profile(current_user.id)
    return SuccessResponse(data=data)


@router.patch("/me", response_model=SuccessResponse[LearningProfileRead])
async def update_learning_profile(
    body: LearningProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[LearningProfileRead]:
    data = await LearningProfileService(db).update_profile(current_user.id, body)
    await db.commit()
    return SuccessResponse(data=data, message="Profil güncellendi")


@router.patch("/active-exam", response_model=SuccessResponse[LearningProfileRead])
async def set_active_exam(
    body: ActiveExamUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[LearningProfileRead]:
    """Sprint-3.1.A — Active Exam değiştir; Primary değişmez."""
    data = await LearningProfileService(db).set_active_exam(
        current_user.id, body.exam_type
    )
    await db.commit()
    return SuccessResponse(data=data, message="Active exam güncellendi")


@router.get("/onboarding/status", response_model=SuccessResponse[OnboardingStatusRead])
async def onboarding_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[OnboardingStatusRead]:
    data = await LearningProfileService(db).onboarding_status(current_user.id)
    return SuccessResponse(data=data)


@router.post("/onboarding/complete", response_model=SuccessResponse[LearningProfileRead])
async def onboarding_complete(
    body: OnboardingCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[LearningProfileRead]:
    data = await LearningProfileService(db).complete_onboarding(current_user.id, body)
    return SuccessResponse(data=data, message="Onboarding tamamlandı")


@router.post(
    "/onboarding/welcome-tone",
    response_model=SuccessResponse[WelcomeToneResponse],
)
async def onboarding_welcome_tone(
    body: WelcomeToneRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[WelcomeToneResponse]:
    """RC3 D2 — state machine adımı için Gemini Flash ton satırı."""
    data = await WelcomeToneService(db).line(current_user.id, body)
    return SuccessResponse(data=data)


@router.post("/onboarding/skip", response_model=SuccessResponse[LearningProfileRead])
async def onboarding_skip(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[LearningProfileRead]:
    data = await LearningProfileService(db).skip_onboarding(current_user.id)
    return SuccessResponse(data=data, message="Onboarding atlandı")


@router.get("/exam-targets", response_model=SuccessResponse[list[ExamTargetRead]])
async def list_exam_targets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[ExamTargetRead]]:
    profile = await LearningProfileService(db).get_profile(current_user.id)
    return SuccessResponse(data=profile.exam_targets)


@router.post("/exam-targets", response_model=SuccessResponse[ExamTargetRead])
async def create_exam_target(
    body: ExamTargetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ExamTargetRead]:
    data = await LearningProfileService(db).create_exam_target(current_user.id, body)
    return SuccessResponse(data=data, message="Sınav hedefi eklendi")


@router.patch("/exam-targets/{target_id}", response_model=SuccessResponse[ExamTargetRead])
async def update_exam_target(
    target_id: uuid.UUID,
    body: ExamTargetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ExamTargetRead]:
    data = await LearningProfileService(db).update_exam_target(current_user.id, target_id, body)
    return SuccessResponse(data=data, message="Sınav hedefi güncellendi")


@router.delete("/exam-targets/{target_id}", response_model=SuccessResponse[None])
async def delete_exam_target(
    target_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[None]:
    await LearningProfileService(db).delete_exam_target(current_user.id, target_id)
    return SuccessResponse(data=None, message="Sınav hedefi silindi")


@router.get("/subjects/catalog", response_model=SuccessResponse[list[SubjectCatalogRead]])
async def list_subject_catalog(
    exam_type: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[SubjectCatalogRead]]:
    _ = current_user
    data = await LearningProfileService(db).list_catalog(exam_type=exam_type)
    return SuccessResponse(data=data)


@router.get("/subjects/me", response_model=SuccessResponse[list[UserSubjectRead]])
async def list_my_subjects(
    exam_type: str | None = Query(
        default=None,
        description="Sprint-3.1.C — yoksa Active Exam",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[UserSubjectRead]]:
    data = await LearningProfileService(db).list_my_subjects(
        current_user.id, exam_type=exam_type
    )
    return SuccessResponse(data=data)


@router.get(
    "/subjects/{subject_code}/topics",
    response_model=SuccessResponse[list[TopicCatalogRead]],
)
async def list_subject_topics(
    subject_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[TopicCatalogRead]]:
    """Sprint-3.2.A — Topic Catalog list for a subject (topic_code identity)."""
    _ = current_user
    data = await LearningProfileService(db).list_topics_for_subject(subject_code)
    return SuccessResponse(data=data)


@router.get(
    "/subjects/{subject_code}/topics/{topic_code}/work-surface",
    response_model=SuccessResponse[TopicWorkSurfaceProjection],
)
async def get_topic_work_surface(
    subject_code: str,
    topic_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TopicWorkSurfaceProjection]:
    """Alignment Sprint-3 — Topic Work Surface projection (Decision uygular, üretmez)."""
    data = await LearningProfileService(db).get_topic_work_surface(
        current_user.id, subject_code, topic_code
    )
    return SuccessResponse(data=data)


@router.get(
    "/subjects/{subject_code}",
    response_model=SuccessResponse[SubjectHubDetail],
)
async def get_subject_hub(
    subject_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[SubjectHubDetail]:
    """Sprint-3.1.C — Subject Hub detail (subject_code identity)."""
    data = await LearningProfileService(db).get_subject_hub(
        current_user.id, subject_code
    )
    return SuccessResponse(data=data)


@router.post(
    "/subjects/{subject_code}/topics/{topic_code}/questions/generate",
    response_model=SuccessResponse[QuizGenerateResponse],
)
async def generate_topic_questions(
    subject_code: str,
    topic_code: str,
    body: QuizGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[QuizGenerateResponse]:
    """AI Sprint FAZ 4 — Confidence+Evidence bazlı soru üretimi (LOS § 3+4)."""
    data = await QuestionGenerationService(db).generate(
        current_user.id, subject_code, topic_code, body
    )
    await db.commit()
    return SuccessResponse(data=data, message=f"{len(data.questions)} soru üretildi")


@router.post(
    "/subjects/{subject_code}/topics/{topic_code}/questions/{question_id}/answer",
    response_model=SuccessResponse[GeneratedQuestionAnswerResponse],
)
async def answer_generated_question(
    subject_code: str,
    topic_code: str,
    question_id: uuid.UUID,
    body: GeneratedQuestionAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[GeneratedQuestionAnswerResponse]:
    """AI Sprint FAZ 4 — Soru yanıtla; Evidence sistemine geri besle."""
    data = await QuestionGenerationService(db).answer_question(
        question_id, current_user.id, body
    )
    await db.commit()
    return SuccessResponse(data=data)


@router.get(
    "/subjects/{subject_code}/topics/{topic_code}/questions",
    response_model=SuccessResponse[list[GeneratedQuestionRead]],
)
async def list_pending_questions(
    subject_code: str,
    topic_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[GeneratedQuestionRead]]:
    """AI Sprint FAZ 4 — Bekleyen AI soruları listesi."""
    questions = await QuestionGenerationService(db).list_pending(
        current_user.id, topic_code
    )
    data = [
        GeneratedQuestionRead(
            id=q.id,
            topic_code=q.topic_code,
            subject_code=q.subject_code,
            question_text=q.question_text,
            options=q.options,
            difficulty=q.difficulty,
            status=q.status,
            created_at=q.created_at,
        )
        for q in questions
    ]
    return SuccessResponse(data=data)



@router.get(
    "/subjects/{subject_code}/topics/{topic_code}/notebook",
    response_model=SuccessResponse[TopicNotebookSummary],
)
async def get_topic_notebook(
    subject_code: str,
    topic_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TopicNotebookSummary]:
    """AI Sprint FAZ 2 — Topic Notebook özeti (Confidence + Evidence + Resources)."""
    data = await TopicNotebookService(db).get_summary(
        current_user.id, subject_code, topic_code
    )
    return SuccessResponse(data=data)


@router.post(
    "/subjects/{subject_code}/topics/{topic_code}/explain",
    response_model=SuccessResponse[ExplainResponse],
)
async def post_topic_explain(
    subject_code: str,
    topic_code: str,
    body: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ExplainResponse]:
    """AI Sprint FAZ 3 — Context-aware Topic Explain (LOS § 5 EXPLAIN_ONLY)."""
    data = await TopicExplainService(db).explain(
        current_user.id, subject_code, topic_code, body
    )
    return SuccessResponse(data=data)


@router.get("/journey/trends")
async def get_journey_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sprint 15 — Confidence trend projection (Decide değil)."""
    from app.services.learning_intelligence_service import LearningIntelligenceService

    data = await LearningIntelligenceService(db).journey_trends(current_user.id)
    return SuccessResponse(data=data)
