# Sprint-2.1 — Goal Engine & Adaptive Weekly Planning

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-16  
**Toplantı:** Meeting-019  
**Kapsam:** Goal model/API + auto progress + Flutter `goal_engine` + Dashboard/widget/notif + AI Goal okuma  
**AI Goal oluşturma:** Yok

---

## Amaç

Kullanıcıların haftalık/aylık (ve özel) hedefler tanımlaması; QuestionRecord / StudySession ile otomatik ilerleme; AI Insight Engine’in hedefleri analiz etmesi (oluşturmadan).

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A1 | Event hook + create recompute; `current_value` persist |
| B1 | Plan complete standart tiplere katkı yapmaz |
| C1 | Additive `weekly_goals` + “Bu Haftaki Hedefler” kartı; DailyGoalCard aynı |
| D1 | Backend `milestones_reached`; Flutter local notify |
| E2 | Full paket (6 yüzey + AI kuralları + widget + milestone) |
| F1 | Feature matrix **S-32 Goal Engine** = MVP |

---

## Kapsam

### Backend

| Bileşen | Durum |
|---------|-------|
| Goal model + migration `e5f6a7b8c9d0` | ✅ |
| CRUD + `/active\|completed\|progress\|weekly\|monthly` | ✅ |
| GoalProgressService hooks (QR / Session; Plan no-op) | ✅ |
| Dashboard `weekly_goals` | ✅ |
| InsightContext + RuleEngine goal kuralları | ✅ |
| Unit + integration testler | ✅ |

### Flutter

| Bileşen | Durum |
|---------|-------|
| `features/goal_engine` Clean Architecture | ✅ |
| Goals / Detail / Add / Edit (+ progress & completed sections) | ✅ |
| Dashboard weekly goals kartı + quick action | ✅ |
| Milestone local notification | ✅ |
| Widget `goal_label` | ✅ |
| Model / repository / widget testler | ✅ |

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `pytest` | 129 passed |
| `flutter analyze` (goal_engine slice) | No issues found |
| `flutter test` | 92 passed |

---

## Bilinen Sınırlamalar

- AI Goal Generator / adaptif plan üretimi yok.
- Custom goal otomatik progress almaz (manuel `current_value`).
- Subject/Topic eşlemesi string (katalog yok).
- Milestone yalnızca local; FCM yok.
- “Adaptive Weekly Planning” tam anlamıyla sonraki sprint.

---

## Bir Sonraki Sprint Önerisi

AI Goal Suggestion, Habit Engine iskeleti, veya Gemini study-coach.
