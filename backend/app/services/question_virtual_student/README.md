# Virtual Student Simulation Engine (M31)

Students-as-solvers quality layer. **Never generates questions.**

## Pipeline

```
Author AI
  → Review AI
  → Virtual Student (this package)
  → Review (optional, max 1 bounce)
  → Frozen Gates
  → QuestionCard
```

## Profiles

High Performer, Average, Weak, Fast/Slow Reader, Careless, Overthinker,
Rule Memorizer, Inference Thinker.

## Outputs (internal)

`student_profiles`, `confusion_score`, `ambiguity_probability`,
`reading_time_prediction`, `thinking_time_prediction`, `distractor_attraction`,
`solve_distribution`, `virtual_student_score`

## Reject examples

Multiple interpretations, two plausible answers, distractor imbalance,
very high reading load, too obvious answer, extremely misleading distractor,
unfair wording, artificial language.

## Forbidden

Do not modify Author, Review, QIE engines, Decision, Assessment, Style Learning.
