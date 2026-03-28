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

## Preset Schema

```yaml
- name: hil-2026-apc-nejal           # Unique key (kebab-case)
  description: "..."                   # What this look-and-feel is for
  scope: "*"                           # "*", "C1", "C1 > M1", "C1 > M1 > L3"
  theme_id: njim9kuhfnljvaa           # Gamma API theme ID
  theme_name: "2026 HIL APC Nejal"    # Human-readable (display only)
  parameters:                          # Gamma API params applied at cascade level 3
    # --- Text ---
    textMode: generate                 # generate | condense | preserve
    textOptions:
      amount: detailed                 # brief | concise | detailed | extensive (maps to Gamma UI text amount)
      language: en

    # --- Visuals ---
    imageOptions:
      source: aiGenerated
      model: nano-banana-2-mini        # AI image model (from Gamma model picker)
      style: illustration              # Art style tile (Photo, Illustration, Abstract, 3D, etc.)
      keywords:                        # Extra keywords for image consistency (Gamma UI keyword chips)
        - vector
        - minimalist
        - flat-color
        - linework
        - bold

    # --- Layout ---
    cardOptions:
      dimensions: "16x9"
    format: presentation
    formatVariant: classic             # UI card design mode (classic | traditional | modern); may be UI-only

    # --- Generation defaults ---
    numCards: 10                        # Default card count (overridable by content-type or envelope)
    additionalInstructions: >-         # Base instructions ALWAYS applied; concatenated (not replaced)
      Keep the style of all the images uniform.

  provenance:
    source: exemplar-match             # pilot-run | exemplar-match | user-defined | gary-proposed
    established: "2026-03-27"
    notes: "..."
  version: 2
```

### Field Notes

- **`imageOptions.keywords`**: Stored as a list in the preset for clarity. At flatten time, keywords are appended to the `imageOptions.style` string (comma-separated) for API compatibility, since the Gamma API doesn't have a separate keywords parameter.
- **`formatVariant`**: Captures the Gamma UI's card design mode (Classic, Traditional, Modern). This may be UI-only — no confirmed API mapping. Stored as design intent; Gary includes it in `additionalInstructions` if needed.
- **`numCards`**: Preset-level default. Overridden by content-type-mapping (`numCards: auto` for lecture decks, `3-5` for case studies, etc.) and by the context envelope.
- **`additionalInstructions`**: Uses **concatenation**, not replacement. The preset provides a base instruction; content-type-specific and envelope instructions are appended. This ensures "keep the style uniform" always fires while allowing "one concept per card" to be added for lecture decks.

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
