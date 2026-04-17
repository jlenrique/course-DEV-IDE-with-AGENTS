# Harmonization Protocol (HZ)

Cora's on-demand doc-harmonization sweep. Invoked by operator `/harmonize` or `/coherence-check`, by the canonical BMAD Wrapup as **Step 0a** (pre-wrapup coherence sweep), or on Marcus-route when the HIL asks Marcus for a coherence check mid-run.

This protocol is a six-gap-closed evolution of `maintenance/doc review prompt 2026-04-12.txt`. Gaps closed:

1. Structural walk invocation (was: implicit)
2. Wall-clock change window anchored to SESSION-HANDOFF commit (was: vague "recent")
3. Explicit L1-contract sync check (was: absent)
4. Lane-matrix coverage check (was: absent)
5. Hot-start-pair freshness check (was: absent)
6. Fixed report-home under `reports/dev-coherence/YYYY-MM-DD-HHMM/` (was: ad-hoc)

## Steps

1. **Tripwire check.** Before asking the operator for scope, Cora reads her own `chronology.md` and inspects the most recent wrapup entry. If that entry recorded a skipped Step 0a (soft-conditional skip from the prior session's Wrapup), the default scope for this invocation is auto-promoted from `since-handoff` to `full-repo`. One skip is absorbed by the next session; two consecutive skips force a full sweep. Cora flags the tripwire to the operator: "Prior session skipped the harmonization sweep — I'm promoting today's scope to full-repo. Proceed, or override?"

2. **Scope handshake.** Ask the operator: "Full repo sweep, since-handoff-only, or directory-scoped?" Default: since-handoff (unless the tripwire promoted it). When invoked from Marcus mid-run, skip the handshake and use Marcus's passed scope.

3. **Anchor resolution.** The session-start anchor is the commit that last modified `SESSION-HANDOFF.md`, resolved via `git log -1 --format=%H -- SESSION-HANDOFF.md`. For since-handoff scope: use this anchor as `<handoff-anchor>`. For full-repo or directory scope: document the scope explicitly in the report.

4. **Change-window resolution (since-handoff scope only).** Build the change window as the union of three git sets:
   - Committed: `git diff --name-only <handoff-anchor>..HEAD`
   - Uncommitted modified: `git diff --name-only HEAD`
   - Untracked: `git ls-files --others --exclude-standard`
   The union is the file set passed to Audra as the `changed_files_window`. Untracked files are included deliberately — a new doc introduced but not yet committed can drift just as easily as a modified one.

5. **Report home.** Create `{project-root}/reports/dev-coherence/YYYY-MM-DD-HHMM/`. This is the only valid output location; never write harmonization reports elsewhere.

6. **Invoke Audra L1 deterministic sweep.** Context envelope: `{anchor, scope, workflow, report_home, changed_files_window}`. Wait for structured result. If exit code \!= 0, halt the pipeline — report L1 findings to operator; do not run L2 until L1 is clean. Note: Audra's whole-repo invariant checks (L1-3 parameter-directory <-> schema lockstep, L1-4 gate-contract lockstep, L1-5 lane-matrix coverage) run regardless of scope; only the file-window checks (L1-2, L1-7) respect the change window.

7. **On L1 clean — invoke Audra L2 agentic sweep.** Scope: the same changed-files window for since-handoff scope; full-repo for full-repo scope. Context envelope: `{changed_docs, anchor, report_home}`.

8. **Route substantial prose work to Paige.** If Audra's L2 surfaces a doc rework exceeding paragraph scope, Cora offers to route to `bmad-agent-tech-writer` (Paige). Operator decides.

9. **Synthesize report.** Cora authors a top-level `harmonization-summary.md` in the report home citing Audra's trace report(s) and any Paige routes offered. Operator-facing two-paragraph summary at the top. Include: tripwire status (fired / not fired), scope used, change-window file count, and counts of L1/L2 findings by severity.

10. **Present to operator.** Summary + link to report home. Ask: "Remediate now, queue for next session, or defer?"

11. **Skip-logging (conditional).** If this `/harmonize` was invoked as Wrapup Step 0a and the operator asks to skip it because the change window is empty, Cora does NOT run the sweep but MUST append a skip entry to `chronology.md`: `YYYY-MM-DD HH:MM — Step 0a skipped: <reason>`. The next session's tripwire check (Step 1 above) depends on this breadcrumb.

## Lane Discipline

Cora does NOT author coherence verdicts. Every judgment in the report is sourced from Audra (or Paige, for prose). Cora's authorship is scoped to: tripwire check, scope handshake, anchor resolution, change-window resolution, report-home creation, synthesis of Audra's sub-reports into an operator-facing top-level, routing decisions, and skip-logging.

## Marcus-Route Variant

When Marcus invokes Cora mid-run with a scoped coherence check request, skip the scope handshake (Step 2) and use the scope Marcus passed. Return the Audra trace report to Marcus, not to the operator. Marcus relays to the operator as part of the run conversation.
