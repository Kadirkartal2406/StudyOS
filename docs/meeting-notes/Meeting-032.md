# Meeting-032 — Sprint-3.1.C Subject Hub

**Tarih:** 2026-07-19  
**Konu:** Subject Hub Foundation (S-38)

## Kararlar

1. Subject Detail API sectioned: `subject`, `progress`, `today`, `revision`, `plans`, `exam_summary`, `resources`, `flashcards`, `ai`. Placeholder alanlar OK.
2. Flutter Hub tek widget değil; Header / Progress / Today / Revision / Planner / Exam / AI / Resources / Flashcards ayrı.
3. Deep-link: Question, Revision, Planner, Pomodoro, Exam History, Resources — hepsi `?subject_code=`.
4. Kimlik = `subject_code` only; `subject_name` Hub eşleştirmesinde kullanılmaz.
5. AI: Öneri + Sebep + Explain placeholder; Explain endpoint 3.1.D.
6. Bu sprintte migration yok; katmanlar gelecekteki `subject_code` normalizasyonuna uygun.

## Risk notları

- Legacy question/plan/revision hâlâ display name saklayabilir; bridge servis içi.
- Resources / Flashcards / Exam summary çoğu kullanıcıda placeholder.
- Hub olmadan açılan listeler eski davranışta kalır.

## Teslim

Kod + docs (Sprint-3.1.C, feature-matrix S-38, api-design/architecture) + pytest / flutter test / analyze.
