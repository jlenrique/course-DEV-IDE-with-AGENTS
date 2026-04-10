# Story 18.3: Content Type Discovery — Discussions & Review Activities

**Epic:** 18 — Additional Assets & Workflow Families
**Status:** backlog
**Sprint key:** `18-3-discovery-discussions-review-activities`
**Added:** 2026-04-06
**Depends on:** Core pipeline stability. Epic 17 research services (soft — hypothesis mode feeds debate scaffolds).

## Summary

Discovery-first story: elicit detailed requirements for discussion prompt and review activity production. These content types are inherently collaborative and often scaffold higher-order thinking. The Epic 17 hypothesis research mode is a natural complement for debate-style discussions.

## Goals

1. Define discussion types: open-ended, structured debate, case discussion, peer review, reflection.
2. Define review activity types: peer critique, self-assessment rubric, portfolio review prompt.
3. Specify scaffolding requirements: discussion rubrics, response templates, moderation guidance.
4. Map agent roles leveraging existing specialists.
5. Identify research integration points (Epic 17 hypothesis mode).
6. Define output formats for LMS delivery and standalone use.
7. Define the workflow family.

## Existing Infrastructure To Reuse

- `skills/bmad-agent-content-creator/` (Irene) — pedagogical scaffolding, rubric design, Bloom's alignment
- `skills/bmad-agent-quality-reviewer/` (Quinn-R) — quality review for instructional soundness
- `skills/canvas-deployment/` — Canvas discussion topic creation, rubric deployment
- `scripts/api_clients/canvas_client.py` — Canvas discussion and assignment API endpoints
- `skills/research-services/` (Epic 17) — hypothesis research for debate scaffolds, pro/con evidence
- `skills/source-wrangler/` — source material ingestion for discussion topics
- `skills/bmad-agent-marcus/` — orchestration and routing

## Key Files

- `_bmad-output/planning-artifacts/discovery-discussions-review-activities.md` — new: requirements document
- `_bmad-output/planning-artifacts/epics.md` — update: implementation stories added after approval

## Acceptance Criteria

1. Requirements document covers all seven goals above.
2. Discussion type taxonomy includes at least: open-ended, structured debate, Socratic seminar, case discussion, peer review, reflective journal prompt.
3. Review activity taxonomy includes at least: peer critique with rubric, self-assessment, portfolio review, group evaluation.
4. Scaffolding section specifies: discussion rubrics, response templates, sentence starters, moderation guidance, grading criteria.
5. Research integration section maps Epic 17 hypothesis mode to debate and critical analysis discussions.
6. Agent role matrix shows how Irene (pedagogy), Canvas specialist (LMS delivery), Quinn-R (quality), and research services (evidence) collaborate.
7. Output format section covers: Canvas discussion topic (with rubric attachment), standalone prompt document, rubric document.
8. Workflow family definition compatible with structural-walk manifest pattern.
9. Document reviewed and approved before implementation stories are created.
