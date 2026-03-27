---
name: gamma-api-mastery
description: "Gamma API tool mastery skill with parameter catalog, content-type optimization, and execution scripts. Invoked by Gary (bmad-agent-gamma) for all Gamma API operations."
---

# Gamma API Mastery

## Purpose

Provides complete Gamma API tool expertise for Gary (Slide Architect). This skill handles all Gamma API operations — generation, polling, export, download — and contains the parameter documentation, content-type optimization templates, and execution scripts that Gary uses to produce slides.

This is the **skill layer** in the three-layer architecture: Gary (agent — judgment) → gamma-api-mastery (skill — tool expertise) → GammaClient (API client — connectivity).

## Key Paths

| Path | Purpose |
|------|---------|
| `./references/parameter-catalog.md` | Complete Gamma API parameter documentation with value ranges and guidance |
| `./references/context-optimization.md` | Content-type → parameter templates for medical education |
| `./references/doc-sources.yaml` | Authoritative doc URLs, changelog, LLM-optimized endpoints for refresh |
| `./scripts/gamma_operations.py` | Agent-level GammaClient wrapper: style guide merge, generate, poll, export, download |
| `./scripts/gamma_evaluator.py` | Extends BaseEvaluator: exemplar analysis, reproduction, comparison |

## Script Index

| Script | Purpose | Invoked By |
|--------|---------|------------|
| `gamma_operations.py` | Load style guide defaults, merge with request params, call GammaClient, poll, export, download artifact | Gary (PR, SG, CT capabilities) |
| `gamma_evaluator.py` | Analyze exemplars, derive reproduction specs, execute reproductions, compare against rubric | Gary (ES capability) via woodshed skill |

## Reference Index

| Reference | Purpose | Loaded When |
|-----------|---------|-------------|
| `parameter-catalog.md` | Full Gamma API parameter space with educational guidance | Gary needs parameter details beyond content-type templates |
| `context-optimization.md` | Pre-built parameter templates per content type | Gary's CT capability maps content type to params |
| `doc-sources.yaml` | URLs for mandatory doc refresh before woodshed cycles | Gary's ES capability runs doc refresh |

## Generation Modes

This skill supports two Gamma API endpoints:

| Mode | Endpoint | When |
|------|----------|------|
| **Text generation** | `POST /v1.0/generations` | Standard — build slides from content with full parameter control |
| **Template generation** | `POST /v1.0/generations/from-template` | When a custom Gamma template (`gammaId`) exists for the scope |

Template-based generation uses `gammaId` + `prompt`. The template encodes layout and visual standards; the prompt provides new content. See `./references/parameter-catalog.md` for full template endpoint documentation.
