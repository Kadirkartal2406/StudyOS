"""
StudyOS — API Router
Tüm v1 router'larını tek noktada toplar.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1 import (
    achievements,
    admin,
    ai_chat,
    ai_cost,
    ai_insights,
    assessment,
    assets,
    auth,
    beta_ops,
    coach,
    dashboard,
    evidence,
    exam_catalog,
    exams,
    goals,
    knowledge,
    learning_profile,
    memory,
    notification_settings,
    notifications,
    planner,
    questions,
    resources,
    revisions,
    statistics,
    study_plans,
    study_sessions,
    topic_quiz,
    users,
)

api_router = APIRouter()



@api_router.get("/health", tags=["system"])
async def health_check() -> JSONResponse:
    """Sistem sağlık kontrolü endpoint'i."""
    return JSONResponse(
        content={
            "success": True,
            "data": {"status": "ok", "service": "studyos-api"},
            "message": "Servis çalışıyor",
        }
    )


api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(study_plans.router, prefix="/study-plans", tags=["study-plans"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(study_sessions.router, prefix="/study-sessions", tags=["study-sessions"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
api_router.include_router(
    exam_catalog.router, prefix="/exam-catalog", tags=["exam-catalog"]
)
api_router.include_router(planner.router, prefix="/planner", tags=["planner"])
api_router.include_router(revisions.router, prefix="/revisions", tags=["revisions"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["achievements"])
api_router.include_router(
    learning_profile.router, prefix="/learning-profile", tags=["learning-profile"]
)
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(ai_insights.router, prefix="/ai", tags=["ai"])
api_router.include_router(ai_chat.router, prefix="/ai", tags=["ai"])
api_router.include_router(ai_cost.router, prefix="/ai", tags=["ai-cost"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(
    notification_settings.router,
    prefix="/notification-settings",
    tags=["notification-settings"],
)
# LOS Module 1 — Evidence Engine
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
# Sprint 13 — In-App Notifications
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
# Sprint 14 — Topic Quiz Generation
api_router.include_router(topic_quiz.router, prefix="/topic-quiz", tags=["topic-quiz"])
# Sprint 18 — Assessment Engine & Daily Challenge
api_router.include_router(assessment.router, prefix="/assessment", tags=["assessment"])
# Sprint 19 — Knowledge Layer
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
# Sprint 20 — Adaptive AI Coach (Experience)
api_router.include_router(coach.router, prefix="/coach", tags=["coach"])
# Sprint 21 RC — Analytics + Beta Feedback
api_router.include_router(beta_ops.router, prefix="/beta", tags=["beta"])
# Sprint 35 — Educational Asset Engine (EAE)
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])

