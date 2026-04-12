# Developer Guide — Architecture, Execution Flow, and Extension Points

**Audience:** Developers building, extending, and maintaining the collaborative intelligence platform.
**Last Updated:** 2026-04-05 | **Project Phase:** Complete (all 14 epics done; prompt-pack family split by workflow template; Epic 13/14 runtime controls live)

---

## Table of Contents

> 2026-04-05 status: Epics 13 and 14 are complete. The live narrated workflow family is now split between `production-prompt-pack-v4.1-narrated-deck-video-export.md` for non-motion runs and `production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` for motion-enabled runs. `DOUBLE_DISPATCH` remains an inline branch inside either workflow template.

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

This project is a **multi-agent collaborative intelligence platform** (**APP** — Agentic Production Platform) for medical education course content production. The core concept: a master orchestrator agent (Marcus) conducts a conversation with the user, delegates to specialist agents, which invoke skills backed by Python scripts, which call external tool APIs. Results flow back through **fidelity assessment (Vera)**, **quality review (Quinn-R)**, and human checkpoints. Governance artifacts include `docs/lane-matrix.md`, `docs/fidelity-gate-map.md`, run **mode** (`mode_state.json`), and optional run **baton** files under `state/runtime/`.

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
| **Agents** | `skills/bmad-agent-{name}/` | Judgment, decision-making, personality, memory | Built in Epic 2+ |

**Why this matters:** You can fix an API client without touching any agent or skill. You can refine a skill's parameter templates without changing the API client it wraps. You can update an agent's personality or routing without modifying any skill code. Each layer evolves at its own pace.

**Fidelity and perception (Epic 2A):** Shared **sensory bridges** (`skills/sensory-bridges/`) produce canonical multimodal perception for validators. **Vera** (`skills/bmad-agent-fidelity-assessor/`) owns source-faithfulness judgments; **Quinn-R** owns quality-standard and learner-effect dimensions — see `docs/lane-matrix.md`.

### Layer Interaction Pattern

```
Agent (.md)  ──reads──>  Skill (SKILL.md + references/)  ──invokes──>  Script (.py)  ──calls──>  API Client
     │                            │                                          │
     │                            │                                          │
     └── judgment, routing        └── tool expertise, templates              └── HTTP, retry, auth
```

---

## Typical Run Walk-Through

For a **step-by-step trial** aligned with instructor copy-paste prompts, staging layout, and HIL gates, see the **Happy-path walkthrough** section in [`docs/user-guide.md`](user-guide.md) (same pipeline as below, with paths and checklist).

Workflow-template rule:
- `narrated-deck-video-export` is the standard narrated template and aligns with `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`
- `narrated-lesson-with-video-or-animation` is the motion-enabled narrated template and aligns with `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `DOUBLE_DISPATCH` remains a bounded Gary-stage branch in either workflow; it does not create a third prompt-pack family

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
5. Marcus checks current run mode (default vs. ad-hoc) via `state/runtime/mode_state.json` (`skills/production-coordination/scripts/manage_mode.py`) or helper `skills/bmad-agent-marcus/scripts/read-mode-state.py`

### Phase 2: Source Material Prompting (Marcus → SP capability)

6. Marcus loads `./references/source-prompting.md` (SP capability)
7. Marcus offers: *"I see Module 2 notes in Notion and some reference PDFs in Box Drive. Want me to pull those in before we start?"*
8. If user accepts, Marcus delegates to **`source-wrangler`** (`skills/source-wrangler/`) to fetch Notion pages, Box Drive files, URLs/HTML captures, etc.

### Phase 3: Production Planning (Marcus → CM capability)

9. Marcus reads `resources/style-bible/master-style-bible.md` **fresh from disk** — never cached
10. Marcus reads `resources/exemplars/` for any relevant worked patterns
11. Marcus reads `state/config/style_guide.yaml` for Gamma-specific parameter preferences
12. Marcus reads `state/config/tool_policies.yaml` to determine the active run preset (e.g., `draft`)
13. Marcus builds a **production plan** from the registry-backed workflow templates in `skills/bmad-agent-marcus/references/workflow-templates.yaml`: what needs to be created, which specialist handles it, and what quality gates apply
    - Canonical narrated template for slide-to-video export: `narrated-deck-video-export` (alias-free)
    - Canonical narrated template with custom video/animation generation: `narrated-lesson-with-video-or-animation`
    - Operator prompt packs map to these templates:
      - `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`
      - `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
