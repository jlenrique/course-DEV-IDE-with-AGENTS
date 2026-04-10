# Story 4A-4: Agent QA Release Gate

Status: done

## Story

As a system maintainer,
I want every agent revision to pass a mandatory quality scan before acceptance,
So that structural defects, prompt craft issues, and lane violations are caught before they become runtime drift.

## Acceptance Criteria

1. Given a new agent or agent revision is proposed, when the quality gate runs, then `bmad-agent-builder` quality optimizer scans for: structure compliance, prompt craft quality, cohesion, execution efficiency, and script opportunities.
2. Pass/fail criteria are defined per scan dimension.
3. Failures block acceptance — the agent must be revised and re-scanned.
4. Given the release gate process is defined, when an agent passes the quality scan, then the scan results are archived in `skills/reports/bmad-agent-{name}/quality-scan/` with timestamp.
5. The dev-story workflow and create-story workflow reference the agent QA gate as a required step for agent-creation stories.
6. The process is documented in a shared reference accessible to all developers.

## Tasks / Subtasks

- [x] Task 1: Define shared release-gate reference (AC: #1, #2, #3, #6)
  - [x] 1.1 Create a shared reference documenting scan dimensions, thresholds, pass/fail criteria, and block/re-scan loop
  - [x] 1.2 Document required archive format and path convention

- [x] Task 2: Enforce workflow references (AC: #5)
  - [x] 2.1 Update create-story workflow to require gate tasks for agent-creation/revision stories
  - [x] 2.2 Update dev-story workflow completion checks to require gate pass evidence before review status on agent stories

- [x] Task 3: Add lightweight guardrail utility for scan archival (AC: #4)
  - [x] 3.1 Add utility script to archive quality scan results in canonical path with timestamp
  - [x] 3.2 Add tests for archive path and payload validation

- [x] Task 4: Produce proof archive record (AC: #4)
  - [x] 4.1 Run quality-scan process for one revised agent and archive timestamped result under `skills/reports/bmad-agent-{name}/quality-scan/`

- [x] Task 5: Validation and mandatory review closure
  - [x] 5.1 Validate workflow references and archive artifacts exist
  - [x] 5.2 Run adversarial review and apply fixes
  - [x] 5.3 Run party-mode consensus review and apply fixes
  - [x] 5.4 Re-validate and move to done

## Dev Notes

### Design Direction

The story formalizes `bmad-agent-builder` quality optimizer as a required release gate and records verifiable scan outcomes per agent revision.

### Expected File Changes

- `_bmad-output/implementation-artifacts/4a-4-agent-qa-release-gate.md` (new)
- `docs/workflow/agent-qa-release-gate.md` (new)
- `.github/skills/bmad-create-story/workflow.md` (modify)
- `.github/skills/bmad-dev-story/workflow.md` (modify)
- `scripts/utilities/archive_agent_quality_scan.py` (new)
- `tests/test_archive_agent_quality_scan.py` (new)
- `skills/reports/bmad-agent-*/quality-scan/*.json` (new evidence)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modify)
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` (modify)
- `next-session-start-here.md` (modify)

## Dev Agent Record

### Agent Model Used
GPT-5.3-Codex

### Debug Log References
- 2026-03-28: Story initialized and implementation started.
- 2026-03-29: Workflow references and release-gate shared documentation added.
- 2026-03-29: Archive utility hardened after adversarial findings (input validation + exit semantics) and tests expanded.
- 2026-03-29: Party-mode consensus review returned GO with no blockers.

### Completion Notes List
- Added shared gate reference at `docs/workflow/agent-qa-release-gate.md` covering required dimensions, thresholds, pass/fail rules, archive schema, workflow integration, and command/exit behavior.
- Updated `bmad-create-story` workflow to require Agent QA Release Gate tasks for agent story scope before ready-for-dev.
- Updated `bmad-dev-story` workflow completion step to require gate pass evidence and archived report path before review/done.
- Added `scripts/utilities/archive_agent_quality_scan.py` to evaluate dimensions and archive canonical scan reports.
- Hardened archive utility with strict validation for agent name, timestamp format, score ranges, and threshold range.
- Added and extended tests in `tests/test_archive_agent_quality_scan.py` (10 passing tests).
- Generated proof archived report: `skills/reports/bmad-agent-quality-reviewer/quality-scan/20260328T214404.json`.
- Validated workflow references and artifacts via targeted search checks.
- Mandatory review closure complete: adversarial review findings remediated, then party-mode consensus review returned GO.

### File List
**Created:**
- `_bmad-output/implementation-artifacts/4a-4-agent-qa-release-gate.md`
- `docs/workflow/agent-qa-release-gate.md`
- `scripts/utilities/archive_agent_quality_scan.py`
- `tests/test_archive_agent_quality_scan.py`
- `skills/reports/bmad-agent-quality-reviewer/quality-scan/20260328T214148.json`
- `skills/reports/bmad-agent-quality-reviewer/quality-scan/20260328T214404.json`

**Modified:**
- `.github/skills/bmad-create-story/workflow.md`
- `.github/skills/bmad-dev-story/workflow.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- `next-session-start-here.md`
- `docs/workflow/agent-qa-release-gate.md`
- `scripts/utilities/archive_agent_quality_scan.py`
- `tests/test_archive_agent_quality_scan.py`

### Change Log
- 2026-03-28: Story initialized and implementation started.
- 2026-03-29: Implemented release-gate documentation, workflow requirements, archive utility, and tests; generated proof archived scan report.
- 2026-03-29: Completed mandatory adversarial + party-mode review closure with hardening fixes; moved to done.
