# Style Preset Library (SP Capability)

A **style preset** is a named, versioned set of Gamma API parameters that fully specifies a visual identity beyond what a Gamma theme alone controls. Themes set colors and typography; presets add image model, image style, text mode, text density, card dimensions, and base `additionalInstructions` — everything needed to **reproduce a specific look and feel reliably** across slides, lessons, modules, and courses.

Presets live in `state/config/gamma-style-presets.yaml` (git-versioned, human-readable).

---

## When to Use SP

- **Every production run.** Before generating, check whether a preset is associated with the selected theme or the current scope. If one exists, it feeds the parameter cascade automatically.
- **Theme selection (TP flow).** When the user picks a theme, Gary checks for a matching preset and reports what additional parameters it will apply.
- **First run for a new scope.** If no preset exists, Gary notes this and may propose one after a successful, user-approved run.
- **Cross-course / cross-client reuse.** A library of presets enables different courses or clients to select from curated visual identities without starting from scratch.

## When NOT to Use SP

- **Woodshed / exemplar reproduction.** Exemplar runs use explicit parameter control — presets would interfere with precise reproduction.
- **`parameters_ready: true` fast-path.** If the context envelope already carries a complete parameter set, skip preset lookup.

---

## Two Style Approaches

Presets support two approaches for image style specification. Gary selects based on the `approach` field:

### Approach A — Named `stylePreset` (proven, default)

Uses `imageOptions.stylePreset` with a named tile value (`illustration`, `lineArt`, `photorealistic`, `abstract`, `3D`). This is the **screenshot-exact configuration** — what you set in the Gamma Prompt Editor and got right. Use this as the default.

```yaml
approach: A
parameters:
  imageOptions:
    source: aiGenerated
    model: nano-banana-2-mini
    stylePreset: illustration        # Named API tile — style field IGNORED by API
    keywords:                        # Gary adds to additionalInstructions as hint
      - vector
      - minimalist
      - flat-color
      - linework
      - bold
```

**Flatten behavior**: `stylePreset` goes to API as-is. `keywords` become `_keywordsHint` (Gary may include in `additionalInstructions`). `style` field not sent.

### Approach B — `custom` stylePreset + text prompt (experimental)

Uses `imageOptions.stylePreset: custom` so the `style` text string drives generation. Requires a reference PNG for Marcus/Gary to study when crafting/refining the style prompt. Use `flux-kontext-pro` — designed for style-reference controlled generation.

```yaml
approach: B
parameters:
  imageOptions:
    source: aiGenerated
    model: flux-kontext-pro          # Best for style-reference matching
    stylePreset: custom              # Enables style field as prompt
    style: >-
      Line drawing illustration. Clean black ink lines on white background.
      Minimal fill, no shading, no photorealism. Editorial medical infographic
      style. Vector aesthetic with bold linework. Flat-color accents only.
    keywords:                        # Appended to style string at flatten time
      - vector
      - minimalist
    referenceImagePath: >-           # Gary reads this PNG to craft/refine style prompt
      course-content/staging/ad-hoc/.../1_Physician-as-Innovator.png
```

**Flatten behavior**: `style` + `keywords` are merged into a single style prompt string. `referenceImagePath` is preserved for Gary to read (not sent to API).

**Note on reference image upload (UI-only):** In the Gamma UI, uploading a reference PNG auto-sets the tile to `custom` and Gamma generates a style embedding from the image internally. This is **not yet available in the API**. `referenceImagePath` is a design-intent field — Gary reads the PNG and writes a precise `style` description. When Gamma adds API support for reference images, this field will map directly.

---

## Preset Schema

```yaml
- name: hil-2026-apc-nejal-A        # Unique key (kebab-case). Suffix -A or -B for approach.
  description: "..."
  approach: A                        # A (named stylePreset) | B (custom + text prompt)
  scope: "*"                         # "*", "C1", "C1 > M1", "C1 > M1 > L3"
  theme_id: njim9kuhfnljvaa
  theme_name: "2026 HIL APC Nejal"
  parameters:
    textMode: generate
    textOptions:
      amount: detailed               # brief | concise | detailed | extensive
      language: en
    imageOptions:
      source: aiGenerated
      model: nano-banana-2-mini
      stylePreset: illustration      # Approach A: named tile
      keywords: [vector, minimalist, flat-color, linework, bold]
      # stylePreset: custom          # Approach B: enables style string
      # style: "..."                 # Approach B: full style prompt
      # referenceImagePath: "..."    # Approach B: PNG for prompt crafting
    cardOptions:
      dimensions: "16x9"
    format: presentation
    formatVariant: classic
    numCards: 10
    additionalInstructions: >-
      Keep the style of all the images uniform.
  provenance:
    source: exemplar-match
    established: "2026-03-27"
    notes: "..."
  version: 1
```

