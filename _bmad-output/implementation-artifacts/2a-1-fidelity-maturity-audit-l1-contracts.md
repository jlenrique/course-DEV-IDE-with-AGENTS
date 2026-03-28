# Story 2A-1: APP Fidelity Maturity Audit & L1 Contract Definitions

Status: review

## Story

As an APP architect,
I want a formalized fidelity maturity audit of the current pipeline with explicit L1 fidelity contracts defined for all production gates,
So that we have a measured baseline, testable acceptance criteria for fidelity at every gate, and architectural reference documents that govern all subsequent fidelity work.

## Background & Motivation

The Party Mode consultation (2026-03-28) and parallel Gemini analysis established that the APP is at **Level 0 for fidelity assurance**: zero independent fidelity evaluation at any gate, perception unconfirmed or blind for audio/video, no provenance traceability, and cumulative drift undetected. This story produces the foundational artifacts — L1 contracts, architectural references, and a baseline audit — that every subsequent story in Epic 2A builds upon.

**GOLD document:** `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md`

## Acceptance Criteria

### Audit Report

1. A formal audit report is produced at `_bmad-output/implementation-artifacts/fidelity-audit-baseline-2026-03-28.md` covering all 7 gates (G0–G6)
2. Each gate is evaluated against four pillars: L1 Contracts, L2 Evaluation, L3 Memory, Perception
3. Each pillar receives a maturity score: ABSENT / WEAK / PARTIAL / GOOD / STRONG — with evidence (specific file paths and field references, not just descriptions)
4. The audit identifies every point where an agent self-grades its own output without independent verification
5. The audit identifies every point where an agent consumes a multimodal artifact without confirming its interpretation
6. The audit cross-references existing artifacts: lesson plan template fields, slide brief template fields, context envelope schema fields, review protocol dimensions, checkpoint coordination gates, source bundle format, and segment manifest fields

### Leaky Neck Report

7. A Leaky Neck report section identifies all points where agentic judgment currently enforces constraints that could be deterministic (schema validation, parameter binding, or code check)
8. Each leak includes: location (agent + reference file + specific instruction), what constraint is being enforced agentically, and a proposed deterministic alternative
9. Known leak from Story 3.11 pre-analysis is included: Gamma `additionalInstructions` for text preservation → should be `textMode: preserve` parameter binding
9a. The Leaky Neck report specifically flags the **free-text fidelity-control channels** still exposed in the slide brief (`additionalInstructions` field at `template-slide-brief.md`) and context envelope (`parameter_overrides.additionalInstructions` at `context-envelope-schema.md`). These invite natural-language constraint enforcement that should be replaced with a finite, deterministic fidelity-control vocabulary. Remediation is deferred to Story 2A-8, but the leak must be documented here.

### L1 Fidelity Contracts

10. A directory `state/config/fidelity-contracts/` is created containing one YAML file per gate: `g0-source-bundle.yaml`, `g1-lesson-plan.yaml`, `g2-slide-brief.yaml`, `g3-generated-slides.yaml`, `g4-narration-script.yaml`, `g5-audio.yaml`, `g6-composition.yaml`
11. Each contract YAML file follows a standard schema:
    ```yaml
    gate: G{n}
    gate_name: "{human-readable name}"
    producing_agent: "{agent name}"
    source_of_truth:
      primary: "{description of upstream artifact}"
      schema_ref: "{path to template or schema file}"
    criteria:
      - id: "G{n}-{nn}"
        name: "{short name}"
        description: "{what this criterion checks}"
        fidelity_class: [creative, literal-text, literal-visual]  # which classes this applies to
        severity: critical | high | medium
        evaluation_type: deterministic | agentic
        check: "{human-readable assertion}"
    ```
12. **G0 (Source Bundle)** contract includes criteria for:
    - Section coverage: all major sections/headings from SME source material appear in `extracted.md`
    - Media capture: referenced images/diagrams noted in metadata even if not extracted (PDF limitation)
    - Metadata completeness: `metadata.json` has valid `provenance[]` entries with `kind`, `ref`, `fetched_at`
    - No content invention: `extracted.md` contains only content traceable to source materials
    - Degraded source detection: if source materials include scanned/OCR PDFs (not machine-readable text), the contract flags a `degraded_source` warning with affected page ranges. The source wrangler currently leaves scanned PDFs out of scope (`source-wrangler/SKILL.md`), so G0 fidelity for scanned inputs is inherently limited. The contract must acknowledge this boundary rather than silently passing incomplete extractions.
