# Story 3.3: Kling Video Specialist Agent & API Client

> **Historical note (2026-04-16):** Paths of the form `<old>-specialist-sidecar/` and `bmad-agent-marcus-sidecar/` were renamed to persona-named sidecars. See `_bmad/memory/` for current paths.

Status: done

## Story

As a user,
I want a Kling video production specialist agent with AI video generation mastery,
so that professional B-roll, concept visualizations, slide-to-video transitions, and educational video clips are generated programmatically for course content.

## Acceptance Criteria

1. `scripts/api_clients/kling_client.py` extends `BaseAPIClient` with text-to-video, image-to-video, task polling, download, extend, and lip-sync methods
2. The client handles Kling's async task model (submit → poll → download) following the GammaClient pattern
3. `skills/bmad-agent-kling/SKILL.md` exists with "Video Director" persona and Kling API parameter mastery
4. `skills/kling-video/SKILL.md` provides video generation capability routing to the API client
5. `skills/kling-video/references/prompt-patterns.md` documents effective prompts for educational video types
6. `skills/kling-video/references/model-selection.md` documents model tradeoffs (O1 vs 2.6 Pro vs 3.0 vs O3)
7. `skills/kling-video/scripts/` imports and orchestrates `scripts/api_clients/kling_client.py`
8. The agent produces 6 sample videos exercising different API capabilities for human review
9. Sample videos are staged in `course-content/staging/` for human review
10. `_bmad/memory/kling-specialist-sidecar/` is initialized with index.md, patterns.md, chronology.md, and access-boundaries.md
11. Integration tests in `tests/test_integration_kling.py` validate client methods against live API
12. Party Mode team reviews completed agent structure for accuracy and completeness
13. Human review (Juan) confirms sample videos meet quality standards for educational video production

## Tasks / Subtasks

