# Next Session Start Here

> Scope note: this file tracks APP project development state only.
> For production content operations, use docs/workflow/production-session-launcher.md.

## Current State (as of 2026-04-05, end of phase-04/epic-12-1-dual-dispatch-infrastructure)

- Active branch: **master** (session merged)
- Working tree: clean
- Latest completed work: **Epic 12 fully implemented** — 5 stories (dual-dispatch infrastructure), 192 tests passing, prompt pack bumped to v4.1
- All completed epics: **12 done** (Epics 1-12 + SB, 52 stories)
- Remaining epics in backlog: **Epic 13** (3 stories), **Epic 14** (7 stories)
- Template ID: `g_gior6s13mvpk8ms` (Image Card beta, image source: placeholder)

## Immediate Next Action

1. **E2E test double-dispatch production run** — Run a tracked production using `DOUBLE_DISPATCH: true` in `docs/workflow/production-prompt-pack-v4.1.md` to validate the full double-dispatch pipeline end-to-end before starting Epic 13.
2. **Then begin Epic 13 implementation** — Story 13.1: Mandatory Perception Contract. Read spec: `_bmad-output/implementation-artifacts/13-1-mandatory-perception-contract.md`.
3. **Sequencing reminder**: Epic 13 → Epic 14. Do not start Epic 14 before Epic 13 (specifically Story 13.2) is complete. Stories 14.4 and 14.5 can run in parallel.

## Branch Metadata

```bash
# Session work merged to master. For next session:
git checkout -b phase-05/epic-13-visual-aware-irene
```

## Key Changes This Session (2026-04-05 evening)

### Epic 12: Double-Dispatch Implementation (5 stories, 14 files, 885+ insertions)
- **manage_run.py**: `--double-dispatch` CLI flag, propagated to run context and YAML
- **run_reporting.py**: `double_dispatch` field + cost estimation block when active
- **run_context_builder.py**: `double_dispatch` param in `build_run_context()`, included in `asset_specs.yaml` and CLI args
- **preflight_runner.py**: `check_double_dispatch_compatibility()` conditional preflight check
- **192 tests passing** (101 non-gamma + 91 gamma), 0 failures

### Prompt Pack v4.1 (8 surgical edits)
- **Changelog + version bump** to v4.1
- **DOUBLE_DISPATCH** added to Run Constants (default false)
- **Design principle callout** for Prompt 7B
- **Prompt 1**: preflight compatibility check when double-dispatch true
- **Prompt 6**: `dispatch_count: 2` + `-B` artifact suffix convention
- **Prompt 7**: conditional dual-dispatch logic
- **New Prompt 7B**: Variant Selection Gate (paired-thumbnail storyboard, per-slide A/B select, `variant-selection.json`)
- **Prompt 8**: conditioned on `variant-selection.json` with merged-set resolution
- **File renamed** `production-prompt-pack-v4.md` → `production-prompt-pack-v4.1.md`
- **All 8 live references updated** across operator card, session launcher, session start, trial-run card, token-efficiency doc, fidelity_walk.py, test_fidelity_walk.py

### Party Mode Advisory: Prompt Pack Strategy
- **Consensus**: Separate packs per workflow template (no conditional mega-pack)
- **Future naming**: `production-prompt-pack-slides-motion-v1.md` when motion workflow ships
- **WORKFLOW_TEMPLATE** run constant to be added for auto-resolution
- **Defer common-prefix extraction** until ≥2 packs share >50% content

## Unresolved Issues

- **E2E double-dispatch test pending**: Epic 12 code + prompt pack complete but no production run with `DOUBLE_DISPATCH: true` yet. Schedule for start of next session.
- **Accent vs background classification**: Gamma's AI classifies images by visual content. Diagrammatic/infographic images get accent placement (cropped). Cannot be overridden via API. Composite fallback handles it.
- **PowerShell `NativeCommandError`**: Python scripts logging to stderr cause PowerShell to report exit code 1. Not a real failure — use `$LASTEXITCODE`.
- **Dispatch log encoding**: `Tee-Object` writes UTF-16 logs; `Get-Content -Encoding Unicode` is needed.
- **conftest.py collision**: `tests/conftest.py` and `skills/gamma-api-mastery/scripts/tests/conftest.py` both register `--run-live-e2e`. Run tests in separate pytest invocations to avoid collision.

## Hot-Start Paths

### E2E double-dispatch testing
- `docs/workflow/production-prompt-pack-v4.1.md` — Run Constants block with `DOUBLE_DISPATCH: true`
- `docs/workflow/production-operator-card-v4.md` — updated gate checklist with 7B
- `scripts/state_management/manage_run.py` — `--double-dispatch` flag
- `scripts/utilities/preflight_runner.py` — `check_double_dispatch_compatibility()`

### Epic 13 implementation targets
- `_bmad-output/implementation-artifacts/13-1-mandatory-perception-contract.md` (first story spec)
- `skills/sensory-bridges/` — perception contract and bridge utilities
- `state/config/narration-grounding-profiles.yaml` — per-fidelity channel balance
- `state/config/narration-script-parameters.yaml` — script-wide style knobs

### Planning reference
- `_bmad-output/planning-artifacts/epics.md` (Epics 13-14 at end of file)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (Epic 12 done, 13-14 backlog)

### Existing infrastructure
- `skills/gamma-api-mastery/scripts/gamma_operations.py` (lines ~1370-1530: literal-visual dispatch)
- `skills/quality-control/scripts/visual_fill_validator.py` (variance-based validator)
- Template ID: `g_gior6s13mvpk8ms` — Image Card beta, image source: placeholder
- API reference: https://developers.gamma.app/llms-full.txt

## Gotchas

- `skills/quality-control/` has a hyphen — can't import as Python package. Use `sys.path.insert` pattern.
- Background terminals start in `C:\Users\juanl\Documents\GitHub` not the project root. Use absolute paths or `cd` first.
- `runTests` tool may not discover script tests by file path; direct pytest invocation is reliable.
- PowerShell chaining uses semicolons, not &&.
- Template endpoint rejects `imageOptions.source` (HTTP 400) — do not send `noImages` on template calls.
- `gamma-dispatch-*.log` and `tests/prompt-harness-results/` are now gitignored.
- conftest.py `--run-live-e2e` collision between `tests/` and `skills/gamma-api-mastery/scripts/tests/` — run separately.
