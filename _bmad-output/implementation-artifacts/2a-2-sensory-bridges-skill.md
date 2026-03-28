# Story 2A-2: Sensory Bridges Skill

Status: ready-for-dev

## Story

As any agent in the APP pipeline,
I want shared sensory bridge scripts that convert multimodal artifacts (images, audio, PDF, PPTX, video) into structured agent-interpretable representations with a canonical request/response schema,
So that I can perceive and verify artifacts I could not otherwise interpret, with confirmed interpretation and calibrated confidence.

## Background & Motivation

The fidelity audit (Story 2A-1) established that the APP is perception-blind for audio and video, perception-unconfirmed for images, and has no canonical schema for multimodal interpretation. Agents consume artifacts they cannot verify — Irene writes narration for slides she hasn't seen, no agent can hear audio output, and no agent can watch composed video. This story builds the shared perception infrastructure that the Fidelity Assessor (Story 2A-4) and all pipeline agents depend on.

**Key architectural decision:** PPTX extraction is the primary deterministic path for G3 text verification (exact text objects from slide data). PNG vision is supplementary for layout and visual assessment. This follows the Hourglass principle — use deterministic extraction through the narrow neck, reserve agentic interpretation for visual judgment.

## Acceptance Criteria

### Skill Structure

1. `skills/sensory-bridges/SKILL.md` exists with modality inventory, invocation patterns, and references
2. `skills/sensory-bridges/references/` contains perception-schema.md, perception-protocol.md, confidence-rubric.md, validator-handoff.md
3. `skills/sensory-bridges/scripts/` contains all bridge scripts with shared utilities

### Canonical Perception Schema (perception-schema.md)

4. A request schema is defined: `{ artifact_path, modality (image|audio|pdf|pptx|video), gate, requesting_agent, purpose }`
5. A response schema is defined per modality:
   - **Common fields:** `modality`, `artifact_path`, `confidence` (HIGH|MEDIUM|LOW), `confidence_rationale`, `perception_timestamp`
   - **Image:** `extracted_text`, `layout_description`, `visual_elements[]`, `slide_title`, `text_blocks[]`
   - **Audio:** `transcript_text`, `timestamped_words[]`, `total_duration_ms`, `wpm`, `pronunciation_flags[]`
   - **PDF:** `pages[]` (page_number + text + image_paths[] + is_scanned), `total_pages`
   - **PPTX:** `slides[]` (slide_number + text_frames[] + image_refs[] + notes), `total_slides`
   - **Video:** `keyframes[]` (timestamp_ms + frame_path), `audio_transcript`, `total_duration_ms`, `scene_changes[]`
6. All bridge scripts accept and return this schema — no free-form output
7. Response schema is JSON-serializable and includes a `schema_version` field

### Image Bridge (png_to_agent.py)

8. Given a PNG or JPG file path, produces structured output with `extracted_text`, `layout_description`, `visual_elements[]`, and `confidence`
9. Uses LLM vision (Claude) for text extraction and layout analysis
10. Returns JSON conforming to the perception schema
11. Unit tests verify output structure against known slide PNGs

### Audio Bridge (audio_to_agent.py)

12. Given an MP3 or WAV file path, produces a timestamped transcript with `transcript_text`, `timestamped_words[]`, `total_duration_ms`, `wpm`, and `confidence`
13. Uses ElevenLabs STT API (preferred) or local Whisper as fallback
14. STT method is added to `ElevenLabsClient` if ElevenLabs API supports it; otherwise Whisper is used via subprocess
15. Returns JSON conforming to the perception schema
16. Unit tests verify output structure (mocked STT for unit tests; live test optional)

### PDF Bridge (pdf_to_agent.py)

17. Given a PDF file path, extracts text content page-by-page and embedded images as separate PNG files
18. Uses `pypdf` (already in requirements) for text extraction
19. Detects scanned/OCR-only pages via text content length heuristic (< 50 chars per page = likely scanned)
20. Returns JSON conforming to the perception schema with `is_scanned` flag per page
21. Unit tests verify extraction against a known PDF

### PPTX Bridge (pptx_to_agent.py)

