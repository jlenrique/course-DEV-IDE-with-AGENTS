# Client-approved Gamma UI settings (exemplar screenshot)

Captured from the **approved exemplar** workflow. Workspace copy:

`assets/c__Users_juanl_AppData_Roaming_Cursor_User_workspaceStorage_e9704733d6441caf77330101e4df18be_images_image-3b1c35c9-ffce-44cd-8a70-fce83b419994.png`

Use this as the **source of truth** for matching look-and-feel on APC / HIL decks.

## Visuals

| UI control | Exemplar value |
|------------|----------------|
| Theme | **2026 HIL APC…** (`njim9kuhfnljvaa` in API) |
| Image source | **AI Images** → `imageOptions.source: "aiGenerated"` |
| AI image model | **Recraft V3** → `imageOptions.model: "recraft-v3"` (20 credits/image per Gamma docs; not `recraft-v3-svg`, not `recraft-v4-svg`) |
| Image art style | **Line drawing** (5th style tile in UI) |
| Add extra keywords | *(empty)* |
| Keyword chips | Not using bold/concise/monochrome/flat chips in exemplar |

## Text

| UI control | Exemplar value |
|------------|----------------|
| Mode | **Condense** → `textMode: "condense"` |
| Amount of text | **Minimal** → `textOptions.amount: "brief"` (closest API enum to “minimal”) |
| Output language | **English (US)** → `textOptions.language: "en"` |

## Format

| UI control | Exemplar value |
|------------|----------------|
| Format | **Presentation** → `format: "presentation"` |
| Layout | **Default** → *(no override unless Gamma exposes `cardOptions` layout)* |
| Card design mode | **Classic** — “Flexible cards with editable text, images, and layout blocks.” → *May be UI-only; not confirmed on public `POST /generations` schema. If generation differs, reproduce final mile in Gamma app.* |

## Generation scope

| UI control | Exemplar value |
|------------|----------------|
| Cards | **10 cards** → `numCards: 10` + `cardSplit: "inputTextBreaks"` when using `---` breaks |

---

## API: `imageOptions.style` for “Line drawing”

Gamma’s web UI uses preset art styles; the REST API uses a **string** on `imageOptions.style`. If a preset ID is undocumented, Gary uses a **literal line-art description** and/or Recraft line-art tokens (verify per generation):

- Descriptive fallback: `Line drawing, clean black ink lines on white, minimal fill, editorial medical infographic, no shading, no photorealism`
- If supported by your workspace: try Recraft-style tokens such as `vector_illustration/line_art` (confirm in Gamma developer docs / support — **not guaranteed**).

**Gary rule:** For **this client**, prefer **`recraft-v3` + line-drawing style** over `recraft-v4-svg`, `flux-2-pro`, or auto model unless explicitly overridden.
