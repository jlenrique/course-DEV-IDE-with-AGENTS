# Story: Literal-Visual Pre-Dispatch Gate — Enforce §06B Before Gary Dispatch

**Status:** ready-for-dev
**Type:** fix-in-flight
**Points:** 1
**Branch:** `trial/2026-04-19` (direct)
**Gate mode:** single-gate (`bmad-code-review` before done)
**Created:** 2026-04-19 — party-mode consensus (Winston, Amelia, Murat, John)
**Blocks:** Trial `C1-M1-PRES-20260419B` Gary dispatch at §07

---

## TL;DR

§06B (Literal-Visual Operator Build) has no enforcement gate. Marcus nearly dispatched Gary with `image_url: null` for a required literal-visual diagram card. Gamma requires a public HTTPS URL — null would silently fail. Fix: new `validate-literal-visual-pre-dispatch.py` that reads `gary-outbound-envelope.yaml` and blocks §07 if required cards are unresolved or `literal-visual-operator-packet.md` is absent.

---

## Story

As the **trial operator**,
I want **Gary dispatch to be blocked by machine gate if any required literal-visual diagram card has no resolved image URL and the operator packet is absent**,
So that **Gamma never receives a null image_url for a literal-visual slide, which would silently produce a broken or missing slide**.

---

## Background

`gary-outbound-envelope.yaml` carries a `diagram_cards[]` block. Each entry has:
- `card_number` / `slide_id`
- `image_url` — must be a public HTTPS URL for Gamma to use the image
- `preintegration_png_path` — local PNG path; valid alternative in tracked mode if file exists on disk
- `required` — boolean

The pack §06B mandates `literal-visual-operator-packet.md` before Gary dispatch, but no script enforces it. No script checks that `image_url` is non-null. In the live trial, S12 had `image_url: null` and `preintegration_png_path` pointing to a local file that needs to be published first.

**Principle:** The more literal the slide, the more important operator scrutiny. Creative → Gary has latitude. Literal-visual → source asset integrity is non-negotiable.

---

## Key Files

- **New:** `skills/bmad-agent-marcus/scripts/validate-literal-visual-pre-dispatch.py`
- **New tests:** `skills/bmad-agent-marcus/scripts/tests/test_validate_literal_visual_pre_dispatch.py`
- **Template edit:** `scripts/generators/v42/templates/sections/06B-literal-visual-operator-build.md.j2`
- **Manifest update:** `state/config/pipeline-manifest.yaml` — add new script to `block_mode_trigger_paths`

**Do NOT touch:**
- `skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py` — post-dispatch validator stays clean
- Existing tests for post-dispatch validator

**Read before writing a line:**
- `skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py` lines 338–426 (`_validate_preintegration_publish_receipt`) — understand the post-dispatch boundary so the new pre-dispatch function does NOT duplicate it
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/gary-outbound-envelope.yaml` — the live input shape

---

## Acceptance Criteria

### AC-1: New script — three checks, reads `gary-outbound-envelope.yaml`

```python
# validate-literal-visual-pre-dispatch.py
# Input: gary-outbound-envelope.yaml (diagram_cards block)
# NOT gary-diagram-cards.json (post-dispatch surface)
```

**Check 1 — Skip gate:** If `diagram_cards` is absent or empty list → return `[]` immediately. No errors.

**Check 2 — Required card URL resolution:** For each card where `required == true`:
- If `image_url` is non-null non-empty string → PASS for this card
- If `image_url` is null/empty AND `preintegration_png_path` is a non-null string AND that path exists on disk → PASS for this card (tracked mode: local PNG staged, awaiting publish)
- Otherwise → FAIL. Error must name `card_number` and `slide_id`.

**Check 3 — Operator packet:** If any `required == true` card exists → `bundle_dir / "literal-visual-operator-packet.md"` must exist. If absent → FAIL.

**Mode check:** In ad-hoc mode, `preintegration_png_path` is NOT a valid alternative. Check 2 must treat ad-hoc + local path as FAIL (mirrors `_validate_preintegration_publish_receipt` policy).

### AC-2: §06B template adds required script call

`scripts/generators/v42/templates/sections/06B-literal-visual-operator-build.md.j2` must include:

```
Required gate command (run before advancing to Prompt 7):
- `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/validate-literal-visual-pre-dispatch.py --bundle-dir [BUNDLE_PATH]`

Gate rule:
- If exit code is non-zero, Gary dispatch is blocked. Resolve all failing cards and re-run before advancing.
- If `diagram_cards` is empty (no literal-visual source assets), gate exits 0 automatically.
```

After template edit: regenerate the pack and run `check_pipeline_manifest_lockstep.py`. Generator fixture tests must pass.

### AC-3: New script added to `block_mode_trigger_paths`

Add to `state/config/pipeline-manifest.yaml` under `block_mode_trigger_paths`:
```yaml
- skills/bmad-agent-marcus/scripts/validate-literal-visual-pre-dispatch.py
```

This is a Tier-1 manifest edit (adding a path, not changing pipeline steps). Dev-agent authority. Run `check_pipeline_manifest_lockstep.py` after and confirm exit 0.

### AC-4: Live bundle passes after operator stages S12

After the fix is implemented, operator will:
1. Write `literal-visual-operator-packet.md` to bundle (confirming S12 source asset)
2. Either publish APC Content Roadmap.jpg to get a public URL, OR confirm `preintegration_png_path` file exists on disk

Script must exit 0 on the live bundle once operator confirms. This is the trial-unblock condition.

### AC-5: Murat's Trap B documented in AC

Pre-dispatch gate and post-dispatch validator serve different purposes — both must exist:
- Pre-dispatch: checks `image_url` presence BEFORE Gary is invoked
- Post-dispatch: checks `literal_visual_publish` receipt AFTER Gary runs

They are NOT redundant. The story AC must state this explicitly in the test file docstring.

---

## Test Matrix (K-floor 10, target 11–13)

| # | Test | Expected |
|---|---|---|
| T1 | `diagram_cards` absent | Exit 0, no errors |
| T2 | `diagram_cards` empty list | Exit 0, no errors |
| T3 | Required card, `image_url` valid HTTPS | PASS |
| T4 | Required card, `image_url` null, `preintegration_png_path` present on disk (tracked) | PASS |
| T5 | Required card, `image_url` null, `preintegration_png_path` declared but file missing | FAIL, named card |
| T6 | Required card, `image_url` null, no `preintegration_png_path` | FAIL, named card |
| T7 | `required: false` card, `image_url` null | PASS (non-blocking) |
| T8 | Packet absent when required card exists | FAIL, packet missing |
| T9 | Packet present when required card exists | Contributes to PASS |
| T10 | Ad-hoc mode + required card + local `preintegration_png_path` | FAIL (ad-hoc cannot use local paths) |
| T11 | Full tracked PASS: all required cards resolved + packet present | Exit 0 |
| T12 | YAML-input integration: reads live-shaped `gary-outbound-envelope.yaml` directly | Correct parse |

---

## Definition of Done

- [ ] `validate-literal-visual-pre-dispatch.py` written and all 12 tests pass
- [ ] Does NOT read `gary-diagram-cards.json` — reads `gary-outbound-envelope.yaml` only
- [ ] `_validate_preintegration_publish_receipt` in post-dispatch validator unchanged
- [ ] §06B template updated with gate command; pack regenerated; L1 check exits 0
- [ ] New script added to `block_mode_trigger_paths`; L1 check exits 0
- [ ] Full test suite passes (no new failures beyond pre-existing 3)
- [ ] `bmad-code-review` single-gate passes