22. Given a PPTX file path, extracts per-slide text frames, image references, and speaker notes
23. Uses `python-pptx` library (add to requirements.txt)
24. Returns JSON conforming to the perception schema: `slides[]` with `slide_number`, `text_frames[]` (exact text strings from shape objects), `image_refs[]` (image file references), `notes` (speaker notes text)
25. This is the **primary deterministic path for G3 text verification** — exact text objects, not OCR
26. Unit tests verify extraction against a known PPTX export from Gamma

### Video Bridge (video_to_agent.py)

27. Given an MP4 or WebM file path, extracts keyframe images at scene changes and transcribes the audio channel
28. Uses `ffmpeg` subprocess for frame extraction and audio channel separation
29. Audio channel is passed to the audio bridge for transcription
30. Returns JSON conforming to the perception schema: `keyframes[]`, `audio_transcript`, `total_duration_ms`, `scene_changes[]`
31. Unit tests verify frame extraction and audio separation (mocked ffmpeg for unit tests)

### Confidence Calibration Rubric (confidence-rubric.md)

32. Modality-specific calibration rubric defines operational meaning of HIGH, MEDIUM, LOW:
    - **Image:** HIGH (≥95% OCR confidence, layout unambiguous), MEDIUM (80-95% OR layout ambiguous), LOW (<80% OR unparseable)
    - **Audio:** HIGH (WER <5%, no unintelligible segments), MEDIUM (WER 5-15% OR unintelligible <3s), LOW (WER >15% OR heavy noise)
    - **PDF:** HIGH (all pages machine-readable), MEDIUM (≥1 scanned page with OCR), LOW (unreadable pages)
    - **PPTX:** HIGH (all text frames extracted, valid structure), MEDIUM (≥1 corrupt shape or unreadable element), LOW (file corrupt or unparseable)
    - **Video:** HIGH (keyframes extracted + audio transcribed), MEDIUM (partial extraction), LOW (corrupt or unprocessable)
33. Thresholds are configurable per production mode (ad-hoc accepts MEDIUM where production requires HIGH)

### Universal Perception Protocol (perception-protocol.md)

34. Five-step protocol documented: Receive → Perceive (invoke bridge) → Confirm (state interpretation with confidence per rubric) → Proceed (if confidence ≥ threshold) → Escalate (if confidence < threshold)
35. Protocol includes the confirmation output format agents must use when stating their perception
36. Protocol is referenced as a skill reference consumable by all agents

### Validator Integration (validator-handoff.md)

37. Documents how sensory bridge outputs feed into BOTH the Fidelity Assessor and Quinn-R's validators
38. Specifies that bridge outputs complement (not replace) Quinn-R's existing `accessibility_checker.py` and `brand_validator.py`
39. Defines the handoff contract: which fields each consumer reads from the perception response

### Dependencies

40. `python-pptx` added to `requirements.txt`
41. `ffmpeg` availability check added to the video bridge (graceful failure if not installed)
42. No new API keys required — image bridge uses native LLM vision, audio bridge uses existing ElevenLabs key or local Whisper

## Tasks / Subtasks

