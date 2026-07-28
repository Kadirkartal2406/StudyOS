"""
Alignment Sprint-1 — Today Projection entegrasyon testleri.

Mevcut test_dashboard_service.py'ye dokunmaz; Today sözleşmesini genişletir.
Gerçek DB oturumu gerektirir (Docker Postgres).
"""

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import RevisionSourceType
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.revision import RevisionCreate
from app.schemas.study_plan import StudyPlanCreate
from app.services.dashboard_service import DashboardService
from app.services.revision_service import RevisionService
from app.services.study_plan_service import StudyPlanService


async def _make_user(db: AsyncSession, **overrides: object) -> User:
    defaults: dict[str, object] = {
        "email": f"today.proj.{uuid.uuid4()}@studyos.dev",
        "hashed_password": "irrelevant",
        "first_name": "Today",
        "last_name": "User",
        "role": UserRole.STUDENT,
        "status": UserStatus.ACTIVE,
        "is_verified": False,
    }
    defaults.update(overrides)
    user = User(**defaults)  # type: ignore[arg-type]
    return await UserRepository(db).add(user)


def _assert_single_primary_action(result) -> None:
    """Her zaman tek Primary Action; reason boş olamaz."""
    assert result.next_action is not None
    action = result.next_action
    assert action.title.strip()
    assert action.reason.strip()
    assert action.cta_label.strip()
    assert action.action_type in {"revision", "study_plan", "focus"}
    assert action.deep_link_hint.startswith("/")
    # Tekil alan — çoğul next_actions yok
    assert not hasattr(result, "next_actions") or getattr(result, "next_actions", None) is None


def _assert_context_and_journey_secondary(result) -> None:
    assert isinstance(result.today_context_lines, list)
    assert len(result.today_context_lines) <= 3
    for line in result.today_context_lines:
        assert isinstance(line, str)
        assert line.strip()
    # Journey line ikincil: varsa string; asla Primary Action yerine geçmez
    if result.today_journey_line is not None:
        assert isinstance(result.today_journey_line, str)
        assert result.today_journey_line.strip()
        assert result.next_action is not None
        assert result.today_journey_line != result.next_action.title


@pytest.mark.asyncio
async def test_today_projection_plan_yields_study_plan_next_action(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)
    today = datetime.now(UTC).date()
    await StudyPlanService(db_session).create_plan(
        user.id,
        StudyPlanCreate(
            title="Problem çözümü",
            subject="TYT Matematik",
            topic="Problemler",
            target_question_count=20,
            estimated_minutes=25,
            study_date=today,
        ),
    )

    result = await DashboardService(db_session).get_dashboard(user)

    _assert_single_primary_action(result)
    assert result.next_action.action_type == "study_plan"
    assert result.next_action.title == "Bu konu üzerinde çalış"
    assert result.next_action.purpose == "study"
    assert result.next_action.tool_hint == "pomodoro"
    # Topic Work Surface tercih; katalog eşleşmezse /subjects
    assert result.next_action.deep_link_hint.startswith("/subjects")
    assert result.next_action.deep_link_hint != "/study-plan"
    assert result.next_action.deep_link_hint != "/pomodoro"
    assert result.next_action.confidence_tone == "high"
    assert "Problemler" in (result.next_action.subtitle or "")
    assert result.next_action.reason.strip()
    _assert_context_and_journey_secondary(result)
    assert any("çalışma bloğun kaldı" in line for line in result.today_context_lines)


