# Lesson Planner Story Readiness Checklist

Use this before opening or starting any remaining Lesson Planner MVP story.
This is an operational checklist shared between the support lane and the
authoritative BMAD story-authoring lane.

## Required before story start

- Confirm `sprint-status.yaml` is the canonical source for state.
- Confirm the story is in the intended gate lane:
  - `single-gate` for precedent-heavy and lower-risk stories
  - `dual-gate` only for explicitly designated foundation, refactor, or high-risk stories
- Confirm predecessor stories are actually closed, not just planned.
- Run the deferred-work touch check:
  - if the story touches a module with deferred findings, review only the findings relevant to that touched surface
  - otherwise leave deferred work parked

## T1 readiness block

Every upcoming story should declare:

- gate mode
- K floor
- target collecting-test range
- required readings
- scaffold required or not
- anti-pattern categories in scope
- side-work or runway dependency, if any

The block heading should be explicit: `## T1 Readiness`.
Before a story is treated as `ready-for-dev`, run:

- `python scripts/utilities/validate_lesson_planner_story_governance.py <story-file>`

Do not start `bmad-dev-story` if that command fails.

## Required readings

For Lesson Planner stories, read and name the relevant sections from:

- `docs/dev-guide/story-cycle-efficiency.md`
- `docs/dev-guide/dev-agent-anti-patterns.md`
- `docs/dev-guide/pydantic-v2-schema-checklist.md` for schema-shape stories

## K-floor discipline

- Default target is `1.2x` to `1.5x` the K floor.
- If the test count rises above `1.5x K`, record why the extra coverage is justified.
- Do not let parameterized theater stand in for named coverage gaps.

## Scaffold rule

If the story is schema-shaped, the scaffold should be ready before dev begins.

- Use `scripts/utilities/instantiate_schema_story_scaffold.py`.
- If a pre-seed already exists, use `--skip-story-spec`.
- Generated scaffold tests remain dormant until the authoritative dev pass turns them into story-real tests.
- The story spec should cite either `docs/dev-guide/scaffolds/schema-story/` or
  `scripts/utilities/instantiate_schema_story_scaffold.py`.

## Parallel runway rule

While one story is in review or patching, keep the next prep tasks explicit.

Current queue:

- `30-1` golden-trace baseline capture completion
- `29-1` non-authoritative warm-start prep
- `32-2` schema-story scaffold readiness
- `32-1` and `32-4` spec-readiness notes

## Closeout hygiene

When story state changes, refresh:

- `sprint-status.yaml` first
- `next-session-start-here.md` second
- any top-level plan or report status line that would now mislead the next session
