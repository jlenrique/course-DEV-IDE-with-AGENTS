# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> **Current objective:** Fire first tracked trial production run (Marcus-the-APP) against the Epic 33 clean baseline.
>
> **Trial branch:** `trial/2026-04-19` @ commit `8b70076`. Both sessions (Marcus window + dev-support window) operate on this branch. Verify with `git branch --show-current` before any work begins. Working tree MUST be clean at every session handoff.
>
> **Deferred inventory status (2026-04-19):** 4 backlog epics (15, 16, 17, 18) / 4 deferred stories in active epics (20c-4, 20c-5, 20c-6, 20a-5) / 7 named-but-not-filed follow-ons. See [`_bmad-output/planning-artifacts/deferred-inventory.md`](_bmad-output/planning-artifacts/deferred-inventory.md). Binding consultation per [CLAUDE.md §Deferred inventory governance](CLAUDE.md).

## Immediate Next Action — Trial Production Run

1. Run the BMAD Session Protocol Session START.
2. **Confirm branch: `trial/2026-04-19`** — `git branch --show-current` must return `trial/2026-04-19`. If not, run `git checkout trial/2026-04-19`.
3. Confirm working tree is clean: `git status --short` should show only `?? .coverage` (benign pytest artifact). No other untracked or modified files.
4. Say **"Marcus, run preflight"** → Marcus executes PR-PF against the trial-branch environment.
5. Say **"Marcus, author the run constants for this bundle"** → Marcus executes PR-RC. Will ask (in plain language): SME source / visuals-or-text-lead / motion-enabled / double-dispatch.
6. Operator GO on Prompt 1 once preflight + run constants are confirmed green.

## Trial Session Discipline

**Fix-in-flight (when something breaks mid-trial):**
- Operator announces: *"Marcus, fix-in-flight."*
- Marcus records the pause-hash and the affected gate/step.
- Dev-support-agent (other IDE window, same branch) commits the fix to `trial/2026-04-19` directly.
- Operator returns to Marcus window: *"Marcus, resume trial."*
- Marcus diffs since the pause-hash, classifies Green/Yellow/Red, reports before resuming.

**Exploration (curiosity / "what if" questions):**
- Operator announces: *"Marcus, pause trial, switch to ad-hoc."*
- Marcus flips `state/runtime/mode_state.json` to `ad-hoc`; exploration happens in `state/runtime/ad-hoc-runs/`.
- Operator announces: *"Marcus, resume trial."* → Marcus flips back to tracked; exploration is quarantined.

**Clean-working-tree invariant:** before any session handoff (Marcus to dev-support or vice versa), `git status --short` must be clean. Both agents commit + push before switching windows.

## Repo State

- **Epic 33 Pipeline Lockstep Substrate:** ALL 6 stories BMAD-closed (33-1 / 33-2 / 33-1a / 33-3 / 33-4 / 15-1-lite-marcus). META-TEST PASS captured — Cora's block-mode hook fired on real intermediate drift; substrate proven load-bearing.
- **Lesson Planner MVP:** all 22 planned stories BMAD-closed + 32-2a. F4 ratification: GREEN/YELLOW (proceed with trial).
- **master** at `2ba1e32` (feat(epic-33): close Pipeline Lockstep Substrate sprint end-to-end). Pushed to origin.
- **trial/2026-04-19** at `8b70076` (chore(trial): pin trial/2026-04-19 branch context). Pushed to origin.
- **No outstanding regressions** — full suite: 1910 passed / 4 skipped / 27 deselected / 2 xfailed / 0 failed.
- **Epic 33 retrospective** — status `required` in sprint-status.yaml; authored at `_bmad-output/implementation-artifacts/epic-33-retro-2026-04-19.md`; NOT yet party-mode reviewed. Can run after trial; not a trial blocker.

## Outstanding Items (next session must surface at Start Step 1a)

1. **Step 0a harmonization skipped** — no formal Audra sweep run this session (Cora was off-manifest participant in party rounds, not invoked as a live skill). Next session's start protocol tripwire will auto-promote /harmonize to full-repo scope. Run `/harmonize` at session open if time permits before trial kickoff; or defer to post-trial.

2. **Epic 33 retrospective** — required per [epics.md §Epic 33 Closure Criteria](_bmad-output/planning-artifacts/epics.md). Party-mode round post-trial: assess FM-A/FM-B/FM-C closure, evaluate META-TEST PASS legitimacy, flag reactivation candidates from `deferred-inventory.md`. Expected candidates: 15-1-lite-irene / 15-1-lite-gary, 26-10 (PR-TR + health-check capabilities), v4.3 substrate trigger.

3. **TALK/marcus-live branch** — off-books live-voice experiments; committed + pushed to `origin/TALK/marcus-live`; NOT merged into master. Trial branch (`trial/2026-04-19`) is clean of TALK commits. If voice-related side-effects surface during trial, revert-ready.

## Startup Commands

```bash
# Verify clean trial baseline before starting session
git branch --show-current          # must be: trial/2026-04-19
git status --short                  # expect: ?? .coverage only
git log --oneline -3                # expect: 8b70076 / 2ba1e32 / 4911fc4

# Optional pre-trial regression smoke
python -m pytest -q --tb=no 2>&1 | tail -5   # expect: 1910 passed, 0 failed
```

## Notes

- Trial-branch-discipline parked as Story PR-TR in [`_bmad-output/planning-artifacts/deferred-inventory.md`](_bmad-output/planning-artifacts/deferred-inventory.md) — scope it after trial #1 generates evidence.
- Pipeline lockstep regime operational cheatsheet: [`docs/dev-guide/pipeline-manifest-regime.md`](docs/dev-guide/pipeline-manifest-regime.md) — T1 required reading for any future pipeline-touching story.
- Any future pipeline edit flows through `state/config/pipeline-manifest.yaml` (manifest → regenerate → commit), not through direct pack or HUD edits.
- Marcus-the-agent CREED has a new standing order: any time he reports sprint state, he re-reads the authoritative file fresh. He does NOT narrate from prior-turn context.
