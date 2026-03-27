# Party Mode: ElevenLabs Capability Audit & Instructional Artifact Brainstorm

**Session Date:** March 26, 2026  
**Purpose:** Study ElevenLabs API surface beyond TTS; identify instructional artifacts, exemplars, and raw materials  
**Team:** Winston (Architect), Mary (Analyst), John (PM), Sally (UX), Caravaggio (Presentation), Sophia (Storyteller), Carson (Brainstorming), Quinn (QA), Bob (SM)  
**Source:** [ElevenLabs API Reference](https://elevenlabs.io/docs/api-reference/introduction)

---

## ElevenLabs Full API Surface (Winston)

| API Capability | Endpoint Category | API Maturity | Relevance to Our Work |
|---|---|---|---|
| **Text to Speech** | `/v1/text-to-speech/{voice_id}` | Production | **Core** — narration, voiceovers |
| **TTS with Timestamps** | `/v1/text-to-speech/{voice_id}/with-timestamps` | Production | **Critical** — slide sync, subtitle generation |
| **Speech to Speech** | Voice transformation | Production | Medium — voice style transfer |
| **Sound Effects** | Text-to-SFX | Production | **High** — transitions, ambient, emphasis |
| **Music Generation** | Eleven Music API | Production | Medium — intros, outros, background |
| **Dubbing** | `/v1/dubbing` | Production (Enterprise for segments) | **High** — multilingual course versions |
| **Audio Isolation** | `/v1/audio-isolation` | Production | Medium — cleaning source audio |
| **Voice Design** | Text-to-voice-creation | Production | Medium — custom course voices |
| **Voice Cloning (IVC)** | Instant voice clone | Production | **High** — instructor voice |
| **Pronunciation Dictionaries** | CRUD + rules | Production | **Critical** — medical terminology |
| **Conversational AI (ElevenAgents)** | Agent workflows | Production | **Speculative** — interactive tutoring |
| **Text to Dialogue** | Multi-speaker generation | Production | **High** — case study scenarios |
| **Voice Remixing** | Voice attribute modification | Production | Low — edge case |
| **Forced Alignment** | Audio + text → timestamps | Production | **High** — transcript alignment |
| **Transcription (STT)** | Speech to text | Production | Medium — QA verification |

Existing `elevenlabs_client.py` covers only TTS + voices + models. API surface is ~5x what's currently wrapped.

---

## Instructional Artifact Categories (Mary)

### Artifact 1: Slide Narrations (Voiceovers) — P0
- **API:** `text-to-speech` + `text-to-speech/with-timestamps`
- **Raw materials:** Script text per slide, voice_id, style guide voice params, pronunciation dictionary
- **Exemplar:** 3-5 slide narrated sequence → MP3 files + VTT timing data, including medical terms requiring pronunciation dict

### Artifact 2: Medical Pronunciation — P0
- **API:** Pronunciation Dictionaries (CRUD + rules)
- **Raw materials:** Medical terminology glossary per course domain
- **Exemplar:** 10-20 medical terms with correct phonemes/IPA

### Artifact 3: Multi-Slide Narration Suite — P0
- **API:** TTS with `previous_request_ids` / `next_request_ids` for continuity
- **Raw materials:** Ordered slide scripts with continuity markers
- **Exemplar:** 3-5 slide narration sequence demonstrating request stitching

### Artifact 4: Case Study Dialogue — P1
- **API:** Text to Dialogue (multi-speaker)
- **Raw materials:** Dialogue scripts with speaker labels, voice assignments, tone direction
- **Exemplar:** 60-90s clinical scenario (2-3 speakers), differential diagnosis discussion

### Artifact 5: Sound Effects Package — P2
- **API:** Sound Effects (text-to-SFX, 0.1-30s, looping support)
- **Raw materials:** Sound design brief per content type
- **Exemplar:** Set of 5-8 SFX: intro sting, transition whoosh, emphasis tone, ambient, notification, conclusion sting

### Artifact 6: Background Music — P2
- **API:** Music API
- **Raw materials:** Music brief (tempo, mood, duration)
- **Exemplar:** Intro/outro/ambient samples

### Artifact 7: Voice Clone (Instructor) — P2
- **API:** IVC/PVC
- **Raw materials:** 3-5 min clean instructor recording + consent form
- **Exemplar:** Instructor audio samples

### Artifact 8: Dubbed Translation — P3
- **API:** Dubbing API
- **Raw materials:** Source English audio + target language + medical glossary
- **Exemplar:** English narration → Spanish dub

### Artifact 9: Interactive Audio Quiz — P3
- **API:** TTS + Qualtrics integration
- **Raw materials:** Quiz bank with audio specs, answer key
- **Exemplar:** One audio-enhanced quiz question

### Artifact 10: Conversational AI Tutor — P3 (Epic 5+)
- **API:** ElevenAgents
- **Raw materials:** Patient profile, scenario, evaluation rubric
- **Exemplar:** 2-minute scripted patient interaction

### Artifact 11: Podcast Module Summaries — P3
- **API:** Text to Dialogue
- **Raw materials:** Module summary points, voice profiles, script template
- **Exemplar:** 3-5 min two-voice discussion

### Artifact 12: Audio Annotations — P2
- **API:** TTS (micro-narrations, 5-15s)
- **Raw materials:** Annotated slide scripts with trigger points
- **Exemplar:** Expert commentary clips per slide element

---

## Priority Matrix (John)

| Artifact Type | User Value | API Readiness | Effort | Priority |
|---|---|---|---|---|
| Slide Narrations | 10/10 | 10/10 | Low | **P0** |
| Pronunciation Dictionaries | 9/10 | 9/10 | Low | **P0** |
| Timestamp-synced narration | 9/10 | 9/10 | Medium | **P0** |
| Case Study Dialogues | 8/10 | 8/10 | Medium | **P1** |
| Sound Effects | 6/10 | 8/10 | Low | **P2** |
| Music (intros/outros) | 5/10 | 7/10 | Low | **P2** |
| Dubbing/Translation | 7/10 | 6/10 | High | **P3** |
| Conversational AI Tutors | 9/10 | 8/10 | Very High | **P3 (Epic 5+)** |
| Voice Cloning | 7/10 | 8/10 | Medium | **P2** |
| Audio Isolation | 3/10 | 9/10 | Low | **P3** |

---

## Accessibility Imperative (Sally)

Timestamp-synced narration enables:
1. Auto-generated WebVTT subtitle tracks (ADA/WCAG 2.1 AA)
2. "Click to hear" on individual slide elements
3. Audio-described navigation for visually impaired learners
4. Speed-adjustable playback without losing sync data

Request stitching (`previous_request_ids`/`next_request_ids`) is critical for natural multi-slide flow.

---

## Evaluator Design (Quinn)

### Cheap Quality Signals (automated)
1. Audio duration vs. word count (130-170 WPM for educational)
2. File size sanity (~1MB/min at 128kbps)
3. Silence ratio via STT
4. `x-character-count` response header for cost tracking

### Content Coverage Signals (STT extraction)
1. STT the output → compare transcript vs. source script
2. Word coverage percentage (>95% for faithful narration)
3. Medical term pronunciation verification via STT
4. Continuity check for multi-slide stitched narrations

### Timestamp-Specific Signals
1. Timestamp completeness (every word has start/end)
2. Monotonicity (strictly increasing)
3. Duration consistency (sum ≈ total audio duration)

---

## Exemplar L-Level Proposal (Caravaggio + Bob)

| Level | Description | Capability Proved |
|---|---|---|
| L1 | Single-slide narration: script → MP3 + VTT | Basic TTS + timestamps |
| L2 | Multi-slide narration with request stitching (3-5 slides) | Continuity across segments |
| L3 | Narration + pronunciation dictionary (medical terms) | Terminology mastery |
| L4 | Case study dialogue (multi-speaker) | Multi-voice production |
| L5 | Complete slide deck narration suite (full output set) | Full production capability |

---

## Decision: User Approved Priorities

**P0 (Must-have for Story 3.2):** Artifacts 1, 2, 3  
**P1 (MVP stretch):** Artifacts 4, 5, 6  
**P2-P3:** Deferred to later stories/epics  

**Key dependency identified:** Scripts must exist before narration. Writer/editor agent or capability needed upstream in the pipeline.
