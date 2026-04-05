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
| `gamma_operations.py` | Production entry point (`execute_generation`): fidelity-aware routing (single-call or two-call split), style guide merge with vocabulary enforcement, URL validation for diagram_cards, GammaClient calls, poll, export, download | Gary (PR, SG, SP, CT capabilities) |
| `gamma_evaluator.py` | Analyze exemplars, derive reproduction specs, execute reproductions, compare against rubric | Gary (ES capability) via woodshed skill |

## Reference Index

| Reference | Purpose | Loaded When |
|-----------|---------|-------------|
| `parameter-catalog.md` | Full Gamma API parameter space with educational guidance | Gary needs parameter details beyond content-type templates |
| `context-optimization.md` | Pre-built parameter templates per content type | Gary's CT capability maps content type to params |
| `doc-sources.yaml` | URLs for mandatory doc refresh before woodshed cycles | Gary's ES capability runs doc refresh |

## Production Entry Point

**`execute_generation()`** is the production entry point for all slide generation. It handles fidelity-aware routing automatically:

- If `slides` parameter includes mixed fidelity classes → dispatches to `generate_deck_mixed_fidelity()` (two-call split: creative in `generate` mode, literal in `preserve` mode with vocabulary-derived constraints)
- If all slides are the same class or no fidelity data → dispatches to `generate_slide()` (single call)
- `merge_parameters()` enforces the fidelity-control vocabulary for literal slides: `text_treatment` → `textMode`, `image_treatment` → `imageOptions.source`, free-text `additionalInstructions` stripped for literal slides
- `diagram_cards` image URLs are validated via `validate_image_url()` before generation proceeds — unreachable URLs halt generation with an error
- **Preintegration bypass**: When a literal-visual card has a local `preintegration_png_path` and `export_dir` is set, the source PNG is copied directly to the export directory — Gamma is skipped entirely for that slide. This guarantees 100% full-slide fill with zero rendering variance. The provenance record shows `generation_id: "preintegration-bypass"`. When no local PNG is available, the system falls back to Gamma API generation with a full-bleed guard instruction.

Gary should always use `execute_generation()` for production runs. `generate_slide()` is the low-level single-call function used internally and for woodshed/debugging.

## Generation Modes

This skill supports three Gamma API operations:

| Mode | Endpoint / Method | When |
|------|------------------|------|
| **Text generation** | `POST /v1.0/generations` | Standard — build slides from content with full parameter control |
| **Template generation** | `POST /v1.0/generations/from-template` | When a custom Gamma template (`gammaId`) exists for the scope |
| **Theme/template listing** | `GET /v1.0/themes` via `GammaClient.list_themes()` | Gary's TP capability — before generation when theme selection is needed |
| **Style preset resolution** | `resolve_style_preset()` in `gamma_operations.py` | Gary's SP capability — after theme selection, resolves a named visual-identity preset from `state/config/gamma-style-presets.yaml` |

### list_themes_and_templates Operation

Invoked by Gary's TP (Theme/Template Preview) capability. Combines:
1. `GammaClient.list_themes(limit=20)` — returns available Gamma themes from the API
2. Template registry lookup from `state/config/style_guide.yaml` → `tool_parameters.gamma.templates`, filtered by scope and content_type

Returns a combined result for Gary to present to Marcus/user:
```python
{
  "registered_templates": [...],  # from style_guide.yaml registry
  "gamma_themes": [...],          # from API
  "recommendation": "..."         # Gary's reasoning
}
```

This operation does NOT consume generation credits. It is safe to call before every deck generation.

### Style Preset Resolution

After theme selection, Gary resolves a matching **style preset** via `resolve_style_preset()` in `gamma_operations.py`. Presets live in `state/config/gamma-style-presets.yaml` and map a theme (plus scope) to supplementary API parameters — image model, image style, text mode, card dimensions — that fully specify a reproducible visual identity. Resolution order: by name → by theme_id → by scope. Resolved preset parameters are injected into the merge cascade at level 3 (between style guide and content type template). See Gary's `./references/style-preset-library.md` for full details.

Template-based generation uses `gammaId` + `prompt`. The template encodes layout and visual standards; the prompt provides new content. See `./references/parameter-catalog.md` for full template endpoint documentation.
