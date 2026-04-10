---
title: 'structural-walk motion dry-run Marcus parity'
type: 'refactor'
created: '2026-04-06'
status: 'implemented'
context:
  - 'scripts/utilities/structural_walk.py'
  - 'state/config/structural-walk/motion.yaml'
  - 'skills/bmad-agent-marcus/scripts/generate-production-plan.py'
  - 'skills/bmad-agent-marcus/references/workflow-templates.yaml'
  - 'docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md'
---

## Intent

The current dry-run slice is intentionally standard-only, but the user
clarified the real requirement: structural walk is only valuable if it
tracks Marcus, the master orchestrator, on the equivalent production
path. The next tranche should therefore add motion dry-run parity only
by resolving and previewing Marcus's motion-enabled path, not by adding
an abstract second preview model.

## Scope

Proposed for the next tranche:

- add a motion dry-run mode only if it derives its sequence from Marcus's
  local workflow-template and production-plan assets
- keep the mode local, deterministic, and read-only apart from the
  generated report
- reuse the existing dry-run contract shape rather than creating a second
  reporting surface
- validate motion-specific Marcus checkpoints such as `gate-2m`,
  `motion-generation`, and `motion-gate` only through local assets and
  docs already treated as source-of-truth

Explicitly out of scope for that tranche:

- live probes or network calls in dry-run mode
- invoking Kling, Gamma, ElevenLabs, MCP connectors, or sensory bridges
- downstream asset generation or file mutation beyond the report
- widening the standard dry-run slice beyond its approved Marcus-sync
  boundary

## Constraints

- Marcus remains the sole user-facing orchestrator and the sole planning
  source-of-truth for workflow sequencing.
- Motion dry-run must resolve the motion-enabled variant from Marcus's
  own local planner/template contract rather than maintaining a separate
  hard-coded motion chain inside structural walk.
- If Marcus's motion planning assets are missing or unresolved, dry-run
  must fail closed with a clear blocker rather than silently degrading.
- Default structural walk behavior must remain fast, local, and suitable
  for CI.

## Acceptance

- Given `--workflow motion --dry-run`, when Marcus's local production
  planner resolves the motion variant, then the report includes the
  motion stage sequence Marcus would follow as resolved from Marcus's own
  planner/template contract, not from a duplicated internal chain.
- Given missing or invalid Marcus motion planning assets, when motion
  dry-run runs, then the report blocks on Marcus-plan resolution with
  explicit evidence.
- Given the motion prompt pack or operator card drifts from the
  Marcus-resolved motion workflow sequence, when motion dry-run is
  expanded, then the report should surface that as a parity failure
  rather than presenting a clean preview.

## Verification Plan

Implemented verification:

- `python -m pytest tests/test_structural_walk.py -q`
- `python -m scripts.utilities.structural_walk --workflow motion --dry-run`
- focused regression proving the motion dry-run sequence comes from
  Marcus's motion workflow template, not a duplicated internal chain
- focused regression proving missing Marcus motion planning assets block
  the motion dry-run preview
