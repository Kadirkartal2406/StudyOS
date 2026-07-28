# Meeting-031 — Sprint-3.1.B Journey Dashboard

**Tarih:** 2026-07-18  
**Konu:** Journey Hub redesign + Active layout

## Kararlar

1. Hero Primary hedef özeti `GET /dashboard` response'una additive eklenir (`primary_target` / `active_target`). Flutter ikinci profil isteğiyle Hero compose etmez.
2. AI Coach kartı bu sprintte yalnızca RuleEngine `reason`/`evidence` gösterir. Recommendation Explain endpoint ve gerçek "Neden?" akışı Sprint-3.1.D'ye ertelenir.
3. Dashboard 5 bölüm: Hero → Bugünkü görevler → AI tip → Ders preview → Plan preview.
4. Revision / Achievement / Activity / Last Exam / Weekly Goals / Quick Actions / OS kartları Dashboard'dan kaldırılır; kendi ekranları durur.
5. Layout Strategy (YKS / KPSS / YDS / default) Active Exam'e göre; Primary değişmez.
6. Migration yok; API kırılmaz; bottom nav büyümez.

## Risk notları

- Eski istemciler yeni alanları yok sayabilir (additive).
- `days_remaining` hâlâ Primary `exam_date` üzerinden (Journey Engine).
- LLM Explain olmadan reason kısa RuleEngine metnidir.

## Teslim

Kod + docs (Sprint-3.1.B, feature-matrix S-37, api-design/architecture notları) + pytest / flutter test / analyze.
