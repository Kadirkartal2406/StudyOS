# Sprint 15 — Learning Intelligence & Personalized Study Feed

**Durum:** ✅ Tamamlandı  
**Tür:** Feature Sprint (ürün — altyapı değil)  
**Tarih:** 2026-07-22  
**Önkoşul:** Sprint 1–14 ✅  
**Referans:** LOS v2.0 — Sense → Evidence → Confidence → Decide (Decide değişmez)

---

## Sprint Goal

StudyOS yalnızca veri toplayan bir uygulama gibi görünmemeli. Kullanıcı:

> "Bu sistem beni gerçekten tanıyor."

hissini yaşamalıdır.

**Bu sprintte hiçbir yeni Decision algoritması yazılmaz.**  
RuleEngine, Confidence, Evidence, Living Plan davranışı değişmez.  
Yalnızca mevcut verinin kullanıcıya sunuluş biçimi geliştirilir.

---

## Modüller

| Modül | Durum |
|-------|--------|
| M15.1 Topic Intelligence Card | ✅ |
| M15.2 Learning Timeline | ✅ |
| M15.3 AI Insight Card | ✅ |
| M15.4 Personalized Home Feed | ✅ |
| M15.5 Quiz History | ✅ |
| M15.6 Resource Intelligence | ✅ |
| M15.7 Journey trends | ✅ |
| M15.8 Dashboard Polish | ✅ |

## Uygulama notları

- Backend: `LearningIntelligenceService` — read-only projection
- Work Surface: intelligence / timeline / insights / quiz_history / resources
- Dashboard: `learning_feed` + `insight_cards`
- API: `GET /topic-quiz/.../history`, `GET /learning-profile/journey/trends`
- Yeni tablo / Decision motoru yok

## Yapılmayanlar (bilinçli)

Yeni Decision / Observation / Confidence / Living Plan / NotebookLM / AI Provider / Navigation rewrite
