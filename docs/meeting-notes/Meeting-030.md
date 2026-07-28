# Meeting-030 — Sprint-3.0.2 Goal Experience

**Tarih:** 2026-07-17  
**Konu:** Goal ürün deneyimi + exam/revision otomatik ilerleme

## Kararlar

1. Goal Engine rewrite yok — additive `product_goal_type` + metadata progress_log.
2. Kullanıcıya 9 ürün tipi; teknik `study_time`/`pomodoro`/… formda gizlenir.
3. Primary Exam create’te SSOT; allowed exam_types dışı red.
4. Net / branş neti / deneme sayısı → `exam_recorded`; revision → `revision_reviewed`.
5. Puan / sıralama: Exam modelinde alan yok → hedef oluşturulur; otomatik ilerleme sınırlı (manuel / ileride).
6. Explain endpoint LLM’e yalnızca anlatım verir; hedef üretmez.
7. Journey progress yüzdeleri `calc_progress` ile Goal ile aynı dil.

## Risk notları

- Score/rank otomatik progress henüz deneme kaydından gelmiyor.
- Eski hedefler `product_goal_type=null` — UI infer ile gösterilir.
- Subject adı eşleşmesi (TYT/AYT aynı isim) branch_net’te dikkat.

## Teslim

Kod + migration + docs + pytest / flutter test / analyze.
