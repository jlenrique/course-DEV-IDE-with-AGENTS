# Canvas Deployment Workflows

This reference defines standard deployment flows for the Canvas specialist.

## Shared Sequence (All Flows)

1. Validate manifest schema and required identifiers.
2. Run accessibility pre-check on all text content.
3. Resolve target course ID (`manifest -> style_guide -> first available course`).
4. Create Canvas entities in dependency order.
5. Attach entities to modules with explicit item ordering.
6. Verify resulting module structure.
7. Return confirmation URLs and structured status.

## Modules

Use when the lesson or unit requires grouped learner navigation.

- Create module via `CanvasClient.create_module`.
- Respect `require_sequential_progress` when specified.
- Add content as module items in intended learner order.
- Verify expected module names after publish.

## Pages

Use for instructional content, overview pages, and static references.

- Create page via `CanvasClient.create_page`.
- Enforce accessibility pre-check on page body content.
- Add page to module as `module_item[type]=Page` with `module_item[page_url]`.
- Return page confirmation URLs.

## Quizzes

Use for graded checks and formative assessments.

- Verify quiz/assignment metadata includes points and submission intent.
- Preferred path for New Quizzes: create assignment object and attach to module.
- If quiz is represented as assignment payload, use `CanvasClient.create_assignment`.
- Verify created assignment appears in course assignment listing.

## Discussions

Use for learner interaction prompts and reflective activities.

- Create discussion topic via Canvas discussion endpoint.
- Enforce accessibility pre-check on discussion prompt/message.
- Attach discussion to module as `module_item[type]=Discussion`.
- Return direct discussion confirmation URL.

## Assignments

Use for submissions, graded exercises, and rubric-backed activities.

- Create assignment via `CanvasClient.create_assignment`.
- Ensure `points_possible` and `submission_types` are explicit for graded work.
- Attach assignment to module as `module_item[type]=Assignment`.
- Verify assignment appears in listing for grading integration confidence.

## Failure Handling

- If any create/attach step fails after writes begin, execute rollback in reverse dependency order.
- Rollback order: module items -> discussions -> assignments -> pages -> modules.
- Return rollback summary alongside the original error for auditability.
