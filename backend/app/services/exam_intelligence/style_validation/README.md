# Style Validation & Benchmark (M27.6)

Quality gate for M27.5 Style Contracts. **No generation. No LLM. No frozen-engine edits.**

## Pipeline

```
Official Exams
  → Parser (M27)
  → Style Learning (M27.5)
  → Style Validation (M27.6)  ← this package
  → Question Author AI (M28)
  → Prompt Builder
  → Gemini
```

## Modules

| Module | Role |
|--------|------|
| `contract_validator` | Required Style Contract fields |
| `similarity_validator` | Expected high/low similarity pairs |
| `cluster_validator` | Reading / reasoning cluster membership |
| `difficulty_validator` | Abrupt curve jumps |
| `reasoning_validator` | Exam reasoning family checks |
| `trap_validator` | Distractor profile checks |
| `reading_validator` | Reading profile consistency |
| `bloom_validator` | Bloom sum ≈ 100% |
| `quality_score` | 0–100 weighted score |
| `validation_report` | Markdown report |
| `validation_repository` | Read API over artifacts |
| `benchmark_runner` | Orchestrates all exams |

## Run

```bash
cd backend
python -m scripts.validate_exam_styles
```

## Outputs

```
data/style_validation/
  summary.json
  quality_scores.json
  cluster_report.json
  similarity_report.json
  difficulty_report.json
  warnings.json
  validation.md
```

M28 should start only when `summary.json` → `m28_ready: true`.
