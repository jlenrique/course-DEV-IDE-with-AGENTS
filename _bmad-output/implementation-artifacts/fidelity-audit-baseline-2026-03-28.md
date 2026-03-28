# APP Fidelity Maturity Audit — Baseline Report

**Date:** 2026-03-28
**Auditor:** Dev agent (Story 2A-1)
**Scope:** All 7 production gates (G0–G6), evaluated against 4 pillars
**Reference:** GOLD document `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md`

---

## Maturity Scoring Key

| Score | Definition |
|-------|-----------|
| **ABSENT** | No capability exists for this pillar at this gate |
| **WEAK** | Partial/informal capability exists but is not testable or reliable |
| **PARTIAL** | Capability exists but has significant gaps |
| **GOOD** | Capability exists and covers most requirements |
| **STRONG** | Capability is complete, testable, and operationalized |

---

## Audit Matrix

| Gate | Artifact | L1 Contracts | L2 Evaluation | L3 Memory | Perception |
|------|----------|:---:|:---:|:---:|:---:|
| **G0** | Source Bundle | ABSENT | ABSENT | ABSENT | WEAK |
| **G1** | Lesson Plan | WEAK | ABSENT | WEAK | OK (text) |
| **G2** | Slide Brief | WEAK | ABSENT | WEAK | OK (text) |
| **G3** | Generated Slides | PARTIAL | SELF-GRADED | PARTIAL | PARTIAL |
| **G4** | Narration Script | WEAK | ABSENT | WEAK | GAP |
| **G5** | Audio | ABSENT | ABSENT | ABSENT | BLIND |
| **G6** | Composition | ABSENT | ABSENT | ABSENT | BLIND |

**Overall Maturity: LEVEL 0 — No independent fidelity assurance exists at any gate.**

---

## Gate-by-Gate Evidence

### G0 — Source Bundle (`extracted.md` from SME materials)

**Producing agent:** Source Wrangler skill (`skills/source-wrangler/`)

| Pillar | Score | Evidence |
|--------|-------|----------|
| **L1 Contracts** | ABSENT | `skills/source-wrangler/references/bundle-format.md` defines output structure (`extracted.md` + `metadata.json` with `provenance[]`), but no testable fidelity criteria exist. No contract specifying "all source sections must be captured" or "no content may be invented." |
| **L2 Evaluation** | ABSENT | No agent evaluates extraction completeness. The source bundle is trusted as-is by all downstream consumers. |
| **L3 Memory** | ABSENT | Source wrangler has no memory sidecar. No fidelity outcomes are captured. |
| **Perception** | WEAK | Text extraction works for Notion pages, HTML, and machine-readable PDFs. **Scanned/OCR PDFs are explicitly out of scope** (`source-wrangler/SKILL.md`). PDF sensory bridge does not exist yet. System can silently start from an incomplete source. |

**Self-grading:** None. No quality or fidelity self-assessment.

---

### G1 — Lesson Plan (LOs + content structure)

**Producing agent:** Irene (`skills/bmad-agent-content-creator/`)

| Pillar | Score | Evidence |
|--------|-------|----------|
| **L1 Contracts** | WEAK | `template-lesson-plan.md` defines required fields (`Objective Served`, `Bloom's Level`, `Content Type`, `Writer Delegation`, `Behavioral / Affective Goal`, assessment hooks table). These are structural requirements, not fidelity criteria. No contract says "every source theme must be covered by an LO." No `source_ref` fields exist — LOs have no traceable link to the source bundle. |
| **L2 Evaluation** | ABSENT | No agent evaluates whether the lesson plan faithfully represents the source material. The user reviews at HIL Gate 1, but this is quality + domain review, not systematic fidelity checking. |
| **L3 Memory** | WEAK | `_bmad/memory/content-creator-sidecar/patterns.md` exists but contains only placeholders — no fidelity patterns captured. User corrections to LOs are not logged. |
| **Perception** | OK | Input is text (`extracted.md`), which Irene can fully interpret. No multimodal perception needed at this gate. |

**Self-grading:** None. Irene does not self-assess fidelity of her lesson plan against the source bundle.

---

### G2 — Slide Brief (per-slide specs + fidelity tags)

**Producing agent:** Irene (`skills/bmad-agent-content-creator/`)

