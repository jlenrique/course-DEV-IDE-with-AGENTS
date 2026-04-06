# Story 14.5: Manual Animation Guidance Skill

**Epic:** 14 — Motion-Enhanced Presentation Workflow
**Status:** done
**Sprint key:** `14-5-manual-animation-guidance`
**Added:** 2026-04-05
**Validated:** 2026-04-05
**Depends on:** Story 14.3 (motion decision point). Can parallel with Story 14.4.

## Summary

Produce detailed, step-by-step animation creation instructions for slides designated as manual animation. The user creates animations in their tool of choice (Vyond, etc.) following the generated guidance, then imports the completed file.

## Goals

1. Generate Animation Guidance Documents per animation-designated slide.
2. Tool-agnostic by default; Vyond-specific when requested.
3. Import validation for user-created animation files.
4. Segment manifest updated on import.

## Key Files

- `skills/bmad-agent-vyond/SKILL.md` — Vyond specialist for optional tool-specific instructions
- `skills/bmad-agent-content-creator/SKILL.md` — Irene Pass 1 narration intent (input to guidance)
- Run directory: `{run_dir}/motion/`

## Acceptance Criteria

1. Animation Guidance Document produced per animation-designated slide containing:
   - Visual description of what the animation should depict (from motion brief + slide content)
   - Suggested duration and pacing
   - Key frames / state descriptions (start, middle, end)
   - Alignment with narration intent from Irene Pass 1 lesson plan
   - Tool-agnostic instructions (no tool-specific jargon unless user specifies tool)
2. Vyond specialist (`bmad-agent-vyond`) can optionally produce Vyond-specific instructions if requested.
3. User imports completed animation file to `{run_dir}/motion/` as `{slide_id}_motion.{ext}`.
4. Import validation: file exists, is a supported video format, duration within expected range.
5. Segment manifest updated: `motion_asset_path`, `motion_source: "manual"`, `motion_duration_seconds`, `motion_status: "imported"`.

## Party Mode Consensus (2026-04-05)

- Tool-agnostic by default — Vyond-specific only when user specifies.
- Manual-tool pattern: app provides guidance, user executes.
