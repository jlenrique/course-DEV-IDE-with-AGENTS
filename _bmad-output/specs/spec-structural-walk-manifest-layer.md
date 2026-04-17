---
title: 'structural-walk manifest contract layer'
type: 'refactor'
created: '2026-04-06'
status: 'implemented'
context:
  - 'scripts/utilities/structural_walk.py'
  - 'state/config/structural-walk/standard.yaml'
  - 'state/config/structural-walk/motion.yaml'
  - 'tests/test_structural_walk.py'
---

## Intent

Externalize workflow-specific structural-walk parity data into
machine-readable manifests before adding any deeper dry-run execution
layer. This keeps the workflow split declarative, diffable, and stable.

## Scope

Implemented in this tranche:

- manifest path contract under `state/config/structural-walk/`
- loader and validation in `scripts/utilities/structural_walk.py`
- migration of workflow-specific cross-cutting and anti-drift data out of Python constants
- regression coverage for manifest loading and invalid manifest shape

Explicitly out of scope:

- live-network behavior in the default walk
- dry-run execution of planners/validators beyond existing optional probes
- changes to `fidelity_walk` compatibility behavior
- changes to gate/contract vocabulary

## Verification

- `pytest tests/test_structural_walk.py -q`
- `python -m scripts.utilities.structural_walk --workflow standard`
- `python -m scripts.utilities.structural_walk --workflow motion`