| Pillar | Score | Evidence |
|--------|-------|----------|
| **L1 Contracts** | WEAK | `template-slide-brief.md` defines per-slide fields (`Content`, `Visual Guidance`, `Learning Purpose`, `Behavioral / Affective Intent`, downstream Gary parameters). Fidelity classification fields (`fidelity`, `fidelity_rationale`) are proposed in Story 3.11 but **not yet in the live template**. No `source_ref` fields. No contract verifying slide brief covers all lesson plan content. |
| **L2 Evaluation** | ABSENT | No agent checks slide brief against lesson plan for completeness or accuracy. |
| **L3 Memory** | WEAK | Same content-creator sidecar — no fidelity-specific patterns captured. |
| **Perception** | OK | Input is text (lesson plan). No multimodal perception needed. |

**Self-grading:** None. Irene does not verify her slide brief covers all LOs from the lesson plan.

---

### G3 — Generated Slides (Gamma PNGs + metadata)

**Producing agent:** Gary (`skills/bmad-agent-gamma/`)

| Pillar | Score | Evidence |
|--------|-------|----------|
| **L1 Contracts** | PARTIAL | `context-envelope-schema.md` defines inbound/outbound contract with `quality_assessment` return fields including `content_fidelity` (0.0–1.0), `embellishment_detected`, `embellishment_details`. `quality-assessment.md` defines self-assessment dimensions: `content_fidelity`, `layout_integrity`, `brand_compliance`, `accessibility`, `pedagogical_alignment`, `intent_fidelity`. These are assessment dimensions, but there are no external testable fidelity contracts — the criteria are embedded in Gary's judgment, not in versioned YAML. |
| **L2 Evaluation** | SELF-GRADED | Gary's `quality-assessment.md` provides structured self-scoring (0.0–1.0 per dimension) returned in the context envelope. **This is self-grading — Gary evaluates his own output.** No independent verification. Quinn-R reviews at HIL Gate 2 but checks quality dimensions (brand, accessibility), not source-material fidelity. |
| **L3 Memory** | PARTIAL | `_bmad/memory/gamma-specialist-sidecar/patterns.md` captures tool-parameter patterns: `textMode: preserve` effectiveness, embellishment observations, file-size proxy signals. These are tool-tuning learnings, not fidelity outcome tracking. No record of "this slide drifted from source" or "user corrected fidelity at Gate 2." |
| **Perception** | PARTIAL | Gary downloads PNGs and can invoke LLM vision (Claude) to interpret them. **However, Gary is not required to confirm his visual interpretation before returning results.** No perception protocol exists. No confirmation step. Gary could misread his own output and score it PASS. |

**Self-grading:** Yes — structured YAML return with `content_fidelity`, `intent_fidelity`, `embellishment_detected`. This is the only gate with any fidelity-adjacent assessment, but it is self-graded.

---

### G4 — Narration Script (script + segment manifest)

**Producing agent:** Irene (Pass 2) (`skills/bmad-agent-content-creator/`)

| Pillar | Score | Evidence |
|--------|-------|----------|
| **L1 Contracts** | WEAK | `template-narration-script.md` defines per-segment structure with `[Gary Slide: {gary_slide_id} — {visual_description}]` linkage. `Behavioral Intent` field per segment. No `source_ref` fields. No contract requiring narration to match actual slide content (it references `visual_description` free-text from Gary, not the actual PNG). `template-segment-manifest.md` defines `behavioral_intent`, `narration_ref`, `visual_cue`, `visual_mode`, `visual_source` — but no `source_ref` tracing back to lesson plan or source bundle. |
| **L2 Evaluation** | ABSENT | No agent checks whether narration accurately describes actual slides. Quinn-R does a pre-composition check on the segment manifest but focuses on timing, coverage, and behavioral_intent support — not source-material fidelity. |
| **L3 Memory** | WEAK | Content-creator sidecar — no fidelity-specific patterns. |
| **Perception** | **GAP** | Irene writes narration referencing `visual_description` free-text from Gary's `gary_slide_output[]` — **she does not look at the actual PNGs.** The `visual_description` is Gary's editorial summary, not a normalized perception artifact. Irene is writing for slides she has not visually confirmed. This is the highest-risk perception gap in the pipeline. |

