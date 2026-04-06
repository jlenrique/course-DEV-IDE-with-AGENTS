# HAPPY PATH SIMULATION - Motion + Double-Dispatch
## Narrated Lesson With Video Or Animation: C1-M1-P2 "Macro Trends in Healthcare Innovation"
### 2026-04-05 | Marcus Happy Path Walked Against Canonical Fidelity and Epic 14 Controls

Simulation scope:
- full Marcus-led happy path from session open through Gate 4 close
- motion-enabled workflow
- double-dispatch enabled for per-slide A/B treatment choice
- no live API calls; this is a control-flow and artifact simulation grounded in current scripts, tests, and fidelity contracts

Canonical readiness anchor:
- `reports/structural-walk/standard/history/fidelity-walk-20260405-222432.md` returned `READY` with `Critical findings: 0`

Prompt-pack output paired to this simulation:
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`

Planner truth for this run:
- requested content type: `narrated-deck-video-export`
- `motion_enabled: true`
- effective workflow: `narrated-lesson-with-video-or-animation`
- `DOUBLE_DISPATCH` remains a bounded branch inside the Gary stage rather than a separate workflow family

---

## Control Decision

This simulation adopts the following doc structure decision:
- motion-enabled narrated production is different enough from static narrated production to warrant its own prompt pack
- double-dispatch is not different enough to warrant its own separate doc; it remains a conditional branch inside the prompt pack

Rationale:
- motion adds new gates (`Gate 2M`, `Motion Gate`) and a new run-scoped control plane (`motion_plan.yaml`)
- double-dispatch changes only the slide generation and winner selection segment before the flow rejoins the authorized winner deck

---

## Stage 0: Session Open + Run Creation

Marcus loads:
- workflow template registry
- specialist registry
- baton/state infrastructure
- run constants loader

Operator intent:
- narrated slide lesson delivered as video
- motion enabled
- double-dispatch enabled to compare treatments per slide

Representative run creation:

```powershell
python skills/production-coordination/scripts/manage_run.py create `
  --run-id C1-M1-P2-MOTION-DD-001 `
  --course C1 `
  --module M1 `
  --lesson P2 `
  --content-type narrated-deck-video-export `
  --preset production `
  --mode tracked `
  --double-dispatch `
  --motion-enabled `
  --motion-budget-max-credits 24 `
  --motion-budget-model-preference pro
```

Expected control effects:
- `run-constants.yaml` includes `motion_enabled: true`
- explicit motion budget is present
- run-scoped context includes `motion_plan.yaml`

---

## Stage 1: Workflow Template Selection

Marcus resolves the workflow using the planner:

```powershell
python skills/bmad-agent-marcus/scripts/generate-production-plan.py `
  narrated-deck-video-export --motion-enabled --json
```

Expected result:
- requested template remains `narrated-deck-video-export`
- effective template becomes `narrated-lesson-with-video-or-animation`
- stage order now includes:
  - `gate-2`
  - `gate-2m`
  - `motion-generation`
  - `motion-gate`
  - `narration-and-manifest`

Key Marcus decision:
- `motion_enabled` is the authoritative switch
- double-dispatch does not change the high-level template, only the Gary branch

---

## Stage 2: Preflight + Environment Readiness

Marcus executes readiness before any ingestion:

```powershell
py -3.13 -m scripts.utilities.app_session_readiness --with-preflight --motion-enabled --json-only
py -3.13 -m scripts.utilities.venv_health_check
py -3.13 skills/pre-flight-check/scripts/preflight_runner.py --motion-enabled
```

Happy-path expectations:
- runtime readiness passes
- Kling credentials are present because motion is enabled
- no production progression occurs on warn/fail

Double-dispatch note:
- Marcus also verifies double-dispatch compatibility before Gary dispatch later in the run

---

## Stage 3: Source Authority + Operator Directives

Marcus produces:
- source authority map
- operator directives packet

Control expectation:
- focus/exclusion/special-treatment directives are recorded before Irene sees the source bundle
- all downstream fidelity checks can distinguish true omissions from operator-excluded content

---

## Stage 4: Source Wrangling + G0

Source Wrangler builds:
- `extracted.md`
- `metadata.json`
- `ingestion-evidence.md`

Then Marcus runs:
- source bundle confidence validation
- Vera G0

Happy-path outcome:
- planning packet is ready for Irene

---

## Stage 5: Irene Pass 1

Irene receives:
- source bundle
- metadata
- operator directives
- course context and style bible

Outputs:
- lesson plan
- slide brief
- literal support plan
- fidelity-sensitive literal-visual cards

Then Marcus runs:
- Vera G1
- Vera G2
- Quinn-R quality G2

Human gate:
- Gate 1 approval on lesson plan + slide brief

---

## Stage 6: Gary Pre-Dispatch Package

Marcus builds:
- `g2-slide-brief.md`
- `gary-slide-content.json`
- `gary-fidelity-slides.json`
- `gary-diagram-cards.json`
- `gary-theme-resolution.json`
- `gary-outbound-envelope.yaml`
- `pre-dispatch-package-gary.md`

If literal-visual slides exist:
- Marcus runs the literal-visual operator checkpoint
- dispatch remains blocked until operator-ready assets are confirmed

Double-dispatch control:
- `gary-outbound-envelope.yaml` carries `dispatch_count: 2`

---

## Stage 7: Gary Dual Dispatch

Gary runs variant A and variant B.

Expected artifacts:
- `gary-dispatch-result.json`
- `gary-dispatch-run-log.json`
- `gary-dispatch-result-B.json`
- `gary-dispatch-run-log-B.json`
- exports for both sets

Marcus then runs:
- dispatch-ready validator on A
- dispatch-ready validator on B
- Vera G3 on A
- Vera G3 on B

Happy-path requirement:
- both variant sets are structurally valid before human comparison begins

---

## Stage 8: Variant Selection (Epic 12 Branch)

Marcus presents paired A/B treatments per slide.

Operator task:
- choose the stronger treatment for each slide position

Required artifact:
- `variant-selection.json`

Important control point:
- no Gate 2 authorization yet
- selection must happen before the canonical winner deck exists

This is why double-dispatch remains a local branch:
- once winners are chosen, the run rejoins the standard authorized-deck path

---

## Stage 9: Storyboard A + Gate 2 Winner Approval

Marcus generates the slide review storyboard and collapses the selected winners into the authorized deck.

Representative authorization command:

```powershell
python skills/bmad-agent-marcus/scripts/write-authorized-storyboard.py `
  --manifest [BUNDLE_PATH]/storyboard/storyboard.json `
  --run-id [RUN_ID] `
  --output [BUNDLE_PATH]/authorized-storyboard.json `
  --selections [BUNDLE_PATH]/variant-selection.json
