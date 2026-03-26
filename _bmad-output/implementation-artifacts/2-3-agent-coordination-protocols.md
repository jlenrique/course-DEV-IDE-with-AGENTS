# Story 2.3: Agent Coordination Protocols

Status: ready-for-dev

## Story

As a user,
I want the orchestrator to coordinate specialist agents seamlessly,
So that multi-agent production workflows execute without my managing individual agents.

## Acceptance Criteria

1. The orchestrator identifies appropriate specialist agents through capability matching.
2. The orchestrator delegates tasks with full context from the production run state (context envelope).
3. Specialist agent results flow back through the orchestrator for quality review.
4. The orchestrator manages dependencies between stages (slides before voiceover, etc.).
5. Coordination state is persisted in SQLite via `agent_coordination` table.
6. The orchestrator's memory sidecar captures coordination patterns for future optimization.

## Tasks / Subtasks

- [ ] Task 1: Create delegation protocol reference (AC: #1, #2, #3)
  - [ ] 1.1: Create `skills/production-coordination/references/delegation-protocol.md` — context envelope spec, specialist matching, result handling, graceful degradation
- [ ] Task 2: Create `log_coordination.py` script for agent_coordination table (AC: #5)
  - [ ] 2.1: `log` command — record delegation event (run_id, agent_name, action, payload)
  - [ ] 2.2: `history` command — query coordination events for a run
- [ ] Task 3: Add dependency enforcement to `manage_run.py` (AC: #4)
  - [ ] 3.1: Add stage dependency validation in `advance` — verify previous stage is approved before advancing
- [ ] Task 4: Update Marcus references for delegation (AC: #1, #2, #3, #6)
  - [ ] 4.1: Update `conversation-mgmt.md` — add "Specialist Delegation" section with context envelope packing instructions
  - [ ] 4.2: Add sidecar write guidance — capturing delegation patterns in `patterns.md` (default mode)
- [ ] Task 5: Write tests (AC: all)
  - [ ] 5.1: Tests for `log_coordination.py` (min 4 tests)
  - [ ] 5.2: Test dependency enforcement in `manage_run.py` advance
- [ ] Task 6: Update interaction test guide
  - [ ] 6.1: Add test scenario for specialist delegation (graceful degradation when unavailable)

## Dev Notes

### Reuse

- `manage_run.py` (Story 2.2) already handles stage sequencing and run state — extend, don't replace
- `agent_coordination` table already exists in `coordination.db` schema
- `conversation-mgmt.md` already has Specialist Handoff Protocol section — extend it
- Context envelope already defined in `conversation-mgmt.md` (outbound/inbound specs)

### Scope Boundaries

- Do NOT build specialist agents — that's Epic 3
- Do NOT implement actual tool API calls — specialists handle that
- DO build the protocol infrastructure that Marcus follows when delegating
- DO build graceful degradation — Marcus reports "specialist not yet available" when agents don't exist

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.3]
- [Source: skills/bmad-agent-marcus/references/conversation-mgmt.md#Specialist Handoff Protocol]
- [Source: scripts/state_management/db_init.py — agent_coordination table schema]

## Dev Agent Record

### Agent Model Used
### Completion Notes List
### Change Log
### File List
