# Sprint M32 — Production Readiness & Cost Optimization Report

**Date:** 2026-07-28  
**Scope:** Cost / safety / cache only — frozen engines (Author/QIE/Review/VSSE/Decision/Living Plan/Assessment/Coach/Blueprint) not rewritten.

## Deliverables

| ID | Item | Status |
|----|------|--------|
| P0 | Auto AI elimination (dev) | Done |
| P1 | Feature flags | Done |
| P2 | Question Pool cache | Done |
| P3 | Compact author (1 LLM / question) | Done (thin adapter; Review/VSSE unchanged) |
| P4 | Gemini max 1 fallback | Done |
| P5 | Request deduplication | Done (in-process single-flight) |
| P6 | Batch generate API | Done `POST /api/v1/ai/cost/batch-generate` |
| P7 | AI cost logger CSV+JSON | Done `data/ai_cost/` |
| P8 | Daily budget / pool-only | Done (`AI_DAILY_REQUEST_BUDGET=1000`) |
| P9 | Cost metrics API | Done `GET /api/v1/ai/cost/metrics` |
| P10 | No frozen-engine behavior rewrite | Done |

## Feature flags (defaults = off for auto AI)

```
ENABLE_AUTO_BOOKLET=false
ENABLE_BACKGROUND_AI=false
ENABLE_MIDNIGHT_SCHEDULER=false
ENABLE_CATCHUP=false
ENABLE_AI_WARMUP=false
ENABLE_COMPACT_AUTHOR=true
AI_GEMINI_MAX_FALLBACKS=1
AI_DAILY_REQUEST_BUDGET=1000
```

## Startup AI requests

- With defaults: **0 Gemini** on backend boot.
- Midnight / catch-up / booklet loops do not start unless flags are explicitly `true`.
- Style seed warmup skipped when `ENABLE_AI_WARMUP=false`.

## Scheduler status

- `midnight_booklet_loop` gated; returns immediately when flags off.
- Dual uvicorn no longer burns Gemini on startup catch-up.

## Gemini calls / quiz (estimate)

| Path | Calls / question (before) | After M32 |
|------|---------------------------|-----------|
| Full Author pipeline | ~6–8 | — |
| Compact author (default) | — | **1** (+ frozen Review/VSSE local, no Gemini) |
| Pool hit | — | **0** |
| Batch API (20 Q) | 20× pipeline | **1** Gemini for up to 20 |

## Cache

- Table: `question_pool_cards` (migration `s32_ai_cost_question_pool`)
- Flow: Quiz → pool fingerprint → hit return / miss Author → persist pool
- Metrics: pool hit %, author calls, gemini calls, avg latency via `/ai/cost/metrics`

## Estimated cost drop

- Dev idle: **~100%** (no auto booklet retries every 30m)
- Repeat quiz same topic/difficulty: **~100%** on pool hit
- First quiz: **~75–85%** fewer Gemini calls via compact author (8→1)
- Batch prewarm: **~95%** vs 20× single calls

## Production ready checklist

- [x] Dev startup = 0 auto Gemini
- [x] Schedulers flag-gated
- [x] Question pool + dedup
- [x] Fallback limit = 1
- [x] Daily budget → pool-only
- [x] Cost logs under `data/ai_cost/`
- [x] Metrics endpoint
- [ ] Set production flags intentionally when enabling nightly booklets
- [ ] Monitor `/ai/cost/metrics` after first real traffic

## Tests

- `tests/unit/test_m32_ai_cost.py` — flags, fallback limit, fingerprint, dedup, metrics, scheduler idle, null author block
