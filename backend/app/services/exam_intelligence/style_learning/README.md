# Exam Style Learning Engine (M27.5)

Learns **how official exams think** from M27 parser outputs.  
**No LLM. No question text. No generation.**

## Pipeline

```
Official Exams
  → Parser (M27)
  → Style Learning (M27.5)   ← this package
  → Question Planner
  → Blueprint
  → Prompt Builder
  → Gemini / LLM
  → Quality Gate
  → User
```

LLM must receive a **Style Contract**, never “KPSS seviyesinde soru üret”.

## Modules

| Module | Role |
|--------|------|
| `question_intent_analyzer` | Topic question intents |
| `reasoning_pattern_analyzer` | Reasoning type mix |
| `trap_pattern_analyzer` | Distractor / trap logic |
| `reading_load_analyzer` | Reading profile |
| `bloom_distribution` | Bloom % mix |
| `difficulty_curve_builder` | Ordered difficulty curve |
| `style_cluster` | Reading-heavy / reasoning-heavy clusters |
| `style_similarity` | Topic↔topic similarity 0–1 |
| `style_contract` | Contract + validation |
| `style_profile_builder` | Assemble per-topic contract |
| `style_repository` | Read API over filesystem |
| `style_learning_engine` | End-to-end orchestration |

## Outputs

```
data/exam_style_contracts/{exam}/{subject}/{topic}/style_contract.json
data/exam_style_profiles_learned/{EXAM}.json
data/exam_style_contracts/_reports/style_learning_summary.json
```

## Run

```bash
cd backend
python -m scripts.learn_exam_styles
```

## Forbidden

- Stem / choices / explanation persistence
- Gemini / QIE / Prompt Builder changes
- Decision / Assessment / Coach / Living Plan / Flutter / API edits
