# Epic 28 Story Worksheet — TEMPLATE

Per-story worksheet filled during story execution. Mirrors the Epic 26 migration-worksheet pattern. Copy this file to `worksheet-<story-id>.md`, fill in as the story progresses.

## Header

- **Story:** 28-N — [title]
- **Sprint key:** `28-N-<slug>`
- **Operator:** Juanl
- **Dev:** [Amelia / other specialist]
- **Opened:** YYYY-MM-DD
- **Closed:** YYYY-MM-DD
- **Points:** [estimate] / [actual]

## Pre-Work Checklist

- [ ] Epic 28 AC Spine reviewed; all 8 shared ACs acknowledged
- [ ] Story AC list drafted and party-mode green-light obtained
- [ ] Dependencies verified (27-2 scite provider available? schemas published?)
- [ ] Tracy sanctum bundle state: [fresh / already-scaffolded / custom]
- [ ] Test scaffold in place (`@pytest.mark.tracy_pilot` + xfail-strict markers)

## Dispatch Topology Verification

Before merge, verify:
- [ ] No Tracy → Texas direct runtime call added in this story (grep test passes)
- [ ] Every Tracy output artifact written atomically
- [ ] Pre-Pass-2 gate receipt (if touched) validates under all three resolution paths

## AC Tracking

| AC | Status | Test | Notes |
|----|--------|------|-------|
| S1 (dispatch topology) | | | |
| S2 (atomic writes) | | | |
| S3 (pre-Pass-2 gate) | | | |
| S4 (manifest schema) | | | |
| S5 (vocabulary SSOT) | | | |
| S6 (editorial_note) | | | |
| S7 (test floor) | | | |
| S8 (dispatch audit log) | | | |
| Story-specific ACs: list inline | | | |

## Deviations from Plan

Document any material deviation from the story's as-ratified AC or file-impact estimate. Brief rationale + party-mode consensus record if a deviation crossed a design boundary.

## Code-Review Record

### Blind Hunter
- Opened: YYYY-MM-DD
- Findings: MUST-FIX count / SHOULD-FIX count / NIT count
- Remediation summary:

### Edge Case Hunter
- Opened:
- Findings:
- Remediation:

### Acceptance Auditor
- Opened:
- AC-by-AC verdict:
- Remediation:

## Artifact Checklist

- [ ] Story artifact at `_bmad-output/implementation-artifacts/28-N-<slug>.md` updated with closure record
- [ ] `sprint-status.yaml` entry status promoted to `done`
- [ ] Test additions listed; skips/xfails accounted for
- [ ] Documentation updated (vocabulary.yaml, runbook if protocol changed)
- [ ] Dispatch audit log example committed to `tests/fixtures/tracy/` if story added new dispatch semantics

## Retrospective Notes

Fill after merge. Signal for future stories:
- What worked
- What dragged
- What I'd do differently next time
- Signal for v2 backlog: did this story's work surface new evidence on Loop A / B / C / D, coherence drift, or dispatch budget?
