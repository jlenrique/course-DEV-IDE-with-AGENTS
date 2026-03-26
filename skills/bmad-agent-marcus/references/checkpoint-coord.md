# Human Checkpoint Coordination

## Purpose

Marcus manages human review gates throughout production workflows. These are non-negotiable quality control points where the user — as creative director and domain expert — reviews, approves, rejects, or requests revision of specialist output.

## Review Gate Protocol

At each checkpoint, Marcus:

1. **Presents the artifact** — Show the work product clearly, with enough context for informed review
2. **States quality criteria** — Reference the specific style bible standards and learning objectives that apply
3. **Shows specialist self-assessment** — Share the specialist's own evaluation of the artifact against criteria
4. **Requests explicit decision** — Ask for one of: approve, reject with reason, or request specific revisions

Example: "Here's the cardiac physiology slide deck — 14 frames covering all four learning objectives. The style bible calls for JCPH Navy headers with Medical Teal highlights on interactive elements. Gamma's self-assessment: all objectives covered, visual hierarchy consistent, one accessibility note on contrast ratio for Figure 3. What's your call — approve, adjust, or revise?"

## Decision Handling

- **Approved** — Record approval in state, advance production plan to next stage, save parameter decisions to patterns (default mode only)
- **Revision requested** — Capture specific feedback, route back to specialist with revision context, re-present at next review gate
- **Rejected** — Record rejection with reason, discuss alternatives with user, adjust production plan

## Quality Criteria Sources

Quality criteria come from two sources, both re-read fresh for each review gate:

- **Style bible** (`resources/style-bible/`) — brand identity, visual standards, accessibility, content voice/tone
- **Medical education standards** — Bloom's alignment, clinical case integration quality, assessment-objective tracing, backward design adherence

## Outcome Tracking

In default mode, record checkpoint outcomes in state:
- Artifact identifier and version
- Decision (approved / revision / rejected)
- Revision count for this artifact
- User feedback notes (condensed)
- Time from first presentation to final approval

This data feeds expertise crystallization in `patterns.md` and production history in `chronology.md`.

## Script Integration

Use the `production-coordination` skill to persist checkpoint outcomes:

- **Before presenting**: call `manage_run.py checkpoint {run_id}` to mark the stage `awaiting-review` and create a `quality_gates` record.
- **On approval**: call `manage_run.py approve {run_id} --score {0.0-1.0}` to record the decision and update the gate record.
- **On revision**: note the feedback in the conversation context. The stage remains at `awaiting-review` until approved or the user redirects.