**Self-grading:** None. Irene does not verify her narration matches actual slide content.

---

### G5 — Audio (ElevenLabs MP3/WAV)

**Producing agent:** ElevenLabs Voice Director (`skills/elevenlabs-audio/`)

| Pillar | Score | Evidence |
|--------|-------|----------|
| **L1 Contracts** | ABSENT | No fidelity contract exists. `elevenlabs-audio/SKILL.md` defines operations (narration generation, timestamp extraction, VTT generation, manifest write-back) but no criteria for "spoken words match script" or "WPM within range." |
| **L2 Evaluation** | ABSENT | No agent verifies audio fidelity. No STT transcription exists to compare spoken output against the narration script. |
| **L3 Memory** | ABSENT | ElevenLabs sidecar (`_bmad/memory/elevenlabs-specialist-sidecar/`) exists but captures voice/parameter patterns, not fidelity outcomes. |
| **Perception** | **BLIND** | No agent can hear audio output. No STT integration exists. No audio sensory bridge. The system produces MP3/WAV files that no agent can interpret. |

**Self-grading:** None.

---

### G6 — Composition (Descript export)

**Producing agent:** Compositor skill + human in Descript (`skills/compositor/`)

| Pillar | Score | Evidence |
|--------|-------|----------|
| **L1 Contracts** | ABSENT | No fidelity contract exists. `compositor/SKILL.md` generates a Descript Assembly Guide from the segment manifest, but there are no criteria for verifying the final composed video matches the guide. Composition is a manual-tool pattern — the human assembles in Descript. |
| **L2 Evaluation** | ABSENT | Quinn-R runs a post-composition pass (referenced in `review-protocol.md`), but this checks quality dimensions, not fidelity against the assembly guide or manifest. |
| **L3 Memory** | ABSENT | No fidelity outcomes captured for composition. |
| **Perception** | **BLIND** | No video sensory bridge exists. No agent can watch the composed video. Frame extraction + STT would be needed. |

**Self-grading:** None.

---

## Independent Verification Gaps

Every point where an agent self-grades without independent verification:

| Gate | Agent | What It Self-Grades | Evidence |
|------|-------|--------------------|---------| 
| G3 | Gary | `content_fidelity`, `intent_fidelity`, `embellishment_detected` — 6 dimensions scored 0.0–1.0 | `quality-assessment.md`, context envelope outbound schema |

All other gates: **no self-grading and no independent grading** — artifacts are passed downstream on trust.

---

## Unconfirmed Perception Points

Every point where an agent consumes a multimodal artifact without confirming interpretation:

| Gate | Agent | Artifact | What Happens | Risk |
|------|-------|----------|-------------|------|
| G3 | Gary | Generated PNGs | Gary downloads PNGs, may visually inspect via LLM vision, but is **not required** to confirm interpretation | Could misread his own output and return incorrect quality scores |
| G4 | Irene | Generated PNGs (via `visual_description`) | Irene receives Gary's free-text `visual_description` summary, **not the actual PNGs**. Writes narration for slides she hasn't seen. | Narration may describe content not actually on the slide |
| G5 | Any | Audio MP3/WAV | **No agent can hear audio.** No STT exists. | Spoken content assumed to match script — cannot verify |
| G6 | Any | Composed video MP4 | **No agent can watch video.** No frame extraction or STT. | Final composition assumed correct — cannot verify |

---

## Leaky Neck Report

Points where agentic judgment enforces constraints that should be deterministic:

### Leak 1: Gamma `additionalInstructions` for text fidelity (CRITICAL)

- **Location:** `skills/bmad-agent-gamma/SKILL.md` principle #4; `template-slide-brief.md` downstream section (`additionalInstructions` field); `context-envelope-schema.md` `parameter_overrides.additionalInstructions`
- **Constraint:** "Preserve this text exactly" / "Do not add content beyond what is given"
- **Mechanism:** Natural-language instruction in `additionalInstructions` passed to Gamma API — relies on Gamma's LLM compliance
- **Failure mode:** Gamma's `generate` mode structurally rewrites content regardless of instructions. This caused the Trial Run 2 Slide 10 failure.
- **Deterministic alternative:** Map fidelity classification directly to `textMode` parameter: `literal-text` → `textMode: preserve`; `literal-visual` → `textMode: preserve` + `imageOptions.source: noImages`. Story 3.11 partially addresses this but the free-text channel remains available.
- **Proposed remediation (Story 2A-8):** Replace free-text constraint channels for literal slides with a finite fidelity-control vocabulary (`text_treatment`, `image_treatment`, `layout_constraint`, `content_scope`). Prohibit `additionalInstructions` for `literal-text` and `literal-visual` slides.

