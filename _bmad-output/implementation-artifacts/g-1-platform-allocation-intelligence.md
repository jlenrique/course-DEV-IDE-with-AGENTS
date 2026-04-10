# Story G.1: Platform Allocation Intelligence

**Epic:** G — Governance Synthesis & Intelligence Optimization  
**Status:** done  
**Sprint key:** g-1-platform-allocation-intelligence  
**Completed:** 2026-03-30

## Summary

Implemented Marcus platform-allocation intelligence as a deterministic, matrix-driven recommendation flow backed by shared exemplar policy data and course context, with explicit conversational accept/modify/override outputs.

## Deliverables

- Added shared matrix config:
  - resources/exemplars/_shared/platform-allocation-matrix.yaml
- Added Marcus allocation engine:
  - skills/bmad-agent-marcus/scripts/platform_allocation.py
- Added test coverage:
  - skills/bmad-agent-marcus/scripts/tests/test_platform_allocation.py
- Added Marcus conversation guidance:
  - skills/bmad-agent-marcus/references/conversation-mgmt.md
- Captured allocation learning in Marcus sidecar:
  - _bmad/memory/bmad-agent-marcus-sidecar/patterns.md

## Acceptance Criteria Trace

- AC1: Marcus loads allocation policies and course context.  
  Implemented via matrix loader + course context loader in platform_allocation.py.
- AC2: Analyzes content profile and recommends platform with reasoning.  
  Implemented deterministic rule engine with rationale output.
- AC3: Accept / modify / override conversationally.  
  Output includes explicit options and rerun-ready normalized profile.
- AC4: Allocation decisions captured for learning.  
  Implemented save_allocation_decision() and recorded real sample decision.

## Validation

- pytest skills/bmad-agent-marcus/scripts/tests/test_platform_allocation.py -v
- Result: 10 passed
- Existing Marcus planning regression tests remain green.

## Adversarial Review & Mitigation

Adversarial review was run and mitigated before marking complete:

- Added unknown matrix-flag detection and invalid interactivity validation.
- Hardened boolean coercion (reject non-binary floats).
- Added sidecar persistence path and CLI error handling.
- Expanded tests for narrative/accessibility branches and edge conditions.

## Completion Notes

This story is complete and integrated as a Marcus intelligence extension (no standalone agent), consistent with Epic G rebaseline architecture.
