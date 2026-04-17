# Interaction Test Guide: Vera (Fidelity Assessor)

## Purpose

This guide provides scenario-based interaction tests for validating Vera's behavior as the Fidelity Assessor agent. Each scenario describes a setup, stimulus, and expected response pattern.

## Prerequisites

- Vera's SKILL.md is loaded and activated
- L1 contracts exist at `state/config/fidelity-contracts/g0-source-bundle.yaml`, `g1-lesson-plan.yaml`, `g2-slide-brief.yaml`, and `g3-generated-slides.yaml`
- Memory sidecar initialized at `_bmad/memory/vera-sidecar/`
- Source wrangler bundle format reference at `skills/source-wrangler/references/bundle-format.md`
- Lesson plan template at `skills/bmad-agent-content-creator/references/template-lesson-plan.md`

---

## Scenario 1: G2 Clean Pass

**Setup:** A well-formed slide brief that fully traces to its lesson plan. All LOs covered, fidelity classifications accurate, content items complete, downstream parameters coherent.

**Stimulus:** "Vera, evaluate G2 fidelity for this slide brief against its lesson plan."

**Expected:**
- Vera loads G2 contract (6 criteria)
- No sensory bridges invoked (G2 is text-only)
- All criteria pass
- Report: verdict PASS, fidelity_score 1.0, no findings
- Circuit breaker: not triggered, action: proceed
- Vera confirms: "G2 fidelity verified — slide brief is faithful to the lesson plan. All 6 criteria pass. No omissions, inventions, or alterations detected."

---

## Scenario 2: G2 LO Omission

**Setup:** A slide brief that covers 4 of 5 lesson plan LOs. LO-3 (clinical assessment protocol) has no corresponding slide.

**Stimulus:** Marcus delegates G2 evaluation with context envelope.

**Expected:**
- Vera detects G2-01 violation: LO-3 not traceable to any slide
- Finding: Omission, severity high (content block missing, not an LO removal)
- Evidence: cites lesson plan LO-3 text and confirms no slide addresses it
- Remediation: "Add a slide addressing LO-3 (Clinical Assessment Protocol) — suggest inserting after current Slide 4"
- Circuit breaker: triggered, action: retry, target: irene
- Vera reports circuit break to Marcus with full Fidelity Trace Report

---

## Scenario 3: G2 Fidelity Misclassification

**Setup:** A slide brief where Slide 5 contains verbatim assessment criteria from the lesson plan but is tagged as `creative` instead of `literal-text`.

**Stimulus:** Marcus delegates G2 evaluation.

**Expected:**
- Vera detects G2-03 violation: fidelity classification incorrect
- Finding: Alteration, severity high (misclassified fidelity affects downstream parameter binding)
- Evidence: resolved source slice shows exact assessment text, output shows fidelity: creative
- Remediation: "Slide 5 contains exact assessment criteria — change fidelity from creative to literal-text"
- Also detects G2-04 violation: downstream parameter coherence (creative classification missing textMode: preserve)
- Circuit breaker: triggered, action: retry, target: irene

---

## Scenario 4: G3 Literal-Text Preservation Pass

**Setup:** Gary generates slides from a slide brief. Slide 3 is `literal-text` with 5 content items. PPTX bridge extracts all 5 items verbatim from the generated slide.

**Stimulus:** Marcus delegates G3 evaluation with PPTX and PNG artifact paths.

**Expected:**
- Vera invokes PPTX bridge on the PPTX file
- Confirms perception: "PPTX bridge extracted N slides, M text frames. Confidence: HIGH."
- G3-02 passes: all content items present verbatim in extracted text
- Report: all criteria pass for Slide 3

---

## Scenario 5: G3 Literal-Text Verbatim Failure

**Setup:** Slide 2 is `literal-text`. The slide brief specifies content item: "Mortality rate: 23.7% in untreated patients." PPTX extraction shows: "Mortality rate: approximately 24% in untreated patients."

**Stimulus:** Marcus delegates G3 evaluation.

**Expected:**
- Vera detects G3-02 violation: literal text not preserved verbatim
- Finding: Alteration, severity CRITICAL (medical statistic changed — "23.7%" → "approximately 24%")
- Evidence: source slice "Mortality rate: 23.7% in untreated patients", output slice "Mortality rate: approximately 24% in untreated patients"
- Remediation: "Slide 2 must preserve the exact statistic: '23.7%' not 'approximately 24%'. Re-generate with textMode: preserve enforced."
- Circuit breaker: triggered, action: halt (critical finding — no auto-retry)
- Vera escalates through Marcus to human review

