# Story 18.2: Content Type Discovery — Quizzes & Assessments

**Epic:** 18 — Additional Assets & Workflow Families
**Status:** backlog
**Sprint key:** `18-2-discovery-quizzes-assessments`
**Added:** 2026-04-06
**Depends on:** Core pipeline stability. Existing Qualtrics and Canvas specialist agents.

## Summary

Discovery-first story: elicit detailed requirements for quiz and assessment content production. The APP already has both a Qualtrics specialist (`skills/bmad-agent-qualtrics-specialist/` + `skills/qualtrics-assessment/`) and a Canvas specialist (`skills/bmad-agent-canvas/` + `skills/canvas-deployment/`), so this discovery should build heavily on existing tooling rather than creating new infrastructure.

## Goals

1. Define assessment types: formative, summative, diagnostic, self-check, peer review prompt.
2. Define item types: multiple choice, short answer, matching, essay prompt, scenario-based.
3. Specify alignment requirements: Bloom's taxonomy mapping, learning objective traceability.
4. Map agent roles leveraging existing specialists.
5. Define quality review requirements: distractor analysis, difficulty calibration, bias review.
6. Define output formats leveraging existing platform tooling.
7. Define the workflow family.

## Existing Infrastructure To Reuse

- `skills/qualtrics-assessment/` — Qualtrics assessment creation skill (survey-type items, rubrics)
- `skills/bmad-agent-qualtrics-specialist/` — Assessment Architect agent (Story 3.7)
- `scripts/api_clients/qualtrics_client.py` — Qualtrics API client (survey CRUD, questions, responses)
- `skills/canvas-deployment/` — Canvas deployment skill (modules, assignments, quizzes)
- `skills/bmad-agent-canvas/` — Deployment Director agent (Story 3.6)
- `scripts/api_clients/canvas_client.py` — Canvas API client (quiz creation, question banks)
- `skills/bmad-agent-content-creator/` (Irene) — learning objective alignment, Bloom's taxonomy mapping
- `skills/bmad-agent-quality-reviewer/` (Quinn-R) — quality review for assessment validity
- `skills/research-services/` (Epic 17) — hypothesis research for scenario-based items
- Existing content-standards.yaml — accessibility requirements for assessments

## Key Files

- `_bmad-output/planning-artifacts/discovery-quizzes-assessments.md` — new: requirements document (deliverable)
- `_bmad-output/planning-artifacts/epics.md` — update: implementation stories added after approval

## Acceptance Criteria

1. Requirements document covers all seven goals above.
2. Assessment type taxonomy includes at least: formative quiz, summative exam, diagnostic pre-test, self-check, peer review rubric/prompt.
3. Item type taxonomy includes at least: multiple choice, short answer, matching, essay prompt, scenario-based.
4. Alignment section specifies how Bloom's taxonomy and learning objectives are validated per item.
5. Agent role matrix shows how existing Qualtrics specialist, Canvas specialist, Irene, and Quinn-R participate — avoids creating new agents where existing ones suffice.
6. Quality review section addresses: distractor quality, difficulty calibration, bias/sensitivity review, accessibility compliance.
7. Output format section covers: Qualtrics survey export, Canvas quiz (native), standalone document/question bank, and item exchange format.
8. Workflow family definition compatible with structural-walk manifest pattern.
9. Document reviewed and approved by operator before implementation stories are created.
