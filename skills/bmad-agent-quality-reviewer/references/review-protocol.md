# Review Protocol

Systematic dimension-by-dimension review procedure for all production artifacts.

## Quality Dimensions

Eight dimensions reviewed across the pipeline. Not every dimension applies equally to every artifact, but all should be considered when relevant. Each has a default severity and can be calibrated based on learned human preferences.

| Dimension | What It Checks | Default Severity | Source of Truth |
|-----------|---------------|-----------------|----------------|
| **Brand Consistency (BV)** | Colors, typography, imagery style, content voice, tone | High | `resources/style-bible/master-style-bible.md` |
| **Accessibility (CC)** | WCAG 2.1 AA: contrast, alt text, reading level, heading hierarchy | Critical (always) | WCAG 2.1 AA standard, `quality-control` scripts |
| **Learning Objective Alignment (LA)** | Every content element traces to an objective; no orphans, no gaps | High | `state/config/course_context.yaml` |
| **Instructional Soundness** | Bloom's taxonomy fit, cognitive load, content sequencing | Medium-High | Pedagogical judgment (no external reference — Quinn-R's expertise) |
| **Intent Fidelity (IF)** | Output supports the intended behavioral / affective learner effect | Medium-High | Irene artifacts + Marcus HIL-approved direction |
| **Content Accuracy** | Medical/clinical correctness concerns | Critical-escalation | Human review via Marcus (Quinn-R flags, never adjudicates) |
| **Audio Quality (AQ)** | WPM, VTT monotonicity, coverage, pronunciation support | High | Manifest + audio/VTT artifacts |
| **Composition Integrity (CI)** | Duration match, audio/visual coordination, caption sync, assembly coherence | High | Manifest + assembled output |

## Review Procedure

### Step 0: Perceive multimodal artifacts

Before any dimension review, confirm perception of all non-text assets in the artifact set. Follow the universal perception protocol (`skills/sensory-bridges/references/perception-protocol.md`):

- **PNGs/images:** Invoke image bridge — confirm visual content, layout, text with confidence
- **Audio files:** Invoke audio bridge — confirm transcript, WPM, duration with confidence
- **Video files:** Invoke video bridge — confirm keyframes, audio transcript with confidence
- **PDFs:** Invoke PDF bridge — confirm text extraction, scanned page detection with confidence

State interpretation with confidence per modality: "Image bridge: Slide N shows [description]. Confidence: HIGH."

Within a production run, perception results are cached per `(artifact_path, modality)`. If Vera or the producing agent has already perceived the same artifact, read the cached result — do not re-invoke (see `skills/sensory-bridges/references/validator-handoff.md`).

If perception confidence is LOW for any artifact, flag to Marcus for human clarification before scoring quality dimensions on that artifact.

### Step 1: Run automated checks

Invoke `quality-control` skill scripts before judgment review:
- `accessibility_checker.py` — returns structured pass/fail per WCAG criterion
- `brand_validator.py` — returns compliance score per brand dimension

Automated results feed into the structured report but do not replace judgment review.

### Step 2: Brand consistency review (BV)

Read `resources/style-bible/` fresh. Check:
- Visual elements: color hex codes, typography, imagery style match style bible
- Content voice: tone, vocabulary, formality level match voice guidelines
- Severity: High for deviations, Critical if deviation also violates accessibility

### Step 3: Accessibility review (CC)

Review automated results from `accessibility_checker.py`. Additionally check:
- Heading hierarchy (H1 → H2 → H3, no skips)
- Reading level appropriate for target audience (from course context)
- Alt text presence and quality for visual elements
- Contrast ratios for text on backgrounds
- Severity: Always Critical — non-negotiable

### Step 4: Learning objective alignment (LA)

Load learning objectives from `state/config/course_context.yaml`. Check:
- Every content element in the artifact traces to a specific objective
- Flag orphaned content (no objective mapping)
- Flag missing coverage (objectives without corresponding content)
- For assessment items: Bloom's level of question matches Bloom's level of objective
- Severity: High for misalignment, Medium for minor gaps

### Step 5: Instructional soundness

Apply pedagogical judgment:
- Bloom's taxonomy: content type matches the cognitive demand of the learning objective
- Cognitive load: content density appropriate for the format and audience
- Sequencing: content flows logically within and across artifacts
- Severity: Medium for optimization opportunities, High for structural design issues

### Step 5b: Intent fidelity

Check whether the artifact actually supports the intended learner effect defined upstream:
- Read `behavioral_intent` from lesson plan, slide brief, narration script, or segment manifest when present
- If absent, fall back to Marcus's HIL-approved creative direction
- Evaluate whether the visual/audio choices reinforce that effect or flatten it
- Severity: Medium for weak execution, High when the artifact fights the intended effect

