# Story 14.2: Segment Manifest Motion Extensions

**Epic:** 14 — Motion-Enhanced Presentation Workflow
**Status:** backlog
**Sprint key:** `14-2-segment-manifest-motion-extensions`
**Added:** 2026-04-05
**Depends on:** Story 14.1 (motion workflow design)

## Summary

Extend the segment manifest schema to support motion designations per segment. New fields track motion type, asset path, source provenance, duration, brief, and lifecycle status.

## Goals

1. Add motion fields to segment manifest schema.
2. Maintain backward compatibility with existing all-static manifests.
3. Add validation: motion segments require `motion_asset_path` before Irene Pass 2.

## Key Files

- `skills/bmad-agent-content-creator/references/template-segment-manifest.md` — schema update
- `skills/compositor/SKILL.md` — manifest interpretation rules update
- `skills/bmad-agent-fidelity-assessor/SKILL.md` — Vera manifest validation

## Acceptance Criteria

1. New fields per segment: `motion_type: "static" | "video" | "animation"` (default: "static").
2. `motion_asset_path: string | null` — path to video MP4 or animation file.
3. `motion_source: "kling" | "manual" | null` — provenance of motion asset.
4. `motion_duration_seconds: float | null` — duration of motion asset.
5. `motion_brief: string | null` — intent/description of the motion.
6. `motion_status: "pending" | "generated" | "imported" | "approved" | null` — lifecycle tracking.
7. Backward compatible: existing manifests with all-static segments work unchanged.
8. Template updated: `skills/bmad-agent-content-creator/references/template-segment-manifest.md`.
9. Validation: `motion_type != "static"` requires `motion_asset_path` populated before Irene Pass 2.
