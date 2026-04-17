# Story 1.3: State Management Infrastructure

> **Historical note (2026-04-16):** Paths of the form `<old>-specialist-sidecar/` and `bmad-agent-marcus-sidecar/` were renamed to persona-named sidecars. See `_bmad/memory/` for current paths.

Status: done

## Story

As a developer,
I want SQLite database, YAML configuration files, and BMad memory sidecar directories initialized,
So that agents have persistent state for coordination, configuration, and learning.

## Acceptance Criteria

1. **Course Context YAML**: `state/config/course_context.yaml` exists with course-level template structure (course name, description, modules array, learning objectives)
2. **Style Guide YAML**: `state/config/style_guide.yaml` exists with brand standards sections and tool parameter preference sections for each Tier 1-2 tool
3. **Tool Policies YAML**: `state/config/tool_policies.yaml` exists with tool allocation policy template (run presets, quality gate thresholds, fallback strategies)
4. **SQLite Database**: `state/runtime/coordination.db` is created with `production_runs`, `agent_coordination`, and `quality_gates` tables via an initialization script
5. **BMad Memory Directories**: `_bmad/memory/` directory exists with placeholder structure for agent sidecars (master-orchestrator, gamma-specialist, elevenlabs-specialist, canvas-specialist, quality-reviewer)
6. **Backup Scripts**: Backup scripts exist at `state/runtime/backup/` for disaster recovery of the SQLite database

## Tasks / Subtasks

