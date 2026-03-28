# Gamma API Parameter Catalog

Complete parameter reference for Gary's Gamma API operations. Sourced from [Gamma Developer Docs](https://developers.gamma.app) via Ref MCP doc refresh (2026-03-27).

## Endpoint: POST /v1.0/generations (Text Generation)

### Required Parameters

#### `inputText` (string, required)
Content used to generate the gamma. Supports text, structured markdown, and inline image URLs.
- Token limit: ~100,000 tokens (~400,000 chars)
- Use `\n---\n` to control card breaks (with `cardSplit: inputTextBreaks`)
- Image URLs can be embedded inline where they should appear
- **Medical ed guidance**: For faithful reproduction, provide exact final text. For lecture generation, provide outlines or notes.

#### `textMode` (string, required)
Controls how `inputText` is modified.
- `generate` — Gamma rewrites and expands. Best for brief outlines → full slides.
- `condense` — Gamma summarizes. Best for long notes → concise slides.
- `preserve` — Gamma retains exact text, may add structural headings. For zero modifications, add `additionalInstructions: "Do not modify the provided text in any way."`
- **Medical ed guidance**: Use `preserve` for finalized SME content. Use `generate` for outline-to-slides. Use `condense` for lengthy notes.
- **Known quirk**: Even in preserve mode, Gamma may add decorative elements, subtitles, or diagrams. Constrain via `additionalInstructions`.

### Optional Parameters

#### `format` (string, default: `presentation`)
- `presentation` | `document` | `social` | `webpage`
- **Medical ed guidance**: Always `presentation` for slides. Use `document` only for long-form handouts.

#### `themeId` (string, default: workspace default)
Theme ID from `GET /v1.0/themes`. Controls colors, fonts, visual style.
- Copy from Gamma app or list via API.
- **Medical ed guidance**: Use JCPH-branded theme if registered. Professional medical aesthetic, not consumer health.

#### `numCards` (integer, default: 10)
- Pro/Teams/Business: 1-60. Ultra: 1-75.
- **Medical ed guidance**: `1` for single-slide exemplars. `auto` for lecture decks. Pair with `textOptions.amount` to control density.

#### `cardSplit` (string, default: `auto`)
- `auto` — Gamma divides content by `numCards`.
- `inputTextBreaks` — Gamma splits on `\n---\n` in input (ignores `numCards`).
- **Medical ed guidance**: Use `inputTextBreaks` for L5+ multi-slide decks where you control the narrative flow.

#### `additionalInstructions` (string, 1-5000 chars)
Free-text guidance for layout, tone, structure, visual style.
- **Medical ed guidance**: Critical for embellishment control and layout specification.
- **Effective constraint phrasings**:
  - Strict: `"Output ONLY the provided text. Do not add content, steps, or diagrams beyond what is given."`
  - Layout: `"Two-column parallel comparison layout"`, `"Three-column card layout with equal-width sections"`
  - Assessment: `"Interactive assessment layout. Question prompt prominent. Answer options clearly separated."`

#### `folderIds` (array of strings)
Folder IDs for organizing output in Gamma workspace.

#### `exportAs` (string)
- `pdf` | `pptx` | `png` — one format per request.
- Export URLs are signed, expire ~7 days. Download immediately.
- **Medical ed guidance**: Default to `png` for production — slides are visual assets for video production and course embedding. Use `pdf` for human review at checkpoint gates and woodshed comparison. Use `pptx` when downstream editing is planned.

### textOptions (object)

#### `textOptions.amount` (string, default: `medium`)
- `brief` | `medium` | `detailed` | `extensive`
- Only relevant when `textMode` is `generate` or `condense`.
- **Medical ed guidance**: `brief` + `numCards: 1` = focused impact slides. `medium` + `numCards: auto` = balanced lecture decks.

#### `textOptions.tone` (string, 1-500 chars)
- Only relevant when `textMode` is `generate`.
- **Medical ed guidance**: `"Professional medical education, clear and evidence-based"` or `"Clinical narrative, patient-centered"`

#### `textOptions.audience` (string, 1-500 chars)
- Only relevant when `textMode` is `generate`.
- **Medical ed guidance**: `"Practicing physicians and health sciences graduate students"`

