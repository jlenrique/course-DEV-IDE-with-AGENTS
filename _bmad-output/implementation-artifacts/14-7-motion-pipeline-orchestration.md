# Story 14.7: End-to-End Motion Pipeline Orchestration & Compositor Update

**Epic:** 14 — Motion-Enhanced Presentation Workflow
**Status:** backlog
**Sprint key:** `14-7-motion-pipeline-orchestration`
**Added:** 2026-04-05
**Depends on:** Story 14.6 (motion perception & Irene integration)

## Summary

Marcus orchestrates the complete motion-enhanced workflow. Compositor generates assembly guides that include motion asset placement. Pre-flight check extended for Kling connectivity. End-to-end integration test validates the full pipeline.

## Goals

1. Marcus workflow variant for motion-enhanced runs.
2. Compositor assembly guide includes motion placement instructions.
3. `sync-visuals` extended to copy motion assets into assembly bundle.
4. Run reporting includes motion metrics.
5. Pre-flight check validates Kling connectivity when motion is enabled.
6. End-to-end integration test.

## Key Files

- `skills/bmad-agent-marcus/SKILL.md` — Marcus motion workflow variant
- `skills/compositor/SKILL.md` — assembly guide motion extension
- `skills/compositor/scripts/compositor_operations.py` — `sync-visuals` motion support
- `skills/pre-flight-check/SKILL.md` — Kling connectivity check
- `skills/production-coordination/` — run reporting motion metrics

## Acceptance Criteria

1. `motion_enabled: true` activates the motion pipeline: Gate 2 → Gate 2M → Kira/manual → Motion Gate → Irene Pass 2.
2. `motion_enabled: false` runs the existing static pipeline with zero behavioral change.
3. Compositor assembly guide includes motion assets: "At Slide 5, play `slide_05_motion.mp4` (8s) on video track, timed to narration segment 5."
4. `sync-visuals` extended to also copy motion assets into the assembly bundle.
5. Run reporting includes motion metrics: clips generated, animations imported, total motion duration, Kira credits consumed.
6. Pre-flight check extended: verify Kling API connectivity when `motion_enabled: true`.
7. End-to-end integration test: a 3-slide mini-run with 1 static + 1 video (Kira) + 1 animation (manual) produces correct manifest, narration with motion references, and assembly guide.

## Cross-Epic Dependencies

- Epic 12 (Double-Dispatch): compatible but independent — double-dispatch and motion can both be active
- Epic 13 (Visual-Aware Irene): hard dependency — visual reference injection is the mechanism for motion-aware narration
- All 15 stories across 3 epics: implementation order 12 → 13 → 14
