# Closure-Artifact Audit (CA)

Spot-mode check triggered by Cora's pre-closure protocol. A single story ID is the input; a CA finding plus evidence is the output.

## Trigger

Cora invokes this capability when the operator signals intent to flip a story from an in-progress state to `done` in `_bmad-output/implementation-artifacts/sprint-status.yaml`.

## Inputs

- `story_id` — e.g., `22-2`, `20c-15`, `SB.1`
- `report_home` — path under `reports/dev-coherence/` for the evidence file

## The Four Closure Artifacts

BMAD closure discipline requires, for every story flipped to `done`:

1. **Acceptance criteria satisfied.** The story file includes explicit AC, and each AC has verification evidence (either in-story narrative or linked evidence file).
2. **Automated verification logged.** Script exit codes, test pass lines, structural-walk returns — any deterministic "green" evidence appropriate to the story type. For pure-documentation stories, automated verification can be a lint or link-check pass; for code stories, it's a test-suite pass.
3. **Layered code review present.** Review record from at least one reviewer other than the author. For solo-operator projects, a Quinn-R / Murat / Winston subagent review record in `_bmad-output/` counts.
4. **Remediated review record present.** Review findings have been acknowledged and either addressed (with evidence) or consciously deferred (with a noted reason).

## Check Steps

1. Read the story file. Locate AC list and verify each has evidence.
2. Grep the story file, implementation artifacts, and run records for automated-verification evidence (`structural_walk` exit codes, `pytest` pass lines, contract-validation receipts).
3. Grep `_bmad-output/implementation-artifacts/` for review records referencing the story ID.
4. For each review record, verify there is a remediation note (either inline or as a subsequent doc) acknowledging findings.

## Finding Shape

Return a structured object:

```yaml
check: closure-artifact
story_id: <id>
ac_satisfied: true | false
ac_evidence_path: <path-or-null>
automated_verification_logged: true | false
automated_verification_evidence_path: <path-or-null>
layered_review_present: true | false
layered_review_path: <path-or-null>
remediated_review_present: true | false
remediated_review_path: <path-or-null>
overall_status: pass | warn
gap_summary: "<one-line-if-warn>"
```

Any `false` in the four artifact checks sets `overall_status: warn`. Per Phase 6 policy: **never block**. Always relay to Cora who relays to the operator.

## Evidence File

Write an evidence file at `{report_home}/evidence/ca-<story_id>.md` containing:

- Story file excerpt showing AC list
- Grep results for automated verification
- Paths to review records (if any)
- Specific gaps if any artifact is missing

## Warn-Mode Language

When returning a warn, phrase the finding in a way Cora can relay cleanly:

- `gap_summary: "Story <id> has AC + automated verification, but no remediated review record. A review exists at <path> but no remediation note."`

Not:

- `gap_summary: "You forgot to remediate the review"` (blame-tone)
- `gap_summary: "Review seems incomplete, probably" (fuzzy)`
