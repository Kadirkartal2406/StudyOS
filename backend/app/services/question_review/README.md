# Question Review AI (M30) — Chief Editor

Inspects Author output. **Never generates questions.**

## Pipeline

```
Question Author
  → Self Critic / Rewrite / Human Examiner (Author-internal)
  → Question Review AI (this package)
  → Frozen Quality Gate / Difficulty / Similarity
  → Final Question
```

## Modules

| Module | Role |
|--------|------|
| `ambiguity_detector` | Double meaning / vague asks |
| `distractor_balance` | Length / silly / duplicate options |
| `language_editor` | TR grammar / AI phrases |
| `exam_feeling_editor` | “ÖSYM yazmış olabilir” feel |
| `cognitive_load` | Unnecessary length |
| `answer_verifier` | Single correct / collisions |
| `fairness_checker` | Cues / key bias / polarity |
| `review_score` | Aggregate 0–100 |
| `review_report` | Internal metadata |
| `review_engine` | Orchestrator |

## Reject policy

`review_score < 90` → FAIL. Caller may request **one** Author rewrite, then review again.

## Forbidden

- Writing stems / choices
- Changing difficulty / style / blueprint / QIE decisions
- Touching Author / Decision / Assessment / Coach / Living Plan
