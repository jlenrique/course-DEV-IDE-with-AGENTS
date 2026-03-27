# Access Boundaries for Irene (Content Creator)

## Read Access
- `state/config/course_context.yaml`
- `state/config/style_guide.yaml`
- `resources/style-bible/`
- `resources/exemplars/`
- `course-content/`
- `course-content/_templates/`
- `_bmad/memory/content-creator-sidecar/`
- `docs/`

## Write Access
- `_bmad/memory/content-creator-sidecar/`
- `course-content/staging/`

## Deny Zones
- `.env`
- `scripts/api_clients/`
- `scripts/state_management/`
- Other agents' memory sidecars (write)
- `resources/style-bible/` (write)
- `.cursor-plugin/`
- `tests/`
- `state/config/` (write)
