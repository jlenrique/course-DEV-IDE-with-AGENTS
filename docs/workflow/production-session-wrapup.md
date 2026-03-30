# Production Session Wrapup Protocol

Goal: close a production shift with explicit ownership, complete evidence, and no ambiguous run state.

Use this as the end-of-session production prompt paired with startup protocol.

## Invocation Contract (Session Close)

- Marcus is the only user-facing interface for this wrap-up flow.
- Specialist closures happen behind Marcus and must resolve baton ownership.
- Every active run must be closed to exactly one terminal state before shift close.
- The session must end with one completed Shift Close Record.

## 1. Run Closure Gate

For each active run, set exactly one state:

- completed
- blocked (reason + owner + next review time)
- handed off (recipient + acceptance confirmation)

Fail condition:

- Any run remains implicit/in-progress at close.

## 2. Baton and Delegation Closure Gate

Verify baton and delegated ownership are consistent.

Pass criteria:

- No specialist left without a known authority owner.
- No stage left in transient or unknown state.
- No unresolved handoff without an accepting owner.

## 3. Evidence and Logging Gate

Confirm evidence completeness:

- Delegation events logged
- Completion/failure events logged
- Human checkpoint decisions recorded
- Artifact paths recorded

Fail condition:

- Any required evidence missing.

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

## 6. Workspace Hygiene Gate

Run:

- `git status --short`
- `git worktree list`

Pass criteria:

- No accidental local code edits in production session context.
- No unintended temporary worktrees left registered.

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

## Open Risks
- Risk:
- Owner:
- Next action:

## Close Decision
- Mode: normal | controlled | emergency-handoff
- Escalation route used (if any): incident | change-window | none
- Next shift first action:
```