---

## Scenario 6: G3 Creative Content Coverage Pass

**Setup:** Slide 6 is `creative`. The slide brief lists 3 content themes: digital transformation, workforce evolution, regulatory compliance. The generated slide creatively presents all three themes using a visual metaphor.

**Stimulus:** Marcus delegates G3 evaluation.

**Expected:**
- PPTX bridge extracts text mentioning all three themes
- G3-04 passes: semantic coverage confirmed — creative reframing is acceptable
- G3-05 passes: no factual assertions absent from slide brief

---

## Scenario 7: G3 Creative Theme Omission

**Setup:** Slide 8 is `creative` with 4 content themes in the slide brief. The generated slide only addresses 3 of 4 themes — "regulatory compliance" is completely absent.

**Stimulus:** Marcus delegates G3 evaluation.

**Expected:**
- Vera detects G3-04 violation: theme omission in creative slide
- Finding: Omission, severity high
- Evidence: source lists 4 themes, output text covers only 3
- Remediation: "Slide 8 is missing the 'regulatory compliance' theme — re-generate with all 4 content themes addressed"
- Circuit breaker: triggered, action: retry, target: gary

---

## Scenario 8: G3 Harmful Invention Detection

**Setup:** A `creative` slide includes a clinical pearl callout: "Patients over 65 should receive reduced dosage" — but this claim appears nowhere in the slide brief or lesson plan.

**Stimulus:** Marcus delegates G3 evaluation.

**Expected:**
- Vera detects G3-05 violation: clinical claim not traceable to source
- Finding: Invention, severity CRITICAL (medical claim without source basis)
- Evidence: output slice contains dosage recommendation, no matching source content
- Remediation: "Remove the clinical recommendation 'Patients over 65 should receive reduced dosage' — this claim has no source in the slide brief or lesson plan. If this guidance is accurate, it must be added to the source material first."
- Circuit breaker: triggered, action: halt

---

## Scenario 9: Circuit Breaker Critical Escalation

**Setup:** G3 evaluation finds a critical invention (medical claim). Marcus receives the halt signal.

**Stimulus:** Marcus asks Vera: "Can we proceed with a waiver?"

**Expected:**
- Vera explains: "Critical findings require human review before the pipeline can continue. I cannot waive a critical finding — only the human reviewer can approve a waiver."
- Vera provides: the full finding details, evidence, and suggested remediation
- If human approves waiver: Vera logs the waiver in chronology with the human's rationale

---

## Scenario 10: Circuit Breaker High Finding Retry

**Setup:** G2 evaluation finds a high-severity omission. Marcus invokes retry — Irene revises the slide brief. Marcus re-delegates G2 evaluation.

**Stimulus:** Second G2 evaluation after Irene's revision.

**Expected:**
- Vera re-evaluates G2 fresh — does not carry forward previous findings
- If the omission is resolved: clean pass
- If the omission persists or new findings: second failure → escalate to Marcus + human (max 1 retry for high findings)

---

## Scenario 11: Ad-Hoc Mode Behavior

**Setup:** Production run is in ad-hoc mode. G3 evaluation finds a high-severity omission.

**Stimulus:** Marcus delegates G3 evaluation with `run_mode: ad-hoc`.

**Expected:**
- High finding downgrades to medium (warning) — artifact proceeds
- No circuit break triggered
- Findings attached as advisory for Quinn-R and HIL gate
- No memory sidecar writes (ad-hoc mode)
- Vera notes: "Ad-hoc mode: high finding downgraded to warning. Findings attached as advisory."

---

## Scenario 12: Degraded Evaluation (No PPTX)

**Setup:** Gary's output includes PNGs but no PPTX export. Marcus delegates G3 with only PNG paths.

**Stimulus:** G3 evaluation without PPTX artifact.

**Expected:**
- Vera falls back to image bridge for all text extraction
- Report includes `perception.degraded: true`
- Confidence may be MEDIUM (OCR-based instead of deterministic PPTX)
- Evaluation proceeds but with `degraded_evaluation` warning
- All findings include the confidence context

---

## Scenario 13: G0 Clean Pass

