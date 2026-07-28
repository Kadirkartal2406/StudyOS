# Sprint-2.5 — Study Resources

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-17  
**Toplantı:** Meeting-023  
**Kapsam:** StudyResource CRUD + plan nested + Flutter + dashboard/AI context  
**YouTube Data API:** Yok (manuel metadata)

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A1 | Yeni `StudyResource` tablosu (Material ayrı) |
| B1 | Feature-matrix **S-31** MVP |
| C1 | Hafif Study Plan Detail + Kaynaklar |
| D1 | Hard delete |
| E1 | `completed_at` / `last_opened_at` |
| F1 | `order_index` via PATCH |
| G1 | Manuel title/thumbnail; `youtube_ready` rezerv |
| H1 | `/resources/statistics` + Flutter placeholder |
| I1 | Context `resources` + MemorySource; Writer yok |
| J1 | Dashboard 3 özet alanı + kart |

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `alembic upgrade head` | `d0e1f2a3b4c5` (study_resources + timestamp default fix) |
| `pytest` | **155 passed** |
| `flutter analyze` | 3 info (önceden var / lint), error yok |
| `flutter test` | **103 passed** |

---

## Ana Dosyalar

**Backend:** `models/study_resource.py`, `api/v1/resources.py`, nested plan routes, dashboard/context wire, migration `c9d0e1f2a3b4`  
**Flutter:** `features/study_resources/**`, plan detail, `TodayResourcesCard`, routes `/resources`  
**Docs:** feature-matrix S-31, api/database/software-architecture

---

## Bilinen Sınırlamalar

- YouTube Data API / otomatik oEmbed yok.
- S3 PDF upload yok.
- AI otomatik “şu videoyu izle” yok.
- Drag-drop reorder UI yok (`order_index` API var).
- MemoryWriter kuralları yok (yalnızca `MemorySource.STUDY_RESOURCE` + Context `resources`).
