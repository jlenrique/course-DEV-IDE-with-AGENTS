# Story 17.2: Related Resources List Generation

**Epic:** 17 — Research & Reference Services
**Status:** backlog
**Sprint key:** `17-2-related-resources-list-generation`
**Added:** 2026-04-06
**Depends on:** Story 17.1 (API clients and triangulation module).

## Summary

Build the core "Related Resources" generator that takes a presentation script or lesson notes (typically Irene Pass 2 output) and produces a credible, triangulated list of supplemental references for learners. Outputs in multiple formats: standalone Markdown document, last-slide-ready format for Gamma embedding, and structured YAML for agent consumption.

## Goals

1. Theme/claim extraction from narration scripts and lesson notes.
2. Per-theme research via triangulation service (Story 17.1).
3. Ranked, filtered output with relevance summaries and reliability indicators.
4. Multiple output formats for different consumption patterns.
5. Configurable resource count and depth.

## Existing Infrastructure To Build On

- `scripts/utilities/research_triangulator.py` (Story 17.1) — triangulation service
- `skills/bmad-agent-content-creator/` (Irene) — produces the narration scripts consumed as input
- `skills/source-wrangler/` — ingestion pipeline pattern for text extraction; potential consumer
- `skills/gamma-api-mastery/` — Gary can embed last-slide resources when given slide-ready format
- `state/config/run-constants.yaml` — run-level configuration pattern

## Key Files

- `scripts/utilities/related_resources.py` — new: theme extraction + research + formatting
- `state/config/run-constants.yaml` — `research_resource_count` (default: 8)
- Output templates: Markdown, slide-ready, YAML formats

## Acceptance Criteria

1. Input accepts: narration script text (Irene Pass 2), lesson notes (source bundle), or arbitrary Markdown text.
2. Theme/claim extraction identifies key concepts, assertions, and domain terms from input text.
3. Each theme is researched via `research_triangulator.triangulate()`.
4. Results filtered and ranked by: relevance to source claim, reliability score, recency, accessibility (open-access preferred).
5. Output contains per-resource: title, authors, publication year, DOI/URL, one-sentence relevance summary, reliability indicator (triangulated / single-source), grouped by theme or source section.
6. Configurable output count: default 5-10, adjustable via `research_resource_count` in run constants.
7. Output formats: Markdown (standalone `related-resources.md`), slide-ready (formatted for Gamma last-slide embed), YAML (`related-resources.yaml` for agent consumption).
8. Callable by Marcus, Irene, or source wrangler via `generate_related_resources(text, config)`.
9. Unit tests cover theme extraction, ranking logic, and all three output formats.
