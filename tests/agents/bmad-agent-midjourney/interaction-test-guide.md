# Interaction Test Guide: Mira (Midjourney Specialist)

## Scenario 1: Bespoke medical image prompt package
- Trigger: request for a clinical process visual.
- Expect: ready-to-paste prompt set with v6/v7 parameter recommendations.

## Scenario 2: Iteration workflow guidance
- Trigger: user asks how to improve first generation.
- Expect: Discord/web iteration steps with seed-preserving guidance.

## Scenario 3: Manual-tool boundary
- Trigger: request to call Midjourney REST API directly.
- Expect: explain manual-tool mode and return prompt workflow instead.

## Scenario 4: Governance routing
- Trigger: out-of-scope request (LMS deployment).
- Expect: route_to Marcus with concise reason.
