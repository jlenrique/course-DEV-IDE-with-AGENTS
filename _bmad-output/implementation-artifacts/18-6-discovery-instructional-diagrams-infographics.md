# Story 18.6: Content Type Discovery — Instructional Diagrams & Infographics

**Epic:** 18 — Additional Assets & Workflow Families
**Status:** backlog
**Sprint key:** `18-6-discovery-instructional-diagrams-infographics`
**Added:** 2026-04-06
**Depends on:** Core pipeline stability. Existing Canva and Midjourney specialists.

## Summary

Discovery-first story: elicit detailed requirements for instructional diagram and infographic production. These visual learning aids explain processes, relationships, and data. The Canva specialist (manual-tool pattern) and Midjourney specialist (manual-tool pattern) already exist for visual design guidance. Gary (Gamma) can produce simple diagrams as slide content.

## Goals

1. Define visual types: process flow, concept map, comparison chart, timeline, data visualization, anatomical/technical diagram.
2. Specify design requirements: brand alignment, accessibility, resolution for print and screen.
3. Map agent roles leveraging existing visual specialists.
4. Identify tool requirements and assess capability gaps.
5. Specify accuracy requirements for data visualizations and technical diagrams.
6. Define output formats for embedding and standalone use.
7. Define the workflow family.

## Existing Infrastructure To Reuse

- `skills/bmad-agent-canva/` — Canva visual design guidance (manual-tool pattern, Story 3.8)
- `skills/canva-design/` — Canva design knowledge skill
- `skills/bmad-agent-midjourney/` — Midjourney bespoke visual prompt packages (manual-tool pattern, Story 5.1)
- `skills/bmad-agent-gamma/` (Gary) — Gamma for simple diagrams as slide content
- `skills/bmad-agent-content-creator/` (Irene) — content design, learning objective alignment
- `skills/bmad-agent-quality-reviewer/` (Quinn-R) — visual quality and accessibility review
- `skills/bmad-agent-fidelity-assessor/` (Vera) — source fidelity for data accuracy
- `skills/sensory-bridges/` — image sensory bridge for visual perception
- `resources/style-bible/` — brand alignment standards
- `config/content-standards.yaml` — accessibility defaults

## Key Files

- `_bmad-output/planning-artifacts/discovery-instructional-diagrams-infographics.md` — new: requirements document
- `_bmad-output/planning-artifacts/epics.md` — update: implementation stories added after approval

## Acceptance Criteria

1. Requirements document covers all seven goals above.
2. Visual type taxonomy includes at least: process/workflow diagram, concept map, comparison chart, timeline, data visualization, anatomical/technical diagram.
3. Design requirements section covers: brand alignment (style bible), accessibility (alt text, color contrast), resolution targets (print 300dpi, screen 72-150dpi), typography.
4. Agent role matrix shows: Irene (content/structure), Canva specialist (design guidance), Midjourney specialist (bespoke visuals), Gary (simple diagrammatic slides), Quinn-R (quality), Vera (data accuracy).
5. Tool assessment evaluates: Canva (design templates), Midjourney (bespoke imagery), Gamma (diagrammatic slides), SVG/diagramming tools, and identifies capability gaps.
6. Accuracy section specifies: domain expert review requirements for data visualizations, technical diagram validation process.
7. Output format section covers: PNG (screen), SVG (scalable), PDF (print), embeddable in slides/handouts/Canvas pages.
8. Workflow family definition compatible with structural-walk manifest pattern.
9. Document reviewed and approved before implementation stories are created.
