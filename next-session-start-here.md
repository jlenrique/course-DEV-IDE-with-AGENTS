# Next Session Start Here

## Immediate Next Action

**Continue Story 3.3 (Kling Video Specialist) — Tasks 2-8 remaining.**

Task 1 (API client) is DONE: `kling_client.py` built, JWT auth verified, live video generated (5s blue gradient, 1.8MB MP4 downloaded, 2 credits consumed). The full generate → poll → download pipeline works end-to-end.

Remaining tasks:
```
2. Party Mode coaching — produce coached bmad-agent-builder discovery answers
3. bmad-agent-builder — create Video Director agent
4. kling-video mastery skill — references + scripts
5. Memory sidecar — initialize 4 files
6. Produce 6 sample videos — use C1-M1 content, exercise different API capabilities
7. Register with Marcus
8. Party Mode validation
```

**Branch**: `epic3-core-tool-agents`

## Current Status — STORIES 3.1 + 3.2 COMPLETE, STORY 3.3 IN PROGRESS

- **Story 3.3 (Kling Video Specialist)**: IN PROGRESS — API client built (`kling_client.py`), JWT auth working, live video generated + downloaded, 5 unit tests pass. Remaining: agent, skill, sidecar, 6 sample videos, validation.
- **Story 3.2 (Irene + Quinn-R — Content Creator + Quality Reviewer)**: DONE — Irene (12 files), Quinn-R (6 files), quality-control skill (3 scripts, 28 tests), 6 sample artifacts approved, Marcus updated
- **Story 3.1 (Gary — Gamma Specialist)**: DONE — Agent built (10 files), mastery skill (6 files), 29 tests, L1+L2 woodshed PASSED
- **Epic 2**: COMPLETE (6/6 stories, 55 tests)
- **Epic 1**: COMPLETE (11/11 stories, 117 tests)

## What's Working Right Now

### MCP Servers (in Cursor agent chat)
- **Gamma**: 2 tools — generate content, browse themes
- **Canvas LMS**: 54 tools — full course/module/assignment management
- **Notion**: 22 tools — pages, databases, comments, search
- **Playwright**: 22 tools — browser automation (user-level)
- **Ref**: 2 tools — doc search and URL reading (user-level)

### API Access (via scripts, not MCP)
- **Kling**: `scripts/api_clients/kling_client.py` — text-to-video, image-to-video, lip-sync, extend, polling, download. JWT auth. LIVE TESTED.
- **ElevenLabs**: `node scripts/smoke_elevenlabs.mjs` — 45 voices
- **Qualtrics**: `node scripts/smoke_qualtrics.mjs` — surveys, questions, distributions
- **All tools**: `node scripts/heartbeat_check.mjs` — full heartbeat

## Hot-Start Context

### Kling API — Key Findings from Live Testing
- **Base URL**: `https://api.klingai.com`
- **Auth**: JWT with access_key as `iss`, secret_key for HS256 signing (30-min token lifetime)
- **Status endpoint**: `/v1/videos/text2video/{task_id}` (type-specific, NOT generic `/v1/videos/{task_id}`)
- **Status values**: `submitted` → `processing` → `succeed` / `failed`
- **Video URL**: nested in `data.task_result.videos[0].url`
- **Mode values**: `std` (720p) / `pro` (1080p) — NOT "standard"/"professional"
- **Model names**: `kling-v1-6`, `kling-v2-6`, `kling-v3-0` (dashes, not dots)
- **Duration**: string `"5"` not integer `5`
- **Parameter name**: `model_name` not `model`
- **Credits**: API credits are SEPARATE from consumer credits. Purchased via Resource Pack at klingai.com/global/dev/model/video
- **Cost**: ~2 credits per 5s std video with kling-v1-6. 1000 API credits purchased.
- **Timing**: ~140s for a 5s std video (14 polls at 10s intervals)

### Key File Paths
- Kling Client: `scripts/api_clients/kling_client.py`
- Kling Tests: `tests/test_integration_kling.py` (5 unit pass, 3 live need credits)
- Kling Story: `_bmad-output/implementation-artifacts/3-3-kling-video-specialist-agent.md`
- Test Video: `course-content/staging/story-3.3-samples/test-blue-gradient.mp4` (1.8MB, 5s)
- C1-M1 Notes: `course-content/courses/TEJAL_Course 01 Mod 01 Notes 2026-03-16.pdf`
- Irene SKILL.md: `skills/bmad-agent-content-creator/SKILL.md`
- Quinn-R SKILL.md: `skills/bmad-agent-quality-reviewer/SKILL.md`
- Marcus SKILL.md: `skills/bmad-agent-marcus/SKILL.md`
- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Epics: `_bmad-output/planning-artifacts/epics.md`

### 6 Sample Videos Planned (Task 6)
| # | Type | API Capability | Content Source |
|---|------|---------------|---------------|
| V1 | Hospital B-roll | text-to-video (pro) | C1-M1 Slide 1 prompt |
| V2 | Pathway concept animation | text-to-video (pro) | C1-M1 Slide 1 overlay |
| V3 | Slide-to-video transition | image-to-video | Gary PNG from SB-C1M1L1-02 |
| V4 | Knowledge timeline | text-to-video (std) | C1-M1 Part 2 Slide 3 |
| V5 | Talking-head lip sync | lip-sync | NS-C1M1L1-02 narration + image |
| V6 | Module bridge transition | image-to-video + sound | C1-M1 Summary slide |

### Epic 3 Story Sequence (9 stories)
| Story | Agent | Status |
|-------|-------|--------|
| 3.1 | Gary (Gamma Specialist) | DONE |
| 3.2 | Irene (Content Creator) + Quinn-R (Quality Reviewer) | DONE |
| 3.3 | Kling Video Specialist | IN PROGRESS (Task 1 done) |
| 3.4 | ElevenLabs Specialist (expanded) | Backlog |
| 3.5 | Canvas Specialist | Backlog |
| 3.6 | Qualtrics Specialist | Backlog |
| 3.7 | Canva Specialist (manual-tool pattern) | Backlog |
| 3.8 | Source Wrangler (Notion + Box) | Backlog |
| 3.9 | Tech Spec Wrangler | Backlog |

### Gotchas
- PowerShell doesn't support `&&` chaining — use `;` instead
- `.venv` is set up with Python 3.13 — activate with `.venv\Scripts\activate`
- Run tests with `.venv\Scripts\python -m pytest tests/ -v`
- Kling API credits are SEPARATE from consumer credits — buy Resource Packs
- Kling status endpoint is type-specific: `/v1/videos/text2video/{id}` not `/v1/videos/{id}`
- Kling uses `model_name` not `model`, duration as string, mode `std`/`pro`
- Cross-skill Python imports use `importlib.util` loader pattern due to hyphenated directory names
- `pyjwt` added to requirements.txt for Kling JWT auth
