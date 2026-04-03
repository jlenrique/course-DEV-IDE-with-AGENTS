# HAPPY PATH SIMULATION — v3 Harmonization Pass
## Narrated Deck Video Export: C1-M1-P2 "Macro Trends in Healthcare Innovation"
### 2026-04-03 | Canonical Template Naming Harmonized

Simulation scope: End-to-end APP run from session start through final Gate 4 approval, with explicit workflow-template selection, party-mode consultation at every stage, and validation evidence.

Supersedes:
- tests/Happy Path Simulation Display Screens 2026-04-03.md (v2)

Primary harmonization objective:
- Canonical Template 1: `narrated-deck-video-export` (no aliases)
- Canonical Template 2: `narrated-lesson-with-video-or-animation` (tool-agnostic naming; no Kling tool name in ID)
- Canonical Template 3: `lesson-adaptive-orchestration` (dynamic orchestration mode; policy/routing driven, not a fixed linear template)

---

## Party-Mode Team (Consulted At Each Stage)

- Winston (Architect): architecture, contracts, stage dependencies
- Amelia (Developer): implementation, CLI behavior, schema integrity
- Bob (Scrum Master): gate protocol and execution order discipline
- Quinn (QA): validator coverage and quality-gate evidence
- Mary (Business Analyst): naming clarity and user-facing semantics

---

## Stage 0: Session Open & Settings Handshake

Marcus loads:
- _bmad/core/config.yaml
- state/runtime/mode_state.json
- specialist registry
- workflow template registry

Marcus asks for execution mode + quality preset confirmation before execution.

Party checks:
- Bob: handshake protocol followed
- Winston: fail-fast load behavior confirmed for workflow registry

---

## Stage 1: Intent Parsing + Workflow Template Selection Moment

User request:
"Build C1/M1/P2 as a narrated slide presentation that will be exported as video in Descript; no custom animation generation for this run."

Marcus evaluates available canonical templates:

1. `narrated-deck-video-export`
- narrated slides + narration + compositing guide + post-composition validation
- no custom motion-generation stage required

2. `narrated-lesson-with-video-or-animation`
- same baseline chain plus explicit motion-generation stage
- intended when custom generated animation/video is requested

3. `lesson-adaptive-orchestration`
- dynamic path, selected at runtime by conversational decisions
- not used for this fixed happy-path run

Decision:
- Selected template: `narrated-deck-video-export`
- Rationale: delivery is video, but custom animation/video asset generation is out of scope for this run

Planner invocation:

```bash
python skills/bmad-agent-marcus/scripts/generate-production-plan.py \
  narrated-deck-video-export --module M1 --lesson P2
```

Observed planner behavior:
- canonical ID appears in help and output
- no alias dependency for template 1
- stage list generated from registry

Party checks:
- Mary: naming now matches user mental model (delivery format vs asset composition)
- Amelia: template choice is deterministic and traceable in planner output

---

## Stage 2: Fidelity Discovery

Marcus asks literal fidelity questions (visuals and literal text requirements).

Captured guidance:
- literal visual: dual-axis chart from source page 7
- literal text: 10 knowledge-check topics from chapters 2 and 3

Party checks:
- Winston: upstream fidelity intent captured before source wrangling execution
- Quinn: source_ref capture enables later gate traceability

---

## Stage 3: Source Wrangling

Source Wrangler builds source bundle:
- extracted.md
- metadata.json
- ingestion-evidence.md
- raw/

Validator command:

```bash
python skills/bmad-agent-marcus/scripts/validate-source-bundle-confidence.py \
  --bundle-dir course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal/
```

Party checks:
- Quinn: validator contract exists and is covered by tests

---

## Stage 4: Vera G0 Source Completeness

Gate contract:
- state/config/fidelity-contracts/g0-source-bundle.yaml

Result:
- pass

Party checks:
- Winston: G0 used as intended prior to downstream creative generation

---

## Stage 5: Irene Pass 1 (Lesson Plan + Slide Brief)

Irene outputs:
- lesson plan
- slide brief with fidelity tags
- card-level instructions for Gary

Party checks:
- Amelia: template usage aligned with content-creator references
- Mary: artifact language remains user-review friendly for Gate 1

---

## Stage 6: Vera G1 (Lesson Plan vs Source)

Result:
- pass

Party checks:
- Quinn: objective/source alignment validated before slide generation

---

## Stage 7: Vera G2 (Slide Brief vs Lesson Plan)

Result:
- pass

Party checks:
- Winston: confirms planning coherence before any expensive generation calls

---

## Stage 8: Quinn-R Quality G2

Review dimensions:
- instructional alignment
- style adherence
- accessibility basics

Result:
- pass

Party checks:
- Bob: quality gate precedes user checkpoint as required

---

## Stage 9: Gate 1 Human Approval

User reviews lesson plan + slide brief and approves.

Party checks:
- Bob: explicit approval captured before next stage

---

## Stage 10: Imagine Handoff for Literal Visuals

User supplies rebranded literal visuals.
Marcus validates URL/media readiness for Gamma handoff.

