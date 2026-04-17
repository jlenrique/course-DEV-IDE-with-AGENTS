---
title: 'Double-Dispatch Deliberate Diffs Enhancement'
type: 'feature'
created: '2026-04-08'
status: 'done'
baseline_commit: 'fdbce50034e0f3d39bb2ff13069d185771ec6d27'
context: ['docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md', 'docs/project-context.md', '_bmad-output/implementation-artifacts/12-1-dual-dispatch-infrastructure.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Current double-dispatch uses stochastic randomness for A/B variants, not deliberate parameter/prompt diffs. No type-aware dispatch (all modes double, no skip low-var literal). This reduces var quality and review efficiency.

**Approach:** Add deliberate_dispatch flag and variant_strategies array for type-aware deliberate diffs (creative: instr_focus var, text-literal: proportional illus, visual-literal: literal_freedom var). Extend gamma_ops loop for per-variant params.

## Boundaries & Constraints

**Always:** Preserve existing uniform double as fallback. Add deliberate as opt-in. Type-aware (creative always double, literal optional). Winner bridging for Irene (merged PNGs, instr log).

**Ask First:** None.

**Never:** Break existing double, remove stochastic, force all types double.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | deliberate_dispatch=true, variant_strategies set per type | A/B with deliberate diffs, selection/storyboard works | N/A |
| INVALID_STRATEGIES | Malformed variant_strategies | Fallback to uniform stochastic | Log warning, continue |
| NO_STRATEGIES | deliberate_dispatch=true but no strategies | Fallback to uniform | Log info |

</frozen-after-approval>

## Code Map

- `skills/gamma-api-mastery/scripts/gamma_operations.py` -- extend double_dispatch loop for variant_strategies parsing, per-variant params
- `skills/bmad-agent-marcus/scripts/generate-storyboard.py` -- handles A/B pairs/selections (no change)
- `skills/production-coordination/scripts/run_context_builder.py` -- add deliberate_dispatch flag, variant_strategies to YAML
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` -- update DOUBLE_DISPATCH spec

## Tasks & Acceptance

**Execution:**
- [x] `skills/gamma-api-mastery/scripts/gamma_operations.py` -- add variant_strategies parsing, per-variant params in double_dispatch loop -- enables deliberate diffs
- [x] `skills/production-coordination/scripts/run_context_builder.py` -- add --deliberate-dispatch flag, variant_strategies arg to YAML -- enables envelope config
- [x] `gary-slide-content.json` -- add variants[] array (manual for now) -- provides per-slide strategies
- [x] `skills/gamma-api-mastery/scripts/tests/test_gamma_operations.py` -- add tests for deliberate diffs, fallback -- locks behavior

**Acceptance Criteria:**
- Given deliberate_dispatch=true and valid variant_strategies, when dispatch runs, then A/B have different params per type and selection works.
- Given invalid variant_strategies, when dispatch runs, then uniform stochastic fallback with warning.
- Given no variant_strategies, when deliberate_dispatch=true, then uniform fallback with info log.

## Verification

**Commands:**
- `pytest skills/gamma-api-mastery/scripts/tests/test_gamma_operations.py -k double_dispatch` -- expected: new tests pass.
- `python -m scripts.utilities.fidelity_walk` -- expected: no new regressions.

**Manual checks (if no CLI):**
- Inspect storyboard HTML for A/B diffs in prompts/params.