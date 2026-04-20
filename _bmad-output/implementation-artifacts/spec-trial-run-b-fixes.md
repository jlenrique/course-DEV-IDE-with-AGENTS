---
title: 'Trial Run B fixes: preflight cache + scan gate + Marcus display standards'
type: 'bugfix'
created: '2026-04-19'
status: 'in-progress'
baseline_commit: '3fa61944ecdc2f98a93386b44a5bb9a73e75ebd3'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/dev-brief-trial-run-b-fixes.md'
  - '{project-root}/docs/dev-guide/pipeline-manifest-regime.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Trial Run B surfaced six workflow gaps across the v4.2 pack, preflight reuse, scan-first enforcement, Marcus display standards, and ffmpeg resolver hygiene. These gaps cause operator confusion, redundant preflight pings, and weak evidence for Prompt 2 compliance.

**Approach:** Implement the briefed fixes via generator templates, workflow policy defaults, preflight caching, scan gate validation, and Marcus documentation updates, backed by targeted tests and regenerated pack fixtures. Run party-mode review and bmad-code-review before considering the work done.

## Boundaries & Constraints

**Always:** Use the v4.2 generator pipeline for pack changes; keep pipeline-manifest step ordering untouched; use existing gate patterns and fail-closed behavior; preserve the live bundle path as read-only; add tests for every new or revised behavior; run party-mode review and bmad-code-review before declaring completion.

**Ask First:** Any pack version bump, pipeline-manifest step ordering change, or decision to keep/remove runtime/test artifacts like `.coverage` or `state/runtime/lesson_plan_log.jsonl`.

**Never:** Hand-edit `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`, add new pipeline steps, or run commands against the active bundle directory.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fresh session receipt | `--session-receipt` points to a cache with matching root and age <= policy | `emit_preflight_receipt` reuses cached report and writes bundle receipt | N/A |
| Stale or invalid receipt | Cache missing, stale, wrong root, or malformed | `emit_preflight_receipt` runs live readiness and writes fresh receipt | Log cache miss; continue |
| Scan gate invalid | `source-directory-scan.md` missing or fails validation | Validator returns `valid: false`; harness marks Prompt 2 as PARTIAL/INCONSISTENT | Fail closed with issues |
| Docx provider dispatch | Directive specifies `docx` provider | Runner accepts `docx` without falling back to `local_file` | Fail closed if provider is unknown |

</frozen-after-approval>

## Code Map

