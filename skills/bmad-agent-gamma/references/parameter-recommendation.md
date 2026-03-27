# Parameter Recommendation (PR)

Recommend optimal Gamma API parameter combinations given content type, learning objective, and audience context from the delegation envelope.

## Decision Process

1. Read style guide defaults from `state/config/style_guide.yaml` → `tool_parameters.gamma`
2. **Check for template**: If `template_id` in context envelope, route to from-template endpoint (see `./references/content-type-mapping.md` for template logic). If no template_id, check the template registry for a scope + content_type match — if found, recommend it to Marcus before proceeding with text generation.
3. Identify content type from context envelope (use CT capability if mapping is needed)
4. Check memory sidecar `patterns.md` for previously effective parameter combinations for this content type
5. Apply style bible visual standards (colors, typography, accessibility)
6. Construct complete parameter set with reasoning for each non-default choice

## Parameter Priority (merge order)

See `./references/style-guide-integration.md` for the canonical five-level merge order. In short: API defaults → style guide → content type template → context envelope overrides → Gary's per-request judgment. Later levels win.

## Embellishment Control

Gamma adds content even in `textMode: preserve`. Proactively include constraining `additionalInstructions` when content fidelity matters:

- **Strict faithful**: `"Output ONLY the provided text. Do not add content, steps, or diagrams beyond what is given. Do not embellish or expand."`
- **Moderate control**: `"Stay close to the provided content. Minor formatting adjustments are acceptable but do not add new information."`
- **Creative freedom**: Omit constraint — allow Gamma to enhance

Track which constraint phrasings produce the best fidelity outcomes in `patterns.md`.

## Image Control

- `imageOptions.source: "noImages"` — use for faithful reproduction and text-focused slides
- `imageOptions.source: "pexels"` or `"webFreeToUse"` — use for production slides needing stock imagery
- `imageOptions.source: "aiGenerated"` — use when custom visuals are explicitly requested

## Export Format Selection

- **PNG** — default for production. These are visual assets for video production (Descript, CapCut, Kling) and course embedding (CourseArc, Canvas). Lossless quality at Gamma's render resolution.
- **PDF** — for human review at checkpoint gates, woodshed comparison (text extraction), and archival.
- **PPTX** — when downstream editing or manual refinement is planned.

Always request export and download immediately — URLs expire (~7 days).

## Recommendation Format

Return parameter recommendations as structured blocks:

```yaml
parameters:
  inputText: "[content]"
  textMode: preserve
  format: presentation
  numCards: 1
  additionalInstructions: "[constraint + layout guidance]"
  textOptions:
    amount: brief
  imageOptions:
    source: noImages
  exportAs: pdf
reasoning:
  textMode: "Preserve mode because input content is finalized"
  numCards: "Single slide exemplar"
  additionalInstructions: "Constraining embellishment + requesting specific layout"
  imageOptions: "Text-focused slide — images would distract"
```
