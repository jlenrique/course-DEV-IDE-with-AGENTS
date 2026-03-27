# Access Boundaries for Quinn-R (Quality Reviewer)

## Read Access
- Entire project repository (needs to review any produced artifact)
- `resources/style-bible/`
- `state/config/course_context.yaml`
- `state/config/style_guide.yaml`
- `state/config/tool_policies.yaml`
- `state/runtime/coordination.db`
- `course-content/`
- `_bmad/memory/quality-reviewer-sidecar/`
- `skills/quality-control/`

## Write Access
- `_bmad/memory/quality-reviewer-sidecar/`
- `state/runtime/coordination.db` (quality_gates table via quality_logger.py only)

## Deny Zones
- `.env`
- `scripts/api_clients/`
- `course-content/` (write — review only, never modify)
- Other agents' memory sidecars (write)
- `resources/style-bible/` (write)
- `.cursor-plugin/`
- `tests/`
