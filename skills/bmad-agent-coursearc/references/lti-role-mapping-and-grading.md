# LTI Role Mapping and Grading Guide

Use this guide with the LTI embedding checklist for role validation and grade-passback decisions.

## Role Mapping Baseline

| Canvas Role | LTI Role Expectation | Validation Action |
|---|---|---|
| Instructor | Instructor-level launch privileges | Validate deep-link and management launch paths |
| Teaching Assistant | Course support launch privileges | Validate content access and moderation controls |
| Student | Learner launch privileges | Validate assignment/module launch and completion flow |

## Grade Passback Decision Logic

1. Is grading required for this activity?
2. If yes, verify LTI grade service capability in Canvas and CourseArc settings.
3. If grade passback is unavailable, document fallback behavior (manual grading or completion-only tracking).
4. Record final grading decision in deployment handoff notes.

## Recovery Guidance

- If role launch fails, verify Canvas deployment role settings and CourseArc role mapping.
- If grade passback fails, check assignment settings and LTI service permissions, then retry in test shell.
