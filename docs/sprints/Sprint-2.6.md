# Sprint-2.6 — Exam & Mock Exam Engine

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-17  
**Toplantı:** Meeting-024  
**Kapsam:** Öğrenci deneme CRUD + sonuçlar + istatistik/trend + Flutter + dashboard/AI context  
**Kurumsal K-14:** Yok (ayrı)

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A1 | Yeni öğrenci `exams` / `exam_results` (kurumsal § dokunulmadı) |
| B2 | API prefix **`/exams`** |
| C1 | Feature-matrix **S-13 → MVP** |
| D1 | Create nested results + `PUT /exams/{id}/results` |
| E1 | Hard delete + CASCADE |
| F2 | `ExamType` = QuestionRecord enum |
| G1 | Default QT net + strategy hook |
| H1 | Context/Prompt `exams`; MemorySource; Writer yok |
| I1 | Activity `exam_completed` (metadata exam_id) |
| J1 | Local milestone (ilk / 10. / rekor) |
| K1 | Goal’e yazılmaz |
| L1 | Dashboard additive + AI özet alanı |

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `alembic upgrade head` | `e1f2a3b4c5d6` |
| `pytest` | **158 passed** |
| `flutter analyze` | error yok (info/warning) |
| `flutter test` | **106 passed** |

---

## Bilinen Sınırlamalar

- Kurumsal Exam (K-14) yok.
- Konu bazlı derin deneme analizi yok.
- MemoryWriter otomatik kayıt yok.
- FCM push yok (local milestone only).
- Goal entegrasyonu yok (K1).
- Exam-type’a özel net formülü yok (hook hazır).
