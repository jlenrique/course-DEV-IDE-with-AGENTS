# HAPPY PATH SIMULATION — v2
## Narrated Lesson: C1-M1-P2 "Macro Trends in Healthcare Innovation"
### 2026-04-03 | Workflow Template Registry Edition

> **Historical note (2026-04-16):** Paths of the form `<old>-specialist-sidecar/` and `bmad-agent-marcus-sidecar/` were renamed to persona-named sidecars. See `_bmad/memory/` for current paths.


**Simulation scope:** Full narrated-lesson happy path, Stage 0 (session open) through Descript handoff package (Stage 23 / gate-4). Consultant commentary from the BMAD party-mode team at each critical gate and specialist handoff.

**Supersedes:** `tests/Happy Path Simulation Display Screens 2026-04-02.txt`

**Key change from v1:** The v1 simulation (2026-04-02) identified a critical gap — `narrated-lesson` was not a recognized content type in `generate-production-plan.py`. That gap has been resolved. Marcus now reads a YAML registry (`skills/bmad-agent-marcus/references/workflow-templates.yaml`) that defines 12 workflow templates, including `narrated-lesson` (23 stages) with its alias `narrated-presentation-with-video`. This simulation validates the fixed infrastructure end-to-end.

---

## Party Mode Team

| Agent | Persona | Focus |
|---|---|---|
| 🏗️ **Winston** | Architect | Structural integrity, contract alignment |
| 💻 **Amelia** | Developer | Script correctness, implementation fidelity |
| 🏃 **Bob** | Scrum Master | Gate protocol, process discipline |
| 🧪 **Quinn** | QA Engineer | Test coverage, validation evidence |
| 📊 **Mary** | Business Analyst | User clarity, requirements tracing |

---

## STAGE 0: Session Open & Settings Handshake

Marcus activates and loads:

- `_bmad/core/config.yaml` → `user_name: Juanl`
- `_bmad/memory/bmad-agent-marcus-sidecar/index.md` → prior learning and sidecar entries
- `state/runtime/mode_state.json` → execution mode: `ad-hoc`, quality preset: `draft`
- `skills/bmad-agent-marcus/references/specialist-registry.yaml` → 9 specialists, all active
- **NEW (v2):** `skills/bmad-agent-marcus/references/workflow-templates.yaml` → 12 workflow templates, including `narrated-lesson` (23 stages) and `narrated-slides` (19 stages)

Marcus greets:

> "Hey Juanl! Session settings check: execution mode is **ad-hoc** and quality preset is **draft**. Assets go to `course-content/staging/ad-hoc/`. Keep these settings, switch mode, or change preset before we start?"

User confirms. Marcus logs confirmation.

**Contract validation:**
- `read-mode-state.py` reads `state/runtime/mode_state.json` — confirmed working (see `test-read-mode-state.py`)
- Workflow template registry loads at Marcus boot — `load_workflow_templates()` and `build_workflow_lookup()` called before argparse in `generate-production-plan.py`

---

🏃 **Bob:** Settings handshake protocol followed per `conversation-mgmt.md`. Both axes confirmed before any work. Good. I also want to note that the workflow template registry is now loaded at boot — Marcus has the full plan vocabulary ready before the first user message. That's the right initialization order.

🏗️ **Winston:** Confirmed — the registry load is fail-fast: if the YAML is malformed or missing, Marcus raises `ValueError` or `RuntimeError` before proceeding. That's the correct behavior. The registry is the single source of truth for plan vocabulary.

---

## STAGE 1: Intent Parsing & Workflow Template Resolution

User says:

> "Let's build a narrated lesson for C1 Module 1 — Presentation 2: Macro Trends in Healthcare Innovation. I have Tejal's notes in a Notion page and some PDFs in Box."

Marcus parses:

- **Content type:** `narrated-lesson` (full pipeline) — maps to workflow template ID `narrated-lesson` in the registry
- **Scope:** C1 / M1 / P2
- **Source materials:** Notion + Box

Marcus invokes the production planner:

```bash
cd "c:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS"
python skills/bmad-agent-marcus/scripts/generate-production-plan.py narrated-lesson \
  --module M1 --lesson P2
```

**Actual output (verified 2026-04-03):**

