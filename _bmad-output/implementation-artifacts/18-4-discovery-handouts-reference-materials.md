# Story 18.4: Content Type Discovery — Handouts & Reference Materials

**Epic:** 18 — Additional Assets & Workflow Families
**Status:** backlog
**Sprint key:** `18-4-discovery-handouts-reference-materials`
**Added:** 2026-04-06
**Depends on:** Core pipeline stability. Epic 17 research services (soft — related resources and citations for reference materials).

## Summary

Discovery-first story: elicit detailed requirements for handout and reference material production. These supplemental assets complement presentations and lessons. The Canva specialist (manual-tool pattern) provides visual design guidance, and Epic 17 research services provide citation enrichment.

## Goals

1. Define handout types: study guide, cheat sheet, quick reference, glossary, procedure guide, worksheet.
2. Specify design requirements: visual standards, accessibility, print-readiness.
3. Map agent roles leveraging existing specialists.
4. Identify tool requirements and assess design tooling options.
5. Define relationship to primary content (companion vs. standalone).
6. Define output formats for print and digital delivery.
7. Define the workflow family.

## Existing Infrastructure To Reuse

- `skills/bmad-agent-content-creator/` (Irene) — content design, learning objective alignment
- `skills/bmad-agent-canva/` — Canva visual design guidance (manual-tool pattern, Story 3.8)
- `skills/canva-design/` — Canva design knowledge skill
- `skills/bmad-agent-gamma/` (Gary) — Gamma for simple visual elements within handouts
- `skills/research-services/` (Epic 17) — related resources and citation injection for reference materials
- `skills/bmad-agent-quality-reviewer/` (Quinn-R) — quality and accessibility review
- `skills/bmad-agent-fidelity-assessor/` (Vera) — source fidelity for reference accuracy
- `config/content-standards.yaml` — voice, audience, accessibility defaults
- `resources/style-bible/` — brand alignment standards

## Key Files

- `_bmad-output/planning-artifacts/discovery-handouts-reference-materials.md` — new: requirements document
- `_bmad-output/planning-artifacts/epics.md` — update: implementation stories added after approval

## Acceptance Criteria

1. Requirements document covers all seven goals above.
2. Handout type taxonomy includes at least: study guide, cheat sheet/quick reference, glossary, procedure guide, worksheet, reading guide.
3. Design requirements section covers: brand alignment (style bible), accessibility (WCAG), print vs. screen optimization, typography and layout standards.
4. Agent role matrix shows Irene (content), Canva specialist (design guidance), Gary (visual elements where appropriate), Quinn-R (quality), and research services (citations).
5. Tool assessment evaluates: Canva (design), Gamma (visual elements), PDF generation pipeline, and identifies any tooling gaps.
6. Relationship section defines: companion-to-lesson linking, standalone reference indexing, and asset-lesson pairing invariant compliance.
7. Output format section covers: PDF (print-ready), Markdown, Canva design template, Canvas page/file attachment.
8. Workflow family definition compatible with structural-walk manifest pattern.
9. Document reviewed and approved before implementation stories are created.
