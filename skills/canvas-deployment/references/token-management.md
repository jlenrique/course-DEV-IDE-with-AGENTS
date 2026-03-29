# Canvas Token Management

## Required Environment Keys

- `CANVAS_API_URL`
- `CANVAS_ACCESS_TOKEN`

Optional policy keys:
- `CANVAS_TOKEN_SCOPES` (comma-separated scopes currently granted)
- `CANVAS_REQUIRED_SCOPES` (comma-separated scopes expected by institution)

## Handling Rules

1. Never print token values in logs or user-facing responses.
2. Validate presence of required keys before API calls.
3. Use `CanvasClient.get_self()` as an authentication sanity check.
4. If required scopes are configured, validate required subset before publish.
5. Return remediation guidance without exposing secret material.

## Rotation Guidance

- Treat repeated 401/403 as potential rotation/scope events.
- Pause deploy and request re-issuance from LMS admin.
- Re-run readiness checks after token update.

## Audit-safe Diagnostics

Allowed:
- key presence booleans
- status codes
- endpoint categories (course, module, assignment)

Not allowed:
- token value
- full raw auth headers
- copied `.env` content