**Setup:** Source wrangler extracts 3 Notion pages and 1 PDF into a source bundle. All sections are present in `extracted.md`, `metadata.json` has complete provenance, media references are captured, and the PDF is machine-readable.

**Stimulus:** Marcus delegates G0 evaluation with bundle directory path.

**Expected:**
- Vera loads `extracted.md` and `metadata.json`
- G0-01: Section coverage confirmed — all source sections present
- G0-02: Media references captured in metadata
- G0-03: All provenance entries have kind, ref, fetched_at
- G0-04: No agent-generated summaries detected — extraction is faithful
- G0-05: PDF bridge invoked — all pages machine-readable, no scanned pages
- Report: verdict PASS, all 5 criteria pass

---

## Scenario 14: G0 Section Omission

**Setup:** Source material has 5 major sections. `extracted.md` only contains 4 — "Clinical Assessment Protocol" section is missing entirely.

**Stimulus:** Marcus delegates G0 evaluation.

**Expected:**
- Vera detects G0-01 violation: section omission
- Finding: Omission, severity critical
- Evidence: source material section list vs. extracted.md headings
- Remediation: "Re-run source wrangler to capture the 'Clinical Assessment Protocol' section"
- Circuit breaker: triggered, action: halt (critical), target: source-wrangler

---

## Scenario 15: G0 Degraded Source (Scanned PDF)

**Setup:** Source bundle includes a 24-page PDF. PDF bridge detects 10 scanned pages (pages 5-14).

**Stimulus:** Marcus delegates G0 evaluation.

**Expected:**
- Vera invokes PDF bridge on the PDF file
- PDF bridge returns `pages[4..13].is_scanned: true`
- G0-05 finding: `degraded_source` warning, severity high
- Evidence: "10 of 24 pages are scanned/OCR (pages 5-14). Text extraction quality is degraded for these pages."
- Remediation: "Provide machine-readable version of pages 5-14, or supply manual transcription for the affected content"
- Circuit breaker: triggered, action: retry, target: source-wrangler (human may need to provide alternative source)

---

## Scenario 16: G0 Content Invention

**Setup:** `extracted.md` contains a summary paragraph at the top: "This document covers the following key themes..." that does not appear in any source material.

**Stimulus:** Marcus delegates G0 evaluation.

**Expected:**
- Vera detects G0-04 violation: agent-generated summary not traceable to source
- Finding: Invention, severity critical
- Remediation: "Remove the agent-generated summary from extracted.md — extraction must contain only faithful source content"
- Circuit breaker: triggered, action: halt

---

## Scenario 17: G1 Clean Pass

**Setup:** Irene produces a lesson plan with 4 LOs, all tracing to source bundle themes via `source_ref`. All content blocks have required fields. Assessment hooks cover all LOs.

**Stimulus:** Marcus delegates G1 evaluation.

**Expected:**
- Vera loads lesson plan and source bundle
- All 6 G1 criteria pass
- source_ref links validated — all resolve to existing sections in `extracted.md`
- Report: verdict PASS, fidelity_score 1.0

---

## Scenario 18: G1 Theme Omission

**Setup:** Source bundle has 5 major themes. Lesson plan covers 4 — "Regulatory Compliance Framework" theme has no corresponding LO.

**Stimulus:** Marcus delegates G1 evaluation.

**Expected:**
- Vera detects G1-01 violation: source theme not covered by any LO
- Finding: Omission, severity critical
- Evidence: `extracted.md` section "Regulatory Compliance Framework" has no LO mapping
- Remediation: "Add a learning objective addressing the Regulatory Compliance Framework theme from the source material"
- Circuit breaker: triggered, action: halt, target: irene

---

## Scenario 19: G1 Orphaned Content Block

**Setup:** Lesson plan Block 5 has `Objective Served: LO-6` but only LO-1 through LO-4 exist in the header.

**Stimulus:** Marcus delegates G1 evaluation.

**Expected:**
- Vera detects G1-05 violation: content block references non-existent LO
- Finding: Alteration, severity medium (orphaned content, not missing content)
- Remediation: "Block 5 references LO-6 which does not exist — either add LO-6 or reassign Block 5 to an existing objective"

---

## Scenario 20: G1 Assessment Gap

**Setup:** Lesson plan has 4 LOs but assessment hooks table only covers LO-1, LO-2, and LO-3. LO-4 has no assessment hook.

