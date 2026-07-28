# Sprint-3.0.2 — Goal Experience & Exam Goals

**Durum:** Tamamlandı  
**Tür:** Product Polish (Goal Engine rewrite yok)  
**Bağımlılık:** Sprint-3.0.1 Learning Profile SSOT

## Amaç

Goal sistemi gerçek öğrenci hedeflerini (net, puan, sıralama, deneme, revision…) destekler.
Teknik `goal_type` motor katmanında kalır; kullanıcı ürün tiplerini görür.

## Kapsam

| Hedef | Sonuç |
|-------|--------|
| 1 Ürün tipleri | 9 product_goal_type; teknik tipler UI’da gizlendi |
| 2 Primary Exam | Create’te otomatik; YKS↔KPSS karışmaz; subject filtresi |
| 3 Dinamik form | Tipe göre alanlar (net/ders/dakika/puan…) |
| 4 Dashboard kart | progress / kalan / % / tahmini tamamlanma |
| 5 Detay ekranı | why / sources / last update / progress_log + explain |
| 6 Auto progress | question / session / exam / revision hook |
| 7 Rule sadeleştirme | weekly_summary cleanup; `calc_progress` tek dil |
| 8 Explain | `POST /goals/{id}/explain` — LLM üretmez |
| 9 Journey = Goal | `calc_progress` Journey today/week/month ile paylaşılır |
| 10 Docs | Bu dosya + Meeting-030 + feature-matrix S-36 |

## Migration

**Additive:** `k7f8a9b0c1d2` — `goals.product_goal_type` (nullable + index).

## API (additive)

- `GoalCreate.product_goal_type` (opsiyonel; verilirse motor type/period eşlenir)
- `GoalRead` + `product_goal_type`, `estimated_completion`, `progress_sources`, `progress_log`, `why_created`
- `WeeklyGoalSummaryItem` + current/target/estimated
- `POST /goals/{id}/explain`

## Korunan kurallar

- LLM hedef üretmez
- RuleEngine / GoalProgressService korunur (rewrite yok)
- Mevcut `/goals` endpoint’leri bozulmaz
- Motor `goal_type` enum değişmez
