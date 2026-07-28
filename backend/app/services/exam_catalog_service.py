"""ExamCatalogService — read-only Exam Intelligence Catalog."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.exam_intelligence import EiExam, EiPack, EiSubject, EiTopic
from app.schemas.exam_catalog import (
    EiExamRead,
    EiExamSummary,
    EiImportanceItem,
    EiPackRead,
    EiSubjectRead,
    EiTopicRead,
)
from app.services.exam_catalog.seed import build_exam_intelligence_seed

logger = logging.getLogger("studyos.exam_catalog")


class ExamCatalogService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def ensure_synced(self) -> int:
        """Idempotent seed upsert. Returns topic count.

        İlk yüklemede tam seed; sonraki çağrılarda exam varsa no-op
        (Decision Engine / hot path'i yavaşlatmamak için).
        """
        existing = await self.db.execute(select(EiExam.id).limit(1))
        if existing.scalar_one_or_none() is not None:
            count = await self.db.execute(select(EiTopic.id).limit(1))
            return 0 if count.scalar_one_or_none() is None else -1

        seed = build_exam_intelligence_seed()
        topic_total = 0
        for exam_data in seed:
            exam = await self._upsert_exam(exam_data)
            for pack_data in exam_data.get("packs") or []:
                topic_total += await self._upsert_pack_tree(
                    exam, pack_data, parent=None
                )
        await self.db.flush()
        logger.info("Exam Intelligence Catalog seeded topics=%s", topic_total)
        return topic_total

    async def force_resync(self) -> int:
        """Seed'i yeniden uygula (admin / migration sonrası)."""
        seed = build_exam_intelligence_seed()
        topic_total = 0
        for exam_data in seed:
            exam = await self._upsert_exam(exam_data)
            for pack_data in exam_data.get("packs") or []:
                topic_total += await self._upsert_pack_tree(
                    exam, pack_data, parent=None
                )
        await self.db.flush()
        return topic_total

    async def _upsert_exam(self, data: dict[str, Any]) -> EiExam:
        result = await self.db.execute(
            select(EiExam).where(EiExam.code == data["code"])
        )
        exam = result.scalar_one_or_none()
        if exam is None:
            exam = EiExam(
                code=data["code"],
                name=data["name"],
                display_order=int(data.get("display_order") or 0),
                source=str(data.get("source") or "official"),
                is_active=True,
            )
            self.db.add(exam)
            await self.db.flush()
        else:
            exam.name = data["name"]
            exam.display_order = int(data.get("display_order") or 0)
            exam.source = str(data.get("source") or "official")
            exam.is_active = True
        return exam

    async def _upsert_pack_tree(
        self,
        exam: EiExam,
        data: dict[str, Any],
        *,
        parent: EiPack | None,
    ) -> int:
        result = await self.db.execute(
            select(EiPack).where(
                EiPack.exam_id == exam.id, EiPack.code == data["code"]
            )
        )
        pack = result.scalar_one_or_none()
        if pack is None:
            pack = EiPack(
                exam_id=exam.id,
                code=data["code"],
                name=data["name"],
                parent_pack_id=parent.id if parent else None,
                display_order=int(data.get("display_order") or 0),
                branch_key=data.get("branch_key"),
                is_active=True,
            )
            self.db.add(pack)
            await self.db.flush()
        else:
            pack.name = data["name"]
            pack.parent_pack_id = parent.id if parent else None
            pack.display_order = int(data.get("display_order") or 0)
            pack.branch_key = data.get("branch_key")
            pack.is_active = True

        topic_count = 0
        for subj in data.get("subjects") or []:
            topic_count += await self._upsert_subject(exam, pack, subj)
        for child in data.get("children") or []:
            topic_count += await self._upsert_pack_tree(exam, child, parent=pack)
        return topic_count

    async def _upsert_subject(
        self,
        exam: EiExam,
        pack: EiPack,
        data: dict[str, Any],
    ) -> int:
        result = await self.db.execute(
            select(EiSubject).where(
                EiSubject.pack_id == pack.id, EiSubject.code == data["code"]
            )
        )
        subject = result.scalar_one_or_none()
        if subject is None:
            subject = EiSubject(
                pack_id=pack.id,
                exam_code=exam.code,
                pack_code=pack.code,
                code=data["code"],
                name=data["name"],
                display_order=int(data.get("display_order") or 0),
                legacy_subject_code=data.get("legacy_subject_code"),
                is_active=True,
            )
            self.db.add(subject)
            await self.db.flush()
        else:
            subject.exam_code = exam.code
            subject.pack_code = pack.code
            subject.name = data["name"]
            subject.display_order = int(data.get("display_order") or 0)
            subject.legacy_subject_code = data.get("legacy_subject_code")
            subject.is_active = True

        count = 0
        for topic in data.get("topics") or []:
            await self._upsert_topic(exam, pack, subject, topic)
            count += 1
        return count

    async def _upsert_topic(
        self,
        exam: EiExam,
        pack: EiPack,
        subject: EiSubject,
        data: dict[str, Any],
    ) -> EiTopic:
        result = await self.db.execute(
            select(EiTopic).where(EiTopic.code == data["code"])
        )
        topic = result.scalar_one_or_none()
        fields = dict(
            subject_id=subject.id,
            exam_code=exam.code,
            pack_code=pack.code,
            subject_code=subject.code,
            code=data["code"],
            name=data["name"],
            display_order=int(data.get("display_order") or 0),
            importance_score=float(data.get("importance_score") or 0.5),
            average_question_count=float(data.get("average_question_count") or 1.0),
            question_range_min=int(data.get("question_range_min") or 0),
            question_range_max=int(data.get("question_range_max") or 2),
            difficulty_score=float(data.get("difficulty_score") or 0.5),
            estimated_study_minutes=int(data.get("estimated_study_minutes") or 30),
            revision_cost=float(data.get("revision_cost") or 1.0),
            assessment_weight=float(data.get("assessment_weight") or 1.0),
            knowledge_tags=list(data.get("knowledge_tags") or []),
            aliases=list(data.get("aliases") or []),
            source=str(data.get("source") or "estimated"),
            legacy_topic_code=data.get("legacy_topic_code"),
            is_active=True,
        )
        if topic is None:
            topic = EiTopic(**fields)
            self.db.add(topic)
        else:
            for key, value in fields.items():
                setattr(topic, key, value)
        return topic

    async def list_exams(self) -> list[EiExamSummary]:
        await self.ensure_synced()
        result = await self.db.execute(
            select(EiExam)
            .where(EiExam.is_active.is_(True))
            .options(selectinload(EiExam.packs))
            .order_by(EiExam.display_order, EiExam.code)
        )
        exams = list(result.scalars().unique().all())
        return [
            EiExamSummary(
                id=e.id,
                code=e.code,
                name=e.name,
                display_order=e.display_order,
                is_active=e.is_active,
                source=e.source,
                pack_count=len([p for p in e.packs if p.is_active]),
            )
            for e in exams
        ]

    async def get_exam_tree(self, exam_code: str) -> EiExamRead:
        await self.ensure_synced()
        exam = await self._load_exam(exam_code)
        packs = [p for p in exam.packs if p.is_active and p.parent_pack_id is None]
        return EiExamRead(
            id=exam.id,
            code=exam.code,
            name=exam.name,
            display_order=exam.display_order,
            is_active=exam.is_active,
            source=exam.source,
            packs=[self._pack_to_read(p, exam.packs) for p in sorted(packs, key=lambda x: x.display_order)],
        )

    async def list_packs(self, exam_code: str) -> list[EiPackRead]:
        tree = await self.get_exam_tree(exam_code)
        return tree.packs

    async def get_pack(self, exam_code: str, pack_code: str) -> EiPackRead:
        await self.ensure_synced()
        exam = await self._load_exam(exam_code)
        pack = next((p for p in exam.packs if p.code == pack_code and p.is_active), None)
        if pack is None:
            raise NotFoundError(f"Pack bulunamadı: {exam_code}/{pack_code}")
        return self._pack_to_read(pack, exam.packs)

    async def list_subjects(
        self,
        exam_code: str,
        *,
        pack_code: str | None = None,
        branch_key: str | None = None,
    ) -> list[EiSubjectRead]:
        await self.ensure_synced()
        exam = await self._load_exam(exam_code)
        packs = list(exam.packs)
        if pack_code:
            packs = [p for p in packs if p.code == pack_code]
        if branch_key:
            key = branch_key.strip().lower()
            packs = [p for p in packs if (p.branch_key or "").lower() == key]
        subjects: list[EiSubjectRead] = []
        for pack in packs:
            for s in sorted(pack.subjects, key=lambda x: x.display_order):
                if not s.is_active:
                    continue
                subjects.append(self._subject_to_read(s, include_topics=False))
        return subjects

    async def list_topics(
        self,
        exam_code: str,
        subject_code: str,
        *,
        pack_code: str | None = None,
    ) -> list[EiTopicRead]:
        await self.ensure_synced()
        q = (
            select(EiTopic)
            .where(
                EiTopic.exam_code == exam_code.lower(),
                EiTopic.subject_code == subject_code,
                EiTopic.is_active.is_(True),
            )
            .order_by(EiTopic.display_order, EiTopic.name)
        )
        if pack_code:
            q = q.where(EiTopic.pack_code == pack_code)
        result = await self.db.execute(q)
        topics = list(result.scalars().all())
        if not topics:
            raise NotFoundError(
                f"Topic bulunamadı: {exam_code}/{subject_code}"
            )
        return [EiTopicRead.model_validate(t) for t in topics]

    async def get_topic(self, topic_code: str) -> EiTopicRead:
        await self.ensure_synced()
        result = await self.db.execute(
            select(EiTopic).where(EiTopic.code == topic_code)
        )
        topic = result.scalar_one_or_none()
        if topic is None or not topic.is_active:
            raise NotFoundError(f"Topic bulunamadı: {topic_code}")
        return EiTopicRead.model_validate(topic)

    async def importance_ranking(
        self,
        exam_code: str,
        *,
        pack_code: str | None = None,
        limit: int = 50,
    ) -> list[EiImportanceItem]:
        await self.ensure_synced()
        q = select(EiTopic).where(
            EiTopic.exam_code == exam_code.lower(),
            EiTopic.is_active.is_(True),
        )
        if pack_code:
            q = q.where(EiTopic.pack_code == pack_code)
        q = q.order_by(EiTopic.importance_score.desc(), EiTopic.name).limit(limit)
        result = await self.db.execute(q)
        return [
            EiImportanceItem(
                topic_code=t.code,
                name=t.name,
                subject_code=t.subject_code,
                pack_code=t.pack_code,
                importance_score=t.importance_score,
                average_question_count=t.average_question_count,
                assessment_weight=t.assessment_weight,
                source=t.source,
            )
            for t in result.scalars().all()
        ]

    async def _load_exam(self, exam_code: str) -> EiExam:
        code = (exam_code or "").strip().lower()
        result = await self.db.execute(
            select(EiExam)
            .where(EiExam.code == code, EiExam.is_active.is_(True))
            .options(
                selectinload(EiExam.packs)
                .selectinload(EiPack.subjects)
                .selectinload(EiSubject.topics)
            )
        )
        exam = result.scalar_one_or_none()
        if exam is None:
            raise NotFoundError(f"Sınav bulunamadı: {exam_code}")
        return exam

    def _pack_to_read(self, pack: EiPack, all_packs: list[EiPack]) -> EiPackRead:
        children = [
            self._pack_to_read(c, all_packs)
            for c in sorted(
                [p for p in all_packs if p.parent_pack_id == pack.id and p.is_active],
                key=lambda x: x.display_order,
            )
        ]
        subjects = [
            self._subject_to_read(s, include_topics=True)
            for s in sorted(pack.subjects, key=lambda x: x.display_order)
            if s.is_active
        ]
        return EiPackRead(
            id=pack.id,
            code=pack.code,
            name=pack.name,
            display_order=pack.display_order,
            is_active=pack.is_active,
            branch_key=pack.branch_key,
            parent_pack_id=pack.parent_pack_id,
            subjects=subjects,
            children=children,
        )

    def _subject_to_read(
        self, subject: EiSubject, *, include_topics: bool
    ) -> EiSubjectRead:
        topics = []
        if include_topics:
            topics = [
                EiTopicRead.model_validate(t)
                for t in sorted(subject.topics, key=lambda x: x.display_order)
                if t.is_active
            ]
        return EiSubjectRead(
            id=subject.id,
            exam_code=subject.exam_code,
            pack_code=subject.pack_code,
            code=subject.code,
            name=subject.name,
            display_order=subject.display_order,
            is_active=subject.is_active,
            legacy_subject_code=subject.legacy_subject_code,
            topics=topics,
        )
