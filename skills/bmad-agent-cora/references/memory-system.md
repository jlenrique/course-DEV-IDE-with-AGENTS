# Memory System for Cora

**Memory location:** `{project-root}/_bmad/memory/cora-sidecar/`

## Core Principle

Cora's sidecar captures **patterns**, not **snapshots**. Git has the snapshots. Cora's memory records what repeated behavior across dev sessions has taught her — which docs drift most often, which session types leave the hot-start pair stale, which harmonization depths the operator prefers in which contexts, which stories tend to arrive at closure with artifacts missing.

Tokens are expensive. Only remember what matters. Condense everything to its essence.

## File Structure

### `index.md` — Primary Source

Load on every activation. Contains:

- Active dev-session context: last session anchor commit, current branch, outstanding pre-closure findings, intended next anchor task
- Operator preferences: preferred harmonization scope default, pre-closure hook preference (warn / silent), Paige-routing threshold for prose drift
- Last three session-WRAPUP summaries in compressed form
- Transient session section (cleared on next WRAPUP)

Update when essential context changes (immediately for critical data).

### `patterns.md` — Durable Learnings

Accumulates cross-session learnings. Examples:

- "`docs/project-context.md` dated updates tend to lag behind code by ~1 week; flag on every session-START after the 7-day mark."
- "`parameter-directory.md` and `parameter-registry-schema.yaml` rarely drift when a story touches only runtime; they drift often when a story touches narration-time parameters."
- "Operator prefers harmonization at session-START but skips at WRAPUP when time is short."

Update when a pattern crystallizes across 3+ sessions. Never single-session observations.

### `chronology.md` — Dated Milestones

Append-only log of dated session milestones. Format: `YYYY-MM-DD HH:MM — one-line summary`. Used for Cora's "what did I do last time we talked" recall without having to re-read the handoff pair.

### `access-boundaries.md` — Access Control

Load on activation. Defines read / write / deny zones. See that file for details.

## Load Order

1. `./references/memory-system.md` (this file) — discipline
2. `access-boundaries.md` — boundary enforcement
3. `index.md` — current context (always)
4. `patterns.md` (on request or when drafting recommendations)
5. `chronology.md` (on request or for recall)

## Mode Awareness

Cora is not mode-aware in the Marcus sense (tracked / ad-hoc) — dev sessions don't have execution-mode semantics. But Cora respects the operator's `/harmonize` scope preference as a session-scoped state in `index.md`.
