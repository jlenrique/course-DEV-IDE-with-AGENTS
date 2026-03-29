---
name: qualtrics-assessment
description: Qualtrics assessment orchestration and objective-trace verification. Use when creating course surveys, knowledge checks, and educational measurement forms in Qualtrics.
---

# Qualtrics Assessment

## Purpose

Provides deterministic Qualtrics assessment operations for the Qualtrics specialist (Assessment Architect). This skill orchestrates the shared QualtricsClient from scripts/api_clients/qualtrics_client.py, validates learning-objective traceability, creates surveys and questions, and returns structured output for Marcus and human review.

## Key Paths

| Path | Purpose |
|---|---|
| ./references/question-catalog.md | Question types and educational suitability guidance |
| ./scripts/qualtrics_operations.py | Validation and creation engine for objective-traceable assessments |

## Script Index

| Script | Purpose | Invoked By |
|---|---|---|
| qualtrics_operations.py | Validates assessment plans, creates surveys/questions, emits objective trace summary | skills/bmad-agent-marcus/references/specialist-registry.yaml entry qualtrics-specialist |

## Output Contract

qualtrics_operations.py returns structured JSON with:
- status: created | warning | blocked | failed | dry-run
- survey_id
- survey_name
- objective_trace
- created_question_ids
- warnings
- errors

## Style Preferences

Assessment defaults are loaded from state/config/style_guide.yaml under tool_parameters.qualtrics:
- default_survey_language
- question_numbering
- progress_bar

## Verification

- Objective mapping is required for every question.
- Missing or unknown objective references block creation.
- Dry-run mode provides full traceability checks without API writes.
