# Sprint 14 — Topic Quiz Generation (LLM → Evidence)

**Durum:** ✅ Tamamlandı  
**Tür:** Feature Sprint (LOS §10)  
**Tarih:** 2026-07-22  
**Önkoşul:** Sprint 5–13 ✅  
**Referans:** LOS v2.0 §10

---

## Onaylanan kararlar

| Soru | Karar |
|------|--------|
| Provider | **LLM Quiz** (NotebookLM adapter sonra) |
| Work Surface | **Secondary Tool** — “Bu konu için soru üret” |
| Çözüm UI | **Yeni Quiz Session ekranı** (Soru Kaydı formu değil) |

---

## Kalite katmanı (zorunlu)

LLM çıktısı kullanıcıya gösterilmeden önce backend doğrular:

1. JSON şeması geçerli
2. Her soru tam **4 şık** (A–D)
3. Tam **1 doğru cevap** (şık anahtarlarından biri)
4. Soru metni / şıklar boş değil, makul uzunluk
5. Topic uyumu (subject/topic adları prompt’ta + soft check)
6. Geçersiz item’lar elenir; geçerli kalan **sıfır** ise üretim reddedilir (retry 1x)

Provider değişse bile aynı `QuizQualityGate` uygulanır.

---

## Alignment Goal

Intent → System Prompt Builder → LLM → **Quality Gate** → Topic bind → Quiz Session → Evidence. Prompt yok. Decide yok. Tek quiz Living Plan değiştirmez.

---

## Modüller

- M14.1 Model + migration + API ✅
- M14.2 Prompt builder + LLM adapter ✅
- M14.3 Quality Gate ✅
- M14.4 Submit → Evidence ✅
- M14.5 Mobile: secondary tool + Quiz Session screen ✅

## API

- `POST /api/v1/topic-quiz/subjects/{subject}/topics/{topic}/generate`
- `GET /api/v1/topic-quiz/{generation_id}`
- `POST /api/v1/topic-quiz/{generation_id}/submit`
