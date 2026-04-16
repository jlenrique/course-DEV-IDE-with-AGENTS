# Directory Responsibilities

Canonical reference for configuration and reference directory boundaries. All agents, skills, and project documentation should align to these definitions.

## Configuration Hierarchy

Three directory tiers provide layered configuration. Higher priority wins when content overlaps.

| Priority | Directory | Purpose | Mutability | Who Writes |
|----------|-----------|---------|------------|------------|
| **1 (authoritative)** | `resources/style-bible/` | Brand identity, visual design system, voice/tone, accessibility standards, tool-specific prompt templates | Human-curated only | User (via manual edit) |
| **2 (operational)** | `state/config/` | Mutable runtime configuration — per-tool parameter preferences, course hierarchy, run presets, quality gates | Agent-writable | Marcus (via conversation) + scripts |
| **3 (fallback)** | `config/` | Bootstrap project defaults — minimal audience, voice, accessibility, review gate floor | Rarely changes | Developer (ships with repo) |

## Directory Details

### `config/` — Static Project Defaults

Ships with the repository. Provides minimum-viable defaults for agents that operate outside the Marcus production workflow (e.g., ad-hoc Cursor rule guidance, standalone skills).

| File | Contents |
|------|----------|
| `content-standards.yaml` | Baseline audience, voice, accessibility floor, review gates |
| `platforms.example.yaml` | Canvas/CourseArc endpoint template |

**Superseded by** `resources/style-bible/` once that file exists. Agents inside Marcus's workflow never consult `config/` directly — they use the cascade defined in Marcus's `conversation-mgmt.md`.

### `state/config/` — Mutable Runtime Configuration

Per-deployment, per-course configuration that evolves through orchestrator conversations. Git-versioned YAML.

| File | Contents | Agent Interaction |
|------|----------|-------------------|
| `style_guide.yaml` | Per-tool parameter preferences only (Gamma LLM, ElevenLabs voice ID, Canvas course ID, etc.) | Read before generation; write-back learned preferences |
| `course_context.yaml` | Course hierarchy — name, code, modules, lessons, learning objectives | Read for scope resolution; updated as curriculum planning proceeds |
| `tool_policies.yaml` | Run presets (explore/draft/production/regulated), quality gate thresholds, retry policy, fallback strategies | Read for quality enforcement; rarely updated by agents |
| `narration-script-parameters.yaml` | Script-level tunable knobs for Irene Pass 2 — narration density, word ranges, cluster head/interstitial word budgets, bridge cadence policy | Read by Irene + Vera G4; human-tuned |
| `experience-profiles.yaml` | Two extreme experience profiles (visual-led, text-led) with `slide_mode_proportions` and `narration_profile_controls` target values | Read by Creative Director (CD) + profile resolver in `run_constants.py`; human-curated |
| `parameter-registry-schema.yaml` | Master registry of all production parameters across three families (run-constants, narration-time, assembly-time) | Read by validators and the parameter-directory doc; append-only as parameters are added |
| `prompting.yaml` | Cluster prompt engineering templates (small/large), safety clauses, token budget, hashing config | Read by cluster dispatch scripts; human-curated templates |
| `dispatch.yaml` | Cluster dispatch sequencing policy — ordering, batch size, max concurrency, retry/backoff, hashing | Read by `skills/bmad-agent-marcus/scripts/cluster_dispatch_sequencing.py`; operational tuning |
| `validation.yaml` | Cluster coherence validation rules — required/forbidden terms, sequencing enforcement, sampling mode, hashing | Read by `skills/bmad-agent-marcus/scripts/cluster_coherence_validation.py` |

**Subdirectory: `state/config/fidelity-contracts/`** — L1 fidelity contract YAML per gate. One file per gate (e.g., `g0-source-bundle.yaml`, `g1.5-cluster-plan.yaml`, `g2.5-cluster-coherence.yaml`, `g4-narration-script.yaml`). Each defines evaluation criteria with `id`, `severity`, `evaluation_type` (deterministic or agentic), and `check` specification. G1.5 and G2.5 are conditional — present only for lessons with cluster segments.

**Subdirectory: `state/config/structural-walk/`** — Workflow-specific manifest files for the structural walk tool (`standard.yaml`, `motion.yaml`, `cluster.yaml`). See `docs/structural-walk.md`.

**Subdirectory: `state/config/schemas/`** — Machine-readable schemas for agent-generated artifacts. Currently: `creative-directive.schema.json` and `creative-directive.schema.yaml` (CD agent output format). Validators in `scripts/utilities/creative_directive_validator.py` read from these schemas at runtime, not from hardcoded field lists.

**Does NOT contain**: brand identity, colors, typography, voice/tone, or accessibility standards. Those live in `resources/style-bible/`.

### `state/runtime/` — Ephemeral Runtime State

Not git-versioned. Operational state that doesn't survive a fresh clone.

| Item | Contents |
|------|----------|
| `coordination.db` | SQLite — production runs, agent coordination, quality gate records |
| `backup/` | Database backup and restore scripts |

### `scripts/` — Executable Code and Utilities

Python scripts for API clients, state management, utilities, and CLI tools. Organized by function.

| Subdirectory | Contents |
|--------------|----------|
| `api_clients/` | API client classes extending `BaseAPIClient` (Gamma, ElevenLabs, Canvas, etc.) |
| `state_management/` | SQLite database operations and schema management |
| `utilities/` | Shared utilities: run constants parsing, file helpers, logging, progress map CLI, creative directive validator, **profile-aware slide/runtime estimator** (`slide_count_runtime_estimator.py`) |
| `tests/` | Cross-cutting test utilities and fixtures |