14. Marcus presents the plan to the user for confirmation

### Phase 4: Specialist Delegation (Marcus → Gary, Gamma Specialist)

15. Marcus builds a **context envelope** containing:
    - Production run ID
    - Content type: presentation
    - Module/lesson identifier: M2-L3
    - Learning objectives from course_context.yaml
    - User constraints (from conversation)
    - Relevant style bible sections (color palette, typography, Gamma prompt template)
    - Applicable exemplar references
16. Marcus delegates to Gary (`gamma-specialist` agent)
17. Gary loads his own SKILL.md, reads `references/` for parameter mastery details
18. The specialist determines optimal Gamma parameters:
    - First: check `state/config/style_guide.yaml` for saved preferences
    - Second: apply context inference (medical content → specific LLM, style, format choices)
    - Third: if missing critical parameters, escalate back to Marcus for conversational elicitation

### Phase 5: Tool Execution (Specialist → Skill → API Client)

19. Gary invokes Python scripts in `skills/gamma-api-mastery/scripts/`
20. The script instantiates `GammaClient` from `scripts/api_clients/gamma_client.py`
21. `GammaClient.generate()` sends the API request with all parameters
22. `GammaClient.wait_for_generation()` polls until completion (3s intervals, up to 120 attempts)
23. The generated presentation data is returned to the specialist

Literal-visual dispatch rule:
- In mixed-fidelity generation, literal-visual slides are treated as full-slide image-only payloads.
- Dispatch input for literal-visual slides is URL-only image content; supporting prose belongs in Irene Pass 2 narration/script.
- Missing literal-visual diagram-card image mappings are fail-closed errors.

### Phase 6: Fidelity and quality review

24. The specialist performs **execution-only** self-assessment (e.g. Gary: layout integrity, parameter confidence, embellishment risk — see `skills/bmad-agent-gamma/references/quality-assessment.md` and `docs/lane-matrix.md`)
25. Where applicable, **sensory bridges** confirm perception of PNGs/audio before scoring; cached perception may be reused across Vera and Quinn-R per `skills/sensory-bridges/references/validator-handoff.md`
26. The specialist returns to Marcus: artifact paths, execution self-assessment, parameter decisions for style guide, and pipeline fields (e.g. `gary_slide_output`, provenance)
27. Marcus routes the artifact to **Vera** (`bmad-agent-fidelity-assessor`) for **source-faithfulness** (O/I/A, provenance, drift signals) per `docs/fidelity-gate-map.md` — failures can circuit-break before Quinn-R
28. On pass, Marcus invokes **Quinn-R** (`bmad-agent-quality-reviewer`) for **quality standards**: brand, accessibility (WCAG 2.1 AA), learning objective alignment, instructional soundness, learner-effect intent fidelity, content accuracy flags, audio/composition dimensions as applicable

### Phase 7: Human Checkpoint (Marcus → User)

29. Marcus loads `./references/checkpoint-coord.md` (HC capability)
30. Marcus presents the work to the user:
    - *"Slides are done — 12 frames covering all three learning objectives for drug interactions. JCPH Navy headers, Medical Teal accents. Quality review passed. Ready for your review."*
31. User reviews and either approves, requests changes, or redirects

### Phase 8: State Updates (if default mode)