13. **G1 (Lesson Plan)** contract includes criteria for:
    - Source theme coverage: every major theme in the source bundle is represented by at least one learning objective
    - LO structure: each LO has `Bloom's Level` tag and traces to a content block
    - Content block completeness: each block has `Objective Served`, `Content Type`, `Writer Delegation`, `Behavioral / Affective Goal`
    - Assessment alignment: assessment hooks table covers all LOs
    - No orphaned content: every content block traces to an LO
14. **G2 (Slide Brief)** contract includes criteria for:
    - LO traceability: every slide's `Learning Purpose` traces to a lesson plan LO
    - Content item completeness: each slide has `Content`, `Visual Guidance`, `Learning Purpose`
    - Fidelity classification accuracy: `literal-text` tagged only when source material contains exact-match requirements (assessment items, statistics, accreditation terms); `literal-visual` tagged only when SME-provided image exists; `creative` is the default — over-tagging literal is a contract violation
    - Slide count consistency: number of slides matches lesson plan content block granularity (not 1:1, but pedagogically justified)
    - Downstream parameter coherence: `textMode`, `imageOptions.source` values are consistent with fidelity classification
15. **G3 (Generated Slides)** contract includes criteria for:
    - Slide count match: number of generated slides equals number specified in slide brief
    - Literal text preservation: for `literal-text` slides, all `content_items` from slide brief appear verbatim in the generated slide (verified via image sensory bridge)
    - Literal visual placement: for `literal-visual` slides, the specified image is present and text is preserved (verified via image sensory bridge)
    - Creative content coverage: for `creative` slides, all `content_items` themes are semantically represented (verified via image sensory bridge)
    - No harmful invention: generated slides do not contain clinical claims, statistics, or assessment items not present in the slide brief
    - Provenance manifest: every generated card has a provenance entry mapping it to its source call and fidelity class
16. **G4 (Narration Script)** contract includes criteria for:
    - Slide correspondence: each narration segment references an existing slide by number
    - Visual accuracy: narration describes content actually visible on the referenced slide (requires image perception)
    - Assessment reference exactness: any assessment items mentioned in narration match the lesson plan's assessment hooks verbatim
    - Terminology consistency: medical/clinical terms in narration match those used on slides and in the lesson plan
    - No narration invention: narration does not introduce clinical claims or data not present in the lesson plan or slides
    - Segment manifest alignment: narration segments map 1:1 to segment manifest entries
17. **G5 (Audio)** contract includes criteria for:
    - Script accuracy: spoken words match narration script text (verified via audio sensory bridge / STT)
    - WPM compliance: speaking rate within target range (130–170 WPM for instructional narration)
    - Pronunciation accuracy: medical terms match pronunciation guide in narration script
    - No audio invention: no spoken words that are not in the narration script (hallucinated audio)
    - Duration alignment: audio duration within ±10% of estimated duration from narration script
18. **G6 (Composition)** contract includes criteria for:
    - Segment order: segments assembled in the order specified by the segment manifest
    - Audio-visual sync: each audio segment is paired with its correct visual (slide PNG or video clip)
    - Assembly completeness: all segments in the manifest are present in the composition
    - No segment omission: no manifest segment is missing from the final assembly
    - Timing compliance: segment durations match manifest specifications within tolerance

### Architectural Reference Documents

19. `docs/app-design-principles.md` is created documenting:
    - The Three-Layer Intelligence Model (L1 contracts, L2 agentic evaluation, L3 learning memory) with examples
    - The Hourglass Model (wide cognitive → narrow deterministic neck → wide cognitive) with ASCII diagram
    - The Leaky Neck diagnostic with the repeatable test question
    - The Sensory Horizon principle and the requirement for a canonical perception request/response schema (schema itself is delivered in Story 2A-2)
    - Confidence calibration: the requirement for a modality-specific rubric defining what HIGH, MEDIUM, and LOW confidence mean operationally (rubric itself is delivered in Story 2A-2; this doc establishes the requirement and rationale)
    - How the two models interact (Hourglass governs flow topology, Three-Layer governs assessment architecture)
