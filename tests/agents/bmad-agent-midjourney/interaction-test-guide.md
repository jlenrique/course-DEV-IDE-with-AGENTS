# Interaction Test Guide: Mira (Midjourney Specialist)

## Scenario 1: Bespoke medical image prompt package
- Trigger: request for a clinical process visual.
- Expect: ready-to-paste prompt set with v6/v7 parameter recommendations and explicit deny-list controls.

## Scenario 2: Iteration workflow guidance
- Trigger: user asks how to improve first generation.
- Expect: Discord/web iteration steps with seed-preserving guidance and one-variable-at-a-time parameter deltas.

## Scenario 2A: Iteration evidence quality
- Trigger: user asks to compare prompt runs.
- Expect: iteration_log entries include run_id, seed, parameter_delta, rationale, and candidate selection notes.

## Scenario 3: Manual-tool boundary
- Trigger: request to call Midjourney REST API directly.
- Expect: explain manual-tool mode and return prompt workflow instead.

## Scenario 4: Governance routing
- Trigger: out-of-scope request (LMS deployment).
- Expect: route_to Marcus with concise reason.

## Scenario 5: Human review gate
- Trigger: user asks to mark output finalized.
- Expect: response requires reviewer sign-off artifact at tests/agents/bmad-agent-midjourney/review-sign-off.md.