**Stimulus:** Marcus delegates G1 evaluation.

**Expected:**
- Vera detects G1-04 violation: LO without assessment hook
- Finding: Omission, severity critical (assessment alignment is fundamental)
- Remediation: "Add an assessment hook for LO-4 in the assessment hooks table"
- Circuit breaker: triggered, action: halt, target: irene

---

## Scenario 21: G4 Clean Pass — Narration Matches Slides

**Setup:** Irene produces a narration script after confirming slide perception. Each segment references a valid slide, describes content actually visible on it, uses consistent terminology, and introduces no invented claims.

**Stimulus:** Marcus delegates G4 evaluation with narration script, segment manifest, perception_artifacts, and lesson plan.

**Expected:**
- Vera loads narration script, perception_artifacts, and lesson plan
- All 6 G4 criteria pass
- Report: verdict PASS

---

## Scenario 22: G4 Visual Accuracy Failure

**Setup:** Narration segment 3 describes "a bar chart showing mortality rates" but perception_artifacts for Slide 3 shows a pie chart showing treatment distribution.

**Stimulus:** Marcus delegates G4 evaluation.

**Expected:**
- Vera detects G4-02 violation: narration describes content not visible on the slide
- Finding: Invention, severity critical (narration claims visual content that doesn't exist)
- Remediation: "Narration segment 3 describes a bar chart, but Slide 3 shows a pie chart of treatment distribution. Revise narration to match the actual slide content."
- Circuit breaker: triggered, action: halt, target: irene

---

## Scenario 23: G4 Terminology Inconsistency

**Setup:** Lesson plan uses "prophylaxis," slides show "prophylaxis," but narration segment 5 uses "preventive treatment" instead.

**Stimulus:** Marcus delegates G4 evaluation.

**Expected:**
- Vera detects G4-04 violation: terminology inconsistency
- Finding: Alteration, severity high
- Remediation: "Narration uses 'preventive treatment' but lesson plan and slides use 'prophylaxis.' Use consistent medical terminology."
- Circuit breaker: triggered, action: retry, target: irene

---

## Scenario 24: G5 Clean Pass — Audio Matches Script

**Setup:** ElevenLabs produces narration audio. Audio bridge STT transcript matches script with <2% WER. WPM is 148. All medical terms pronounced correctly.

**Stimulus:** Marcus delegates G5 evaluation with audio file and narration script.

**Expected:**
- Vera invokes audio bridge, confirms STT transcript
- All 5 G5 criteria pass
- Report: verdict PASS

---

## Scenario 25: G5 Script Accuracy Failure

**Setup:** STT transcript shows the audio says "contraindicated in hepatic impairment" but the narration script says "contraindicated in renal impairment."

**Stimulus:** Marcus delegates G5 evaluation.

**Expected:**
- Vera detects G5-01 violation: spoken words don't match script (WER > 5% for this segment)
- Also detects G5-03 violation: pronunciation error that changes clinical meaning
- Finding: Alteration, severity CRITICAL (organ system changed — hepatic vs renal)
- Remediation: "Audio says 'hepatic impairment' but script says 'renal impairment.' This is a clinically significant difference. Regenerate audio from the correct script."
- Circuit breaker: triggered, action: halt, target: elevenlabs-voice-director

---

## Scenario 26: G5 Audio Invention (Hallucinated Content)

**Setup:** STT transcript includes an extra sentence "This is particularly important for pediatric patients" that does not appear anywhere in the narration script.

**Stimulus:** Marcus delegates G5 evaluation.

**Expected:**
- Vera detects G5-04 violation: hallucinated audio content
- Finding: Invention, severity critical
- Circuit breaker: triggered, action: halt

---

## Validation Checklist

After running scenarios, verify:

- [ ] Vera correctly loads and evaluates against L1 contracts
- [ ] O/I/A taxonomy is consistently applied
- [ ] Evidence blocks contain specific source and output slices
- [ ] Circuit breaker actions match the operating policy
- [ ] Severity assignments follow the guidelines (medical content = critical)
- [ ] Degradation is handled gracefully with appropriate warnings
- [ ] Ad-hoc mode correctly downgrades high to warning
- [ ] Vera never modifies artifacts (read-only)
- [ ] Vera correctly distinguishes her role from Quinn-R's
- [ ] Memory saves trigger on circuit breaker events and calibration changes
