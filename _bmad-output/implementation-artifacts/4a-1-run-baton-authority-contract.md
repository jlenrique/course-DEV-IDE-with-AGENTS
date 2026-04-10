# Story 4A-1: Run Baton & Authority Contract

Status: done

## Story

As a production user,
I want an explicit authority contract for every active production run that agents check before acting,
So that specialist agents operate within a clear delegation hierarchy and users can seamlessly switch between orchestrated production and standalone consultation.

## Acceptance Criteria

1. Given Marcus creates a production run, when the run baton is initialized, then the baton contains `run_id`, `orchestrator`, `current_gate`, `invocation_mode`, `allowed_delegates`, `escalation_target`, and `blocking_authority`.
2. Baton state is persisted in a session-accessible runtime location.
3. Marcus can update `current_gate` as the pipeline progresses.
4. Given a user directly invokes a specialist while an active baton exists, then the specialist redirects by default: "Marcus is running [run_id], currently at [gate]. Redirect, or enter standalone consult mode?"
5. Given user explicitly requests standalone consult mode, specialist can operate outside baton authority and does not mutate active production run state.
6. Given a run completes or is cancelled, baton is cleared.
7. Design remains lightweight (YAML/JSON runtime contract), no new DB infrastructure required.

## Tasks / Subtasks

- [x] Task 1: Implement run baton runtime contract script (AC: #1, #2, #3, #4, #5, #6, #7)
  - [x] 1.1 Create `skills/production-coordination/scripts/manage_baton.py`
  - [x] 1.2 Implement commands: `init`, `get`, `update-gate`, `check-specialist`, `close`
  - [x] 1.3 Persist baton in `state/runtime/` using lightweight JSON files
  - [x] 1.4 Ensure `check-specialist` supports default redirect behavior and explicit standalone override semantics

- [x] Task 2: Integrate baton lifecycle with production run lifecycle (AC: #3, #6)
  - [x] 2.1 Update `skills/production-coordination/scripts/manage_run.py` to add `cancel` command
  - [x] 2.2 Ensure `complete` and `cancel` both close the baton for the run

- [x] Task 3: Update agent/coordination protocol docs for enforcement (AC: #3, #4, #5)
  - [x] 3.1 Update Marcus orchestration reference for baton lifecycle and gate updates
  - [x] 3.2 Update production-coordination skill references/capabilities for baton operations
  - [x] 3.3 Update active specialist SKILL docs to require baton check on direct invocation

- [x] Task 4: Add tests and validate behavior (AC: #1-#7)
  - [x] 4.1 Add tests for `manage_baton.py` lifecycle + redirect behavior
  - [x] 4.2 Extend `manage_run.py` tests for cancel and baton auto-close behavior
  - [x] 4.3 Run focused regression tests for production-coordination scripts

- [x] Task 5: Update story/status artifacts
  - [x] 5.1 Update this story file (tasks, completion notes, file list, change log)
  - [x] 5.2 Update sprint status from `backlog` to `review` for 4a-1 if all validations pass
- [x] Task 6: Mandatory review closure gate
  - [x] 6.1 Run adversarial code review for 4A-1
  - [x] 6.2 Run party-mode consensus review for 4A-1
  - [x] 6.3 Apply consensus fixes and revalidate tests before marking done

## Dev Notes

### Implementation Direction

Use the existing production-coordination runtime state pattern (`manage_mode.py`, `manage_run.py`) and avoid introducing database schema changes for baton state.

### Party Mode Consensus (2026-03-28)

Consensus recommendation: implement a lightweight baton runtime script, integrate close-on-complete/cancel in run lifecycle, add specialist direct-invocation redirect protocol, and validate with focused tests.

### Expected File Changes

- `skills/production-coordination/scripts/manage_baton.py` (new)
- `skills/production-coordination/scripts/manage_run.py` (modify)
- `skills/production-coordination/scripts/tests/test_manage_baton.py` (new)
- `skills/production-coordination/scripts/tests/test_manage_run.py` (modify)
- `skills/production-coordination/SKILL.md` (modify)
- `skills/production-coordination/references/run-state-schema.md` (modify)
- `skills/production-coordination/references/delegation-protocol.md` (modify)
- `skills/bmad-agent-marcus/references/conversation-mgmt.md` (modify)
- `skills/bmad-agent-gamma/SKILL.md` (modify)
- `skills/bmad-agent-content-creator/SKILL.md` (modify)
- `skills/bmad-agent-elevenlabs/SKILL.md` (modify)
- `skills/bmad-agent-kling/SKILL.md` (modify)
- `skills/bmad-agent-quality-reviewer/SKILL.md` (modify)
- `skills/bmad-agent-fidelity-assessor/SKILL.md` (modify)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modify)

## Dev Agent Record

### Agent Model Used
GPT-5.3-Codex

### Debug Log References
- 2026-03-28: Party-mode-style consensus consultation executed; recommendation adopted.

### Completion Notes List
- Added `manage_baton.py` with lightweight JSON baton contract and commands: init/get/update-gate/check-specialist/close.
- Added specialist redirect contract output with explicit standalone-consult bypass semantics.
- Updated `manage_run.py` with `cancel` command and baton close-on-complete/cancel behavior.
- Added baton gate sync on `manage_run.py advance` so `current_gate` tracks pipeline stage progression when baton exists.
- Added/updated production-coordination references for baton lifecycle, run-state relation, and delegation guardrails.
- Updated Marcus orchestration reference with baton lifecycle and direct-invocation redirect protocol.
- Updated active specialist SKILL docs (Gary, Irene, ElevenLabs Voice Director, Kira, Quinn-R, Vera) with required baton check protocol on direct invocation.
- Validation: `pytest -q skills/production-coordination/scripts/tests` -> `58 passed`.
- Mandatory review closure completed: adversarial review + party-mode consensus re-review executed, consensus hardening fixes applied (active-baton init guard, clearer baton sync/close semantics, invocation-mode behavior clarification, corrupt baton warning path, and additional lifecycle/edge-case tests).

### File List
**Created:**
- `_bmad-output/implementation-artifacts/4a-1-run-baton-authority-contract.md`
- `skills/production-coordination/scripts/manage_baton.py`
- `skills/production-coordination/scripts/tests/test_manage_baton.py`
- `skills/production-coordination/references/baton-lifecycle.md`

**Modified:**
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `skills/production-coordination/scripts/manage_run.py`
- `skills/production-coordination/scripts/tests/test_manage_run.py`
- `skills/production-coordination/scripts/manage_baton.py`
- `skills/production-coordination/scripts/tests/test_manage_baton.py`
- `skills/production-coordination/SKILL.md`
- `skills/production-coordination/references/run-state-schema.md`
- `skills/production-coordination/references/delegation-protocol.md`
- `skills/production-coordination/references/workflow-lifecycle.md`
- `skills/bmad-agent-marcus/SKILL.md`
- `skills/bmad-agent-marcus/references/conversation-mgmt.md`
- `skills/bmad-agent-gamma/SKILL.md`
- `skills/bmad-agent-content-creator/SKILL.md`
- `skills/bmad-agent-elevenlabs/SKILL.md`
- `skills/bmad-agent-kling/SKILL.md`
- `skills/bmad-agent-quality-reviewer/SKILL.md`
- `skills/bmad-agent-fidelity-assessor/SKILL.md`

### Change Log
- 2026-03-28: Story initialized and implementation started.
- 2026-03-28: Story implemented and validated; moved to review.
- 2026-03-28: Mandatory adversarial + party-mode review gate completed; consensus fixes applied and validated; moved to done.
