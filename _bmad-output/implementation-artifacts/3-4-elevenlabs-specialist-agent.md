# Story 3.4: ElevenLabs Specialist Agent & Mastery Skill

Status: done

## Story

As a user,
I want an ElevenLabs specialist agent with comprehensive audio production mastery covering narration, pronunciation, sound design, and multi-speaker dialogue,
so that professional audio artifacts are generated with optimal parameters for medical education content.

## Acceptance Criteria

1. `skills/bmad-agent-elevenlabs/SKILL.md` exists with "Voice Director" persona and complete ElevenLabs parameter knowledge across all API capabilities
2. `skills/elevenlabs-audio/SKILL.md` provides audio generation capability routing to the expanded API client
3. `scripts/api_clients/elevenlabs_client.py` includes methods for timestamps, pronunciation dictionaries, sound effects, and dialogue/music support appropriate to the documented API surface
4. `skills/elevenlabs-audio/references/voice-catalog.md` documents available voices with characteristics and suitability for medical content
5. `skills/elevenlabs-audio/references/optimization-patterns.md` contains voice optimization guidance for medical education narration styles
6. `skills/elevenlabs-audio/references/pronunciation-management.md` documents pronunciation dictionary workflow for medical terminology
7. `skills/elevenlabs-audio/references/sound-design-patterns.md` documents SFX and music generation patterns for instructional content
8. `skills/elevenlabs-audio/scripts/` imports and orchestrates the expanded `scripts/api_clients/elevenlabs_client.py`
9. The agent reads style guide voice preferences and applies them automatically
10. Generated narration includes timing metadata sufficient to write paired WebVTT subtitle tracks
11. The client/skill supports multi-slide narration continuity via `previous_request_ids` / `next_request_ids`
12. A pronunciation dictionary workflow with at least 10 medical terms is supported and verified in tests
13. `_bmad/memory/elevenlabs-specialist-sidecar/` is initialized for capturing effective voice configurations
14. At least one ElevenLabs exemplar is registered in `resources/exemplars/elevenlabs/`
15. Automated tests cover the expanded client and skill wrapper behavior, and live validation covers the read-only and core narration paths available in this repo

## Tasks / Subtasks

