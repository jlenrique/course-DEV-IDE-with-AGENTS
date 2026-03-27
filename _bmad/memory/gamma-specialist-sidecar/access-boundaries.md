# Gary — Access Boundaries

## Read (both modes)
- `state/config/style_guide.yaml` — tool parameter preferences
- `state/config/course_context.yaml` — course hierarchy
- `resources/style-bible/` — brand identity, visual standards (re-read fresh)
- `resources/exemplars/gamma/` — exemplar library
- `resources/exemplars/_shared/` — comparison rubric, woodshed protocol
- `skills/gamma-api-mastery/` — mastery skill (SKILL.md, references, scripts)
- `skills/woodshed/` — shared woodshed skill
- GammaClient API client code (read for understanding, not modify)
- `_bmad/memory/gamma-specialist-sidecar/` — own memory sidecar
- `docs/directory-responsibilities.md` — configuration hierarchy
- Context envelope data from Marcus delegation

## Write (default mode)
- `_bmad/memory/gamma-specialist-sidecar/` — own sidecar (all files per mode rules)
- `course-content/staging/` — generated slide artifacts
- `resources/exemplars/gamma/{id}/reproductions/` — woodshed outputs
- `resources/exemplars/gamma/{id}/reproduction-spec.yaml` — updated specs
- `resources/exemplars/gamma/_catalog.yaml` — mastery status updates
- `skills/gamma-api-mastery/references/parameter-catalog.md` — API doc refresh updates

## Write (ad-hoc mode)
- `_bmad/memory/gamma-specialist-sidecar/index.md` — transient section only
- `course-content/staging/ad-hoc/` — scratch area
- Reproduction artifacts (woodshed always records attempts)

## Deny (both modes)
- `.env` — secrets
- GammaClient API client code — never modify
- Other agents' memory sidecars
- `resources/style-bible/` — human-curated, read-only
- `.cursor-plugin/plugin.json` — infrastructure
- `tests/` — not Gary's responsibility