**Pre-composition behavioral_intent validation (G4 artifacts):** When reviewing narration script + segment manifest before audio generation:
- Verify `behavioral_intent` is present on every segment (warn if missing)
- Cross-check that `behavioral_intent` is coherent across the narration script stage directions, segment manifest, and any composition notes for the same segment
- Flag segments where the narration tone/content contradicts the stated `behavioral_intent` (e.g., clinical monotone narration paired with an "inspire curiosity" intent)
- For non-static segments (`visual_mode: video`), confirm the motion-first narration approach supports the stated behavioral effect rather than undermining it with static-slide description

### Step 6: Content accuracy scan

Flag potential medical/clinical accuracy concerns:
- Unusual drug dosages or ranges
- Unfamiliar or potentially incorrect clinical terminology
- Internal contradictions within or across artifacts
- Severity: Critical-escalation — always route through Marcus to human review
- NEVER adjudicate — flag the concern with location, description, and why it triggered

## Fidelity-Aware Review (Mixed-Fidelity Decks)

When reviewing slide decks with mixed fidelity classes, Quinn-R uses the `provenance` manifest from Gary's return envelope to apply class-appropriate review criteria:

| Fidelity Class | Review Focus |
|---------------|-------------|
| **creative** | Standard visual quality + pedagogical alignment. Gamma AI enhancements are expected and welcome. |
| **literal-text** | Exact text match against slide brief input. Flag any Gamma embellishment (added subtitles, bullet rewriting, merged content). Score content fidelity conservatively. |
| **literal-visual** | Image presence verification (is the user-provided image on the slide?). Surrounding text preservation. Layout integrity with the embedded image. |

Quinn-R reads the `provenance[]` array to determine which call produced each slide and applies the matching criteria. For literal slides, content fidelity is the dominant dimension — a beautifully styled slide that changes the text fails quality review.

## Multi-Artifact Review

When reviewing multiple related artifacts (e.g., narration script + paired slide brief):

### Cross-artifact consistency checks
- Pairing references match (NS-M2L3-04 references SB-M2L3-04 and vice versa)
- Content alignment: narration text and slide text tell the same story
- Terminology consistency: same medical terms used across paired artifacts
- Sequencing consistency: slide order matches narration order
- Intent consistency: `behavioral_intent` is coherent across slide, narration, manifest, and final composition notes

### Asset-lesson pairing invariant
- Every artifact references its lesson plan (LP-{id})
- No artifact exists without a lesson plan reference
- All artifacts within a lesson plan are accounted for

## Calibration Protocol

Quinn-R adjusts severity classifications based on human reviewer feedback:

### How calibration works
1. After each human review checkpoint, Marcus relays which findings were accepted, rejected, or adjusted
2. Quinn-R records the calibration event in `patterns.md` with: finding type, original severity, human action, adjusted severity, reasoning
3. On subsequent reviews, Quinn-R applies learned adjustments transparently

### Calibration rules
- **Promoted findings** (human asked to escalate): increase severity for that finding type going forward
- **Demoted findings** (human consistently dismisses): decrease severity, but never below Low for any quality dimension
- **Audience-specific thresholds** (e.g., "Grade 13 reading level acceptable for attending physicians"): record as audience-conditional calibration
- **Transparency**: always note calibration adjustments in the quality report

### Calibration limits
- Accessibility findings CANNOT be demoted below Critical — non-negotiable
- Medical accuracy flags CANNOT be suppressed — always escalate
- Calibration resets if the style bible is updated (new standards = fresh baseline)

## Audio / Composition Checks

When the review includes narration or final assembly:

- **AQ**: narration WPM, VTT monotonicity, pronunciation support, segment coverage
- **CI**: video duration vs narration duration, caption sync, transition consistency, assembly coherence
- **IF**: the emotional/behavioral effect should survive into the assembled output, not be lost in technically correct but flat composition

### SFX / Music Cue Selection (CI sub-check)

When `sfx` or `music` cue fields are present in the segment manifest:
- Verify cue selections are contextually appropriate for the segment's content and pedagogical purpose
- Check that SFX/music choices support the segment's `behavioral_intent` (e.g., a calming music cue should not accompany an "urgency" intent)
- Flag jarring transitions where adjacent segments have incompatible audio atmosphere cues
- Severity: Medium for suboptimal cue selection, High if the cue actively undermines the learning experience

### Bridge Re-validation at Pre-Composition

When reviewing the approved Pass 2 package before composition spend:
- Confirm that intro/outro bridge segments are still correctly placed after any Gate 3 revisions
- Verify bridge cadence (intro/outro every N slides or M minutes) remains within the configured policy from `narration-script-parameters.yaml`
- Flag bridge segments whose `behavioral_intent` does not serve a transitional or framing purpose
- Severity: Medium for cadence drift, High if bridge placement creates pedagogical discontinuity
