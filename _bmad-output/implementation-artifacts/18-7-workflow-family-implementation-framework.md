# Story 18.7: Workflow Family Implementation Framework

**Epic:** 18 — Additional Assets & Workflow Families
**Status:** backlog
**Sprint key:** `18-7-workflow-family-implementation-framework`
**Added:** 2026-04-06
**Depends on:** At least one discovery document (Stories 18.1-18.6) approved. Existing structural-walk and prompt-pack infrastructure.

## Summary

Build a reusable framework for standing up new workflow families based on approved discovery documents. The framework provides templates for pipeline stages, run-constants extensions, structural-walk manifests, learning ledger initialization, pre-flight check extensions, and prompt packs. Validated by implementing the first approved content type end-to-end.

## Goals

1. Pipeline stage template: stage name, agent, input contract, output contract, HIL gate placement.
2. Run-constants extension pattern for new workflow families.
3. Structural-walk manifest extension pattern for new workflow families.
4. Learning ledger initialization for new workflow families (integrates with Epic 15 Story 15.6).
5. Pre-flight check extension pattern for new tool dependencies.
6. Prompt-pack template for operator guidance.
7. Validate by implementing the first approved content type.

## Existing Infrastructure To Build On

- `state/config/structural-walk/standard.yaml` — structural-walk manifest pattern (document integrity checks, cross-cutting checks)
- `state/config/structural-walk/motion.yaml` — second workflow variant manifest (motion-enabled)
- `scripts/utilities/structural_walk.py` — manifest-driven structural validation engine
- `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md` — prompt-pack format for standard workflow
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` — prompt-pack format for motion workflow
- `docs/workflow/production-operator-card-v4.md` — operator card pattern
- `docs/structural-walk.md` — structural walk documentation
- `state/config/run-constants.yaml` via `scripts/utilities/run_constants.py` — run-level config
- `skills/production-coordination/` — workflow stage and delegation patterns
- `skills/pre-flight-check/` — connectivity verification pattern
- Epic 15 Story 15.6 — workflow-family learning ledger (integration point)

## Key Files

- `docs/workflow/workflow-family-implementation-guide.md` — new: framework documentation
- `docs/workflow/workflow-family-template-prompt-pack.md` — new: prompt-pack template
- `state/config/structural-walk/template.yaml` — new: manifest template for new workflow families
- `state/config/workflow-family-learning/` — new: learning ledger directory (Epic 15 integration)

## Acceptance Criteria

1. `docs/workflow/workflow-family-implementation-guide.md` documents the complete process for standing up a new workflow family from a discovery document.
2. Pipeline stage template specifies: stage name, responsible agent, input contract (required fields), output contract (produced fields), HIL gate placement and review criteria.
3. Run-constants extension pattern shows how to add workflow-family-specific parameters without breaking existing workflows.
4. Structural-walk manifest template (`state/config/structural-walk/template.yaml`) shows how to declare document-integrity and cross-cutting checks for a new workflow.
5. Learning ledger initialization pattern creates `state/config/workflow-family-learning/{family-name}.yaml` with empty-but-structured schema for tracking failure modes, expensive stages, and human preferences.
6. Pre-flight check extension pattern shows how to add new API/tool connectivity checks.
7. Prompt-pack template shows how to structure operator guidance for a new workflow family.
8. Framework validated by implementing the first approved content type end-to-end (the implementation itself is a separate story spawned from the approved discovery document).
9. Subsequent content types can be stood up by following the framework without architectural changes.
10. Guide reviewed and approved by operator.