Party checks:
- Quinn: literal visuals are now explicit controlled inputs, not implicit assumptions

---

## Stage 11: Gary Slide Generation

Gary executes mixed-fidelity generation and returns slide artifacts.

Dispatch validator:

```bash
python skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py \
  --payload gary-dispatch.json
```

Party checks:
- Winston: fail-closed dispatch guard protects Gate 2
- Amelia: contiguous card mapping and local file checks prevent downstream breakage

---

## Stage 12: Storyboard Generation (Marcus)

Marcus creates storyboard JSON + HTML view from Gary payload.

Party checks:
- Bob: correct sequence (dispatch validation before storyboard)

---

## Stage 13: Vera G3 (Generated Slides vs Slide Brief)

Result:
- pass

Party checks:
- Winston: perception-based slide verification active (not text-only comparison)

---

## Stage 14: Quinn-R Quality G3

Result:
- pass with minor non-blocking note

Party checks:
- Quinn: quality notes are advisory unless threshold breach

---

## Stage 15: Gate 2 Human Approval

User reviews slides and approves for narration handoff.
Authorized storyboard snapshot written.

Party checks:
- Bob: critical gate protocol correctly enforced

---

## Stage 16: Irene Pass 2 (Narration + Segment Manifest)

Irene uses approved storyboard + perception artifacts to draft:
- narration script
- segment manifest

Handoff validator:

```bash
python skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py \
  --envelope pass2-envelope.json
```

Party checks:
- Amelia: perception grounding requirement enforced by validator
- Quinn: local image path checks prevent unresolved media references

---

## Stage 17: Vera G4 (Narration vs Slides + Lesson Plan)

Result:
- pass

Party checks:
- Winston: confirms script coherence with approved visual payload and source intent

---

## Stage 18: Quinn-R Quality G4

Result:
- pass (minor pacing advisory)

Party checks:
- Mary: findings are actionable and user-comprehensible at checkpoint

---

## Stage 19: Gate 3 Human Approval

User approves narration artifacts.

Party checks:
- Bob: gate closure recorded before audio generation

---

## Stage 20: ElevenLabs Audio Generation

Outputs:
- narration audio files
- caption files
- audio metadata back into manifest

Party checks:
- Quinn: specialized client contract and smoke path are present

---

## Stage 21: Vera G5 (Audio vs Narration)

Result:
- pass

Party checks:
- Winston: post-synthesis verification prevents latent pronunciation/content drift

---

## Stage 22: Quinn-R Pre-Composition Validation

Checks:
- manifest completeness
- file presence
- timing consistency

Result:
- pass

Party checks:
- Quinn: deterministic pre-composition validation completed

---

## Stage 23: Compositor Guide Generation

Commands:

```bash
python skills/compositor/scripts/compositor_operations.py sync-visuals manifest.yaml
python skills/compositor/scripts/compositor_operations.py guide manifest.yaml DESCRIPT-ASSEMBLY-GUIDE.md
```

Result:
- Descript handoff package generated

Party checks:
- Amelia: compositor command surface intact

---

## Stage 24: Descript Manual Assembly (User)

User assembles package and exports MP4 + captions.

Party checks:
- Mary: handoff instructions are explicit and operationally usable

---

## Stage 25: Quinn-R Post-Composition Validation (G6)

Contract:
- state/config/fidelity-contracts/g6-composition.yaml

Result:
- pass

Party checks:
- Winston: post-composition validation is correctly separated from pre-composition checks

---

## Stage 26: Gate 4 Final Human Approval

User reviews final output and approves.

Party checks:
- Bob: full gate sequence complete and closed

---

## Stage 27: Run Finalization

Marcus summarizes outputs and final asset locations.
Run closes in ad-hoc mode without tracked-state persistence.

Party checks:
- Mary: summary language is clear and aligned to user next actions

---

## Remediation Log (Harmonization Pass)

Remediation 1:
- issue: canonical naming ambiguity between lesson scope and delivery format
- action: introduced harmonized canonical names and removed aliases from template 1
- status: complete

Remediation 2:
- issue: tool-name leakage in canonical naming
- action: renamed motion-enabled canonical template to tool-agnostic `narrated-lesson-with-video-or-animation`
- status: complete

Remediation 3:
- issue: stale references to legacy narrated IDs in tests/docs
- action: updated registry, tests, and docs to harmonized canonical names
- status: complete

---

## Validation Evidence

Planner help now includes harmonized IDs:
- narrated-deck-video-export
- narrated-lesson-with-video-or-animation

Test evidence run:
- `test-generate-production-plan.py`: 10 passed
- Core Marcus suite (planner + dispatch + pass2 + source validators): 46 passed

---

## Party-Mode Team Closeout

- Winston: architecture coherent, naming boundaries now explicit
- Amelia: implementation safe; canonical IDs enforced by tests
- Bob: process integrity maintained through all gates
- Quinn: validator coverage preserved; no regression detected
- Mary: user-facing semantics now map cleanly to intent

Simulation status: COMPLETE.
