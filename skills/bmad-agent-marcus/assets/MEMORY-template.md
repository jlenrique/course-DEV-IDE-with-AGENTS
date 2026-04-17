# Memory

Curated long-term knowledge. Session logs live in `sessions/`; this file is the durable distillation.

## Current Run State

_Updated per session. If there's an active tracked run, record:_

- **Run ID:**
- **Phase / gate:**
- **Last action:**
- **Next planned action:**
- **Known blockers:**

## Routing Learnings

_Patterns about which specialist handles which content family best, when to use which workflow template, etc._

- (empty until observations accumulate)

## Operator Preferences

_Promoted from BOND when they stabilize into patterns._

- (empty)

## Open Questions

_Things the operator hasn't resolved that affect future runs. Date-stamped so stale items can be pruned._

- (empty)

## Known Gotchas

_Windows/encoding quirks, tool-version pitfalls, API rate-limit patterns — anything I learned the hard way and future-me needs to know._

- **2026-04-17**: Windows cp1252 stdio encoding crashes on `↔` characters in some CLI help output. Use `PYTHONIOENCODING=utf-8` when invoking Python subprocesses that may print Unicode. Discovered via Texas runner `--help` crash.
- **2026-04-17**: `pyproject.toml` build-backend is broken (`setuptools.backends._legacy:_Backend` not a real module). Pre-existing; fix is one-liner to `setuptools.build_meta`. Out of scope for my orchestration work.

## Historical Context

_Anchors that help me understand "why things are the way they are" across sessions._

- **2026-04-17**: Migrated from legacy sidecar (`_bmad/memory/marcus-sidecar/`) to BMB sanctum (`_bmad/memory/bmad-agent-marcus/`) as Epic 26 Story 26-1 pilot. The old sidecar path is deprecated but retained for backward compatibility; 2 runtime callers still reference it (`scripts/state_management/init_state.py`, `tests/test_state_management.py`). Epic 27 will remove.
- **2026-04-17**: Legacy SKILL.md (249 lines) split into this sanctum (identity/doctrine) + `references/` (operational runbooks). New SKILL.md is a terse router.
- **Epic 25 (2026-04-17):** Texas runtime wrangling runner shipped. My Prompt-3 delegation now invokes `skills/bmad-agent-texas/scripts/run_wrangler.py` directly with exit codes 0/10/20/30 driving halt-vs-proceed. `--legacy-prose` fallback is the safety net.
- **Epic 23 (2026-04-15):** Cluster-aware Irene Pass 2 closed. Live mode is cluster-aware refinement, not structural-coherence-check.
