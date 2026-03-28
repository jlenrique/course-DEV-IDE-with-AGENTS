# Parameter Recommendation (PR)

Recommend optimal Gamma API parameter combinations given content type, learning objective, and audience context from the delegation envelope.

## Decision Process

1. Read style guide defaults from `state/config/style_guide.yaml` → `tool_parameters.gamma`
2. **Check for template**: If `template_id` in context envelope, route to from-template endpoint (see `./references/content-type-mapping.md` for template logic). If no template_id, check the template registry for a scope + content_type match — if found, recommend it to Marcus before proceeding with text generation.
3. **Resolve style preset** (SP capability): If the envelope includes `style_preset`, resolve by name. Otherwise resolve by `theme_id` or scope via `resolve_style_preset()`. A matched preset provides image model, style, text mode, and other parameters that establish the visual identity baseline. See `./references/style-preset-library.md`.
4. Identify content type from context envelope (use CT capability if mapping is needed)
5. Check memory sidecar `patterns.md` for previously effective parameter combinations for this content type
6. Apply style bible visual standards (colors, typography, accessibility)
7. Construct complete parameter set with reasoning for each non-default choice

## Parameter Priority (merge order)

See `./references/style-guide-integration.md` for the canonical six-level merge order. In short: API defaults → style guide → **style preset** → content type template → context envelope overrides → Gary's per-request judgment. Later levels win.

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

## Deck Mode Parameter Guidance

When `deck_mode: true` or content type maps to multi-slide, apply deck-specific guidance:

### numCards Ranges by Content Type

| Content Type | Recommended numCards | Rationale |
|-------------|---------------------|-----------|
| Lecture deck | 5-12 | One concept per card; Gamma decides breaks |
| Case study deck | 3-5 | Presenting complaint → diagnosis → management |
| Module overview | 3-4 | Objectives → topics → assessment preview |
| Assessment set | 2-4 | One question per card; use inputTextBreaks |
| Narrative arc | 4-8 | Story beats, rising action |
| Module bumper | 1-2 | Title + subtitle or title only |

`numCards: auto` is valid — Gamma decides the count. Use `auto` when Irene's slide brief says "Gary's judgment" for number of slides.

### cardSplit Strategy

- `"auto"` — Gamma decides how to distribute content across cards. Use for most lecture and narrative content.
- `"inputTextBreaks"` — Gamma splits on `\n---\n` separators in `inputText`. Use when Irene provides a brief with explicit per-slide sections marked.

### Deck-Level additionalInstructions

Deck-mode instructions must address both the overall deck AND per-card structure:
- **Lecture deck**: `"Professional medical education deck. Each card covers one key concept. Consistent visual hierarchy throughout: Montserrat headings, clean body text, ample white space. Do not pack multiple concepts onto one card."`
- **Case study deck**: `"Clinical case study format. Card 1: presenting complaint. Cards 2-3: clinical reasoning. Final card: management summary. Maintain clinical narrative voice throughout."`
- **Assessment set**: `"Assessment slide format. Each card contains exactly one question with clearly separated answer options. Question prompt prominent. No explanatory text on question cards — save explanations for separate review slides if needed."`

## Export Format Selection

- **PNG** — default for production pipeline. Gary's PNGs are the primary visual input to Irene's Pass 2 (`gary_slide_output`) and downstream to Kira (image-to-video) and Descript (slide holds). Lossless quality at Gamma's render resolution.
- **PDF** — for human review at HIL Gate 2, woodshed comparison (text extraction), and archival.
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