@pytest.mark.asyncio
async def test_today_projection_revision_due_beats_plan(
    db_session: AsyncSession,
) -> None:
    """Revision due varsa Next Action = Revision (plan olsa bile)."""
    user = await _make_user(db_session)
    today = datetime.now(UTC).date()
    await StudyPlanService(db_session).create_plan(
        user.id,
        StudyPlanCreate(
            title="Fizik",
            subject="Fizik",
            topic="Kuvvet",
            target_question_count=10,
            estimated_minutes=30,
            study_date=today,
        ),
    )
    await RevisionService(db_session).create(
        user.id,
        RevisionCreate(
            title="Türev tekrarı",
            subject="Matematik",
            topic="Türev",
            source_type=RevisionSourceType.MANUAL,
            difficulty=3,
            reason="Manuel due",
        ),
    )

    result = await DashboardService(db_session).get_dashboard(user)

    _assert_single_primary_action(result)
    assert result.next_action.action_type == "revision"
    assert result.next_action.title == "Bu konu üzerinde tekrar yap"
    assert result.next_action.purpose == "review"
    assert result.next_action.tool_hint == "revision"
    assert result.next_action.deep_link_hint.startswith("/subjects")
    assert result.next_action.deep_link_hint != "/revisions"
    assert "Türev" in (result.next_action.subtitle or result.next_action.title)
    assert result.next_action.reason.strip()
    assert result.next_action.confidence_tone == "high"
    _assert_context_and_journey_secondary(result)
    assert any("tekrar bekliyor" in line for line in result.today_context_lines)


@pytest.mark.asyncio
async def test_today_projection_empty_day_safe_focus(
    db_session: AsyncSession,
) -> None:
    user = await _make_user(db_session)

    result = await DashboardService(db_session).get_dashboard(user)

    _assert_single_primary_action(result)
    assert result.next_action.action_type == "focus"
    # Observation: Topic Work Surface veya Subject container — pomodoro doğrudan değil
    assert result.next_action.deep_link_hint.startswith("/subjects")
    assert result.next_action.deep_link_hint != "/pomodoro"
    assert result.next_action.confidence_tone == "low"
    assert result.next_action.reason.strip()
    assert (
        "sinyal" in result.next_action.reason.lower()
        or "tanımaya" in result.next_action.reason.lower()
    )
    _assert_context_and_journey_secondary(result)
    assert len(result.today_context_lines) <= 3


@pytest.mark.asyncio
async def test_today_projection_reason_never_blank_and_single_action(
    db_session: AsyncSession,
) -> None:
    """Boş gün + planlı gün: reason her zaman dolu; tek next_action."""
    user = await _make_user(db_session)
    empty = await DashboardService(db_session).get_dashboard(user)
    _assert_single_primary_action(empty)
    assert empty.next_action.reason.strip() != ""

    today = datetime.now(UTC).date()
    await StudyPlanService(db_session).create_plan(
        user.id,
        StudyPlanCreate(
            title="Kimya",
            subject="Kimya",
            target_question_count=5,
            estimated_minutes=20,
            study_date=today,
        ),
    )
    with_plan = await DashboardService(db_session).get_dashboard(user)
    _assert_single_primary_action(with_plan)
    assert with_plan.next_action.reason.strip() != ""
    # Response modelinde yalnızca bir Primary Action alanı
    assert with_plan.next_action.action_type == "study_plan"


@pytest.mark.asyncio
async def test_today_context_lines_cap_at_three(db_session: AsyncSession) -> None:
    user = await _make_user(db_session)
    today = datetime.now(UTC).date()
    plan_svc = StudyPlanService(db_session)
    for i in range(4):
        await plan_svc.create_plan(
            user.id,
            StudyPlanCreate(
                title=f"Blok {i}",
                subject="Matematik",
                topic=f"Konu {i}",
                target_question_count=5,
                estimated_minutes=15,
                study_date=today,
            ),
        )
    await RevisionService(db_session).create(
        user.id,
        RevisionCreate(
            title="Due tekrar",
            subject="Matematik",
            source_type=RevisionSourceType.MANUAL,
            reason="due",
        ),
    )

    result = await DashboardService(db_session).get_dashboard(user)

    assert len(result.today_context_lines) <= 3
    _assert_single_primary_action(result)
    _assert_context_and_journey_secondary(result)
