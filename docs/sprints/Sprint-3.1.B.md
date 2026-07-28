# Sprint-3.1.B — Journey Dashboard Redesign

**Durum:** Tamamlandı  
**Tür:** Product UX (Journey Hub)  
**Bağımlılık:** Sprint-3.1.A Active Exam Foundation  
**Migration:** Yok

## Amaç

Dashboard modül listesi değil; Journey Hub olacak.

Kullanıcı uygulamayı açınca: "Ben şu sınava hazırlanıyorum. Bugün ne yapmalıyım?"

## Kapsam

| # | İş | Sonuç |
|---|-----|--------|
| 1 | Hero | Active switcher + Primary hedef + journey bars + gün kalan |
| 2 | Bugünkü görevler | Plan / Pomodoro / Revision / günlük hedef |
| 3 | AI Coach kartı | RuleEngine tip + reason (LLM Explain yok) |
| 4 | Dersler preview | Kısa chip listesi → `/subjects` |
| 5 | Plan preview | Özet → `/study-plan` |
| 6 | Layout Strategy | YKS / KPSS / YDS / default |
| 7 | API additive | `primary_target`, `active_target`, `today_ai_recommendation_reason` |

## Kararlar

1. Primary hedef özeti `GET /dashboard` içinde (tek request).
2. "Neden?" / recommendation Explain → **Sprint-3.1.D**.
3. Kartlar silinmedi; Dashboard yüzeyinden demote edildi.
4. Bottom nav büyümedi.

## API (additive)

- `DashboardExamTargetSummary` → `primary_target`, `active_target`
- `AiRecommendation.reason` + dashboard `today_ai_recommendation_reason`
- Mevcut alanlar korundu; `?exam_type=` Active default

## Flutter bileşenleri

- `dashboard_hero.dart`
- `dashboard_today_tasks.dart`
- `dashboard_ai_coach.dart`
- `dashboard_subject_preview.dart`
- `dashboard_plan_preview.dart`
- `dashboard_layout_strategy.dart`

## Dışarıda

- Subject Hub, Goal UX, AI Coach ekranı / LLM Explain
- Migration / DB
- Bottom nav expansion

## Doğrulama

- pytest
- flutter test
- flutter analyze
