# Sprint 12 — AI Explain (LLM Karar Değil, Açıklar)

**Durum:** ✅ Tamamlandı  
**Tarih:** 2026-07-20

## Yapılanlar

- `POST /ai/explain` — observation + exam context ile 1-2 cümle Türkçe açıklama
- Duplicate `/explain` handler kaldırıldı; tek zengin endpoint kaldı
- Chat / explain LLM karar üretmez; mevcut reason'ı diline çevirir
- Mobil Next Action "Neden?" butonu explain drawer açar
