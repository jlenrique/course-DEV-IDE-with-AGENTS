# Memory System — Gary (Gamma Specialist)

## Core Principle

Gary's memory captures parameter effectiveness patterns and production outcomes — the expertise that makes each successive slide generation better than the last. Memory is mode-aware: default mode learns, ad-hoc mode does not.

## File Structure

Sidecar location: `{project-root}/_bmad/memory/gamma-specialist-sidecar/`

| File | Purpose | Write Rules |
|------|---------|-------------|
| `index.md` | Active context, mastery status, quick-access preferences | Default: full. Ad-hoc: transient section only |
| `access-boundaries.md` | Read/write/deny zones | Set at build time, read-only at runtime |
| `patterns.md` | Learned parameter effectiveness, content type mappings, embellishment control phrases, fidelity-specific learnings (constraint effectiveness per fidelity class, image placement results, visual consistency across split calls, edge cases in preserve mode) | Default mode only (append) |
| `chronology.md` | Slide generation history, exemplar mastery milestones | Default mode only (append) |

## Write Discipline

### Default Mode
- **`index.md`**: Update active context after each production task — current mastery status, most-used parameters, active run context
- **`patterns.md`**: Append after successful production runs — what parameter combinations worked, for what content types, quality scores achieved. Periodically condense redundant entries
- **`chronology.md`**: Append after each generation — run ID, content type, parameters used, quality scores, outcome
- **`access-boundaries.md`**: Read-only at runtime

### Ad-Hoc Mode
- **`index.md`**: Transient ad-hoc session section only (cleared on switch back to default)
- All other sidecar files: **read-only** — experimental runs do not pollute learned patterns

### Never Cache
Style bible content (`resources/style-bible/`) and exemplar content (`resources/exemplars/`) are always re-read from disk. Memory stores parameter effectiveness *outcomes*, not reference document content.

## Memory Maintenance

`patterns.md` is append-only and will grow over time. Periodically:
1. Review for redundant or contradicted patterns
2. Condense into authoritative summaries
3. Remove patterns that have been superseded by better-performing alternatives
4. Commit the condensed version

## Access Boundaries

### Read (both modes)
- `state/config/style_guide.yaml` — tool parameter preferences
- `state/config/course_context.yaml` — course hierarchy
- `resources/style-bible/` — brand identity and visual standards (re-read fresh)
- `resources/exemplars/gamma/` — exemplar library
- `resources/exemplars/_shared/` — comparison rubric, woodshed protocol
- `skills/gamma-api-mastery/` — own mastery skill
- `skills/woodshed/` — shared woodshed skill
- GammaClient API client at project-level `api_clients/` (read code for understanding, not modify)
- `docs/directory-responsibilities.md` — configuration hierarchy
- Context envelope data from Marcus delegation

### Write (default mode)
- `{project-root}/_bmad/memory/gamma-specialist-sidecar/` — own sidecar
- `course-content/staging/` — generated slide artifacts
- `resources/exemplars/gamma/{id}/reproductions/` — woodshed outputs
- `resources/exemplars/gamma/{id}/reproduction-spec.yaml` — updated reproduction specs
- `resources/exemplars/gamma/_catalog.yaml` — mastery status updates
- `skills/gamma-api-mastery/references/parameter-catalog.md` — API doc refresh updates

### Write (ad-hoc mode)
- `{project-root}/_bmad/memory/gamma-specialist-sidecar/index.md` — transient section only
- `course-content/staging/ad-hoc/` — scratch area
- Reproduction artifacts (woodshed always records attempts)

### Deny (both modes)
- `.env` — secrets
- GammaClient API client — never modify (read-only for code understanding)
- Other agents' memory sidecars
- `resources/style-bible/` — human-curated, read-only
- `.cursor-plugin/plugin.json` — infrastructure
- `tests/` — not Gary's responsibility
