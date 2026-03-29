# Canvas Specialist — Access Boundaries

## Read (both modes)

- `state/config/`
- `scripts/api_clients/`
- `skills/canvas-deployment/`
- `skills/woodshed/`
- `resources/exemplars/canvas/`
- `course-content/staging/`
- `_bmad/memory/canvas-specialist-sidecar/`

## Write (default mode)

- `_bmad/memory/canvas-specialist-sidecar/` (append-only patterns and chronology)
- `course-content/staging/` (deployment outputs, if any)
- `resources/exemplars/canvas/{id}/reproductions/` (woodshed artifacts)
- `resources/exemplars/canvas/_catalog.yaml` (status updates)

## Write (ad-hoc mode)

- `_bmad/memory/canvas-specialist-sidecar/index.md` transient section only
- `course-content/staging/ad-hoc/`

## Deny (both modes)

- `.env`
- Other agent sidecars under `_bmad/memory/`
- Human-curated style bible source docs (read-only)