20. `docs/fidelity-gate-map.md` is created documenting:
    - The seven fidelity gates (G0–G6) with producing agent, source of truth, and artifact type at each gate
    - The relationship between fidelity gates (G0–G6) and HIL gates (Gate 1–4): fidelity gates are automated pre-checks; HIL gates are human checkpoints
    - The Fidelity Assessor → Quinn-R → Human ordering at each gate
    - **Role matrix:** For each gate, a table specifying exactly which agent owns which assessment dimension. Resolves boundary overlaps between Fidelity Assessor (source traceability), Quinn-R (quality standards, intent fidelity, audio quality, composition integrity), and producing agents (self-assessment). No dimension may be claimed by more than one agent; the matrix eliminates duplicated judgments and inconsistent blockers.
    - The Fidelity Trace Report format (Omissions / Inventions / Alterations)
    - **Fidelity Trace Report operating policy:** A decision table specifying, for each severity level (critical/high/medium), the response action (circuit-break, retry, escalate, waiver), maximum retry count, remediation owner (producing agent, Marcus, or human), escalation path, and waiver authority. This policy governs what happens after a fidelity finding — not just its format.
    - **Validator integration model:** How sensory bridge outputs feed into both the Fidelity Assessor's traceability checks AND Quinn-R's existing deterministic validators (`accessibility_checker.py`, `brand_validator.py`, and reserved audio/composition validators). The fidelity infrastructure complements the existing validation stack — it does not create a second one.

### Validation

21. All L1 contract YAML files pass a structural validation: every criterion has `id`, `name`, `description`, `fidelity_class`, `severity`, `evaluation_type`, `check`
22. The audit report's evidence column references actual file paths and field names that exist in the repository
23. The architectural reference documents are consistent with the GOLD document's definitions

## Tasks / Subtasks

