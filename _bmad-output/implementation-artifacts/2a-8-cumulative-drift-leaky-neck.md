# Story 2A-8: Cumulative Drift Tracking & Leaky Neck Remediation

Status: done

## Story

As a course content producer,
I want the Fidelity Assessor to track cumulative fidelity drift across the entire pipeline and I want all leaky necks in the pipeline remediated,
So that small per-gate fidelity losses don't compound into large divergence from SME intent, and all deterministic constraints are enforced deterministically.

## Tasks / Subtasks

- [x] Task 1: Implement resolve_source_ref() — heading hierarchy, line range, heading anchor. 11 tests pass.
- [x] Task 2: Gate evaluation protocol Step 6b added — global drift checks at G3+, source_ref resolver, evidence retention
- [x] Task 3: Fidelity-control vocabulary defined: text_treatment, image_treatment, layout_constraint, content_scope
- [x] Task 4: Slide brief template updated with vocabulary section — literal slides use vocabulary, creative slides keep additionalInstructions
- [x] Task 5: Drift thresholds added to Fidelity Trace Report (ad-hoc 20/40%, production 10/20%, regulated 5/10%)
- [x] Task 6: 38 contracts valid, parity PASS, 11 resolver tests pass, no regressions

## Dev Agent Record

### Agent Model Used
Claude claude-4.6-opus (via Cursor)
### Completion Notes List
- `resolve_source_ref()` implemented with 3 resolution modes (heading hierarchy, line range, heading anchor), case-insensitive matching, partial hierarchy support, 11 tests
- Cumulative drift tracking: global check at G3+ comparing current output to G0 source themes via source_ref chains
- Drift thresholds configurable per run mode: ad-hoc (20%/40%), production (10%/20%), regulated (5%/10%)
- Fidelity-control vocabulary: 4 deterministic fields replacing free-text additionalInstructions for literal slides
- Slide brief template updated: literal slides use vocabulary, creative slides keep additionalInstructions
- Evidence retention format for drift captures self-contained comparison records
### File List
**New:**
- `scripts/resolve_source_ref.py` (provenance resolver)
- `tests/test_resolve_source_ref.py` (11 tests)
**Modified:**
- `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md` (Step 6b drift, resolver reference)
- `skills/bmad-agent-fidelity-assessor/references/fidelity-trace-report.md` (drift section)
- `skills/bmad-agent-content-creator/references/template-slide-brief.md` (fidelity-control vocabulary)
### Change Log
- 2026-03-28: Story 2A-8 — source_ref resolver, cumulative drift tracking, fidelity-control vocabulary, drift thresholds
