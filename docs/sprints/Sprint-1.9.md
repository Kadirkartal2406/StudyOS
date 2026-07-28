# Sprint-1.9 — Question Tracking & Performance Analytics

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-16  
**Toplantı:** Meeting-017  
**Kapsam:** QuestionRecord + `/questions` CRUD/stats + Flutter `question_tracking` + Dashboard B1

---

## Amaç

Çözülen soruların takip edilmesi, performans analizi ve gelecekte AI modülünü besleyecek veri altyapısının kurulması. Bu sprintte AI yok.

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A1 | `subject` / `topic` düz string; Subject/Topic FK yok |
| B1 | Dashboard bugünkü soru = QuestionRecord; `/statistics/*` süre odaklı kalır |
| C1 | Feature klasörü `question_tracking` |
| D2 | Tam UI (5 ekran) + Dashboard quick action + charts |
| E1 | Yeni §1.11b QuestionRecord; QuestionStatistics taslak notu |
| F1 | Activity event yok |

---

## Kapsam

### Backend

| Bileşen | Durum |
|---------|-------|
| QuestionRecord model + migration | ✅ |
| CRUD + filtre/sayfalama | ✅ |
| `/questions/statistics\|daily\|subjects\|topics\|exams` | ✅ |
| Dashboard today_questions ← QuestionRecord | ✅ |
| Unit + integration testler | ✅ |

### Flutter

| Bileşen | Durum |
|---------|-------|
| `features/question_tracking` Clean Architecture | ✅ |
| List / Add / Edit / Detail / Statistics ekranları | ✅ |
| fl_chart günlük bar | ✅ |
| Dashboard quick action + Statistics “Soru” linki | ✅ |
| Model / repository / widget testler | ✅ |

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `pytest` | 116 passed |
| `ruff check` (questions slice) | All checks passed |
| `flutter analyze` (question_tracking) | No issues found |
| `flutter test` | 78 passed |

---

## Bilinen Sınırlamalar

- Subject/Topic tabloları yok; serbest metin.
- Net formülü tüm exam_type için YKS cezası (0.25).
- Session finish otomatik QuestionRecord oluşturmaz (D3 yok).
- S-08 konu işaretleme ayrı özellik; bu sprintte yok.
- Activity `question_recorded` yok.

---

## Bir Sonraki Sprint Önerisi

Subject/Topic katalog, exam_type’a özel net formülleri, Session finish → QuestionRecord, AI analiz iskeleti.
