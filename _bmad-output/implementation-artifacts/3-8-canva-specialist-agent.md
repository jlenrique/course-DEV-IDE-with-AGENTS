# Story 3.8: Canva Specialist Agent (Manual-Tool Pattern)

> **Historical note (2026-04-16):** Paths of the form `<old>-specialist-sidecar/` and `bmad-agent-marcus-sidecar/` were renamed to persona-named sidecars. See `_bmad/memory/` for current paths.

Epic: 3 - Core Tool Specialist Agents & Mastery Skills
Status: done
Sprint key: 3-8-canva-specialist-agent
Completed: 2026-03-29

## Summary

Implemented the Canva specialist as a manual-tool Visual Designer with knowledge-only capability routing, explicit poll/task response contracts for Marcus delegation, sidecar memory initialization, and tracker/documentation updates to close Epic 3.

## Deliverables

- Agent definitions:
  - agents/canva-specialist.md
  - skills/bmad-agent-canva/SKILL.md

- Knowledge-only design skill:
  - skills/canva-design/SKILL.md
  - skills/canva-design/references/capability-catalog.md
  - skills/canva-design/references/template-catalog.md
  - skills/canva-design/references/pptx-import-workflow.md

- Sidecar initialization:
  - _bmad/memory/canva-specialist-sidecar/index.md
  - _bmad/memory/canva-specialist-sidecar/patterns.md
  - _bmad/memory/canva-specialist-sidecar/chronology.md
  - _bmad/memory/canva-specialist-sidecar/access-boundaries.md

- Marcus routing and status updates:
  - skills/bmad-agent-marcus/SKILL.md
  - _bmad-output/implementation-artifacts/sprint-status.yaml
  - docs/project-context.md

- Story contract tests:
  - tests/test_canva_specialist_contract.py

## Acceptance Criteria Trace

- skills/bmad-agent-canva/SKILL.md exists with Visual Designer persona and capability boundaries.
- skills/canva-design/SKILL.md exists as knowledge-only design guidance (no scripts directory).
- Canva references exist:
  - capability-catalog.md
  - template-catalog.md
  - pptx-import-workflow.md
- Poll and task response contracts are explicit for Marcus delegation.
- style-bible and style_guide usage is required in activation and output guidance.
- _bmad/memory/canva-specialist-sidecar/ is initialized with read/write/deny boundaries.
- Marcus specialist inventory lists canva-specialist as active (Story 3.8).

## Validation

- python -m pytest tests/test_canva_specialist_contract.py tests/test_exemplar_catalogs_yaml.py -q
  - Result: pass

## Party Mode and Adversarial Closure

- Party-mode consultation: completed against Story 3.8 artifacts and Marcus routing; recommendations incorporated.
- Adversarial review: findings mitigated before closure:
  - strengthened poll/task return contracts with concrete payload examples and decision fields
  - explicit sidecar access boundaries (read/write/deny) plus deny-zone rationale
  - Marcus blocked-stage recovery guidance added to conversation management
  - template search workflow made executable with concrete Canva search terms
  - configuration precedence clarified across wrapper and skill layers
  - agent registry updated in agents/README.md for discoverability
  - verification tests expanded for poll contract, payload fields, and precedence rules
- Re-check adversarial pass: no blocking findings; remaining notes are minor rigor follow-ups.
