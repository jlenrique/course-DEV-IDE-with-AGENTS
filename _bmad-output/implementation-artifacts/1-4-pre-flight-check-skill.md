# Story 1.4: Pre-Flight Check Skill

Status: done

## Story

As a user,
I want a pre-flight check skill that verifies all MCPs, APIs, and tool capabilities before production runs,
So that I know the system is ready before starting content creation.

## Acceptance Criteria

1. **Skill Structure**: Pre-flight-check skill exists at `skills/pre-flight-check/SKILL.md` with references/ and scripts/ subdirectories
2. **MCP Connectivity Check**: All configured MCP servers in `.mcp.json` and `.cursor/mcp.json` are tested for connectivity and tool discovery
3. **API Key Validation**: All API keys in `.env` are validated against their respective services with read-only test calls
4. **Existing Script Integration**: `scripts/heartbeat_check.mjs` is incorporated as the baseline API readiness check; targeted smoke scripts (`scripts/smoke_elevenlabs.mjs`, `scripts/smoke_qualtrics.mjs`) are included for API-primary tools
5. **Tool Doc Scanning**: Current tool documentation is scanned via Ref MCP for capability or status changes
6. **Readiness Report**: A comprehensive readiness report is generated with pass/fail status per tool, classifying each as: MCP-ready, API-ready, manual-only, or blocked/deferred
7. **Resolution Guidance**: Resolution guidance is provided for any failures detected
8. **Reference Documentation**: `skills/pre-flight-check/references/` contains diagnostic procedures, tool doc scanning patterns, and a matrix explaining when to rely on MCP checks vs API smoke checks

## Tasks / Subtasks

