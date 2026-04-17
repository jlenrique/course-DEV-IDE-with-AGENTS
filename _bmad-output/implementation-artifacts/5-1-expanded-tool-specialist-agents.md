# Story 5.1: Expanded Tool Specialist Agents (Vyond, Midjourney, Articulate)

> **Historical note (2026-04-16):** Paths of the form `<old>-specialist-sidecar/` and `bmad-agent-marcus-sidecar/` were renamed to persona-named sidecars. See `_bmad/memory/` for current paths.

Epic: 5 - Tool Capability Expansion
Status: done
Sprint key: 5-1-expanded-tool-specialist-agents
Completed: 2026-03-29

## Summary

Closed Story 5.1 by finalizing manual-tool specialist wrappers for Vyond, Midjourney, and Articulate; hardening specialist contracts and references; adding review-signoff and payload-schema evidence artifacts; and validating closure via targeted contract tests and adversarial re-check.

## Deliverables

- Wrapper agents:
  - agents/vyond-specialist.md
  - agents/midjourney-specialist.md
  - agents/articulate-specialist.md

- Specialist skill hardening:
  - skills/bmad-agent-vyond/SKILL.md
  - skills/bmad-agent-midjourney/SKILL.md
  - skills/bmad-agent-articulate/SKILL.md

- New and expanded reference artifacts:
  - skills/bmad-agent-articulate/references/wcag-2-1-aa-interactive-checklist.md
  - skills/bmad-agent-articulate/references/scorm-export-review-checklist.md
  - skills/bmad-agent-midjourney/references/parameter-catalog-v6-v7.md

- Sidecar memory updates:
  - _bmad/memory/vyond-specialist-sidecar/patterns.md
  - _bmad/memory/vyond-specialist-sidecar/chronology.md
  - _bmad/memory/midjourney-specialist-sidecar/patterns.md
  - _bmad/memory/midjourney-specialist-sidecar/chronology.md
  - _bmad/memory/articulate-specialist-sidecar/patterns.md
  - _bmad/memory/articulate-specialist-sidecar/chronology.md

- Validation and evidence artifacts:
  - tests/test_manual_tool_specialist_contracts.py
  - tests/agents/bmad-agent-vyond/interaction-test-guide.md
  - tests/agents/bmad-agent-midjourney/interaction-test-guide.md
  - tests/agents/bmad-agent-articulate/interaction-test-guide.md
  - tests/agents/bmad-agent-vyond/review-sign-off.md
  - tests/agents/bmad-agent-midjourney/review-sign-off.md
  - tests/agents/bmad-agent-articulate/review-sign-off.md
  - tests/agents/bmad-agent-vyond/sample-guidance-response.yaml
  - tests/agents/bmad-agent-vyond/sample-blocked-response.yaml
  - tests/agents/bmad-agent-midjourney/sample-guidance-response.yaml
  - tests/agents/bmad-agent-midjourney/sample-blocked-response.yaml
  - tests/agents/bmad-agent-articulate/sample-guidance-response.yaml
  - tests/agents/bmad-agent-articulate/sample-blocked-response.yaml

- Registry/docs updates:
  - agents/README.md
  - _bmad-output/implementation-artifacts/sprint-status.yaml
  - docs/project-context.md

## Acceptance Criteria Trace

- Three Story 5.1 specialist wrappers exist and route to `skills/bmad-agent-*` skill files.
- Manual-tool boundary is explicit in skills and wrappers (no API runtime execution).
- Human review sign-off artifacts exist with named reviewer accountability and evidence links.
- Articulate WCAG 2.1 AA interaction checklist provides criterion-level matrix and evidence fields.
- Midjourney parameter guidance includes v6/v7 decision rules, guardrails, and iteration protocol.
- Specialist interaction and payload contracts are validated with positive and blocked-path sample payloads.

## Validation

- pytest tests/test_manual_tool_specialist_contracts.py
  - Result: pass (9 tests)
- pytest tests/test_manual_tool_specialist_contracts.py tests/test_canva_specialist_contract.py tests/test_coursearc_specialist_contract.py
  - Result: pass (24 tests)

## Party Mode and Adversarial Closure

- Initial adversarial review: blocked; identified gaps in sign-off accountability, WCAG depth, and behavioral payload validation.
- Mitigations applied: sign-off hardening, expanded WCAG matrix, schema-level payload fixtures, stricter contract tests, structured Midjourney chronology entries.
- Final adversarial re-check: PASS (no blocking findings).