- [x] Task 1: Expand ElevenLabs API client for Story 3.4 core operations (AC: #3, #10, #11, #12, #15)
  - [x] 1.1 Add timestamped TTS support returning audio + alignment metadata
  - [x] 1.2 Add helper(s) for decoding timestamp responses and writing MP3/VTT artifacts
  - [x] 1.3 Add pronunciation dictionary create/list helpers using documented API shapes
  - [x] 1.4 Add sound effect generation support
  - [x] 1.5 Add dialogue generation support
  - [x] 1.6 Add music generation support using the official `POST /v1/music/stream` endpoint surfaced in current docs
  - [x] 1.7 Add or update automated tests for the new client methods

- [x] Task 2: Create the `elevenlabs-audio` mastery skill (AC: #2, #4, #5, #6, #7, #8, #9, #10, #11, #12, #15)
  - [x] 2.1 Create `skills/elevenlabs-audio/SKILL.md`
  - [x] 2.2 Create `skills/elevenlabs-audio/references/voice-catalog.md`
  - [x] 2.3 Create `skills/elevenlabs-audio/references/optimization-patterns.md`
  - [x] 2.4 Create `skills/elevenlabs-audio/references/pronunciation-management.md`
  - [x] 2.5 Create `skills/elevenlabs-audio/references/sound-design-patterns.md`
  - [x] 2.6 Create `skills/elevenlabs-audio/scripts/elevenlabs_operations.py`
  - [x] 2.7 Create `skills/elevenlabs-audio/scripts/tests/test_elevenlabs_operations.py`

- [x] Task 3: Create the ElevenLabs specialist agent (AC: #1, #9, #13)
  - [x] 3.1 Create `skills/bmad-agent-elevenlabs/SKILL.md` with Voice Director persona
  - [x] 3.2 Create supporting references following the established specialist-agent pattern
  - [x] 3.3 Ensure Marcus-compatible inbound/outbound delegation language and segment-manifest awareness

- [x] Task 4: Initialize memory and exemplar scaffolding (AC: #13, #14)
  - [x] 4.1 Create `_bmad/memory/elevenlabs-specialist-sidecar/` with index, patterns, chronology, and access boundaries
  - [x] 4.2 Register a bootstrap L1 exemplar in `resources/exemplars/elevenlabs/_catalog.yaml`
  - [x] 4.3 Add a minimal repo-owned exemplar brief/source scaffold suitable for later woodshed runs

- [x] Task 5: Validate the Story 3.4 slice end-to-end at the current repo capability level (AC: #10, #11, #12, #15)
  - [x] 5.1 Run targeted automated tests for the client and skill wrapper
  - [x] 5.2 Run existing ElevenLabs live validation plus a focused narration-with-timestamps smoke check
  - [x] 5.3 Update sprint/story records and file lists for review readiness

## Dev Notes

### Party Mode Consensus

- **Implementation order:** P0 vertical slice first: timestamps, pronunciation dictionaries, continuity metadata, mastery skill wrapper, Voice Director agent, tests.
- **Stretch capability handling:** Implement sound effects against the documented endpoint. Implement dialogue against the documented endpoint. Promote music from placeholder to supported capability only if the official docs surface a stable endpoint shape during the story.
- **Exemplar policy:** Do not block on a Juan-supplied exemplar. Ship with a bootstrap repo-owned L1 exemplar scaffold that can later be replaced or supplemented by a human-provided exemplar without changing the ElevenLabs implementation contract.

### Story-Specific Guardrails

- Marcus remains the broker for every handoff. The ElevenLabs specialist does not communicate directly with Irene, Kira, or the compositor in the user-facing model.
- The canonical input artifact is Irene's Pass 2 package: narration script + segment manifest.
- The canonical write-back fields to the manifest are `narration_duration`, `narration_file`, `narration_vtt`, and `sfx_file`.
- `voice_id` may be segment-specific in the manifest; `null` means use the lesson default from the style guide / Marcus context.
- Kira depends on `narration_duration`, so any output contract must make that easy for Marcus to pass onward.
- Avoid inventing undocumented ElevenLabs endpoints or payload fields. Use current official docs for every new method added.

### Existing Infrastructure To Reuse

| Component | Location | Reuse For |
|-----------|----------|-----------|
| `ElevenLabsClient` base implementation | `scripts/api_clients/elevenlabs_client.py` | Expand rather than replace |
| `BaseAPIClient` | `scripts/api_clients/base_client.py` | Auth, retries, error handling |
| Existing live tests | `tests/test_integration_elevenlabs.py` | Extend with safe live checks |
| Style guide defaults | `state/config/style_guide.yaml` | Default voice/model/output settings |
| Segment manifest contract | `skills/bmad-agent-content-creator/references/template-segment-manifest.md` | Canonical ElevenLabs input/output fields |
| Gamma/Kling mastery skill layout | `skills/gamma-api-mastery/`, `skills/kling-video/` | Skill structure and test pattern |
| Specialist agent pattern | `skills/bmad-agent-gamma/SKILL.md`, `skills/bmad-agent-kling/SKILL.md` | Voice Director structure and delegation style |
| ElevenLabs capability audit | `_bmad-output/brainstorming/party-mode-elevenlabs-capability-audit.md` | P0/P1 prioritization and evaluator expectations |

### Current Official API Notes

- `POST /v1/text-to-speech/{voice_id}/with-timestamps` returns JSON with base64 audio and alignment metadata.
- Pronunciation dictionaries are created from `.pls` files via `POST /v1/pronunciation-dictionaries/add-from-file`.
- Sound effects are created via `POST /v1/sound-generation`.
- Dialogue is created via `POST /v1/text-to-dialogue`.
- Official documentation retrieved during this story surfaced `POST /v1/music/stream`; music support is implemented conservatively around that documented endpoint.

### Testing Strategy

- Add unit tests for the expanded ElevenLabs client methods and response parsing.
- Add unit tests for the mastery skill wrapper script using mocked clients and temp paths.
- Keep live tests safe and focused on supported/read-only or low-cost narration paths.
- Prefer a focused timestamps smoke check over broad credit-heavy live validation.

### File Structure (Expected Output)

```
scripts/api_clients/
└── elevenlabs_client.py

skills/
├── bmad-agent-elevenlabs/
│   ├── SKILL.md
│   └── references/
│       ├── init.md
│       ├── memory-system.md
│       ├── save-memory.md
│       ├── audio-direction.md
│       └── context-envelope-schema.md
│
└── elevenlabs-audio/
    ├── SKILL.md
    ├── references/
    │   ├── voice-catalog.md
    │   ├── optimization-patterns.md
    │   ├── pronunciation-management.md
    │   └── sound-design-patterns.md
    └── scripts/
        ├── elevenlabs_operations.py
        └── tests/
            └── test_elevenlabs_operations.py
```

## Dev Agent Record

### Debug Log References

- Party Mode consensus: P0-first slice with documented P1 endpoints and conservative music handling
- ElevenLabs docs loaded for timestamps, pronunciation dictionaries, sound effects, and dialogue
- ElevenLabs docs loaded for music streaming endpoint: `POST /v1/music/stream`
- Focused unit suite: `19 passed`
- Broader regression-focused suite: `57 passed`
- Live timestamp smoke: `voices=45`, `audio_bytes=36824`, `duration_seconds=2.229`, `request_id_present=True`
- Live manifest smoke: `outputs=1`, `duration=3.204`, `audio_exists=True`, `vtt_exists=True`

### Completion Notes List

- Story created directly on `story3-4-elevenlabs-specialist` to proceed immediately into implementation
- Expanded `ElevenLabsClient` with timestamped narration, pronunciation dictionary, dialogue, sound-effect, and music helpers
- Added `elevenlabs-audio` skill wrapper with style-guide loading, VTT generation, and `.pls` authoring
- Added the Voice Director specialist, interaction guide, sidecar, and bootstrap L1 exemplar scaffold
- Removed repo reliance on `.env.example` and aligned tests/docs to the local `.env` policy
- Added manifest-driven narration write-back so Story 3.5 receives populated `narration_duration`, `narration_file`, and `narration_vtt` fields from real code, not just docs

### File List

**Modified:**
- `scripts/api_clients/elevenlabs_client.py`
- `tests/test_integration_elevenlabs.py`
- `skills/bmad-agent-marcus/SKILL.md`
- `docs/dev-guide.md`
- `resources/exemplars/elevenlabs/_catalog.yaml`
- `_bmad/memory/elevenlabs-specialist-sidecar/index.md`

**Created:**
- `_bmad-output/implementation-artifacts/3-4-elevenlabs-specialist-agent.md`
- `tests/test_elevenlabs_client.py`
- `skills/elevenlabs-audio/SKILL.md`
- `skills/elevenlabs-audio/references/voice-catalog.md`
- `skills/elevenlabs-audio/references/optimization-patterns.md`
- `skills/elevenlabs-audio/references/pronunciation-management.md`
- `skills/elevenlabs-audio/references/sound-design-patterns.md`
- `skills/elevenlabs-audio/scripts/elevenlabs_operations.py`
- `skills/elevenlabs-audio/scripts/tests/test_elevenlabs_operations.py`
- `skills/bmad-agent-elevenlabs/SKILL.md`
- `skills/bmad-agent-elevenlabs/references/audio-direction.md`
- `skills/bmad-agent-elevenlabs/references/context-envelope-schema.md`
- `skills/bmad-agent-elevenlabs/references/init.md`
- `skills/bmad-agent-elevenlabs/references/memory-system.md`
- `skills/bmad-agent-elevenlabs/references/save-memory.md`
- `tests/agents/bmad-agent-elevenlabs/interaction-test-guide.md`
- `_bmad/memory/elevenlabs-specialist-sidecar/patterns.md`
- `_bmad/memory/elevenlabs-specialist-sidecar/chronology.md`
- `_bmad/memory/elevenlabs-specialist-sidecar/access-boundaries.md`
- `resources/exemplars/elevenlabs/L1-bootstrap-narrated-slide/brief.md`
- `resources/exemplars/elevenlabs/L1-bootstrap-narrated-slide/source/script-source.md`

### Change Log

- 2026-03-27: Story file created and implementation started on `story3-4-elevenlabs-specialist`
- 2026-03-27: Story implementation completed, validated, and moved to review
