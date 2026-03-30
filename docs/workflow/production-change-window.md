# Production Change Window Protocol

Goal: apply **planned** production changes safely—routing, governance, runbooks, skills, scripts, or deployment behavior—with rollback readiness, explicit approval, and a single auditable record.

**Role in the suite:** Use this flow when startup or wrapup escalates to **planned remediation**, or when you intentionally schedule a change. Pair with `docs/workflow/production-session-launcher.md` (escalation route #2) and **not** with break-glass incident response unless an incident forces a change.

**Related prompts:** `production-session-start.md` (Shift Open) · `production-session-wrapup.md` (Shift Close) · `production-incident-runbook.md` (unplanned disruption)

---

## Copy/Paste Prompt (Marcus executes this protocol)

Use when opening a **declared change window** in chat (paste as one message, then answer Marcus’s checkpoints):

```
You are Marcus. Execute docs/workflow/production-change-window.md in full, gate by gate.
This is a PLANNED change window, not an incident. Fail closed if pre-change or verification gates fail.
Do not merge unrelated production work into this window.
At completion, output exactly one completed Change Window Record using the template in that file, then stop and wait for my instruction.
```

---

## Invocation Contract (Change Window)

- **Marcus** is the only user-facing interface for this flow unless a human explicitly engages a specialist for a scoped technical task Marcus delegates.
- No ad-hoc production mutations outside a **declared** change window (Change ID + owner + scope + rollback point).
- If any **critical** gate fails, **stop execution** and either roll back or hold until the blocker is cleared—do not “finish anyway.”
- The session that executes this protocol must end with **one** completed **Change Window Record**.

## Preconditions

- Change is **scheduled** or explicitly approved (not silent edits during a content run).
- Incident response is **not** the primary path (if this is reactive break-glass, use `production-incident-runbook.md` first, then optionally open a change window for the fix).

## 1. Change Window Declaration Gate

Record and confirm:

- **Change ID** (unique, traceable)
- **Owner** (single accountable human)
- **Scope** (files, skills, scripts, config, docs—explicit list)
- **Start/end window** (local + UTC)
- **Risk level** (low | medium | high)
- **Rollback owner** (must differ from implementer if risk is high—otherwise document same)

**Pass:** All fields set and acknowledged by operator.

## 2. Pre-Change Gate

Before any mutation:

- **Workspace / branch** — same checks as Shift Open integrity: `git rev-parse --show-toplevel`, `git branch --show-current`, `git status --short`, `git worktree list`
- **Baseline tests** — targeted suite green for scope (name the commands run)
- **Rollback point** — commit hash or tag recorded
- **Stakeholders** — who was notified (or “N/A” with rationale)

**Fail:** Do not apply changes. Route to incident runbook if production is unsafe.

## 3. Execution Controls Gate

During the window:

- Apply **only** scoped changes; no drive-by edits.
- Keep commits **small** and attributable (one logical change per commit where possible).
- Record **checkpoint decisions** (what changed, why, when).

If unexpected behavior appears: **stop** and evaluate **rollback** immediately.

## 4. Verification Gate

After changes:

- Run **targeted** automated tests (list commands + result)
- Run **production preflight** (same family as Shift Open dependency gate)
- **Validate** affected runbook/session behavior (e.g. re-read `production-session-start.md` / `wrapup` paths if those files changed)
- **Side-effect review** — unrelated workflows still coherent

**Fail:** Roll back to declared rollback point unless operator explicitly accepts documented residual risk (record in record).

## 5. Rollback Decision Gate

If verification fails or risk is unacceptable:

- Execute rollback to declared rollback point
- Verify known-good state (preflight + spot check)
- Record rollback reason and follow-up work item

## 6. Change Closure Gate

At end of window:

- Declare **success** | **rollback** | **partial** (partial requires explicit follow-up Change ID or incident)
- Update **operational docs** if behavior changed (pointer to PR or doc commits)
- List **open follow-ups** with owner and target date

## Required Output (Strict)

Output **one and only one** Change Window Record:

```md
# Change Window Record

- Change ID:
- Owner:
- Start (local):
- Start (UTC):
- End (local):
- End (UTC):
- Scope:
- Risk level:
- Rollback point (commit/tag):

## Gate Results
- Declaration: pass | fail
- Pre-Change: pass | fail
- Execution Controls: pass | fail
- Verification: pass | fail
- Rollback Decision: pass | fail | n/a
- Closure: pass | fail

## Pre-Change Gate
- Branch/workspace verified: yes | no
- Baseline tests green: yes | no
- Stakeholders informed: yes | no

## Execution Log
- Step 1:
- Step 2:

## Verification
- Targeted tests: pass | fail
- Preflight checks: pass | fail
- Runbook/session behavior: pass | fail
- Side-effect review: pass | fail

## Outcome
- Result: success | rollback | partial
- Escalation route used (if any): incident | none
- Follow-up actions (owner / due):
```

## Notes

- After a successful window, the next **production session** should still begin with `production-session-launcher.md` → `production-session-start.md` to prove governance and preflight on the new baseline.
- If a change window **introduces** a defect discovered in operation, open **`production-incident-runbook.md`** for containment before mixing further planned edits.
