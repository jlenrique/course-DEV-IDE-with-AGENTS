# Story 14.4: Kira Pipeline Integration

**Epic:** 14 — Motion-Enhanced Presentation Workflow
**Status:** done
**Sprint key:** `14-4-kira-pipeline-integration`
**Added:** 2026-04-05
**Validated:** 2026-04-05
**Depends on:** Story 14.3 (motion decision point). Can parallel with Story 14.5.

## Summary

Wire Kira (Kling video specialist) into the motion-enhanced pipeline. Kira receives slide PNGs + motion briefs and produces video clips for video-designated slides, respecting budget constraints.

## Goals

1. Marcus routes video-designated slides to Kira with context envelope.
2. Kira uses image-to-video (preferred) or text-to-video based on brief.
3. Model selection respects budget preferences (std/pro).
4. Downloaded MP4s go to `{run_dir}/motion/`.
5. Running cost tally with budget ceiling enforcement.

## Key Files

- `skills/bmad-agent-kling/SKILL.md` — Kira agent (already exists)
- `skills/kling-video/SKILL.md` — Kling video skill (already exists)
- `scripts/api_clients/kling_client.py` — Kling API client (already exists)
- `skills/bmad-agent-marcus/SKILL.md` — Marcus motion routing

## Acceptance Criteria

1. Kira receives context envelope containing: slide PNG, motion brief, narration intent (from Irene Pass 1), duration target, budget constraints.
2. Kira uses image-to-video (preferred) or text-to-video based on brief complexity.
3. Model selection respects `motion_budget.model_preference` (std/pro).
4. Each generated MP4 downloaded immediately to `{run_dir}/motion/` as `{slide_id}_motion.mp4`.
5. Kira returns structured results: `{slide_id, mp4_path, model_used, duration_seconds, credits_consumed, self_assessment}`.
6. Running cost tally updated after each generation.
7. If budget ceiling hit, Marcus pauses and downgrades remaining clips to `std` (or flags if already `std`).
8. Segment manifest updated: `motion_asset_path`, `motion_source: "kling"`, `motion_duration_seconds`, `motion_status: "generated"`.

## Party Mode Consensus (2026-04-05)

- Image-to-video preferred (leverages Gary's approved slide PNGs).
- Budget auto-downgrade from pro to std on ceiling hit.
