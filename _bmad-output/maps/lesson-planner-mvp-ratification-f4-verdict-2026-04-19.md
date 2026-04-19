# Lesson Planner MVP Ratification — F4 Verdict (2026-04-19)

**Round type:** BMAD party-mode green-light  
**Participants:** Sally (UX), John (PM), Winston (Architect), Murat (Test Architect)  
**Precondition evidence:** `reports/dev-coherence/2026-04-19-1546/` (A-first remediation + full-repo harmonize re-verify)

## Global Verdict

- **Decision:** Proceed with Marcus trial production run now.
- **Gate posture:** Conditional GREEN / YELLOW (no BLOCK flags).
- **Required framing (ratified):** **MVP = UX-ready backend contracts + walkthrough harness, not rendered UX.**

## Per-Flag Verdicts

| Flag | Verdict | Owner | Follow-on |
|---|---|---|---|
| 1 — No rendered UX layer in MVP scope | BACKLOG-FOLLOW-ON | PM + UX | Open post-MVP rendered UX epic with explicit acceptance boundaries. |
| 2 — §6-C runnable at terminal | RATIFY-AS-SHIPPED | PM + Operator | Keep terminal walkthrough path as accepted MVP trial method. |
| 3 — "Card turns gold" semantic relocation | RATIFY-AS-SHIPPED | Architect + PM | Keep semantic pin on `scope_decision.state == "ratified"` + verbatim rationale. |
| 4 — Stub-dials "next sprint" wording | BACKLOG-FOLLOW-ON | PM + Eng Lead | Either ship rendered controls in follow-on or soften wording to remove time-bound promise. |
| 5 — Retrospectives optional | BACKLOG-FOLLOW-ON | PM | Produce one consolidated Lesson Planner MVP retrospective artifact. |

## Preconditions Satisfied in this Session

- Fixed Tracy collection regression by scoping package registration in `tests/conftest.py`.
- Rolled stale zero-edit baseline forward in `tests/contracts/test_30_1_zero_test_edits.py`.
- Restored `04A` stage threading in `scripts/utilities/run_hud.py`.
- Verification complete:
  - targeted regression slice: `11 passed`
  - HUD/progress lockstep slice: `78 passed`
  - full repo suite: `1910 passed, 4 skipped, 27 deselected, 2 xfailed`

## Trial-Start Guardrails

1. Re-run command set in `reports/dev-coherence/2026-04-19-1546/evidence/reverify-commands.md` immediately before kickoff.
2. Preserve trial input/config provenance for reproducibility.
3. Enforce stop condition on new deterministic drift or critical runtime failure.
