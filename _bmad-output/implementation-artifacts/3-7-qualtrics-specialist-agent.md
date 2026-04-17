# Story 3.7: Qualtrics Specialist Agent & Mastery Skill

> **Historical note (2026-04-16):** Paths of the form `<old>-specialist-sidecar/` and `bmad-agent-marcus-sidecar/` were renamed to persona-named sidecars. See `_bmad/memory/` for current paths.

Epic: 3 - Core Tool Specialist Agents & Mastery Skills
Status: done
Sprint key: 3-7-qualtrics-specialist-agent
Completed: 2026-03-29

## Summary

Implemented the Qualtrics specialist Assessment Architect with a deterministic assessment orchestration skill, objective-trace validation, sidecar memory, and woodshed exemplar reproduction using the shared Qualtrics API client.

## Deliverables

- Agent definition:
  - agents/qualtrics-specialist.md

- New mastery skill:
  - skills/qualtrics-assessment/SKILL.md
  - skills/qualtrics-assessment/references/question-catalog.md
  - skills/qualtrics-assessment/scripts/qualtrics_operations.py
  - skills/qualtrics-assessment/scripts/tests/test_qualtrics_operations.py

- Qualtrics API helper hardening:
  - scripts/api_clients/qualtrics_client.py
    - update_survey_options()
    - reproduce_survey_snapshot() with robust input/shape handling

- Sidecar initialization:
  - _bmad/memory/qualtrics-specialist-sidecar/index.md
  - _bmad/memory/qualtrics-specialist-sidecar/patterns.md
  - _bmad/memory/qualtrics-specialist-sidecar/chronology.md
  - _bmad/memory/qualtrics-specialist-sidecar/access-boundaries.md

- Exemplar assets and run retention:
  - resources/exemplars/qualtrics/_catalog.yaml
  - resources/exemplars/qualtrics/L1-survey-inventory-snapshot/brief.md
  - resources/exemplars/qualtrics/L1-survey-inventory-snapshot/reproduction-spec.yaml
  - resources/exemplars/qualtrics/L1-survey-inventory-snapshot/source/reference-snapshot-schema.yaml
  - resources/exemplars/qualtrics/L1-survey-inventory-snapshot/reproductions/2026-03-29_021502/run-log.yaml
  - resources/exemplars/qualtrics/L1-survey-inventory-snapshot/reproductions/2026-03-29_021502/output/api_response.json

- Marcus routing updates:
  - skills/bmad-agent-marcus/SKILL.md
  - skills/bmad-agent-marcus/references/conversation-mgmt.md

- Additional hardening tests:
  - tests/test_qualtrics_snapshot_helper.py
  - tests/test_exemplar_catalogs_yaml.py

## Acceptance Criteria Trace

- agents/qualtrics-specialist.md exists with Assessment Architect persona.
- skills/qualtrics-assessment/SKILL.md exists and routes to deterministic operations.
- question-catalog reference exists for educational question suitability.
- script orchestration imports and uses scripts/api_clients/qualtrics_client.py.
- style guide preferences are read from state/config/style_guide.yaml.
- _bmad/memory/qualtrics-specialist-sidecar/ initialized and populated.
- exemplar exists in resources/exemplars/qualtrics/.
- woodshed reproduction completed with retained run-log.yaml and output artifact.

## Validation

- python -m pytest skills/qualtrics-assessment/scripts/tests/test_qualtrics_operations.py tests/test_qualtrics_snapshot_helper.py tests/test_exemplar_catalogs_yaml.py -q
  - Result: pass
- python -m pytest tests/test_integration_qualtrics.py --run-live -q
  - Result: 3 passed
- python skills/woodshed/scripts/reproduce_exemplar.py qualtrics L1-survey-inventory-snapshot --session-attempt 1
  - Result: status completed with response status 200 in run-log.

## Party Mode and Adversarial Closure

- Party-mode consensus review: pass-with-fixes, then pass after mitigations.
- Adversarial findings mitigated before closure:
  - catalog YAML normalization and parser guard test
  - dry-run validation parity with execute mode
  - snapshot helper input/shape hardening
  - delegation rule consistency in Marcus conversation management
  - exemplar artifact redaction for identifier safety
