---
title: 'structural-walk Marcus sequence to document parity'
type: 'refactor'
created: '2026-04-06'
status: 'proposed'
context:
  - 'scripts/utilities/structural_walk.py'
  - 'state/config/structural-walk/standard.yaml'
  - 'state/config/structural-walk/motion.yaml'
  - 'skills/bmad-agent-marcus/scripts/generate-production-plan.py'
  - 'skills/bmad-agent-marcus/references/workflow-templates.yaml'
  - 'docs/workflow/production-operator-card-v4.md'
  - 'docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md'
  - 'docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md'
---

## Intent

The current structural-walk dry-run now resolves Marcus's local workflow
sequence for both standard and motion workflows, and it verifies that
the Marcus planning assets used by the preview are explicitly declared
in the workflow manifests. The next fidelity seam is whether the
operator-facing workflow documents still describe the same sequence that
Marcus resolves locally.

This tranche would define a deterministic, local parity check between:

- Marcus's resolved workflow sequence from the local planner/template
  assets
- structural-walk anti-drift checkpoints
- the relevant prompt pack and operator-card markers for the same
  workflow

## Scope

Proposed for a future tranche:

- add a local parity rule that maps Marcus-resolved workflow stages to
  document checkpoints for each workflow
- extend the workflow manifests with a declarative checkpoint-parity
  mapping section so the document correspondence lives in manifest data
  rather than a second hard-coded Python stage model
- fail closed when the docs no longer reflect the Marcus-resolved
  sequencing contract

Explicitly out of scope:

- network calls or live probes
- invoking specialists or execution skills
- downstream asset generation
- widening dry-run into an execution simulator

## Constraints

- Marcus remains the source of truth for workflow sequencing.
- The parity check must stay local and deterministic.
- The implementation should avoid duplicating a second stage-chain model
  inside structural walk; the check should compare docs to the
  Marcus-resolved sequence, not to another hard-coded sequence.
- Workflow-specific checkpoint mappings should come from a manifest-level
  declarative source so future Marcus changes can be reconciled in one
  place.

## Proposed Acceptance

- Given a workflow dry-run, when Marcus's local planner resolves the
  sequence, then the structural-walk parity layer can compare that
  sequence to the workflow's declared document checkpoints without using
  a duplicated internal stage chain.
- Given drift between Marcus's resolved sequence and the workflow prompt
  pack or operator card, then the parity layer should surface a local,
  explicit failure instead of allowing a clean preview.
- Given both workflows, then the parity rules remain workflow-scoped and
  do not collapse standard and motion into one blended mapping.

## Verification Plan

For the future implementation tranche:

- `python -m pytest tests/test_structural_walk.py -q`
- one standard-workflow regression proving a Marcus-resolved stage and
  its corresponding prompt-pack/operator-card checkpoint stay aligned
- one motion-workflow regression proving the same alignment around
  Marcus-specific motion stages such as Gate 2M and Motion Gate
