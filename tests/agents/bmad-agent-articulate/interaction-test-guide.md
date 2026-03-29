# Interaction Test Guide: Aria (Articulate Specialist)

## Scenario 1: Branching scenario specification
- Trigger: request for branching clinical decision module.
- Expect: branch map with decision points, remediation loops, objective tracing, and explicit completion criteria.

## Scenario 2: SCORM export review
- Trigger: user asks for pre-upload verification.
- Expect: checklist covering manifest, launch path, completion tracking, LMS smoke test, and gradebook verification.

## Scenario 2A: WCAG interaction compliance
- Trigger: user asks for accessibility readiness.
- Expect: explicit checks mapped to WCAG 2.1 AA criteria and evidence payload fields.

## Scenario 3: Manual-tool boundary
- Trigger: request to run Articulate API generation.
- Expect: no-API clarification and step-by-step UI build guidance.

## Scenario 4: Wrong-agent redirect
- Trigger: request for video synthesis.
- Expect: redirect to Kling/ElevenLabs through Marcus.

## Scenario 5: Human review gate
- Trigger: user asks to mark output finalized.
- Expect: response requires reviewer sign-off artifact at tests/agents/bmad-agent-articulate/review-sign-off.md.
