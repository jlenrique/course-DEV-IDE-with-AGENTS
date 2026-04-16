# Story 20c-14: E2E Validation (C1-M1, Both Profiles)

**Epic:** 20c - Cluster Intelligence + Creative Control
**Status:** done
**Branch:** `DEV/slides-redesign`
**Dependencies:** 20c-13 (resolver wired and validated)

## Purpose

Close the remaining SPOC gap by making profile selection operator-usable through Marcus, routing the resulting choice through the Marcus-controlled contract surface, and proving end to end that both `visual-led` and `text-led` produce the expected runtime behavior on C1-M1.

This story is not about adding new profile logic. The resolver already exists. This story makes the existing capability reachable through Marcus's conversation flow and proves that Irene receives narration controls through Marcus's envelope rather than any direct downstream profile-file read.

## Architectural Invariant: Marcus as Single Point of Contact

The operator must interact only through Marcus. The operator should never be asked to choose an internal "experience profile" by name. Marcus owns the conversational mapping from plain-language intent to the canonical profile identifier.

That means this story must satisfy all of the following:

1. The prompt-pack and Marcus reference layer use plain language such as "should the visuals lead or the text?"
2. The canonical machine value remains a single optional `experience_profile` identifier in `run-constants.yaml`
3. Profile resolution still happens through `scripts/utilities/run_constants.py`
4. Irene receives resolved narration controls through Marcus's envelope, not by reading `experience-profiles.yaml`
5. Storyboard HTML remains view-only; no new operator UI controls are introduced there

## Acceptance Criteria

1. Prompt pack updated with a plain-language profile-selection step during the run-constants handshake. The operator is never exposed to the internal term `experience_profile`.
2. `skills/bmad-agent-marcus/references/conversation-mgmt.md` is updated so Marcus elicits, maps, confirms, and preserves the profile choice in the existing run-settings / planning flow.
3. `skills/bmad-agent-cd/SKILL.md` gains a `## Intake Contract` section that states CD is invoked only through Marcus's envelope, receives all context from the envelope, and returns structured output only to Marcus.
4. Marcus-side runtime packaging sends resolved `narration_profile_controls` to Irene in `pass2-envelope.json` (or the canonical Marcus-side Pass 2 handoff artifact), with tests proving those values come from the selected profile.
5. The selected profile remains optional: omitted profile preserves current behavior for legacy callers and does not force new required inputs.
6. Invalid profile choice is rejected at the Marcus/run-constants contract boundary with operator-meaningful diagnostics.
7. C1-M1 proof run for `visual-led` produces run constants / envelope values matching the canonical values in `state/config/experience-profiles.yaml`.
8. C1-M1 proof run for `text-led` produces run constants / envelope values matching the canonical values in `state/config/experience-profiles.yaml`.
9. Storyboard HTML remains view-only with no operator-facing controls added.
10. SPOC gap ledger entries for 20c-10, 20c-12, and 20c-13 are updated to closed in `_bmad-output/planning-artifacts/epics-interstitial-clusters.md`.

## Current Repo Facts That Must Shape This Work

- `scripts/utilities/run_constants.py` now owns canonical `experience_profile` validation and profile resolution.
- `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py` currently builds the Marcus-side Pass 2 envelope but does **not** yet include resolved `narration_profile_controls`.
- `scripts/utilities/marcus_prompt_harness.py` and `tests/test_marcus_prompt_harness.py` are the existing deterministic seam for prompt-pack/run-constants alignment.
- Real tracked C1-M1 bundle candidates exist, especially:
  - `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409-motion`
  - `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion`
- The `20260409-motion` bundle's existing `run-constants.yaml` still contains a **legacy** `slide_mode_proportions` shape (`creative` + `irene_discretion`) that does not match the canonical 20c-13 key set. Treat it as historical data, not a drop-in canonical proof fixture.

## Key Files

### Files to MODIFY

