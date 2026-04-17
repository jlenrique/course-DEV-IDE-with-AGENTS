# Memory System for Audra

**Memory location:** `{project-root}/_bmad/memory/audra-sidecar/`

## Core Principle

Audra's sidecar captures **patterns**, not **snapshots**. Git has the snapshots; trace reports under `reports/dev-coherence/` have the per-run evidence. Audra's memory records what repeated sweeps across sessions have taught her — drift velocity per contract pair, which L1 checks most often catch real issues, which L2 findings tend to be false positives, which story types or authors produce which kinds of closure-artifact gaps.

Tokens are expensive. Only remember what matters. Condense everything to its essence.

## File Structure

### `index.md`

Load on every activation. Contains:

- Current invocation context: anchor commit, scope, workflow, invocation source (operator-direct / Cora-route / Marcus-route-via-Cora)
- Last three sweep summaries in compressed form (exit code + one-line)
- Operator preferences: which L2 check families the operator has asked Audra to emphasize or mute
- Transient session section (cleared on next invocation)

### `patterns.md`

Durable cross-session learnings. Examples:

- "`parameter-directory.md` drifts from schema ~1 in every 5 stories that touch narration-time parameters; rarely on runtime-only stories."
- "Closure-artifact gaps on `done` stories: most common class is missing 'remediated review record'; next is missing automated verification."
- "Placement violations under `state/config/` vs `config/` correlate with stories touching parameter families; add emphasis on the placement check for those stories."

Append only on crystallized patterns (3+ confirming observations).

### `chronology.md`

Append-only dated log. Format: `YYYY-MM-DD HH:MM — <run-type> <scope>. L1 exit <code>. <N> L1 findings, <N> L2 findings.`

### `access-boundaries.md`

See that file. Audra is **read-mostly** across the repo and **write-scoped** to her own sidecar plus trace reports under `reports/dev-coherence/`.

## Load Order

1. `./references/memory-system.md` (this file)
2. `access-boundaries.md`
3. `index.md`
4. `patterns.md` (on every sweep, to inform check-emphasis decisions)
5. `chronology.md` (on request)

## What Not to Cache

Never cache file contents. The L1 sweep re-reads every artifact fresh. Drift detection depends on fresh reads; caching would defeat the purpose.
