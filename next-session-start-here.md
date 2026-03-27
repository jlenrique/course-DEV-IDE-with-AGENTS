# Next Session Start Here

## Immediate Next Action

**Implement Story 3.4 (ElevenLabs Specialist - expanded scope with timestamps, pronunciation, SFX, music, dialogue)**

Stories 3.1-3.3 are DONE. The content pipeline now has: Irene (content design) -> Gary (slides) -> Kira (video) -> Quinn-R (quality review). ElevenLabs is the next critical piece for narration synthesis.

**Important pre-Story 3.4 decision:** Run a dedicated Party Mode session on the audio/video composition architecture question before building the ElevenLabs agent. Key questions to resolve:
- When should audio be generated natively in Kling versus separately in ElevenLabs?
- When should SFX or light music be introduced in Kling versus later in editing tools?
- Should narration be composed later in CapCut or another editor after ElevenLabs synthesis?
- Should final lip-sync and compositing happen in Kling, Descript, CapCut, or another downstream editor?
- What is the ideal assembly/composition workflow across all these tools?

**Early production trial priority:** Gary slide PNG -> Kira image-to-video animation. This was identified during Story 3.3 review as a high-value pipeline integration to prove early.

**Branch**: `epic3-core-tool-agents`

## Current Status - STORIES 3.1 + 3.2 + 3.3 COMPLETE, EPIC 3 IN PROGRESS

- **Story 3.3 (Kira - Kling Video Specialist)**: DONE - API client (JWT auth, live-tested), Kira agent (7 files), kling-video skill (7 files), 5+5 tests, comparison video set (baseline v2-6 std vs premium v2-6 pro), human-reviewed, production guidance established
- **Story 3.2 (Irene + Quinn-R)**: DONE - 12+6+10 files, 28 tests, 6 sample artifacts approved
- **Story 3.1 (Gary)**: DONE - 10+6 files, 29 tests, L1+L2 woodshed PASSED
- **Epic 2**: COMPLETE (6/6 stories, 55 tests)
- **Epic 1**: COMPLETE (11/11 stories, 117 tests)

## Key Kling Findings from Story 3.3

### What works well
- Atmospheric B-roll (hospital corridors, clinical environments)
- Montage-style visual storytelling (physician innovator lineage)
- Non-text-dependent motion sequences
- Best baseline: `kling-v2-6 std sound-off 5s` at 1.5 credits
- Best premium: `kling-v2-6 pro 5s` at 2.5 credits

### What does NOT work well
- Text-heavy concept animations produce garbled characters
- Infographic/timeline/roadmap clips where Kling must render readable embedded text
- `kling-v3-0` is not accepted on the current API surface

### Production guidance
- Use Gary for text-bearing visuals; use Kira for atmosphere, transitions, and non-text motion
- Serialize Kling submissions (concurrency limit enforced by API)
- Download MP4s immediately (CDN URLs expire)
- Image-to-video from Gary PNGs is the next high-value integration to prove

## What's Working Right Now

### MCP Servers
- **Gamma**: 2 tools
- **Canvas LMS**: 54 tools
- **Notion**: 22 tools
- **Playwright**: 22 tools
- **Ref**: 2 tools

### API Access
- **Kling**: `scripts/api_clients/kling_client.py` - JWT auth, text-to-video, image-to-video, lip-sync, extend. LIVE TESTED.
- **ElevenLabs**: `node scripts/smoke_elevenlabs.mjs` - 45 voices
- **Qualtrics**: `node scripts/smoke_qualtrics.mjs`
- **All tools**: `node scripts/heartbeat_check.mjs`

## Epic 3 Story Sequence (9 stories)
| Story | Agent | Status |
|-------|-------|--------|
| 3.1 | Gary (Gamma Specialist) | DONE |
| 3.2 | Irene (Content Creator) + Quinn-R (Quality Reviewer) | DONE |
| 3.3 | Kira (Kling Video Specialist) | DONE |
| 3.4 | ElevenLabs Specialist (expanded) | NEXT |
| 3.5 | Canvas Specialist | Backlog |
| 3.6 | Qualtrics Specialist | Backlog |
| 3.7 | Canva Specialist (manual-tool pattern) | Backlog |
| 3.8 | Source Wrangler (Notion + Box) | Backlog |
| 3.9 | Tech Spec Wrangler | Backlog |

## Gotchas
- PowerShell doesn't support `&&` chaining
- `.venv` with Python 3.13
- Kling API credits are SEPARATE from consumer credits
- Kling status endpoint is type-specific: `/v1/videos/text2video/{id}`
- Kling uses `model_name` not `model`, duration as string, mode `std`/`pro`
- Kling text rendering produces garbled characters - use Gary for text-bearing visuals
- `pyjwt` in requirements.txt for Kling JWT auth
- Cross-skill Python imports use `importlib.util` loader pattern
