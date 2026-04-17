# Story 6.1: CourseArc Specialist Agent & LTI Integration

> **Historical note (2026-04-16):** Paths of the form `<old>-specialist-sidecar/` and `bmad-agent-marcus-sidecar/` were renamed to persona-named sidecars. See `_bmad/memory/` for current paths.

Epic: 6 - LMS Platform Integration & Delivery
Status: done
Sprint key: 6-1-coursearc-specialist-agent
Completed: 2026-03-30

## Summary

Closed Story 6.1 by hardening and validating the existing manual-tool CourseArc specialist implementation, adding a delegation-safe wrapper for Marcus routing, deepening LTI/SCORM/WCAG reference guidance, defining evidence collection schema, and adding contract tests.

## Deliverables

- Agent wrapper (delegation path fix):
  - agents/coursearc-specialist.md

- Existing specialist skill hardened:
  - skills/bmad-agent-coursearc/SKILL.md

- Expanded CourseArc references:
  - skills/bmad-agent-coursearc/references/lti13-canvas-embedding-checklist.md
  - skills/bmad-agent-coursearc/references/lti-role-mapping-and-grading.md
  - skills/bmad-agent-coursearc/references/scorm-packaging-specs.md
  - skills/bmad-agent-coursearc/references/interactive-block-guidance.md
  - skills/bmad-agent-coursearc/references/wcag-interactive-verification.md
  - skills/bmad-agent-coursearc/references/evidence-collection-schema.md

- Sidecar memory updates:
  - _bmad/memory/coursearc-specialist-sidecar/patterns.md
  - _bmad/memory/coursearc-specialist-sidecar/chronology.md

- Contract tests:
  - tests/test_coursearc_specialist_contract.py

- Status/docs updates:
  - _bmad-output/implementation-artifacts/sprint-status.yaml
  - docs/project-context.md
  - agents/README.md

## Acceptance Criteria Trace

- skills/bmad-agent-coursearc/SKILL.md exists and remains manual-tool (no API runtime assumptions).
- LTI 1.3 integration guidance exists and now includes normative references and role/grade decision companion.
- SCORM packaging specifications exist and include version/manifest/completion guidance.
- Interactive content block guidance exists for sorting, flip cards, and virtual patient drills with authoring/validation/export details.
- WCAG 2.1 AA verification guidance exists with criterion-code mapping and evidence-based completion rule.

## Validation

- python -m pytest tests/test_coursearc_specialist_contract.py -q
  - Result: pass
- python -m pytest tests/test_exemplar_catalogs_yaml.py -q
  - Result: pass

## Party Mode and Adversarial Closure

- Party-mode consultation: pass-with-fixes; identified completeness gaps in references and evidence process.
- Adversarial review loop: mitigations applied and re-reviewed to pass with no blocking findings.
- Key mitigations:
  - Added agent wrapper for Marcus delegation resolution.
  - Added evidence schema with run_id rules and manifest template.
  - Added LTI role mapping and grade-passback decision guide.
  - Expanded interaction guidance with concrete per-block authoring/validation/export details.
  - Strengthened contract tests to verify actionable reference content, not just file existence.