- [x] Task 1: Create state directory structure (AC: #1, #2, #3)
  - [x] 1.1: Create `state/config/` directory
  - [x] 1.2: Create `state/runtime/` directory
  - [x] 1.3: Create `state/runtime/backup/` directory
  - [x] 1.4: Add `state/runtime/*.db` and `state/runtime/backup/` to `.gitignore`
- [x] Task 2: Create YAML configuration templates (AC: #1, #2, #3)
  - [x] 2.1: Create `state/config/course_context.yaml` with course-level template
  - [x] 2.2: Create `state/config/style_guide.yaml` with brand standards + per-tool parameter sections
  - [x] 2.3: Create `state/config/tool_policies.yaml` with run presets and quality gate config
- [x] Task 3: Create SQLite initialization (AC: #4)
  - [x] 3.1: Create `scripts/state_management/__init__.py`
  - [x] 3.2: Create `scripts/state_management/db_init.py` with schema definitions and initialization function
  - [x] 3.3: Define `production_runs` table (run_id, purpose, status, context_json, started_at, completed_at, preset)
  - [x] 3.4: Define `agent_coordination` table (event_id, run_id, agent_name, action, payload_json, timestamp)
  - [x] 3.5: Define `quality_gates` table (gate_id, run_id, stage, status, reviewer, findings_json, decided_at)
  - [x] 3.6: Create `scripts/state_management/init_state.py` as CLI entry point that creates the DB + YAML files
- [x] Task 4: Create BMad memory sidecar directories (AC: #5)
  - [x] 4.1: Create `_bmad/memory/master-orchestrator-sidecar/` with placeholder `index.md`
  - [x] 4.2: Create `_bmad/memory/gamma-specialist-sidecar/` with placeholder `index.md`
  - [x] 4.3: Create `_bmad/memory/elevenlabs-specialist-sidecar/` with placeholder `index.md`
  - [x] 4.4: Create `_bmad/memory/canvas-specialist-sidecar/` with placeholder `index.md`
  - [x] 4.5: Create `_bmad/memory/quality-reviewer-sidecar/` with placeholder `index.md`
- [x] Task 5: Create backup/restore scripts (AC: #6)
  - [x] 5.1: Create `state/runtime/backup/backup_db.py` that copies coordination.db with timestamp
  - [x] 5.2: Create `state/runtime/backup/restore_db.py` that restores from a specified backup (+ --latest flag)
- [x] Task 6: Validation tests (all ACs)
  - [x] 6.1: Create `tests/test_state_management.py` verifying YAML structure, DB schema, sidecar dirs, and backup ops

## Dev Notes

### Architecture Compliance

**State Management Model** (from architecture):
- **YAML files**: Course context, style guides, tool policies — human-readable, git-versioned in `state/config/`
- **SQLite database**: Runtime coordination state, production run tracking in `state/runtime/`
- **BMad memory sidecars**: Agent learning, expertise patterns, session history in `_bmad/memory/`

**Hybrid Approach Rationale**: YAML for human-editable policies; SQLite for transactional runtime state with ACID guarantees; BMad sidecars for persistent agent learning using existing BMad pattern.

### Existing Repository State (Do Not Break)

| Path | Status | Action |
|------|--------|--------|
| `scripts/__init__.py` | EXISTS (Story 1.2) | Preserve |
| `scripts/api_clients/` | EXISTS (Story 1.2) | Preserve |
| `scripts/utilities/` | EXISTS (Story 1.2) | Preserve |
| `_bmad/` | EXISTS (BMad infrastructure) | Preserve — add `memory/` subdirectories |
| `config/content-standards.yaml` | EXISTS | Preserve — separate from `state/config/` |
| `.gitignore` | EXISTS (updated in 1.2) | Add state/runtime patterns |

### YAML Template Design

**course_context.yaml** structure (from architecture):
```yaml
course:
  name: ""
  code: ""
  description: ""
  audience: ""
  learning_objectives: []
  modules: []
```

**style_guide.yaml** structure — brand standards + per-tool parameter preferences:
```yaml
brand:
  colors: {primary: "", secondary: "", accent: ""}
  fonts: {heading: "", body: ""}
  tone: ""
  audience_level: ""

tool_parameters:
  gamma:
    default_llm: ""
    style: ""
    format: ""
  elevenlabs:
    default_voice_id: ""
    stability: 0.5
    clarity: 0.75
  canvas:
    default_course_id: ""
```

**tool_policies.yaml** structure — run presets per architecture:
```yaml
run_presets:
  explore: {quality_threshold: 0.6, human_review: false}
  draft: {quality_threshold: 0.7, human_review: true}
  production: {quality_threshold: 0.9, human_review: true}
  regulated: {quality_threshold: 0.95, human_review: true, compliance_check: true}
```

### SQLite Schema Design

Tables must support production run lifecycle (FR7-12), quality gate coordination (FR23-27), and agent coordination (FR1-6). Use JSON columns for flexible payload storage. All tables include created_at/updated_at timestamps.

### BMad Memory Sidecar Pattern

Each sidecar directory follows the BMad standard:
- `index.md` — Essential context loaded on activation
- `patterns.md` — Learned preferences (append-only, periodically condensed) — created as placeholder
- `chronology.md` — Session and production run history — created as placeholder
- `access-boundaries.md` — Agent scope control (read/write/deny zones) — created as placeholder

Only create `index.md` with minimal placeholder content; the other files are documented in `index.md` as planned extensions.

### Previous Story Intelligence (Story 1.2)

- Python infrastructure is working: `.venv` with all dependencies, `BaseAPIClient`, utilities
- `scripts/` is a Python package — new `scripts/state_management/` module follows same pattern
- `scripts/utilities/file_helpers.py` provides `project_root()` and `resolve_path()` — reuse these
- `.gitignore` has Python patterns — extend for SQLite and backup files
- ruff lint config in `pyproject.toml` — all new Python code must pass ruff

### Anti-Patterns to Avoid

- Do NOT create production run management logic — that's Story 4.1
- Do NOT create agent coordination protocols — that's Story 2.3
- Do NOT create quality gate coordination logic — that's Story 4.2
- Do NOT populate YAML configs with real course data — templates only
- Do NOT create BMad agent .md files — those are Epic 2-3
- SQLite schema is initialization only — no ORM, no migration framework needed yet

### Testing Requirements

- `tests/test_state_management.py` verifies:
  - All 3 YAML config files exist and parse correctly
  - YAML templates have expected top-level keys
  - SQLite database can be created with all 3 tables
  - Tables have expected columns
  - BMad memory sidecar directories exist with `index.md`
  - Backup script can create a timestamped copy of the database
  - Restore script can recover from a backup

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#State Management] — Hybrid state approach
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure] — state/ directory layout
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.3] — Story requirements and acceptance criteria
- [Source: docs/project-context.md#State Management] — YAML + SQLite + BMad memory confirmed

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent Mode)

### Debug Log References

- All YAML files parse correctly with PyYAML
- SQLite database creates with all 3 tables + indexes via `init_database()`
- Backup/restore roundtrip verified with data integrity
- ruff lint passes with zero errors on all new Python files
- 33/33 Story 1.3 tests pass; 64/64 total Python tests pass (no regressions)

### Completion Notes List

- Created `state/config/course_context.yaml` with course-level template: name, code, description, audience, learning_objectives, modules, delivery_mode
- Created `state/config/style_guide.yaml` with brand section (colors, fonts, tone) and per-tool parameter sections for 8 tools (gamma, elevenlabs, canvas, qualtrics, canva, botpress, wondercraft, kling)
- Created `state/config/tool_policies.yaml` with 4 run presets (explore, draft, production, regulated), quality gates per stage, fallback strategies, and retry policy matching architecture NFRs
- Created `scripts/state_management/db_init.py` with SQLite schema: `production_runs` (11 columns), `agent_coordination` (6 columns + foreign key), `quality_gates` (9 columns + foreign key), plus indexes. WAL journal mode enabled.
- Created `scripts/state_management/init_state.py` CLI tool for one-step state initialization
- Created 5 BMad memory sidecar directories under `_bmad/memory/` with `index.md` files documenting planned sidecar structure, agent references, and access boundaries
- Created `state/runtime/backup/backup_db.py` with timestamped backup creation
- Created `state/runtime/backup/restore_db.py` with restore-from-file and `--latest` auto-discovery
- Added `state/runtime/*.db` and related patterns to `.gitignore`
- Created test suite with 33 assertions covering all 6 acceptance criteria

### Change Log

- 2026-03-26: Story implemented — State management infrastructure with YAML configs, SQLite schema, BMad memory sidecars, and backup/restore. All 6 acceptance criteria satisfied. 33/33 tests pass. Ruff lint clean.

### File List

New files created:
- `state/config/course_context.yaml`
- `state/config/style_guide.yaml`
- `state/config/tool_policies.yaml`
- `state/runtime/.gitkeep`
- `state/runtime/backup/__init__.py`
- `state/runtime/backup/backup_db.py`
- `state/runtime/backup/restore_db.py`
- `scripts/state_management/__init__.py`
- `scripts/state_management/db_init.py`
- `scripts/state_management/init_state.py`
- `_bmad/memory/master-orchestrator-sidecar/index.md`
- `_bmad/memory/gamma-specialist-sidecar/index.md`
- `_bmad/memory/elevenlabs-specialist-sidecar/index.md`
- `_bmad/memory/canvas-specialist-sidecar/index.md`
- `_bmad/memory/quality-reviewer-sidecar/index.md`
- `tests/test_state_management.py`

Modified files:
- `.gitignore` (added state/runtime patterns)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (status updates)
