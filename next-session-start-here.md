# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> **Current objective:** Remediate the 4 defects the 2026-04-17 trial surfaced, then restart the APC C1-M1 Tejal trial production run with a clean slate — reaching last session's halt-point in minutes, not hours.

## Immediate Next Action (pick-up point)

**Run BMAD Session Protocol Session START**, then pivot directly into the remediation batch described below.

The session START will load Cora for a since-handoff harmonization check, verify branch state, and summarize what's changed since this handoff anchor — expected fast because session WRAPUP already ran a full-repo L1 CLEAN sweep.

## Hot-Start Summary

Last session closed the Epic 26 pilot wave (Marcus 26-1, Irene 26-2, Dan 26-3 all BMB-migrated + scaffold v0.2 shipped as 26-4), wired the v4.2 prompt pack's new stages (Creative Directive + clustering) into Marcus's workflow templates, and opened the APC C1-M1 Tejal trial production run. **Trial halted at Prompt 1 on the `emit-preflight-receipt.py` validator** — a good halt that exposed a pack-doc-vs-code schema drift plus three other defect classes. Operator chose to end session, remediate, and restart fresh.

## Sequenced Remediation Plan for This Session

> **Status update (2026-04-17 pretrial-prep run, `dev/epic-26-pretrial-prep`):**
>
> - **Step 1 (progress_map.py remediation):** DONE via commit `1572819` (Juan's refactor) + session-1 baseline repair (commit `a944189`).
> - **Step 2 (pack-doc Run Constants schema repair):** SUPERSEDED by **Story 26-6 — Marcus Production-Readiness Capabilities**. Instead of rewriting the pack's "Run Constants" section to show canonical lowercase YAML, the section was stripped and moved into Marcus as capabilities **PR-PF (Preflight)** and **PR-RC (Run-Constants author+validate)**. The canonical reference is now [`docs/dev-guide/marcus-capabilities.md`](docs/dev-guide/marcus-capabilities.md); the archived pack-doc content lives at [`docs/workflow/archive/prompt-pack-preprompt-2026-04.md`](docs/workflow/archive/prompt-pack-preprompt-2026-04.md). Marcus now authors the YAML directly — no more hand-transcription from the pack.
> - **Step 3 (Texas wrangler intake expansion):** DEFERRED per scope-confirmation party-mode consensus (2026-04-17). Not in pretrial-prep run scope; revisit post first clean trial restart.
> - **Step 4 (Texas CLI cp1252 guard):** IN-SCOPE as **Story 26-7** (stretch) on the same pretrial-prep run.
> - **Step 5 (Audra L1-W docs-vs-code lockstep check):** THIN VERSION SHIPPED in session-1 commit `a944189` — `tests/contracts/test_pack_doc_matches_schema.py`. Fuller L1-W impl deferred.
> - **Step 6 (Trial restart):** pending completion of pretrial-prep run (26-6 + 26-7 + merge to master).
>
> Read the below as historical plan-of-record. The active work is tracked in the run charter at [`_bmad-output/implementation-artifacts/run-charters/pretrial-prep-charter-20260417.md`](_bmad-output/implementation-artifacts/run-charters/pretrial-prep-charter-20260417.md) and Story 26-6 at [`_bmad-output/implementation-artifacts/26-6-marcus-production-readiness-capabilities.md`](_bmad-output/implementation-artifacts/26-6-marcus-production-readiness-capabilities.md).

Before touching the trial, close as many of these 4 defects as possible. Order is ROI-descending: each unblocks a chunk of the restart path.

### Step 1 — Remediate ambient worktree state (Juan's `progress_map.py`)

**Unblocks:** green pytest baseline.

Juan has an uncommitted mid-refactor of `scripts/utilities/progress_map.py` (216 deletions, 35 insertions — replaced `_parse_epic_labels_from_comments` with hardcoded `WAVE_LABELS` dict) that breaks 34 tests. Must decide:

- **Option A (complete):** finish the refactor, update the 34 tests to expect the new WAVE_LABELS form, commit.
- **Option B (revert):** `git checkout scripts/utilities/progress_map.py` if the refactor direction was later reconsidered.
- **Option C (park):** stash and park in a feature branch for later.

Recommend A or B before remediating anything else. Session-owned work on top of a broken-baseline is noise. `git diff scripts/utilities/progress_map.py` for the full picture.

### Step 2 — Open Story 26-X (prompt-pack Run Constants schema repair) → fix the pack doc

**Unblocks:** operators setting up new runs from the pack alone hit PASS on first `emit-preflight-receipt.py`.

Backlog stub: [_bmad-output/implementation-artifacts/prompt-pack-v4-2-run-constants-schema-drift.md](_bmad-output/implementation-artifacts/prompt-pack-v4-2-run-constants-schema-drift.md)

Action: Paige tech-writer story. Rewrite pack Run Constants section (`docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` lines ~22-37) to show canonical **lowercase nested YAML** (`run_id:`, nested `motion_budget:` block, etc.) instead of UPPERCASE flat display. Validator (`scripts/utilities/run_constants.py:96-99`) unchanged. Acceptance: a fresh operator authoring `run-constants.yaml` from the pack alone → `emit-preflight-receipt.py` passes first try.

### Step 3 — Open Story 26-Y (Texas wrangler intake-surface expansion) → party-mode consensus + implement

**Unblocks:** Images and DOCX become first-class source types. This is the bigger story of the four.

Backlog stub: [_bmad-output/implementation-artifacts/texas-visual-source-gap-backlog.md](_bmad-output/implementation-artifacts/texas-visual-source-gap-backlog.md) (severity: High after DOCX drift surfaced)

Action sequence:
1. **Party-mode consensus** on A (extend runner) vs B (sibling wrangler Texas orchestrates). Invite Winston (runner architecture) + Amelia (implementation cost) + Murat (test boundary) + Paige (transform-registry doc SSOT).
2. Per operator scope direction: **"Texas as wrangler must be savvy at finding and handling anything and everything"** → Option C (reject) withdrawn. Texas accepts all; routes deliberately.
3. Close both defects in one story: (a) wire `python-docx` into `.docx` branch of `local_file` handler (registry already promises it), (b) add image provider routed through sensory-bridges.
4. New G0 fidelity criteria for visual sources; new contract roles (`visual-primary`, `visual-supplementary`).
5. Transform registry becomes the binding contract — any format advertised must have a working extractor OR be marked `planned`.

### Step 4 — Open Story 26-Z (Texas CLI cp1252 guard) → one-line fix + test

**Unblocks:** `run_wrangler.py --help` runs cleanly on Windows without `PYTHONIOENCODING=utf-8`.

Tiny story — add the pattern we used in scaffold v0.2:
```python
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
```
Add one test asserting `--help` returns exit 0 on Windows with cp1252 default stdout (or that the guard is present).

### Step 5 — Open Story 26-W (Audra L1 docs-vs-code schema-lockstep check) → design + implement

**Unblocks:** future drift between docs (pack Run Constants, Texas transform-registry, other) and code (validators, runners) gets caught at L1 sweep rather than surfaced during trial execution.

New check class: `format-capability-lockstep`. Compiles schema claims from load-bearing docs, diffs against validator/runner schemas. Would have caught BOTH Step 2 (pack doc schema drift) AND Step 3 (Texas DOCX promise-vs-code drift) before they reached the trial.

### Step 6 — Restart the trial on a clean slate

**Pick-up conditions:** Steps 1-4 done; Step 5 optional. The fresh restart should breeze through the points that cost us time last session:

1. **Fresh branch from master** after merging the remediation commits. Branch name suggestion: `dev/trial-run-c1m1-tejal-20260418` or similar.
2. **Create fresh source bundle** `apc-c1m1-tejal-<YYYYMMDD>-motion/` — do NOT reuse `20260415` (has stale artifacts from this session's halted run — trial-run-c1m1-tejal-20260417.md runbook + Texas extracted.md etc. still live there). Fresh bundle directory gives a clean slate.
3. **Author `run-constants.yaml` using Step 2's corrected pack-doc** — canonical lowercase nested YAML. Expect `emit-preflight-receipt.py` to PASS first try.
4. **Issue the 4-Execution-Rules binding + Prompt 1** as a single consolidated message to Marcus (re-use the one logged in last session's runbook at `trial-run-c1m1-tejal-20260417.md` under "Catch-up message composed for Marcus"). Adjust only the bundle path.
5. **Texas source-wrangling** should now work cleanly including the DOCX cross-val (post-Step-3 remediation) AND the roadmap image (if Step 3's image provider landed).
6. **Proceed through Prompt 2+** — territory we never reached. This is where the real trial-production validation starts.

Estimated time to reach "back to where we halted": **~15 minutes** if Steps 1-4 complete cleanly. Previous attempt took ~2 hours largely due to surprise defects; now pre-mediated.

## Branch Metadata

- **Current branch (end of 2026-04-17 session):** `dev/epic-26-scaffold-v02` with 3 session commits (`a878b82`, `cdfad84`, `5e073cf`) + operator commit (`5ffc76b`) on top of handoff anchor `c9f8d1c`.
- **Repository baseline branch after closeout:** `master` (merge NOT performed this session — see "Git Closeout Exception" below).
- **Intended next working branch:** `dev/trial-run-c1m1-tejal-20260418` (or similar), branched from `master` after the remediation merge lands.

## Git Closeout Exception (2026-04-17)

**Merge-to-master was skipped this session** because `scripts/utilities/progress_map.py` carries an uncommitted mid-refactor (Juan-authored, not session work) that breaks 34 tests. Per Session WRAPUP Protocol Step 12: "Do not perform the merge-to-master flow when any of the following are true: unrelated pre-existing worktree changes remain."

**Resume path:** Step 1 above (remediate `progress_map.py`) → green pytest baseline → then merge `dev/epic-26-scaffold-v02` to `master` → branch `dev/trial-run-c1m1-tejal-20260418` from fresh `master`.

## Startup Commands

```powershell
# 1. Verify branch state
git status --short
git log --oneline -6

# 2. Run the session START protocol (Cora-orchestrated)
# Cora will re-read SESSION-HANDOFF.md + this file + git log since anchor
# and summarize what's ready to resume.

# 3. Before touching remediation, decide on progress_map.py
git diff scripts/utilities/progress_map.py
# → pick Option A (complete), B (revert), or C (park)

# 4. Once baseline is green, open Story 26-X (Paige tech-writer):
# pack-doc Run Constants schema repair
# Then 26-Y (Texas wrangler expansion, party-mode)
# Then 26-Z (Texas CLI cp1252 guard)
# Then 26-W (Audra docs-vs-code schema-lockstep check — optional)

# 5. Trial restart — fresh bundle, fresh branch
mkdir course-content\staging\tracked\source-bundles\apc-c1m1-tejal-20260418-motion
# Author run-constants.yaml from the (now-corrected) pack doc.
# Reuse the catch-up-message-to-Marcus from the prior runbook, adjust bundle path.
```

## Hot-Start Files

- [SESSION-HANDOFF.md](SESSION-HANDOFF.md) — backward-looking record of this session
- [_bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260417.md](_bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260417.md) — runbook with every trial action + halt point detail
- [_bmad-output/implementation-artifacts/texas-visual-source-gap-backlog.md](_bmad-output/implementation-artifacts/texas-visual-source-gap-backlog.md) — Step 3 source material
- [_bmad-output/implementation-artifacts/prompt-pack-v4-2-run-constants-schema-drift.md](_bmad-output/implementation-artifacts/prompt-pack-v4-2-run-constants-schema-drift.md) — Step 2 source material
- [_bmad-output/implementation-artifacts/26-5-bmb-scaffold-preservation.md](_bmad-output/implementation-artifacts/26-5-bmb-scaffold-preservation.md) — the one scaffold-v0.2-adjacent story still open in backlog; gates the batch-wave of ~14 remaining agent migrations
- [reports/dev-coherence/2026-04-17-1900/harmonization-summary.md](reports/dev-coherence/2026-04-17-1900/harmonization-summary.md) — pre-trial L1 CLEAN sweep (reuse as baseline unless something material changed since)
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` — the canonical pack (Step 2's target for line ~22-37 rewrite)

## Key Gotchas Discovered This Session

- **Pack-doc-vs-code drift** is a real defect class. Check for it in any load-bearing doc that displays YAML/config schemas. Audra gets a story for this (Step 5).
- **`_bmad/memory/` is fully gitignored** — re-scaffolded sanctums are local-only. Fresh clone won't have them until the scaffold runs. Not a blocker; just awareness.
- **Stale bundle gates** (`gate-01-result.yaml`, `gate-04-result.yaml` with FAIL verdicts) can linger across runs in a reused bundle directory. Always clear before a fresh run. Use a new `<YYYYMMDD>-motion` bundle dir to sidestep.
- **Marcus via Skill tool**: not registered in the default harness. Operator had to wait for Skill-tool-native load. Once loaded, performed correctly. Unknown whether this is fixable at the harness level or is by-design.
- **Coordination DB is canonical**; bundle + DB + pack must all agree on active run_id. A stale DB is confusing. Marcus flagged this at trial open and corrected it (cancelled 20260409, activated 20260415).

## Run HUD

```powershell
.venv\Scripts\python -m scripts.utilities.run_hud --open
```

Three tabs: System Health / Production Run / Dev Cycle. Auto-refreshes every 10 seconds.

**Caveat:** run_hud currently depends on `progress_map.py` which is in a broken-mid-refactor state. The HUD may not render correctly until Step 1 completes.

## Ambient Worktree State at Handoff

Expect these at session open — NOT this session's work:

- `scripts/utilities/progress_map.py` — uncommitted refactor, breaks 34 tests. See Step 1.

## Protocol Status

Follows the canonical BMAD session protocol pair ([bmad-session-protocol-session-START.md](bmad-session-protocol-session-START.md) / [bmad-session-protocol-session-WRAPUP.md](bmad-session-protocol-session-WRAPUP.md)).
