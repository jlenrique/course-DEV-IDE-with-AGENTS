# Story 17.4: Hypothesis & Learning Experience Research Mode

**Epic:** 17 — Research & Reference Services
**Status:** backlog
**Sprint key:** `17-4-hypothesis-learning-experience-research-mode`
**Added:** 2026-04-06
**Depends on:** Story 17.1 (triangulation service, especially Scite.ai citation context categorization).

## Summary

Add a hypothesis research mode that finds pro/con evidence for claims, themes, or hypotheses extracted from lesson content. Output is a structured research package suitable for designing learning experiences like debates, critical analysis exercises, and evidence-evaluation activities. Scite.ai citation contexts (supporting/contrasting/mentioning) are the primary differentiator from the general research mode.

## Goals

1. Hypothesis/claim extraction from lesson content.
2. Evidence categorization: supporting, contrasting, nuancing.
3. Structured hypothesis research package output.
4. Suggested learning activities based on evidence landscape.
5. Evidence strength assessment per side.
6. Academic integrity flagging for low-reliability findings.

## Existing Infrastructure To Build On

- `scripts/api_clients/scite_client.py` (Story 17.1) — citation context classification (supporting/contrasting/mentioning)
- `scripts/api_clients/consensus_client.py` (Story 17.1) — consensus-level findings
- `scripts/utilities/research_triangulator.py` (Story 17.1) — cross-validation
- `skills/bmad-agent-content-creator/` (Irene) — consumes packages for discussion design, debate scaffolds, critical thinking exercises
- Existing assessment/discussion patterns in Epic 18 discovery stories — this service feeds those workflows

## Key Files

- `scripts/utilities/hypothesis_researcher.py` — new: hypothesis extraction, evidence categorization, package generation
- `state/config/run-constants.yaml` — `research_mode: related | citation | hypothesis | all`

## Acceptance Criteria

1. Input: theme, claim, or hypothesis text (from lesson content or operator specification).
2. Scite.ai citation contexts used to identify: supporting evidence, contrasting evidence, mentioning-only references.
3. Consensus findings categorized by stance: supports, challenges, nuances.
4. Output is a structured hypothesis research package:
   - claim/hypothesis statement
   - supporting evidence summary with citations
   - contrasting evidence summary with citations
   - nuances and qualifications
   - suggested learning activities (e.g., "Have students compare Smith 2023 and Jones 2024")
   - evidence strength assessment per side
5. Consumable by Irene for designing discussion prompts, debate scaffolds, or critical thinking exercises.
6. Marcus can request hypothesis research during run planning when content involves multi-perspective topics.
7. Academic integrity note flags findings with low reliability or limited triangulation.
8. Unit tests: evidence categorization, balanced output, learning activity suggestions, integrity flagging.