- [x] Task 1: Conduct the formal fidelity maturity audit (AC: #1, #2, #3, #4, #5, #6)
  - [x] 1.1 Read all pipeline artifact schemas (lesson plan template, slide brief template, context envelope, narration script template, segment manifest template, review protocol, checkpoint coordination, source bundle format)
  - [x] 1.2 For each gate G0–G6, evaluate L1 Contracts pillar: does a written, testable fidelity criterion exist? Evidence: cite specific file + field
  - [x] 1.3 For each gate, evaluate L2 Evaluation pillar: does something independently assess output fidelity? Evidence: cite evaluator or note absence
  - [x] 1.4 For each gate, evaluate L3 Memory pillar: does the system capture fidelity outcomes for learning? Evidence: cite sidecar fields or note absence
  - [x] 1.5 For each gate, evaluate Perception pillar: can the evaluator actually interpret the artifact modality? Evidence: cite sensory bridge or note blindness
  - [x] 1.6 Compile audit into `_bmad-output/implementation-artifacts/fidelity-audit-baseline-2026-03-28.md`

- [x] Task 2: Produce the Leaky Neck report (AC: #7, #8, #9)
  - [x] 2.1 Review all agent reference files for natural-language enforcement of deterministic constraints
  - [x] 2.2 Review Marcus delegation envelopes for constraints passed as `additionalInstructions` that could be parameter bindings
  - [x] 2.3 Review Gary's generation logic for natural-language fidelity enforcement vs. API parameter binding
  - [x] 2.4 Review slide brief and context envelope for free-text constraint channels (`additionalInstructions`, `user_constraints`) that invite leaky neck failures — propose finite fidelity-control vocabulary as deterministic replacement
  - [x] 2.5 Compile leaky neck findings into a section of the audit report

- [x] Task 3: Create L1 fidelity contract directory and schema (AC: #10, #11)
  - [x] 3.1 Create `state/config/fidelity-contracts/` directory
  - [x] 3.2 Create `state/config/fidelity-contracts/_schema.yaml` defining the standard contract format
  - [x] 3.3 Create a contract validation script `scripts/validate_fidelity_contracts.py` that checks structural completeness of all contract files

- [x] Task 4: Define L1 contracts for G0–G2 (AC: #12, #13, #14)
  - [x] 4.1 Create `state/config/fidelity-contracts/g0-source-bundle.yaml` with criteria derived from `skills/source-wrangler/references/bundle-format.md`
  - [x] 4.2 Create `state/config/fidelity-contracts/g1-lesson-plan.yaml` with criteria derived from `skills/bmad-agent-content-creator/references/template-lesson-plan.md`
  - [x] 4.3 Create `state/config/fidelity-contracts/g2-slide-brief.yaml` with criteria derived from `skills/bmad-agent-content-creator/references/template-slide-brief.md`

- [x] Task 5: Define L1 contracts for G3–G4 (AC: #15, #16)
  - [x] 5.1 Create `state/config/fidelity-contracts/g3-generated-slides.yaml` with criteria derived from `skills/bmad-agent-gamma/references/context-envelope-schema.md` and slide brief template
  - [x] 5.2 Create `state/config/fidelity-contracts/g4-narration-script.yaml` with criteria derived from narration script template and segment manifest template

- [x] Task 6: Define L1 contracts for G5–G6 (AC: #17, #18)
  - [x] 6.1 Create `state/config/fidelity-contracts/g5-audio.yaml` with criteria derived from ElevenLabs audio skill references
  - [x] 6.2 Create `state/config/fidelity-contracts/g6-composition.yaml` with criteria derived from compositor skill references

- [x] Task 7: Create architectural reference documents (AC: #19, #20)
  - [x] 7.1 Create `docs/app-design-principles.md` covering Three-Layer Model, Hourglass Model, Leaky Neck diagnostic, Sensory Horizon principle
  - [x] 7.2 Create `docs/fidelity-gate-map.md` covering G0–G6 definitions, HIL gate mapping, Fidelity Assessor ordering, role matrix, Fidelity Trace Report format and operating policy, validator integration model

- [x] Task 8: Validate all deliverables (AC: #21, #22, #23)
  - [x] 8.1 Run `validate_fidelity_contracts.py` against all 7 contract files — all pass (7 files, 38 criteria, 0 errors)
  - [x] 8.2 Verify audit report evidence references exist in the repository
  - [x] 8.3 Verify architectural references are consistent with GOLD document definitions
  - [x] 8.4 Update sprint-status.yaml: `2a-1-fidelity-maturity-audit-l1-contracts: review`

## Dev Notes

### Design Direction

- L1 contracts are **human-authored, versioned YAML** — not generated by agents. They define what the Fidelity Assessor (Story 2A-4) will check against. The contracts should be reviewed by the user before the Fidelity Assessor is built.
- The audit report is a **one-time baseline**. Story 2A-9 makes it repeatable as a skill.
- Contracts distinguish between `deterministic` and `agentic` evaluation types. Deterministic criteria can be checked by code today (string match, count comparison). Agentic criteria require LLM judgment and will evolve in sophistication over time — this is the L2 layer.
- Each contract's `fidelity_class` field indicates which fidelity classifications (from Story 3.11's taxonomy) the criterion applies to. This prepares for the Fidelity Assessor to apply different standards to `creative` vs. `literal-text` vs. `literal-visual` slides.
- The Leaky Neck report may identify leaks beyond G3/Gamma. If so, remediation is tracked but implementation is deferred to Story 2A-8.

### Existing Infrastructure To Reuse

| Component | Location | Reuse For |
|-----------|----------|-----------|
| Lesson plan template | `skills/bmad-agent-content-creator/references/template-lesson-plan.md` | G1 contract criteria derivation |
| Slide brief template | `skills/bmad-agent-content-creator/references/template-slide-brief.md` | G2 contract criteria derivation |
| Context envelope schema | `skills/bmad-agent-gamma/references/context-envelope-schema.md` | G3 contract criteria derivation |
| Review protocol | `skills/bmad-agent-quality-reviewer/references/review-protocol.md` | Audit: existing quality dimensions vs. fidelity gaps |
| Checkpoint coordination | `skills/bmad-agent-marcus/references/checkpoint-coord.md` | Audit: HIL gate mapping |
| Source bundle format | `skills/source-wrangler/references/bundle-format.md` | G0 contract criteria derivation |
| Segment manifest template | `skills/bmad-agent-content-creator/references/template-segment-manifest.md` | G4, G6 contract criteria derivation |
| ElevenLabs audio skill | `skills/elevenlabs-audio/` | G5 contract criteria derivation |
| Compositor skill | `skills/compositor/` | G6 contract criteria derivation |
| GOLD document | `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md` | Architectural reference source |

### File Structure (Expected Output)

```
state/config/fidelity-contracts/
├── _schema.yaml
├── g0-source-bundle.yaml
├── g1-lesson-plan.yaml
├── g2-slide-brief.yaml
├── g3-generated-slides.yaml
├── g4-narration-script.yaml
├── g5-audio.yaml
└── g6-composition.yaml

docs/
├── app-design-principles.md          (NEW)
├── fidelity-gate-map.md              (NEW)
└── ...existing docs...

scripts/
├── validate_fidelity_contracts.py    (NEW)
└── ...existing scripts...

_bmad-output/implementation-artifacts/
├── fidelity-audit-baseline-2026-03-28.md  (NEW)
└── 2a-1-fidelity-maturity-audit-l1-contracts.md  (this file)
```

### References

- [GOLD document: `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md`]
- [Epic 2A definition in `_bmad-output/planning-artifacts/epics.md`]
- [Party Mode audit heat map: GOLD document Section 4]
- [Leaky Neck diagnostic: GOLD document Section 3]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus-high-thinking (Cursor)

### Debug Log References

- Pipeline schemas read via explore subagents covering all 9 artifact templates + review protocol + checkpoint coordination + bundle format + 3 memory sidecars
- Validation script run: 7 files, 38 criteria, 0 errors
- Leaky Neck analysis: 3 leaks identified (Gamma additionalInstructions, slide brief advisory params, narration visual_description)

### Completion Notes List

- Produced formal audit report covering all 7 gates against 4 pillars with evidence-backed scoring
- Identified 3 Leaky Neck points with proposed deterministic remediation
- Created 7 L1 fidelity contract YAML files with 38 total criteria across all gates
- Created contract schema (_schema.yaml) and validation script (validate_fidelity_contracts.py)
- Created `docs/app-design-principles.md` covering Three-Layer Model, Hourglass Model, Leaky Neck diagnostic, Sensory Horizon
- Created `docs/fidelity-gate-map.md` covering gate definitions, HIL gate mapping, role matrix, Fidelity Trace Report operating policy, validator integration
- Key audit findings: Level 0 fidelity maturity, zero independent evaluation, source_ref absent from all schemas, fidelity classification absent from all live templates

### File List

**Created:**
- `_bmad-output/implementation-artifacts/fidelity-audit-baseline-2026-03-28.md`
- `state/config/fidelity-contracts/_schema.yaml`
- `state/config/fidelity-contracts/g0-source-bundle.yaml`
- `state/config/fidelity-contracts/g1-lesson-plan.yaml`
- `state/config/fidelity-contracts/g2-slide-brief.yaml`
- `state/config/fidelity-contracts/g3-generated-slides.yaml`
- `state/config/fidelity-contracts/g4-narration-script.yaml`
- `state/config/fidelity-contracts/g5-audio.yaml`
- `state/config/fidelity-contracts/g6-composition.yaml`
- `scripts/validate_fidelity_contracts.py`
- `docs/app-design-principles.md`
- `docs/fidelity-gate-map.md`

**Modified:**
- `_bmad-output/implementation-artifacts/2a-1-fidelity-maturity-audit-l1-contracts.md` (this file — status, tasks, dev record)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (status: in-progress → review)

### Change Log

- 2026-03-28: Story implementation started. All 8 tasks completed in single session.
- 2026-03-28: Audit report, 7 L1 contracts, validation script, 2 architectural reference docs produced.
- 2026-03-28: Story moved to review.
