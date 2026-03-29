# CourseArc Interactive Block Guidance

Scope and limitations:

- This guide covers verified patterns for sorting activities, flip cards, and virtual patient drills.
- If a requested interaction type is not listed here, escalate to Marcus for feasibility and platform-routing decisions.

Supported interaction guidance set:

1. Sorting activities: clear category labels and immediate correctness feedback.
2. Flip cards: concise front prompts and explanatory backs with source citations.
3. Virtual patient drills: branch logic with clinically safe remediation paths.

Clinical safety definition for virtual patient drills:

- No branch should recommend unsafe clinical action without immediate corrective feedback.
- Remediation path must include why an option is unsafe and what safer action is expected.
- Escalation moments must be clearly labeled for instructor debrief.

## Sorting Activities

Authoring steps:

1. Define category labels with clear, non-overlapping meaning.
2. Add draggable items mapped to one correct category each.
3. Configure immediate correctness feedback with remediation hints.

Validation checklist:

- Category wording is unambiguous.
- Each draggable has one intended destination.
- Keyboard traversal and focus order are testable.

Export and deployment notes:

- Include interaction instructions in the surrounding lesson text.
- Capture one completed-attempt screenshot in evidence bundle.

## Flip Cards

Authoring steps:

1. Place concise prompt on front face.
2. Place explanatory answer on back face with source citation.
3. Verify card sequence aligns with learning objective flow.

Validation checklist:

- Front text is short and readable.
- Back text includes source citation format agreed for course.
- Card navigation is keyboard and screen-reader testable.

Export and deployment notes:

- Add citation references in evidence-index for audit traceability.
- Record one card front/back pair in evidence artifacts.

## Virtual Patient Drills

Authoring steps:

1. Define branching scenario nodes with decision prompts.
2. Label safe and unsafe decisions explicitly in author notes.
3. Attach remediation text for each unsafe branch.
4. Add debrief summary for instructors.

Validation checklist:

- Unsafe options always trigger corrective guidance.
- Safe options reinforce rationale and next-step logic.
- Branch transitions are testable for keyboard-only navigation.

Export and deployment notes:

- Include branch map artifact in evidence bundle.
- Include remediation excerpts for at least one unsafe branch.

For each block type, return:
- objective alignment
- authoring steps
- validation checklist
- export/deployment notes

Decision path:

1. Is the requested interaction one of: sorting, flip card, virtual patient?
2. If yes, use this guide directly.
3. If no, return `status: blocked` and route to Marcus with requested interaction details.
