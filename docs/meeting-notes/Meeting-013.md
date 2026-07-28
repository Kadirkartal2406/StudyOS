# Meeting-013 — Sprint-3.0 Post-Revision (Bug Fix + UX)

**Tarih:** 2026-07-17  
**Durum:** Implementasyon tamamlandı (additive)

## Deneme hatası (kök neden)

1. Backend `total_net` / `net_score` Decimal → JSON string (`"9.50"`); Flutter `as num?` TypeError (201 sonrası parse).
2. Form `question_count: 0` gönderebiliyordu → 422.

**Düzeltme:** Pydantic float serializer + Flutter `_asDouble` + sıfır satırları atlama.

## Post-revision kapsam

| # | Değişiklik |
|---|------------|
| 2 | Subject catalog TYT/AYT/KPSS/YDS zenginleştirme + `section`; Derslerim ekranı |
| 3–5 | Primary exam varsayılan; Exam/Question/Goal/Planner formları filtrelendi |
| 6 | `goals.exam_type` (nullable, additive) |
| 7 | Dashboard `my_subjects` + Derslerim kartı |
| 8 | Learning Profile / exam_targets yeniden yazılmadı |

## Migration

`j6e7f8a9b0c1` — `subject_catalog.section`, catalog upsert, legacy deaktif, `goals.exam_type`

## Korunan kurallar

- LLM plan/hedef/ders üretmez
- RuleEngine journey/achievements
- Multi-exam (`exam_targets` 1:N) bozulmadı; primary varsayılan context