32. If approved and in **default mode**:
    - Content saved to `course-content/staging/m02-drug-interactions/`
    - SQLite `production_runs` table updated with run completion
    - SQLite `quality_gates` table updated with review results
    - Marcus's memory sidecar `patterns.md` appended with what worked
    - Marcus's `chronology.md` appended with session record
    - `state/config/style_guide.yaml` updated with any new parameter preferences
33. If in **ad-hoc mode**:
    - Content saved to scratch/staging area
    - No state writes except transient section of Marcus's `index.md`
    - QA results still recorded (QA always runs)

### Phase 9: Promotion (User-Directed)

34. User reviews content in staging
35. User tells Marcus to promote: *"Looks good, promote to courses"*
36. Content moves from `course-content/staging/` to `course-content/courses/`
37. Platform publishing follows (Canvas API, CourseArc/LTI, etc.) using the active specialist or manual path supported for that platform in the current repo state.

---

## State Management Deep Dive

### The Three Tiers

```
┌─────────────────────────────────────────────┐
│  YAML Configuration (state/config/)         │  ← Git-versioned, human-readable
│  • course_context.yaml                      │  ← Evolves slowly
│  • style_guide.yaml                         │  ← Agent-writable (learned prefs)
│  • tool_policies.yaml                       │  ← Admin-managed (run presets)
│  • fidelity-contracts/ (G0–G6 YAML)         │  ← L1 fidelity criteria
├─────────────────────────────────────────────┤
│  SQLite + JSON (state/runtime/)             │  ← Gitignored, ephemeral
│  • coordination.db + tables               │  ← Production runs, coordination,
│  • mode_state.json                          │    quality gates; mode + baton
│  • run_baton.{run_id}.json                  │  ← Does NOT survive fresh clone
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

Run settings use two independent axes:

- Execution mode: `tracked` (alias `default`) vs `ad-hoc`
- Quality preset: `explore`, `draft`, `production`, `regulated`

Execution mode is a **gate on the state management layer**, not on agents. Agents behave identically in both execution modes — the infrastructure handles routing:

| State Target | Tracked/Default Mode | Ad-Hoc Mode |
|-------------|:------------:|:-----------:|
| SQLite tables | Full write | Suppressed |
| YAML configs | Full write | Suppressed |
| Memory sidecar `patterns.md` | Append | Read-only |
| Memory sidecar `chronology.md` | Append | Read-only |
| Memory sidecar `index.md` | Full write | Transient section only |
| Memory sidecar `access-boundaries.md` | Read-only | Read-only |
| Quality gate execution | Always | Always |
| Asset output | `course-content/staging/` | Scratch/staging area |
| Remote git side effects (commit/push) | Permitted when explicitly requested by feature contract | Suppressed (fail-closed or explicit no-op) |

Quality preset is applied separately by policy thresholds and validators; it does not redefine persistence routing.

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

Specialists return: **artifact paths** + **execution self-assessment** (lane-scoped; see `docs/lane-matrix.md`) + **parameter decisions to save** + pipeline-specific payloads (e.g. `gary_slide_output`, provenance).

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

### Current Skills (representative)

| Skill | Location | Role |
|-------|----------|------|
| `pre-flight-check` | `skills/pre-flight-check/` | MCP/API/doc readiness |
| `production-coordination` | `skills/production-coordination/` | Run/mode/baton/style-guide helpers |
| `source-wrangler` | `skills/source-wrangler/` | Notion, Box, URL/HTML ingestion |
| `tech-spec-wrangler` | `skills/tech-spec-wrangler/` | Doc refresh via Ref MCP |
| `gamma-api-mastery` | `skills/gamma-api-mastery/` | Gamma generate/export operations |
| `elevenlabs-audio` | `skills/elevenlabs-audio/` | ElevenLabs TTS operations |
| `kling-video` | `skills/kling-video/` | Kling video operations |
| `compositor` | `skills/compositor/` | Segment manifest → Descript guide, `sync-visuals` |
| `quality-control` | `skills/quality-control/` | Automated brand/a11y helpers + SQLite logging |
| `woodshed` | `skills/woodshed/` | Exemplar mastery workflow |
| `sensory-bridges` | `skills/sensory-bridges/` | Multimodal perception for validators |
| `bmad-agent-fidelity-assessor` | `skills/bmad-agent-fidelity-assessor/` | Vera — fidelity trace reports |
| `app-maturity-audit` | `skills/app-maturity-audit/` | Four-pillar APP maturity audit |
| `bmad-agent-marcus` | `skills/bmad-agent-marcus/` | Orchestrator agent (SKILL.md) |
| `bmad-agent-content-creator` | `skills/bmad-agent-content-creator/` | Irene |
| `bmad-agent-gamma` | `skills/bmad-agent-gamma/` | Gary |
| `bmad-agent-elevenlabs` | `skills/bmad-agent-elevenlabs/` | Voice Director |
| `bmad-agent-kling` | `skills/bmad-agent-kling/` | Kira |
| `bmad-agent-quality-reviewer` | `skills/bmad-agent-quality-reviewer/` | Quinn-R |

Current state notes:
- run reporting, workflow state, and governance artifacts are live in the completed Epic 4 / 4A / G implementation set
- platform deployment still depends on the specific specialist or manual path available for that tool in the repo

### Compositor assembly bundle CLI

Before a human assembles in Descript, **localize** Gate-approved stills next to the manifest (see `skills/compositor/SKILL.md`). From the repo root, using the project `.venv`:

```bash
.venv\Scripts\python.exe skills/compositor/scripts/compositor_operations.py sync-visuals path/to/manifest.yaml
.venv\Scripts\python.exe skills/compositor/scripts/compositor_operations.py guide path/to/manifest.yaml path/to/DESCRIPT-ASSEMBLY-GUIDE.md
```

- **`sync-visuals`** copies each segment `visual_file` into `<manifest_dir>/visuals/` (override with `--subdir`) and rewrites only those path strings in the manifest (YAML layout preserved).
- **`guide`** emits the Descript Assembly Guide; the legacy **two-argument** form (`manifest` then `output`, without the `guide` subcommand) still works.
- After compositor output exists, production runs require **`DESMOND-OPERATOR-BRIEF.md`** in the same `assembly-bundle/` (prompt **14.5**): see `skills/bmad-agent-desmond/SKILL.md` — not generated by this CLI.
- Tests: `pytest skills/compositor/scripts/tests`

### ElevenLabs manifest narration CLI

From the repo root, using the project `.venv`:

```bash
.venv\Scripts\python.exe skills/elevenlabs-audio/scripts/elevenlabs_operations.py manifest \
  path/to/assembly-bundle/segment-manifest.yaml \
  --output-dir path/to/assembly-bundle \
  --voice-selection path/to/voice-selection.json
