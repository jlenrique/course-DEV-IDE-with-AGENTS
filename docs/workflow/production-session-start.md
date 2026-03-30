# Production Session Startup Protocol

Goal: open a production shift with explicit authority, verified readiness, and a safe first action.

Use this as the first-session startup prompt when operating the app for real course-content production.

## Invocation Contract (First Session)

- Marcus is the only user-facing interface for this startup flow.
- Specialist work is delegated behind Marcus per registry and baton rules.
- If any critical gate fails, fail closed: do not start or resume production run execution.
- The session must end this protocol with a single completed Shift Open Record.
- Use two run-setting axes explicitly:
	- Execution mode: `tracked` (alias `default`) or `ad-hoc`
	- Quality preset: `explore`, `draft`, `production`, or `regulated`

Terminology note:
- "Production session" here means real APP operations (not APP development).
- "Production preset" means the quality strictness level on the preset axis.

## Preconditions

- You are opening the intended production workspace path.
- You are on the intended production branch/tag for this shift.
- You have authority to operate active runs.

## 1. Shift Open Declaration

Record:

- Operator name
- Start timestamp (local + UTC)
- Session purpose
- Planned duration

## 1a. Run Settings Alignment Gate

Declare and confirm both settings before any run execution:

- Execution mode (`tracked/default` or `ad-hoc`)
- Quality preset (`explore`/`draft`/`production`/`regulated`)

Pass criteria:

- Settings are explicitly stated and unambiguous.
- Operator intent is clear: production operations context vs app-development context.

## 2. Workspace and Branch Integrity Gate

Run:

- `git rev-parse --show-toplevel`
- `git branch --show-current`
- `git status --short`
- `git worktree list`

Pass criteria:

- Correct workspace path.
- Correct branch/tag.
- No unplanned local code changes.
- No unexpected extra worktrees.

If stale metadata appears, run:

- `git worktree prune --verbose`

## 3. Runtime and Governance Gate

Verify these references are current and readable:

- `skills/production-coordination/references/delegation-protocol.md`
- `skills/production-coordination/references/baton-lifecycle.md`
- `skills/bmad-agent-marcus/references/specialist-registry.yaml`

Pass criteria:

- Delegation pathing is registry-based.
- Baton ownership rules are unambiguous.
- Specialist registry entries map to existing `SKILL.md` files.

## 4. Dependency Preflight Gate

Run the production preflight skill/commands.

Minimum checks:

- Required MCP servers reachable.
- Required third-party APIs reachable.
- Credential keys present (do not print secrets).
- Required runtime paths writable.

## 5. Active Run Recovery Gate

Review current run state:

- Active runs
- Blocked runs
- Pending human checkpoints
- Orphaned stages

Pass criteria:

- Every active run has a clear owner.
- Every blocked run has a known blocker reason and next action.

## 6. Quality Gate Posture

Confirm quality controls are active:

- Human-in-the-loop controls: `docs/workflow/human-in-the-loop.md`
- Agent QA gate policy: `docs/workflow/agent-qa-release-gate.md`

For this shift, define:

- Mandatory checkpoints before publish
- Outputs that require explicit sign-off

## 7. Decision and Escalation Routing

Decision options:

- Full: proceed with first queued production action
- Limited: proceed under documented constraints
- Hold: do not execute runs until blocker is cleared

If any critical gate fails:

- Do not start run execution.
- Route to the correct control flow:
	- Incident path: `docs/workflow/production-incident-runbook.md`
	- Planned remediating change path: `docs/workflow/production-change-window.md`

## Required Output (Strict)

At completion, output one and only one Shift Open Record using this structure:

```md
# Production Shift Open

- Operator:
- Start (local):
- Start (UTC):
- Workspace path:
- Branch/tag:
- Session objective:

## Gate Results
- Run Settings Alignment: pass | fail
- Workspace/Branch Integrity: pass | fail
- Runtime/Governance: pass | fail
- Dependency Preflight: pass | fail
- Active Run Recovery: pass | fail
- Quality Gate Posture: pass | fail

## Active Settings
- Execution mode: tracked | ad-hoc
- Quality preset: explore | draft | production | regulated

## Blocking Issues
- Issue:
- Owner:
- Next action:

## Decision
- Mode: full | limited | hold
- First approved action:
- Escalation route used (if any): incident | change-window | none
```
