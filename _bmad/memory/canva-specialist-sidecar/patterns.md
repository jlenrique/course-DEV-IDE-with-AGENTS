# Patterns

- Prefer Canva-native template primitives before custom edits.
- Treat PPTX import as a bootstrap step, not final output.
- Validate readability at both projection and laptop scales.
- Keep exports deterministic: document format, naming, and intent.

## Marcus Communication Expectations

- Poll responses must include feasible contribution, no-API constraints, and recommended workflow.
- Task responses must include ordered steps and explicit blockers.
- Accessibility checks must be listed in every guidance-ready response.

## Error Handling

- If required template family is unavailable, return blocked with a replacement shortlist.
- If style sources are unreadable, halt and request style source resolution.
- If PPTX import drifts heavily, recommend manual rebuild for affected slide(s) with rationale.

## Exemplar Scope (v1)

- Story 3.8 establishes the manual-tool guidance baseline only.
- Automated woodshed exemplar reproduction is intentionally deferred for Canva.
