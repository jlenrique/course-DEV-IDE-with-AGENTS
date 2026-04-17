# Pre-Closure Protocol (PC)

Triggered when the operator indicates intent to flip a story from any in-progress state to `done` in `sprint-status.yaml`.

Phase-6 scope in `dev-support-agents-vision.md`: **warn mode** — surface findings, never block. Promotion to block mode is deferred until one full wave of experience validates signal quality.

## Steps

1. **Capture story ID.** Operator says "mark story 22-3 done" or similar. Parse story ID.
2. **Invoke Audra closure-artifact audit.** Context envelope: `{story_id, report_home}`.
   - Audra checks the four BMAD closure artifacts:
     - Acceptance criteria present and satisfied
     - Automated verification logged (script exit codes, test passes)
     - Layered code review present
     - Remediated review record present (review findings acknowledged and addressed)
3. **On all four present.** Cora relays: "Audra's closure audit is clean for [story_id]. Good to flip to `done`." Operator proceeds.
4. **On any gap.** Cora relays in warn-mode format: "Audra flagged [summary of gap(s)] on [story_id]. You can still flip, but I want to flag it. Proceed, pause to remediate, or defer to next session?"
5. **Never flip status in `sprint-status.yaml` directly.** The operator owns this write. Cora only surfaces findings.
6. **If flipped despite warnings.** Append to `chronology.md`: `YYYY-MM-DD HH:MM — Story <ID> flipped to done despite Audra warnings: <summary>.` This is a pattern input for later sidecar learning.

## Memory Implication

After 10+ warn-mode invocations, review `chronology.md` for patterns. If a class of closure-artifact gap is consistently surfaced and consistently overruled, that pattern goes into `patterns.md` as either a false-positive signal (tune Audra) or a real discipline gap (surface to operator as a process question).

## When NOT to Invoke

- Story status changes that do not touch `done` (e.g., `in-progress` → `blocked`, or `draft` → `ready`)
- Bulk status updates during sprint planning
- Retrospective closures where the operator has already run the closure audit manually

In these cases Cora stays silent.
