# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> Current objective: Execute the long-deferred fresh trial production run against the APC C1-M1 Tejal source, now that Texas's runtime runner is live and the G3.5 lockstep gap is closed.

## Current State (as of 2026-04-17 wrapup)

- Active branch: `dev/marcus-sanctum-migration` (name retained; Marcus migration deferred in favor of Texas production-readiness this session)
- Working tree has ~25 files of uncommitted changes from this session — operator owns the commit decision (see Step 12 of the wrapup protocol)
- Full repo regression: **919 passed, 2 skipped, 0 failed**
- Contract validator: **9 contracts, 79 criteria, 0 errors**
- Structural walks: **3/3 READY**
- **Epic 25 / Story 25-1 — DONE.** Texas runtime wrangling runner shipped with layered BMAD code review clean (3 lenses, 13 MUST-FIX+SHOULD-FIX remediations, 18 tests).
- **G3.5 remediation — DONE** earlier this session. All 9 fidelity contracts reorganized; G3.5 row removed from gate-map; new `blocks_on:` declarative precondition field added.

## Immediate Next Action

**Execute a fresh trial production run using prompt pack v4.2g.** The three blockers that prevented trial runs through the prior session are now closed:

1. **30-line-stub risk is preventable** — Texas's extraction_validator (4-tier classification) now runs via `run_wrangler.py`, and the prompt pack's Prompt 3 retains the hard word-count check as a belt-and-suspenders assertion.
2. **G3.5 lockstep gap is closed** — G3.5 row removed from `docs/fidelity-gate-map.md`; its checks now live as deterministic sub-criteria G3-08..G3-12 in `state/config/fidelity-contracts/g3-generated-slides.yaml`. Validator enforces the new ordering invariant.
3. **Texas is wired at runtime** — Prompt 3 invokes `python skills/bmad-agent-texas/scripts/run_wrangler.py --directive ... --bundle-dir ...` directly. Exit codes 0/10/20/30 drive Marcus's halt-vs-proceed decision. The `--legacy-prose` fallback is documented as a safety net if the runner surprises anyone mid-pipeline.

### Trial Run Playbook

- Source: `course-content/courses/tejal-APC-C1/APC_C1-M1_Tejal_2026-03-29.pdf`
- Cross-validation asset: `course-content/courses/tejal-APC-C1/C1M1Part01.md`
- Invoke Marcus per v4.2g prompt pack, Prompt 1 onward. Prompt 3 is the Texas integration point — pay attention to `extraction-report.yaml` output for tier classification + cross-validation results.
- Monitor via the run HUD (`python scripts/utilities/run_hud.py --open`) — three tabs (System Health, Production Run, Dev Cycle).

### Key Risks for the Trial Run

- **Texas runner has zero real-trial evidence.** Every test used synthetic fixtures. First real trial is the first time the runner faces a production PDF. The `--legacy-prose` fallback is the escape hatch.
- **First cross-validation run against real content.** `cross_validator.py` was unit-tested against real content in a prior session but has never been invoked from the runner with a real Notion-exported MD cross-referenced against a PDF extraction.
- **Expected tier-1 path** for the APC C1-M1 source (~24 pages, ~6000 expected words). If the tier comes out DEGRADED or FAILED, the runner will exit 20 and halt the run — consult `blocking_issues[]` in `result.yaml`.

## Alternative Paths

**If deferring the trial run:**
- **Marcus sanctum migration** — the session-START party-mode team produced a full design pass before the Texas pivot. John proposed Epic 25 originally (now used by Texas) → new epic would be needed; Winston recommended identity-extraction over First Breath; Murat recommended Dan→Marcus→Irene pilot sequence with a Marcus golden-path test BEFORE migration. Amelia estimated per-agent effort. All of this is in the 2026-04-17 session transcript.
- **Follow-up stories filed during Texas review** (none blocking):
  - Vera-side G0 gate runner that consumes `extraction-report.yaml` and emits `gates/gate-03-result.yaml`
  - Explicit fallback-chain orchestration inside the runner
  - Git-SHA-derived version strings replacing hand-maintained `@2026-04-17` dates
  - Manifest self-inclusion strategy for `result.yaml` hash provenance

## Branch Metadata

- Repository baseline branch: `master` (synced with `origin/master` at 2026-04-17 wrapup — includes this session's merge of `dev/epic-25-texas-runner`)
- Next working branch: `dev/trial-run-c1m1-tejal-20260417` (created from updated `master` and pushed to origin with upstream set; intended for the fresh trial run)
- Closed-out working branch (archived on origin): `dev/epic-25-texas-runner` (contains Epic 25 Story 25-1 + G3.5 remediation; merged cleanly into `master` this session)

Resume commands (PowerShell):

```powershell
cd c:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS
git checkout dev/trial-run-c1m1-tejal-20260417
git pull origin dev/trial-run-c1m1-tejal-20260417
git status --short
git log --oneline -5
```

## Unresolved Issues / Risks

- **Uncommitted worktree** as of wrapup — operator owns the commit decision.
- **Branch name is misleading** — `dev/marcus-sanctum-migration` but work was Texas-focused. Rename or create a new branch before the trial run if clarity matters.
- **`pyproject.toml` build-backend is broken** (`setuptools.backends._legacy:_Backend` is not a real module). Pre-existing. Fix is a one-liner change to `setuptools.build_meta`, but unrelated to this session's scope.
- **First-trial-run-under-Texas risk** — runner has library-level confidence but zero runtime confidence against real production input. Plan accordingly.
- **Marcus sanctum migration still pending** — branch name says so but session deferred the work.
- **No Audra findings carried forward from Step 0a** — session wrapup sweep was clean.

## Hot-Start Files

- `SESSION-HANDOFF.md` — backward-looking record of this session
- `_bmad-output/implementation-artifacts/25-1-texas-runtime-wrangling-runner.md` — story 25-1 artifact (done, with Review Record)
- `skills/bmad-agent-texas/scripts/run_wrangler.py` — the runner CLI
- `skills/bmad-agent-texas/references/extraction-report-schema.md` — v1.0 schema
- `skills/bmad-agent-texas/references/delegation-contract.md` — Marcus↔Texas contract with Runtime Invocation section
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` — Prompt 3 now invokes runner; `--legacy-prose` fallback documented
- `scripts/validate_fidelity_contracts.py` — enforces the new A2 ordering + `blocks_on:` invariants
- `state/config/fidelity-contracts/g3-generated-slides.yaml` — G3-08..G3-12 criteria (formerly G3.5)
- `state/config/fidelity-contracts/_schema.yaml` — schema doc with `blocks_on:` spec
- `tests/test_validate_fidelity_contracts.py` — 17 tests for validator invariants
- `skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py` — 18 runner tests
- `reports/dev-coherence/2026-04-17-0034/` — G3.5 remediation audit trail
- `reports/dev-coherence/2026-04-17-0142/` — session-wrapup audit trail
- `course-content/courses/tejal-APC-C1/` — source for the trial run

## Run HUD

```
.venv/Scripts/python -m scripts.utilities.run_hud --open
```

Three tabs: System Health / Production Run / Dev Cycle. Auto-refreshes every 10 seconds.

## Protocol Status

Follows the canonical BMAD session protocol pair ([bmad-session-protocol-session-START.md](bmad-session-protocol-session-START.md) / [bmad-session-protocol-session-WRAPUP.md](bmad-session-protocol-session-WRAPUP.md)).