```

Result:
- `authorized-storyboard.json` contains the canonical winner-only deck
- Gate 2 applies to the selected deck, not to unresolved A/B variants

This is the structural hinge between Epic 12 and Epic 14.

---

## Stage 10: Gate 2M Motion Designation

Marcus now treats `authorized-storyboard.json` as the source of truth for motion planning.

He builds and applies the run-scoped motion plan:

```powershell
python skills/production-coordination/scripts/motion_plan.py build `
  --authorized-storyboard [BUNDLE_PATH]/authorized-storyboard.json `
  --output [BUNDLE_PATH]/motion_plan.yaml `
  --motion-enabled `
  --motion-budget-max-credits 24 `
  --motion-budget-model-preference pro
```

```powershell
python skills/production-coordination/scripts/motion_plan.py apply `
  --motion-plan [BUNDLE_PATH]/motion_plan.yaml `
  --designations [BUNDLE_PATH]/motion-designations.json `
  --output [BUNDLE_PATH]/motion_plan.yaml
```

Operator task:
- designate every authorized slide as `static`, `video`, or `animation`
- optionally provide motion brief or guidance notes

Happy-path assumption for this simulation:
- most slides remain static
- a minority route to Kling
- a small subset routes to manual animation

Critical control:
- Gate 2M is separate from Gate 2
- no unresolved or missing slide coverage is allowed in motion-enabled runs

---

## Stage 11: Motion Generation / Import

Marcus routes rows from `motion_plan.yaml`:
- `static` -> no action
- `video` -> Kling generation
- `animation` -> manual animation guidance/import path

Representative behaviors proven by tests:
- image-to-video is preferred when a source image exists
- manual animation import validates file type and duration
- budget logic allows one `pro -> std` downgrade per over-budget clip
- if a clip still exceeds budget after downgrade, the run pauses rather than silently continuing

Expected motion plan state after this stage:
- non-static rows have concrete asset paths
- statuses are no longer `pending`

---

## Stage 12: Motion Gate

Human review occurs on generated/imported motion assets.

Operator choices per non-static slide:
- approve asset
- reset slide to static
- send back for remediation

Gate rule:
- Irene Pass 2 is blocked until the motion plan is complete and all non-static rows intended for the run are approved

---

## Stage 13: Irene Pass 2 (Motion-Aware)

Marcus delegates Irene with:
- winner deck slide output
- source bundle
- operator directives
- Irene Pass 1 artifacts
- `variant-selection.json`
- `motion_plan.yaml`

Irene responsibilities in this happy path:
- generate image perception artifacts for approved slide PNGs
- hydrate segment manifest motion fields from `motion_plan.yaml`
- fail closed if motion plan coverage is missing
- perceive approved motion assets for non-static segments
- write motion-aware narration and segment manifest

Outputs:
- `narration-script.md`
- `segment-manifest.yaml`
- `perception-artifacts.json`
- motion perception confirmations for non-static rows

---

## Stage 14: G4 + Storyboard B

Marcus runs:
- Pass 2 handoff validator
- Vera G4
- Quinn-R quality G4

Then Marcus regenerates Storyboard B:
- selected winner deck
- script context
- motion-aware manifest rows

Operator approval here confirms:
- slide/script alignment
- motion-aware narration still fits the chosen visual treatment

---

## Stage 15: Downstream Production

After Gate 3 approval:
- ElevenLabs generates audio
- Vera G5 validates audio vs narration
- Quinn-R validates pre-composition bundle
- Compositor syncs stills and motion assets into the assembly bundle
- Descript assembly proceeds
- Quinn-R validates exported composition
- Gate 4 closes the run

Important observation:
- downstream stages are not structurally reinvented by Epic 14
- the major change is that the manifest and assembly bundle now carry motion assets and placement instructions

---

## Happy-Path Verdict

This motion + double-dispatch run is structurally sound on the current implementation.

Why:
- canonical fidelity walk is `READY`
- Epic 12 winner selection can collapse A/B variants into a canonical authorized deck
- Epic 14 motion planning binds only to that authorized winner deck
- motion-enabled Irene Pass 2 is fail-closed on incomplete motion coverage
- static slides remain backward compatible

Doc recommendation confirmed by the simulation:
- motion-enabled narrated production should have its own prompt pack
- double-dispatch should remain an inline branch inside the static and motion prompt packs rather than becoming its own document family