### Leak 2: Slide brief `textMode` / `imageOptions` as advisory (MEDIUM)

- **Location:** `template-slide-brief.md` downstream section — `textMode` and `imageOptions.source` are specified per slide but are **advisory guidance** for Gary, not deterministic parameter bindings
- **Constraint:** "Use `textMode: preserve` for this slide"
- **Mechanism:** Gary reads the slide brief recommendation and makes a judgment call about parameters
- **Failure mode:** Gary could override the slide brief's `textMode` recommendation based on his own assessment
- **Deterministic alternative:** When fidelity is `literal-text` or `literal-visual`, the `textMode` and `imageOptions` values should be mandatory bindings that Gary passes directly to the API — not recommendations he may override
- **Proposed remediation (Story 2A-8):** Fidelity-control vocabulary fields are mandatory for literal slides; Gary may not override them

### Leak 3: Narration visual accuracy via free-text description (MEDIUM)

- **Location:** `template-narration-script.md` per-segment `[Gary Slide: {gary_slide_id} — {visual_description}]`
- **Constraint:** "Narration should describe what's on the slide"
- **Mechanism:** Irene reads Gary's free-text `visual_description` and writes narration based on it — relies on `visual_description` being accurate
- **Failure mode:** If `visual_description` is inaccurate (Gary summarized wrong, or the actual PNG differs from what Gary intended), Irene writes narration for content that doesn't match the slide
- **Deterministic alternative:** Replace `visual_description` free-text with normalized sensory bridge perception artifact from `png_to_agent.py`. Irene references the structured perception output, not Gary's editorial summary.
- **Proposed remediation (Story 2A-6):** Gary→Irene handoff supplemented with `perception_artifacts[]` from sensory bridge

---

## Cross-Reference Summary

| Artifact | File | Fidelity-Relevant Fields | `source_ref` Present? | Fidelity Classification Present? |
|----------|------|-------------------------|:---:|:---:|
| Lesson plan template | `skills/bmad-agent-content-creator/references/template-lesson-plan.md` | LO + Bloom's, content blocks, assessment hooks, `behavioral_intent` | NO | NO |
| Slide brief template | `skills/bmad-agent-content-creator/references/template-slide-brief.md` | Content, Visual Guidance, Learning Purpose, downstream Gary params | NO | NO (proposed in 3.11) |
| Context envelope | `skills/bmad-agent-gamma/references/context-envelope-schema.md` | `quality_assessment` with `content_fidelity`, `intent_fidelity`, `embellishment_detected` | NO | NO |
| Narration script template | `skills/bmad-agent-content-creator/references/template-narration-script.md` | Slide linkage via `visual_description`, `behavioral_intent` | NO | NO |
| Segment manifest template | `skills/bmad-agent-content-creator/references/template-segment-manifest.md` | `behavioral_intent`, `narration_ref`, write-back fields for ElevenLabs/Kira | NO | NO |
| Quality assessment | `skills/bmad-agent-gamma/references/quality-assessment.md` | 6 self-assessment dimensions (0.0–1.0) | NO | NO |
| Review protocol | `skills/bmad-agent-quality-reviewer/references/review-protocol.md` | 8 dimensions: brand, accessibility, LA, instructional, intent fidelity, content accuracy, audio, composition | NO | NO |
| Source bundle format | `skills/source-wrangler/references/bundle-format.md` | `provenance[]` with `kind`, `ref`, `fetched_at` | N/A (source) | NO |

**Key finding:** `source_ref` is absent from EVERY artifact schema. `fidelity` classification is absent from EVERY live template (proposed only in Story 3.11, not yet implemented).

---

*This audit establishes the Level 0 baseline. Stories 2A-2 through 2A-9 systematically close these gaps.*