```

- **`manifest`** subcommand reads a segment manifest, synthesizes narration for each segment via ElevenLabs, and writes audio + VTT files back alongside the manifest.
- **`--voice-selection`** (optional) — path to `voice-selection.json`. When provided the tool (1) verifies `locked_manifest_hash` and `locked_script_hash` against the Gate 3 locked artifacts before any API spend, (2) auto-resolves the selected voice as the default synthesis voice (explicit `--default-voice-id` still overrides), and (3) emits per-segment progress to stderr.
- Tests: `pytest skills/elevenlabs-audio/scripts/tests`

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

### Theme Resolution and Cluster Dispatch

For cluster-aware Gary dispatch:
- `run-constants.yaml` → `theme_selection` ("theme-a") → `gary-theme-resolution.json` → `theme_id` ("njim9kuhfnljvaa")
- `theme_paramset_key` ("preset-a") → `gamma-style-presets.yaml` → `imageOptions.model` ("gemini-3.1-flash-image-mini")
- Trial script `cluster_dispatch_trial.py` hardcodes canonical values for validation.

### Gamma PNG Export Handling

Gamma's PNG export may return a single image or a ZIP archive of multiple images. The `_materialize_exported_slide_paths` function in `skills/gamma-api-mastery/scripts/gamma_operations.py` handles this normalization:

```python
def _materialize_exported_slide_paths(
    downloaded_path: Path,
    *,
    requested_format: str | None,
    expected_card_numbers: list[int],
    module_lesson_part: str,
    export_dir: Path,
    label: str,
) -> list[str]:
    # Parses slide_XX.png filenames, handles _variant_A/B suffixes
    # Sorts numerically, validates against expected_card_numbers
    # Returns deterministic per-card PNG paths
