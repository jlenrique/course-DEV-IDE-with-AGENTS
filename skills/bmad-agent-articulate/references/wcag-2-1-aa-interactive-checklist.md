# WCAG 2.1 AA Interactive Checklist (Articulate)

Reference documentation:

- WCAG 2.1 Quick Reference: https://www.w3.org/WAI/WCAG21/quickref/

## Required Checks

- 2.1.1 Keyboard (A): all interactions are keyboard-operable.
- 2.1.2 No Keyboard Trap (A): users can move focus away from all components.
- 2.4.3 Focus Order (A): focus sequence preserves meaning and operability.
- 2.4.7 Focus Visible (AA): visible focus state for interactive controls.
- 1.3.1 Info and Relationships (A): structure and relationships are programmatically identifiable.
- 1.3.2 Meaningful Sequence (A): content reading order matches intended meaning.
- 1.4.3 Contrast (Minimum) (AA): text and UI contrast meet AA thresholds.
- 1.4.10 Reflow (AA): layout remains usable at 320 CSS px equivalent where applicable.
- 1.3.3 Sensory Characteristics (A): instructions do not rely on color only.
- 1.1.1 Non-text Content (A): meaningful alternatives for non-text assets.
- 3.3.2 Labels or Instructions (A): controls include clear labels/instructions.

## Articulate-Specific Validation

- Storyline triggers can be executed without mouse-only actions.
- Rise interaction blocks expose readable labels and instructions.
- Branching hotspots include keyboard equivalents and focus order checks.

## Verification Matrix

| Criterion | Test Method | Evidence |
|---|---|---|
| 2.1.1 | Keyboard-only path through each interaction branch | video capture or step log |
| 2.1.2 | Attempt tab/shift+tab escape from modal/hotspot states | issue log or pass note |
| 2.4.3 | Record focus order for all controls in sequence | focus-order checklist |
| 2.4.7 | Capture focused state screenshots for key controls | screenshot set |
| 1.4.3 | Measure text/control contrast values | contrast report |
| 1.3.1 / 1.3.2 | Validate heading/reading sequence for narration and content | structural audit note |
| 1.1.1 | Confirm alt text or transcript mapping for media | media inventory map |
| 3.3.2 | Verify labels/instructions for every required learner action | interaction copy checklist |

## Evidence Format

- criterion code
- pass/fail
- evidence path
- remediation action
- verifier
- verification date
