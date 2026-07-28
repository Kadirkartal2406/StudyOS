# Sprint-3.2.A — Topic Catalog Foundation

**Durum:** Tamamlandı  
**Tür:** Domain model (Topic Catalog)  
**Bağımlılık:** Sprint-3.1.C / 3.1.C.x Subject Catalog  
**Migration:** Yalnızca `topic_catalog` tablosu (`m9a0b1c2d3e4`)  
**Feature:** Topic Foundation

## Domain ilkesi

Topic Catalog, Subject Catalog ile aynı mimaridir ve uzun vadeli domain modelidir
(Topic Hub, Activities, AI, Planner temeli). Identity = `topic_code`.

## Mimari

```
TOPIC_CATALOG_SEED
  → ensure_topic_catalog_synced (DB upsert)
  → topic_catalog (SSOT)
  → GET .../subjects/{code}/topics + Hub.topics
  → Subject Hub Topic List (Flutter)
```

## Kapsam

| Dahil | Hariç |
|-------|--------|
| `topic_catalog` migration | Activity `topic_code` kolonları |
| Seed + ensure sync | Topic Detail ekranı |
| Topic API + Hub section | Planner / AI / Dashboard rewrite |
| Flutter Hub Topic List | Flashcard / Question / Revision / Goal |

## Tablo

`topic_catalog`: `code`, `name`, `subject_code` (FK → `subject_catalog.code`),
`sort_order`, `difficulty`, `is_active`, `created_at`

## Sonraki sprintler

**3.2.B** Topic Hub · **3.2.C** Topic Activities · **3.2.D** Topic Work Surface  

Vizyon: [`docs/product/product-vision.md`](../product/product-vision.md) · Roadmap: [`docs/planning/roadmap-vision-aligned.md`](../planning/roadmap-vision-aligned.md)