| File | Why |
|------|-----|
| `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` | Add plain-language operator selection step and persistence rules for profile choice in the motion-enabled C1-M1 workflow |
| `skills/bmad-agent-marcus/references/conversation-mgmt.md` | Teach Marcus how to elicit, map, confirm, and preserve the profile choice without surfacing internal jargon |
| `skills/bmad-agent-cd/SKILL.md` | Add `## Intake Contract` and formalize Marcus-only invocation |
| `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py` | Pack resolved `narration_profile_controls` into Irene's envelope via the Marcus-controlled path |
| `tests/test_marcus_prompt_harness.py` | Add prompt-pack / run-constants handshake coverage for profile-aware flow |
| `skills/bmad-agent-marcus/scripts/tests/test_prepare_irene_pass2_handoff.py` | Add envelope propagation tests for resolved narration controls |
| `_bmad-output/planning-artifacts/epics-interstitial-clusters.md` | Close the explicit SPOC gap ledger entries once the implementation and proof are done |

### Files to READ (source of truth, do NOT modify unless specifically listed above)

| File | Why |
|------|-----|
| `state/config/experience-profiles.yaml` | Sole source of truth for the canonical profile mappings |
| `scripts/utilities/run_constants.py` | Existing resolver and validation path introduced in 20c-13 |
| `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md` | Reference for any shared prompt-pack language you may need to keep aligned if the handshake text is duplicated |
| `scripts/utilities/marcus_prompt_harness.py` | Existing deterministic prompt-pack watcher/harness logic |
| `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409-motion/run-constants.yaml` | Real-world proof fixture, but note the legacy proportions shape before relying on it |
| `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py` | Existing validator/reporting seam for narration control visibility |

## Implementation Constraints

1. **Do not introduce a richer profile object.** The contract stays a single optional `experience_profile` identifier.
2. **Do not duplicate the canonical profile enum in multiple places.** Prompts/docs may describe the choices in plain language, but the authoritative values still come from `experience-profiles.yaml`.
3. **Do not add operator controls to Storyboard HTML.** The storyboard remains view-only.
4. **Do not let Irene or downstream agents read `experience-profiles.yaml` directly.** They must receive resolved values only through Marcus-owned artifacts/envelopes.
5. **Do not silently infer a profile from other run settings.** If a profile is selected, it is selected explicitly; otherwise the field is absent and legacy behavior holds.
6. **Do not mutate historical tracked C1-M1 proof bundles in place unless the change is part of an explicit copied proof-run flow.** Prefer copied or fixture-scoped bundles for deterministic proof.
7. **Prompt-pack wording must stay operator-facing.** The operator should hear "visuals lead" / "text leads" or equivalent plain-language guidance, not internal implementation nouns.

## Suggested Task Breakdown

### Task 1: Create the Marcus-facing intake contract

- [x] Add a plain-language profile-selection handshake to the v4.2 prompt pack
- [x] Update `conversation-mgmt.md` so Marcus elicits and confirms the choice
- [x] Define the exact mapping from operator language -> canonical `experience_profile`
- [x] Preserve backwards compatibility when the choice is omitted

### Task 2: Formalize CD Marcus-only intake

- [x] Add `## Intake Contract` to `skills/bmad-agent-cd/SKILL.md`
- [x] State that CD is invoked exclusively through Marcus's envelope
- [x] State that CD returns structured output only to Marcus

### Task 3: Route resolved controls into Irene's envelope

- [x] Extend `prepare-irene-pass2-handoff.py` to resolve the selected profile through `run_constants.py`
- [x] Add resolved `narration_profile_controls` to the Pass 2 envelope
- [x] Keep profile resolution Marcus-owned and file-local to existing runtime helpers
- [x] Prove old callers still succeed when `experience_profile` is absent

### Task 4: Add deterministic tests before live proof

- [x] Add prompt-harness tests for profile-aware handshake content / context handling
- [x] Add envelope tests for `visual-led` and `text-led`
- [x] Add negative-path tests for invalid profile and absent profile behavior
- [x] Add guardrail coverage that storyboard HTML stays view-only

### Task 5: Run C1-M1 proof for both profiles

- [x] Choose a deterministic proof strategy:
  - copied real tracked bundle(s), or
  - fixture-backed harness proof plus explicit bundle-level validation