- [ ] Task 1: Create skill directory structure and reference documents (AC: #1, #2, #4, #5, #6, #7)
  - [ ] 1.1 Create `skills/sensory-bridges/SKILL.md` with modality inventory and invocation patterns
  - [ ] 1.2 Create `skills/sensory-bridges/references/perception-schema.md` with canonical request/response schemas
  - [ ] 1.3 Create shared utilities module `skills/sensory-bridges/scripts/bridge_utils.py` (schema validation, confidence scoring, JSON serialization)

- [ ] Task 2: Implement PPTX bridge (AC: #22, #23, #24, #25, #26)
  - [ ] 2.1 Add `python-pptx` to `requirements.txt` (AC: #40)
  - [ ] 2.2 Create `skills/sensory-bridges/scripts/pptx_to_agent.py` — extract text frames, image refs, notes per slide
  - [ ] 2.3 Write unit tests `skills/sensory-bridges/scripts/tests/test_pptx_to_agent.py`

- [ ] Task 3: Implement image bridge (AC: #8, #9, #10, #11)
  - [ ] 3.1 Create `skills/sensory-bridges/scripts/png_to_agent.py` — LLM vision analysis with structured output
  - [ ] 3.2 Write unit tests `skills/sensory-bridges/scripts/tests/test_png_to_agent.py`

- [ ] Task 4: Implement PDF bridge (AC: #17, #18, #19, #20, #21)
  - [ ] 4.1 Create `skills/sensory-bridges/scripts/pdf_to_agent.py` — page-by-page text + image extraction + scanned detection
  - [ ] 4.2 Write unit tests `skills/sensory-bridges/scripts/tests/test_pdf_to_agent.py`

- [ ] Task 5: Implement audio bridge (AC: #12, #13, #14, #15, #16)
  - [ ] 5.1 Research ElevenLabs STT API availability; if available, add `speech_to_text()` method to `ElevenLabsClient`
  - [ ] 5.2 Create `skills/sensory-bridges/scripts/audio_to_agent.py` — STT transcription with timestamps
  - [ ] 5.3 Write unit tests `skills/sensory-bridges/scripts/tests/test_audio_to_agent.py`

- [ ] Task 6: Implement video bridge (AC: #27, #28, #29, #30, #31)
  - [ ] 6.1 Create `skills/sensory-bridges/scripts/video_to_agent.py` — ffmpeg frame extraction + audio bridge delegation
  - [ ] 6.2 Write unit tests `skills/sensory-bridges/scripts/tests/test_video_to_agent.py`

- [ ] Task 7: Create remaining reference documents (AC: #32, #33, #34, #35, #36, #37, #38, #39)
  - [ ] 7.1 Create `skills/sensory-bridges/references/confidence-rubric.md`
  - [ ] 7.2 Create `skills/sensory-bridges/references/perception-protocol.md`
  - [ ] 7.3 Create `skills/sensory-bridges/references/validator-handoff.md`

- [ ] Task 8: Validate and complete (AC: #40, #41, #42)
  - [ ] 8.1 Run all sensory bridge unit tests — all pass
  - [ ] 8.2 Run existing project tests — no regressions
  - [ ] 8.3 Verify all bridge scripts accept request schema and return response schema
  - [ ] 8.4 Update sprint-status.yaml

## Dev Notes

### Design Direction

- **PPTX bridge is the highest-value deliverable** for G3 verification. It provides deterministic text extraction (exact strings from slide objects) without OCR confidence issues. Implement first.
- **Image bridge** uses native LLM vision capability. In Cursor, the Read tool can read images. The bridge wraps this capability in the canonical schema. For unit testing, mock the LLM vision call and test schema conformance.
- **Audio bridge** depends on STT availability. ElevenLabs has STT API — check docs via Ref MCP. If not available or not cost-effective, fall back to local Whisper (`openai-whisper` package or `whisper.cpp` subprocess).
- **Video bridge** delegates to ffmpeg (subprocess) for frame extraction and to the audio bridge for transcription. This is a composition of existing tools, not new AI capability.
- **PDF bridge** reuses `pypdf` already in requirements. The source wrangler's `source_wrangler_operations.py` already has PDF extraction — factor shared logic if appropriate (DRY).

### Existing Infrastructure To Reuse

| Component | Location | Reuse For |
|-----------|----------|-----------|
| pypdf dependency | `requirements.txt` | PDF bridge — already available |
| PDF extraction logic | `skills/source-wrangler/scripts/source_wrangler_operations.py` | PDF bridge — may share extraction utility |
| ElevenLabs client | `scripts/api_clients/elevenlabs_client.py` | Audio bridge — add STT method if API supports it |
| Base API client | `scripts/api_clients/base_client.py` | Audio bridge — HTTP patterns for STT API |
| L1 contracts | `state/config/fidelity-contracts/` | Verify bridge output fields match contract `requires_perception` + `perception_modality` |

### File Structure (Expected Output)

```
skills/sensory-bridges/
├── SKILL.md
├── references/
│   ├── perception-schema.md
│   ├── perception-protocol.md
│   ├── confidence-rubric.md
│   └── validator-handoff.md
└── scripts/
    ├── bridge_utils.py
    ├── png_to_agent.py
    ├── audio_to_agent.py
    ├── pdf_to_agent.py
    ├── pptx_to_agent.py
    ├── video_to_agent.py
    └── tests/
        ├── test_png_to_agent.py
        ├── test_audio_to_agent.py
        ├── test_pdf_to_agent.py
        ├── test_pptx_to_agent.py
        └── test_video_to_agent.py
```

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

### Change Log
