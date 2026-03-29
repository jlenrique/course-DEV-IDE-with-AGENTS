# Story 3.6: Canvas Specialist Agent & Mastery Skill

**Epic:** 3 — Core Tool Specialist Agents & Mastery Skills  
**Status:** done  
**Sprint key:** 3-6-canvas-specialist-agent  
**Completed:** 2026-03-29

## Summary

Built the Canvas specialist "Deployment Director" through the six-phase bmad-agent-builder process, implemented the `canvas-deployment` mastery skill with deterministic deployment orchestration and accessibility gating, and completed a live woodshed exemplar reproduction with retained run-log artifacts.

## Six-Phase Builder Trace

- **Phase 1 (Intent):** Canvas LMS deployment specialist with compliance-first release behavior.
- **Phase 2 (Capabilities):** External-skill primary model (`skills/canvas-deployment/`) plus internal deployment planning, accessibility pre-check, and structure verification routing.
- **Phase 3 (Requirements):** Persona, communication style, principles, sidecar memory, and access boundaries captured from Story 3.6 discovery answers.
- **Phase 4 (Draft & Refine):** Agent/skill structure aligned with existing specialist patterns and Marcus delegation contracts.
- **Phase 5 (Build):** Agent file, skill references, scripts, tests, sidecar files, exemplar files, and woodshed compatibility fixes implemented.
- **Phase 6 (Summary):** Party-mode and adversarial review passes executed; findings mitigated before completion.

## Deliverables

- Agent definition:
  - `agents/canvas-specialist.md`
- New mastery skill:
  - `skills/canvas-deployment/SKILL.md`
  - `skills/canvas-deployment/references/deployment-workflows.md`
  - `skills/canvas-deployment/references/institutional-requirements.md`
  - `skills/canvas-deployment/references/token-management.md`
  - `skills/canvas-deployment/scripts/canvas_operations.py`
  - `skills/canvas-deployment/scripts/tests/test_canvas_operations.py`
- Canvas API helper hardening:
  - `scripts/api_clients/canvas_client.py` (`reproduce_course_snapshot`)
- Woodshed reliability fixes:
  - `skills/woodshed/scripts/reproduce_exemplar.py` (import path + .env hydration)
- Exemplar and run artifacts:
  - `resources/exemplars/canvas/_catalog.yaml`
  - `resources/exemplars/canvas/L1-course-structure-snapshot/brief.md`
  - `resources/exemplars/canvas/L1-course-structure-snapshot/reproduction-spec.yaml`
  - `resources/exemplars/canvas/L1-course-structure-snapshot/source/reference-snapshot-schema.yaml`
  - `resources/exemplars/canvas/L1-course-structure-snapshot/reproductions/2026-03-29_013800/run-log.yaml`
  - `resources/exemplars/canvas/L1-course-structure-snapshot/reproductions/2026-03-29_013800/output/api_response.json`
  - `resources/exemplars/canvas/L1-course-structure-snapshot/reproductions/2026-03-29_013800/comparison.yaml`
- Sidecar initialization and governance:
  - `_bmad/memory/canvas-specialist-sidecar/index.md`
  - `_bmad/memory/canvas-specialist-sidecar/patterns.md`
  - `_bmad/memory/canvas-specialist-sidecar/chronology.md`
  - `_bmad/memory/canvas-specialist-sidecar/access-boundaries.md`
- Marcus integration updates:
  - `skills/bmad-agent-marcus/SKILL.md`
  - `skills/bmad-agent-marcus/references/conversation-mgmt.md`

## Acceptance Criteria Trace

- `agents/canvas-specialist.md` exists with Deployment Director persona and Canvas REST API routing.
- `skills/canvas-deployment/SKILL.md` exists and routes to deterministic deployment operations.
- `deployment-workflows.md` covers pages, quizzes, discussions, assignments, and modules.
- `institutional-requirements.md` captures policy/compliance enforcement points.
- `skills/canvas-deployment/scripts/` imports and orchestrates shared Canvas client.
- Accessibility validation executes before deployment writes (`run_accessibility_precheck`).
- Deployment output includes confirmation URLs and module structure verification fields.
- `_bmad/memory/canvas-specialist-sidecar/` is initialized and populated.
- Party-mode review performed and findings evaluated.
- At least one Canvas exemplar exists and is cataloged.
- Exemplar reproduction completed via Canvas API using woodshed workflow.
- Reproduction retained run-log + artifact output.

## Validation

- `python -m pytest skills/canvas-deployment/scripts/tests/test_canvas_operations.py tests/test_canvas_snapshot_helper.py -q`
  - Result: `14 passed`
- `python -m pytest tests/test_integration_canvas.py --run-live -q`
  - Result: `4 passed`
- `python skills/woodshed/scripts/reproduce_exemplar.py canvas L1-course-structure-snapshot --session-attempt 3`
  - Result: `status: completed` with response status `200` in run-log.
- Builder lint gate:
  - `scan-path-standards.py skills/canvas-deployment` -> `pass`
  - `scan-scripts.py skills/canvas-deployment` -> `pass`

## Adversarial Review & Mitigation

Adversarial findings were reviewed and mitigated before closure:

- Hardened woodshed import/env behavior in `reproduce_exemplar.py` (fixed failed attempt causes).
- Added robust error/validation handling in `reproduce_course_snapshot` helper.
- Added duplicate-module manifest validation in `canvas_operations.py`.
- Expanded tests for:
  - duplicate module-name rejection,
  - out-of-order module verification failure,
  - partial rollback failure reporting,
  - invalid course_id handling in snapshot helper.

## Completion Notes

Story 3.6 is complete and integrated. Canvas specialist capability is now active in Marcus routing, with deterministic deployment tooling and verified woodshed exemplar retention.