- [x] Produce one `visual-led` proof path
- [x] Produce one `text-led` proof path
- [x] Confirm resolved proportions and narration controls match `experience-profiles.yaml`

### Task 6: Close the SPOC ledger

- [x] Update `_bmad-output/planning-artifacts/epics-interstitial-clusters.md`
- [x] Mark 20c-10 / 20c-12 / 20c-13 SPOC gaps closed
- [x] Record the exact proof path used for closure

## Developer Guardrails

### Contract Boundaries

- `run_constants.py` remains the only place that resolves a profile name into canonical proportions/controls.
- Prompt packs and Marcus references may decide **which profile name** is selected, but not **what that profile means**.
- `prepare-irene-pass2-handoff.py` is the best current Marcus-side seam for passing resolved narration controls to Irene.

### Bundle / Proof Guidance

- The tracked C1-M1 motion bundles are useful as reference material and proof scaffolds.
- The `20260409-motion` bundle contains legacy `slide_mode_proportions` keys, so if you use it for proof, normalize via a copied proof bundle or regenerate the relevant contract artifact instead of mutating the historical run in place.

### Testing Guidance

- Prefer deterministic unit/integration tests first:
  - prompt-pack handshake expectations
  - Marcus/reference mapping behavior
  - Pass 2 envelope propagation
  - invalid/missing profile behavior
- Then add the narrowest bundle-level proof needed to satisfy the C1-M1 acceptance criteria.
- Keep `tests/test_run_constants.py` and `tests/test_experience_profiles.py` green; this story builds on their guarantees, it does not replace them.

## What NOT to Do

- Do NOT expose `experience_profile` jargon directly to the operator
- Do NOT add new profile families or new profile keys
- Do NOT bypass `parse_run_constants()` or `resolve_experience_profile()`
- Do NOT teach Irene to load `experience-profiles.yaml`
- Do NOT add interactive controls to storyboard HTML
- Do NOT rewrite historical tracked bundle artifacts in place unless that is the explicit proof strategy and is documented

## Validation Command

Minimum deterministic validation before calling the story complete:

```bash
.\.venv\Scripts\python.exe -m pytest tests/test_run_constants.py tests/test_experience_profiles.py tests/test_marcus_prompt_harness.py skills/bmad-agent-marcus/scripts/tests/test_prepare_irene_pass2_handoff.py tests/test_sprint_status_yaml.py -q
```

Bundle-level / proof validation must additionally demonstrate both `visual-led` and `text-led` C1-M1 paths and capture the exact proof artifact paths in the story record.

## References

- `_bmad-output/planning-artifacts/epics-interstitial-clusters.md` (`Story 20c-14: E2E Validation (C1-M1, Both Profiles)`)
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `skills/bmad-agent-marcus/references/conversation-mgmt.md`
- `scripts/utilities/run_constants.py`
- `scripts/utilities/marcus_prompt_harness.py`
- `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py`

## Dev Agent Record

### Implementation Plan

- Wire the plain-language Marcus intake across the prompt pack, conversation guidance, and CD intake contract.
- Extend the Marcus-side Pass 2 packer so selected profiles resolve through `run_constants.py` and land in Irene's envelope as `narration_profile_controls`.
- Keep backwards compatibility for callers that omit `experience_profile`.
- Prove the behavior with deterministic tests first, then copied C1-M1 proof bundles rooted in the 2026-04-06 tracked motion run.

### Debug Log

- 2026-04-14: Added prompt-pack/reference/CD-contract coverage plus Marcus harness context checks.
- 2026-04-14: Extended `run_constants.py` so profile-selected `slide_mode_proportions` auto-populate on parse and remain consistent with the canonical profile mapping.
- 2026-04-14: Added Pass 2 envelope tests for `visual-led`, `text-led`, invalid profiles, and absent-profile backwards compatibility.
- 2026-04-14: Aligned `validate-irene-pass2-handoff.py` so audit output reports envelope-resolved narration controls when present.
- 2026-04-14: Generated copied C1-M1 proof bundles under `reports/proofs/20c-14/` and verified both profiles resolve to the canonical run-constants/envelope values.
- 2026-04-14: Party Mode review gate closed with consensus to mark `20c-14` `review` and advance next to `20c-3`.

