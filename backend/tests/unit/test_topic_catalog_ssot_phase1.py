"""Faz 1 — read-only catalog SSOT regressions (no live DB required)."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.models.topic_test import TopicTest, TopicTestStatus
from app.services.exam_catalog_service import ExamCatalogService
from app.services.learning_profile_service import LearningProfileService
from app.services.topic_catalog_resolver import (
    BLOCKED_LEGACY_TOPIC_CODES,
    CANONICAL_ASCII_TOPIC,
    FORBIDDEN_PRODUCT_FOLDS,
    LEGACY_ASCII_TOPIC,
    YDS_ORPHAN_SUBJECTS,
    YDS_SKILL_FOLD,
    catalog_exam_code_for_read,
    canonical_topic_code_for_display,
    exam_code_filter_for_list_topics,
    resolver_to_topic,
    topic_codes_for_dual_read,
)
from app.services.topic_test_catalog_service import TopicTestCatalogService


TYT_MAT_LP_ONLY = (
    "tyt_matematik__sayi_basamaklari",
    "tyt_matematik__bolme_bolunebilme",
    "tyt_matematik__obeb_okek",
    "tyt_matematik__rasyonel_sayilar",
    "tyt_matematik__mutlak_deger",
    "tyt_matematik__carpanlara_ayirma",
    "tyt_matematik__kumeler",
    "tyt_matematik__polinomlar",
    "tyt_matematik__ikinci_derece",
    "tyt_matematik__permutasyon_kombinasyon",
)


def test_to_topic_null_blocked_legacy_not_in_resolver():
    for code in BLOCKED_LEGACY_TOPIC_CODES:
        assert resolver_to_topic(code) is None
    for code in TYT_MAT_LP_ONLY:
        assert resolver_to_topic(code) is None


def test_forbidden_product_folds_never_become_to_topic():
    for src, dest in FORBIDDEN_PRODUCT_FOLDS.items():
        assert resolver_to_topic(src) is None
        assert resolver_to_topic(src) != dest


def test_yds_collapse_never_in_resolver():
    yds_topics = [c for c in BLOCKED_LEGACY_TOPIC_CODES if c.startswith("yds_")]
    assert yds_topics
    for code in yds_topics:
        assert resolver_to_topic(code) is None
    for dest in YDS_SKILL_FOLD.values():
        assert dest not in {resolver_to_topic(c) for c in BLOCKED_LEGACY_TOPIC_CODES}


def test_tyt_yks_catalog_exam_alias_does_not_touch_pool_key():
    assert catalog_exam_code_for_read("tyt") == "yks"
    assert catalog_exam_code_for_read("ayt") == "yks"
    assert catalog_exam_code_for_read("ydt") == "yks"
    assert catalog_exam_code_for_read("kpss") == "kpss"
    assert catalog_exam_code_for_read("kpss_lisans") == "kpss"
    assert catalog_exam_code_for_read("yds") == "yds"


def test_exam_filter_ssot_off_keeps_raw_tyt(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "TOPIC_CATALOG_SSOT", False)
    assert exam_code_filter_for_list_topics("tyt") == "tyt"


def test_exam_filter_ssot_on_aliases_tyt_to_yks(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "TOPIC_CATALOG_SSOT", True)
    assert exam_code_filter_for_list_topics("tyt") == "yks"
    assert exam_code_filter_for_list_topics("tyt") != "tyt"


def test_ascii_dual_read_group():
    pair = set(topic_codes_for_dual_read(LEGACY_ASCII_TOPIC))
    assert pair == {CANONICAL_ASCII_TOPIC, LEGACY_ASCII_TOPIC}
    assert set(topic_codes_for_dual_read(CANONICAL_ASCII_TOPIC)) == pair
    assert topic_codes_for_dual_read("tyt_matematik__problemler") == (
        "tyt_matematik__problemler",
    )
    assert canonical_topic_code_for_display(LEGACY_ASCII_TOPIC) == CANONICAL_ASCII_TOPIC


def test_ascii_dual_read_sql_selects_both_codes_exam_stays_tyt():
    codes = topic_codes_for_dual_read(LEGACY_ASCII_TOPIC)
    q = select(TopicTest).where(
        TopicTest.exam == "tyt",
        TopicTest.topic_code.in_(codes),
        TopicTest.status == TopicTestStatus.PUBLISHED,
    )
    sql = str(
        q.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
    )
    assert "tyt" in sql
    assert "yks" not in sql
    assert CANONICAL_ASCII_TOPIC in sql
    assert LEGACY_ASCII_TOPIC in sql


def _ei_topic(*, code: str, name: str, order: int = 1) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        exam_code="yks",
        pack_code="tyt",
        subject_code="tyt_matematik",
        code=code,
        name=name,
        display_order=order,
        is_active=True,
        importance_score=0.0,
        average_question_count=0.0,
        question_range_min=0,
        question_range_max=0,
        difficulty_score=0.0,
        estimated_study_minutes=0,
        revision_cost=0.0,
        assessment_weight=0.0,
        knowledge_tags=[],
        aliases=[],
        source="seed",
        legacy_topic_code=None,
    )


def _compile_sql(stmt) -> str:
    return str(
        stmt.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )


@pytest.mark.asyncio
async def test_list_topics_ssot_off_filters_raw_tyt(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "TOPIC_CATALOG_SSOT", False)
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = [
        _ei_topic(code="tyt_matematik__problemler", name="Problemler"),
    ]
    db.execute = AsyncMock(return_value=result)
    svc = ExamCatalogService(db)
    svc.ensure_synced = AsyncMock(return_value=-1)
    topics = await svc.list_topics("tyt", "tyt_matematik")
    sql = _compile_sql(db.execute.await_args.args[0])
    assert "tyt" in sql
    assert "'yks'" not in sql
    assert [t.code for t in topics] == ["tyt_matematik__problemler"]


@pytest.mark.asyncio
async def test_list_topics_ssot_on_aliases_yks_keeps_uncertain(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "TOPIC_CATALOG_SSOT", True)
    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = [
        _ei_topic(code="tyt_matematik__gorsel_veri", name="Grafik / Tablo", order=10),
        _ei_topic(code="tyt_matematik__uncertain", name="Sınıflanamayan / Diğer", order=1),
        _ei_topic(
            code="tyt_matematik__sayi_basamaklari",
            name="Sayı Basamakları",
            order=2,
        ),
    ]
    db.execute = AsyncMock(return_value=result)
    svc = ExamCatalogService(db)
    svc.ensure_synced = AsyncMock(return_value=-1)
    topics = await svc.list_topics("tyt", "tyt_matematik")
    sql = _compile_sql(db.execute.await_args.args[0])
    assert "yks" in sql
    codes = [t.code for t in topics]
    assert "tyt_matematik__gorsel_veri" in codes
    assert "tyt_matematik__uncertain" in codes
    assert "tyt_matematik__sayi_basamaklari" not in codes
    for blocked in TYT_MAT_LP_ONLY:
        assert blocked not in codes


@pytest.mark.asyncio
async def test_list_topics_yds_orphan_does_not_query(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "TOPIC_CATALOG_SSOT", True)
    db = AsyncMock()
    svc = ExamCatalogService(db)
    svc.ensure_synced = AsyncMock(return_value=-1)
    for subj in YDS_ORPHAN_SUBJECTS:
        with pytest.raises(NotFoundError):
            await svc.list_topics("yds", subj)
    db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_hub_ssot_emits_canonical_skips_lp_only(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "TOPIC_CATALOG_SSOT", True)
    svc = LearningProfileService(AsyncMock())
    ei = [
        SimpleNamespace(
            id=uuid.uuid4(),
            code="tyt_matematik__gorsel_veri",
            name="Grafik / Tablo",
            subject_code="tyt_matematik",
            display_order=10,
            is_active=True,
        ),
        SimpleNamespace(
            id=uuid.uuid4(),
            code="tyt_matematik__problemler",
            name="Problemler",
            subject_code="tyt_matematik",
            display_order=20,
            is_active=True,
        ),
        SimpleNamespace(
            id=uuid.uuid4(),
            code="tyt_matematik__uncertain",
            name="Sınıflanamayan / Diğer",
            subject_code="tyt_matematik",
            display_order=1,
            is_active=True,
        ),
    ]
    with patch(
        "app.services.learning_profile_service.ExamCatalogService"
    ) as catalog_cls:
        catalog_cls.return_value.list_topics = AsyncMock(return_value=ei)
        hub = await svc._hub_topics("tyt_matematik", exam_type="tyt")
    codes = {t.code for t in hub.items}
    assert "tyt_matematik__gorsel_veri" in codes
    assert "tyt_matematik__uncertain" in codes
    assert "tyt_matematik__problemler" in codes
    for blocked in TYT_MAT_LP_ONLY:
        assert blocked not in codes


@pytest.mark.asyncio
async def test_hub_ascii_canonical_not_legacy_slug(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "TOPIC_CATALOG_SSOT", True)
    svc = LearningProfileService(AsyncMock())
    ei = [
        SimpleNamespace(
            id=uuid.uuid4(),
            code=CANONICAL_ASCII_TOPIC,
            name="Katı Cisimler",
            subject_code="tyt_geometri",
            display_order=10,
            is_active=True,
        ),
    ]
    with patch(
        "app.services.learning_profile_service.ExamCatalogService"
    ) as catalog_cls:
        catalog_cls.return_value.list_topics = AsyncMock(return_value=ei)
        hub = await svc._hub_topics("tyt_geometri", exam_type="tyt")
    codes = {t.code for t in hub.items}
    assert CANONICAL_ASCII_TOPIC in codes
    assert LEGACY_ASCII_TOPIC not in codes
    assert "tyt_geometri__dik_ucgen" not in codes


@pytest.mark.asyncio
async def test_hub_falls_back_to_lp_when_catalog_fails(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "TOPIC_CATALOG_SSOT", True)
    svc = LearningProfileService(AsyncMock())
    lp_row = SimpleNamespace(
        id=uuid.uuid4(),
        code="tyt_matematik__sayi_basamaklari",
        name="Sayı Basamakları",
        subject_code="tyt_matematik",
        sort_order=20,
        difficulty=1,
        is_active=True,
    )
    svc.ensure_topic_catalog_synced = AsyncMock()
    svc.repo.list_topics = AsyncMock(return_value=[lp_row])
    with patch(
        "app.services.learning_profile_service.ExamCatalogService"
    ) as catalog_cls:
        catalog_cls.return_value.list_topics = AsyncMock(
            side_effect=NotFoundError("Topic bulunamadı: tyt/tyt_matematik")
        )
        hub = await svc._hub_topics("tyt_matematik", exam_type="tyt")
    assert hub.items[0].code == "tyt_matematik__sayi_basamaklari"


@pytest.mark.asyncio
async def test_hub_legacy_path_when_ssot_off(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "TOPIC_CATALOG_SSOT", False)
    svc = LearningProfileService(AsyncMock())
    lp_row = SimpleNamespace(
        id=uuid.uuid4(),
        code="tyt_matematik__sayi_basamaklari",
        name="Sayı Basamakları",
        subject_code="tyt_matematik",
        sort_order=20,
        difficulty=1,
        is_active=True,
    )
    svc.ensure_topic_catalog_synced = AsyncMock()
    svc.repo.list_topics = AsyncMock(return_value=[lp_row])
    with patch(
        "app.services.learning_profile_service.ExamCatalogService"
    ) as catalog_cls:
        hub = await svc._hub_topics("tyt_matematik", exam_type="tyt")
    catalog_cls.assert_not_called()
    assert hub.items[0].code == "tyt_matematik__sayi_basamaklari"


@pytest.mark.asyncio
async def test_list_catalog_dual_read_does_not_update_rows():
    db = AsyncMock()
    published = TopicTest(
        id=uuid.uuid4(),
        exam="tyt",
        subject_code="tyt_geometri",
        topic_code=CANONICAL_ASCII_TOPIC,
        week_id="2026-W33",
        difficulty="easy",
        ordinal=1,
        status=TopicTestStatus.PUBLISHED,
        question_count=10,
    )
    tests_result = MagicMock()
    tests_result.scalars.return_value.all.return_value = [published]
    attempts_result = MagicMock()
    attempts_result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(side_effect=[tests_result, attempts_result])
    catalog = await TopicTestCatalogService(db).list_catalog(
        uuid.uuid4(),
        exam="tyt",
        subject_code="tyt_geometri",
        topic_code=LEGACY_ASCII_TOPIC,
    )
    assert catalog.tests[0].id == published.id
    db.delete.assert_not_called()
    compiled = _compile_sql(db.execute.await_args_list[0].args[0])
    assert CANONICAL_ASCII_TOPIC in compiled
    assert LEGACY_ASCII_TOPIC in compiled
    assert "tyt" in compiled
    assert "yks" not in compiled
    assert published.exam == "tyt"
    assert published.topic_code == CANONICAL_ASCII_TOPIC