### Field Notes

- **`imageOptions.stylePreset`**: The API field that maps to the UI tile buttons. When named (not `custom`), `style` is ignored by the API. Added to Gamma API Feb 27, 2026.
- **`imageOptions.keywords`**: Stored as a list. Approach A: becomes `_keywordsHint` (for `additionalInstructions` injection). Approach B: appended to `style` string.
- **`imageOptions.referenceImagePath`**: Approach B only. Design-intent field. Gary reads the PNG file to study the visual language and write/refine the `style` prompt. Not sent to API.
- **`formatVariant`**: UI card design mode (Classic, Traditional, Modern). May be UI-only. Stored as design intent.
- **`numCards`**: Preset-level default, overridden by content-type-mapping and context envelope.
- **`additionalInstructions`**: Concatenated across all cascade layers, not overridden.

---

## Resolution Order

Gary resolves a preset using `resolve_style_preset()` in `gamma_operations.py`:

1. **By name** — if the context envelope or Marcus specifies `style_preset: "hil-2026-apc-nejal"`, exact match.
2. **By theme ID** — if the user selected a theme via TP, find a preset whose `theme_id` matches.
3. **By scope** — find the most specific scope match for the current production context. Longer scope strings are more specific; `"*"` is the fallback.
4. **No match** — return empty dict; the cascade proceeds without a preset layer.

---

## Merge Position

Presets slot into the parameter cascade at **level 3 of 6**:

```
1. API defaults
2. Style guide (state/config/style_guide.yaml → tool_parameters.gamma)
3. STYLE PRESET  ← this capability
4. Content type template (content-type-mapping.md)
5. Context envelope overrides (Marcus delegation)
6. Gary per-request judgment
```

A preset value is overridden by anything at levels 4-6, **except `additionalInstructions`** which uses concatenation — all layers contribute fragments that are joined into a single instruction string. This means the preset's base instruction ("keep the style uniform") is always present, while content-type-specific additions ("one concept per card") and envelope additions are appended.

---

## Governance

- **User writes and approves presets.** The file is git-versioned; changes go through normal commit review.
- **Gary may propose new presets** after a successful, user-approved run. Proposals are presented to Marcus/user as: "This run used [theme + parameters]. Want me to save this as a named preset for future [scope] runs?"
- **No autonomous mutation.** Gary never writes to `gamma-style-presets.yaml` directly. Proposals go through HIL.
- **Version tracking.** Each preset has a `version` field, incremented on edits. This supports audit trail and rollback.

---

## Proposing a New Preset

After a successful run where the user approves the output (HIL Gate 2 pass):

```
🎯 This deck worked well with these settings:
   Theme: 2026 HIL APC Nejal (njim9kuhfnljvaa)
   Image model: recraft-v3, style: line-drawing
   Text: condense / brief

Want me to propose saving this as a named style preset?
If so, what name and scope? (e.g., "hil-2026-formal" for all courses,
or "c1-lecture-lineart" for Course 1 only)
```

---

## Validating Presets Against API Surface

Presets reference Gamma API parameters (image models, text modes) that may change over time. Gary should:

1. **On activation**, note the preset file's `version` fields.
2. **Before generation**, verify that key parameter values (especially `imageOptions.model`) are still valid by checking against `gamma-api-mastery/references/parameter-catalog.md` (refreshed by tech-spec-wrangler).
3. **If a parameter is stale**, report to Marcus: "Preset 'hil-2026-apc-nejal' references `recraft-v3` which is no longer in the Gamma model list. Recommend updating the preset."

This connects to the existing tech-spec-wrangler doc-refresh cycle — when API docs are refreshed, Gary can cross-check presets.

---

## Listing Presets

Gary presents available presets when:
- User asks "what style presets are available?"
- TP flow includes preset information alongside themes
- Marcus needs to select a visual identity for a new production run

Format:
```
📋 Available Style Presets:

1. [hil-2026-apc-nejal] — HIL 2026 APC branded deck
   Theme: 2026 HIL APC Nejal | Image: recraft-v3 line-drawing | Text: condense/brief
   Scope: * (all courses) | Version: 1
   ✅ ACTIVE — matches current theme selection

2. [example-client-photographic] — (future preset)
   ...
```