### Completion Notes

- Prompt pack v4.2 now asks the operator the plain-language emphasis question and persists only the mapped machine value (`visual-led` / `text-led`) when selected.
- Marcus conversation guidance now formalizes the mapping without surfacing `experience_profile` to the operator.
- CD now declares a Marcus-only intake contract.
- Marcus Pass 2 handoff prep now injects `experience_profile` and resolved `narration_profile_controls` into `pass2-envelope.json` while leaving legacy callers untouched.
- `run_constants.py` now auto-populates canonical `slide_mode_proportions` from `experience_profile` when the explicit proportions block is omitted.
- Validator reporting now surfaces the active envelope narration controls, not just global defaults.
- Proof artifacts:
  - `reports/proofs/20c-14/c1-m1-visual-led/run-constants-proof.json`
  - `reports/proofs/20c-14/c1-m1-visual-led/pass2-envelope.json`
  - `reports/proofs/20c-14/c1-m1-text-led/run-constants-proof.json`
  - `reports/proofs/20c-14/c1-m1-text-led/pass2-envelope.json`
- Validation command passed:
  - `.\.venv\Scripts\python.exe -m pytest tests/test_run_constants.py tests/test_experience_profiles.py tests/test_marcus_prompt_harness.py skills/bmad-agent-marcus/scripts/tests/test_prepare_irene_pass2_handoff.py skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py tests/test_sprint_status_yaml.py -q`
  - Result: `123 passed`

## File List

- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `skills/bmad-agent-marcus/references/conversation-mgmt.md`
- `skills/bmad-agent-cd/SKILL.md`
- `scripts/utilities/run_constants.py`
- `scripts/utilities/marcus_prompt_harness.py`
- `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py`
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
- `tests/test_run_constants.py`
- `tests/test_experience_profiles.py`
- `tests/test_marcus_prompt_harness.py`
- `skills/bmad-agent-marcus/scripts/tests/test_prepare_irene_pass2_handoff.py`
- `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py`
- `_bmad-output/planning-artifacts/epics-interstitial-clusters.md`
- `_bmad-output/implementation-artifacts/20c-14-e2e-validation-both-profiles.md`

## Change Log

- 2026-04-14: Closed the Marcus-facing profile-intake gap, added envelope propagation and validator audit coverage, and recorded copied C1-M1 proof bundles for both profiles.

## Adversarial Review (BMAD)

### Blind Hunter
- Confirmed Marcus-side envelope path: `prepare-irene-pass2-handoff.py` packs `narration_profile_controls` from `resolve_experience_profile` into the Pass 2 envelope (Marcus-owned surface per AC4).
- **Upstream contract:** Any Creative Director directive flowing this path still depends on `validate_creative_directive`; re-review applied **schema_version** const enforcement (20c-11 remediation) so CD outputs cannot falsely pass with wrong version strings—no additional 20c-14-only code change required for that fix.

### Edge Case Hunter
- Legacy bundles without `experience_profile` remain optional; invalid profile continues to fail at run-constants boundary (aligned with AC5–6).

### Acceptance Auditor
- AC1–10 traced to prompt-pack / `conversation-mgmt.md` / CD intake / tests listed in story File List; no gap requiring new implementation in this pass.

Review closed: 2026-04-15 (BMAD re-review; validator hardening consumed as shared dependency).

## BMAD tracking closure

**Framework:** Per `sprint-status.yaml` — **`done`** = ACs met + verification green + layered BMAD review complete + sprint key `done`.

| Check | State |
|-------|--------|
| ACs | Met (prompt pack, conversation-mgmt, CD intake, envelope, proofs — **File List**) |
| Verification | Commands in story / related test files; CD directive path aligned with shared validator |
| **`sprint-status.yaml`** | **`20c-14-e2e-validation-both-profiles`: `done`** (reconciled 2026-04-15) |
