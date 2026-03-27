# Session Handoff - Stories 3.2 + 3.3 Complete

**Date:** 2026-03-27
**Branch:** `epic3-core-tool-agents`
**Session focus:** Complete Story 3.2 (Irene + Quinn-R) + Complete Story 3.3 (Kira / Kling Video Specialist)

## What Was Completed

### Story 3.2: Content Creator + Quality Reviewer (DONE - all ACs met)
- Irene (12 files), Quinn-R (6 files), quality-control skill (10 files, 28 tests)
- 6 sample content artifacts human-approved
- Marcus routing table updated
- Interaction test guides created

### Story 3.3: Kling Video Specialist (DONE - all ACs met)

1. **Kling API client** (`kling_client.py`) - JWT auth, text-to-video, image-to-video, lip-sync, extend, polling, download. Live-tested and proven.

2. **Party Mode coaching** - `party-mode-coaching-kling-specialist.md` produced with full team input.

3. **Kira agent** (`skills/bmad-agent-kling/`) - 7 files. Video Director persona with 5 internal capabilities (VP, SC, MS, VQ, CT), pipeline awareness, cost-aware model selection, live-tested API constraints baked in.

4. **kling-video mastery skill** (`skills/kling-video/`) - 7 files. Prompt patterns, model selection, parameter catalog (live-tested), `kling_operations.py` wrapper with CLI, 5 tests.

5. **Memory sidecar** - 4 files with production-validated patterns and chronology.

6. **Comparison video set** - 17+ MP4 clips across three tiers:
   - Legacy baseline: `kling-v1-6 std 5s`
   - Preferred baseline: `kling-v2-6 std sound-off 5s` (1.5 credits)
   - Premium: `kling-v2-6 pro 5s` (2.5 credits)
   - v3.0 spot-check: rejected by API (`model_name` invalid)

7. **Human review outcome:**
   - Production-worthy: hospital B-roll and physician innovator lineage montages
   - Rejected: text-heavy concept animations (garbled characters)
   - Key insight: Kira is best for atmosphere/montage, not readable embedded text

8. **Marcus registration** - `kling-specialist` (Kira) set to active in routing table.

9. **Interaction test guide** - 8 scenarios covering activation, delegation, API awareness, cost selection, pipeline reuse, degradation, and redirect.

## What Is Next

- **Story 3.4: ElevenLabs Specialist** (expanded scope)
- **Pre-Story 3.4 decision:** Party Mode session on audio/video composition architecture (when to use Kling native audio vs ElevenLabs, where lip-sync and final composition should happen, role of Descript/CapCut)
- **Early production trial:** Gary slide PNG -> Kira image-to-video pipeline integration

## Key Lessons

1. **Kling text rendering is unreliable.** Generated video cannot be trusted to render readable on-screen text. Use Gary (static slides) for text-bearing visuals; use Kira for atmosphere, montage, and non-text motion.
2. **API credits are separate from consumer credits.** Purchase Resource Packs at klingai.com/global/dev/model/video.
3. **Kling enforces concurrency limits.** Serialize all generation requests. The `1303` error code means "parallel task over resource pack limit."
4. **`kling-v2-6 std sound-off` is cheaper than `kling-v1-6 std`.** The billing data surprised us: 1.5 vs 2.0 credits for the same 5s duration.
5. **`kling-v3-0` is not available** on the current API surface. Do not assume newer models are accessible without live verification.
6. **Native sound is request-shape-sensitive.** Passing `sound=False` can trigger a body parse error; omitting the field entirely is safer.
7. **Image-to-video from Gary PNGs** is identified as the next high-value integration to prove in early production trials.

## Validation Summary

| Check | Result |
|-------|--------|
| Kling client unit tests | 5 pass |
| kling-video operations tests | 5 pass |
| Quality-control tests | 28 pass |
| Gary mastery tests | 37 pass |
| Irene quality scan | Good (0 critical) |
| Quinn-R quality scan | Good (0 critical) |
| Kira lint gate (path + scripts) | Pass |
| Human review of Kling clips | 4 approved, text-heavy rejected |

**Total tests: 187 pass** (112 project + 37 Gary + 28 quality-control + 5 Kling client + 5 kling-video)

## Artifact Update Checklist

- [x] Story 3.2: done
- [x] Story 3.3: done
- [x] Sprint status: 3.2 done, 3.3 done
- [x] Next session: updated for Story 3.4
- [x] SESSION-HANDOFF: this file
- [x] Marcus SKILL.md: Kira registered active
- [x] Kling client: `scripts/api_clients/kling_client.py`
- [x] Kira agent: `skills/bmad-agent-kling/`
- [x] kling-video skill: `skills/kling-video/`
- [x] Kling sidecar: `_bmad/memory/kling-specialist-sidecar/`
- [x] Kling tests: `tests/test_integration_kling.py` + `skills/kling-video/scripts/tests/`
- [x] Interaction test guide: `tests/agents/bmad-agent-kling/`
- [x] Coaching doc: `_bmad-output/brainstorming/party-mode-coaching-kling-specialist.md`
- [x] Comparison summary: `course-content/staging/story-3.3-samples/comparison-summary.md`
- [x] Generation manifest: `course-content/staging/story-3.3-samples/generation-manifest.csv`
- [x] Dev guide: updated with KlingClient
- [x] Project context: updated
- [x] requirements.txt: pyjwt added