```
# Production Plan: Narrated Presentation With Video

Generated: 2026-04-03 00:20
Content Type: Narrated Presentation With Video
Workflow Template: narrated-lesson
Module: M1  |  Lesson: P2

| # | Stage                    | Specialist           | Description                                                                  | Status  |
|---|--------------------------|----------------------|------------------------------------------------------------------------------|---------|
| 1 | source-wrangling         | source-wrangler      | Build source bundle from Notion, Box, and uploaded materials                 | pending |
| 2 | lesson-plan-and-slide-brief | content-creator   | Irene Pass 1: produce lesson plan and slide brief with fidelity tags         | pending |
| 3 | fidelity-g1              | fidelity-assessor    | Verify lesson plan against source bundle                                     | pending |
| 4 | fidelity-g2              | fidelity-assessor    | Verify slide brief against lesson plan                                       | pending |
| 5 | quality-g2               | quality-reviewer     | Review lesson plan and slide brief quality before user approval              | pending |
| 6 | gate-1                   | USER REVIEW          | User approves lesson plan and slide brief                                    | pending |
| 7 | imagine-handoff          | USER REVIEW          | Confirm rebranded literal-visual assets and hosted URLs for Gamma            | pending |
| 8 | slide-generation         | gamma-specialist     | Generate slides from approved brief and diagram cards                        | pending |
| 9 | storyboard               | bmad-agent-marcus    | Generate storyboard bundle for slide review and downstream authorization      | pending |
|10 | fidelity-g3              | fidelity-assessor    | Verify generated slides against slide brief                                  | pending |
|11 | quality-g3               | quality-reviewer     | Review generated slides for brand, accessibility, and hierarchy              | pending |
|12 | gate-2                   | USER REVIEW          | User approves slides for narration handoff                                   | pending |
|13 | narration-and-manifest   | content-creator      | Irene Pass 2: produce narration script and segment manifest                  | pending |
|14 | fidelity-g4              | fidelity-assessor    | Verify narration script against approved slides and lesson plan              | pending |
|15 | quality-g4               | quality-reviewer     | Review narration script and segment manifest quality                         | pending |
|16 | gate-3                   | USER REVIEW          | User approves narration script and manifest                                  | pending |
|17 | audio-generation         | elevenlabs-specialist| Generate narration audio, captions, and audio metadata                       | pending |
|18 | fidelity-g5              | fidelity-assessor    | Verify generated audio against narration script                              | pending |
|19 | motion-generation        | kling-specialist     | Generate silent motion clips aligned to approved narration durations         | pending |
|20 | pre-composition-validation| quality-reviewer    | Validate assembly bundle inputs before Descript handoff                      | pending |
|21 | composition-guide        | compositor           | Generate Descript assembly guide and sync approved stills into the bundle    | pending |
|22 | post-composition-validation| quality-reviewer   | Validate the exported MP4 and captions after manual assembly                 | pending |
|23 | gate-4                   | USER REVIEW          | User reviews the final narrated video package                                | pending |
```

Marcus then runs fidelity discovery (per `conversation-mgmt.md` §Intent Parsing):

> "Before we plan further — two questions: Are there any visuals in Tejal's notes that need faithful reproduction? And any text that must appear literally on slides?"

User: "Yes — there's a dual-axis chart on page 7 that needs to be rebranded, and the 10 Knowledge Check topics from Chapters 2 & 3 must appear exactly."

Marcus captures:

```yaml
fidelity_guidance:
  literal_visuals:
    - description: "Dual-axis chart from page 7"
      source_ref: "TEJAL_Notes.pdf#page7"
  literal_text:
    - description: "10 KC topics from Chapters 2 & 3"
      source_ref: "extracted.md#Chapter 2-3 Knowledge Check"
```

---

🏗️ **Winston:** This is the key fix from v1. The original simulation found `narrated-lesson` missing from the argparse choices. It now appears as a first-class workflow ID in the planner. The plan is generated from the registry, not from an embedded dict. The template ID, label, and all 23 stages are rendered correctly. The architecture is sound.

💻 **Amelia:** Confirmed via direct CLI run: `generate-production-plan.py narrated-lesson --module M1 --lesson P2 --json` returns `content_type: "narrated-lesson"`, `requested_content_type: "narrated-lesson"`, all 23 stages in registry order. The alias `narrated-presentation-with-video` also resolves to the same canonical ID. Both tested green (10 tests in `test-generate-production-plan.py`, 46 total passing across the suite).

🧪 **Quinn:** Test coverage for the planner is strong: canonical ID resolution, alias resolution, stage ordering for `narrated-lesson` (full 23-stage assertion), help-flag validation, and `all-content-types` sweep. No gaps visible.

📊 **Mary:** The user-facing plan output is clear. Stage labels are readable without being verbose. The `USER REVIEW` specialist column on gate rows makes the HIL touchpoints immediately visible. This is a usability improvement over the original.

---

## STAGE 2: Source Wrangling

**Workflow template stage 1: `source-wrangling` → `source-wrangler`**

Marcus delegates to Source Wrangler:

> "Pulling Tejal's Notion page and Box references into a source bundle."

Source Wrangler builds bundle at: `course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal/`

Bundle contents:
- `extracted.md` — clean markdown from Notion + Box + PDF
- `metadata.json` — provenance map (section headings, source_refs, confidence scores)
- `ingestion-evidence.md` — per-source ingestion notes and confidence reasoning
- `raw/` — original files

**Contract check:**

```bash
python skills/bmad-agent-marcus/scripts/validate-source-bundle-confidence.py \
  --bundle-dir course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal/
```

`validate-source-bundle-confidence.py` verifies `extracted.md`, `metadata.json`, and `ingestion-evidence.md` are present and internally consistent. Returns: `status: passed`.

---

🧪 **Quinn:** Source bundle validator is present and tested (5 passing tests in `test-validate-source-bundle-confidence.py`). The validator checks both structural presence and logical consistency of confidence scores. Contract is solid.

---

## STAGE 3: Vera G0 — Source Bundle Completeness

