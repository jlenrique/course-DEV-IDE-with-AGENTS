---
title: 'SB.1 storyboard run-view refresh with related asset rows'
type: 'feature'
created: '2026-04-02'
status: 'done'
baseline_commit: 311ae154d1959ec1c09bdd056c37de8525da40c5
context:
  - docs/project-context.md
  - docs/workflow/human-in-the-loop.md
  - _bmad-output/implementation-artifacts/sb-1-evolving-lesson-storyboard-run-view.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The current storyboard tooling is Gary-dispatch-centric and does not yet expose run-level linked assets (video/audio/interactive/source) in the same operator-facing view. This limits storyboard usefulness as a live run index during Marcus-led review.

**Approach:** Extend storyboard generation with an optional related-asset input that appends non-slide rows to the manifest/HTML projection while preserving deterministic slide ordering, existing summary behavior, and current strict/missing-asset safety. Add focused tests for parsing, rendering, and regression compatibility.

## Boundaries & Constraints

**Always:** Keep `storyboard.json` as the machine authority and `index.html` as a pure projection. Preserve existing slide row ordering from `gary_slide_output` and never mutate existing outbound contracts from Gamma operations. New behavior must be additive and backward-compatible when related assets are absent.

**Ask First:** If linked assets should become mandatory for any gate, or if schema versioning must trigger fail-closed behavior in downstream validators beyond current storyboard consumers.

**Never:** Do not add interactive approval UI in HTML. Do not rewrite Gary generation/dispatch logic to fit storyboard needs. Do not bundle literal-visual download persistence into this slice (tracked in deferred work).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | Gary payload + valid related-assets file containing non-slide entries with labels/links/types | Generated manifest includes appended non-slide entries and HTML renders link/type metadata without breaking slide rows | N/A |
| OPTIONAL_INPUT_ABSENT | Gary payload only (no related-assets argument) | Manifest/HTML remain behaviorally equivalent to current implementation | N/A |
| INVALID_RELATED_ASSET_ENTRY | Related-assets file includes malformed entry (missing required label or link) | Generation fails with clear validation error identifying bad entry index | Exit non-zero with ValueError context |
| REMOTE_AND_LOCAL_LINKS | Related-assets file mixes URL links and local file links | URL links render clickable anchors; local links are emitted as relative/static links | Invalid path treated as missing status in output row |

</frozen-after-approval>

## Code Map

- `skills/bmad-agent-marcus/scripts/generate-storyboard.py` -- Extend manifest builder + HTML projection + CLI for related assets.
- `skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py` -- Add regression and edge-case tests for related-asset parsing/rendering.
- `_bmad-output/implementation-artifacts/sb-1-evolving-lesson-storyboard-run-view.md` -- Story anchor for acceptance intent and scope continuity.

## Tasks & Acceptance

**Execution:**
- [x] `skills/bmad-agent-marcus/scripts/generate-storyboard.py` -- Add optional related-assets loader/validator and merge into output rows -- enables run-view storyboard beyond slides.
- [x] `skills/bmad-agent-marcus/scripts/generate-storyboard.py` -- Render non-slide linked assets in HTML with type/label/link/status columns -- keeps single scannable storyboard artifact.
- [x] `skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py` -- Add tests for valid related assets, malformed entries, and no-input compatibility -- protects backward behavior.
- [x] `skills/bmad-agent-marcus/SKILL.md` -- Document operator command for refreshed storyboard with related-assets input -- keeps Marcus protocol aligned.

**Acceptance Criteria:**
- Given a valid related-assets file, when storyboard generation runs, then non-slide entries appear in manifest/HTML with stable ordering after slide rows.
- Given no related-assets file, when generation runs, then output remains compatible with existing tests and storyboard consumers.
- Given malformed related-assets entries, when generation runs, then the command exits non-zero with a specific validation message.
- Given mixed URL/local related links, when HTML is generated, then links remain usable and entry status correctly identifies present/remote/missing.

## Spec Change Log

## Design Notes

Use a small normalized shape for appended entries to avoid row-type branching in many places:

```json
{
  "row_kind": "related_asset",
  "asset_type": "video|audio|interactive|source|other",
  "label": "Module intro b-roll",
  "link": "relative/path/or/url",
  "asset_status": "present|remote|missing"
}
```

This keeps renderer logic simple while preserving future expansion for run-stage fields.

## Verification

**Commands:**
- `.venv/Scripts/python -m pytest skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py -q` -- expected: all tests pass.
- `.venv/Scripts/python skills/bmad-agent-marcus/scripts/generate-storyboard.py generate --payload <fixture> --out-dir <tmp> --related-assets <fixture>` -- expected: storyboard.json/index.html include related rows.

**Manual checks (if no CLI):**
- Open generated `index.html` and confirm related asset rows are visible and clickable.

## Suggested Review Order

**Manifest expansion and authority**

- Validate additive schema and normalized sequencing for non-slide run artifacts.
  [`generate-storyboard.py:118`](../../skills/bmad-agent-marcus/scripts/generate-storyboard.py#L118)

- Confirm slide ordering remains canonical while related rows append deterministically.
  [`generate-storyboard.py:188`](../../skills/bmad-agent-marcus/scripts/generate-storyboard.py#L188)

**Rendering and operator visibility**

- Check HTML projection branch for related-asset rows and link/status presentation.
  [`generate-storyboard.py:328`](../../skills/bmad-agent-marcus/scripts/generate-storyboard.py#L328)

- Verify CLI surface exposes the new input contract without changing existing commands.
  [`generate-storyboard.py:553`](../../skills/bmad-agent-marcus/scripts/generate-storyboard.py#L553)

- Ensure runbook guidance matches implementation flag and expected operator flow.
  [`SKILL.md:123`](../../skills/bmad-agent-marcus/SKILL.md#L123)

**Regression coverage**

- Review edge-case guard for malformed slide collections in summary generation.
  [`test_generate_storyboard.py:101`](../../skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py#L101)

- Verify related-asset parsing/validation and sequence consistency assertions.
  [`test_generate_storyboard.py:181`](../../skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py#L181)

- Confirm end-to-end CLI behavior with `--related-assets` remains green.
  [`test_generate_storyboard.py:392`](../../skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py#L392)
