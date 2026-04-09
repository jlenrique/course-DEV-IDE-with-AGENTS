# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> For production operations, pair it with `docs/operations-context.md` and the workflow docs it points to.

## Current State (as of 2026-04-09, mid-run)

- Active branch: `ops/next-session`
- Expected git state: working tree has uncommitted session work to be committed
- Active production run: `C1-M1-PRES-20260409` — **IN PROGRESS** (Prompts 1-7D complete, paused before Kira video gen + Irene Pass 2)
- Bundle: `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409-motion`
- Run status in DB: `active`
- Workflow: `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`

## Run C1-M1-PRES-20260409 Status

### Completed Prompts
- Prompt 1: Activation + Preflight — PASS
- Prompt 2: Source Authority Map — PASS (carried from C1-M1-PRES-20260406)
- Prompt 2A: Operator Directives — carried, approved
- Prompt 3: Ingestion + Validation — PASS
- Prompt 4: Quality Gate + Irene Packet — PASS, Vera G0 PASS
- Prompt 4.5: Slide Count & Runtime — locked (15 slides, 10 min, 40s avg, 0.5 variability)
- Prompt 5: Irene Pass 1 — 15 slides, Gate 1 PASS (Vera G1, G2, Quinn-R G2)
- Prompt 5.5: HIL Mode Approval — approved (11 creative, 3 literal-text, 1 literal-visual)
- Prompt 6: Pre-Dispatch Package — all 7 artifacts built, validated
- Prompt 6B: Literal-Visual Checkpoint — card-03.png confirmed
- Prompt 7: Gary Dispatch — double-dispatch with deliberate strategies, 30 PNGs on disk, validator PASS
- Prompt 7B: Variant Selection — 14×B + slide 9×A, operator-exported from interactive storyboard UI
- Prompt 7C: Storyboard A + Gate 2 — authorized-storyboard.json written, 15 winner slides collapsed
- Prompt 7D: Gate 2M Motion — slides 1,5 = video (Kira), all others = static, motion_plan.yaml applied

### Next Prompts (in order)
1. **Fix PNG export ordering** — CRITICAL: exported PNGs are mis-mapped to card numbers. `_materialize_exported_slide_paths` in `gamma_operations.py` assumes positional correspondence but Gamma reorders internally. Investigate and fix before any perception.
2. **Kira video generation** — slides 1 and 5, pro model, 125 credit budget. Use Kling API.
3. **Motion Gate** — approve generated clips
4. **Perception bridge** — sensory bridge read of all 15 winner stills + 2 video clips
5. **Irene Pass 2** — narration with "triple vision" (visuals + on-screen text + source material)

## Key Run Parameters

```yaml
run_id: C1-M1-PRES-20260409
prior_run_id: C1-M1-PRES-20260406
double_dispatch: true
deliberate_dispatch: true
variant_strategies: instr_focus (creative), proportional_illus (literal-text), literal_freedom (literal-visual)
motion_enabled: true
motion_budget: 125 credits, pro model
motion_slides: 1 (video), 5 (video), rest static
locked_slide_count: 15
target_total_runtime_minutes: 10
slide_runtime_average_seconds: 40
theme: hil-2026-apc-nejal-A (Gamma API ID: njim9kuhfnljvaa)
voice: TBD (not yet selected this run)
```

## Branch Metadata

```bash
# Already on ops/next-session — continue from here
git status
```

## Code Changes This Session (to be committed)

| File | Change |
|------|--------|
| `gamma_operations.py` | Double-dispatch export dir routing, CLI theme override fix, composite fallback URL fix, deliberate variant strategies |
| `validate-gary-dispatch-ready.py` | Double-dispatch paired card sequence support |
| `generate-storyboard.py` | Interactive A/B selection UI, project-root asset resolution, publish overwrite support |
| `write-authorized-storyboard.py` | Nested `{selections: {...}}` format support from browser export |
| `slide_count_runtime_estimator.py` | Removed hard cap, added --max-slides |
| `test_gamma_operations.py` | Fixed deliberate dispatch test fixtures |
| `rerun-carry-forward-manifest.md` | New doc for re-run bundle setup |

## Known Issues

1. **PNG export ordering**: Gamma deck export PNGs don't match card numbers. The `_materialize_exported_slide_paths` function in `gamma_operations.py` needs investigation. This affects storyboard thumbnail accuracy and perception bridge input.
2. **3 test failures**: `TestExecuteGenerationDeliberateDispatch` PNG export tests have mock fixture issues (not code bugs — live dispatch works correctly).
3. **Vera/Quinn storyboard scores**: Deck-level, not per-slide. Per-slide scoring requires running Vera G3 perception on each PNG individually.

## Storyboard URL

https://jlenrique.github.io/assets/storyboards/C1-M1-PRES-20260409/index.html

## Hot-Start Paths

- `docs/operations-context.md`
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `docs/workflow/rerun-carry-forward-manifest.md`
- Bundle: `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409-motion/`
- Exemplar: `resources/exemplars/gamma/L3-mm-of-innovation/brief.md`
