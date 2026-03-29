# External Canvas Mastery Exemplar Map

Purpose: Curate high-value Canvas API exemplars from https://github.com/Jlenrique-TEAM/canvas-mastery and map them to extension points in this repository.

## How to Use This Map

1. Pick one capability lane.
2. Create a new exemplar folder under resources/exemplars/canvas using the L1 snapshot pattern.
3. Reproduce via skills/woodshed/scripts/reproduce_exemplar.py.
4. Record outputs and update resources/exemplars/canvas/_catalog.yaml.

## Curated Exemplar Lanes

| Lane | External Source | Why It Matters | Local Extension Point |
|---|---|---|---|
| Page lifecycle | src/api/clients/client_helpers/page_helpers.py | Covers create, get, update, list page flows and error handling | scripts/api_clients/canvas_client.py and skills/canvas-deployment/scripts/canvas_operations.py |
| Assignment creation | src/services/assignment_service.py | Service-level pattern for create/list assignment orchestration and caching | skills/canvas-deployment/scripts/canvas_operations.py |
| Rubric linkage | docs/stories/rsm-003.reconciliation-execution.md | Clear endpoint contract for rubric association to assignments | skills/canvas-deployment/references/deployment-workflows.md |
| Outcomes bulk operations | src/api/clients/client_helpers/canvas_outcomes.py | Batch create patterns with stats and throughput feedback | future skill under skills/canvas-outcomes/ |
| Enrollment term pagination | src/api/clients/canvas_client.py (get_enrollment_terms) | Reliable pagination handling for large institutions | scripts/api_clients/canvas_client.py |
| Scale/performance behavior | tests/integration/test_canvas_api_integration.py | Large-volume scenarios and reliability expectations | tests/test_integration_canvas.py |
| Live module context loading | tests/integration/services/test_recommendation_engine_live.py | Real-world module/assignment shape capture from Canvas | resources/exemplars/canvas/ (new L2 reproducible snapshots) |
| Health + command workflows | _bmad-output/CANVAS-API-QUICK-REFERENCE.md | Operational command contracts already validated in another codebase | docs/ad-hoc-contract.md and future CLI wrappers |

## Suggested Next Exemplar IDs

- L2-module-build-with-page-assignment-discussion
- L2-assignment-plus-rubric-association
- L2-outcomes-bulk-create-with-dry-run
- L2-enrollment-term-pagination-audit
- L3-course-reconciliation-and-rollback

## Suggested Sequence

1. L2-module-build-with-page-assignment-discussion
2. L2-assignment-plus-rubric-association
3. L2-outcomes-bulk-create-with-dry-run
4. L3-course-reconciliation-and-rollback

## Notes

- Keep all runs audit-safe: never store token values in exemplar artifacts.
- Keep each exemplar deterministic with explicit course_id and expected output fields.
- Preserve dry-run first, then execute workflow for any write-capable exemplar.