```

This ensures slide_01.png maps to card 1, etc., preventing storyboard misalignment.

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
| `KlingClient` | `kling_client.py` | JWT (HS256 from access_key+secret_key) | Text-to-video, image-to-video, lip-sync, extend, polling, download |
| `NotionClient` | `notion_client.py` | Bearer (internal integration token) | Pages/blocks search and read for source wrangling |

---

## Extension Guide: Adding New Capabilities

This is where you come in. The three-layer architecture means there are three distinct extension points, each with its own recipe.

### Recipe 1: Adding a New API Client

**When:** A new tool needs programmatic access (Tier 1-3 in the tool inventory).

**Steps:**

1. Create `scripts/api_clients/{tool}_client.py` extending `BaseAPIClient`
2. Use the appropriate auth pattern for the tool (check API docs)
3. Add env vars to `.env` (see `docs/admin-guide.md`)
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

**Templates:**
- **Orchestrator agent:** `skills/bmad-agent-marcus/SKILL.md` — identity, communication style, principles, activation, capability routing
- **Specialist agent:** `skills/bmad-agent-gamma/SKILL.md` (Gary) — delegation protocol, context envelope schema, degradation handling, dual activation (headless + interactive)
- **Mastery skill:** `skills/gamma-api-mastery/` — SKILL.md + parameter catalog + context optimization + evaluator + operations scripts
- **Evaluator:** `skills/gamma-api-mastery/scripts/gamma_evaluator.py` — extends BaseEvaluator with medium-specific extraction and comparison

**Why coaching matters:** Agent definitions require domain expertise (medical education, physician audience) combined with architectural and tool knowledge. The Party Mode team provides rigor; the user provides instructional vision.

### Evaluator Design Requirements (Lessons from Story 3.1)

Every specialist agent's evaluator MUST follow these requirements, established through Gary's woodshed debugging:

1. **Guide the tool's intelligence — never suppress it.** Rich instructions describing the desired visual/audio/structural outcome outperform restrictive constraints. Each tool has a core creative strength; work with it.

2. **Extract and compare actual output.** The evaluator must perform medium-specific output extraction (PDF text, audio duration, image analysis) and compare against source content. "Did a file download?" is not a quality check.

3. **Score based on content coverage — not exact match.** Check that source key words and phrases appear in the reproduction. Tool enhancements (sub-descriptions, visual accents, structural formatting) are usually beneficial, not failures.

4. **Use a cheap quality signal.** File size (slides), duration vs word count (audio), dimensions (images), question count (surveys) — instant proxies for quality that cost nothing.

5. **Separate woodshed from production QA.** Woodshed compares against a source exemplar (tool control). Production QA compares against the context envelope (did the agent produce what Marcus asked for). Same rubric dimensions, different reference point.

6. **Capture know-how from production feedback.** The agent's `patterns.md` grows from user checkpoint reviews, not woodshed scores. Real insights emerge from the user saying "excellent" or "fix the density."

See `skills/woodshed/SKILL.md` → "Evaluator Design Requirements" for the full reference with per-tool examples.

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

### Test layout

**Root integration suite** — `tests/` (API clients, state, pre-flight, fidelity helpers, Notion, etc.).

**Skill-scoped suites** — many skills ship their own `scripts/tests/` (e.g. `skills/gamma-api-mastery/scripts/tests/`, `skills/sensory-bridges/scripts/tests/`, `skills/production-coordination/scripts/tests/`, `skills/compositor/scripts/tests/`). Run them by path when you change that skill.

```
tests/                               ← Shared repo tests
├── conftest.py
├── test_integration_*.py            ← Live API tests (Gamma, ElevenLabs, Canvas, …)
├── test_preflight_check.py
├── test_python_infrastructure.py
├── test_state_management.py
├── test_fidelity_drift_check.py
├── test_resolve_source_ref.py
└── …

