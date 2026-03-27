# Access Boundaries for Kira (Kling Specialist)

## Read Access
- `state/config/course_context.yaml`
- `state/config/style_guide.yaml`
- `resources/style-bible/`
- `course-content/staging/`
- `course-content/courses/`
- `skills/kling-video/`
- `scripts/api_clients/kling_client.py` (read-only for understanding)
- `_bmad/memory/kling-specialist-sidecar/`
- Source assets from Gary, Irene, ElevenLabs, and Marcus delegation

## Write Access
- `_bmad/memory/kling-specialist-sidecar/`
- `course-content/staging/`

## Deny Zones
- `.env`
- Other agents' memory sidecars
- `resources/style-bible/` (write)
- `tests/`
- Runtime modification of API client code from the agent layer
