# Sprint-3.2.B — Topic Hub

**Durum:** Planlandı (implementasyon onayı bekliyor)  
**Tür:** Product UX + Domain (Topic öğrenme birimi)  
**Bağımlılık:** Sprint-3.2.A Topic Catalog Foundation  
**Migration:** Yok (activity `topic_code` → 3.2.C)  
**Üst vizyon:** [`docs/product/product-vision.md`](../product/product-vision.md)  
**Roadmap:** [`docs/planning/roadmap-vision-aligned.md`](../planning/roadmap-vision-aligned.md)

## Vizyon kapısı (gate)

| # | Soru | Bu sprintte cevap |
|---|------|-------------------|
| 1 | Düşünme yükünü azaltıyor mu? | Evet — konu seçince tek merkez; “hangi modüle gideyim?” azalır |
| 2 | Exam pack mi / genel modül mü? | Topic domain; Active Exam subject altındaki konular |
| 3 | Topic identity korunuyor mu? | Evet — route/API `topic_code`; display `name` |
| 4 | RuleEngine / LLM? | Değişmez; AI section placeholder veya mevcut subject AI köprüsü |
| 5 | Tekil olay mutate? | Yok — metrikler read-only / placeholder |
| 6 | Hangi yüzey? | **Topic** (Hub); Today/Journey dokunulmaz |

## Amaç

Topic seçildiğinde kullanıcı “burası öğrenme merkezi” hissetsin.

Subject Hub → Konu listesi → **Topic Hub (Detail)**.

3.2.A’daki liste yeterli değildi; detay yüzeyi yoktu. Bu sprint Topic’i ürün birimi yapar — henüz full Work Surface (3.2.D) ve activity FK (3.2.C) olmadan.

## Kapsam

| # | İş | Sonuç |
|---|-----|--------|
| 1 | API | `GET /learning-profile/topics/{topic_code}` sectioned detail (Subject Hub parity, sade) |
| 2 | Flutter | `/topics/:topicCode` → Topic Hub screen |
| 3 | Subject Hub | Konu satırına tap → Topic Hub |
| 4 | Sections | Header (prefix: TYT Matematik · Problemler), Progress placeholder, Today stub, Actions stub (soru/plan/pomodoro deep-link `?topic_code=` hazırlığı), AI stub |
| 5 | Docs + test | Sprint notu, api-design, unit/widget |

### Response şekli (öneri)

```json
{
  "topic": { "topic_code", "topic_name", "subject_code", "difficulty", "sort_order" },
  "subject": { "subject_code", "subject_name", "section" },
  "progress": { "placeholder": true },
  "today": { "placeholder": true },
  "actions": { "questions", "plans", "pomodoro", "resources", "revision" },
  "ai": { "recommendation": null, "explain_available": false }
}
```

Metrikler 3.2.C öncesi name-bridge veya boş placeholder olabilir; identity her zaman `topic_code`.

## Bilinçli hariç

- Activity tablolarına `topic_code` kolonu (→ **3.2.C**)
- Topic Work Surface tek composition (→ **3.2.D**)
- Dashboard / Today OS (→ **3.3.A**)
- Planner / Trend RuleEngine / Explain rewrite
- Flashcard / NotebookLM
- LLM davranışı

## Mimari kurallar

- Subject Catalog / Topic Catalog SSOT korunur
- Primary / Active Exam korunur
- Additive API; Subject Hub bozulmaz
- Deep-link query: `topic_code` (tüketiciler 3.2.C/D’de doldurulur; bu sprintte query taşınabilir)

## Doğrulama

- pytest: topic detail by code; unknown code 404
- flutter: Topic Hub screen + navigation from Subject Hub
- analyze clean

## Sonraki

**3.2.C** Topic Activities (`topic_code` bindings) → **3.2.D** Topic Work Surface
