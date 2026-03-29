# Access Boundaries: Canva Specialist

## Read
- resources/style-bible/
- state/config/style_guide.yaml
- course-content/staging/
- skills/bmad-agent-canva/
- skills/canva-design/
- _bmad/memory/canva-specialist-sidecar/

## Write
- course-content/staging/
- _bmad/memory/canva-specialist-sidecar/

## Deny
- .env
- other sidecar directories
- scripts/api_clients/

Rationale: Canva specialist follows a manual-tool contract. Deny zones prevent accidental crossover into credential surfaces or API execution lanes owned by other specialists.
