# Memory System for Quinn-R

**Memory location:** `{project-root}/_bmad/memory/quinn-r-sidecar/`

## Core Principle

Tokens are expensive. Only remember what matters: calibration with the human reviewer, recurring quality patterns per specialist, and effective feedback phrasings that lead to quick fixes.

## File Structure

### `index.md` — Primary Source

**Load on activation.** Contains:
- Active review context: current run ID, artifacts under review
- Calibration summary: key severity adjustments based on human reviewer feedback
- Recurring issue patterns: top 3 recurring quality issues across recent reviews
- Transient ad-hoc session section (cleared on switch to default)

**Update:** When calibration changes or recurring patterns shift.

### `access-boundaries.md` — Access Control

**Load on activation.** Contains:
- **Read access** — Entire project repository, `resources/style-bible/`, `state/config/`, `state/runtime/coordination.db`, `course-content/`, `{project-root}/_bmad/memory/quinn-r-sidecar/`, `skills/quality-control/`
- **Write access** — `{project-root}/_bmad/memory/quinn-r-sidecar/`, `state/runtime/coordination.db` (quality_gates table via quality_logger.py only)
- **Deny zones** — `.env`, project-level API client code, `course-content/` (write — review only, never modify), other agents' sidecars (write), `resources/style-bible/` (write), `.cursor-plugin/`, `tests/`

Before any file operation, verify the path is within allowed boundaries.

### `patterns.md` — Learned Patterns

**Load when needed.** Contains:
- Specialist quality patterns: which specialists produce which recurring issues
- Human reviewer calibration: which findings the user accepts/rejects/adjusts
- Effective feedback patterns: which phrasings lead to quick fixes vs. confusion
- Quality trend data: improvement or regression per dimension over time
- Accessibility issue catalog: specific WCAG violations with proven fix patterns

**Format:** Append-only, default mode writes only. Condense periodically.

### `chronology.md` — Timeline

**Load when needed.** Contains:
- Review history: run ID, artifact type, producing specialist, findings by severity, pass/fail by dimension
- Human review outcomes: which findings the human agreed with, adjusted, or dismissed
- Calibration events: when and why severity classifications were adjusted

**Format:** Append-only, default mode writes only. Prune regularly.

## Mode-Aware Write Rules

- **Default mode:** All sidecar files writable per rules above. Quality results logged to SQLite via `quality_logger.py`.
- **Ad-hoc mode:** All files read-only except transient section in `index.md`. Quality review still EXECUTES but results not persisted to sidecar or SQLite.

Style bible content is NOT cached in memory — always re-read from disk as primary quality rubric.

## Memory Persistence Strategy

### Write-Through (Immediate)

Persist immediately when:
1. Human reviewer provides calibration feedback (severity adjustment)
2. New recurring pattern detected (3+ occurrences of same issue from same specialist)
3. Review cycle completes with notable findings

### Save Triggers

- Quality review cycle completes (capture findings summary)
- Human reviewer accepts or rejects agent findings (calibration data)
- Pattern threshold crossed (recurring issue count reaches 3+)
- Session ends with outstanding calibration context

Memory is updated via the Save Memory capability which reads current index.md, updates with session context, writes condensed version, and checkpoints patterns/chronology if significant changes occurred.

## First Run

If sidecar doesn't exist, load `./references/init.md` to create the structure.
