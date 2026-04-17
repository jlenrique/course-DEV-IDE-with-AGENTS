# Memory System for Marcus

**Memory location:** `{project-root}/_bmad/memory/marcus-sidecar/`

## Core Principle

Tokens are expensive. Only remember what matters. Condense everything to its essence. Style bible and exemplar content is NEVER cached in memory — always re-read from `resources/style-bible/` and `resources/exemplars/` fresh from disk.

## File Structure

### `index.md` — Primary Source

**Load on every activation.** Contains:
- Active production context: current run ID, module/lesson in progress, outstanding tasks
- User preferences: preferred voices, style parameters, review cadence, communication preferences
- Current run mode (default/ad-hoc)
- Transient ad-hoc session section (cleared on switch back to default)

**Update:** When essential context changes (immediately for critical data).

### `access-boundaries.md` — Access Control

**Load on activation.** Contains:

#### Read Access (both modes)
- Entire project repository (all source, docs, configs, planning artifacts)
- `config/` — bootstrap content defaults (fallback only — superseded by style bible when present)
- `state/config/` — mutable per-tool parameter preferences, course context hierarchy, run preset policies
- `state/runtime/` — SQLite database (production runs, coordination, quality gates)
- `{project-root}/_bmad/memory/marcus-sidecar/` — own sidecar (primary)
- `{project-root}/_bmad/memory/*-sidecar/` — other agent sidecars (read-only, for coordination context)
- `resources/style-bible/` — **authoritative** brand identity, visual design system, voice/tone, accessibility standards
- `resources/exemplars/` — worked production patterns, platform allocation policies and matrices
- `resources/tool-inventory/` — tool access matrix and capability reference
- `course-content/` — all courses, staging, templates
- `BOX_DRIVE_PATH` (environment variable) — local filesystem reference materials
- Notion pages via `source-wrangling` skill (API read)

#### Write Access (default mode)
- `state/config/style_guide.yaml` — save learned tool parameter preferences via conversation
- `state/runtime/` — production run state, coordination records
- `{project-root}/_bmad/memory/marcus-sidecar/` — own memory sidecar (all files)
- `course-content/staging/` — production drafts awaiting review
- `course-content/courses/` — only after explicit human approval at review gate
- Notion pages via `source-wrangling` skill (API write — feedback, readiness assessments)
- **Never writes to**: `config/` (static project defaults), `resources/style-bible/` (human-curated), `resources/exemplars/` (human-curated)

#### Write Access (ad-hoc mode — strict subset)
- `course-content/staging/ad-hoc/` — scratch area only
- `{project-root}/_bmad/memory/marcus-sidecar/index.md` — transient ad-hoc session section only
- All other state writes suppressed

#### Deny Zones (both modes — never write)
- `.env` — never read or write secrets directly
- `.cursor-plugin/plugin.json` — plugin manifest is infrastructure
- `config/` — static project defaults, not agent-writable
- `resources/` — human-curated reference libraries, not agent-writable
- API client source code — Marcus never modifies connectivity layer code
- `tests/` — Marcus doesn't write or modify tests
- Other agents' memory sidecars — read yes, write never

**Critical:** On every activation, load these boundaries first. Before any file operation, verify the path is within allowed boundaries.

### `patterns.md` — Learned Patterns

**Load when needed. Default mode writes only. Append-only, periodically condensed.**
- Successful workflow sequences (e.g., "slides → review → voiceover → assembly" works better than parallel)
- Parameter combinations the user approved (e.g., "ElevenLabs voice Rachel for clinical narration")
- Common revision patterns (e.g., "user always adjusts slide count downward on first review")
- Specialist performance notes (e.g., "Gamma produces better results with detailed outlines vs. brief prompts")
- Fidelity discovery patterns: user's common responses to visual/textual fidelity queries, typical literal slide counts per deck, content types that consistently trigger fidelity flags, hosting workflow preferences (Gamma workspace upload vs. other), Imagine export settings that produce best results

### `chronology.md` — Timeline

**Load when needed. Default mode writes only. Append-only.**
- Production run history: run ID, content type, module/lesson, start/end timestamps, outcome
- User satisfaction signals: approved on first review, required revisions, explicit feedback
- Tool usage log: which specialists were invoked, parameters used, results quality

## Mode-Aware Write Rules

| File | Default Mode | Ad-Hoc Mode |
|------|-------------|-------------|
| `index.md` | Full write | Transient ad-hoc section only |
| `access-boundaries.md` | Read-only (set at build time) | Read-only |
| `patterns.md` | Append, condense | Read-only |
| `chronology.md` | Append | Read-only |

## Memory Persistence Strategy

### Write-Through (Immediate)
- User preference changes
- Production run state transitions
- Mode switches
- Explicit save requests (SM capability)

### Checkpoint (Periodic)
- After completing production stages
- After review gate decisions
- When context has accumulated significantly

## Memory Maintenance

Periodically condense `patterns.md` and `chronology.md` to keep them lean. Prune outdated entries — a pattern from six months ago that has been superseded is noise.

## First Run

If sidecar doesn't exist, load `./references/init.md` to create the structure.
