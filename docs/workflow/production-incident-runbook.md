# Production Incident Runbook

Goal: **contain** production risk quickly, **preserve evidence**, and **restore safe operation** with clear ownership—then exit via verification and a single incident record.

**Role in the suite:** Use this flow for **unplanned** disruption: outages, broken gates, corrupted run/baton state, missing critical artifacts, or authority/delegation breaches. Escalated from `production-session-start.md` / `production-session-wrapup.md` when gates fail or close cannot complete safely. **Do not** use this for scheduled upgrades—use `docs/workflow/production-change-window.md`.

**Related prompts:** `production-session-launcher.md` (escalation route #1) · `production-session-start.md` · `production-session-wrapup.md`

---

## Copy/Paste Prompt (Marcus executes this protocol)

Use when declaring an **active incident** in chat:

```
You are Marcus. Execute docs/workflow/production-incident-runbook.md in full, gate by gate.
This is an INCIDENT: prioritize containment and evidence over forward progress.
Do not start new production run stages on affected runs until containment is explicit.
At completion, output exactly one completed Incident Record using the template in that file, then stop and wait for my instruction.
If the fix requires a planned remediation window after containment, say so and point to docs/workflow/production-change-window.md—do not conflate incident response with the change window protocol in the same record.
```

---

## Invocation Contract (Incident)

- **Marcus** is the coordinating interface; specialists are invoked **only** for narrowly scoped diagnosis or recovery steps Marcus delegates.
- **Fail closed** on resume: do not return to “normal” execution until **Verification Before Resume** passes.
- One **Incident ID** per distinct event; if scope splits, open a linked sub-incident or new ID with reference.
- End with **exactly one** completed **Incident Record** per invocation cycle (update same record on subsequent chat turns if the incident spans sessions).

## Preconditions

- A **trigger** below matches (or operator explicitly declares incident).
- Operator can **pause** affected runs (no silent continuation).

## Incident Triggers

Open an incident when any of the following occurs:

- External API outage or severe degradation affecting active runs
- Failed quality/fidelity gate with **publish** or **integrity** risk
- Corrupted or ambiguous run/baton state
- Missing critical artifact for an **active** run stage
- Incorrect delegation pathing or **authority breach** relative to `delegation-protocol.md` / specialist registry

## Severity Levels

- **SEV-1:** Active publish risk or data integrity risk; immediate containment
- **SEV-2:** Production flow blocked for one or more runs
- **SEV-3:** Degraded behavior with documented workaround

## 1. Immediate Containment Gate

Within the first response window:

- **Pause** affected run progression (document run IDs).
- **Prevent** new dispatches for affected stages.
- **Preserve** current run state, logs, and artifact paths (do not destructive cleanup).
- **Notify** operator channel (or session) with severity + run IDs + incident commander.

**Pass:** Containment explicit; no ambiguous “still running” state on affected work.

## 2. Incident Record Gate

Create or update the incident record with:

- **Incident ID**
- **Start** (local + UTC)
- **Severity**
- **Affected runs**
- **Reporter**
- **Incident commander** (single owner)

**Pass:** Record exists before deep remediation proceeds.

## 3. Diagnostic Triage Gate

Collect:

- Last known **successful** stage
- First **failing** action and timestamp
- **External dependency** status (API/MCP)
- **Baton/delegation** state snapshot (paths, not secrets)
- Relevant **log excerpts** and **artifact paths**

**Pass:** Triage written; no hand-wavy “unknown failure.”

## 4. Recovery Decision Gate

Choose **one path per affected run** (document each):

- Retry same stage
- Reroute to alternate specialist path
- Skip stage with **explicit human approval** (record approver)
- Stop run pending external recovery

Every decision records:

- **Owner**
- **Rationale**
- **Expected next checkpoint**

## 5. Verification Before Resume Gate

Before declaring “normal” or closing the shift:

- Failing condition **resolved** or **safely bypassed** with approval
- Smallest relevant **preflight** re-run: pass
- **Quality gate** requirements still enforceable
- **Authority chain** and **baton** state coherent

**Fail:** Remain in incident or controlled close per `production-session-wrapup.md` (emergency-handoff).

## 6. Closure and Follow-up Gate

At incident close:

- Mark **resolved** | **handed off** | **monitoring**
- **Root cause category** (external | config | code | process | operator error | unknown)
- **Prevention actions** with owners/dates
- If permanent fix needs a **planned** change, open **`production-change-window.md`** as a separate tracked window

## Required Output (Strict)

Output **one** Incident Record (new or updated) using:

```md
# Incident Record

- Incident ID:
- Severity: SEV-1 | SEV-2 | SEV-3
- Start (local):
- Start (UTC):
- Reporter:
- Commander:
- Affected runs:

## Gate Results
- Containment: pass | fail
- Record Established: pass | fail
- Diagnostic Triage: pass | fail
- Recovery Decision: pass | fail
- Verification Before Resume: pass | fail | n/a
- Closure: pass | fail | open

## Symptoms
-

## Containment Actions
-

## Recovery Decision
- Path chosen (per run):
- Owner:
- Rationale:
- Next checkpoint:

## Verification
- Preflight rerun: pass | fail | n/a
- Quality gate posture: pass | fail | n/a
- Baton/delegation coherence: pass | fail | n/a

## Closure
- End (local):
- End (UTC):
- Status: resolved | handed-off | monitoring
- Root cause category:
- Prevention actions (owner / due):
- Follow-on change window ID (if any):
```

## Notes

- **Launcher recall:** `production-session-launcher.md` routes failures to **incident** (this file) vs **change-window** (planned). Keep that distinction in every Marcus response during dual-track work.
- After SEV-1 containment, prefer **Shift Close** with `emergency-handoff` in `production-session-wrapup.md` if the operator cannot safely continue the same chat session.