### `resources/style-bible/` — Authoritative Brand Reference

The single source of truth for all brand and content standards. Human-curated, not agent-writable.

| File | Contents |
|------|----------|
| `master-style-bible.md` | Color palette (hex values), typography system, imagery standards, voice characteristics, writing style guidelines, content structure templates, tool-specific translation prompts, quality assurance checklists |

Marcus and specialist agents re-read this fresh for each production task — never cached in memory.

### `resources/exemplars/` — Exemplar Library & Worked Production Patterns

Two roles: (1) **exemplar-driven agent development** — real artifacts that specialist agents must study and reproduce to prove tool mastery, and (2) reference patterns from past production decisions.

| Subdirectory | Contents |
|--------------|----------|
| `_shared/` | Cross-cutting woodshed protocol: comparison rubric template, workflow documentation |
| `gamma/` | Gamma exemplar artifacts with `_catalog.yaml`, per-exemplar `brief.md`, `source/`, `reproduction-spec.yaml`, and `reproductions/` history |
| `elevenlabs/` | ElevenLabs exemplar artifacts (same structure) |
| `canvas/` | Canvas exemplar artifacts (same structure) |
| `qualtrics/` | Qualtrics exemplar artifacts (same structure) |
| `canva/` | Canva exemplar artifacts (same structure) |
| `policies/` | Platform allocation decision frameworks (Canvas vs CourseArc criteria) |
| `platform-matrices/` | Worked allocation examples from actual course modules |

**Exemplar workflow**: Juan provides exemplar artifacts → agent studies via woodshed skill → agent reproduces programmatically → comparison against original proves mastery. All reproduction attempts (pass/fail) are retained with detailed run logs. See `_shared/woodshed-workflow.md` for the full protocol including reflection between failed cycles and circuit breaker give-up rules.

**Write rules**: Exemplar `source/` and `brief.md` are human-curated only. Agents write to `reproduction-spec.yaml`, `reproductions/`, and `failure-report.yaml`.

**Doc refresh protocol**: `_shared/doc-refresh-protocol.md` defines how agents refresh their tool's API documentation before woodshed cycles. Each mastery skill maintains `references/doc-sources.yaml` with authoritative URLs, LLM-optimized endpoints (e.g., Gamma's `llms.txt`), and changelog locations. Agents use the Ref MCP (`ref_search_documentation`, `ref_read_url`) to check for changes and update their `parameter-catalog.md` accordingly.

### `maintenance/` — Cross-harmonization and governance utilities

| File | Contents |
|------|----------|
| `audit_done_bmad_coverage.py` | Optional audit: compares `sprint-status.yaml` `done` keys to formal BMAD closure markers in story artifacts; stdout or redirect to `reports/audit-done-bmad-coverage.txt` |
| `cross-harmonization-report-*.md` | Dated session reports when docs/sprint/story alignment passes are run |

### `reports/` — Operator and automation outputs

| Path | Contents |
|------|----------|
| `reports/audit-done-bmad-coverage.txt` | (Optional) Saved output of BMAD done-story coverage audit |
| `reports/proofs/<story-key>/...` | Frozen proof JSON bundles (e.g. `20c-14` profile propagation) — not the same as exemplar slides; see `next-session-start-here.md` and story `20c-14` |

### `resources/tool-inventory/` — Tool Capability Reference

| File | Contents |
|------|----------|
| `tool-access-matrix.md` | 17-tool audit: tier classification, API/MCP status, access patterns |

### `_bmad/memory/` — Agent Learning (Memory Sidecars)

Per-agent persistent learning. Mode-aware write rules apply.

| File | Contents | Write Rule |
|------|----------|------------|
| `index.md` | Active context, preferences, current mode | Default: full. Ad-hoc: transient section only |
| `access-boundaries.md` | Read/write/deny zones | Set at build time, read-only |
| `patterns.md` | Learned workflow/parameter patterns | Default mode only (append) |
| `chronology.md` | Session and production run history | Default mode only (append) |

### `course-content/staging/` — Draft and bundle workspace

Gitignored in full-tree workflows; agents write drafts and **source bundles** here. For **tracked** production runs, a bundle folder may include **`run-constants.yaml`** at its root: frozen `RUN_ID`, repo-relative `bundle_path`, absolute primary source path, theme keys, execution mode, and quality preset. That file is the machine-readable twin of the v4 prompt pack “Run Constants” block; validate with `scripts.utilities.run_constants` (see `docs/workflow/trial-run-pass2-artifacts-contract.md` §1B).

## Resolution Rules

When an agent needs brand, style, or parameter information:

1. **Brand colors, typography, imagery, voice/tone** → `resources/style-bible/` (always)
2. **Tool parameters** (voice IDs, LLM choices, format preferences) → `state/config/style_guide.yaml`
3. **Course hierarchy and learning objectives** → `state/config/course_context.yaml`
4. **Run presets, quality thresholds, retry policy** → `state/config/tool_policies.yaml`
5. **Platform allocation decisions** → `resources/exemplars/` (reference patterns)
6. **Accessibility standards** → `resources/style-bible/` (detailed); fallback to `config/content-standards.yaml` if no style bible exists
7. **Learned preferences and patterns** → `_bmad/memory/{agent}-sidecar/patterns.md`

## Anti-Patterns

- Never store brand identity in `state/config/style_guide.yaml` — that's for tool dial settings only
- Never treat `config/content-standards.yaml` as authoritative when a style bible exists
- Never cache style bible content in agent memory — always re-read from disk
- Never write to `config/` or `resources/` from agent logic — these are human-curated
- Never confuse `state/config/tool_policies.yaml` (operational policy) with `resources/exemplars/policies/` (domain knowledge patterns)
