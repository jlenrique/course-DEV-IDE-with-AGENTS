# Story 14.6: Motion Perception & Irene Pass 2 Integration

**Epic:** 14 — Motion-Enhanced Presentation Workflow
**Status:** backlog
**Sprint key:** `14-6-motion-perception-irene-integration`
**Added:** 2026-04-05
**Depends on:** Stories 14.4 and 14.5 (Kira integration + manual animation). Also depends on Epic 13 (visual reference injection).

## Summary

Irene perceives motion assets (video clips and animations) via sensory bridges and writes narration that speaks to both static slides and motion content. This integrates the video sensory bridge into Irene's Pass 2 workflow and extends visual reference injection to motion segments.

## Goals

1. HIL Motion Gate: user reviews all motion assets before they flow to Irene.
2. Irene invokes video sensory bridge on motion assets.
3. Narration for motion segments references motion content via visual reference injection (Epic 13).
4. Timing cues for motion segments in narration script.

## Key Files

- `skills/bmad-agent-content-creator/SKILL.md` — Irene Pass 2 motion-aware logic
- `skills/sensory-bridges/SKILL.md` — video sensory bridge
- `skills/sensory-bridges/references/perception-protocol.md` — universal perception protocol

## Acceptance Criteria

1. HIL Motion Gate: user reviews all generated/imported motion assets before they flow to Irene.
2. Irene Pass 2 receives both `gary_slide_output` (static slides) and motion assets in her context envelope.
3. For motion-designated segments, Irene invokes video sensory bridge on the motion asset.
4. Perception logged: "Slide N has motion (video/animation): I see [description]. Confidence: HIGH/MEDIUM/LOW."
5. Narration for motion segments references the motion content specifically (using visual reference injection from Epic 13).
6. `visual_references_per_slide` parameter applies to both static and motion segments.
7. Narration script includes timing cues for motion segments: "[as the animation plays]", "[during the transition]."
8. Segment manifest correctly distinguishes static narration timing from motion narration timing.
