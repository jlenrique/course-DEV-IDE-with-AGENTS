# Qualtrics Specialist - Access Boundaries

## Read (both modes)

- state/config/
- scripts/api_clients/
- skills/qualtrics-assessment/
- skills/woodshed/
- resources/exemplars/qualtrics/
- _bmad/memory/qualtrics-specialist-sidecar/

## Write (default mode)

- _bmad/memory/qualtrics-specialist-sidecar/ (append-only patterns and chronology)
- course-content/staging/ (assessment outputs, if any)
- resources/exemplars/qualtrics/{id}/reproductions/ (woodshed artifacts)
- resources/exemplars/qualtrics/_catalog.yaml (status updates)

## Write (ad-hoc mode)

- _bmad/memory/qualtrics-specialist-sidecar/index.md transient section only
- course-content/staging/ad-hoc/

## Deny (both modes)

- .env
- Other agent sidecars under _bmad/memory/
- Human-curated style bible source docs (read-only)
