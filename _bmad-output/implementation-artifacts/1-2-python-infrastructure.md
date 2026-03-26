# Story 1.2: Python Infrastructure & Environment Configuration

Status: done

## Story

As a developer,
I want a Python development environment with API key management and dependency isolation,
So that agent skills can execute Python scripts for tool integration and state management.

## Acceptance Criteria

1. **Virtual Environment**: A `.venv` virtual environment is created with all dependencies from `requirements.txt`, using Python 3.10+
2. **Environment Template**: `.env.example` provides a complete template with documented entries for all API-capable tools — **ALREADY COMPLETE from Story 1.1; verify and preserve**
3. **API Client Base**: `scripts/api_clients/` contains a base API client class with authenticated session management, exponential backoff retry logic (3 attempts: 2s, 4s, 8s), and error handling patterns
4. **Utilities Module**: `scripts/utilities/` contains shared helper functions for file operations, logging setup, and .env loading
5. **Dependency Verification**: Automated dependency verification confirms all packages install correctly in the virtual environment
6. **Project Packaging**: `pyproject.toml` and `requirements.txt` define project metadata and pinned dependencies

## Tasks / Subtasks

- [x] Task 1: Create Python project packaging files (AC: #6)
  - [x] 1.1: Create `pyproject.toml` with project metadata, Python >=3.10 requirement, and dependency list
  - [x] 1.2: Create `requirements.txt` with pinned versions for: `requests`, `python-dotenv`, `pydantic`, `aiohttp`, `pyyaml`, `pytest`, `pytest-asyncio`, `ruff`
  - [x] 1.3: Add `dev` optional dependency group in pyproject.toml for test/lint tools
- [x] Task 2: Create and configure virtual environment (AC: #1)
  - [x] 2.1: Create `.venv` using `python -m venv .venv`
  - [x] 2.2: Install dependencies from `requirements.txt` into `.venv`
  - [x] 2.3: Add `.venv/` to `.gitignore`
  - [x] 2.4: Add `__pycache__/`, `*.pyc`, `*.pyo`, `.pytest_cache/`, `*.egg-info/` to `.gitignore`
- [x] Task 3: Create scripts package structure (AC: #3, #4)
  - [x] 3.1: Create `scripts/api_clients/__init__.py` with package docstring
  - [x] 3.2: Create `scripts/api_clients/base_client.py` with `BaseAPIClient` class
  - [x] 3.3: Create `scripts/utilities/__init__.py` with package docstring
  - [x] 3.4: Create `scripts/utilities/logging_setup.py` with standardized logging configuration
  - [x] 3.5: Create `scripts/utilities/env_loader.py` with Python-native .env loading
  - [x] 3.6: Create `scripts/utilities/file_helpers.py` with path resolution and safe file operations
  - [x] 3.7: Create `scripts/__init__.py` to make scripts a package
- [x] Task 4: Implement BaseAPIClient (AC: #3)
  - [x] 4.1: Implement authenticated session with configurable auth header patterns (Bearer, X-API-KEY, custom)
  - [x] 4.2: Implement exponential backoff retry (3 attempts: 2s, 4s, 8s delays) with configurable retry-able status codes
  - [x] 4.3: Implement standard error handling with clear diagnostic messages for auth failures, rate limits, timeouts
  - [x] 4.4: Implement request/response logging at DEBUG level
  - [x] 4.5: Add type hints for all public methods and return values
- [x] Task 5: Verify .env.example completeness (AC: #2)
  - [x] 5.1: Confirmed .env.example covers all 15 tools — already complete from Story 1.1
  - [x] 5.2: No modifications needed
- [x] Task 6: Automated dependency verification (AC: #5)
  - [x] 6.1: Create `tests/test_python_infrastructure.py` to verify all imports succeed
  - [x] 6.2: Verify BaseAPIClient instantiates correctly with mock configuration
  - [x] 6.3: Verify utilities module imports and basic function operation
  - [x] 6.4: Verify .venv is functional and dependencies resolve

## Dev Notes

### Architecture Compliance

**Python Infrastructure Role**: Supporting code for API clients, state management, and file operations — invoked from agent skills when code execution is required. Scripts use Python for deterministic operations; agents remain .md files for reasoning.

**Script Execution Model**: Agents invoke Python scripts in `scripts/` directories via Cursor's terminal. PEP 723 inline metadata is planned for self-contained dependency declarations in individual scripts, but `requirements.txt` provides the shared baseline.

**Directory Layout from Architecture**:
```
scripts/                         # Shared Python infrastructure
├── __init__.py
├── api_clients/                 # Tool API client libraries
│   ├── __init__.py
│   └── base_client.py           # THIS STORY
├── state_management/            # SQLite + YAML (Story 1.3)
└── utilities/                   # Shared utility functions
    ├── __init__.py
    ├── logging_setup.py
    ├── env_loader.py
    └── file_helpers.py
```

### Existing Repository State (CRITICAL — Do Not Break)

| Path | Status | Action |
|------|--------|--------|
| `scripts/heartbeat_check.mjs` | EXISTS | Preserve — Node.js heartbeat script |
| `scripts/smoke_elevenlabs.mjs` | EXISTS | Preserve — Node.js smoke check |
| `scripts/smoke_qualtrics.mjs` | EXISTS | Preserve — Node.js smoke check |
| `scripts/run_mcp_from_env.cjs` | EXISTS | Preserve — MCP env wrapper |
| `scripts/lib/load_env.cjs` | EXISTS | Preserve — Node.js env loader |
| `.env.example` | EXISTS (complete, 120 lines) | Verify, do NOT modify unless gap found |
| `.cursor-plugin/plugin.json` | EXISTS | Preserve |
| `.mcp.json` / `.cursor/mcp.json` | EXISTS | Preserve |
| `hooks/` | EXISTS | Preserve |
| `agents/`, `skills/`, `commands/`, `rules/` | EXISTS | Preserve |
| `config/content-standards.yaml` | EXISTS | Preserve |
| All `_bmad/` and `_bmad-output/` | EXISTS | Preserve |

### BaseAPIClient Design

The base client should follow the architecture's API client pattern:

```python
class BaseAPIClient:
    """Base API client with session management, retry logic, and error handling."""

    def __init__(
        self,
        base_url: str,
        auth_header: str = "Authorization",
        auth_prefix: str = "Bearer",
        api_key: str | None = None,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None: ...

    def get(self, endpoint: str, **kwargs) -> dict: ...
    def post(self, endpoint: str, **kwargs) -> dict: ...
    def put(self, endpoint: str, **kwargs) -> dict: ...
    def delete(self, endpoint: str, **kwargs) -> dict: ...
```

Auth header patterns needed across tools:
- `Authorization: Bearer {token}` — Canvas, Botpress, Descript
- `X-API-KEY: {key}` — Gamma, Wondercraft
- `xi-api-key: {key}` — ElevenLabs
- `X-API-TOKEN: {key}` — Qualtrics

Retry logic per architecture NFRs: exponential backoff with 3 attempts at 2s, 4s, 8s delays. Retry on 429 (rate limit), 500, 502, 503, 504.

### Python Version Note

System Python is 3.13 via pyenv. Architecture specifies Python 3.10+ minimum. Use system Python 3.13 for the venv. The `.venv` approach avoids version conflicts with other projects.

### Dependency Selection Rationale

| Package | Purpose | Why |
|---------|---------|-----|
| `requests` | Sync HTTP client | Standard for API clients, matches existing patterns |
| `python-dotenv` | .env file loading | Standard Python .env support |
| `pydantic` | Data validation | Type-safe configuration and API response models |
| `aiohttp` | Async HTTP client | Future async agent coordination (subagents-pydantic-ai) |
| `pyyaml` | YAML config files | State management config in Story 1.3 |
| `pytest` | Testing framework | Per project standards |
| `pytest-asyncio` | Async test support | For async API client tests |
| `ruff` | Linting + formatting | Fast Python linter, replaces flake8+black |

**NOT including yet** (future stories):
- `subagents-pydantic-ai` — Epic 2 (orchestrator agent coordination)
- `aiosqlite` — Story 1.3 (state management)

### Anti-Patterns to Avoid

- Do NOT create actual tool-specific API clients (Gamma, ElevenLabs, Canvas) — those are Stories 1.6-1.8
- Do NOT create state management code (SQLite, YAML config) — that's Story 1.3
- Do NOT modify existing Node.js scripts — they coexist with Python infrastructure
- Do NOT hardcode any API keys or secrets
- Do NOT create a `setup.py` — use modern `pyproject.toml` only
- Do NOT delete `scripts/.gitkeep` if it exists (it may already be gone, that's fine)

### Testing Requirements

- `tests/test_python_infrastructure.py` verifies:
  - All Python packages import successfully
  - `BaseAPIClient` instantiates with mock config
  - Retry logic works with simulated failures (mock HTTP responses)
  - Utilities module functions work correctly
  - `.env` loading works (using `.env.example` as template)
- Run tests with: `python -m pytest tests/test_python_infrastructure.py -v`

### Project Structure Notes

- `scripts/` directory already contains Node.js files — Python packages coexist alongside them
- `scripts/__init__.py` makes the directory importable as a Python package without breaking Node.js usage
- `scripts/api_clients/` is NEW — base client only, no tool-specific clients yet
- `scripts/utilities/` is NEW — logging, env loading, file helpers
- `scripts/state_management/` is NOT created yet — that's Story 1.3

### Previous Story Intelligence (Story 1.1)

- Story 1.1 created the Cursor plugin scaffold: `.cursor-plugin/plugin.json`, `.mcp.json`, hooks, directories
- Used cross-platform Node.js `.mjs` hook scripts instead of .sh for Windows compatibility
- Created `scripts/run_mcp_from_env.cjs` to load `.env` secrets at runtime for MCP servers
- `.gitignore` currently only covers `.env`, `.DS_Store`, `Thumbs.db`, and `secrets/` — needs Python patterns added
- 34/35 Story 1.1 validation tests pass (1 benign failure: `.gitkeep` superseded by real files)

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Python Infrastructure] — Python infrastructure role and script execution model
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure] — Directory layout with scripts/, api_clients/, utilities/
- [Source: _bmad-output/planning-artifacts/architecture.md#Anti-Patterns] — Skills framework requirement for API calls
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.2] — Story requirements and acceptance criteria
- [Source: resources/tool-inventory/tool-access-matrix.md] — Auth header patterns per tool
- [Source: docs/project-context.md#Key Decisions] — Python 3.10+, pip packaging, virtual environment isolation

## Dev Agent Record

### Agent Model Used

claude-4.6-opus (Cursor Agent Mode)

### Debug Log References

- All Python packages installed successfully via pip into `.venv`
- ruff lint passes with zero errors across all Python files
- 31/31 pytest tests pass covering all 6 acceptance criteria
- Story 1.1 regression check: 34/35 tests still pass (same benign `.gitkeep` failure)

### Completion Notes List

- Created `pyproject.toml` with Python >=3.10, dependency ranges, ruff config, and pytest config
- Created `requirements.txt` with 8 packages: requests, aiohttp, python-dotenv, pydantic, pyyaml, pytest, pytest-asyncio, ruff
- Created `.venv` with Python 3.13.6, all dependencies installed successfully
- Added Python gitignore patterns: `.venv/`, `__pycache__/`, `*.pyc`, `*.pyo`, `.pytest_cache/`, `.ruff_cache/`, `*.egg-info/`, `dist/`, `build/`
- Created `scripts/__init__.py` making scripts directory a Python package while coexisting with Node.js files
- Created `scripts/api_clients/base_client.py` with `BaseAPIClient` supporting configurable auth headers (Bearer, X-API-KEY, xi-api-key, X-API-TOKEN), exponential backoff retry (2s, 4s, 8s), and structured error hierarchy (`APIError`, `AuthenticationError`, `RateLimitError`)
- Created `scripts/utilities/env_loader.py` with Python-native .env loading matching Node.js `load_env.cjs` behavior
- Created `scripts/utilities/logging_setup.py` with standardized log formatting, optional file output, and configurable levels for FR40 development mode
- Created `scripts/utilities/file_helpers.py` with `project_root()`, `resolve_path()`, `safe_read_json()`, `safe_write_json()` helpers
- Verified `.env.example` is already complete from Story 1.1 — no modifications needed
- Created comprehensive test suite at `tests/test_python_infrastructure.py` with 31 test assertions covering venv, imports, BaseAPIClient (7 behavioral tests), utilities (7 tests), packaging, env template, and gitignore

### Change Log

- 2026-03-26: Story implemented — Python infrastructure created with venv, packaging, BaseAPIClient, utilities, and 31 passing tests. All 6 acceptance criteria satisfied. Ruff lint clean.

### File List

New files created:
- `pyproject.toml`
- `requirements.txt`
- `scripts/__init__.py`
- `scripts/api_clients/__init__.py`
- `scripts/api_clients/base_client.py`
- `scripts/utilities/__init__.py`
- `scripts/utilities/env_loader.py`
- `scripts/utilities/logging_setup.py`
- `scripts/utilities/file_helpers.py`
- `tests/test_python_infrastructure.py`
- `.venv/` (not tracked in git)

Modified files:
- `.gitignore` (added Python patterns)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (status updates)
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` (next step updated)
