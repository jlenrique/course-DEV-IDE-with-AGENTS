# Qualtrics Question Catalog

Use this reference to select question formats aligned with educational intent.

## Core Types

| Type | Qualtrics Code | Best Use | Notes |
|---|---|---|---|
| Multiple choice (single answer) | MC + SAVR | Knowledge checks with one correct answer | Keep distractors plausible and concise |
| Multiple choice (multi-answer) | MC + MAVR | Multi-select conceptual understanding | State expected number of choices if constrained |
| Text entry | TE + SL | Reflection, rationale, open response | Use scoring rubric downstream if graded |
| Matrix/Likert | Matrix + Likert | Course evaluations and attitude measures | Avoid overlong matrices; keep scale labels explicit |

## Objective Mapping Rules

1. Every question must include learning_objective_id.
2. learning_objective_id must map to an objective declared in the plan.
3. If one objective has no mapped questions, block the plan as incomplete.

## Pattern Guidance

- Knowledge check: prioritize MC single answer for reliability.
- Short formative pulse: mix one MC + one TE item.
- Course evaluation: Likert matrix + optional TE comment prompt.

## Common Anti-Patterns

- Objective not stated in item stem context.
- Overlapping distractors that reduce measurement validity.
- Matrix questions with inconsistent scale semantics.
