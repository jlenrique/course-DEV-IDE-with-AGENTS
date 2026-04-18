# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> **Current objective:** Begin implementation of the newly-ratified Epic 27 + Epic 28. Story 27-1 (DOCX drift fix) is the cheapest, highest-severity work and unblocks the pending Tejal trial restart.

## Immediate Next Action (pick-up point)

**Run BMAD Session Protocol Session START**, then pivot directly into Story 27-1 implementation via `bmad-create-story` → `bmad-dev-story`.

Session START will: load Cora for a since-handoff harmonization check (tripwire promotes this to **full-repo** scope because last session's 0a was deferred), verify branch state, and summarize what's changed since the handoff anchor.

## Hot-Start Summary

Last session ratified **two new epics** via party-mode consensus and merged them to master:

- **Epic 27 — Texas Intake Surface Expansion** (7 stories, 23 pts): DOCX drift fix + scite.ai + image + YouTube + Notion MCP + Box + Playwright MCP providers. Technician-capability upgrade.
- **Epic 28 — Tracy the Detective** (2 pilot stories + 2 v2 stubs, 12 pts): new production-tier research-specialist born-sanctum, partners with Texas, dispatched by Irene via Marcus, pilot provider scite.ai.

Critical path: **27-1 → 27-2 → 28-1 → 28-2**. Fan-out 27-3/4/5/6/7 parallel after 27-2 merges.

Master now at `90f19eb` (merge commit). Previous branch `dev/epic-26-pretrial-prep` preserved in origin for historical traceability.

## Sequenced Implementation Plan for This Session

### Step 1 — Harmonization sweep (full-repo scope, tripwire-promoted)

`/harmonize` full-repo. Expected L1 findings: 377 ruff errors repo-wide (pre-existing warehouse debt, documented in last session's handoff). Session-owned files from last commit are clean. Acknowledge and proceed — this is cleared incrementally per the 26-7 commit's "clearing the warehouse as we go" philosophy.

### Step 2 — Cut new working branch for Epic 27 implementation

```bash
git checkout master
git pull origin master
git checkout -b dev/epic-27-texas-intake
git push -u origin dev/epic-27-texas-intake
```

Per John Round-3 branch hygiene: implementation opens per-epic branches, NOT layered on the merged `dev/epic-26-pretrial-prep`.

### Step 3 — Story 27-1 — DOCX provider wiring (cheapest, highest-severity)

**Unblocks:** the halted APC C1-M1 Tejal trial restart (DOCX cross-validation was the failure mode at halt).

Spec: [_bmad-output/implementation-artifacts/27-1-docx-provider-wiring.md](_bmad-output/implementation-artifacts/27-1-docx-provider-wiring.md) — 2 pts, 7 ACs, file-impact enumerated.

Flow per BMAD sprint run charter:
1. `bmad-create-story 27-1` — expand ratified-stub spec into full implementation-ready story.
2. `bmad-party-mode` green-light (Winston + Amelia + Murat + Paige; operator invokes).
3. `bmad-dev-story 27-1` — execute.
4. `bmad-party-mode` implementation review (Winston + Amelia + Murat).
5. `bmad-code-review` (Blind Hunter + Edge Case Hunter + Acceptance Auditor).
6. Remediate MUST-FIX. Close story in sprint-status.yaml.

### Step 4 — Story 27-2 — scite.ai provider

**Blocks:** Epic 28's Tracy pilot.

Spec: [_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md](_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md) — 5 pts, 9 ACs, introduces `--tracy-approved-resources` flag + `source_origin` tag + atomic-write hygiene.

Prereq: scite.ai API token. Store in local `.env` (see `.env.example` after T1 lands). No API token → story scaffolds but tests mark `xfail` until token available.

### Step 5 — Merge 27-1 + 27-2 to master, then cut Epic 28 branch

After both 27-1 and 27-2 close `done`:

```bash
# Close 27-1 + 27-2 on dev/epic-27-texas-intake branch
git checkout master
git merge --no-ff dev/epic-27-texas-intake
git push origin master

# Cut Epic 28 branch
git checkout -b dev/epic-28-tracy-pilot
git push -u origin dev/epic-28-tracy-pilot
```

### Step 6 — Story 28-1 — Tracy pilot (scite.ai end-to-end)

Spec: [_bmad-output/implementation-artifacts/28-1-tracy-pilot-scite-ai.md](_bmad-output/implementation-artifacts/28-1-tracy-pilot-scite-ai.md) — 9 pts, 12 ACs.

**Pre-read before starting:**
- [_bmad-output/implementation-artifacts/epic-28-tracy-detective.md](_bmad-output/implementation-artifacts/epic-28-tracy-detective.md) — epic context + Tracy's identity
- [_bmad-output/implementation-artifacts/epic-28/_shared/ac-spine.md](_bmad-output/implementation-artifacts/epic-28/_shared/ac-spine.md) — 8 cross-cutting ACs
- [_bmad-output/implementation-artifacts/epic-28/_shared/runbook.md](_bmad-output/implementation-artifacts/epic-28/_shared/runbook.md) — 14-step dispatch procedure
- [skills/bmad-agent-tracy/references/vocabulary.yaml](skills/bmad-agent-tracy/references/vocabulary.yaml) — SSOT for intent_class, authority_tier, fit_score, editorial_note, provider_metadata.scite

Tracy is born-sanctum: no migration story, scaffold via `scripts/bmb_agent_migration/init_sanctum.py` v0.2.

### Step 7 — Story 28-2 — Gate family + regression hardening

Spec: [_bmad-output/implementation-artifacts/28-2-tracy-gate-hardening.md](_bmad-output/implementation-artifacts/28-2-tracy-gate-hardening.md) — 3 pts, stub (expand via `bmad-create-story`).

### Step 8 — Trial restart (APC C1-M1 Tejal) on fresh branch

After 27-1 merges (minimum) or after 27-2 + Tracy pilot closes (preferred for full robustness):

```bash
git checkout master
git pull origin master
git checkout -b dev/trial-run-c1m1-tejal-<YYYYMMDD>
# Follow fresh-bundle trial-restart flow in SESSION-HANDOFF.md (prior sessions)
```

## Branch Metadata

- **Repository baseline branch after closeout:** `master` at `90f19eb` (Epic 27+28 ratified + prior wave merged)
- **Next working branch:** `dev/epic-27-texas-intake` (cut from master as Step 2 above)
- **Epic 28 working branch:** `dev/epic-28-tracy-pilot` (cut from master after 27-1 + 27-2 merge)
- **Preserved reference branch:** `dev/epic-26-pretrial-prep` (pushed to origin; kept for historical reference)
- **Merge strategy:** `--no-ff` per Epic 26 + Epic 27/28 pattern

## Startup Commands

```bash
# 1. Verify branch state + pull latest master
git checkout master
git pull origin master
git log --oneline -6

# 2. Run the session START protocol (Cora-orchestrated)
# Cora will run full-repo harmonization (tripwire-promoted due to deferred 0a last session).

# 3. Cut the next working branch
git checkout -b dev/epic-27-texas-intake
git push -u origin dev/epic-27-texas-intake

# 4. Begin Story 27-1 via bmad-create-story
# (Expand ratified-stub spec into full story, then party-mode green-light, then bmad-dev-story.)

# 5. Run HUD sanity check (shows Epic 27+28 now with proper labels per last session's progress_map hardening)
.venv\Scripts\python -m scripts.utilities.run_hud --open
```

## Hot-Start Files

- [SESSION-HANDOFF.md](SESSION-HANDOFF.md) — backward-looking record of the 2026-04-17 Epic 27+28 ratification session
- [_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md](_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md) — Epic 27 artifact (story roster, AC spine, risk register, party-consensus record)
- [_bmad-output/implementation-artifacts/epic-28-tracy-detective.md](_bmad-output/implementation-artifacts/epic-28-tracy-detective.md) — Epic 28 artifact (Tracy identity, dependency graph, v2 backlog capture)
- [_bmad-output/implementation-artifacts/epic-28/_shared/](_bmad-output/implementation-artifacts/epic-28/_shared/) — shared spine (ac-spine, runbook, worksheet-template)
- [_bmad-output/implementation-artifacts/27-1-docx-provider-wiring.md](_bmad-output/implementation-artifacts/27-1-docx-provider-wiring.md) — full spec for the first implementation story
- [_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md](_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md) — full spec for the Epic 28-blocker
- [_bmad-output/implementation-artifacts/28-1-tracy-pilot-scite-ai.md](_bmad-output/implementation-artifacts/28-1-tracy-pilot-scite-ai.md) — full spec for Tracy's birth
- [skills/bmad-agent-tracy/references/vocabulary.yaml](skills/bmad-agent-tracy/references/vocabulary.yaml) — SSOT for Tracy's controlled vocabulary

## Key Risks / Unresolved Issues

1. **Repo-wide ruff debt (377 errors, 77 auto-fixable).** Pre-existing warehouse clutter. Not a blocker. Strategy: clear incrementally as stories touch affected files. No cleanup-only story opened.

2. **Tejal trial restart still pending.** Unblocked once 27-1 merges (minimum). Full robustness pending 27-2 if scite.ai referenced in the trial's source brief.

3. **Story 26-5 (scaffold preservation semantics)** remains backlog. Gates the batch migration wave of the remaining ~14 sidecar-pattern agents. Not blocking Epic 27/28 (Tracy is born-sanctum).

4. **Tracy v1 scoring rubric is naive by design.** Expected post-pilot iteration. First run is evidence-gathering, not rubric validation (John Round-3 flag captured as 28-1 AC).

5. **Deferred Cora harmonization** from last session's 0a → **auto-promoted to full-repo scope** for this session per wrapup-protocol tripwire. Budget 5-10 minutes extra at session start.

6. **Dr. Quinn's v2 concerns** (coherence drift, Loop B supply-creates-demand, Loop C vocabulary capture, Loop D rubber-stamping) are backlog-stubbed and cited in Epic 28 risk register. Post-pilot retrospective owns re-litigation.

## Key Gotchas Discovered This Session

- **Dispatch-vs-artifact is a load-bearing distinction.** For any specialist pair (Tracy↔Texas, Irene↔Gary, future...), runtime dispatch goes through Marcus; artifact handoff travels via filesystem with atomic writes. Codified as Epic 28 AC-S1; apply universally.
- **Doc-contract before implementation.** Paige's discipline: author the SSOT vocabulary file (e.g., `vocabulary.yaml`) at ratification time so implementation can't drift from a non-existent contract.
- **Ratification vs implementation is a hard boundary.** Last session shipped epics + story specs + shared spine + ONE doc-contract artifact. Code implementation deferred. This matches Epic 26's pattern and prevents scope creep.
- **Pre-commit hooks clean debt as you go.** 77 ruff auto-fixes landed in-flight on `progress_map.py` during the session's commit. Follow this for every story that touches a warehouse-debt file.
- **ratified-stub is a recognized status.** Last session added it to `READY_STATUSES` in `progress_map.py`. Use it for stories that are party-ratified with AC spine but not yet full-speced.

## Run HUD

```bash
.venv\Scripts\python -m scripts.utilities.run_hud --open
```

Three tabs: System Health / Production Run / Dev Cycle. Auto-refreshes every 10 seconds. After last session's progress_map hardening, the HUD will correctly show Epic 27 ("Texas Intake Surface Expansion") and Epic 28 ("Tracy the Detective") with proper labels and 0/7 + 0/4 progress bars.

## Ambient Worktree State at Handoff

**Clean.** `git status --short` = empty. No uncommitted work, no untracked files outside gitignored areas.

## Protocol Status

Follows the canonical BMAD session protocol pair ([bmad-session-protocol-session-START.md](bmad-session-protocol-session-START.md) / [bmad-session-protocol-session-WRAPUP.md](bmad-session-protocol-session-WRAPUP.md)).
