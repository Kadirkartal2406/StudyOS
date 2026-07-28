# Sprint 17 — M17.2 Resource System Audit

**Tarih:** 2026-07-22  
**Durum:** ✅ Audit + P0/P1 hardening uygulandı  
**Kural:** Yeni endpoint / migration / AI / NotebookLM yok  

---

## Verdict

StudyResource **topic-first değildi**. Storage kodları destekliyordu; list API, Work Surface, Explain context ve router topic’i düşürüyordu. Exam izolasyonu kod prefix’leriyle (`kpss_…` vs `tyt_…`) sağlanır — `exam_id` kolonu yok (bilinçli).

---

## Yüzey tablosu

| Modül | Önce | Sonra |
|-------|------|-------|
| M17.2.1 Scope / list API | ❌ `topic_code` Query yok | ✅ `GET /resources?topic_code=` |
| M17.2.2 Work Surface | ❌ subject OR leak | ✅ yalnızca `subject_code`+`topic_code` |
| M17.2.3 Explain context | ❌ subject fallback | ✅ topic-only (+ archived hariç) |
| M17.2.4 Quiz | ✅ kaynak kullanmıyor | ✅ aynı (PASS) |
| M17.2.5 Notebook | ⚠️ count vardı, UI yok | ✅ count + top 3 list |
| M17.2.6 CRUD / router | ❌ WS→create topic düşüyordu | ✅ router `topicCode` geçiyor |
| M17.2.7 Empty UX | ❌ section gizli | ✅ EmptyState + CTA |
| M17.2.8 Duplicate | ❌ sınırsız | ✅ aynı URL+topic → ValidationError |
| M17.2.9 Labels | ⚠️ sahte/kırık sort | ✅ Son kullanılan / Zayıf alan / status |
| Cross-exam | PARTIAL | ✅ topic-only + kod izolasyonu |

---

## Uygulanan düzeltmeler

### Backend
- `api/v1/resources.py` — `topic_code` query
- `learning_intelligence_service.resource_intelligence` — topic-only, archived hariç, gerçek label’lar
- `topic_context_builder` — subject fallback kaldırıldı
- `study_resource_service.create` — URL+topic dedupe
- `study_resource_repository.find_duplicate_url`

### Mobile
- `app_router` — `/resources?topic_code=`
- Work Surface — boş kaynak EmptyState
- Notebook — `resourceCount` + başlık listesi
- ResourcesScreen — konu odaklı boş metin / başlık

---

## Bilinçli bırakılanlar

| Madde | Not |
|-------|-----|
| `exam_id` kolonu | Migration yok; izolasyon `subject_code`/`topic_code` prefix |
| Soft delete | Hard delete by design |
| Quiz prompt’a kaynak enjekte | Quiz kaynak kullanmıyor (PASS) — değiştirilmedi |
| Explain system prompt’a kaynak listesi | `_suggest_resource` post-hoc; context artık topic-only |
| Global statistics strip | Scoped stats P1 — sonraki tur |

---

## Manuel test (M17.2.10)

- [ ] KPSS → Türkçe → Paragraf → 3 kaynak ekle
- [ ] Work Surface yalnızca o 3 kaynağı gösterir
- [ ] Quiz / Explain / Notebook aynı topic bağlamı
- [ ] Aynı URL’yi tekrar ekle → hata
- [ ] Kaynak sil → WS + Notebook sayısı düşer
- [ ] YKS → Türkçe → Paragraf → farklı kaynak; KPSS kaynakları görünmez
- [ ] Boş topic → EmptyState + “Kaynak ekle”

---

## Quiz notu

Quiz PromptBuilder kaynak **kullanmıyor** — topic/subject/exam metni ile üretir. Resource sızıntısı riski yok. Explain/Notebook artık topic kaynaklarıyla beslendiği için AI zinciri sağlamlaştı.
