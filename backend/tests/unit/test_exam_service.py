"""
StudyOS — Exam service unit tests
"""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserStatus
from app.schemas.exam import ExamCreate, ExamResultCreate, ExamResultsReplace
from app.services.exam_net import compute_exam_net
from app.services.exam_service import ExamService
from app.models.question_record import ExamType


async def _user(db: AsyncSession, email: str) -> User:
    user = User(
        email=email,
        hashed_password="x",
        first_name="Exam",
        last_name="Unit",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


def test_compute_exam_net_matches_question_tracking():
    assert compute_exam_net(12, 4) == Decimal("11.00")


@pytest.mark.asyncio
async def test_create_exam_with_results_and_milestone(db_session: AsyncSession):
    user = await _user(db_session, "exam.unit@studyos.dev")
    svc = ExamService(db_session)
    created = await svc.create_exam(
        user.id,
        ExamCreate(
            title="TYT Deneme 1",
            exam_type=ExamType.TYT,
            exam_date=date(2026, 7, 10),
            duration_minutes=135,
            results=[
                ExamResultCreate(
                    subject="Matematik",
                    correct_count=30,
                    wrong_count=8,
                    blank_count=2,
                    question_count=40,
                    duration_minutes=60,
                )
            ],
        ),
    )
    assert "first_exam" in created.milestones
    assert created.exam.total_net == Decimal("28.00")
    assert created.exam.result_count == 1

    detail = await svc.get_exam(created.exam.id, user.id)
    assert detail.results[0].subject == "Matematik"

    replaced = await svc.replace_results(
        created.exam.id,
        user.id,
        ExamResultsReplace(
            results=[
                ExamResultCreate(
                    subject="Türkçe",
                    correct_count=20,
                    wrong_count=4,
                    blank_count=1,
                    question_count=25,
                    duration_minutes=40,
                )
            ]
        ),
    )
    assert replaced.result_count == 1
    assert replaced.results[0].subject == "Türkçe"

    stats = await svc.get_statistics(user.id)
    assert stats.total_exams == 1
    assert stats.last_exam_title == "TYT Deneme 1"
