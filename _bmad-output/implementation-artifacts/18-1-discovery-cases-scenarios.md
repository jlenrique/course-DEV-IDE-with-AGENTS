# Story 18.1: Content Type Discovery — Cases & Scenarios

**Epic:** 18 — Additional Assets & Workflow Families
**Status:** backlog
**Sprint key:** `18-1-discovery-cases-scenarios`
**Added:** 2026-04-06
**Depends on:** Core pipeline stability (Epics 1-14 complete). At least one successful narrated-deck trial run recommended.

## Summary

Discovery-first story: elicit detailed requirements for case study and scenario-based learning content production. The deliverable is a requirements document, not code. Implementation stories will be added to this epic after the discovery document is reviewed and approved by the operator.

## Goals

1. Define content structure: narrative arc, decision points, branching vs. linear, debriefing components.
2. Identify source material requirements: real-world data, anonymization, domain expertise needs.
3. Map agent roles: Irene for pedagogy, potential new specialist for scenario logic, Quinn-R for quality.
4. Identify tool requirements: Gamma for visuals? Botpress for interactive branching? New tools?
5. Define output formats: document, slide-embedded, LMS-native, interactive web.
6. Specify HIL gate placement and what the human reviews at each gate.
7. Define the workflow family: named stages, handoff contracts, acceptance criteria.

## Existing Infrastructure To Reuse

- `skills/bmad-agent-content-creator/` (Irene) — pedagogical design for case structure, learning objectives
- `skills/bmad-agent-quality-reviewer/` (Quinn-R) — quality review adapted for case content
- `skills/bmad-agent-marcus/` — orchestration, routing, checkpoint choreography
- `scripts/api_clients/botpress_client.py` — potential interactive branching platform (Tier 2: API Only)
- `skills/research-services/` (Epic 17) — hypothesis research mode for pro/con case evidence
- `skills/bmad-agent-gamma/` (Gary) — visual treatments for case scenarios
- `skills/source-wrangler/` — ingestion of case source materials from Notion/Box
- Canvas deployment pipeline (Story 3.6) — LMS-native case delivery
- Existing HIL gate pattern from narrated-deck workflow

## Key Files

- `_bmad-output/planning-artifacts/discovery-cases-scenarios.md` — new: requirements document (deliverable)
- `_bmad-output/planning-artifacts/epics.md` — update: implementation stories added after approval

## Acceptance Criteria

1. Requirements document exists in `_bmad-output/planning-artifacts/` covering all seven goals above.
2. Content structure section includes: narrative arc patterns (linear, branching, iterative), decision point taxonomy, debriefing components, and complexity levels.
3. Agent role matrix specifies which existing agents participate and whether new specialists are needed.
4. Tool requirements section evaluates Botpress (interactive branching), Gamma (case visuals), Canvas (LMS-native), and identifies any gaps.
5. Output format section specifies at least: PDF document, slide-embedded version, Canvas module structure.
6. HIL gates section specifies gate count, gate placement, and per-gate review criteria.
7. Workflow family definition includes named stages and handoff contracts compatible with existing structural-walk manifest pattern.
8. Document reviewed and approved by operator before implementation stories are created.
