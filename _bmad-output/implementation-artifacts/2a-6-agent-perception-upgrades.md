# Story 2A-6: Existing Agent Perception Upgrades

Status: done

## Story

As Irene, Gary, and Quinn-R,
We want to adopt the universal perception protocol with sensory bridges when we consume multimodal artifacts,
So that we confirm our interpretation of non-text artifacts before acting on them — eliminating silent misperception.

## Acceptance Criteria

1. Irene Pass 2: invokes image bridge on each slide PNG, confirms interpretation with confidence, writes narration based on confirmed perception
2. Irene Pass 2 envelope receives `perception_artifacts[]` alongside `gary_slide_output[]` — narration references perception as ground truth
3. LOW confidence perception escalates to Marcus for human clarification
4. Gary: invokes image bridge on generated PNGs for self-assessment, confirms perception before scoring
5. Quinn-R: invokes appropriate sensory bridge for multimodal artifacts, confirms interpretation before scoring
6. All three agents' SKILL.md files updated with perception protocol references
7. Perception confirmation is visible in agent output (not silent)

## Tasks / Subtasks

- [x] Task 1: Update Irene for perception protocol (AC: #1, #2, #3, #6, #7)
- [x] Task 2: Update Gary for perception protocol (AC: #4, #6, #7)
- [x] Task 3: Update Quinn-R for perception protocol (AC: #5, #6, #7)
- [x] Task 4: Update Marcus Pass 2 envelope (AC: #2)
- [x] Task 5: Validate and complete

## Dev Agent Record

### Agent Model Used
Claude claude-4.6-opus (via Cursor)

### Completion Notes List
- Irene Pass 2: perception protocol added — confirms slide perception via `perception_artifacts[]` before writing narration, LOW confidence escalates to Marcus
- Irene inbound envelope: `perception_artifacts` field added alongside `gary_slide_output` with usage guidance (perception = ground truth, visual_description = creative context)
- Gary: Principle 9 added ("Perceive before assessing"), quality-assessment.md updated with perception step before dimension scoring, references shared cache
- Quinn-R: Principle 11 added ("Perceive before scoring"), review-protocol.md Step 0 added for multimodal perception before any dimension review, references shared cache
- Marcus Pass 2 envelope: `perception_artifacts[]` field added with schema and auditable-loop note for G4 fidelity verification
- All agents reference universal perception protocol and validator-handoff caching model
- 131 tests pass, 38 contracts valid, parity check PASS, no regressions

### File List
**Modified:**
- `skills/bmad-agent-content-creator/SKILL.md` (Pass 2 perception, inbound envelope)
- `skills/bmad-agent-gamma/SKILL.md` (Principle 9)
- `skills/bmad-agent-gamma/references/quality-assessment.md` (perception step)
- `skills/bmad-agent-quality-reviewer/SKILL.md` (Principle 11)
- `skills/bmad-agent-quality-reviewer/references/review-protocol.md` (Step 0)
- `skills/bmad-agent-marcus/references/conversation-mgmt.md` (Pass 2 envelope)

### Change Log
- 2026-03-28: Story 2A-6 — Irene, Gary, Quinn-R all adopt universal perception protocol with shared sensory bridge cache
