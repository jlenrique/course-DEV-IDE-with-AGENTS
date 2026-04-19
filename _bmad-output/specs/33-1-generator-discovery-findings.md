# 33-1 Generator Discovery Findings

## Summary

Story `33-1-generator-discovery` completed as an investigation spike. The repository has no in-repo generator-of-record that writes `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`. Current evidence supports case **(c) no-generator**: the v4.2 pack is maintained as a hand-authored document and read by runtime tooling.

## Generator Location

**Verdict:** case **(c) explicit escalation**.

- No script, module, workflow template, or command entrypoint was found that materializes the v4.2 prompt pack to disk.
- The strongest in-repo references are read-only consumers:
  - `scripts/utilities/marcus_prompt_harness.py` selects v4.2 as an input path (`MOTION_PROMPT_PACK`) but does not generate it.
  - `scripts/utilities/run_hud.py` includes a `SYNC-WITH` reference and TODO for manifest extraction, again as consumer alignment, not generation.
- Git history on the pack file is dominated by direct documentation edits to the markdown file itself.

## Generator Inputs

No generator inputs identified; see `## Escalation`.

Observed current state:

- Effective "input" is direct human editing of `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`.
- No parameter file, template file, or environment-variable contract was discovered that can be invoked to regenerate this file.

## Generator Outputs

No generator outputs identified; see `## Escalation`.

Current on-disk fingerprint baseline for Story 33-3:

- Target artifact: `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- SHA-256:
  `6f5d1143222528ea3a9cdcf3e99ca7198d8b587c4c808f06a5a52583d9f36ce3`
- Command used:
  `python -c "import hashlib;from pathlib import Path;p=Path('docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md');print(hashlib.sha256(p.read_bytes()).hexdigest())"`

## Regeneration Procedure

No executable regeneration procedure exists in-repo for v4.2 at this time.

- Case (a) verification (run generator to scratch output and diff) is not feasible because no generator entrypoint was found.
- Story 33-2 cannot yet "rewire the generator" to consume `state/config/pipeline-manifest.yaml` without first establishing a generator-of-record (new story 33-1a or a party-mode scope rewrite of 33-2).

## Drift Between Generator and On-Disk v4.2

Not applicable for this story run.

- Drift comparison requires a generator output vs on-disk output pair.
- Because no generator exists, there is no regeneration artifact to diff.

## Gap Analysis

Required scope decisions before Story 33-2 can execute safely:

- Define the canonical generation contract first:
  - **Option A:** new `33-1a` builds an in-repo generator and then 33-2 rewires that generator to `state/config/pipeline-manifest.yaml`.
  - **Option B:** re-scope 33-2 into "generator creation + manifest wiring" (larger than current 33-2 charter; requires party-mode consensus).
- Introduce manifest-driven generation interfaces once generator ownership exists:
  - Canonical manifest location is `state/config/pipeline-manifest.yaml` (33-1 addendum A-1).
  - `--manifest-path` (or equivalent) must become required input.
  - Manifest schema should include gate order, gate names, gate types, and insertion-point semantics now hard-coded in docs/HUD/orchestrator surfaces.
  - Generator contract must enumerate from manifest records (parameterized IDs), not hardcoded step-ID literals; this is the addendum guard required to support the `04.5` (polling) and `04.55` (lock) split without code churn (33-1 addendum A-2).
  - Workflow insertion migration in 33-2 is hard-replace to `insert_between(before_id, after_id, new_step)` with legacy `insert_4a_between_step_04_and_05` removed (no compatibility shim) per addendum ruling (33-1 addendum A-3).
- Preserve a deterministic output contract:
  - 33-3 should validate regenerated v4.2 byte-level stability (or deliberate, reviewed diffs) against the SHA baseline above.
- Out-of-scope discoveries to carry forward:
  - Current workflow documentation appears to be maintained by direct editorial commits; this is process drift and should be addressed by generator governance, not ad-hoc edits.

## Kill-switch Decision

**ESCALATE.**

Kill-switch condition triggered: **Generator does not exist at all** (story kill-switch #1). This prevents safe execution of the currently described 33-2 "rewire existing generator" path.

Recommendation:

- Escalate to `bmad-party-mode` to choose either:
  - `ESCALATED-TO-33-1a` (build generator first), or
  - `ESCALATED-SCOPE-CHANGE-ON-33-2` (merge generator creation into 33-2).

## Escalation

Escalation triggered and required.

- Proposed follow-up story: **33-1a — Build the v4.2 generator from scratch**.
- Blocking rationale: no in-repo generation surface currently exists to wire against `state/config/pipeline-manifest.yaml`.
- Until party-mode resolves the path, 33-2 should remain backlog to avoid hidden scope explosion.

## Evidence Index

- `git log --follow --name-only -- docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
  - Shows repeated direct edits to the pack file across commits; no paired generator artifact path in commit-level evidence.
- `git log --all --source --oneline -- "*prompt-pack*generator*"`
  - No results.
- `rg "production-prompt-pack-v4\\.2-narrated-lesson-with-video-or-animation\\.md" scripts`
  - Shows consumer references such as `scripts/utilities/marcus_prompt_harness.py` and `scripts/utilities/run_hud.py`.
- `rg "v4\\.2|prompt-pack|generator" _bmad`
  - No generator candidate in `_bmad` workflows/templates.
- `python -c "<sha256 command above>"`
  - Captured baseline digest for v4.2.
- `_bmad-output/implementation-artifacts/33-1-generator-discovery.md` §Post-Close R1 Addendum
  - Binding rulings applied here: canonical manifest path (`state/config/pipeline-manifest.yaml`), `04.5`/`04.55` split contract expectation, and `insert_between(...)` hard migration note.

No separate `_bmad-output/specs/33-1-evidence/` files were required for this pass; all evidence commands and outcomes are enumerated here.
