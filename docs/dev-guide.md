# Developer Guide — Architecture, Execution Flow, and Extension Points

**Audience:** Developers building, extending, and maintaining the collaborative intelligence platform.
**Last Updated:** 2026-03-26 | **Project Phase:** Epic 2 (Master Orchestrator in progress)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Three-Layer Architecture](#three-layer-architecture)
3. [Typical Run Walk-Through](#typical-run-walk-through)
4. [State Management Deep Dive](#state-management-deep-dive)
5. [Configuration Cascade](#configuration-cascade)
6. [Agent Anatomy](#agent-anatomy)
7. [Skill Anatomy](#skill-anatomy)
8. [API Client Anatomy](#api-client-anatomy)
9. [Extension Guide: Adding New Capabilities](#extension-guide-adding-new-capabilities)
10. [Testing](#testing)
11. [Coding Standards and Patterns](#coding-standards-and-patterns)
12. [Project File Map](#project-file-map)
13. [Key Reference Documents](#key-reference-documents)

---

## Architecture Overview

This project is a **multi-agent collaborative intelligence platform** for medical education course content production. The core concept: a master orchestrator agent (Marcus) conducts a conversation with the user, delegates to specialist agents, which invoke skills backed by Python scripts, which call external tool APIs. Results flow back up the chain through quality gates and human checkpoints.

```
┌─────────────────────────────────────────────────────┐
│                    USER (Cursor Chat)                │
│            "Create slides for Module 2"              │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              MARCUS (Master Orchestrator)            │
│  • Parses intent        • Reads style bible fresh   │
│  • Selects specialist   • Manages checkpoint gates  │
│  • Passes context envelope to specialist             │
└──────────────────────┬──────────────────────────────┘
                       │ delegates
                       ▼
┌─────────────────────────────────────────────────────┐
│           SPECIALIST AGENT (e.g. Gamma)             │
│  • Loads SKILL.md       • Reads references/         │
│  • Applies tool mastery • Makes parameter decisions │
└──────────────────────┬──────────────────────────────┘
                       │ invokes
                       ▼
┌─────────────────────────────────────────────────────┐
│             SKILL (e.g. gamma-api-mastery)           │
│  • SKILL.md routing     • references/ for details   │
│  • scripts/ for execution (Python API calls)        │
└──────────────────────┬──────────────────────────────┘
                       │ calls
                       ▼
┌─────────────────────────────────────────────────────┐
│          API CLIENT (e.g. GammaClient)              │
│  • Authenticated session  • Retry with backoff      │
│  • Pagination             • Structured errors       │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP
                       ▼
┌─────────────────────────────────────────────────────┐
│              EXTERNAL TOOL API (Gamma)              │
└─────────────────────────────────────────────────────┘
```

---

## Three-Layer Architecture

The system is built on three independently updatable layers. This separation is the most important architectural concept in the project.

| Layer | Location | Responsibility | Lifecycle |
|-------|----------|---------------|-----------|
| **API Clients** | `scripts/api_clients/` | Connectivity, retry, auth, pagination | Built in Epic 1 (DONE) |
| **Skills** | `skills/{name}/` | Tool expertise, parameter templates, execution orchestration | Built in Epic 3+ |
| **Agents** | `skills/bmad-agent-{name}/` or `agents/` | Judgment, decision-making, personality, memory | Built in Epic 2+ |

**Why this matters:** You can fix an API client without touching any agent or skill. You can refine a skill's parameter templates without changing the API client it wraps. You can update an agent's personality or routing without modifying any skill code. Each layer evolves at its own pace.

### Layer Interaction Pattern

```
Agent (.md)  ──reads──>  Skill (SKILL.md + references/)  ──invokes──>  Script (.py)  ──calls──>  API Client
     │                            │                                          │
     │                            │                                          │
     └── judgment, routing        └── tool expertise, templates              └── HTTP, retry, auth
```

---

## Typical Run Walk-Through

Here's what happens step-by-step when a user says: **"Marcus, create a presentation on drug interactions for Module 2, Lesson 3."**

### Phase 1: Intent Parsing (Marcus)

1. Marcus receives the user message in Cursor agent chat
2. Marcus loads `./references/conversation-mgmt.md` (CM capability)
3. Marcus parses the intent:
   - **Content type:** presentation (slides)
   - **Topic:** drug interactions
   - **Scope:** Module 2, Lesson 3
   - **Implied specialist:** Gamma (slide generation)
4. Marcus reads `state/config/course_context.yaml` to resolve Module 2, Lesson 3 metadata and learning objectives
5. Marcus checks current run mode (default vs. ad-hoc) from `state/runtime/` or via `./scripts/read-mode-state.py`

### Phase 2: Source Material Prompting (Marcus → SP capability)

6. Marcus loads `./references/source-prompting.md` (SP capability)
7. Marcus offers: *"I see Module 2 notes in Notion and some reference PDFs in Box Drive. Want me to pull those in before we start?"*
8. If user accepts, Marcus delegates to the `source-wrangling` skill (planned) to fetch Notion pages and Box Drive files

### Phase 3: Production Planning (Marcus → CM capability)

9. Marcus reads `resources/style-bible/master-style-bible.md` **fresh from disk** — never cached
10. Marcus reads `resources/exemplars/` for any relevant worked patterns
11. Marcus reads `state/config/style_guide.yaml` for Gamma-specific parameter preferences
12. Marcus reads `state/config/tool_policies.yaml` to determine the active run preset (e.g., `draft`)
13. Marcus builds a **production plan**: what needs to be created, which specialist handles it, what quality gates apply
14. Marcus presents the plan to the user for confirmation

### Phase 4: Specialist Delegation (Marcus → Gamma Specialist)

15. Marcus builds a **context envelope** containing:
    - Production run ID
    - Content type: presentation
    - Module/lesson identifier: M2-L3
    - Learning objectives from course_context.yaml
    - User constraints (from conversation)
    - Relevant style bible sections (color palette, typography, Gamma prompt template)
    - Applicable exemplar references
16. Marcus delegates to the `gamma-specialist` agent
17. The Gamma specialist loads its own SKILL.md, reads `references/` for parameter mastery details
18. The specialist determines optimal Gamma parameters:
    - First: check `state/config/style_guide.yaml` for saved preferences
    - Second: apply context inference (medical content → specific LLM, style, format choices)
    - Third: if missing critical parameters, escalate back to Marcus for conversational elicitation

### Phase 5: Tool Execution (Specialist → Skill → API Client)

19. The Gamma specialist invokes Python scripts in `skills/gamma-api-mastery/scripts/`
20. The script instantiates `GammaClient` from `scripts/api_clients/gamma_client.py`
21. `GammaClient.generate()` sends the API request with all parameters
22. `GammaClient.wait_for_generation()` polls until completion (3s intervals, up to 120 attempts)
23. The generated presentation data is returned to the specialist

### Phase 6: Quality Review (Specialist → Quality Gate)

24. The specialist performs a self-assessment against style bible standards
25. The specialist returns to Marcus:
    - Artifact path (where the presentation was saved)
    - Quality self-assessment score
    - Parameter decisions made (for saving to style guide)
26. Marcus invokes the `quality-reviewer` agent (planned) for independent quality validation
27. Quality reviewer checks: brand consistency, accessibility (WCAG 2.1 AA), learning objective alignment

### Phase 7: Human Checkpoint (Marcus → User)

28. Marcus loads `./references/checkpoint-coord.md` (HC capability)
29. Marcus presents the work to the user:
    - *"Slides are done — 12 frames covering all three learning objectives for drug interactions. JCPH Navy headers, Medical Teal accents. Quality review passed. Ready for your review."*
30. User reviews and either approves, requests changes, or redirects

### Phase 8: State Updates (if default mode)

31. If approved and in **default mode**:
    - Content saved to `course-content/staging/m02-drug-interactions/`
    - SQLite `production_runs` table updated with run completion
    - SQLite `quality_gates` table updated with review results
    - Marcus's memory sidecar `patterns.md` appended with what worked
    - Marcus's `chronology.md` appended with session record
    - `state/config/style_guide.yaml` updated with any new parameter preferences
32. If in **ad-hoc mode**:
    - Content saved to scratch/staging area
    - No state writes except transient section of Marcus's `index.md`
    - QA results still recorded (QA always runs)

### Phase 9: Promotion (User-Directed)

33. User reviews content in staging
34. User tells Marcus to promote: *"Looks good, promote to courses"*
35. Content moves from `course-content/staging/` to `course-content/courses/`
36. Platform publishing follows (Canvas API deployment, etc.)

---

## State Management Deep Dive

### The Three Tiers

```
┌─────────────────────────────────────────────┐
│  YAML Configuration (state/config/)         │  ← Git-versioned, human-readable
│  • course_context.yaml                      │  ← Evolves slowly
│  • style_guide.yaml                         │  ← Agent-writable (learned prefs)
│  • tool_policies.yaml                       │  ← Admin-managed (run presets)
├─────────────────────────────────────────────┤
│  SQLite Runtime (state/runtime/)            │  ← Gitignored, ephemeral
│  • coordination.db                          │  ← Production runs, coordination,
│    - production_runs table                  │    quality gates
│    - agent_coordination table               │  ← Does NOT survive fresh clone
│    - quality_gates table                    │
├─────────────────────────────────────────────┤
│  Memory Sidecars (_bmad/memory/)            │  ← Git-versioned, append-only
│  • {agent}-sidecar/                         │  ← Agent learning, expertise
│    - index.md (context)                     │    crystallization
│    - patterns.md (learned patterns)         │  ← Mode-aware write rules
│    - chronology.md (history)                │
│    - access-boundaries.md (scope)           │
└─────────────────────────────────────────────┘
```

### Mode-Aware Write Rules

The ad-hoc/default mode switch is a **gate on the state management layer**, not on agents. Agents behave identically in both modes — the infrastructure handles routing:

| State Target | Default Mode | Ad-Hoc Mode |
|-------------|:------------:|:-----------:|
| SQLite tables | Full write | Suppressed |
| YAML configs | Full write | Suppressed |
| Memory sidecar `patterns.md` | Append | Read-only |
| Memory sidecar `chronology.md` | Append | Read-only |
| Memory sidecar `index.md` | Full write | Transient section only |
| Memory sidecar `access-boundaries.md` | Read-only | Read-only |
| Quality gate execution | Always | Always |
| Asset output | `course-content/staging/` | Scratch/staging area |

---

## Configuration Cascade

When an agent needs information, the resolution order matters. Higher priority wins.

| Priority | Source | What It Provides |
|----------|--------|-----------------|
| **1** | `resources/style-bible/` | Brand colors, typography, imagery, voice/tone, accessibility |
| **2** | `state/config/style_guide.yaml` | Tool parameter preferences (voice IDs, LLM choices, format prefs) |
| **3** | `state/config/course_context.yaml` | Course hierarchy and learning objectives |
| **4** | `state/config/tool_policies.yaml` | Run presets, quality thresholds, retry policy |
| **5** | `resources/exemplars/` | Platform allocation patterns (reference, not config) |
| **6** | `config/content-standards.yaml` | Fallback defaults (only if no style bible exists) |
| **7** | `_bmad/memory/{agent}-sidecar/patterns.md` | Learned preferences from past runs |

**Critical anti-patterns** (from `docs/directory-responsibilities.md`):
- Never store brand identity in `state/config/style_guide.yaml` — that's for tool dial settings only
- Never cache style bible content in agent memory — always re-read from disk
- Never write to `config/` or `resources/` from agent logic — these are human-curated

---

## Agent Anatomy

Agents are `.md` files created through the `bmad-agent-builder` six-phase discovery process. They follow the BMad SKILL.md standard.

### Structure of an Agent File

```markdown
---
name: bmad-agent-marcus
description: Creative Production Orchestrator for health sciences / medical education...
---

# Marcus

## Overview          ← What this agent does and how it operates
## Identity          ← Persona, domain expertise, disposition
## Communication Style ← How the agent talks to the user
## Principles        ← Decision-making rules (numbered, non-negotiable)
## Does Not Do       ← Explicit boundary — what the agent refuses to touch
## On Activation     ← Startup sequence (load config, memory, greet user)
## Capabilities      ← Routing tables:
  ### Internal       ← Capabilities handled by loading reference docs
  ### External Skills ← Delegated to other skills
  ### External Agents ← Delegated to specialist agents
```

### The Context Envelope

When Marcus delegates to a specialist, he passes a structured context envelope:

| Field | Purpose |
|-------|---------|
| Production run ID | Tracking and state management |
| Content type | What's being created (presentation, assessment, etc.) |
| Module/lesson identifier | Scope within the course hierarchy |
| User constraints | From the conversation (time limits, style preferences, etc.) |
| Style bible sections | Relevant brand standards for this task |
| Exemplar references | Applicable worked patterns |

Specialists return: **artifact path** + **quality self-assessment** + **parameter decisions to save**.

### Memory Sidecar Structure

Each agent gets a memory sidecar at `_bmad/memory/{agent}-sidecar/`:

```
{agent}-sidecar/
├── index.md              ← Entry point. Marcus loads this first on activation
├── access-boundaries.md  ← Read/write/deny zones (set at build time)
├── patterns.md           ← Learned patterns (append-only, default mode)
└── chronology.md         ← Session/run history (append-only, default mode)
```

The `index.md` tells the agent what else to load. This progressive disclosure pattern keeps activation fast — agents don't read their full history on every startup.

---

## Skill Anatomy

Skills are SKILL.md directories that provide tool-specific capabilities with progressive disclosure.

### Structure

```
skills/{skill-name}/
├── SKILL.md              ← Frontmatter (name + description) + routing + invocation
├── references/           ← Detailed capability docs loaded on demand
│   ├── diagnostic-procedures.md
│   ├── check-strategy-matrix.md
│   └── ...
└── scripts/              ← Python code for execution
    ├── preflight_runner.py
    └── ...
```

### SKILL.md Frontmatter

```yaml
---
name: pre-flight-check
description: "Verify all MCPs, APIs, and tool capabilities before production runs..."
---
```

The `name` and `description` fields drive auto-discovery by the Cursor plugin system.

### Progressive Disclosure Pattern

Skills load only what they need:
1. **SKILL.md** is always loaded — contains routing and high-level instructions
2. **references/** files are loaded on demand when a specific capability is invoked
3. **scripts/** are executed only when code needs to run

This keeps context windows manageable — agents don't load 50 pages of reference docs when they only need one capability.

### Current Skills

| Skill | Location | Status |
|-------|----------|--------|
| `pre-flight-check` | `skills/pre-flight-check/` | Active |
| `bmad-agent-marcus` | `skills/bmad-agent-marcus/` | Active (Epic 2) |
| `production-coordination` | planned | Epic 4 |
| `run-reporting` | planned | Epic 4 |
| `parameter-intelligence` | planned | Epic 3 |
| `source-wrangling` | planned | Epic 3 |
| `gamma-api-mastery` | planned | Epic 3 |
| `elevenlabs-audio` | planned | Epic 3 |
| `canvas-deployment` | planned | Epic 3 |
| `quality-control` | planned | Epic 4 |

---

## API Client Anatomy

All API clients extend `BaseAPIClient` in `scripts/api_clients/base_client.py`.

### BaseAPIClient Provides

| Feature | Implementation |
|---------|---------------|
| **Authenticated sessions** | Configurable auth patterns (Bearer, X-API-KEY, xi-api-key, X-API-TOKEN) |
| **Retry with backoff** | 3 attempts, 2s/4s/8s delays, respects Retry-After header |
| **Retryable status codes** | 429, 500, 502, 503, 504 |
| **Structured errors** | `APIError`, `AuthenticationError`, `RateLimitError` with status code and response body |
| **Pagination** | Link-header (Canvas-style) via `get_paginated()` |
| **Raw responses** | `get_raw()` / `post_raw()` for binary content (audio, etc.) |
| **JSON parsing** | Automatic with fallback for non-JSON responses |

### Creating a New Client

```python
"""NewTool API client.

API Docs: https://docs.newtool.com
Auth: Authorization: Bearer {token}
"""
from scripts.api_clients.base_client import BaseAPIClient
import os

class NewToolClient(BaseAPIClient):
    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or os.environ.get("NEWTOOL_API_KEY", "")
        super().__init__(
            base_url="https://api.newtool.com/v1",
            auth_header="Authorization",
            auth_prefix="Bearer",
            api_key=api_key,
        )

    def list_items(self) -> list[dict]:
        """List available items."""
        return self.get("/items")

    def create_item(self, content: str, **params) -> dict:
        """Create a new item."""
        return self.post("/items", json={"content": content, **params})
```

### Existing Clients

| Client | File | Auth Pattern | Key Features |
|--------|------|-------------|-------------|
| `GammaClient` | `gamma_client.py` | X-API-KEY (raw) | Themes, generation, polling for completion |
| `ElevenLabsClient` | `elevenlabs_client.py` | xi-api-key (raw) | TTS, voice listing, file output (binary) |
| `CanvasClient` | `canvas_client.py` | Bearer token | Pagination (Link header), modules, pages, assignments |
| `QualtricsClient` | `qualtrics_client.py` | X-API-TOKEN (raw) | Surveys, questions, response export |
| `PanoptoClient` | `panopto_client.py` | Bearer (OAuth2) | Folders, sessions, OAuth2 token refresh |

---

## Extension Guide: Adding New Capabilities

This is where you come in. The three-layer architecture means there are three distinct extension points, each with its own recipe.

### Recipe 1: Adding a New API Client

**When:** A new tool needs programmatic access (Tier 1-3 in the tool inventory).

**Steps:**

1. Create `scripts/api_clients/{tool}_client.py` extending `BaseAPIClient`
2. Use the appropriate auth pattern for the tool (check API docs)
3. Add env vars to `.env` and `.env.example`
4. Add integration test in `tests/test_integration_{tool}.py`
5. Update `resources/tool-inventory/tool-access-matrix.md`
6. Add tool parameter section in `state/config/style_guide.yaml`
7. Run tests: `.venv\Scripts\python -m pytest tests/test_integration_{tool}.py -v`

**Template:** Use `scripts/api_clients/gamma_client.py` as the canonical example — it demonstrates generation, polling, and clean parameter handling.

### Recipe 2: Adding a New Skill

**When:** A tool capability needs orchestration logic, parameter intelligence, or reference documentation beyond what the raw API client provides.

**Steps:**

1. Create directory: `skills/{skill-name}/`
2. Create `SKILL.md` with frontmatter (`name`, `description` with trigger phrases)
3. Create `references/` with detailed capability docs (loaded on demand)
4. Create `scripts/` with Python execution code (imports from `scripts/api_clients/`)
5. If the skill serves Marcus: add it to Marcus's External Skills routing table in `skills/bmad-agent-marcus/SKILL.md`
6. Follow PEP 723 for script dependency declarations

**Template:** Use `skills/pre-flight-check/` as the canonical example — it demonstrates the full SKILL.md + references/ + scripts/ pattern with clear invocation instructions.

**Key principle:** Skills are the bridge between agent reasoning (.md) and code execution (.py). The SKILL.md provides the "what and when"; references/ provide the "how in detail"; scripts/ provide the "execute this."

### Recipe 3: Adding a New Agent

**When:** A new domain needs autonomous judgment, personality, and memory — not just tool execution.

**Steps:**

1. **Party Mode coaching** — Run a team session (Winston, Mary, John, Sally, Quinn) to refine discovery answers
2. **bmad-agent-builder** — Run the six-phase discovery in a fresh Cursor chat session
   - Phase 1: Intent & Identity
   - Phase 2: Capabilities & Routing
   - Phase 3: Requirements & Constraints
   - Phase 4: Draft Review (use gap checklist)
   - Phase 5: Build & Quality Scan
   - Phase 6: Summary & Validation
3. **Skill co-creation** — Build the agent's mastery skill (SKILL.md + references/ + scripts/) in the same story
4. **Memory sidecar** — Create `_bmad/memory/{agent}-sidecar/` with index.md, access-boundaries.md, patterns.md, chronology.md
5. **Register with Marcus** — Add the agent to Marcus's External Specialist Agents table
6. **Party Mode validation** — Team reviews for accuracy and completeness

**Template:** Use `skills/bmad-agent-marcus/SKILL.md` as the canonical example of a fully-built agent with identity, communication style, principles, activation sequence, and capability routing.

**Why coaching matters:** Agent definitions require domain expertise (medical education, physician audience) combined with architectural and tool knowledge. The Party Mode team provides rigor; the user provides instructional vision.

### Recipe 4: Refining an Existing Agent's Behavior

**When:** An agent makes suboptimal decisions, needs new capabilities, or its routing table needs updating.

**Where to look:**

| What to Change | Where to Edit |
|---------------|--------------|
| Agent personality, tone, domain knowledge | Agent's `.md` file — Identity and Communication Style sections |
| Decision-making rules | Agent's `.md` file — Principles section |
| What the agent delegates to | Agent's `.md` file — Capabilities routing tables |
| Tool parameter defaults | `state/config/style_guide.yaml` |
| Quality thresholds | `state/config/tool_policies.yaml` |
| Brand/style standards | `resources/style-bible/master-style-bible.md` (human-curated) |
| Learned patterns | `_bmad/memory/{agent}-sidecar/patterns.md` (review and condense) |
| Reference documentation | Agent's `references/` directory |

**Key insight:** Most behavioral refinements don't require code changes. The agent layer is all `.md` — you're editing natural language instructions, not code. The configuration cascade means you can often tune behavior just by updating YAML or the style bible.

### Recipe 5: Adding a New Reference to a Skill

**When:** A skill needs new detailed documentation for a capability it already has.

1. Create `skills/{skill}/references/{new-reference}.md`
2. Add a routing entry in the skill's SKILL.md pointing to the new reference
3. The reference is loaded on demand when that capability is invoked

---

## Testing

### Test Structure

```
tests/
├── conftest.py                    ← Shared fixtures, env loading, dev mode support
├── fixtures/
│   └── __init__.py
├── test_integration_gamma.py      ← Live API tests for Gamma
├── test_integration_elevenlabs.py ← Live API tests for ElevenLabs
├── test_integration_canvas.py     ← Live API tests for Canvas
├── test_integration_qualtrics.py  ← Live API tests for Qualtrics
├── test_integration_canva.py      ← Canva config validation
├── test_integration_panopto.py    ← Panopto API tests (3 skipped — no creds)
├── test_preflight_check.py        ← Pre-flight check validation
├── test_python_infrastructure.py  ← BaseAPIClient, utilities
├── test_state_management.py       ← SQLite and YAML operations
└── test_plugin_scaffold.mjs       ← Plugin structure validation (Node.js)
```

### Running Tests

```bash
# All tests
.venv\Scripts\python -m pytest tests/ -v

# Specific test file
.venv\Scripts\python -m pytest tests/test_integration_gamma.py -v

# With dev mode (enhanced logging)
DEV_MODE=1 .venv\Scripts\python -m pytest tests/ -v
```

**Current status:** 117 tests pass, 3 skipped (Panopto — no credentials configured).

### Writing New Tests

Follow the existing pattern in `tests/test_integration_gamma.py`:

1. Import the client from `scripts/api_clients/`
2. Use `conftest.py` fixtures for environment loading
3. Test against **live APIs** (this project uses integration tests, not mocks)
4. Use `pytest.mark.skipif` for tests requiring unavailable credentials
5. Keep tests read-only where possible (list, get, verify — don't create/delete in production)

---

## Coding Standards and Patterns

### Python

| Convention | Example |
|-----------|---------|
| **Classes** | `PascalCase`: `GammaClient`, `BaseAPIClient` |
| **Functions** | `snake_case` with action verbs: `list_themes()`, `wait_for_generation()` |
| **Variables** | `snake_case` descriptive: `conversation_state`, `production_context` |
| **Constants** | `UPPER_SNAKE_CASE`: `MAX_POLL_ATTEMPTS`, `RETRYABLE_STATUS_CODES` |
| **Files** | `snake_case`: `gamma_client.py`, `base_client.py` |

### Database

| Convention | Example |
|-----------|---------|
| **Tables** | `snake_case`: `production_runs`, `agent_coordination` |
| **Columns** | `snake_case` with prefixes: `run_id`, `agent_status` |
| **Foreign keys** | `{table}_id`: `course_id`, `module_id` |
| **Indexes** | `idx_{table}_{column}`: `idx_production_runs_status` |

### Error Handling

```python
# Use structured errors from base_client.py
from scripts.api_clients.base_client import APIError, AuthenticationError, RateLimitError

# Good: structured error with context
raise APIError(
    f"Generation failed: {data.get('error', 'unknown')}",
    status_code=response.status_code,
    response_body=data,
)

# Bad: generic exception
raise Exception("Failed")  # No context, no recovery path
```

### Anti-Patterns

- **Never** call tool APIs directly from agent `.md` files — always go through skills → scripts → API clients
- **Never** cache style bible content in agent memory — always re-read from disk
- **Never** store brand identity in `state/config/style_guide.yaml` — that's for tool dial settings only
- **Never** write to `config/` or `resources/` from agent logic — these are human-curated
- **Never** bypass the mode gate — respect ad-hoc/default write rules at the infrastructure level

---

## Project File Map

```
course-DEV-IDE-with-AGENTS/
├── .cursor-plugin/plugin.json         ← Cursor plugin manifest (auto-discovers agents, skills)
├── .mcp.json                          ← MCP server definitions (project-level)
├── .cursor/mcp.json                   ← MCP server definitions (Cursor-specific)
├── .env.example                       ← API key template (committed)
├── .env                               ← Actual secrets (gitignored)
├── pyproject.toml                     ← Python project config
├── requirements.txt                   ← Python dependencies
│
├── agents/                            ← Custom agent .md files (auto-discovered by Cursor)
│   └── README.md
├── skills/                            ← SKILL.md directories (auto-discovered by Cursor)
│   ├── bmad-agent-marcus/SKILL.md     ← Master orchestrator agent
│   └── pre-flight-check/SKILL.md      ← System validation skill
├── rules/                             ← .mdc rules for persistent agent behavior guidance
├── hooks/                             ← Event-driven automation (sessionStart, sessionEnd)
├── commands/                          ← Agent-executable command files
│
├── scripts/
│   ├── api_clients/                   ← Python API clients (BaseAPIClient + 5 tool clients)
│   ├── state_management/              ← SQLite init, DB operations
│   ├── utilities/                     ← Env loading, file helpers, logging, dev mode
│   ├── run_mcp_from_env.cjs          ← MCP wrapper (loads .env secrets at runtime)
│   ├── heartbeat_check.mjs           ← Baseline API heartbeat across all tools
│   ├── smoke_elevenlabs.mjs          ← Targeted ElevenLabs smoke test
│   └── smoke_qualtrics.mjs           ← Targeted Qualtrics smoke test
│
├── state/
│   ├── config/                        ← YAML runtime configs (git-versioned)
│   └── runtime/                       ← SQLite database (gitignored)
├── _bmad/memory/                      ← Agent memory sidecars (git-versioned)
│
├── config/                            ← Static bootstrap defaults
├── resources/
│   ├── style-bible/                   ← Authoritative brand standards (human-curated)
│   ├── exemplars/                     ← Worked production patterns
│   └── tool-inventory/                ← 17-tool access matrix
│
├── course-content/
│   ├── staging/                       ← Agent drafts for human review
│   ├── courses/                       ← Approved/published content
│   └── _templates/                    ← Reusable content scaffolds
│
├── tests/                             ← 117 passing tests (integration + unit)
├── docs/                              ← This guide + user guide + admin guide + reference docs
│
├── _bmad/                             ← BMad Method configuration
├── _bmad-output/
│   ├── planning-artifacts/            ← PRD, architecture, epics (complete)
│   ├── implementation-artifacts/      ← Story artifacts, sprint/workflow status
│   └── brainstorming/                 ← Session docs (Marcus coaching, etc.)
│
├── bmad-session-protocol.md           ← How to run BMAD sessions
├── next-session-start-here.md         ← Hot-start context for next session
└── SESSION-HANDOFF.md                 ← Session record and handoff context
```

---

## Key Reference Documents

These are the authoritative sources — this guide references them rather than duplicating their content.

| Document | Location | What It Covers |
|----------|----------|---------------|
| **Architecture** | `_bmad-output/planning-artifacts/architecture.md` | Full architectural decisions, patterns, validation |
| **PRD** | `_bmad-output/planning-artifacts/prd.md` | 80 FRs, success criteria, user journeys, compliance |
| **Epics & Stories** | `_bmad-output/planning-artifacts/epics.md` | 10 epics, 35 stories, FR coverage map |
| **Directory Responsibilities** | `docs/directory-responsibilities.md` | Configuration hierarchy, resolution rules, anti-patterns |
| **Tool Access Matrix** | `resources/tool-inventory/tool-access-matrix.md` | 17 tools classified by access tier |
| **Style Bible** | `resources/style-bible/master-style-bible.md` | Brand identity, content standards, tool prompts |
| **Session Protocol** | `bmad-session-protocol.md` | Cold start, hot start, shutdown, cross-context handoff |
| **Project Context** | `docs/project-context.md` | Current state, key decisions, repository contract |
| **HIL Workflow** | `docs/workflow/human-in-the-loop.md` | Staging → review → promotion → publish |
| **Agent Environment** | `docs/agent-environment.md` | MCP setup, API guidance, BMad alignment |
| **Marcus Coaching** | `_bmad-output/brainstorming/party-mode-coaching-marcus-orchestrator.md` | Full discovery answers for orchestrator creation |
