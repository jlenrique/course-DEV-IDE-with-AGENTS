# Exemplar Study (ES)

Analyze exemplar artifacts to extract patterns and derive reproduction specifications for the woodshed workflow.

## Doc Refresh (Mandatory Before Woodshed)

Before any exemplar study or reproduction, check for Gamma API changes:

1. Read `skills/gamma-api-mastery/references/doc-sources.yaml` for authoritative URLs and `last_refreshed` date
2. Check the Gamma API changelog for changes since last refresh
3. If changes found: scan affected parameter pages via Ref MCP (`ref_search_documentation`, `ref_read_url`)
4. Update `skills/gamma-api-mastery/references/parameter-catalog.md` if API changes are discovered
5. Log discoveries to memory sidecar `patterns.md`

## Exemplar Analysis Process

For each exemplar in `resources/exemplars/gamma/{id}/`:

1. **Read the brief** (`brief.md`) — extract:
   - Layout pattern (parallel comparison, title-plus-body, three-column cards, assessment, narrative progression)
   - Content structure (headings, body, sections, items)
   - Pedagogical type (content delivery, assessment, narrative, synthesis)
   - What the agent should learn (agent guidance from the brief)

2. **Examine the source** (`source/`) — analyze the actual artifact:
   - Visual structure and spatial layout
   - Text density and distribution
   - Color usage and contrast
   - Typography hierarchy

3. **Derive reproduction spec** — map analysis to Gamma API parameters:
   - `numCards` based on slide count
   - `textMode` based on content finality (preserve for final content, generate for outlines)
   - `additionalInstructions` for layout guidance and embellishment control
   - `textOptions` for density control
   - `imageOptions` for image handling
   - `exportAs` for output format

4. **Save spec** to `resources/exemplars/gamma/{id}/reproduction-spec.yaml`

## Integration with GammaEvaluator

The `GammaEvaluator` in `skills/gamma-api-mastery/scripts/gamma_evaluator.py` extends `BaseEvaluator` from `skills/woodshed/scripts/woodshed_base.py`. It implements:

- `analyze_exemplar()` — extract layout pattern, content structure, pedagogical type
- `derive_reproduction_spec()` — map analysis to Gamma API parameters
- `execute_reproduction()` — call GammaClient via gamma_operations.py
- `compare_reproduction()` — Gamma-specific comparison with rubric weights

Gary provides the analytical judgment; the evaluator provides the execution framework.

## Exemplar Library

Current exemplars in `resources/exemplars/gamma/_catalog.yaml`:

| ID | Level | Layout Pattern | Key Learning |
|----|-------|---------------|-------------|
| L1-two-processes-one-mind | L1 | two-column-parallel | Parallel comparison with preserve mode |
| L2-diagnosis-innovation | L2 | title-plus-body | Minimal content, embellishment control |
| L3-deep-empathy | L3 | three-column-cards | Multi-section card layout |
| L4.1-check-your-understanding | L4.1 | assessment-interactive | Assessment formatting |
| L4.2-youre-already-an-innovator | L4.2 | narrative-progression | Three-beat story arc |

## Mastery Progression

L1-L2 must be mastered (faithful mode) before L3-L4. Faithful mode must pass before creative mode unlocks per exemplar. See `skills/woodshed/SKILL.md` for the complete workflow, circuit breaker rules, and reflection protocol.
