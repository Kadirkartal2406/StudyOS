# Question Author AI (M29)

Multi-step question editor. **Does not rewrite QIE / Blueprint / Difficulty / Similarity.**

## Pipeline

```
Official Exams
  → Parser
  → Style Learning
  → Style Contracts
  → Blueprint (QIE plan — frozen)
  → Question Author AI (this package)
  → Quality Gate / Difficulty / Similarity (frozen QIE gates)
  → Final Question
```

## Steps

| Module | Role |
|--------|------|
| `author_planner` | Question Plan only (no stem) |
| `question_writer` | Write stem (+ correct answer) |
| `distractor_author` | Separate wrong options by trap type |
| `self_critic` | 0–100 style/difficulty/… scores |
| `rewrite_engine` | Max 2 rewrites if thresholds fail |
| `naturalizer` | Reduce AI smell / ÖSYM tone |
| `human_examiner` | Commission verdict; reject &lt; 85 |
| `diversity_controller` | Last-500 structure dedupe |
| `calibration_author` | First-four diversity rules |
| `prompt_library` | Template library (Author-only) |
| `orchestrator` | `QuestionAuthorEngine` |

## Thresholds

- Style ≥ 85
- Difficulty ≥ 70
- Distractor ≥ 80 → else rewrite (≤ 2)
- Human Examiner ≥ 85 → else reject

## Internal metadata (not user-facing)

`author_score`, `critic_score`, `rewrite_count`, `exam_feeling`, `style_score`,
`difficulty_score`, `naturalness`, `reasoning_score`, `distractor_score`,
`reading_time`, `ai_confidence`

## Usage

```python
from app.services.question_author import QuestionAuthorEngine

engine = QuestionAuthorEngine(use_llm=True)
authored = await engine.author_batch(qie_plans, ctx=generate_context)
```

QIE Orchestrator calls this thinly, then still runs frozen quality / difficulty / similarity gates.
