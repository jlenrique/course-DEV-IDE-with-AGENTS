# Next Session Start Here

> Scope note: this file tracks APP project development state only.
> For production content operations, use docs/workflow/production-session-launcher.md.

## Current State (as of 2026-04-05, end of phase-02/sunday-2026-04-05)

- Active branch: **master** (session merged)
- Working tree: clean
- Latest completed work: Literal-visual anti-fade prompt, fail-fast retry (1 attempt + composite fallback), variance-based fill validation, provenance tracking
- All BMAD epics: **done** (11 epics, 47 stories, all complete)
- Template ID: `g_gior6s13mvpk8ms` (Image Card beta, image source: placeholder)

## Immediate Next Action

1. **Run a production dispatch** with the new anti-fade prompt and fail-fast strategy to validate in a real production run. The prompt harness showed 3/3 success for background-classified images (card-09) and reliable composite fallback for accent-classified images (card-02).
2. **Review composite output quality** — when composite fallback fires, verify the center-crop from `_composite_full_bleed()` is acceptable for the specific image. The composite is deterministic but may crop differently than the user intended.
3. **Optimize source images** if needed — see `skills/gamma-api-mastery/references/literal-visual-image-optimization.md` for attributes that favor Gamma's background classification (dense, photographic, minimal whitespace).

## Branch Metadata

```bash
# Session work is on master. For next session:
git checkout -b phase-NN/description
```

## Key Changes This Session (2026-04-05)

### gamma_operations.py
- **Anti-fade prompt**: "Replace the placeholder image with this image at full opacity (not as background, not faded)."
- **Fail-fast**: `_MAX_TEMPLATE_RETRIES = 1` (was 3) — single template attempt, then composite fallback
- **Export settle**: `_TEMPLATE_EXPORT_SETTLE_SECONDS = 15` (was 10)
- **Download fallback**: When no local preintegration PNG exists, downloads from hosted URL and composites
- **Provenance**: `literal_visual_source` field on output records (template | composite-preintegration | composite-download)

### visual_fill_validator.py
- **Variance detection**: `_content_stddev()` distinguishes blank (<5), faded (<25), real content (>=25)
- **Dual-signal pass logic**: content variance AND (edge fill OR stddev > 40)
- **content_stddev** field in return dict

### New files
- `skills/gamma-api-mastery/scripts/tests/test_literal_visual_prompt_harness.py` — live API test harness (`--run-live-e2e`)
- `skills/gamma-api-mastery/references/literal-visual-image-optimization.md` — dev reference for PNG optimization
- `skills/quality-control/scripts/tests/test_visual_fill_validator.py` — 18 unit tests

## Unresolved Issues

- **Accent vs background classification**: Gamma's AI classifies images by visual content. Diagrammatic/infographic images get accent placement (cropped). This cannot be overridden via the API. The composite fallback handles it, but the Gamma "set" will be incomplete for those slides.
- **PowerShell `NativeCommandError`**: Python scripts logging to stderr cause PowerShell to report exit code 1. Not a real failure — use `$LASTEXITCODE`.
- **Dispatch log encoding**: `Tee-Object` writes UTF-16 logs; `Get-Content -Encoding Unicode` is needed.

## Hot-Start Paths

- `skills/gamma-api-mastery/scripts/gamma_operations.py` (lines ~1370-1530: literal-visual dispatch)
- `skills/gamma-api-mastery/scripts/tests/test_gamma_operations.py` (TestLiteralVisualRetryOnBlank class)
- `skills/quality-control/scripts/visual_fill_validator.py` (variance-based validator)
- `skills/quality-control/scripts/tests/test_visual_fill_validator.py` (18 validator tests)
- `skills/gamma-api-mastery/scripts/tests/test_literal_visual_prompt_harness.py` (live API prompt harness)
- `skills/gamma-api-mastery/references/literal-visual-image-optimization.md` (PNG optimization guide)
- Template ID: `g_gior6s13mvpk8ms` — Image Card beta, image source: placeholder
- API reference: https://developers.gamma.app/llms-full.txt

## Gotchas

- `skills/quality-control/` has a hyphen — can't import as Python package. Use `sys.path.insert` pattern.
- Background terminals start in `C:\Users\juanl\Documents\GitHub` not the project root. Use absolute paths or `cd` first.
- `runTests` tool may not discover script tests by file path; direct pytest invocation is reliable.
- PowerShell chaining uses semicolons, not &&.
- Template endpoint rejects `imageOptions.source` (HTTP 400) — do not send `noImages` on template calls.
- `gamma-dispatch-*.log` and `tests/prompt-harness-results/` are now gitignored.
