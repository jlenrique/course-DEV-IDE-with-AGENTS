# Memory System for Irene

**Memory location:** `{project-root}/_bmad/memory/content-creator-sidecar/`

## Core Principle

Tokens are expensive. Only remember what matters: which writers excel at which content types, which content structures the user approves, which patterns produce good downstream results.

## File Structure

### `index.md` — Primary Source

**Load on activation.** Contains:
- Active production context: current run ID, module/lesson in progress
- Content pipeline status: artifacts drafted, in review, approved
- Writer delegation queue: pending delegations, returned drafts awaiting review
- Transient ad-hoc session section (cleared on switch to default)

**Update:** When production context changes or delegation state transitions.

### `access-boundaries.md` — Access Control

**Load on activation.** Contains:
- **Read access** — `state/config/`, `resources/style-bible/`, `resources/exemplars/`, `course-content/`, `{project-root}/_bmad/memory/content-creator-sidecar/`, `docs/`, `course-content/_templates/`
- **Write access** — `{project-root}/_bmad/memory/content-creator-sidecar/`, `course-content/staging/`
- **Deny zones** — `.env`, project-level API client and state management code, other agents' sidecars (write), `resources/style-bible/` (write), `.cursor-plugin/`, `tests/`, `state/config/` (write)

Before any file operation, verify the path is within allowed boundaries.

### `patterns.md` — Learned Patterns

**Load when needed.** Contains:
- Writer effectiveness: which BMad writer produces best results for which content type
- Effective content structures the user approved on first pass
- Script-to-slide pairing patterns Gary handles cleanly
- Learning objective decomposition strategies that work for different course levels
- Common revision patterns: what the user consistently adjusts
- Assessment design preferences by Bloom's level
- Fidelity classification patterns: which content types consistently need literal-text or literal-visual treatment, source material signals that predict literal needs (e.g., "Knowledge Check" headings), user correction patterns when fidelity tags are overridden

**Format:** Append-only, default mode writes only. Condense periodically.

### `chronology.md` — Timeline

**Load when needed.** Contains:
- Content production history: run ID, module/lesson, artifact types, writers used, review outcomes
- Writer delegation log: which writer, brief quality, prose quality, revision rounds
- User satisfaction signals: first-pass approvals, revision requests, explicit feedback

**Format:** Append-only, default mode writes only. Prune regularly.

## Mode-Aware Write Rules

- **Default mode:** All sidecar files writable per rules above
- **Ad-hoc mode:** All files read-only except transient section in `index.md`

Style bible and course context are NOT cached in memory — always re-read from disk.

## Memory Persistence Strategy

### Write-Through (Immediate)

Persist immediately when:
1. Writer delegation completes (effectiveness data)
2. User approves or revises content (satisfaction signal)
3. Production run completes (chronology entry)

### Save Triggers

- Content artifact assembly completes
- Writer delegation round finishes (capture effectiveness data)
- User provides explicit feedback on content quality
- Session ends with outstanding context

Memory is updated via the Save Memory capability which reads current index.md, updates with session context, writes condensed version, and checkpoints patterns/chronology if significant changes occurred.

## First Run

If sidecar doesn't exist, load `./references/init.md` to create the structure.
