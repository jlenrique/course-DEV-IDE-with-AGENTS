# Next Session Start Here

> Scope note: this file tracks APP project development state only.
> For production content operations, use docs/workflow/production-session-launcher.md.

## Current State (as of 2026-04-05, end of phase-03/sunday-afternoon-2026-04-05)

- Active branch: **master** (session merged)
- Working tree: clean
- Latest completed work: Party Mode planning session — 3 new epics (12-14) with 15 stories formally planned, documented, and registered
- All legacy epics: **done** (11 epics, 47 stories, all complete)
- New epics in backlog: **Epic 12** (5 stories), **Epic 13** (3 stories), **Epic 14** (7 stories)
- Template ID: `g_gior6s13mvpk8ms` (Image Card beta, image source: placeholder)

## Immediate Next Action

1. **Begin Epic 12 implementation** — Story 12.1: Dual-Dispatch Infrastructure. Add `double_dispatch` flag to `run-constants.yaml` and extend `execute_generation()` in `gamma_operations.py` to make two independent Gamma API calls per slide position when the flag is `true`.
2. **Read Story 12.1 spec**: `_bmad-output/implementation-artifacts/12-1-dual-dispatch-infrastructure.md` for full acceptance criteria.
3. **Sequencing reminder**: Epic 12 → Epic 13 → Epic 14. Do not start Epic 13 before Epic 12 is complete. Do not start Epic 14 before Epic 13 (specifically Story 13.2) is complete. Stories 14.4 and 14.5 can run in parallel.

## Branch Metadata

```bash
# Session work merged to master. For next session:
git checkout -b phase-04/description
```

## Key Changes This Session (2026-04-05 afternoon)

### Planning Artifacts
- **epics.md**: Epics 12, 13, 14 appended with full story definitions and acceptance criteria
- **15 story files created** in `_bmad-output/implementation-artifacts/`:
  - 12-1 through 12-5 (Double-Dispatch Gamma Slide Selection)
  - 13-1 through 13-3 (Visual-Aware Irene Pass 2 Scripting)
  - 14-1 through 14-7 (Motion-Enhanced Presentation Workflow)
- **sprint-status.yaml**: All 15 new stories registered as `backlog`
- **bmm-workflow-status.yaml**: Updated counts (14 epics, 62 stories), new key decisions, next step

### Party Mode Consensus Decisions
- **Double-dispatch**: per-run flag (not per-slide), both variants fidelity-reviewed before selection, Irene gets only winners
- **Visual-aware Irene**: perception mandatory (was optional), visual references default 2 per slide, LOW-confidence escalates to Marcus not user
- **Motion workflow**: Gate 2M separate from Gate 2, motion is additive, Kira image-to-video preferred, budget auto-downgrade, animation guidance tool-agnostic
- **Cross-epic**: Irene receives only selected winner slides (losers archived)
- **Operational**: resolve questions via party mode team consensus rather than interrupting user

## Unresolved Issues

- **Accent vs background classification**: Gamma's AI classifies images by visual content. Diagrammatic/infographic images get accent placement (cropped). Cannot be overridden via API. Composite fallback handles it.
- **PowerShell `NativeCommandError`**: Python scripts logging to stderr cause PowerShell to report exit code 1. Not a real failure — use `$LASTEXITCODE`.
- **Dispatch log encoding**: `Tee-Object` writes UTF-16 logs; `Get-Content -Encoding Unicode` is needed.
- **No code changes this session**: All work was planning-only. No implementation code was written or modified. The literal-visual anti-fade + fail-fast from the prior session (phase-02) is the current production state.

## Hot-Start Paths

### Epic 12 implementation targets
- `skills/gamma-api-mastery/scripts/gamma_operations.py` — `execute_generation()` dual-dispatch extension
- `state/config/run-constants.yaml` — `double_dispatch` parameter
- `skills/gamma-api-mastery/scripts/generate_storyboard.py` — selection storyboard
- `skills/quality-control/scripts/visual_fill_validator.py` — variant validation

### Planning reference
- `_bmad-output/planning-artifacts/epics.md` (Epics 12-14 at end of file)
- `_bmad-output/implementation-artifacts/12-1-dual-dispatch-infrastructure.md` (first story spec)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (backlog state)

### Existing infrastructure (unchanged)
- `skills/gamma-api-mastery/scripts/gamma_operations.py` (lines ~1370-1530: literal-visual dispatch)
- `skills/quality-control/scripts/visual_fill_validator.py` (variance-based validator)
- `skills/gamma-api-mastery/scripts/tests/test_literal_visual_prompt_harness.py` (live API prompt harness)
- Template ID: `g_gior6s13mvpk8ms` — Image Card beta, image source: placeholder
- API reference: https://developers.gamma.app/llms-full.txt

## Gotchas

- `skills/quality-control/` has a hyphen — can't import as Python package. Use `sys.path.insert` pattern.
- Background terminals start in `C:\Users\juanl\Documents\GitHub` not the project root. Use absolute paths or `cd` first.
- `runTests` tool may not discover script tests by file path; direct pytest invocation is reliable.
- PowerShell chaining uses semicolons, not &&.
- Template endpoint rejects `imageOptions.source` (HTTP 400) — do not send `noImages` on template calls.
- `gamma-dispatch-*.log` and `tests/prompt-harness-results/` are now gitignored.
