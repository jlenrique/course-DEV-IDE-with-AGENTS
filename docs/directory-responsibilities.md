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

**Does NOT contain**: brand identity, colors, typography, voice/tone, or accessibility standards. Those live in `resources/style-bible/`.

### `state/runtime/` — Ephemeral Runtime State

Not git-versioned. Operational state that doesn't survive a fresh clone.

| Item | Contents |
|------|----------|
| `coordination.db` | SQLite — production runs, agent coordination, quality gate records |
| `backup/` | Database backup and restore scripts |

### `resources/style-bible/` — Authoritative Brand Reference

The single source of truth for all brand and content standards. Human-curated, not agent-writable.

| File | Contents |
|------|----------|
| `master-style-bible.md` | Color palette (hex values), typography system, imagery standards, voice characteristics, writing style guidelines, content structure templates, tool-specific translation prompts, quality assurance checklists |

Marcus and specialist agents re-read this fresh for each production task — never cached in memory.

### `resources/exemplars/` — Worked Production Patterns

Proven patterns from past production decisions. Reference material, not configuration.

| Subdirectory | Contents |
|--------------|----------|
| `policies/` | Platform allocation decision frameworks (Canvas vs CourseArc criteria) |
| `platform-matrices/` | Worked allocation examples from actual course modules |

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