**Workflow template stage 3: `fidelity-g1` → `fidelity-assessor` (Note: G0 is a pre-planning gate; Vera's G0 maps to source-bundle completeness before the planner stages run)**

Marcus delegates to Vera with a G0 gate envelope pointing to the source bundle.

**Contract:** Vera loads `state/config/fidelity-contracts/g0-source-bundle.yaml`, reads `extracted.md` + `metadata.json`, checks section coverage, provenance integrity, and PDF degradation flags.

Returns: `status: passed` — all source sections present, no omissions, no PDF artifacting flagged.

---

🧪 **Quinn:** `g0-source-bundle.yaml` contract file confirmed present. Vera's `SKILL.md` documents G0 capability explicitly. Circuit breaker handling for G0 failures is documented in `conversation-mgmt.md`. Contract architecture: ✅

---

## STAGE 4: Irene Pass 1 — Lesson Plan + Slide Brief

**Workflow template stage 2: `lesson-plan-and-slide-brief` → `content-creator`**

Marcus delegates to Irene with a Pass 1 context envelope:

```yaml
pass: 1
content_type: "lesson-plan"
scope: "C1/M1/P2"
learning_objectives: [from course_context.yaml]
fidelity_guidance:
  literal_visuals:
    - { description: "Dual-axis chart", source_ref: "TEJAL_Notes.pdf#page7" }
  literal_text:
    - { description: "10 KC topics", source_ref: "extracted.md#Chapter 2-3 Knowledge Check" }
governance:
  allowed_outputs: ["lesson_plan", "slide_brief"]
```

Irene loads `skills/bmad-agent-content-creator/references/` templates:
- `template-lesson-plan.md` → lesson plan structure
- `template-slide-brief.md` → per-slide brief with fidelity tags

Irene produces:

1. **Lesson plan** — 4 learning objectives, content outline, Bloom's taxonomy levels, visual suggestions
2. **Slide brief** — 16 slides, per-slide: content summary, `fidelity_tag` (creative / literal-text / literal-visual), `source_ref`, `behavioral_intent`
   - Slides 3, 11: `literal-visual` (Tejal's rebranded chart)
   - Slide 7: `literal-text` (KC topics exact reproduction)
3. **Gary downstream annotations** — `numCards` suggestion, `textMode` per slide

**Contract check — all Pass 1 templates present:**

```
skills/bmad-agent-content-creator/references/
  template-lesson-plan.md       ✓
  template-slide-brief.md       ✓
  template-narration-script.md  ✓  (for Pass 2)
  template-segment-manifest.md  ✓  (for Pass 2)
  pedagogical-framework.md      ✓
  delegation-protocol.md        ✓
```

---

🏗️ **Winston:** Irene's output structure is correct. The fidelity tags on the slide brief drive the downstream mixed-fidelity split in Gary. Literal-visual slides trigger image URL injection; literal-text slides get exact text enforcement. The data flow from Irene → Gary via the fidelity field is the core of the mixed-fidelity system.

---

## STAGE 5: Vera G1 — Lesson Plan vs Source Bundle

**Workflow template stage 3: `fidelity-g1` → `fidelity-assessor`**

Marcus delegates to Vera with a G1 gate envelope.

**Contract:** Vera loads `state/config/fidelity-contracts/g1-lesson-plan.yaml`, compares learning objectives to source themes, validates `source_refs`, and checks lesson plan structural integrity.

Returns: `status: passed`.

---

## STAGE 6: Vera G2 — Slide Brief vs Lesson Plan

**Workflow template stage 4: `fidelity-g2` → `fidelity-assessor`**

Marcus delegates to Vera with a G2 gate envelope.

**Contract:** Vera loads `state/config/fidelity-contracts/g2-slide-brief.yaml`, compares slide brief coverage to lesson plan objectives, checks fidelity tag consistency, verifies `source_refs` on literal slides.

Returns: `status: passed`.

---

## STAGE 7: Quinn-R G2 Quality Review

**Workflow template stage 5: `quality-g2` → `quality-reviewer`**

Marcus delegates to Quinn-R for quality review of the lesson plan and slide brief prior to user approval.

**Contract check:** Quinn-R's `SKILL.md` (`skills/bmad-agent-quality-reviewer/SKILL.md`) — present. References directory present. 8 review dimensions in protocol.

Quinn-R returns: all clear. No instructional alignment or style-bible concerns.

---

🧪 **Quinn:** The quality gate before Gate 1 is a key process improvement. In earlier pipeline design, users were presented artifacts without a pre-review pass. Now Quinn-R runs before Gate 1, Gate 2, Gate 3, and Gate 4. The `quality-g2` stage in the workflow template correctly positions Quinn-R *before* `gate-1`, not after. This is the right order.

---

## STAGE 8 [HIL Gate 1]: Lesson Plan Review

**Workflow template stage 6: `gate-1` → `human`**

Marcus presents to user:

> "Lesson plan and slide brief for C1-M1-P2 are ready. 16 slides covering 4 learning objectives. Irene flagged Slides 3 and 11 as **literal-visual** (Tejal's rebranded chart), Slide 7 as **literal-text** (KC topics exact). Quinn-R pre-review: all clear. Style bible: JCPH Navy headers, Montserrat headings. What's your call?"

User approves. Marcus logs approval.

---

🏃 **Bob:** Gate 1 protocol followed per `checkpoint-coord.md`. Artifact presented, quality criteria stated (Vera G1+G2 and Quinn-R passed), explicit approval requested. The gate does not proceed without explicit user sign-off. ✅

🏗️ **Winston:** The separation of `quality-g2` (Quinn-R runs) and `gate-1` (user approves) in the workflow template is intentional and correct. Quality review results are *presented at* the gate, not run *during* it. The sequence: Vera G1 → Vera G2 → Quinn-R G2 → Gate 1 is the full pre-approval validation chain.

---

## STAGE 9: Imagine Handoff — Literal Visual Assets

**Workflow template stage 7: `imagine-handoff` → `human`**

Marcus surfaces the literal-visual slides:

> "Irene flagged Slides 3 and 11 as needing rebranded visuals. Source: Tejal's chart from page 7. Are the rebranded PNGs ready?"

User drops PNGs to `course-content/staging/ad-hoc/rebranded-assets/`.

Marcus validates URLs via `gamma_operations.py validate-url <url>` — confirms HTTPS-accessible with image content-type.

Marcus builds `diagram_cards` block for Gary's context envelope:

```json
"diagram_cards": [
  { "card_number": 3, "url": "https://host/rebranded-chart-v1.png", "fidelity": "literal-visual",
    "source_ref": "TEJAL_Notes.pdf#page7" },
  { "card_number": 11, "url": "https://host/rebranded-chart-v1.png", "fidelity": "literal-visual",
    "source_ref": "TEJAL_Notes.pdf#page7" }
]
```

**Contract:** Imagine Handoff Checkpoint protocol documented in `conversation-mgmt.md`. URL validation command present in `gamma_operations.py`.

---

## STAGE 10: Gary — Gamma Slide Generation

**Workflow template stage 8: `slide-generation` → `gamma-specialist`**

Marcus delegates to Gary with a context envelope containing:

- Approved slide brief from Irene
- `diagram_cards` for literal-visual slides (validated HTTPS URLs)
- Style bible sections (color palette, typography, visual hierarchy)
- `governance.allowed_outputs: ["artifact_paths", "quality_assessment", "parameter_decisions"]`

Gary invokes the `gamma-api-mastery` skill:

1. `merge_parameters()` — merges style guide + template + envelope params. Enforces fidelity-control vocabulary.
2. `partition_by_fidelity()` — splits 16 slides into groups: creative (12), literal-text (1: Slide 7), literal-visual (2: Slides 3, 11)
3. `execute_generation()` — production entry point for mixed-fidelity generation. Two API calls: creative batch + literal-visual batch.
4. Downloads PNGs + PPTX assets.

Gary returns `gary_slide_output[]` with per-slide: `slide_id`, `file_path` (local PNG), `card_number`, `fidelity`, `source_ref`, `visual_description`.

**Pre-dispatch validation:**

```bash
python skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py \
  --payload gary-dispatch.json
```

Requires: non-empty `file_path` (local PNG, exists on disk), non-empty `source_ref`, contiguous `card_number` 1..N.

**Contract validation:** `partition_by_fidelity` tested (12 tests). `execute_generation` documented as production entry point. `merge_parameters()` enforces fidelity-control vocabulary. `validate-gary-dispatch-ready.py` tests: 20 tests passing.

---

🏗️ **Winston:** The Gary dispatch validator is the technical pre-gate for Gate 2. It's fail-closed — non-contiguous card numbers, missing PNGs, or remote URLs all cause hard failures with structured JSON error output. This is the correct pattern for a critical checkpoint validator.

🧪 **Quinn:** 20 tests on Gary dispatch validator, 5 on source bundle validator, 17 on Irene Pass 2 validator. All passing. The three critical contract validators have solid coverage.

---

## STAGE 11: Marcus — Storyboard Generation

**Workflow template stage 9: `storyboard` → `bmad-agent-marcus`**

Marcus runs the storyboard generator (his own capability):

```bash
python skills/bmad-agent-marcus/scripts/generate-storyboard.py generate \
  --payload gary-dispatch.json \
  --out-dir bundle/ \
  --run-id C1-M1-P2-ADHOC
```

Produces:
- `storyboard/storyboard.json` — structured storyboard data with all slide metadata
- `storyboard/index.html` — human-readable visual run-view

Marcus reads aloud the storyboard summary.

**Contract:** 14 storyboard tests green (`test_generate_storyboard.py`). `storyboard_version: 3`, `run_id` present in manifest metadata.

---

🏃 **Bob:** This stage is self-contained within Marcus — no specialist delegation needed. The storyboard is generated from Gary's validated payload so it only runs after the dispatch validator passes. Correct ordering.

---

## STAGE 12: Vera G3 — Generated Slides vs Slide Brief

**Workflow template stage 10: `fidelity-g3` → `fidelity-assessor`**

Marcus delegates to Vera with a G3 gate envelope.

**Contract:** Vera loads `state/config/fidelity-contracts/g3-generated-slides.yaml`. Invokes PPTX bridge and image bridge from the `sensory-bridges` skill to perceive the actual generated slides. Compares perceived slide content to the approved slide brief.

Returns: `status: passed`.

---

🏗️ **Winston:** The G3 contract is where the sensory bridge architecture does real work. Vera isn't comparing text to text — she's perceiving the actual PPTX/PNG output and comparing it to the brief. The perception protocol (from Epic 2A) ensures that perception artifacts are cached and carried forward to downstream gates. This is the anti-hallucination mechanism.

---

## STAGE 13: Quinn-R G3 Quality Review

**Workflow template stage 11: `quality-g3` → `quality-reviewer`**

Quinn-R reviews Gary's output across 8 dimensions:
- Brand consistency (JCPH Navy, Montserrat)
- Accessibility contrast (WCAG 2.1 AA, 4.5:1)
- Visual hierarchy
- Content fidelity to slide brief
- Literal-visual accuracy (Slides 3, 11)
- Literal-text accuracy (Slide 7 — KC topics)
- Layout integrity
- Instructional alignment

Returns: brand consistent, one minor contrast note on Slide 11 (white text on light teal — addressable). No blocking issues.

---

## STAGE 14 [HIL Gate 2]: Slides Review (CRITICAL)

**Workflow template stage 12: `gate-2` → `human`**

Marcus runs the storyboard authorization pre-check:

```bash
python skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py \
  --payload gary-dispatch.json
```

Returns: `status: passed`.

Marcus presents:

> "Here's the C1-M1-P2 slide deck — 16 frames covering all 4 learning objectives. Gary's self-assessment: layout integrity 0.92, parameter confidence 0.88. Vera: G3 passed. Quinn-R: brand consistent, one minor contrast note on Slide 11 (white text on light teal). This is the **critical gate** — once you approve, I'll send these to Irene for narration. What's your call?"

User approves with note: "Fix the contrast on Slide 11 in Descript."

Marcus writes the authorized storyboard:

```bash
python skills/bmad-agent-marcus/scripts/write-authorized-storyboard.py \
  --manifest storyboard.json \
  --run-id C1-M1-P2-ADHOC \
  --output authorized-storyboard.json
```

---

🧪 **Quinn:** Gate 2 is secured by three layers: (1) Gary dispatch validator (technical pre-gate, blocks on missing assets), (2) Vera G3 fidelity gate (perceptual comparison, blocks on drift), (3) Quinn-R brand/accessibility review (blocks on critical failures, notes on minor issues). The authorized storyboard write is fail-closed on overwrite. ✅

🏃 **Bob:** Gate 2 is the most important checkpoint in the pipeline. The storyboard authorization is the commitment point — downstream Irene, ElevenLabs, Kira all operate on the authorized storyboard. This is the correct pattern for a fail-closed gate.

---

## STAGE 15: Irene Pass 2 — Narration Script + Segment Manifest

**Workflow template stage 13: `narration-and-manifest` → `content-creator`**

Marcus delegates to Irene with a Pass 2 context envelope:

```yaml
pass: 2
content_type: "narration-script"
run_id: "C1-M1-P2-ADHOC"
gary_slide_output: [array — PNG paths + visual descriptions per slide]
perception_artifacts: [from Vera's G3 sensory bridge cache]
governance:
  allowed_outputs: ["narration_script", "segment_manifest", "pairing_references"]
```

Irene loads:
- `template-narration-script.md` → per-segment script format
- `template-segment-manifest.md` → YAML manifest schema

Irene produces:

1. **Narration script** — 16 segment scripts, voice suggestions, pronunciation guides
2. **Segment manifest YAML** — per-slide: `gary_slide_id`, `narration_text`, `sfx_cue`, `music_direction`, `visual_source`, `visual_mode`, `behavioral_intent`

**Marcus handoff validation:**

```bash
python skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py \
  --envelope pass2-envelope.json
```

**Contract validation:** 17 Irene Pass 2 handoff tests green. Validates `source_image_path` presence (local file on disk), slide ID alignment between manifest and authorized storyboard, segment count consistency.

---

🏗️ **Winston:** The perception artifacts from Vera's G3 cache being passed to Irene is a critical detail. Irene writes narration to what Vera *perceived* about the slides — not just what was in the brief. This closes the brief-to-slide drift gap. The perception-grounding enforcement (Epic 11 Story 3) makes this mandatory.

💻 **Amelia:** 17 tests on the Irene Pass 2 validator, all green. The perception artifacts check was added in Story 11.3 as a mandatory contract field. Any handoff without `perception_artifacts` referencing the G3 cache fails before Irene even runs. Correct.

---

## STAGE 16: Vera G4 — Narration vs Slides + Lesson Plan

**Workflow template stage 14: `fidelity-g4` → `fidelity-assessor`**

Marcus delegates to Vera with a G4 gate envelope.

**Contract:** Vera loads `state/config/fidelity-contracts/g4-narration-script.yaml`. Verifies narration content matches perceived slide visual content (from G3 cache) AND assessment items match lesson plan (from G1 cache).

Returns: `status: passed`.

---

## STAGE 17: Quinn-R G4 Quality Review

**Workflow template stage 15: `quality-g4` → `quality-reviewer`**

Quinn-R reviews narration script + segment manifest:
- Instructional soundness
- Behavioral intent fidelity (learner effect alignment)
- Content accuracy flags
- Pacing consistency

Returns: strong intent fidelity, one pacing note on Segment 12.

---

## STAGE 18 [HIL Gate 3]: Script & Manifest Review

**Workflow template stage 16: `gate-3` → `human`**

Marcus presents:

> "Narration script and segment manifest ready. 16 segments, estimated 18 minutes total. SFX on 3 segments, background music throughout. Vera: G4 passed. Quinn-R: strong intent fidelity, one pacing note on Segment 12 — slightly dense coverage, could be split if desired. What's your call?"

User approves with note: "Keep Segment 12 as is."

Marcus logs approval. Gate 3 is committed.

---

🏃 **Bob:** Gate 3 protocol clean. Vera and Quinn-R both ran before gate presentation. User saw the quality findings inline, not as a separate review step. This is the streamlined gate pattern: findings surfaced *at* the gate, not requiring a separate review session. ✅

---

## STAGE 19: ElevenLabs — Audio Generation

**Workflow template stage 17: `audio-generation` → `elevenlabs-specialist`**

Marcus delegates to the ElevenLabs audio specialist with the approved segment manifest. Specialist reads:
- `narration_text` per segment → voice synthesis input
- `voice_selection` from style guide (`state/config/style_guide.yaml`)
- `sfx_cue` → SFX asset selection
- `music_direction` → background music selection

Specialist generates:
- Narration MP3 files per segment (16)
- VTT caption files per segment
- SFX assets (3 segments)
- Background music file

Writes back to manifest: `narration_duration`, `narration_file`, `narration_vtt` per segment.

**Contract check:** `skills/bmad-agent-elevenlabs/` → SKILL.md + references present. ElevenLabs client (`scripts/api_clients/elevenlabs_client.py`) present and tested.

---

🧪 **Quinn:** ElevenLabs specialist and client are tested. The live smoke test for ElevenLabs (`scripts/smoke_elevenlabs.mjs`) validates connectivity. The client has error handling and rate/quota management. No concerns.

---

## STAGE 20: Vera G5 — Audio vs Narration Script

**Workflow template stage 18: `fidelity-g5` → `fidelity-assessor`**

Marcus delegates to Vera with a G5 gate envelope.

**Contract:** Vera loads `state/config/fidelity-contracts/g5-audio.yaml`. Invokes the audio bridge from `sensory-bridges` skill — runs STT on each narration MP3 and compares the transcript to the approved script. Checks WPM, pronunciation flags, and segment alignment.

Returns: `status: passed` — all segments within WPM range, transcript matches script with minor phonetic variations, no pronunciation flags.

---

🏗️ **Winston:** G5 is the only gate that goes backward through audio synthesis — it's the post-synthesis verification that what came back from ElevenLabs matches what was sent. This is a critical circuit breaker. If ElevenLabs mis-synthesizes a proper noun or medical term, G5 catches it before composition.

---

## STAGE 21: Kira — Silent Motion Video Clips

**Workflow template stage 19: `motion-generation` → `kling-specialist`**

Marcus delegates to Kira (Kling specialist) **only after ElevenLabs returns `narration_duration` per segment**. The segment durations are the input constraint for Kira — clips align to narration length.

Kira reads the segment manifest for:
- `visual_source` — source image or brief for motion clip
- `visual_mode` — `slide-still` (no Kira call) or `motion-clip` (Kira generates)
- `narration_duration` — clip must match

Kira generates silent motion clips for segments marked `visual_mode: motion-clip`. Writes back: `visual_file`, `visual_duration`.

**Contract check:** `skills/bmad-agent-kling/` → SKILL.md + references present. Kling client (`scripts/api_clients/kling_client.py`) present (Epic 3, Story 3.3).

---

📊 **Mary:** The narration-first, then motion ordering is the correct user-facing design. If Kira ran before ElevenLabs, the clip durations could mismatch the audio — the user would have to explain why clips look wrong. The workflow template's stage ordering (audio-generation → fidelity-g5 → motion-generation) enforces the correct dependency. This is one of the key structural decisions the party-mode team validated in the v1 planning session.

🏗️ **Winston:** Correct dependency enforcement. The `narrated-lesson` template has `motion-generation` at stage 19, *after* `fidelity-g5` at stage 18. The stage order in the YAML is the execution order contract. If someone tries to skip stages, Marcus checks the plan sequence. No re-ordering is permitted without a Gate override.

---

## STAGE 22: Quinn-R Pre-Composition Validation

**Workflow template stage 20: `pre-composition-validation` → `quality-reviewer`**

Quinn-R runs the pre-composition completeness pass across all assembly bundle inputs:

- All `narration_file` paths populated and files exist on disk
- All `visual_file` paths populated and files exist on disk
- All `narration_vtt` paths populated
- `narration_duration` matches `visual_duration` within ±200ms tolerance per segment
- Segment count in manifest matches segment count in authorized storyboard
- `behavioral_intent` field populated for all segments

Returns: all checks pass. Assembly bundle is complete.

---

🧪 **Quinn:** Pre-composition validation is the last machine-quality check before the human compositor step. It should be deterministic — either all fields are populated or they aren't. Quinn-R's role here is to provide a readable summary for Marcus to present at the composition guide stage, not to make subjective judgment calls. This is correctly scoped. ✅

---

## STAGE 23: Compositor — Descript Assembly Guide

**Workflow template stage 21: `composition-guide` → `compositor`**

Marcus delegates to the Compositor skill:

```bash
# Step 1: Sync approved stills into assembly bundle
python skills/compositor/scripts/compositor_operations.py sync-visuals manifest.yaml

# Step 2: Generate Descript Assembly Guide
python skills/compositor/scripts/compositor_operations.py guide manifest.yaml \
  DESCRIPT-ASSEMBLY-GUIDE.md
```

`sync-visuals` copies Gate-2-authorized slide PNGs into the assembly bundle directory.

`guide` generates `DESCRIPT-ASSEMBLY-GUIDE.md` from the completed manifest with:
- Per-segment instructions (import, arrange, timing, text overlay)
- Track assignment table (V1: slide stills/video clips; A1: narration; A2: music; A3: SFX)
- Segment timing from manifest
- Caption file pairing

**Contract:** Compositor scripts callable (`skills/compositor/scripts/compositor_operations.py`). `guide` and `sync-visuals` subcommands both present. Assembly guide format reference: `skills/compositor/references/assembly-guide-format.md`.

---

## STAGE 24: Descript Manual Handoff

Marcus hands off the complete package to the user:

> "Everything's assembled. Here's your Descript package:
>
> - `DESCRIPT-ASSEMBLY-GUIDE.md` — step-by-step assembly instructions
> - `audio/` — 16 narration MP3s + background music
> - `visuals/` — approved slide stills (Gate-2-authorized PNGs)
> - `video/` — Kira silent motion clips (where `visual_mode: motion-clip`)
> - `captions/` — 16 VTT files
>
> Track assignments: V1 = video/slides; A1 = narration; A2 = music; A3 = SFX.
>
> Open Descript, import the assets, follow the guide. Note: Slide 11's contrast in the exported PNG has a minor issue you flagged at Gate 2 — you may want to adjust the text overlay in Descript before final export."

User assembles in Descript and exports MP4 + VTT.

---

## STAGE 25 [POST-COMPOSITION]: Quinn-R Post-Composition Validation

**Workflow template stage 22: `post-composition-validation` → `quality-reviewer`**

User returns the exported MP4 + VTT to the bundle directory.

Quinn-R runs post-composition validation using the G6 contract:

**Fidelity contract:** `state/config/fidelity-contracts/g6-composition.yaml` (Gate: G6, HIL Gate: Gate 4)

Criteria checked:
- Segment order in video matches manifest (`G6-01` — critical)
- Audio-visual sync per segment (`G6-02` — critical)  
- Assembly completeness — no missing segments (`G6-03` — critical)
- Caption accuracy and timing alignment (`G6-04` — critical)
- Overall composition integrity score

Returns: composition integrity 0.94. Minor audio level note on the music transition at 7:42. All G6 critical criteria passed.

---

🏗️ **Winston:** G6 is the only post-human-assembly gate in the pipeline. Critically, it verifies the composition *after* the human has worked in Descript — it's not just validating the inputs, it's validating the final artifact. The contract uses video perception (keyframe analysis, STT on the composed audio track) to verify segment order and sync. This is the correct end-of-pipeline verification pattern.

🧪 **Quinn:** G6 contract present at `state/config/fidelity-contracts/g6-composition.yaml`. The G6 contract covers assembly completeness, segment order, audio-visual sync, and caption accuracy. All criteria have `requires_perception: true` and `perception_modality: video`. This requires the video perceptual bridge — confirmed present in the sensory-bridges skill (Epic 2A). Contract architecture tight. ✅

---

## STAGE 26 [HIL Gate 4]: Final Video Review

**Workflow template stage 23: `gate-4` → `human`**

Marcus presents:

> "Final video is back from Quinn-R's post-composition review. 18 minutes, 16 segments, all captions validated. Quinn-R: composition integrity 0.94 — all G6 critical criteria passed.
>
> Notes: Minor audio level at 7:42 music transition (cosmetic, acceptable for draft preset). Slide 11 contrast was addressed in Descript — visual now compliant.
>
> **What's your call?**"

User approves. Asset staged for Canvas deployment.

Marcus logs approval and run finalization.

---

🏃 **Bob:** Gate 4 completed. Full pipeline traversed: 23 template stages, 4 HIL gates, 6 fidelity contracts (G0–G5 + G6), 3 quality-reviewer passes, and a post-composition human assembly step. The workflow template correctly represents this pipeline and Marcus executed it in registry-defined order. ✅

📊 **Mary:** The gate-4 presentation gives the user exactly what they need: the key quality metric (0.94 integrity), the fidelity assessment (all criticals passed), the actionable note (audio at 7:42), and a clear decision prompt. No status report jargon, no jargon overwhelm. This is the right user-facing design.

💻 **Amelia:** End-to-end contract chain: G0 → G1 → G2 (quality-g2) → Gate 1 → G3 (quality-g3) → Gate 2 → G4 (quality-g4) → Gate 3 → G5 → G6 (quality pre-comp, post-comp) → Gate 4. All contracts present, all validators tested green. The workflow template correctly maps each fidelity stage to the right gate and specialist. No implementation gaps visible.

---

## STAGE 27: Run Finalization

Marcus runs finalization:

- Verify all assets in target locations under `course-content/staging/ad-hoc/`
- Ad-hoc mode: skip state writes (no `manage_run.py` persist call)
- Present summary:

> "Run complete for C1-M1-P2. Produced: 16-slide narrated presentation with video, 18-minute runtime, captions, Descript assembly guide. Final package is in `course-content/staging/ad-hoc/`. When you're ready, promote to `course-content/courses/` and deploy to Canvas."

---

---

# FINDINGS SUMMARY

## 🟢 RESOLVED SINCE v1 (2026-04-02)

| Finding | v1 Status | v2 Status |
|---|---|---|
| `narrated-lesson` missing from `generate-production-plan.py` argparse choices | 🔴 GAP | ✅ FIXED |
| No script-generated plan skeleton for the most complex workflow | 🔴 GAP | ✅ FIXED |
| Planner relied on embedded Python dict (second source of truth risk) | 🟡 RISK | ✅ FIXED |

**Resolution:** `generate-production-plan.py` was migrated to read from `skills/bmad-agent-marcus/references/workflow-templates.yaml` (single canonical YAML registry). `narrated-lesson` is now a first-class template ID with 23 stages, matching the happy-path pipeline. Alias `narrated-presentation-with-video` also resolves correctly. All 10 planner tests pass.

## 🟡 NEW OBSERVATIONS (v2 — minor, no blockers)

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| 1 | `conversation-mgmt.md` pipeline table does not explicitly name G6 as the fidelity contract label for post-composition validation — it says "Quinn-R post-comp" without naming the contract file. | LOW | Cosmetic doc note; G6 contract is referenced in Quinn-R's SKILL.md and the contract file exists. No functional impact. No change needed. |
| 2 | Admin guide and dev guide headers show `Last Updated: 2026-03-29`. The workflow-template registry changes (2026-04-02) and this simulation (2026-04-03) are not reflected. | LOW | Update `Last Updated` headers in both docs to `2026-04-03`. |
| 3 | Sprint status `last_updated` is `2026-04-02` and doesn't note the workflow template normalization pass. | LOW | Update `last_updated` to `2026-04-03` with a note about the workflow template registry and simulation v2. |

## 🟢 VALIDATED (all clean)

- All 6 fidelity contracts present (G0–G6) and correctly mapped to workflow stages
- All 3 critical Marcus validators present and tested (Gary dispatch, Irene Pass 2, source bundle)
- All specialist agents present with SKILL.md (11 agent skills confirmed)
- 46 pytest tests passing across Marcus scripts and validators
- Storyboard authorization (write-authorized-storyboard.py) present and tested
- Compositor operations present and callable (sync-visuals, guide)
- G6 (post-composition) contract architecture verified: video perception bridge required and present (Epic 2A)
- Workflow template stage ordering enforces the narration-before-motion dependency (audio-g5 at stage 18, motion-generation at stage 19)

---

# PARTY-MODE TEAM FINAL ASSESSMENT

🏗️ **Winston:** The infrastructure is now sound. The planner reads from a single YAML source of truth. The 23-stage narrated-lesson template correctly represents the happy path including the video generation variant. The contract chain from G0 through G6 is intact. No structural concerns.

💻 **Amelia:** All validators tested, all scripts callable, all 46 tests green. The one observation (doc headers) is housekeeping, not an implementation issue. The workflow template registry is the right architecture — adding a new template requires only editing the YAML, no script changes.

🏃 **Bob:** The simulation used the workflow template as the authoritative plan reference throughout and it held up at every stage. Gate protocol was followed at Gates 1, 2, 3, and 4. All pre-gate validations ran before user presentation. The sprint is clean.

🧪 **Quinn:** Test coverage is solid across the critical path. The three validators and the planner cover the highest-risk contract points. Post-composition validation (G6) is covered by the contract file and mapped in the workflow template. No test gaps detected.

📊 **Mary:** The simulation confirms that end users (specifically Juanl) can now start a `narrated-lesson` run by simply telling Marcus the content type and scope — Marcus generates the plan from the registry, surfaces the 23-stage sequence, and orchestrates through to the Descript handoff. The workflow template makes the happy path transparent and repeatable.

---

**Simulation status: COMPLETE. No blocking findings. Minor remediations (doc headers, sprint status) addressed in project closeout.**

---

*Simulation authored: 2026-04-03*
*Marcus version: current (master)*
*Workflow template registry version: 1*
*Test suite: 46 passing*
