---
title: 'structural-walk workflow split and hardening'
type: 'refactor'
created: '2026-04-05'
status: 'implemented-tranche-1'
context:
  - 'docs/project-context.md'
  - 'docs/fidelity-gate-map.md'
  - 'docs/fidelity-walk.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The current Fidelity Walk is valuable, but it is overloaded and underspecified: the docs describe a faithful sanity check for the production happy path, while the implementation is a single static asset-presence audit anchored to the standard narrated workflow. It also writes generated reports into `tests/`, which mixes operational artifacts with regression assets and makes the procedure feel more like an ad hoc script than a canonical platform check.

**Approach:** Recast the feature as a Structural Walk with explicit workflow variants for the two primary narrated production flows: standard and motion-enabled. First tranche focuses on structure, naming, storage, and stronger deterministic/runtime checks: canonical `structural_walk` entry point, backward-compatible `fidelity_walk` wrapper, workflow-specific specs and output directories, migrated historical reports, and “real” checks where feasible (contract validation, module import sanity, optional live probe commands) without turning the baseline command into a flaky network smoke suite.

## Boundaries & Constraints

**Always:** Preserve a deterministic, fast default mode suitable for local use and CI. Keep the existing gate/contract vocabulary intact even if the public procedure name changes. Support both high-level workflows explicitly: standard narrated and motion-enabled narrated. Store generated reports under `reports/structural-walk/` instead of `tests/`. Keep a compatibility path for existing `fidelity_walk` imports/invocations during the transition. Make checks more real by preferring parse/import/command execution over bare file existence when the dependency is meant to be executable.

**Ask First:** Any change that would remove backward compatibility for `python -m scripts.utilities.fidelity_walk`, rename the underlying gate contracts, or turn the default walk into a mandatory live-network probe that can fail due to external service availability.

**Never:** Do not collapse the two workflows back into one blended report. Do not make the baseline structural walk depend on mocked data. Do not move unit test sources out of `tests/`. Do not treat generated operational reports as regression fixtures going forward.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| STANDARD_WALK | Repo has canonical standard narrated assets and docs | Structural walk generates a standard workflow report under `reports/structural-walk/standard/` and exits cleanly when no findings exist | Non-zero exit with remediation items if required standard assets/checks fail |
| MOTION_WALK | Repo has motion workflow docs, motion pipeline scripts, and motion-specific anti-drift guards | Structural walk generates a motion workflow report under `reports/structural-walk/motion/` and includes motion-specific checkpoints | Non-zero exit with motion-scoped remediation items if motion-only dependencies drift or fail |
| COMPAT_WRAPPER | Operator still invokes `python -m scripts.utilities.fidelity_walk` | Wrapper remains functional and routes to the canonical structural walk default without breaking imports | Wrapper must surface canonical path/use in output rather than silently diverging |
| LIVE_PROBE_FAILURE | Optional live probe command is enabled and one probe fails | Report records the failed probe distinctly from structural checks and overall status reflects remediation needed | Failure evidence must include the executed probe and stderr/stdout summary, not just “missing” |

</frozen-after-approval>

## Code Map

- `scripts/utilities/fidelity_walk.py` -- current walk implementation to preserve as compatibility wrapper
- `tests/test_fidelity_walk.py` -- current regression coverage to evolve into structural-walk tests
- `docs/fidelity-walk.md` -- current user-facing procedure doc to convert into compatibility/redirect guidance
- `docs/fidelity-gate-map.md` -- source of workflow and checkpoint semantics
- `scripts/validate_fidelity_contracts.py` -- existing real contract validator to integrate directly
- `scripts/heartbeat_check.mjs` -- candidate small-scale live probe for optional sanity execution
- `docs/workflow/production-session-wrapup.md` -- operational reference that should point to the canonical structural walk

## Tasks & Acceptance

**Execution:**
- [x] `scripts/utilities/structural_walk.py` -- introduce canonical structural-walk engine with explicit `standard` and `motion` workflow specs, stronger asset/import checks, optional live probes, and workflow-specific output paths -- makes the procedure match its intended purpose
- [x] `scripts/utilities/fidelity_walk.py` -- convert to a backward-compatible wrapper over structural walk defaults -- preserves existing operator habits and imports while transitioning the canonical name
- [x] `docs/structural-walk.md`, `docs/fidelity-walk.md`, `docs/workflow/production-session-wrapup.md` -- document the canonical renamed procedure, workflow split, output locations, and compatibility alias -- keeps operator docs aligned with implementation
- [x] `reports/structural-walk/**` and historical `tests/fidelity-walk-*.md` assets -- create canonical report directories and move existing generated reports into the standard workflow history location -- separates operational artifacts from tests
- [x] `tests/test_structural_walk.py` and wrapper coverage -- validate standard/motion workflow selection, new output paths, stronger checks, compatibility wrapper behavior, and historical asset assumptions -- protects the refactor from regressions

**Acceptance Criteria:**
- Given the standard narrated workflow, when the canonical structural walk runs with default settings, then it produces a standard-scoped report under `reports/structural-walk/standard/` and validates the expected gate chain and anti-drift checks.
- Given the motion-enabled narrated workflow, when the structural walk runs with `--workflow motion`, then it evaluates motion-specific dependencies and anti-drift checkpoints separately from the standard workflow.
- Given an executable Python dependency referenced by the walk, when its file exists but import execution fails, then the report records a real failure rather than incorrectly reporting the asset as merely present.
- Given an operator still uses the legacy fidelity-walk command/module, when it is invoked, then the command still works and clearly routes through the canonical structural-walk behavior.
- Given optional live probes are requested, when a probe command fails, then the report includes explicit probe evidence and marks the walk as needing remediation.

## Spec Change Log

## Design Notes

This is a tranche refactor, not the final end state. The goal of tranche one is to make the procedure structurally honest and operationally useful without turning it into a heavyweight end-to-end simulator. The baseline command stays deterministic and local; “real” checks in this tranche mean import, parse, contract, and small command execution where the dependency is supposed to be runnable.

The second tranche can deepen from “structural walk” into “dry-run sanity walk” by executing selected non-network planning/validation steps and richer checkpoint parity checks from machine-readable workflow manifests instead of embedded constants.

## Verification

**Commands:**
- `pytest tests/test_structural_walk.py -q` -- expected: standard and motion variants plus wrapper behavior pass
- `python -m scripts.utilities.structural_walk --workflow standard` -- expected: report written under `reports/structural-walk/standard/`
- `python -m scripts.utilities.structural_walk --workflow motion` -- expected: report written under `reports/structural-walk/motion/`
- `python -m scripts.utilities.structural_walk --workflow standard --live-probe contracts-cli` -- expected: live probe recorded distinctly and exits cleanly when contracts CLI passes