- [x] Task 1: Create skill directory structure (AC: #1)
  - [x] 1.1: Create `skills/pre-flight-check/SKILL.md` with capability routing and invocation instructions
  - [x] 1.2: Create `skills/pre-flight-check/references/` directory
  - [x] 1.3: Create `skills/pre-flight-check/scripts/` directory
- [x] Task 2: Create Python pre-flight runner (AC: #2, #3, #6, #7)
  - [x] 2.1: Create `skills/pre-flight-check/scripts/preflight_runner.py` as the main orchestrator
  - [x] 2.2: Implement MCP config parser — reads `.mcp.json` and `.cursor/mcp.json` to discover configured MCP servers
  - [x] 2.3: Implement API key presence check — heartbeat_check.mjs SKIP lines detect missing keys
  - [x] 2.4: Implement Node.js script runner — shells out to existing heartbeat and smoke scripts, parses output
  - [x] 2.5: Implement readiness report generator with 6 status tiers (MCP-ready, API-ready, manual-only, blocked/deferred, failed, skipped)
  - [x] 2.6: Implement resolution guidance for 7 failure modes (missing key, auth 401/403, rate limit, connection, timeout, OAuth, manual)
- [x] Task 3: Create reference documentation (AC: #8)
  - [x] 3.1: Create `skills/pre-flight-check/references/diagnostic-procedures.md` with troubleshooting per tool + known blockers table
  - [x] 3.2: Create `skills/pre-flight-check/references/check-strategy-matrix.md` with decision tree and per-tool mapping
  - [x] 3.3: Create `skills/pre-flight-check/references/tool-doc-scanning.md` with Ref MCP scan targets and patterns
- [x] Task 4: Integrate with existing scripts (AC: #4)
  - [x] 4.1: `run_node_script()` invokes `node scripts/heartbeat_check.mjs` and captures stdout/stderr
  - [x] 4.2: Invokes smoke_elevenlabs.mjs and smoke_qualtrics.mjs; appends smoke results to heartbeat entries
  - [x] 4.3: `parse_heartbeat_output()` regex parses PASS/FAIL/SKIP lines into structured dicts
- [x] Task 5: Tool doc scanning capability (AC: #5)
  - [x] 5.1: Create `skills/pre-flight-check/scripts/doc_scanner.py` with ScanTarget dataclass and Ref MCP instructions
  - [x] 5.2: Scan targets defined for Gamma, ElevenLabs, Canvas LMS, Qualtrics, Canva
  - [x] 5.3: `format_scan_prompt()` generates agent-readable prompt; `get_scan_instructions()` returns structured data
- [x] Task 6: Validation tests (all ACs)
  - [x] 6.1: Create `tests/test_preflight_check.py` with 35 test assertions covering all 8 acceptance criteria
  - [x] 6.2: MCP config parsing tested with mock files (project, cursor, merged, missing) + real configs
  - [x] 6.3: Readiness report classification tested for all 6 status tiers + format_report output
  - [x] 6.4: Resolution guidance tested for 7 failure scenarios + default fallback

## Dev Notes

### Architecture Compliance

**Pre-Flight Check (FR66-70)** maps to `skills/pre-flight-check/` + `hooks/hooks.json` sessionStart trigger.

The skill follows the BMad progressive disclosure pattern:
```
skills/pre-flight-check/
├── SKILL.md          # Agent interface — how to invoke, what it does
├── references/       # Diagnostic procedures, strategy matrix, doc scanning
│   ├── diagnostic-procedures.md
│   ├── check-strategy-matrix.md
│   └── tool-doc-scanning.md
└── scripts/          # Python execution code
    ├── preflight_runner.py   # Main orchestrator
    └── doc_scanner.py        # Tool doc scanning via Ref MCP
```

### Pre-Flight Check Strategy (from tool-access-matrix.md)

The tool-access-matrix already defines the validation hierarchy:

| Tool State | Pre-Flight Method |
|---|---|
| Cursor-verified MCP | Check MCP connectivity + tool discovery first |
| API-verified, MCP-deferred | Run focused smoke scripts or read-only API probes |
| Manual-only | Report as manual workflow, not failure |
| Blocked/deferred MCP | Report blocker and route to API or manual path |

Current recommended mapping:

| Tool | Method | Script/Check |
|---|---|---|
| Gamma | MCP + API heartbeat | MCP config check + `heartbeat_check.mjs` |
| Canvas LMS | MCP + API heartbeat | MCP config check + `heartbeat_check.mjs` |
| ElevenLabs | API smoke | `smoke_elevenlabs.mjs` |
| Qualtrics | API smoke | `smoke_qualtrics.mjs` |
| Botpress | API heartbeat | `heartbeat_check.mjs` |
| Wondercraft | API heartbeat | `heartbeat_check.mjs` |
| Kling | Config presence | `heartbeat_check.mjs` |
| Canva | Report OAuth blocker | Static classification |
| Vyond/CourseArc/Articulate | Report manual-only | Static classification |

### Existing Scripts to Integrate

All three scripts are Node.js and output to stdout:
- **`scripts/heartbeat_check.mjs`** — Tests all API-accessible tools. Outputs `PASS:`, `FAIL:`, `SKIP:` lines per tool. Exit code 1 if any failures.
- **`scripts/smoke_elevenlabs.mjs`** — Focused ElevenLabs check: voice listing, voice count. Uses `scripts/lib/load_env.cjs`.
- **`scripts/smoke_qualtrics.mjs`** — Focused Qualtrics check: whoami + survey listing. Uses `scripts/lib/load_env.cjs`.

The Python runner should shell out to these via `subprocess.run()`, capture output, and parse the PASS/FAIL/SKIP pattern.

### MCP Config Parsing

Read both MCP config files to discover configured servers:
- `.mcp.json` (project-level, versioned)
- `.cursor/mcp.json` (local active config)

Both use the same format: `{"mcpServers": {"name": {"command": "...", "args": [...]}}}`. Currently configured: `gamma` and `canvas-lms`, both using `scripts/run_mcp_from_env.cjs` wrapper.

### SKILL.md Design

The SKILL.md should be an agent-readable skill file that:
1. Describes what the pre-flight check does
2. Provides invocation instructions (both manual and via session hook)
3. Routes to references/ for diagnostic details
4. Routes to scripts/ for execution

### Tool Doc Scanning (AC #5)

The doc scanning capability uses the Ref MCP (already available at user level) to:
- Search for recent API changelogs or deprecation notices
- Detect new tool capabilities or parameter changes
- Identify service status issues

This is a **best-effort** capability — the `doc_scanner.py` defines scan targets and patterns, but actual scanning happens when the agent invokes the skill and uses Ref MCP. The Python code prepares the scan instructions; the agent executes them.

### Readiness Report Format

```
═══════════════════════════════════════════
PRE-FLIGHT CHECK RESULTS
═══════════════════════════════════════════

MCP-READY:
  ✓ Gamma — MCP configured, API heartbeat passed
  ✓ Canvas LMS — MCP configured, API heartbeat passed

API-READY:
  ✓ ElevenLabs — API smoke passed (45 voices)
  ✓ Qualtrics — API smoke passed (user authenticated)
  ✓ Botpress — API heartbeat passed

MANUAL-ONLY:
  ○ Vyond — Manual workflow (no API for non-Enterprise)
  ○ CourseArc — LTI/SCORM only
  ○ Articulate — Desktop/web authoring only

BLOCKED/DEFERRED:
  ✗ Canva — OAuth redirect rejected by Cursor

RESOLUTION NEEDED:
  ✗ Wondercraft — FAIL: HTTP 401 (check WONDERCRAFT_API_KEY)

═══════════════════════════════════════════
```

### Existing Repository State (Do Not Break)

| Path | Status | Action |
|---|---|---|
| `scripts/heartbeat_check.mjs` | EXISTS | Integrate, do NOT modify |
| `scripts/smoke_elevenlabs.mjs` | EXISTS | Integrate, do NOT modify |
| `scripts/smoke_qualtrics.mjs` | EXISTS | Integrate, do NOT modify |
| `scripts/lib/load_env.cjs` | EXISTS | Preserve |
| `scripts/run_mcp_from_env.cjs` | EXISTS | Preserve |
| `.mcp.json` / `.cursor/mcp.json` | EXISTS | Read for MCP discovery |
| `hooks/hooks.json` | EXISTS | Preserve — sessionStart already points to placeholder |
| `hooks/scripts/session-start.mjs` | EXISTS | Preserve — placeholder for future hook integration |
| `skills/README.md` | EXISTS | Preserve |
| `resources/tool-inventory/tool-access-matrix.md` | EXISTS | Reference, do NOT modify |
| `scripts/api_clients/` | EXISTS (Story 1.2) | Preserve |
| `scripts/utilities/` | EXISTS (Story 1.2) | Preserve |
| `scripts/state_management/` | EXISTS (Story 1.3) | Preserve |

### Previous Story Intelligence

**Story 1.1**: Created hook scripts as Node.js `.mjs` for Windows compatibility. The `session-start.mjs` is a placeholder that logs and returns JSON — future hook integration with pre-flight is deferred to Epic 2 when the orchestrator can invoke it.

**Story 1.2**: Python infrastructure with `BaseAPIClient`, `env_loader`, `logging_setup`, `file_helpers`. The pre-flight runner should use `scripts.utilities` for path resolution and logging.

**Story 1.3**: State management with YAML configs and SQLite. Not directly used by pre-flight, but the tool_policies.yaml retry_policy matches the retry logic here.

### Anti-Patterns to Avoid

- Do NOT modify existing Node.js scripts — wrap them, don't rewrite them
- Do NOT attempt to actually connect to MCP servers from Python (MCP protocol is handled by Cursor) — just verify the config files are present and well-formed
- Do NOT create the master orchestrator integration (Story 2.5 handles that)
- Do NOT modify `hooks/hooks.json` or hook scripts — Story 2.5 wires the orchestrator
- Do NOT hardcode API keys or secrets
- Do NOT create actual API clients for individual tools — those are Stories 1.6-1.11

### Testing Requirements

Tests should verify:
- Skill directory structure (SKILL.md, references/, scripts/)
- MCP config parsing extracts server names and validates structure
- Heartbeat script output parsing correctly identifies PASS/FAIL/SKIP
- Readiness report classifies tools correctly
- Resolution guidance maps failure types to actionable advice
- All Python code passes ruff lint

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Pre-Flight Check] — FR66-70 mapping
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.4] — Story requirements and ACs
- [Source: resources/tool-inventory/tool-access-matrix.md#Pre-Flight Check Guidance] — Check strategy matrix
- [Source: scripts/heartbeat_check.mjs] — Baseline heartbeat script
- [Source: scripts/smoke_elevenlabs.mjs] — ElevenLabs smoke check
- [Source: scripts/smoke_qualtrics.mjs] — Qualtrics smoke check

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent Mode)

### Debug Log References

- 35/35 Story 1.4 tests pass
- 99/99 total Python tests pass across all stories (zero regressions)
- ruff lint clean on all new Python files
- conftest.py created to handle dashed directory name import (`skills/pre-flight-check/` → `skills.pre_flight_check.scripts`)
- MCP config parsing verified against real `.mcp.json` and `.cursor/mcp.json`

### Completion Notes List

- Created `skills/pre-flight-check/SKILL.md` following BMad progressive disclosure pattern with invocation instructions, check matrix, and reference routing
- Created `skills/pre-flight-check/scripts/preflight_runner.py` — main orchestrator with: MCP config parser, Node.js script runner, heartbeat output parser (regex), readiness report generator (6 status tiers), resolution guidance (7 failure patterns)
- Created `skills/pre-flight-check/scripts/doc_scanner.py` — defines 5 scan targets (Gamma, ElevenLabs, Canvas, Qualtrics, Canva) with search queries and focus areas for Ref MCP
- Created 3 reference documents: diagnostic-procedures.md (troubleshooting per tool + known blockers), check-strategy-matrix.md (decision tree + per-tool mapping), tool-doc-scanning.md (Ref MCP patterns + scan frequency guidance)
- Integrated existing Node.js scripts via `subprocess.run()` — heartbeat_check.mjs as baseline, smoke scripts for ElevenLabs and Qualtrics
- Created `tests/conftest.py` to register skill scripts with dashed directory names for clean Python imports
- Created test suite with 35 assertions covering all 8 acceptance criteria

### Change Log

- 2026-03-26: Story implemented — Pre-flight check skill with SKILL.md, Python runner, doc scanner, 3 reference docs, and 35 passing tests. All 8 acceptance criteria satisfied.

### File List

New files created:
- `skills/pre-flight-check/SKILL.md`
- `skills/pre-flight-check/scripts/__init__.py`
- `skills/pre-flight-check/scripts/preflight_runner.py`
- `skills/pre-flight-check/scripts/doc_scanner.py`
- `skills/pre-flight-check/references/diagnostic-procedures.md`
- `skills/pre-flight-check/references/check-strategy-matrix.md`
- `skills/pre-flight-check/references/tool-doc-scanning.md`
- `tests/conftest.py`
- `tests/test_preflight_check.py`

Modified files:
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (status updates)
