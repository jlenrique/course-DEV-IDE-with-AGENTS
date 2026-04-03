# Next Session Start Here

> Scope note: this file tracks **APP project + operator ramp-up** state. For production content operations, still use `docs/workflow/production-session-launcher.md` at session open.

## Operator intent (locked for next session)

**Start a fresh production run** — new `RUN_ID`, new bundle folder, and a new frozen `run-constants.yaml` for *that* run. The Tejal `C1-M1-PRES-20260403` bundle remains valid **reference material** only unless you explicitly choose to resume it.

## BMAD party mode consensus (2026-04-03)

Facilitated alignment on the **controlled shift close** + **handoff** + your **fresh-run** intent:

| Agent | Consensus |
|-------|-----------|
| **Winston** (architect) | Land the tooling on a **clean known revision** (`commit`/`merge` to baseline) before long production execution — avoids “which code validated my constants?” ambiguity. Single worktree; branch `RUN/<date>` or `master` after merge both OK if hygiene gates pass. |
| **Mary** (analyst) | **“Fresh run”** is a **new scope contract**: restate course/module/lesson, sources, and theme in the Run Constants block — do not silently inherit the Tejal PDF paths unless that is still the deliberate scope. |
| **John** (PM) | First user-facing outcome of the new session = **production value** (content pipeline), not more APP work — after the small commit gate, Marcus leads with **launcher + v4**, not feature coding. |
| **Amelia** (dev) | `pytest tests/` already green on the wiring; after commit, only re-run if you touch code. **`run_constants` + `--bundle-dir`** are the canonical mechanical checks for the new bundle. |
| **Quinn** (QA) | **Fail-closed**: session readiness **with preflight** + optional `--bundle-dir` **before** v4 Prompt 1; no ingestion without **Prompt 2A** / `operator-directives.md` when on v4 tracked path. |
| **Bob** (SM) | Ordered day-one checklist: **(1)** commit/stash APP delta → **(2)** `production-session-launcher` (full startup) → **(3)** create bundle dir → **(4)** freeze **new** `run-constants.yaml` → **(5)** readiness + Marcus §1. |

**Unanimous:** The previous decision to **document state in handoff files** and **close controlled** (not emergency) stays valid; the only amendment is **prioritizing a new run** over auto-continuing Tejal.

---

## Immediate next action (do this first)

1. **Commit or stash** the pending working tree (run-constants loader, readiness/validator wiring, docs, tests) — **party mode: do not skip**; protects the revision you will run production against.
2. **Fresh production run:** execute `docs/workflow/production-session-launcher.md` in full (Marcus startup protocol). Declare execution mode + quality preset again for *this* shift.
3. Create a **new** tracked bundle directory under `course-content/staging/tracked/source-bundles/<new-folder>/`, fill and freeze **`run-constants.yaml`** (`bundle_path` must match that folder).
4. Run:
   - `python -m scripts.utilities.app_session_readiness --with-preflight --bundle-dir <new-bundle-path>`
   - `python -m scripts.utilities.run_constants --bundle-dir <new-bundle-path> --verify-paths --json` (recommended)
5. Marcus **v4 Prompt 1** for the **new** `RUN_ID` (write `preflight-results.json` into the new bundle per pack).

**Optional — resume Tejal only if you explicitly want that scope:** use `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260403` and its existing `run-constants.yaml` instead of steps 3–5 above.

## Unresolved issues / blockers (must not be buried)

- **Dirty git tree:** Multiple modified + new files from run-constants feature; **not** on `origin` until you commit/push — **blocks a clean “fresh run” narrative** until resolved.
- **Tejal run `C1-M1-PRES-20260403`:** Abandoned for **fresh run** unless you opt back in; only `run-constants.yaml` may exist locally — **no** `production_runs` row, **no** `operator-directives.md` (harmless if you use a **new** bundle instead).
- **Every new tracked run:** `operator-directives.md` still **mandatory before ingestion** (v4 Prompt 2A).

## Branch metadata (after 2026-04-03 shift close)

| | |
|--|--|
| **Repository baseline** | `master` (harmonization + prior work merged; confirm `git pull` if others commit) |
| **Current working branch** | `RUN/Friday-2026-04-03` (local; may have uncommitted changes) |
| **Next working branch (if you finish the run branch)** | Return to `master` after merge, or create `RUN/<next-date>` for the next production day |

```powershell
cd C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS
git status --short
git branch --show-current
# To resume on master after landing commits:
# git checkout master
# git pull origin master
```

## Current dev state (as of 2026-04-03, shift close sync)

- **BMAD epics:** all **done** (11 epics, 47 stories) — no sprint story required for the run-constants wiring unless you choose to log ad-hoc work.
- **New infrastructure:** `scripts.utilities.run_constants`; session readiness `--bundle-dir`; validator honors `run-constants.yaml` when present. See `docs/workflow/trial-run-pass2-artifacts-contract.md` §1B (v1.2).

## Worktree hygiene

- **Expected:** single primary worktree at `C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS`.
- If stale entries appear: `git worktree prune --verbose`.

## Hot-start paths

- **New run:** you choose `course-content/staging/tracked/source-bundles/<new-bundle>/run-constants.yaml` (create on day one).
- **Reference only (Tejal frozen, prior intent):** `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260403/run-constants.yaml`
- **Ad-hoc reference bundle (prior Tejal work):** `course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/`
- **Prompt pack:** `docs/workflow/trial-run-prompts-to-irene-pass2-v4.md`
- **Operator card:** `docs/workflow/trial-run-v3-operator-card.md`
- **First tracked run checklist:** `docs/workflow/first-tracked-run-checklist.md`
- **Status artifacts:** `_bmad-output/implementation-artifacts/sprint-status.yaml`, `bmm-workflow-status.yaml`

## Quality gate snapshot (2026-04-03)

- `pytest tests/`: **227 passed** (after run-constants wiring).
- Session readiness + preflight: **pass** when last run in session.

## Gotchas

- `course-content/staging/` is **gitignored** — bundle + `run-constants.yaml` do not travel with `git push`; back up locally if needed.
- `runTests` / IDE test discovery may miss some Marcus script tests; **`pytest tests/ ...`** by path is reliable.
- PowerShell: use **semicolons**, not `&&`, unless your shell profile enables chaining.
