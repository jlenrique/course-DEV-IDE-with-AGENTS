# Story 26-5: BMB Scaffold Preservation Semantics

**Epic:** 26 — BMB Sanctum Migration
**Tier:** Scaffold hardening (backlog — open before batch migration wave)
**Status:** backlog
**Opened:** 2026-04-17 (Story 26-4 close-out)
**Predecessors:** 26-4 (scaffold v0.2 shipped)

## Story

As the platform maintainer, I want the BMB scaffold's `--force` re-render to preserve operator-edited sanctum content, so that re-scaffolding during the 14-agent batch migration wave (and beyond) doesn't clobber accumulated First-Breath work.

## Why This Is Backlog, Not Done

Party-mode consensus during Story 26-4 was split:

- **Winston (architect):** preservation semantics is the right primitive; build it in 26-4 so the batch wave inherits it.
- **Amelia (dev):** YAGNI — 3 pilots, gitignored sanctums, no operator edits yet; `--force` is sufficient now.
- **John (PM):** "Winston's not wrong, he's just early." Preservation matters once operator edits accumulate at scale; deferring until then is legitimate iteration discipline.
- **Murat (test architect):** whichever way, the preservation heuristic needs snapshot-style regression tests to prevent false positives clobbering real edits.

Landing: defer to 26-5, open the story NOW so it's visible and can't slip through the cracks.

## When to Run This

**Before any agent in the batch wave has completed a real First Breath that writes custom content into their BOND/MEMORY/PERSONA/CREED files.** Once operator edits are live, re-scaffolding `--force` becomes dangerous. The window is: after 26-4 closed, before batch wave begins.

## Acceptance Criteria (draft — refine at open)

- **AC1** — Scaffold detects "template-rendered" files by signature (e.g., contains `"friend"` literal OR known absolute Windows path literal OR literal `{sanctum_path}` token). These files are eligible for overwrite.
- **AC2** — Scaffold detects "operator-edited" files by absence of template signatures AND mtime newer than the template source. These files are preserved.
- **AC3** — `--force` retains v0.2 semantics (overwrite everything) but gains a companion flag `--preserve-edits` that engages preservation heuristic.
- **AC4** — Regression test: snapshot Marcus/Irene/Dan sanctums, inject a simulated operator edit, run scaffold `--preserve-edits`, verify edit survives while buggy-signature files get rewritten.
- **AC5** — False-positive test: operator edit that accidentally contains a buggy signature — document the tradeoff and ensure the operator is warned (not silently clobbered).

## Risks Forward

- **False positive:** operator legitimately writes the word "friend" somewhere → heuristic clobbers their edit. Mitigation: signature must be structured (e.g., `"- **Operator:** friend"` exact-match, not bare "friend").
- **False negative:** buggy template-rendered file survives because the operator touched it. Mitigation: mtime + content-signature joint check.

## Not In Scope for 26-5

- ASCII purity lint (deferred to a future 26-6 if ever needed)
- `.gitkeep` in empty `scripts/` directory (low-value nit; scaffold v0.2 still only drops `.gitkeep` in `sessions/` and `capabilities/`)
- Deep YAML merge for nested config keys (current configs are flat; defer until a real nested-config use case emerges)

## Reference Artifacts

- `scripts/bmb_agent_migration/init_sanctum.py` (v0.2 current)
- `_bmad-output/implementation-artifacts/epic-26/_shared/scaffold-v0.2-backlog.md` (v0.2 shipped spec)
- `tests/migration/test_bmb_scaffold.py` (43 tests as of 26-4 close)