- `scripts/generators/v42/templates/sections/01-activation-preflight.md.j2` -- Prompt 1 prereq + session receipt flag
- `scripts/generators/v42/templates/sections/02-source-authority-map.md.j2` -- scan-first gate instructions
- `scripts/generators/v42/templates/sections/02A-operator-directives.md.j2` -- poll timing wording + parameters
- `scripts/generators/v42/render.py` -- pass workflow policy into templates
- `scripts/utilities/workflow_policy.py` -- defaults and YAML fail-soft loader
- `state/config/workflow-policy.yaml` -- poll timing and cache defaults
- `scripts/utilities/emit_preflight_receipt.py` -- session receipt cache reuse
- `scripts/marcus_capabilities/pr_pf.py` -- persist session receipt
- `skills/bmad-agent-marcus/capabilities/pr-pf.md` -- capability doc update
- `skills/bmad-agent-marcus/capabilities/schemas/pr_pf.yaml` -- schema update
- `scripts/utilities/validate_source_directory_scan_gate.py` -- scan gate validator
- `scripts/utilities/marcus_prompt_harness.py` -- Prompt 2 evidence classification
- `scripts/utilities/ffmpeg.py` -- canonical ffmpeg resolver
- `skills/bmad-agent-texas/scripts/run_wrangler.py` -- accepted provider dispatch
- `skills/bmad-agent-marcus/SKILL.md` -- HIL display standards
- `skills/bmad-agent-marcus/references/conversation-mgmt.md` -- HIL display standards
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` -- generated output
- `tests/test_emit_preflight_receipt.py` -- cache behavior tests
- `tests/test_validate_source_directory_scan_gate.py` -- validator tests
- `tests/test_marcus_prompt_harness.py` -- prompt 2 evidence tests
- `tests/test_ffmpeg_utility.py` -- resolver priority tests
- `tests/marcus_capabilities/test_pr_pf.py` -- session receipt persistence test
- `tests/contracts/test_run_wrangler_provider_dispatch.py` -- provider dispatch acceptance (docx)
- `tests/generators/v42/fixtures/expected_pack/fixture_pack.md` -- expected pack fixture
- `tests/generators/v42/fixtures/pack_sha_fixture.txt` -- pack sha fixture

## Tasks & Acceptance

**Execution:**
- [ ] `scripts/utilities/workflow_policy.py` -- load defaults, coerce invalid values, and fail-soft on YAML errors -- keep template rendering deterministic
- [ ] `state/config/workflow-policy.yaml` -- add poll timing + cache defaults -- expose parameters for templates
- [ ] `scripts/utilities/emit_preflight_receipt.py` -- add session receipt cache reuse with age and root checks, CLI arg, and cache messaging -- avoid double preflight
- [ ] `scripts/marcus_capabilities/pr_pf.py` -- persist session receipt on success and surface path -- enable reuse from Prompt 1
- [ ] `skills/bmad-agent-marcus/capabilities/pr-pf.md` and `skills/bmad-agent-marcus/capabilities/schemas/pr_pf.yaml` -- document new arg/result -- keep capability docs aligned
- [ ] `scripts/utilities/validate_source_directory_scan_gate.py` -- implement scan gate validator with contiguous rows and operator approval checks -- fail closed
- [ ] `scripts/utilities/marcus_prompt_harness.py` -- classify Prompt 2 as PASS/PARTIAL/INCONSISTENT based on scan gate -- evidence parity
- [ ] `scripts/generators/v42/templates/sections/01-activation-preflight.md.j2` -- add PR-RC prerequisite block and session receipt flag -- operator clarity
- [ ] `scripts/generators/v42/templates/sections/02-source-authority-map.md.j2` -- add scan-first gate steps and required writes -- enforce operator role assignment
- [ ] `scripts/generators/v42/templates/sections/02A-operator-directives.md.j2` -- correct poll timing language and parameterize values -- avoid invalid early submission rule
- [ ] `scripts/generators/v42/render.py` -- pass workflow policy into templates -- enable parameterized text
- [ ] `scripts/utilities/ffmpeg.py` and any ffmpeg call sites -- ensure resolver is used before PATH -- prevent .venv misses
- [ ] `skills/bmad-agent-texas/scripts/run_wrangler.py` -- accept `docx` provider in dispatch set -- align runner with provider directory
- [ ] `skills/bmad-agent-marcus/SKILL.md` and `skills/bmad-agent-marcus/references/conversation-mgmt.md` -- add HIL display standards -- align registration + sanctum
- [ ] `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` and generator fixtures -- regenerate pack and update fixtures -- keep generator truth
- [ ] `tests/test_emit_preflight_receipt.py`, `tests/test_validate_source_directory_scan_gate.py`, `tests/test_marcus_prompt_harness.py`, `tests/test_ffmpeg_utility.py`, `tests/marcus_capabilities/test_pr_pf.py`, `tests/contracts/test_run_wrangler_provider_dispatch.py` -- add/adjust tests for new behavior
- [ ] Cleanup: remove `.coverage` and `state/runtime/lesson_plan_log.jsonl` if they are test artifacts and not intended for commit
- [ ] Run party-mode review and bmad-code-review after fixes and tests pass

**Acceptance Criteria:**
- Given a fresh session receipt with matching repo root, when `emit_preflight_receipt` is called with `--session-receipt`, then the cached payload is reused and written to the bundle receipt.
- Given a stale, malformed, or wrong-root session receipt, when `emit_preflight_receipt` runs, then a live readiness run is executed and the bundle receipt is still produced.
- Given a source-directory scan file missing approval or contiguous rows, when `validate_source_directory_scan_gate` runs, then it fails closed with actionable issues and Prompt 2 is marked PARTIAL or INCONSISTENT.
- Given the updated templates, when the v4.2 pack is regenerated, then Prompt 1 includes the PR-RC prerequisite and session receipt option, Prompt 2 includes scan-first instructions, and Prompt 2A contains the corrected poll timing wording with parameterized values.
- Given updated Marcus docs, when reviewing the SKILL and conversation guidance, then HIL display standards for numbered rows and pagination are present in both layers.
- Given ffmpeg call sites, when invoked, then the resolver in `scripts/utilities/ffmpeg.py` is used before PATH fallbacks.
- Given a directive with `docx` provider, when the runner dispatches the provider, then it is accepted without falling back to `local_file`.
- All new or revised behaviors have supporting tests, party-mode review is complete, and bmad-code-review findings are addressed.

## Verification

**Commands:**
- `.\.venv\Scripts\python.exe -m scripts.generators.v42.render --manifest state/config/pipeline-manifest.yaml --output docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` -- expected: pack regenerated
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` -- expected: exit 0
- `\.venv\Scripts\python.exe -m pytest tests/test_emit_preflight_receipt.py tests/test_validate_source_directory_scan_gate.py tests/test_marcus_prompt_harness.py tests/test_ffmpeg_utility.py tests/marcus_capabilities/test_pr_pf.py tests/contracts/test_run_wrangler_provider_dispatch.py tests/generators/v42` -- expected: all pass

</frozen-after-approval>
