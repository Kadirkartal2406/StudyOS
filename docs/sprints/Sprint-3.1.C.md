# Sprint-3.1.C — Subject Hub Foundation

**Durum:** Tamamlandı  
**Tür:** Product UX (Subject work center)  
**Bağımlılık:** Sprint-3.1.A Active Exam + Sprint-3.1.B Journey Hub  
**Migration:** Yok  
**Feature:** S-38

## Amaç

Her ders için tek giriş noktası: Subject Hub. Kimlik `subject_code`; ileride normalizasyona hazır, bu sprintte migration yok.

## Kapsam

| # | İş | Sonuç |
|---|-----|--------|
| 1 | Detail API | `GET /learning-profile/subjects/{subject_code}` sectioned response |
| 2 | List filter | `GET .../subjects/me?exam_type=` Active Exam default |
| 3 | Flutter Hub | Header / Progress / Today / Revision / Planner / Exam / AI / Resources / Flashcards widget'ları |
| 4 | Deep-link | `?subject_code=` → Questions, Revisions, Study Plan, Planner, Pomodoro, Exams, Resources |
| 5 | Dashboard | Ders preview chip → `/subjects/{code}` |
| 6 | AI section | Öneri + Sebep + Explain placeholder (`explain_available=false`) |

## Response şekli

```json
{
  "subject": {},
  "progress": {},
  "today": {},
  "revision": {},
  "plans": {},
  "exam_summary": {},
  "resources": {},
  "flashcards": {},
  "ai": {}
}
```

Boş alanlar placeholder olabilir (`resources`, `flashcards`, Explain).

## Kararlar

1. Hub kimliği yalnızca `subject_code`; `subject_name` eşleştirme için kullanılmaz.
2. Legacy activity bridge (questions/plans/revisions) servis içinde name ile kalabilir; API yüzeyi code odaklı.
3. Explain endpoint → **Sprint-3.1.D**.
4. Bottom nav değişmedi; Flashcard engine / Resource subject kolonu yok.

## Flutter yüzey

- Route: `/subjects/:subjectCode`
- Widgets: `subject_hub_sections.dart`
- Resolver: `subject_code_resolver.dart` (legacy list filter bridge)

## Dışarıda

- DB migration / subject_code normalize
- LLM Explain
- Flashcard motoru
- Bottom-nav Subject tab

## Doğrulama

- `pytest` (unit `test_subject_hub`)
- `flutter test` / `flutter analyze`