skills/*/scripts/tests/              ← Per-skill unit tests (compositor, gamma ops, bridges, …)
```

### Running Tests

```bash
# Repo root suite (default profile: excludes tests marked live_api)
.venv\Scripts\python -m pytest tests/ -v

# Include live API tests explicitly
.venv\Scripts\python -m pytest tests/ -v --run-live

# One skill's tests
.venv\Scripts\python -m pytest skills/compositor/scripts/tests -v

# Broad pass (root + major skills — adjust globs as needed)
.venv\Scripts\python -m pytest tests skills/gamma-api-mastery/scripts/tests skills/production-coordination/scripts/tests -v

# With dev mode (enhanced logging)
set DEV_MODE=1
.venv\Scripts\python -m pytest tests/ -v
```

**Note:** Total test count changes as stories land; use `pytest --collect-only` for an exact count.

- By default, tests marked `live_api` are deselected unless `--run-live` is provided.
- Slower/flakier end-to-end live tests are marked `live_api_e2e` and require an additional `--run-live-e2e` flag.
- For Kling specifically, use `KLING_LIVE_STRICT=1` when you want queue-timeouts to fail the run instead of xfail.

Examples:

```powershell
# Stable live canary coverage (recommended default)
.venv\Scripts\python -m pytest tests/test_integration_kling.py --run-live -v

# Full live E2E Kling coverage (opt-in)
.venv\Scripts\python -m pytest tests/test_integration_kling.py --run-live --run-live-e2e -v

# Strict mode (timeout becomes failure)
set KLING_LIVE_STRICT=1
.venv\Scripts\python -m pytest tests/test_integration_kling.py --run-live --run-live-e2e -v
```

### Ruff Lint Policy (Ratchet)

The project uses a ratchet policy so delivery can continue while lint debt is reduced incrementally:

1. Keep the existing backlog as a temporary baseline.
2. New/changed Python files must be Ruff-clean.
3. Full-project Ruff count must not rise above baseline.

Policy details and command examples:

- `docs/workflow/ruff-ratchet-policy.md`

### Writing New Tests

1. Prefer **live API** checks for external tools (with `skipif` when env vars absent), matching existing `tests/test_integration_*.py` patterns.
2. For skill logic, add tests under that skill's `scripts/tests/` and run with `pytest path/to/tests`.
3. Keep destructive operations out of shared integration tests where possible.

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
├── .env                               ← Actual secrets (gitignored; key names in docs/admin-guide.md)
├── pyproject.toml                     ← Python project config
├── requirements.txt                   ← Python dependencies
│
├── skills/                            ← SKILL.md directories (auto-discovered) — **primary home for agents**
│   ├── bmad-agent-marcus/             ← Marcus + scripts (e.g. read-mode-state)
│   ├── bmad-agent-gamma/              ← Gary
│   ├── pre-flight-check/
│   ├── production-coordination/       ← manage_mode, manage_baton, style guide, …
│   └── …                              ← See [Current Skills](#current-skills-representative)
├── rules/                             ← .mdc rules for persistent agent behavior guidance
├── hooks/                             ← Event-driven automation (sessionStart, sessionEnd)
├── commands/                          ← Agent-executable command files
│
├── scripts/
│   ├── api_clients/                   ← Python API clients (Gamma, ElevenLabs, Canvas, … + Notion, Kling)
│   ├── state_management/              ← SQLite init, DB operations
│   ├── utilities/                     ← Env loading, file helpers, logging, dev mode
│   ├── run_mcp_from_env.cjs          ← MCP wrapper (loads .env secrets at runtime)
│   ├── heartbeat_check.mjs           ← Baseline API heartbeat across all tools
│   ├── smoke_elevenlabs.mjs          ← Targeted ElevenLabs smoke test
│   └── smoke_qualtrics.mjs           ← Targeted Qualtrics smoke test
│
├── state/
│   ├── config/                        ← YAML + fidelity-contracts/ (git-versioned)
│   └── runtime/                       ← SQLite, mode_state.json, run_baton.*.json (gitignored)
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
├── tests/                             ← Root pytest suite (integration + unit)
├── docs/                              ← This guide + user guide + admin guide + reference docs
│
├── _bmad/                             ← BMad Method configuration
├── _bmad-output/
│   ├── planning-artifacts/            ← PRD, architecture, epics (complete)
│   ├── implementation-artifacts/      ← Story artifacts, sprint/workflow status
│   └── brainstorming/                 ← Session docs (Marcus coaching, etc.)
│
├── bmad-session-protocol-session-START.md   ← BMAD start-of-session protocol
├── bmad-session-protocol-session-WRAPUP.md  ← BMAD end-of-session protocol
├── bmad-session-protocol-session-MISC.md    ← BMAD reference notes
├── next-session-start-here.md         ← Hot-start context for next session
└── SESSION-HANDOFF.md                 ← Session record and handoff context
```

---

## Key Reference Documents

These are the authoritative sources — this guide references them rather than duplicating their content.

| Document | Location | What It Covers |
|----------|----------|---------------|
| **Architecture** | `_bmad-output/planning-artifacts/architecture.md` | Full architectural decisions; governance + APP sections |
| **PRD** | `_bmad-output/planning-artifacts/prd.md` | **91 FRs** (incl. FR81–FR91 governance), success criteria, journeys |
| **Epics & Stories** | `_bmad-output/planning-artifacts/epics.md` | Current epic and story catalog, including Epic 13 visual-aware Irene and Epic 14 motion workflow |
| **Fidelity gate map** | `docs/fidelity-gate-map.md` | G0–G6, Vera vs Quinn-R ordering, role matrix |
| **Lane matrix** | `docs/lane-matrix.md` | Cross-agent judgment ownership |
| **Fidelity architecture (GOLD)** | `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md` | APP / three-layer / hourglass / sensory horizon |
| **Directory Responsibilities** | `docs/directory-responsibilities.md` | Configuration hierarchy, resolution rules, anti-patterns |
| **Tool Access Matrix** | `resources/tool-inventory/tool-access-matrix.md` | 17 tools classified by access tier |
| **Style Bible** | `resources/style-bible/master-style-bible.md` | Brand identity, content standards, tool prompts |
| **Session Protocol (Start)** | `docs/workflow/production-session-start.md` | Production shift startup gates and readiness checks |
| **Session Protocol (Wrap-up)** | `docs/workflow/production-session-wrapup.md` | End-of-session shutdown, evidence, and handoff |
| **Session Protocol (Launcher)** | `docs/workflow/production-session-launcher.md` | Marcus activation prompt for production operations sessions |
| **Project Context** | `docs/project-context.md` | Current state, key decisions, repository contract |
| **User Guide (happy path)** | `docs/user-guide.md` (Happy-path walkthrough) | Trial planner: Marcus model prompts, X-ray table, staging tree, Gates 1–3, compositor handoff |
| **HIL Workflow** | `docs/workflow/human-in-the-loop.md` | Staging → review → promotion → publish |
| **Agent Environment** | `docs/agent-environment.md` | MCP setup, API guidance, BMad alignment |
| **Marcus Coaching** | `_bmad-output/brainstorming/party-mode-coaching-marcus-orchestrator.md` | Full discovery answers for orchestrator creation |
| **Sprint / workflow status** | `_bmad-output/implementation-artifacts/sprint-status.yaml`, `bmm-workflow-status.yaml` | Epic and story Kanban + BMM phase |
