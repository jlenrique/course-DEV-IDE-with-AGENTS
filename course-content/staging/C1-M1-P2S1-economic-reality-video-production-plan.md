# Production Plan: "The Economic & Structural Reality" Educational Video

**Run ID:** C1-M1-P2S1-VID-001
**Created:** 2026-03-26
**Mode:** Default
**Status:** Planning — awaiting approval

---

## 1. Context

| Field | Value |
|-------|-------|
| **Course** | C1 — Foundations of Innovation Leadership |
| **Module** | M1 — Foundations of the Innovation Mindset |
| **Part** | Part 2: The Macro Trends & The Case for Change |
| **Slide** | Slide 1: The Economic & Structural Reality |
| **Content Type** | Educational video (data visualization + voiceover narration) |
| **Target Duration** | 60–90 seconds |
| **Source Document** | `course-content/courses/TEJAL_Course 01 Mod 01 Notes 2026-03-16.pdf` (pp. 6–7) |
| **Subject Matter Expert** | Dr. Tejal Naik |

### Learning Objectives Served

This video directly supports **CLO #2** from the M1 notes:

> Analyze the macro-economic and structural trends—including administrative burnout, healthcare consumerism, and technological acceleration—that necessitate intrapreneurial physician leadership. (Analyze)

### Asset-Lesson Pairing

| Asset | Paired Lesson | Objective Trace |
|-------|---------------|-----------------|
| Data visualization (slide/image) | C1-M1 Part 2, Chapter 2 | CLO #2 (Analyze macro trends) |
| Voiceover narration (audio) | C1-M1 Part 2, Chapter 2 | CLO #2 (Analyze macro trends) |
| Assembled video | C1-M1 Part 2, Chapter 2 | CLO #2 (Analyze macro trends) |

---

## 2. Source Content

### Narration Script (from SME notes — production-ready)

> "To understand our current environment, we must first look at the structural forces at play. U.S. healthcare spending continues to rise exponentially, now accounting for nearly one-fifth of the nation's economy and reaching $5.2 trillion in 2024. Alongside this financial pressure is a massive structural shift in how we work. Between 2012 and 2022, independent private practice fell drastically, while the share of physicians employed by large health systems surged. We are increasingly working within massive, complex organizations, which fundamentally changes our autonomy and decision-making authority. To effect change now, you cannot just optimize your own clinic; you must know how to navigate and influence a large enterprise."

**Word count:** ~118 words
**Estimated read time:** ~55–65 seconds at professional narration pace

### Visual Specification (from SME notes)

> A sleek, corporate data visualization slide on a dark navy background. The left side features an upward trending line graph labeled 'National Health Expenditures reaching $5.2 Trillion'. The right side features two comparing bar charts showing 'Independent Practice' shrinking and 'Hospital Employment' growing. Clean sans-serif typography, highly legible, modern aesthetic.

### Academic References

- CMS National Health Expenditure (NHE) Fact Sheet
- American Medical Association Practice Ownership Report

---

## 3. Style Bible Compliance Requirements

All production outputs must conform to the JCPH Master Style Bible v1.0:

### Visual Standards

| Element | Specification | Source |
|---------|--------------|--------|
| **Background** | Dark navy `#1e3a5f` | Style Bible — Chart and Data Visualization |
| **Data colors** | Teal primary `#4a90a4`, white secondary `#ffffff`, orange accents `#fd7e14` for emphasis | Style Bible — Chart and Data Visualization |
| **Data typography** | Source Sans Pro 400/600 for numbers and labels | Style Bible — Typography System |
| **Heading typography** | Montserrat 600/700 for slide title | Style Bible — Typography System |
| **Chart style** | Clean, minimal, emphasis on signal over noise | Style Bible — Chart and Data Visualization |
| **Mobile optimization** | Large touch targets, readable at small sizes | Style Bible — Chart and Data Visualization |
| **Contrast** | WCAG 2.1 AA minimum (4.5:1 normal text, 3:1 large) | Style Bible — Accessibility |
| **Color independence** | Information never conveyed by color alone | Style Bible — Accessibility |

### Voice & Tone Standards

| Element | Specification |
|---------|--------------|
| **Voice profile** | Professional, authoritative, clear articulation |
| **Pace** | Moderate, appropriate for medical content |
| **Tone** | Respectful peer-to-peer communication |
| **Quality** | Professional narration standard |
| **Audience context** | Practicing physicians — time-constrained, evidence-driven |

### Gamma Prompt Template (from Style Bible)

