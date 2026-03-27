# Next Session Start Here

## Immediate Next Action

**Run the first controlled slide + narration pilot through Descript** (Kira out of scope). Use `dev/trial-run-slide-narration` or current default branch.

Story **3.9 Source Wrangler** is implemented: `skills/source-wrangler/` + `NotionClient` + URL/HTML ingest + Playwright-assisted capture path. Stories 3.4, 3.5, 3.9, and 3.10 are in place; segment manifest and doc-refresh coverage remain active.

**Pre-Story 3.4 decision (RESOLVED):** The Party Mode composition architecture session established:
- Silent video + Smart Audio model (Kling sound-off, ElevenLabs owns all audio)
- Narration-paced video (ElevenLabs generates first, Kira matches durations)
- Segment manifest as single source of truth
- Descript as sole composition platform (manual-tool pattern)
- Compositor skill as Story 3.5 (proof-of-concept end-to-end assembly)

**Decision record:** `_bmad-output/brainstorming/party-mode-composition-architecture.md`

**Branch**: `dev/trial-run-slide-narration` (pilot) or `master`

## Current Status — STORIES 3.1 + 3.2 + 3.3 + 3.3.1 + 3.4 + 3.5 + 3.9 + 3.10 COMPLETE

- **Story 3.3.1 (Composition Harmonization + Gary Deck)**: DONE — all agents updated, architecture updated, Gary deck mode + theme/template preview added, Epic 3 re-sequenced to 11 stories
- **Story 3.4 (Voice Director / ElevenLabs)**: DONE — expanded ElevenLabs client (timestamps, dictionaries, dialogue, SFX, music stream), `elevenlabs-audio` skill, Voice Director agent, sidecar, bootstrap exemplar, focused live timestamp + manifest smoke passed
- **Story 3.5 (Compositor + Intent Contract)**: DONE — `skills/compositor/` added, proof-of-concept `descript-assembly-guide.md` generated from completed manifest, `behavioral_intent` formalized across Irene templates/manifest, Gary intent self-check added, Quinn-R intent-fidelity review added
- **Story 3.10 (Tech Spec Wrangler)**: DONE — `skills/tech-spec-wrangler/` added, ElevenLabs/Compositor doc-source coverage created, refresh metadata + proof report + sidecar logging validated
- **Story 3.3 (Kira - Kling Video Specialist)**: DONE - API client (JWT auth, live-tested), Kira agent (7 files), kling-video skill (7 files), 5+5 tests, comparison video set (baseline v2-6 std vs premium v2-6 pro), human-reviewed, production guidance established
- **Story 3.2 (Irene + Quinn-R)**: DONE - 12+6+10 files, 28 tests, 6 sample artifacts approved
- **Story 3.1 (Gary)**: DONE - 10+6 files, 29 tests, L1+L2 woodshed PASSED
- **Epic 2**: COMPLETE (6/6 stories, 55 tests)
- **Epic 1**: COMPLETE (11/11 stories, 117 tests)

## Composition Architecture (Resolved 2026-03-27)

### Pipeline
```
Marcus → Irene P1 → Marcus/[Gate 1] → Gary → Marcus/[Gate 2] →
Irene P2 → Marcus/[Gate 3] → ElevenLabs → Marcus → Kira →
Marcus → Quinn-R pre-comp → Compositor → Descript →
Quinn-R post-comp → Marcus/[Gate 4] → Canvas
```

### Key Design Decisions
- **Silent video always** from Kling (`sound-off`)
- **ElevenLabs owns all audio** (narration, SFX, music)
- **Segment manifest** (YAML) = single source of truth, all agents read/write
- **Narration-paced video** = audio drives visual timing
- **Descript** = sole composition platform, manual-tool pattern
- **Compositor skill** (Story 3.5) = generates Descript Assembly Guide from completed manifest
- **Four HIL gates** = lesson plan, slides, script+manifest, final video
- **Quinn-R two-pass** = pre-composition (asset quality) + post-composition (final export)

### Irene Two-Pass Model
- **Pass 1** (before Gary): lesson plan + slide brief
- **Pass 2** (after Gary + HIL Gate 2): narration script + segment manifest
- Gary returns `gary_slide_output` array with slide PNGs → passed to Irene for Pass 2

### Gary Deck Enhancement
- **Deck mode**: numCards ranges per content type (lecture 5-12, case study 3-5, overview 3-4)
- **Theme/template preview** (TP capability): presents available themes + registered templates before generation
- `GammaClient.list_themes()` live-tested: returns 10 themes (institutional: "2026 HIL APC Nejal")
- `gary_slide_output` return field feeds Irene Pass 2

## Epic 3 Story Sequence (11 stories)
| Story | Agent/Skill | Status |
|-------|-------------|--------|
| 3.1 | Gary (Gamma Specialist) | DONE |
| 3.2 | Irene (Content Creator) + Quinn-R (Quality Reviewer) | DONE |
| 3.3 | Kira (Kling Video Specialist) | DONE |
| 3.3.1 | Composition Harmonization + Gary Deck | DONE |
| 3.4 | ElevenLabs Specialist (expanded) | DONE |
| 3.5 | Compositor Skill (Descript Assembly Guide) | DONE |
| 3.6 | Canvas Specialist | Backlog |
| 3.7 | Qualtrics Specialist | Backlog |
| 3.8 | Canva Specialist (manual-tool pattern) | Backlog |
| 3.9 | Source Wrangler (Notion + Box + web/Playwright) | DONE |
| 3.10 | Tech Spec Wrangler | DONE |

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
- **Gamma themes**: `GammaClient.list_themes()` returns 10 themes. LIVE TESTED.

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
- Image-to-video from Gary PNGs is the next high-value integration (Compositor proof-of-concept)

## Gotchas
- PowerShell doesn't support `&&` chaining
- `.venv` with Python 3.13
- Kling API credits are SEPARATE from consumer credits
- Kling status endpoint is type-specific: `/v1/videos/text2video/{id}`
- Kling uses `model_name` not `model`, duration as string, mode `std`/`pro`
- Kling text rendering produces garbled characters - use Gary for text-bearing visuals
- `pyjwt` in requirements.txt for Kling JWT auth
- Cross-skill Python imports use `importlib.util` loader pattern
- GammaClient.list_themes() requires dotenv load in Python scripts (API key from .env)
