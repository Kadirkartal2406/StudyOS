# Meeting-029 — Sprint-3.0.1 Product Consistency

**Tarih:** 2026-07-17  
**Konu:** Learning Profile SSOT entegrasyonu (Product Polish)

## Kararlar

1. Primary Exam tüm modüllerin varsayılan context’i.
2. Subject metrikleri additive schema — **yeni migration yok**.
3. Edit ekranları da create ile aynı profil filtresini kullanır.
4. Revision manuel ekleme subject dropdown = `user_subjects`.
5. Dashboard `subjects_summary` insight kartı.

## Risk notları

- Free-text subject adı eşleşmesi (TYT/AYT aynı “Matematik”).
- Eski revision kartları eşleşmezse filtre geri düşer (tüm liste).

## Teslim

Kod + docs + pytest / flutter test / analyze.
