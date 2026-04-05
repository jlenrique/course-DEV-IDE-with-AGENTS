# Next Session Start Here

> Scope note: this file tracks APP project development state only.
> For production content operations, use docs/workflow/production-session-launcher.md.

## Current State (as of 2026-04-05, end of RUN/Friday-Night-2026-04-03)

- Active branch: **RUN/Friday-Night-2026-04-03** (not yet merged to master)
- Working tree: modified — session work committed but merge pending
- Latest completed work: Literal-visual template dispatch with retry loop, fill validation quality gate, composite fallback, and export settle delay
- All BMAD epics: **done** (11 epics, 47 stories, all complete)
- Production run: `C1-M1-PRES-20260405k` — 10 slides produced, literal-visual cards 2 & 9 via composite fallback

## Immediate Next Action

1. **Provide a better Gamma template** for literal-visual full-bleed image cards. The current template (`g_gior6s13mvpk8ms`) renders correctly in Gamma's web UI but exports as blank PNGs. Hypothesis: Gamma's export renderer races ahead of image settlement. The 10-second `_TEMPLATE_EXPORT_SETTLE_SECONDS` delay was added but not yet validated in a dispatch.
2. **Run a dispatch** with the new template + settle delay to see if Gamma exports are no longer blank. If they pass fill validation on the first attempt, the retry+fallback path won't fire.
3. If the template fix resolves the export blank issue, consider reducing `_MAX_TEMPLATE_RETRIES` from 3 to 2 or removing the composite fallback (leave it as safety net).

## Branch Metadata

```bash
# Resume on this branch (session work is here):
git checkout RUN/Friday-Night-2026-04-03

# After verifying, merge to master:
git checkout master && git pull origin master
git merge RUN/Friday-Night-2026-04-03
git push origin master
```

## Key Changes This Session (2026-04-04 → 2026-04-05)

### gamma_operations.py
- **Literal-visual template dispatch** rewritten with:
  - Prompt restructured: image instruction first, title at end (was poisoning Gamma's AI)
  - Retry loop (`_MAX_TEMPLATE_RETRIES = 3`) with `validate_visual_fill` quality gate
  - Composite fallback via `_composite_full_bleed()` from preintegration PNGs when retries exhaust
  - Export settle delay (`_TEMPLATE_EXPORT_SETTLE_SECONDS = 10`) between generation completion and download
- Import: `validate_visual_fill` from `skills/quality-control/scripts/` via `sys.path.insert`
- New import: `import time` for settle delay

### test_gamma_operations.py
- 89 tests passing (was ~80)
- New test class `TestLiteralVisualRetryOnBlank` (5 tests):
  - `test_retry_succeeds_on_second_attempt`
  - `test_retries_exhaust_and_falls_back_to_composite`
  - `test_retries_exhaust_no_fallback_logs_error`
  - `test_no_retry_when_first_attempt_passes`
  - `test_prompt_starts_with_image_instruction_not_title`

### visual_fill_validator.py (NEW)
- `skills/quality-control/scripts/visual_fill_validator.py` — edge-band sampling validator
- Functions: `validate_visual_fill(png_path)`, `validate_literal_visual_slides(slide_output)`
- 90% fill threshold, 8px edge bands

## Unresolved Issues

- **Gamma template export blank race condition**: Template API generations render correctly in Gamma UI but export as blank PNGs. Root cause appears to be export firing before image card content settles. The 10s settle delay is coded but untested in dispatch.
- **Exit code 1**: Dispatch exits 1 because stderr receives Python logging warnings (PowerShell `NativeCommandError`). Not a real failure — the dispatch produces valid output.
- **Dispatch log encoding**: `Tee-Object` writes UTF-16 logs; `Get-Content -Encoding Unicode` is needed to read them.

## Hot-Start Paths

- `skills/gamma-api-mastery/scripts/gamma_operations.py` (lines ~1370-1490: literal-visual template dispatch)
- `skills/gamma-api-mastery/scripts/tests/test_gamma_operations.py` (lines ~1870-2010: retry/fallback tests)
- `skills/quality-control/scripts/visual_fill_validator.py` (fill validator)
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260403/gamma-export/` (run k output)
- `course-content/staging/tracked/literal-visual-preintegration/apc-c1m1-tejal/card-02.png` and `card-09.png` (source PNGs for composite fallback)
- Template ID: `g_gior6s13mvpk8ms` — the current template that needs replacement
- `gamma-dispatch-20260405k.log` — last dispatch log (run k, composite fallback active)

## Gotchas

- `skills/quality-control/` has a hyphen — can't import as Python package. Use `sys.path.insert` pattern.
- Background terminals start in `C:\Users\juanl\Documents\GitHub` not the project root. Use absolute paths or `cd` first.
- `runTests` tool may not discover script tests by file path; direct pytest invocation is reliable.
- PowerShell chaining uses semicolons, not &&.
