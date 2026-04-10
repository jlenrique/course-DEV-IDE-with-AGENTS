# Story 15.6: Workflow-Family Learning Ledger

**Epic:** 15 — Learning & Compound Intelligence
**Status:** backlog
**Sprint key:** `15-6-workflow-family-learning-ledger`
**Added:** 2026-04-06
**Depends on:** Story 15.1 (learning events tagged by workflow family). Story 18.7 (workflow family implementation framework — integration point).

## Summary

Track learning not only per-agent but per-workflow family (narrated deck, motion-enabled lesson, assessment generation, etc.), so the platform gets smarter at the level the user actually experiences. Each workflow family maintains its own learning ledger that grows from real run data. Marcus consults family-level heuristics when planning runs.

## Goals

1. Per-workflow-family learning ledger in YAML.
2. Tracking: failure modes, expensive stages, escalation points, preset combinations, human preferences.
3. Ledger grows from real run data only (no pre-populated guesses).
4. Marcus consultation for run planning.
5. Auto-creation for new workflow families.
6. Integration with Epic 18 workflow family framework.

## Existing Infrastructure To Build On

- `state/config/run-constants.yaml` via `scripts/utilities/run_constants.py` — run-level config (workflow family tag)
- Learning events (Story 15.1) — tagged with workflow family
- Retrospectives (Story 15.2) — per-run findings attributed to workflow family
- `state/config/structural-walk/standard.yaml` and `motion.yaml` — existing workflow family manifests
- `skills/production-coordination/` — workflow stage definitions
- `docs/workflow/production-prompt-pack-v4.1-*.md` and `v4.2-*.md` — existing workflow family documentation
- Epic 18 Story 18.7 — workflow family implementation framework (learning ledger initialization)

## Key Files

- `state/config/workflow-family-learning/` — new: directory for per-family YAML ledgers
- `state/config/workflow-family-learning/narrated-deck-video-export.yaml` — new: first family ledger
- `state/config/workflow-family-learning/motion-enabled-narrated-lesson.yaml` — new: second family ledger
- `scripts/utilities/workflow_family_learning.py` — new: ledger read/write/update functions
- `skills/bmad-agent-marcus/` — update: reference workflow-family heuristics in run planning

## Acceptance Criteria

1. Per-family ledger at `state/config/workflow-family-learning/{family-name}.yaml` tracks: `frequent_failure_modes[]`, `expensive_stages[]`, `best_escalation_points[]`, `best_preset_combinations[]`, `common_human_preferences[]`, `run_count`, `last_updated`.
2. Ledger entries grow from real run data: retrospective findings are classified by workflow family and appended.
3. No pre-populated guesses — ledger starts empty and grows organically.
4. Marcus can read workflow-family heuristics: `load_family_learning(family_name)` returns structured data for run planning.
5. Auto-creation: when a run uses an unrecognized family tag, a new empty ledger is created automatically.
6. Two initial ledger files created for existing workflow families: `narrated-deck-video-export` and `motion-enabled-narrated-lesson`.
7. Integration with Epic 18 Story 18.7: workflow family implementation framework initializes a new ledger as part of standing up a new workflow family.
8. Callable: `python -m scripts.utilities.workflow_family_learning --family <name> --show` for inspection.
9. Unit tests: ledger creation, data append, auto-creation, load function, empty-start guarantee.
