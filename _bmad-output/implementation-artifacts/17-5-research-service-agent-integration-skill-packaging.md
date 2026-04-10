# Story 17.5: Research Service Agent Integration & Skill Packaging

**Epic:** 17 — Research & Reference Services
**Status:** backlog
**Sprint key:** `17-5-research-service-agent-integration-skill-packaging`
**Added:** 2026-04-06
**Depends on:** Stories 17.1-17.4 (all research service modules).

## Summary

Package the research service modules (triangulation, related resources, citation injection, hypothesis research) into a shared skill directory following the established SKILL.md pattern. Wire agent integration so Marcus, Irene, and source wrangler can invoke research capabilities through the skill interface. Add run-constants configuration, per-run caching, and reporting metrics.

## Goals

1. `skills/research-services/` skill directory with SKILL.md, references, scripts.
2. Three modes exposed: `related-resources`, `inline-citation`, `hypothesis`.
3. Agent integration: Marcus, Irene, source wrangler can delegate research.
4. Run-constants configuration for research behavior.
5. Per-run result caching to avoid redundant API calls.
6. Research metrics in run reporting.
7. Governance block: research retrieval and formatting only, no pedagogical or visual judgment.

## Existing Infrastructure To Build On

- Skill directory pattern: `skills/{name}/SKILL.md` + `references/` + `scripts/` (27 skills exist)
- `skills/source-wrangler/SKILL.md` — consumer; ingestion pipeline model to follow
- `skills/tech-spec-wrangler/SKILL.md` — similar shared-service skill pattern (doc refresh for agents)
- `skills/production-coordination/SKILL.md` — workflow stage and delegation patterns
- `skills/bmad-agent-marcus/SKILL.md` — orchestrator delegation references
- `state/config/run-constants.yaml` — run-level config pattern via `scripts/utilities/run_constants.py`
- Agent governance block pattern from Epic 4A (lane matrix, allowed_outputs, decision_scope)
- `docs/agent-environment.md` — shared skill inventory (update needed)

## Key Files

- `skills/research-services/SKILL.md` — new: skill definition, modes, governance block
- `skills/research-services/references/` — new: API docs, triangulation logic, output format specs
- `skills/research-services/scripts/` — symlinks or imports from `scripts/utilities/` research modules
- `skills/bmad-agent-marcus/SKILL.md` — update: research delegation reference
- `skills/bmad-agent-content-creator/SKILL.md` — update: research invocation during Pass 1/Pass 2
- `skills/source-wrangler/SKILL.md` — update: research enrichment option for source bundles
- `state/config/run-constants.yaml` — `research_enabled`, `research_mode`, `research_depth`
- `docs/agent-environment.md` — update: shared skill inventory entry

## Acceptance Criteria

1. `skills/research-services/SKILL.md` defines the skill with three modes: `related-resources`, `inline-citation`, `hypothesis`.
2. Governance block specifies lane: research retrieval and formatting only; NOT owned: pedagogical decisions, visual design, quality judgment.
3. Marcus can delegate: "Research related resources for this lesson" → skill returns structured results.
4. Irene can invoke: during Pass 1 (lesson planning with hypothesis research) or Pass 2 (narration with inline citations).
5. Source wrangler can invoke: enrich source bundles with related resources during ingestion.
6. Run-constants: `research_enabled: boolean` (default: false), `research_mode: related | citation | hypothesis | all`, `research_depth: light | moderate | thorough`.
7. Per-run caching: identical queries within a run return cached results without additional API calls.
8. Run reporting includes: queries made, citations found, triangulation rate, API credits consumed (if metered).
9. `docs/agent-environment.md` updated with research-services entry in shared skills table.
10. Integration tests: Marcus delegation flow, Irene invocation flow, source wrangler enrichment flow.
