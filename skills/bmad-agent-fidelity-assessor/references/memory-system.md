# Memory System for Vera (Fidelity Assessor)

**Memory location:** `{project-root}/_bmad/memory/vera-sidecar/`

## Core Principle

Tokens are expensive. Only remember what matters: gate-specific fidelity patterns, user correction calibration, and recurring fidelity issues per producing agent and fidelity class.

## File Structure

### `index.md` — Primary Source

**Load on activation.** Contains:
- Active assessment context: current gate, production run ID, artifacts under evaluation
- Calibration summary: key severity adjustments based on human waiver/correction patterns
- Recurring fidelity patterns: top fidelity issues per gate and producing agent
- Transient ad-hoc session section (cleared on switch to default)

**Update:** When calibration changes, recurring patterns shift, or assessment cycle completes.

### `access-boundaries.md` — Access Control

**Load on activation.** Contains:
- **Read access** — Entire project repository, `state/config/fidelity-contracts/`, `skills/sensory-bridges/`, `course-content/`, all artifact paths received in context envelopes, `docs/fidelity-gate-map.md`, `docs/source-ref-grammar.md`, `docs/app-design-principles.md`, `{project-root}/_bmad/memory/vera-sidecar/`
- **Write access** — `{project-root}/_bmad/memory/vera-sidecar/` only
- **Deny zones** — `.env`, project-level API client code, `course-content/` (write — verify only, never modify), other agents' sidecars (write), `resources/style-bible/` (write), `.cursor-plugin/`, `tests/` (write), `state/config/fidelity-contracts/` (write — contracts are human-authored)

Before any file operation, verify the path is within allowed boundaries.

### `patterns.md` — Learned Patterns

**Load when needed.** Contains:
- Gate-specific fidelity patterns: which gates and producing agents produce which recurring fidelity issues
- Fidelity class patterns: common issues per class (literal-text verbatim failures, creative over-invention, literal-visual placement errors)
- Human correction calibration: which findings the user waives, accepts, or adjusts — and the rationale
- Source_ref resolution patterns: common broken ref patterns and their likely intended targets
- Medical content sensitivity: terminology alterations that were flagged as critical vs. acceptable

**Format:** Append-only, default mode writes only. Condense periodically.

### `chronology.md` — Timeline

**Load when needed.** Contains:
- Assessment history: gate, production run ID, producing agent, finding count by O/I/A category and severity, verdict (pass/fail), fidelity score
- Circuit breaker events: when and why the pipeline was halted, retry outcomes
- Human waiver events: which findings were waived, the rationale provided
- Calibration events: when and why severity classifications were adjusted

**Format:** Append-only, default mode writes only. Prune regularly.

## Mode-Aware Write Rules

- **Default mode:** All sidecar files writable per rules above. Assessment outcomes persisted.
- **Ad-hoc mode:** All files read-only except transient section in `index.md`. Fidelity assessment still EXECUTES but results not persisted to sidecar.

L1 contract files are NEVER written by Vera — they are human-authored and version-controlled.

## Memory Persistence Strategy

### Write-Through (Immediate)

Persist immediately when:
1. Human provides correction or waiver (calibration data)
2. Circuit breaker triggered (critical event)
3. New recurring pattern detected (3+ occurrences of same fidelity issue from same agent at same gate)

### Save Triggers

- Fidelity assessment cycle completes (capture findings summary)
- Human waives or adjusts a finding (calibration data)
- Pattern threshold crossed (recurring issue count reaches 3+)
- Session ends with outstanding assessment context

Memory is updated via the Save Memory capability which reads current index.md, updates with session context, writes condensed version, and checkpoints patterns/chronology if significant changes occurred.

## First Run

If sidecar doesn't exist, load `./references/init.md` to create the structure.
