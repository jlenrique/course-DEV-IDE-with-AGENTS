---
name: production-readiness-run-constants
code: PR-RC
description: Author or validate a bundle's run-constants.yaml in the canonical lowercase-nested schema the preflight validator expects.
script_module: scripts.marcus_capabilities.pr_rc
schema_path: skills/bmad-agent-marcus/capabilities/schemas/pr_rc.yaml
full_or_stub: full
---

# PR-RC — Run-Constants

## When to invoke

This is the **direct fix for the 2026-04-17 Prompt 1 trial halt**. Offer it whenever:

- The operator is about to author `run-constants.yaml` for a new tracked-bundle run.
- The operator suspects the existing `run-constants.yaml` has schema drift (validator recently tightened, pack-doc recently rewritten, prior receipt failed).
- The operator asks "Marcus, create/check run constants" or "author the run constants for this bundle."

Historically the operator copied UPPERCASE fields from the prompt pack's "Run Constants" section into a yaml file. The validator enforces **lowercase snake_case**, with `motion_budget` and `slide_mode_proportions` as nested maps. This mismatch halted the 2026-04-17 trial at Prompt 1. PR-RC makes Marcus the author, closing that drift vector.

## Inputs

From invocation args:

- `values` (dict, required) — operator-provided canonical values. Keys should already be lowercase snake_case. Marcus accepts UPPERCASE at the conversational layer and normalizes before invoking.
- `target_path` (str, optional) — override for where to write. Defaults to `{bundle_path}/run-constants.yaml`.
- `mode_sub` (str, default `author`) — `author` writes a new file; `validate` reads an existing file and delegates to `run_constants.parse_run_constants`.

From invocation context:

- `context.bundle_path` (required for `author` sub-mode) — determines where `run-constants.yaml` lands.
- `context.run_id` (optional) — echoed into the return envelope.

## Procedure

1. **Summarize mode.** Render the canonical lowercase-nested YAML preview that *would* be written. Do not touch disk. Call `run_constants.parse_run_constants()` internally on the proposed dict to confirm the shape validates before presenting. Operator sees what Marcus will write.
2. **Execute mode + `mode_sub: author`.** Build the YAML document using the pinned canonical schema (required fields: `run_id, lesson_slug, bundle_path, primary_source_file, theme_selection, theme_paramset_key, execution_mode, quality_preset`; nested: `motion_budget`, `slide_mode_proportions`). Round-trip through `parse_run_constants` to confirm validity. Write to `target_path`. Return envelope populates `result.written_path` and `landing_point.sha256`.
3. **Execute mode + `mode_sub: validate`.** Read existing `target_path`. Delegate to `run_constants.parse_run_constants`. On `RunConstantsError`, set `status: error` and populate `errors[]` with a code `RUN_CONSTANTS_INVALID` entry naming the failing field. On success, return a PASS envelope.
4. **Idempotency (AC-T.7).** `author` mode writes byte-equal output given the same `values`. Re-running `author` on the same inputs yields the same sha256.

## Outputs / artifacts

- `run-constants.yaml` at the target path, in canonical lowercase-nested form.
- Structured `ReturnEnvelope` with the parsed values, landing-point sha256, and any validation errors.

## Gates / checkpoints

- `emit-preflight-receipt.py` (external validator) accepts PR-RC-authored files on first invocation (AC-B.1). This is the gate whose failure halted the 2026-04-17 trial.
- Schema-parity check against the receipt consumer at Prompt 2 (AC-B.4) — contract match, not behavior.

## Examples

```
Operator: Author the run constants for this bundle — motion-enabled, 125
          credits pro tier, visual-led profile, default cluster density.
Marcus (PR-RC summarize):
  I'll write run-constants.yaml to:
    course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260418-motion/run-constants.yaml

  Canonical form:
    run_id: C1-M1-PRES-20260418
    lesson_slug: apc-c1m1-tejal
    bundle_path: course-content/staging/.../apc-c1m1-tejal-20260418-motion
    primary_source_file: course-content/courses/APC C1-M1 Tejal 2026-03-29.pdf
    theme_selection: hil-2026-apc-nejal-A
    theme_paramset_key: hil-2026-apc-nejal-A
    execution_mode: tracked/default
    quality_preset: production
    motion_enabled: true
    motion_budget:
      max_credits: 125
      model_preference: pro
    double_dispatch: true
    experience_profile: visual-led
    cluster_density: default

  Validation dry-run: PASS.
  Recommendation: write — this matches the profile you set and preflight
    should accept it first try.
  Proceed?
Operator: yes
Marcus: [invokes PR-RC execute/author; reports sha256 + PASS from validator]
```