> "Create professional medical education slides with:
> - Color scheme: Navy blue primary (#1e3a5f), teal accents (#4a90a4)
> - Typography: Clean, executive presentation style
> - Layout: Minimal, high contrast, mobile-optimized
> - Aesthetic: Corporate medical education, not consumer health
> - Content focus: [SPECIFIC_TOPIC]"

---

## 4. Production Stages

### Stage 1: Script Review & Finalization

| Field | Value |
|-------|-------|
| **Specialist** | Marcus (internal — CM capability) |
| **Input** | Raw narration from SME notes |
| **Action** | Review script for style bible voice/tone compliance, pacing, clarity. Minor polish only — SME's clinical voice and content authority are preserved. |
| **Output** | Finalized narration script |
| **Status** | Can execute now |

**CHECKPOINT GATE 1** — Juan reviews finalized script before voiceover production.

### Stage 2: Data Visualization Production

| Field | Value |
|-------|-------|
| **Specialist** | `gamma-specialist` |
| **Input** | Visual specification from SME notes + style bible compliance requirements |
| **Action** | Generate a single-slide data visualization with dual-axis layout: (1) NHE line graph trending to $5.2T, (2) practice model bar comparison. Apply JCPH Navy background, teal/white data colors, Source Sans Pro labels, Montserrat title. |
| **Output** | High-resolution slide image (PNG/PDF) in `course-content/staging/` |
| **Tool** | Gamma API (API-ready, verified in pre-flight) |
| **Fallback** | If Gamma output requires refinement: export and adjust manually, or use Canva with brand kit |
| **Status** | Can execute now (Gamma API operational) |

**Context envelope to specialist:**
```yaml
run_id: C1-M1-P2S1-VID-001
content_type: data-visualization-slide
scope: C1 > M1 > Part 2 > Slide 1
learning_objective: "Analyze macro-economic and structural trends (CLO #2)"
style_bible_sections:
  - "Chart and Data Visualization"
  - "Color Palette — Primary and Supporting"
  - "Typography System"
  - "Accessibility Requirements"
user_constraints:
  - "Dark navy background, not light"
  - "Dual-axis layout: line graph left, bar charts right"
  - "Clean, minimal — emphasis on signal over noise"
data_points:
  - "NHE: $5.2 trillion (2024), upward trend"
  - "Independent practice: declining 2012–2022"
  - "Hospital employment: surging 2012–2022"
```

**CHECKPOINT GATE 2** — Juan reviews data visualization for accuracy, brand compliance, and readability.

### Stage 3: Voiceover Production

| Field | Value |
|-------|-------|
| **Specialist** | `elevenlabs-specialist` |
| **Input** | Approved narration script from Stage 1 |
| **Action** | Synthesize professional voiceover using ElevenLabs. Voice selection TBD with Juan — candidates from pre-flight: Roger (Laid-Back, Resonant), Sarah (Mature, Reassuring), George (Warm, Captivating Storyteller). |
| **Output** | MP3 audio file in `course-content/staging/` |
| **Tool** | ElevenLabs API (API-ready, 45 voices available, verified in pre-flight) |
| **Parameters to decide** | Voice ID, model (Eleven v3 recommended for quality), stability/similarity settings |
| **Status** | Can execute now (ElevenLabs API operational) |

**Context envelope to specialist:**
```yaml
run_id: C1-M1-P2S1-VID-001
content_type: voiceover-narration
scope: C1 > M1 > Part 2 > Slide 1
style_bible_sections:
  - "ElevenLabs Voice Generation"
  - "Voice and Content Guidelines — Voice Characteristics"
voice_requirements:
  profile: "Professional, authoritative, clear articulation"
  pace: "Moderate — appropriate for physician audience"
  tone: "Respectful peer-to-peer, not lecturing"
  quality: "Professional narration standard"
script_word_count: 118
estimated_duration: "55–65 seconds"
```

**CHECKPOINT GATE 3** — Juan reviews voiceover for tone, pacing, pronunciation of medical/financial terms.

### Stage 4: Video Assembly

| Field | Value |
|-------|-------|
| **Specialist** | `assembly-coordinator` |
| **Input** | Approved data visualization (Stage 2) + approved voiceover (Stage 3) |
| **Action** | Combine static visual with audio narration into a video format. Add subtle motion if appropriate (e.g., data points animating in sequence with narration). Add captions (accessibility requirement). |
| **Output** | MP4 video file in `course-content/staging/` |
| **Tool** | Manual assembly (Descript, CapCut, or similar) — `assembly-coordinator` agent is planned but not built |
| **Status** | MANUAL STEP — requires Juan or manual tool use |

**CHECKPOINT GATE 4** — Juan reviews assembled video for sync, pacing, caption accuracy, overall quality.

### Stage 5: Quality Review

| Field | Value |
|-------|-------|
| **Specialist** | `quality-reviewer` |
| **Input** | Assembled video from Stage 4 |
| **Action** | Validate against style bible (full rubric), check Bloom's alignment to CLO #2 (Analyze level), verify accessibility (captions, contrast, color independence), confirm asset-lesson pairing. |
| **Output** | Quality assessment report |
| **Tool** | Marcus performs initial QA (quality-reviewer agent is planned but not built) |
| **Status** | Marcus handles QA manually for this test run |

**FINAL CHECKPOINT** — Quality sign-off. If passed, asset moves from staging to production-ready.

---

## 5. Platform Allocation

Per the Canvas + CourseArc Platform Allocation Policy:

| Decision Factor | Assessment | Platform |
|-----------------|-----------|----------|
| Requires grading? | No — this is embedded instructional content | Not Canvas-graded |
| Requires peer interaction? | No | Not Canvas discussion |
| Needs polished narrative control? | Yes — data storytelling with tight flow | **CourseArc** (optimal) |
| Media-rich with embedded video? | Yes | **CourseArc** (optimal) |
| WCAG 2.1 compliance critical? | Yes | **CourseArc** (built-in) |

**Recommendation:** Embed this video within a CourseArc lesson page, launched from the Canvas Module 1 structure (Integration Pattern 1: Canvas Module → CourseArc Lesson).

---

## 6. Dependency Map

```
Stage 1: Script Review ──────────────────┐
                                         │
                                    [Gate 1: Script Approval]
                                         │
                          ┌──────────────┴──────────────┐
                          │                             │
                  Stage 2: Data Viz              Stage 3: Voiceover
                  (Gamma API)                    (ElevenLabs API)
                          │                             │
                   [Gate 2: Visual]            [Gate 3: Audio]
                          │                             │
                          └──────────────┬──────────────┘
                                         │
                                  Stage 4: Assembly
                                  (Manual — Descript/CapCut)
                                         │
                                   [Gate 4: Video Review]
                                         │
                                  Stage 5: Quality Review
                                  (Marcus — manual QA)
                                         │
                                  [Final Checkpoint]
                                         │
                                   ✓ Production Complete
```

**Parallelization opportunity:** Stages 2 and 3 can run in parallel after Gate 1 approval — the data visualization and voiceover have no dependency on each other.

---

## 7. Current Constraints & Workarounds

| Constraint | Impact | Workaround |
|-----------|--------|-----------|
| `gamma-specialist` agent not built | Cannot auto-delegate slide generation | Marcus invokes Gamma API directly or provides prompt for manual generation |
| `elevenlabs-specialist` agent not built | Cannot auto-delegate voiceover | Marcus invokes ElevenLabs API directly or provides parameters for manual generation |
| `assembly-coordinator` agent not built | Cannot automate video assembly | Manual step — Juan assembles in Descript, CapCut, or similar |
| `quality-reviewer` agent not built | No automated QA pipeline | Marcus performs manual quality review against style bible checklist |
| Voice selection not yet decided | Cannot proceed to Stage 3 without voice choice | Present voice options at Gate 1 for Juan's decision |

---

## 8. Estimated Effort

| Stage | Automated | Manual | Elapsed Time |
|-------|-----------|--------|-------------|
| Script review | Marcus | Juan reviews | ~10 min |
| Data visualization | Gamma API | Juan reviews | ~15 min |
| Voiceover | ElevenLabs API | Juan reviews | ~10 min |
| Video assembly | — | Juan produces | ~30 min |
| Quality review | Marcus | Juan approves | ~10 min |
| **Total** | | | **~75 min** |

---

## 9. Success Criteria

- [ ] Video is 55–90 seconds in length
- [ ] Data visualization uses JCPH Navy background, teal/white data colors, Source Sans Pro labels
- [ ] Voiceover is professional, authoritative, moderate pace — appropriate for physician audience
- [ ] All data points are factually accurate (CMS NHE, AMA Practice Ownership)
- [ ] WCAG 2.1 AA contrast ratios met
- [ ] Captions are accurate and synchronized
- [ ] Asset is paired with C1-M1 Part 2 lesson context and traces to CLO #2
- [ ] Platform allocation documented (CourseArc embed via Canvas Module)
