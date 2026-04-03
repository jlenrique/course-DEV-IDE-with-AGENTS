---
title: 'Canonical fidelity walk generation and regression hardening'
type: 'bugfix'
created: '2026-04-03T00:00:00Z'
status: 'draft'
context: ['docs/fidelity-walk.md', 'docs/fidelity-gate-map.md', 'docs/lane-matrix.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The latest saved fidelity walk was generated from an ad hoc path that checked the wrong G5 and G6 contract filenames, producing a false remediation report and undermining trust in the release-readiness check.

**Approach:** Add a canonical fidelity-walk generator under the repo's utilities, encode the authoritative per-gate asset map in one place, and cover the gate map, anti-drift checks, and markdown output with regression tests so future reports are generated from validated repo state instead of handwritten assumptions.

## Boundaries & Constraints

**Always:** Preserve the existing G0-G6 gate model and contract names already present in state/config/fidelity-contracts; treat documented redirects as redirects rather than defects; keep the implementation additive and compatible with current production docs and tests; save generated reports into tests using the documented timestamped naming pattern.

**Ask First:** Any change that renames canonical fidelity contracts, weakens an existing gate/anti-drift check, or reclassifies a documented missing asset from remediation to redirect without evidence in repo docs.

**Never:** Patch the symptom by adding fake alias contract files; silently delete the defective report artifact; widen this work into unrelated fidelity or production-prompt refactors.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Canonical gate assets and anti-drift docs are present | Generator writes a READY markdown report using canonical G5/G6 contract names and current repo evidence | N/A |
| MISSING_ASSET | A required gate asset is absent | Report marks the gate as remediation-needed and lists the exact missing path | Continue report generation and surface the missing asset in the summary |
| REDIRECT_PATH | A superseded path is explicitly documented as redirected | Report marks the item as redirect/documented rather than missing | Do not count the redirect as a critical finding |
| DOC_DRIFT | Anti-drift checkpoint text is missing from a required doc | Report marks the anti-drift check as failed and includes the missing evidence target | Continue report generation and include the failed check in summary |

</frozen-after-approval>

## Code Map

- `docs/fidelity-walk.md` -- operator-facing procedure and output contract for the canonical walk.
- `docs/fidelity-gate-map.md` -- authoritative gate ordering and checkpoint expectations.
- `scripts/validate_fidelity_contracts.py` -- existing contract validation utility to reuse or align with.
- `tests/fidelity-walk-20260403-111500.md` -- known-good report shape and canonical G5/G6 names.
- `tests/fidelity-walk-20260403-153321.md` -- defective ad hoc artifact that demonstrates the regression to prevent.

## Tasks & Acceptance

**Execution:**
- [ ] `scripts/utilities/fidelity_walk.py` -- implement a canonical gate asset registry, anti-drift checks, markdown rendering, and timestamped report writing -- eliminates ad hoc filename drift at the root.
- [ ] `tests/test_fidelity_walk.py` -- add focused tests for canonical G5/G6 contract mapping, redirect handling, anti-drift checks, and summary/report rendering -- locks the generator against the observed false-negative regression.
- [ ] `docs/fidelity-walk.md` -- replace prompt-only guidance with the canonical invocation path and clarify that reports must come from the scripted generator -- removes operator ambiguity.
- [ ] `_bmad-output/implementation-artifacts/epic-11-party-mode-consensus-log.md` -- append the party-mode consensus round covering root cause, remediation choice, and non-regression guardrails -- records the requested consensus artifact.

**Acceptance Criteria:**
- Given the current repo state, when the canonical fidelity-walk generator runs, then it produces a report that references `state/config/fidelity-contracts/g5-audio.yaml` and `state/config/fidelity-contracts/g6-composition.yaml` and does not flag them as missing.
- Given a required gate asset is removed in a test fixture, when the generator runs, then the affected gate is reported as remediation-needed and the exact missing path appears in the summary.
- Given the documented redirect placeholder remains declared in the repo, when the generator evaluates cross-cutting assets, then the redirect is recorded without increasing the critical finding count.
- Given anti-drift checkpoint text is absent from a required document fixture, when the generator runs, then the anti-drift section records a failure with evidence instead of silently passing.

## Verification

**Commands:**
- `python -m scripts.utilities.fidelity_walk --output tests/fidelity-walk-YYYYMMDD-HHMMSS.md` -- expected: markdown report is written and uses canonical gate assets.
- `pytest tests/test_fidelity_walk.py` -- expected: regression suite passes.
- `pytest` -- expected: full repo test suite passes.---
title: 'SB.1 preintegration literal-visual publish and URL substitution'
type: 'feature'
created: '2026-04-02'
status: 'draft'
context:
  - docs/project-context.md
  - docs/workflow/human-in-the-loop.md
  - _bmad-output/implementation-artifacts/sb-1-evolving-lesson-storyboard-run-view.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** In the current flow, literal-visual URLs are user-supplied Gamma links at dispatch time. There is no automated function to take user-created literal-visual slides, download/store them as local preintegration PNGs, publish those PNGs into the Git-site destination (`jlenrique/jlenrique.github.io`, `assets/gamma`), and then inject hosted URLs into Gary's API package without further user action.

**Approach:** Preserve the existing tested Gary generation/export pipeline for creative, literal-text, and literal-visual outputs. Add a preintegration literal-visual preparation path that: (1) identifies literal-visual source PNGs prepared by the user, (2) publishes them to `assets/gamma/<module_lesson_part>/` in the Git site with commit+push, (3) emits a readiness signal indicating preintegration PNG URLs are available, and (4) programmatically substitutes those hosted URLs into Gary's API-call package (diagram card/image URL fields) before dispatch.

## Boundaries & Constraints

**Always:** Do not break or refactor the current mixed-fidelity generation/download behavior. Keep source files in place (copy semantics). Distinguish terminology: preintegration literal-visual PNGs (user-created assets prepared before Gary dispatch) vs post-integration literal visuals (slides generated by Gary). Perform commit+push automatically in the Git-site repo during this feature when execution mode is tracked/default; in ad-hoc mode the feature must fail closed (or explicitly no-op) to preserve ad-hoc side-effect boundaries. Keep required outbound contract fields unchanged.

**Ask First:** None for this slice; commit+push and URL substitution are part of the required behavior.

**Never:** Do not require manual user URL entry for literal-visual hosted links once preintegration PNGs are present. Do not alter creative/literal-text handling paths. Do not expose secrets in logs.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Preintegration literal-visual PNGs are present locally + site repo URL + `assets/gamma` target | Site repo sync + commit+push succeed; readiness signal is emitted; Gary dispatch package receives Git-site hosted URLs for literal-visual cards programmatically | N/A |
| NO_LITERAL_VISUAL | No literal-visual slides in unified results | No publish operation attempted; payload publish metadata indicates skipped/no-op | N/A |
| REMOTE_OR_MISSING_SOURCE | Preintegration file path is missing or invalid | Card remains unresolved; readiness signal is false; Gary package is not updated for that card | Non-fatal aggregate warning unless strict mode enabled |
| GIT_FAILURE | Clone/pull/commit/push fails due to auth/connectivity | Generation exits with explicit publish error context and does not rewrite literal-visual URLs in Gary package | Raise RuntimeError with git command context |

</frozen-after-approval>

## Code Map

- `skills/gamma-api-mastery/scripts/gamma_operations.py` -- Add preintegration literal-visual publish helper, readiness signaling, mode-aware guardrails, and diagram-card URL substitution integration.
- `skills/gamma-api-mastery/scripts/tests/test_gamma_operations.py` -- Add unit tests for publish helper, readiness signaling, substitution behavior, ad-hoc guardrails, and git failures.
- `_bmad-output/implementation-artifacts/deferred-work.md` -- Mark deferred item as completed/replaced by active implementation.

## Tasks & Acceptance

**Execution:**
- [ ] `skills/gamma-api-mastery/scripts/gamma_operations.py` -- Add helper(s) to sync local clone of `jlenrique/jlenrique.github.io`, copy preintegration literal-visual PNGs to `assets/gamma/<module_lesson_part>/`, and commit+push updates in tracked/default mode only.
- [ ] `skills/gamma-api-mastery/scripts/gamma_operations.py` -- Add readiness signal + URL map output for literal-visual cards and inject hosted URLs into Gary API package fields before dispatch, while preserving lane ownership (Marcus orchestrates; Gary executes tool path).
- [ ] `skills/gamma-api-mastery/scripts/tests/test_gamma_operations.py` -- Add tests for happy path, no literal visuals, unresolved preintegration sources, URL substitution, and git failures.
- [ ] `_bmad-output/implementation-artifacts/deferred-work.md` -- Update deferred ledger entry to reflect active implementation.

**Acceptance Criteria:**
- Given preintegration literal-visual PNGs and configured site repo target, when preparation runs, then PNGs are copied and pushed into `assets/gamma/<module_lesson_part>/` in the site repo.
- Given no literal-visual outputs, when generation completes, then publish path is skipped without affecting `gary_slide_output`.
- Given valid preintegration publish output, when Gary dispatch package is assembled, then literal-visual cards receive Git-site URLs programmatically with no user URL entry.
- Given missing/invalid preintegration sources, when preparation runs, then readiness signal reports unresolved cards and dispatch URL substitution is withheld for those cards.
- Given execution mode is ad-hoc, when publish is requested, then the feature fails closed or no-ops with explicit status and no remote git side effects.
- Given git clone/pull/commit/push failure, when publish is required for URL substitution, then the function raises explicit runtime error context.

## Spec Change Log

## Design Notes

Publish metadata and readiness output should be additive and isolated, for example:

```json
{
  "literal_visual_publish": {
    "repo_url": "https://github.com/jlenrique/jlenrique.github.io",
    "target_subdir": "assets/gamma/C1-M1-PART",
    "preintegration_ready": true,
    "copied_count": 2,
    "pushed": true,
    "url_base": "https://jlenrique.github.io/assets/gamma/C1-M1-PART",
    "substituted_cards": [5, 7],
    "skipped": [{"card_number": 9, "reason": "missing_local_path"}]
  }
}
```

This preserves backward compatibility for existing required contract fields while making substitution state explicit.

Implementation should also emit run_id-correlated operational logs only (Channel C), avoid writing to human-curated `resources/` or `config/`, and reuse existing Gamma export/path helpers to satisfy DRY expectations.

## Verification

**Commands:**
- `.venv/Scripts/python -m pytest skills/gamma-api-mastery/scripts/tests/test_gamma_operations.py -k literal_visual -q` -- expected: targeted tests pass.
- `.venv/Scripts/python -m ruff check skills/gamma-api-mastery/scripts/gamma_operations.py skills/gamma-api-mastery/scripts/tests/test_gamma_operations.py` -- expected: no lint violations in touched files.

**Manual checks (if no CLI):**
- Inspect local checkout of the site repo and verify copied files exist under `assets/gamma/<module_lesson_part>/`.
- Confirm generated Gary dispatch package contains hosted Git-site URLs for literal-visual cards only.
