# Story 2.2: Conversational Workflow Management

Status: done

## Story

As a user,
I want the orchestrator to manage production runs through natural conversation,
So that I can initiate, direct, and review content creation by talking to one agent.

## Acceptance Criteria

1. **Given** the master orchestrator agent is activated **When** a user says "Create the Welcome video for C1M1" **Then** the orchestrator parses intent and identifies required content type, module, and production requirements.

2. **Given** intent is parsed **When** the orchestrator plans the workflow **Then** it creates a production plan with agent assignments and workflow stages, and requests confirmation before proceeding: "Here's my plan. Shall I proceed?"

3. **Given** the user approves a plan **When** production is in progress **Then** the orchestrator presents work products for review at human checkpoint gates.

4. **Given** a production stage completes **When** Marcus reports progress **Then** reporting is conversational: "Slides complete. Ready for voiceover. Want to review?"

5. **Given** the user provides guidance, corrections, or approvals **When** at any point in the conversation **Then** Marcus incorporates the input and adjusts accordingly.

6. **Given** a production run completes **When** all stages are approved **Then** Marcus records the run in chronology (default mode), captures patterns, archives state, and presents a summary.

## FRs Covered

FR53, FR54, FR55, FR56, FR57, FR58, FR59, FR60 (Conversational Orchestrator Interface)

## Tasks / Subtasks

