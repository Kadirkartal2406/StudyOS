"""Unit tests for Question Pool Stock Targets Configuration."""

from app.core.question_pool_stock_config import load_question_pool_stock_targets
from app.services.exam_catalog.seed import build_exam_intelligence_seed


def test_load_question_pool_stock_targets() -> None:
    targets = load_question_pool_stock_targets()
    assert len(targets) == 4

    exams = {t.exam for t in targets}
    assert exams == {"kpss", "tyt", "ayt", "lgs"}

    for t in targets:
        assert t.subject_code is not None
        assert t.topic_code is not None
        assert t.minimum > 0
        assert t.target >= t.minimum


def test_stock_targets_exist_in_catalog_seed() -> None:
    targets = load_question_pool_stock_targets()
    seed = build_exam_intelligence_seed()

    # Flatten catalog seed topics
    catalog_topics: set[str] = set()

    def collect_topics(pack: dict) -> None:
        for subj in pack.get("subjects") or []:
            for t in subj.get("topics") or []:
                catalog_topics.add(t["code"])
        for child in pack.get("children") or []:
            collect_topics(child)

    for exam in seed:
        for pack in exam.get("packs") or []:
            collect_topics(pack)

    for t in targets:
        assert t.topic_code in catalog_topics, f"Target topic code {t.topic_code} not found in catalog seed"
