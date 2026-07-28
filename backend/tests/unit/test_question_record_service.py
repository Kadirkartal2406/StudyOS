"""
StudyOS — QuestionRecord Service Unit Testleri
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.question_record import QuestionRecordCreate, QuestionRecordUpdate
from app.services.question_record_service import QuestionRecordService, compute_net_score
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest


async def _user(db: AsyncSession, email: str):
    user, _, _ = await AuthService(db).register(
        RegisterRequest(
            email=email,
            password="GucluSifre123!",
            first_name="Soru",
            last_name="Test",
            role="student",
        )
    )
    return user


def _create(**overrides):
    data = {
        "subject": "Matematik",
        "topic": "Türev",
        "question_count": 20,
        "correct_count": 12,
        "wrong_count": 5,
        "blank_count": 3,
        "duration_minutes": 40,
        "exam_type": "tyt",
        "difficulty": "medium",
        "source": "book",
    }
    data.update(overrides)
    return QuestionRecordCreate(**data)


@pytest.mark.asyncio
async def test_compute_net_score_yks_formula():
    assert float(compute_net_score(12, 4)) == 11.0


@pytest.mark.asyncio
async def test_create_and_get_question_record(db_session: AsyncSession):
    user = await _user(db_session, "qr.create@studyos.dev")
    service = QuestionRecordService(db_session)

    record = await service.create(user.id, _create())
    assert record.question_count == 20
    assert float(record.net_score) == 10.75  # 12 - 5*0.25

    fetched = await service.get(record.id, user.id)
    assert fetched.id == record.id


@pytest.mark.asyncio
async def test_create_rejects_mismatched_counts(db_session: AsyncSession):
    user = await _user(db_session, "qr.badcounts@studyos.dev")
    with pytest.raises(Exception):
        await QuestionRecordService(db_session).create(
            user.id,
            QuestionRecordCreate(
                subject="Fizik",
                question_count=10,
                correct_count=3,
                wrong_count=3,
                blank_count=3,
            ),
        )


@pytest.mark.asyncio
async def test_update_recalculates_net(db_session: AsyncSession):
    user = await _user(db_session, "qr.update@studyos.dev")
    service = QuestionRecordService(db_session)
    record = await service.create(user.id, _create())

    updated = await service.update(
        record.id,
        user.id,
        QuestionRecordUpdate(
            question_count=10,
            correct_count=8,
            wrong_count=2,
            blank_count=0,
        ),
    )
    assert float(updated.net_score) == 7.5


@pytest.mark.asyncio
async def test_update_rejects_bad_counts(db_session: AsyncSession):
    user = await _user(db_session, "qr.updatebad@studyos.dev")
    service = QuestionRecordService(db_session)
    record = await service.create(user.id, _create())

    with pytest.raises(ValidationError):
        await service.update(
            record.id,
            user.id,
            QuestionRecordUpdate(correct_count=1, wrong_count=1, blank_count=1),
        )


@pytest.mark.asyncio
async def test_delete_and_statistics(db_session: AsyncSession):
    user = await _user(db_session, "qr.stats@studyos.dev")
    service = QuestionRecordService(db_session)
    record = await service.create(user.id, _create())

    overview = await service.get_statistics_overview(user.id)
    assert overview.total_questions == 20
    assert overview.today_questions == 20
    assert overview.record_count == 1

    await service.delete(record.id, user.id)
    with pytest.raises(NotFoundError):
        await service.get(record.id, user.id)

    overview2 = await service.get_statistics_overview(user.id)
    assert overview2.total_questions == 0


@pytest.mark.asyncio
async def test_distributions(db_session: AsyncSession):
    user = await _user(db_session, "qr.dist@studyos.dev")
    service = QuestionRecordService(db_session)
    await service.create(user.id, _create(subject="Kimya", exam_type="ayt"))
    await service.create(user.id, _create(subject="Kimya", topic="Mol", exam_type="ayt"))

    subjects = await service.get_subjects_distribution(user.id)
    assert subjects.total_questions == 40
    assert subjects.items[0].name == "Kimya"

    exams = await service.get_exams_distribution(user.id)
    assert any(i.name == "ayt" for i in exams.items)

    daily = await service.get_daily(user.id, days=7)
    assert daily.total_questions == 40