- [x] Task 1: Create `production-coordination` skill skeleton (AC: #2, #3)
  - [x] 1.1: Create `skills/production-coordination/SKILL.md` — routing for workflow lifecycle operations
  - [x] 1.2: Create `skills/production-coordination/references/workflow-lifecycle.md` — stage sequencing, state transitions, dependency management
  - [x] 1.3: Create `skills/production-coordination/references/run-state-schema.md` — SQLite `production_runs` table usage, JSON status envelope
  - [x] 1.4: Create `skills/production-coordination/scripts/manage_run.py` — create/update/query production run records in SQLite

- [x] Task 2: Enhance `generate-production-plan.py` for run initiation (AC: #1, #2)
  - [x] 2.1: Run ID auto-generation implemented in `manage_run.py create` using `{course}-{module}-{content_type}-{timestamp}` pattern
  - [x] 2.2: Plan creation and run creation are separate steps — Marcus calls `generate-production-plan.py` for the plan, then `manage_run.py create` with the plan's stages to persist the run
  - [x] 2.3: Both scripts return JSON for agent consumption

- [x] Task 3: Create `manage_run.py` — production run state management script (AC: #3, #4, #6)
  - [x] 3.1: `create` command — insert new production_runs row with run_id, content_type, module, status='planning', stages JSON, created_at
  - [x] 3.2: `advance` command — move run to next stage, update current_stage, stage_status
  - [x] 3.3: `checkpoint` command — mark current stage as 'awaiting-review', record checkpoint metadata
  - [x] 3.4: `approve` command — record approval, update quality_gates table
  - [x] 3.5: `complete` command — mark run as completed, set completed_at timestamp
  - [x] 3.6: `status` command — return current run state as JSON (for Marcus to report conversationally)
  - [x] 3.7: `list` command — list active/recent runs

- [x] Task 4: Update Marcus references for production coordination integration (AC: #1-#5)
  - [x] 4.1: Updated `references/conversation-mgmt.md` — added "Run Execution" section with 6-step manage_run.py integration
  - [x] 4.2: Updated `references/checkpoint-coord.md` — added "Script Integration" section for checkpoint/approve/revision recording
  - [x] 4.3: Updated `references/progress-reporting.md` — added "Script Integration" section for status query and natural reporting

- [x] Task 5: Update Marcus SKILL.md External Skills table (AC: #2)
  - [x] 5.1: Changed `production-coordination` status from `planned` to `active`
  - [x] 5.2: Context passed column verified — matches actual skill interface (run ID, current stage, state context)

- [x] Task 6: Write tests (AC: all)
  - [x] 6.1: 17 unit tests for `manage_run.py` — create (3), advance (3), checkpoint (1), approve (3), complete (2), status (2), list (2), full lifecycle (1)
  - [x] 6.2: Task 2 redesigned — plan generation stays in existing script, run creation in `manage_run.py`. No changes to `generate-production-plan.py` needed.
  - [x] 6.3: Integration test: full lifecycle (create → advance → checkpoint → approve → complete → verify state) — passes

- [x] Task 7: Update interaction test guide for Story 2.2 capabilities (AC: all)
  - [x] 7.1: Added Test 13: Production Run Initiation
  - [x] 7.2: Added Test 15: Checkpoint Gate Presentation
  - [x] 7.3: Added Test 14: Progress Reporting During Run
  - [x] 7.4: Deferred tests section preserved for future stories

## Dev Notes

### Architecture Compliance

This story builds the **production-coordination skill** — one of Marcus's 5 external skills. The architecture mandates:

- **Skills as bridge layer**: `SKILL.md` for routing → `references/` for detailed guidance → `scripts/` for Python execution
- **Agent-code separation**: Marcus (agent layer, .md) never calls SQLite directly. He invokes `manage_run.py` (scripts/) which handles all DB operations.
- **State management tiers**: Production run state goes to SQLite (`state/runtime/coordination.db`). Configuration stays in YAML. Memory sidecars stay in `_bmad/memory/`.
- **Mode-aware writes**: In ad-hoc mode, `manage_run.py` operations should still execute but route to a scratch context (or log with `mode: ad-hoc` flag). QA always runs.

### Existing Infrastructure to Reuse (DO NOT REINVENT)

| Component | Location | What It Provides |
|-----------|----------|-----------------|
| `coordination.db` | `state/runtime/coordination.db` | SQLite database with `production_runs`, `agent_coordination`, `quality_gates` tables already created by `scripts/state_management/init_state.py` |
| `generate-production-plan.py` | `skills/bmad-agent-marcus/scripts/` | Already generates production plans with content type workflows, specialist sequencing, and checkpoint gates. EXTEND, don't replace. |
| `read-mode-state.py` | `skills/bmad-agent-marcus/scripts/` | Reads mode and last run from DB/file. Reuse its `find_project_root()` and DB connection patterns. |
| `BaseAPIClient` patterns | `scripts/api_clients/base_client.py` | Error handling patterns (`APIError`, structured exceptions). Follow same patterns for DB errors. |
| `conversation-mgmt.md` | `skills/bmad-agent-marcus/references/` | Already defines intent parsing, content type vocabulary, production planning steps, specialist handoff protocol, and run finalization. UPDATE existing sections, don't duplicate. |
| `checkpoint-coord.md` | `skills/bmad-agent-marcus/references/` | Already defines review gate protocol, decision handling, quality criteria sources, and outcome tracking. UPDATE, don't duplicate. |
| `progress-reporting.md` | `skills/bmad-agent-marcus/references/` | Already defines reporting style, status summary structure, error handling, and proactive reporting triggers. UPDATE, don't duplicate. |

### SQLite Schema Reference

The `production_runs` table already exists in `coordination.db` (created by `scripts/state_management/init_state.py`). Check the current schema before writing any DDL — extend if needed, don't recreate.

```sql
-- Existing table (verify exact schema in init_state.py):
-- production_runs: run_id, course_id, module_id, status, content_type, created_at, completed_at, ...
-- agent_coordination: agent_id, run_id, status, assigned_at, ...
-- quality_gates: gate_id, run_id, stage, result, reviewed_at, ...
```

### Content Type Workflows (Already Defined)

`generate-production-plan.py` already defines 7 content type workflows with specialist sequencing:
- lecture-slides, case-study, assessment, discussion-prompt, video-script, voiceover-narration, interactive-module

Each includes staged specialist assignments and human checkpoint gates. The story extends this by connecting plan generation to persistent run state.

### Production Run State Machine

```
planning → in-progress → [stage cycle] → completed
                              ↓
                    stage: working → awaiting-review → approved → (next stage)
                                          ↓
                                     revision-requested → working (loop)
```

### File Structure for New Code

```
skills/production-coordination/
├── SKILL.md                          # Routing: lifecycle management, state queries
├── references/
│   ├── workflow-lifecycle.md         # Stage transitions, dependency rules, recovery
│   └── run-state-schema.md           # DB schema reference, JSON status envelope format
└── scripts/
    ├── manage_run.py                 # CLI: create/advance/checkpoint/approve/complete/status/list
    └── tests/
        └── test_manage_run.py        # Unit + integration tests
```

### Script Conventions (From Story 2.1)

- Use PEP 723 script metadata (`# /// script` header) for dependency declarations
- Use `find_project_root()` pattern from `read-mode-state.py` for project root discovery
- Use `argparse` with subcommands for multi-action CLI scripts
- Output JSON for agent consumption, markdown for human consumption (support both via `--format` flag)
- Self-contained tests (can run directly: `python test_manage_run.py`)
- Follow snake_case naming for all DB operations per architecture conventions

### Testing Standards

- Tests in `skills/production-coordination/scripts/tests/test_manage_run.py`
- Use temporary SQLite databases (`:memory:` or `tempfile`) — never touch production DB
- Test the full lifecycle: create → advance through stages → checkpoint → approve → complete
- Test edge cases: advance past last stage, approve when not at checkpoint, duplicate run IDs
- Follow the same pattern as `skills/bmad-agent-marcus/scripts/tests/test-read-mode-state.py` (self-contained, direct-execution)
- Also add tests for `generate-production-plan.py` enhancements in existing test file

### What NOT to Build (Scope Boundaries)

- **Do NOT build specialist agents** — they are Epic 3 stories. Marcus gracefully degrades when specialists are unavailable.
- **Do NOT build the quality-reviewer agent** — that's Story 3.4. Quality gates in this story are structural (the gate exists in the state machine), not implemented as agent-to-agent review.
- **Do NOT build the `run-reporting` skill** — that's Story 4.4. This story records state; reporting analyzes it.
- **Do NOT build real-time Cursor chat integration code** — Marcus is an .md agent that Cursor loads natively. No Python needed for the conversational interface itself.
- **Do NOT modify `scripts/api_clients/`** — those are Epic 1 infrastructure. Production coordination doesn't call external APIs.
- **Do NOT modify `scripts/state_management/init_state.py`** — if the existing schema needs extension, add migration logic in `manage_run.py` itself.

### Cross-Story Dependencies

- **Story 2.1 (DONE)**: Marcus agent exists with SKILL.md, references, scripts, sidecar, tests
- **Story 2.3 (NEXT)**: Agent coordination protocols — will extend `production-coordination` skill with multi-agent delegation
- **Story 2.4 (FUTURE)**: Parameter intelligence — will add style guide read/write to the production workflow
- **Story 2.5 (FUTURE)**: Pre-flight orchestration — will add tool readiness check before run initiation

### Previous Story Intelligence (Story 2.1)

Story 2.1 established these patterns that Story 2.2 MUST follow:
- Marcus references use progressive disclosure: SKILL.md → references/ → scripts/
- Scripts use PEP 723 headers, `argparse`, JSON output for agent consumption
- Tests are self-contained (runnable via `python test_file.py` directly)
- Memory sidecar writes respect mode boundaries (default = full, ad-hoc = transient only)
- Marcus SKILL.md has a capability routing table — update the `production-coordination` entry when the skill is built

### Project Structure Notes

- All new files go under `skills/production-coordination/` — this is a new skill directory
- Updates to existing Marcus references go in `skills/bmad-agent-marcus/references/`
- Tests for the new skill go in `skills/production-coordination/scripts/tests/`
- Tests for `generate-production-plan.py` enhancements go in existing `skills/bmad-agent-marcus/scripts/tests/test-generate-production-plan.py`
- Interaction test updates go in `tests/agents/bmad-agent-marcus/interaction-test-guide.md`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 2.2]
- [Source: _bmad-output/planning-artifacts/architecture.md#State Management & Persistence]
- [Source: _bmad-output/planning-artifacts/architecture.md#Agent-Code Integration Patterns]
- [Source: _bmad-output/planning-artifacts/architecture.md#Communication Patterns]
- [Source: _bmad-output/planning-artifacts/architecture.md#Quality Control Patterns]
- [Source: skills/bmad-agent-marcus/SKILL.md#External Skills]
- [Source: skills/bmad-agent-marcus/references/conversation-mgmt.md]
- [Source: skills/bmad-agent-marcus/references/checkpoint-coord.md]
- [Source: skills/bmad-agent-marcus/references/progress-reporting.md]
- [Source: skills/bmad-agent-marcus/scripts/generate-production-plan.py]
- [Source: skills/bmad-agent-marcus/scripts/read-mode-state.py]
- [Source: docs/dev-guide.md#Skill Anatomy]
- [Source: docs/dev-guide.md#Extension Guide: Adding New Capabilities]
- [Source: docs/directory-responsibilities.md]

## Dev Agent Record

### Agent Model Used

claude-4.6-opus-high-thinking (Cursor Agent)

### Completion Notes List

- Created `production-coordination` skill with SKILL.md, 2 reference docs, and `manage_run.py` CLI script
- `manage_run.py` implements 7 subcommands: create, advance, checkpoint, approve, complete, status, list
- Uses existing `coordination.db` schema — no DDL modifications needed
- Context stored as JSON in `context_json` column with stages array, mode, content type, and revision tracking
- Quality gate records created automatically on checkpoint, updated on approval
- Run ID auto-generation: `{course}-{module}-{content_type}-{timestamp}`
- Updated 3 Marcus references: conversation-mgmt.md (Run Execution section), checkpoint-coord.md (Script Integration), progress-reporting.md (Script Integration)
- Updated Marcus SKILL.md: `production-coordination` status → active
- Added 3 new interaction test scenarios (Tests 13-15) to interaction test guide
- 17 new tests all pass; 98/99 existing unit tests pass (1 pre-existing failure: test_has_brand_section)
- 15 Marcus script tests continue to pass (no regressions)

### Change Log

- 2026-03-26: Story 2.2 implemented — production-coordination skill, manage_run.py, Marcus reference updates, interaction tests

### File List

**New files:**
- `skills/production-coordination/SKILL.md`
- `skills/production-coordination/references/workflow-lifecycle.md`
- `skills/production-coordination/references/run-state-schema.md`
- `skills/production-coordination/scripts/manage_run.py`
- `skills/production-coordination/scripts/tests/test_manage_run.py`

**Modified files:**
- `skills/bmad-agent-marcus/SKILL.md` (production-coordination status: planned → active)
- `skills/bmad-agent-marcus/references/conversation-mgmt.md` (added Run Execution section)
- `skills/bmad-agent-marcus/references/checkpoint-coord.md` (added Script Integration section)
- `skills/bmad-agent-marcus/references/progress-reporting.md` (added Script Integration section)
- `tests/agents/bmad-agent-marcus/interaction-test-guide.md` (added Tests 13-15)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (Story 2.2 status updates)