#### `textOptions.language` (string, default: `en`)
- ISO language code. See Gamma docs for accepted values.

### imageOptions (object)

#### `imageOptions.source` (string, default: `aiGenerated`)
| Value | Use Case |
|-------|----------|
| `aiGenerated` | Custom AI images (can specify model and style) |
| `pexels` | Stock photography |
| `webFreeToUse` | Web images licensed for personal use |
| `webFreeToUseCommercially` | Web images for commercial use |
| `themeAccent` | Accent images from selected theme |
| `placeholder` | Empty placeholders for manual addition |
| `noImages` | No images at all |
| `pictographic` | Pictographic illustrations |
| `giphy` | GIFs |
| `webAllImages` | All web images (licensing unknown) |

- **Medical ed guidance**: Use `noImages` for text-focused faithful reproduction. Use `pexels` for professional imagery. Never use `giphy` for medical education.

#### `imageOptions.model` (string, optional)
AI image model when source is `aiGenerated`. Options in Gamma docs reference.

#### `imageOptions.style` (string, 1-500 chars, optional)
Artistic style guidance when source is `aiGenerated`. The Gamma UI presents this as a tile picker (Photo, Illustration, Abstract, 3D, etc.) plus a free-text field. The API accepts a single string that combines the art style and any additional keywords.
- **Medical ed guidance**: `"Professional medical, clean, corporate"` or `"Data visualization, minimal, high contrast"`
- **Style preset integration**: When a style preset includes `imageOptions.keywords` (e.g., `[vector, minimalist, flat-color, linework, bold]`), these are appended to the style string at flatten time: `"illustration, vector, minimalist, flat-color, linework, bold"`. See `style-preset-library.md`.

### cardOptions (object)

#### `cardOptions.dimensions` (string)
- Presentation: `fluid` (default) | `16x9` | `4x3`
- Document: `fluid` (default) | `pageless` | `letter` | `a4`
- Social: `1x1` | `4x5` (default) | `9x16`
- **Medical ed guidance**: `16x9` for standard lecture presentations. `fluid` for content-first layouts.

#### `cardOptions.headerFooter` (object)
Positions: `topLeft`, `topRight`, `topCenter`, `bottomLeft`, `bottomRight`, `bottomCenter`
Types: `text` (value required), `image` (source: `themeLogo` | `custom`), `cardNumber`
Options: `hideFromFirstCard`, `hideFromLastCard`

### sharingOptions (object)

#### `sharingOptions.workspaceAccess` (string)
`noAccess` | `view` | `comment` | `edit` | `fullAccess`

#### `sharingOptions.externalAccess` (string)
`noAccess` | `view` | `comment` | `edit`

#### `sharingOptions.emailOptions` (object)
`recipients` (array of emails), `access` (string)

---

## Endpoint: POST /v1.0/generations/from-template

Template-based generation preserves an existing layout while swapping content.

### Required Parameters

#### `gammaId` (string, required)
The ID of the template gamma. Template must contain exactly one page. Copy from the Gamma app.

#### `prompt` (string, required)
Text content and instructions for how to use the content with the template.
- Token limit: ~100,000 minus template tokens.
- Can include image URLs inline.
- **Medical ed guidance**: Describe what content to swap in. E.g., `"Replace the deep sea content with: [clinical case study text]"`

### Optional Parameters
- `themeId`, `folderIds`, `exportAs`, `sharingOptions` — same as text generation.
- `imageOptions` — new images match the template's image source by default. Override with `imageOptions.model` and `imageOptions.style` if source is `aiGenerated`.

---

## Endpoint: GET /v1.0/generations/{id}

Poll for generation status. Returns `status`: `pending` | `completed` | `failed`.
On completion: `gammaUrl`, `exportUrl` (if `exportAs` was set), credit usage.

## Endpoint: GET /v1.0/themes

List workspace themes. Returns `id`, `name`, `type`, `colorKeywords`, `toneKeywords`.

## Endpoint: GET /v1.0/folders

List workspace folders. Returns `id`, `name`.
