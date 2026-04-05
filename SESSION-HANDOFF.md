# Session Handoff — 2026-04-05 Literal-Visual Fix + Production Run k

## Session Mode

- Execution mode: tracked production run + APP code changes
- Quality preset: production
- Active run: `C1-M1-PRES-20260405k` (run `k` — final successful dispatch)
- Bundle: `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260403`
- Branch: `RUN/Friday-Night-2026-04-03`

## Session Summary

Multi-session effort to fix literal-visual slides (cards 2 and 9) that must show full-bleed preintegration images filling the entire 2400×1350 slide. Gamma's template API renders correctly in the web UI but exports blank PNGs due to a race condition between generation completion and export rendering. Implemented a four-layer defense and validated with run `k`.

## Completed Outcomes

1. **Root cause identified**: Gamma reports generation `status=completed` before the export renderer finishes baking image-card content into the PNG. Evidence: user saw correct images in Gamma's web UI but exported PNGs were blank (12KB).
2. **Prompt hygiene**: Restructured literal-visual prompts — image instruction first, title at end. Previous pattern had title at start, which poisoned Gamma's AI into generating creative content instead of displaying the image.
3. **Retry loop with fill validation**: Added `_MAX_TEMPLATE_RETRIES = 3` with `validate_visual_fill()` quality gate after each download. Edge-band sampling (8px bands, 90% threshold) detects blank exports.
4. **Composite fallback**: When all retries exhaust, `_composite_full_bleed()` reads the local preintegration PNG and composites it at 2400×1350 using Pillow LANCZOS. This is the safety net.
5. **Export settle delay**: Added `_TEMPLATE_EXPORT_SETTLE_SECONDS = 10` — a `time.sleep(10)` between `generate_from_template()` completion and `download_export()`. **Not yet tested with a live dispatch** — added late in the session.
6. **Run `k` dispatched**: All 10 slides produced. Cards 2 and 9 used composite fallback (3/3 template attempts failed for each). Output verified:
   - Slide 02: 2400×1350, 4,429,955 bytes (composite from card-02.png)
   - Slide 09: 2400×1350, 2,927,729 bytes (composite from card-09.png)
   - All other slides: 161KB–1.1MB (Gamma-rendered creative/literal-text cards)
7. **Test suite**: 89 tests passing (5 new tests in `TestLiteralVisualRetryOnBlank`)

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Composite fallback from local PNGs instead of retrying indefinitely | Gamma's export race condition is non-deterministic; infinite retry wastes API quota |
| 10-second settle delay before download | Gives Gamma's export renderer time to bake without adding excessive latency |
| `sys.path.insert` for visual_fill_validator import | `quality-control` directory has a hyphen — can't be a Python package |
| Retry count of 3 | Balances API cost against giving Gamma multiple chances before falling back |

## Lessons Learned

1. **Gamma "Image card" is UI-only** — the API has no `cardType` parameter. Template API with a pre-configured image-card template is the only way to get full-bleed images.
2. **Gamma export race condition** — `wait_for_generation()` returns when `status=="completed"` but the export image may not be rendered yet. A settle delay or polling the export size is needed.
3. **Prompt instruction position matters** — placing the title first caused Gamma to generate creative content even for image-card templates. Image instruction must come first.
4. **PowerShell `NativeCommandError`** — Python scripts logging to stderr cause PowerShell to report exit code 1 even when the script succeeds. Not a real failure — use `$LASTEXITCODE` to check actual exit.
5. **`time.sleep(10)` in production code slows tests** — test suite now takes ~210s because the sleep runs in test paths too. Consider mocking `time.sleep` in the test setup.

## Validation Summary

| Check | Result |
|-------|--------|
| pytest (89 tests) | ✅ All passed (210.51s) |
| Run `k` dispatch | ✅ 10 slides produced, all valid sizes |
| Composite fallback (cards 2, 9) | ✅ 2400×1350, multi-MB files (not blank) |
| git status | 19 modified files, 1,126 insertions / 278 deletions |

## Artifact Update Checklist

| Artifact | Updated? |
|----------|----------|
| `gamma_operations.py` | ✅ Major changes (retry, fallback, settle delay) |
| `test_gamma_operations.py` | ✅ +5 new tests, 10 existing updated |
| `visual_fill_validator.py` | ✅ NEW (untracked) |
| `next-session-start-here.md` | ✅ Rewritten for current state |
| `SESSION-HANDOFF.md` | ✅ This file |
| `sprint-status.yaml` | — No changes (all APP epics already done) |
| `bmm-workflow-status.yaml` | — No changes |
| `project-context.md` | — No changes |
| `agent-environment.md` | — No changes |

## Unresolved Issues

1. **Export settle delay untested in dispatch**: The 10s `time.sleep` was added after run `k`. Next dispatch will be the first live test.
2. **Template quality**: Current template `g_gior6s13mvpk8ms` may not be optimal. User plans to provide a better template next session.
3. **Untracked files**: `visual_fill_validator.py`, dispatch logs, and utility scripts need to be staged and committed.
4. **Test performance**: `time.sleep(10)` in production code makes tests slow (~210s). Should mock sleep in test setup.

## Open Risk

- Risk: The 10s settle delay may be insufficient if Gamma's export renderer takes longer on complex images. If next dispatch still produces blanks, the composite fallback will catch them, but the settle delay value may need tuning.
- Owner: operator
- Mitigation: Composite fallback guarantees valid output regardless of Gamma export timing.