- [ ] Task 1: Build Kling API Client (AC: #1, #2, #11)
  - [ ] 1.1 Create `scripts/api_clients/kling_client.py` extending `BaseAPIClient`
  - [ ] 1.2 Implement `text_to_video()` — POST to text-to-video endpoint with all parameters
  - [ ] 1.3 Implement `image_to_video()` — POST with image URL, prompt, duration, end_image support
  - [ ] 1.4 Implement `lip_sync()` — POST with video URL and audio URL
  - [ ] 1.5 Implement `extend_video()` — POST to extend existing video
  - [ ] 1.6 Implement `get_task_status()` — GET task status by task_id
  - [ ] 1.7 Implement `wait_for_completion()` — poll until SUCCESS/FAILED (same pattern as GammaClient)
  - [ ] 1.8 Implement `download_video()` — retrieve MP4 from CDN URL to local path
  - [ ] 1.9 Add `KLING_API_KEY` to `.env` and `.env.example`
  - [ ] 1.10 Create `tests/test_integration_kling.py` with live API tests

- [ ] Task 2: Party Mode coaching for Kling agent (AC: #3)
  - [ ] 2.1 Run Party Mode coaching to produce bmad-agent-builder discovery answers
  - [ ] 2.2 Save to `_bmad-output/brainstorming/party-mode-coaching-kling-specialist.md`

- [ ] Task 3: Create Kling Video Director agent via bmad-agent-builder (AC: #3)
  - [ ] 3.1 Run bmad-agent-builder six-phase discovery with coached answers
  - [ ] 3.2 Output: `skills/bmad-agent-kling/SKILL.md` with Video Director persona
  - [ ] 3.3 Follow Marcus/Gary/Irene SKILL.md pattern
  - [ ] 3.4 Internal capabilities: video prompt engineering (VP), shot composition (SC), model selection (MS), video quality assessment (VQ), content type mapping (CT)
  - [ ] 3.5 External skill: `kling-video` for API operations

- [ ] Task 4: Create kling-video mastery skill (AC: #4, #5, #6, #7)
  - [ ] 4.1 Create `skills/kling-video/SKILL.md` with routing and invocation
  - [ ] 4.2 Create `skills/kling-video/references/prompt-patterns.md` — effective prompts per video type
  - [ ] 4.3 Create `skills/kling-video/references/model-selection.md` — model tradeoffs and recommendations
  - [ ] 4.4 Create `skills/kling-video/references/parameter-catalog.md` — complete API parameter space
  - [ ] 4.5 Create `skills/kling-video/scripts/kling_operations.py` — agent-level wrapper around KlingClient
  - [ ] 4.6 Create `skills/kling-video/scripts/tests/test_kling_operations.py`

- [ ] Task 5: Initialize memory sidecar (AC: #10)
  - [ ] 5.1 Create `_bmad/memory/kling-specialist-sidecar/` with 4 files

- [ ] Task 6: Produce 6 sample videos for human review (AC: #8, #9, #13)
  - [ ] 6.1 V1: Hospital B-roll — text-to-video, 10s, pro mode, cinematic medical aesthetic
  - [ ] 6.2 V2: Concept animation — clinical pathway diverging into innovator pathway, 5s
  - [ ] 6.3 V3: Slide-to-video transition — animate a Gary-produced slide PNG, 5s
  - [ ] 6.4 V4: Knowledge explosion timeline — 50 years → 73 days visualization, 5s
  - [ ] 6.5 V5: Talking-head overlay — lip-synced narration (requires image + audio)
  - [ ] 6.6 V6: Module bridge transition — animated graphic with native audio, 5s
  - [ ] 6.7 Stage all videos in `course-content/staging/story-3.3-samples/`
  - [ ] 6.8 Human review checkpoint: Juan confirms video quality

- [ ] Task 7: Register agent with Marcus (AC: #3)
  - [ ] 7.1 Update Marcus SKILL.md External Specialist Agents: add kling-specialist → active

- [ ] Task 8: Party Mode validation (AC: #12)
  - [ ] 8.1 Run Party Mode review of completed agent + skill + API client + sample videos

## Dev Notes

### API Client: Follow GammaClient Pattern

`scripts/api_clients/kling_client.py` extends `BaseAPIClient`. Two potential API surfaces exist:

**Official Kling API** ([klingapi.com/docs](https://klingapi.com/docs)):
- Base URL: `https://api.klingapi.com`
- Auth: `Authorization: Bearer {API_KEY}`
- Endpoints: `/v1/videos/text2video`, `/v1/videos/image2video`, `/v1/videos/{task_id}`, `/v1/videos/extend`, `/v1/videos/lip-sync`
- Models: `kling-video-o1`, `kling-v2.6-pro`, `kling-v2.6-std`, `kling-v2.5-turbo`

**Kling 3.0 / O3 API** ([kling3api.com/docs](https://kling3api.com/docs)):
- Base URL: `https://kling3api.com`
- Single unified endpoint: `POST /api/generate` with `type` field routing
- Status: `GET /api/status?task_id={id}`
- Types: `pro-text-to-video`, `pro-image-to-video`, `o3-pro-reference-to-video`, `o3-pro-video-edit`
- 4K output, physics simulation, multi-shot intelligence

**Decision needed:** Determine which API surface to target based on available credentials. The official API has more endpoints (lip-sync, extend). The 3.0 API has newer models (4K, O3 video edit). The client should support the official API as primary with methods that map cleanly. Research during implementation which credentials the user has.

**Async pattern** (identical to GammaClient):
```
1. POST generate request → get task_id
2. Poll GET status → IN_PROGRESS / SUCCESS / FAILED
3. On SUCCESS → extract video URL from response
4. Download MP4 to local path
```

### Key Parameters

| Parameter | Type | Notes |
|-----------|------|-------|
| `model` | string | Model selection: O1, 2.6-pro, 2.6-std, 2.5-turbo, 3.0 |
| `prompt` | string | Max 2000 chars, detailed scene description |
| `duration` | number | 3-15 seconds (3.0), 5-10 (older models) |
| `aspect_ratio` | string | 16:9, 9:16, 1:1 (default 16:9) |
| `mode` | string | standard (720p) or professional (1080p) |
| `negative_prompt` | string | Elements to exclude |
| `sound` | boolean | Native audio generation (default true for 2.6+) |
| `cfg_scale` | number | Prompt adherence 0-1 (3.0 only) |
| `image` | string | Image URL for image-to-video |
| `end_image` | string | End frame for interpolation |
| `multi_shot` | string | `"intelligence"` for auto multi-shot segmentation |

### 6 Sample Videos — Content from C1-M1 Course Notes

The test videos use real content from `course-content/courses/TEJAL_Course 01 Mod 01 Notes 2026-03-16.pdf` and Irene's sample artifacts, exercising different Kling capabilities. The evaluation strategy now uses two tiers:
- **Baseline tier:** `kling-v2-6`, `std`, sound off, `5s`
- **Comparison tier:** `kling-v2-6`, `pro`, `5s`

This decision is based on observed billing data: `kling-v2-6 std sound off 5s` billed cheaper than the earlier `kling-v1-6 std 5s` baseline while still representing a stronger modern default.

| # | Video | Kling Capability | Duration | Content Source |
|---|-------|-----------------|----------|---------------|
| V1 | Hospital B-roll — busy corridor, physician at EHR, soft light, medical blue palette | `text-to-video` | 5s | C1-M1 Slide 1 video prompt |
| V2 | Concept animation — clinical pathway diverging into innovator pathway | `text-to-video` | 5s | C1-M1 Slide 1 animation overlay |
| V3 | Hero's Journey roadmap animation | `text-to-video` | 5s | C1-M1 Slide 2 roadmap prompt |
| V4 | Knowledge explosion timeline — 50 years → 73 days doubling visualization | `text-to-video` | 5s | C1-M1 Part 2 Slide 3 |
| V5 | Physician innovator lineage montage | `text-to-video` | 5s | C1-M1 Slide 3 innovation lineage |
| V6 | Module bridge — Module 1 to Module 2 transition with optional native ambient audio | `text-to-video` | 5s | C1-M1 Summary & Bridge slide |

**Prompts derived from C1-M1 notes:**

**V1 prompt:** "Cinematic 4K video of a modern hospital environment. Scene 1: A physician looking thoughtfully at a computer screen, soft natural light, shallow depth of field. Scene 2: High-quality B-roll of a busy nursing station, fast-paced but professional. Color grading: slightly cool, medical blues and clean whites, conveying urgency but professionalism."

**V2 prompt:** "A clean animation on dark navy background showing a traditional clinical pathway (straight line with medical cross icons) that diverges into two paths at a decision point. The upper path continues straight (labeled 'Clinical Reactor' in subtle text). The lower path curves upward into a dynamic, branching innovator pathway with glowing teal nodes. Smooth, professional motion design, healthcare color palette of navy blue and bright teal."

**V4 prompt:** "A minimalist, data-driven animation showing the acceleration of medical knowledge doubling. Starting with a timeline bar labeled '1950: 50 years to double', it smoothly compresses through decades, accelerating visually until reaching '2026: 73 days'. The compression should feel exponential — slow at first, then increasingly rapid. Clean sans-serif typography on dark background, teal accent color for data points."

### Audio / Lip-Sync Design Note (defer major decision to Story 3.4)

For this Story 3.3 validation slice, the six sample videos are evaluated primarily on **visual design quality**, motion clarity, educational usefulness, and professional medical aesthetic. Kling-native audio may be used sparingly for ambient sound or subtle supporting audio where it naturally fits the depicted environment.

**Important deferred platform decision:** the broader production architecture for audio-in-video remains open and should be resolved around Story 3.4 (ElevenLabs) with a dedicated Party Mode discussion. Questions to settle later:
- When should audio be generated natively in Kling versus separately in ElevenLabs?
- When should SFX or light music be introduced in Kling versus later in editing tools?
- Should narration be composed later in CapCut or another editor after ElevenLabs synthesis?
- Should final lip-sync and compositing happen in Kling, Descript, CapCut, or another downstream editor?

Until that decision is made, Story 3.3 should treat **lip-sync as a supported capability of the API/client**, but not a mandatory acceptance gate for the initial six-video validation set.

### Agent Pattern: Follow Gary (Specialist Agent)

The Kling agent follows the same pattern as Gary (Gamma Specialist):
- Headless primary (Marcus delegation via context envelope)
- Interactive secondary (for video experiments and prompt debugging)
- Context envelope inbound/outbound contract
- Memory sidecar with learned prompt patterns
- Quality self-assessment on generated videos

Key difference from Gary: **no exemplar/woodshed validation**. Videos are validated through human review of 6 sample productions, not exemplar reproduction. This is because video output is inherently more variable than slide output — there's no "faithful reproduction" test for generated video.

### Existing Infrastructure to Reuse (DO NOT REINVENT)

| Component | Location | Reuse For |
|-----------|----------|-----------|
| `BaseAPIClient` | `scripts/api_clients/base_client.py` | Extend for Kling (auth, retry, polling pattern) |
| `GammaClient` | `scripts/api_clients/gamma_client.py` | Pattern template for async task model |
| Marcus SKILL.md | `skills/bmad-agent-marcus/SKILL.md` | Agent structure template |
| Gary SKILL.md | `skills/bmad-agent-gamma/SKILL.md` | Specialist agent pattern |
| `gamma-api-mastery` | `skills/gamma-api-mastery/` | Mastery skill structure template |
| Memory sidecar pattern | `_bmad/memory/gamma-specialist-sidecar/` | 4-file sidecar |
| Content Creator artifacts | `course-content/staging/story-3.2-samples/` | Input for V3 (slide brief → Gary PNG → Kling) and V5 (narration → ElevenLabs audio → Kling lip sync) |
| C1-M1 course notes | `course-content/courses/TEJAL_Course 01 Mod 01 Notes 2026-03-16.pdf` | Video prompts and content context |

### File Structure (Expected Output)

```
scripts/api_clients/
└── kling_client.py                        # API client extending BaseAPIClient

skills/
├── bmad-agent-kling/
│   ├── SKILL.md                           # Video Director agent
│   └── references/
│       ├── init.md
│       ├── memory-system.md
│       ├── save-memory.md
│       ├── video-prompt-engineering.md     # Shot composition + prompt craft
│       ├── content-type-mapping.md         # Educational video types → params
│       └── context-envelope-schema.md      # Marcus delegation contract
│
├── kling-video/
│   ├── SKILL.md                           # Mastery skill routing
│   ├── references/
│   │   ├── prompt-patterns.md             # Effective prompts per video type
│   │   ├── model-selection.md             # Model tradeoffs
│   │   └── parameter-catalog.md           # Complete API parameter space
│   └── scripts/
│       ├── kling_operations.py            # Agent-level KlingClient wrapper
│       └── tests/
│           └── test_kling_operations.py

tests/
└── test_integration_kling.py              # Live API integration tests

_bmad/memory/
└── kling-specialist-sidecar/              # 4 files
    ├── index.md
    ├── patterns.md
    ├── chronology.md
    └── access-boundaries.md

course-content/staging/story-3.3-samples/  # 6 MP4 video files
```

### Testing Standards

- `test_integration_kling.py` tests against live API with `KLING_API_KEY` from `.env`
- Skip tests gracefully if credentials not available (`pytest.mark.skipif`)
- `test_kling_operations.py` mocks `KlingClient` for unit tests
- Keep integration tests read-only where possible (generate short 3s videos to minimize credit usage)
- Download and retain all generated videos for review

### Anti-Patterns to Avoid

- Do NOT hardcode API endpoints — parameterize base URL for API surface flexibility
- Do NOT skip the download step — CDN URLs expire, download immediately on completion
- Do NOT generate long videos in tests — use 3s duration for credit efficiency
- Do NOT place agent files in `agents/` — follow `skills/bmad-agent-{name}/` convention
- Do NOT duplicate GammaClient polling logic — extract shared async pattern if possible
- Do NOT generate videos without negative_prompt for medical content — always exclude "text overlays, watermarks, cartoon style" unless specifically desired

### Key Lessons from Stories 3.1 + 3.2 (Apply Here)

1. **Guide the tool, don't suppress it.** Rich prompts describing the desired visual outcome work better than restrictive constraints. Kling's strength is cinematic generation — work with it.
2. **Separate agent concerns.** Video Director owns shot composition and model selection. Irene owns the content design that feeds the prompts. Quinn-R validates the final output.
3. **Memory sidecar `patterns.md` grows from user checkpoint reviews** — which prompts, models, and durations produce approved results for which content types.
4. **Export and download immediately.** Video CDN URLs expire. Download to local storage on completion (same discipline as Gary's PDF exports).
5. **Cost awareness.** Video generation costs credits per second. Model selection intelligence should consider cost/quality tradeoffs. Pro for hero content, standard for B-roll.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 3.3] — Epic definition with discovery answers and ACs
- [Source: _bmad-output/implementation-artifacts/3-1-gamma-specialist-agent.md] — Gary creation pattern
- [Source: _bmad-output/implementation-artifacts/3-2-content-creator-quality-reviewer-agents.md] — Irene/Quinn-R pattern
- [Source: scripts/api_clients/gamma_client.py] — GammaClient async pattern template
- [Source: scripts/api_clients/base_client.py] — BaseAPIClient extension pattern
- [Source: course-content/courses/TEJAL_Course 01 Mod 01 Notes 2026-03-16.pdf] — C1-M1 video prompts
- [Source: course-content/staging/story-3.2-samples/] — Content Creator sample artifacts
- [API: klingapi.com/docs] — Official Kling API reference
- [API: kling3api.com/docs] — Kling 3.0/O3 API reference
- [API: klingapi.com/features] — Full capability list

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
