# Meeting-034 — Sprint-3.2.A Topic Catalog Foundation

**Tarih:** 2026-07-19  
**Konu:** Topic Catalog (Subject Catalog parity)

## Kararlar

1. Seed-only yok — `topic_catalog` DB SSOT + `ensure_topic_catalog_synced`.
2. Küçük migration yalnızca Topic Catalog; Activity tablolarına `topic_code` yok.
3. `topic_code` = `{subject_code}__{slug}`; `name` display.
4. `subject_code` FK → `subject_catalog.code`.
5. Hub `topics` section + `GET .../subjects/{code}/topics`.
6. Topic Detail / Activity / AI / Planner / Dashboard / Flashcard → sonraki sprintler.

## Teslim

Migration `m9a0b1c2d3e4` + seed + API + Hub Topic List + tests + Sprint-3.2.A.md
