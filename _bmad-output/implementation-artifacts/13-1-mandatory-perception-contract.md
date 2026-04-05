# Story 13.1: Mandatory Perception Contract for Irene Pass 2

**Epic:** 13 — Visual-Aware Irene Pass 2 Scripting
**Status:** backlog
**Sprint key:** `13-1-mandatory-perception-contract`
**Added:** 2026-04-05
**Depends on:** Epic 12 (soft). Hard dependency on sensory bridges skill (Epic 2A complete).

## Summary

Irene's Pass 2 *requires* perception artifacts as first-class input. If not provided in the context envelope, Irene generates them inline via sensory bridges before writing any narration. This elevates perception from "available if present" to a mandatory contract.

## Goals

1. Make `perception_artifacts` a required input for Irene Pass 2 (was optional).
2. Inline generation via image sensory bridge when perception is absent.
3. Confidence-based retry for LOW-confidence perceptions.
4. Escalation to Marcus (not user) for persistent LOW confidence.

## Key Files

- `skills/bmad-agent-content-creator/SKILL.md` — Irene Pass 2 contract (lines ~89-96)
- `skills/sensory-bridges/SKILL.md` — image bridge invocation
- `skills/sensory-bridges/references/perception-protocol.md` — universal perception protocol

## Acceptance Criteria

1. Irene Pass 2 validates `perception_artifacts` presence in the context envelope.
2. If absent, Irene invokes image sensory bridge on each slide PNG in `gary_slide_output` and generates `perception_artifacts` inline.
3. Perception confirmation logged per slide: "I see Slide N shows [description]. Confidence: HIGH/MEDIUM/LOW."
4. LOW-confidence slides trigger automatic re-perception (one retry with different bridge parameters).
5. If still LOW after retry, Irene flags to Marcus for decision (proceed with caveated narration or escalate to user).
6. Perception is confirmed before any narration writing begins.

## Party Mode Consensus (2026-04-05)

- LOW-confidence escalation goes to Marcus, not user — Marcus decides whether to proceed or escalate.
- This keeps the pipeline flowing without unnecessary user interruption.
