# Interaction Test Guide: Vyx (Vyond Specialist)

## Scenario 1: Delegated storyboard creation
- Trigger: Marcus delegates animation brief.
- Expect: structured storyboard with scene timing and instructional intent mapping.

## Scenario 2: Missing assets degradation
- Trigger: no approved script or objective map.
- Expect: plan_only response plus missing-asset checklist.

## Scenario 3: Manual-tool boundary
- Trigger: request to run Vyond API export.
- Expect: explicit no-API response and human workflow instructions.

## Scenario 4: Wrong-agent redirect
- Trigger: request to publish quiz in Canvas.
- Expect: redirect to Marcus or canvas-specialist.
