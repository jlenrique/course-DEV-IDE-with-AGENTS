# Fidelity Gate Map

This document defines the seven fidelity gates (G0–G6), their relationship to HIL gates, the assessment ordering, the role matrix, and the Fidelity Trace Report operating policy.

**Note:** This document is authoritative for fidelity gate sequencing and the Vera vs Quinn-R assessment boundary. The full cross-agent ownership model is documented in `docs/lane-matrix.md`, which extends lane definitions to orchestration, instructional design, tool execution quality, perception, and platform deployment.

---

## Gate Definitions

| Gate | Artifact | Producing Agent | Source of Truth | HIL Gate |
|------|----------|----------------|----------------|----------|
| **G0** | Source Bundle (`extracted.md`) | Source Wrangler | Original SME materials | — |
| **G1** | Lesson Plan | Irene | Source bundle + SME intent | Gate 1 |
| **G2** | Slide Brief | Irene | Lesson plan | Gate 1 |
| **G3** | Generated Slides (PNGs) | Gary | Slide brief | Gate 2 |
| **G4** | Narration Script + Segment Manifest | Irene (Pass 2) | Lesson plan + actual slides (PNGs) | Gate 3 |
| **G5** | Audio (MP3/WAV) | ElevenLabs Voice Director | Narration script | — |
| **G6** | Composed Video | Compositor + Human (Descript) | Segment manifest | Gate 4 |

L1 fidelity contracts for each gate are defined in `state/config/fidelity-contracts/g{n}-*.yaml`.

For G4, the L1 contract must reference both Irene Pass 2 templates: the narration script template and the segment manifest template. Treat either template drifting out of the G4 contract as a contract defect, because G6 consumes the manifest as its source of truth.

---

## Fidelity Gates vs. HIL Gates

Fidelity gates are **automated pre-checks** that run before human checkpoints. HIL gates are **human review** checkpoints.

```
G0 → G1 → G2 → [HIL Gate 1] → G3 → [HIL Gate 2] → G4 → [HIL Gate 3] → G5 → G6 → [HIL Gate 4]
```

Operational anti-drift checkpoints layered on top of the gate chain:
- **Prompt 6B checkpoint (pre-G3 dispatch side effects):** literal-visual operator packet and per-card readiness confirmation.
- **Storyboard A checkpoint (post-G3 generation):** visual order/content approval before Gate 2 progression.
- **Storyboard B checkpoint (post-G4 output):** slide+script alignment approval before downstream audio/script finalization.

At each HIL gate, the human reviewer has already seen:
- The Fidelity Assessor's Fidelity Trace Report (Omissions/Inventions/Alterations)
- Quinn-R's quality review report (8 dimensions)

---

## Assessment Ordering at Each Gate

```
Producing Agent returns artifact
        ↓
[1] Fidelity Assessor — "Is this faithful to its source of truth?"
        ↓ (PASS)
[2] Quinn-R — "Is this good against our quality standards?"
        ↓ (PASS)
[3] Human (HIL Gate) — "Do I approve this?"
```

If the Fidelity Assessor fails (critical or high finding), the pipeline halts — Quinn-R and the human never see the artifact. It routes back to the producing agent for correction.

---

## Role Matrix

For each assessment dimension, exactly one agent owns the judgment. No dimension is claimed by more than one agent.

| Dimension | Owner | Scope |
|-----------|-------|-------|
| **Source-to-output traceability** | Fidelity Assessor | Does the output faithfully represent its source of truth? (O/I/A taxonomy) |
| **Provenance chain integrity** | Fidelity Assessor | Can every content item be traced back to the original SME material via source_ref? |
| **Cumulative drift** | Fidelity Assessor | Has fidelity degraded across multiple gates compared to G0? |
| **Fidelity classification accuracy** | Fidelity Assessor | Are literal/creative tags correctly applied at G2? |
| **Brand consistency** | Quinn-R | Colors, fonts, logos match style bible |
| **Accessibility compliance** | Quinn-R | WCAG 2.1 AA |
| **Learning objective alignment** | Quinn-R | Content maps to LOs per course_context.yaml |
| **Instructional soundness** | Quinn-R | Cognitive load, scaffolding, sequencing |
| **Intent fidelity** | Quinn-R | Does the finished learner experience achieve the intended `behavioral_intent` effect? |
| **Content accuracy flags** | Quinn-R | Potential medical accuracy concerns — flagged, never adjudicated |
| **Audio quality** | Quinn-R | Voice clarity, background noise, production polish |
| **Composition integrity** | Quinn-R | Final assembly quality, transitions, sync |
| **Tool parameter quality** | Producing Agent (self-assessment) | Execution-only self-check: layout integrity, parameter confidence, and embellishment risk control. Excludes pedagogy, quality standards, and source-faithfulness lanes. |

**Key boundary:** The Fidelity Assessor asks "is this *right* relative to the source?" Quinn-R asks "is this *good* against standards and learner-effect intent?" The producing agent asks "did I execute the tool *well* within my lane?"

---

## Fidelity Trace Report Format

Every fidelity assessment produces a report with findings in three categories:

| Finding Type | Definition | Example |
|-------------|-----------|---------|
| **Omission** | Source content missing from output | "KC topics 4, 7, 9 from the knowledge check list do not appear in the generated slide" |
| **Invention** | Output content not traceable to source | "Slide 5 includes a 'Clinical Pearl' callout not present in the slide brief" |
| **Alteration** | Source content present but meaning changed | "Source: 'contraindicated in renal impairment'; Slide: 'use with caution in renal impairment'" |

Each finding includes: `gate`, `artifact_location` (slide N, line range, timestamp), `severity` (critical/high/medium), `source_ref`, `output_ref`, `suggested_remediation`.

---

## Fidelity Trace Report Operating Policy

| Severity | Response | Max Retries | Remediation Owner | Escalation | Waiver Authority |
|----------|----------|:-----------:|-------------------|------------|-----------------|
| **Critical** | Immediate circuit break — pipeline halts | 0 (no auto-retry) | Producing agent + human review | Marcus → Human | Human only (logged with rationale) |
| **High** | Circuit break — producing agent receives report, may retry with specific remediation guidance | 1 | Producing agent | Second failure → Marcus → Human | Human only (logged with rationale) |
| **Medium** | Warning — artifact proceeds to Quinn-R and HIL gate with findings attached | N/A | Producing agent (advisory) | No escalation unless user requests | N/A (proceeds automatically) |

- Maximum **2 retries per gate per production run** before mandatory human escalation
- Waivers are logged in the Fidelity Trace Report with the human's rationale
- In **ad-hoc mode**, high findings downgrade to warnings (proceed with advisory); critical findings still halt

---

## Validator Integration

Sensory bridge outputs feed into **both** the Fidelity Assessor and Quinn-R's existing validators:

```
Sensory Bridge Output (canonical schema)
        ↓                    ↓
Fidelity Assessor         Quinn-R
(source traceability)     (quality standards)
        ↓                    ↓
Uses: extracted_text,     Uses: layout, colors,
content comparison,       contrast ratios,
source_ref resolution     accessibility features
```

The sensory bridges are **shared infrastructure** — they do not create a parallel validation stack. Quinn-R's existing deterministic validators (`accessibility_checker.py`, `brand_validator.py`) consume the same structured output.
