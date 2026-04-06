# Production Session Wrapup Protocol

Goal: close a production shift with explicit ownership, complete evidence, and no ambiguous run state.

Use this as the end-of-session production prompt paired with startup protocol.

## Invocation Contract (Session Close)

- Marcus is the only user-facing interface for this wrap-up flow.
- Specialist closures happen behind Marcus and must resolve baton ownership.
- Every active run must be closed to exactly one terminal state before shift close.
- The session must end with one completed Shift Close Record.

Run-setting reminder:
- Execution mode (`tracked/default` vs `ad-hoc`) and quality preset (`explore`/`draft`/`production`/`regulated`) are distinct settings and must both be represented in handoff context.

## 1. Run Closure Gate

For each active run, set exactly one state:

- completed
- blocked (reason + owner + next review time)
- handed off (recipient + acceptance confirmation)

For tracked/default mode:
- Verify the `production_runs` table in `state/runtime/` reflects the declared terminal state for each run.
- If any run's database state is inconsistent with the declared closure state, correct it before proceeding.

Fail condition:

- Any run remains implicit/in-progress at close.
- Any tracked run's database state does not match its declared closure state.

## 2. Baton and Delegation Closure Gate

Verify baton and delegated ownership are consistent.

Pass criteria:

- No specialist left without a known authority owner.
- No stage left in transient or unknown state.
- No unresolved handoff without an accepting owner.

## 3. Evidence and Logging Gate

Confirm evidence completeness for each run closed in this session:

Required evidence artifacts:
- `preflight-results.json`
- `operator-directives.md` (mandatory for tracked runs; confirms operator provided source-processing instructions or explicitly waived them)
- `ingestion-evidence.md`
- `literal-visual-operator-packet.md` (if literal-visual slides were present)
- Fidelity receipts (G0-G4, as applicable to stages completed)
- `gary-dispatch-validation-result.json` (if Gary dispatch occurred)
- `authorized-storyboard.json` (if Gate 2 storyboard approval occurred)
- `variant-selection.json` (if `DOUBLE_DISPATCH` was enabled)
- `motion-designations.json` and `motion_plan.yaml` (if `MOTION_ENABLED` was enabled)
- Pass 2 handoff validator output (if Irene Pass 2 occurred)
- post-Pass-2 storyboard evidence (if Storyboard B review occurred)
- Stage receipts per prompt

Additional evidence:
- Delegation events logged
- Completion/failure events logged
- Human checkpoint decisions recorded
- Artifact paths recorded

Fail condition:

- Any required evidence missing for a completed run.

## 4. Risk and Blocker Capture Gate

For each blocker/open risk, record:

- blocker or risk description
- owner
- next action
- expected review time

## 5. Next-Shift Handoff Gate

Create handoff with:

- completed outcomes
- blocked items and reasons
- first required next-shift action
- owner per open item
- environment constraints discovered
- execution mode + quality preset for each still-open run
- operator directives summary (were directives provided? any special treatment still in effect for continuing runs?)
- storyboard approvals summary (Gate 2 storyboard and post-Pass-2 storyboard, when applicable)
- motion workflow summary (`MOTION_ENABLED`, Gate 2M status, Motion Gate status, if applicable)

## 6. Workspace Hygiene Gate

Run:

- `git status --short`
- `git worktree list`
- `python -m scripts.utilities.structural_walk --workflow standard`
- if the run used motion: `python -m scripts.utilities.structural_walk --workflow motion`

Pass criteria:

- No accidental local code edits in production session context.
- No unintended temporary worktrees left registered.
- Structural walk report saved under `reports/structural-walk/` using the canonical scripted generator (not ad hoc text generation).

If stale metadata appears, run:

- `git worktree prune --verbose`

## 7. Close Decision and Escalation Routing

Decision options:

- Normal close: all gates pass
- Controlled close: open risks documented with owners
- Emergency handoff: incident active or unsafe state

If close cannot be safely completed:

- Route to incident workflow: `docs/workflow/production-incident-runbook.md`
- Route planned remediation to change workflow: `docs/workflow/production-change-window.md`

## Required Output (Strict)

At completion, output one and only one Shift Close Record using this structure:

```md
# Production Shift Close

- Operator:
- End (local):
- End (UTC):

## Active Settings (echo from Shift Open)
- Execution mode: tracked | ad-hoc
- Quality preset: explore | draft | production | regulated

## Gate Results
- Run Closure: pass | fail
- Baton/Delegation Closure: pass | fail
- Evidence/Logging Completeness: pass | fail
- Risk/Blocker Capture: pass | fail
- Next-Shift Handoff: pass | fail
- Workspace Hygiene: pass | fail

## Run Outcomes
- Completed:
- Blocked:
- Handed off:

## Evidence Summary
- Operator directives recorded: yes | no | n/a (ad-hoc)
- Fidelity receipts complete: yes | no
- Validator outputs archived: yes | no

## Open Risks
- Risk:
- Owner:
- Next action:

## Close Decision
- Mode: normal | controlled | emergency-handoff
- Escalation route used (if any): incident | change-window | none
- Next shift first action:
```
