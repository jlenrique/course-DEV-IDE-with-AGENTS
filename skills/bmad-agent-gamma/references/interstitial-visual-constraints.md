---
title: Interstitial Visual Constraints Library
description: Locked Gamma prompt constraints per interstitial type (reveal, emphasis-shift, bridge-text, simplification, pace-reset) to prevent decorative drift and enforce head-slide inheritance.
---

# Interstitial Visual Constraints (Gamma)

Purpose: lock Gary’s Gamma parameters for the five canonical interstitial types so clustered runs inherit the head slide’s visual DNA and never introduce decorative drift. This library overrides general parameter recommendation for interstitial cards only. Downstream prompt construction (Story 21-2) must treat these as **non-overridable** unless the brief is revised.

## Global Rules (all interstitial types)
- Inherit from head: palette, accent color, background treatment, typography, theme/style preset.
- `numCards: 1`, `imageOptions.source: ai_generated` **only when** a visual element is allowed; otherwise `imageOptions.source: none`.
- `textMode: preserve` unless the template below states `custom`.
- Hard cap element counts per type (see below). No templates, stickers, stock-photo collage, or extra text boxes beyond the brief.
- Layout: single column unless specified; never multi-column for interstitials.
- Additional instructions templates below are **locked**; prepend only the brief’s type-specific content (e.g., isolation target) — do not append extra flair.

## Locked Parameters by Type

| Type | textMode | imageOptions.source | Element cap | Layout | AdditionalInstructions (locked template) |
|------|----------|---------------------|-------------|--------|------------------------------------------|
| reveal | preserve | ai_generated | ≤2 visual elements (one focal) | single column | “Focus on a single focal element that reveals the head slide’s core concept. Use the head accent color as the highlight. No extra text boxes.” |
| emphasis-shift | preserve | none | text-only | single column | “Isolate one key text block from the head slide. Suppress all other text. Use head accent color to emphasize only that block.” |
| bridge-text | preserve | none | text-only | single column | “Large single-phrase bridge line centered. No imagery. Maintain head background atmosphere.” |
| simplification | preserve | ai_generated | 1 data series max | single column | “Show one simplified data series only. No multi-column, no embellishment. Use head palette; avoid decorative icons.” |
| pace-reset | custom (short) | ai_generated or none (icon/whitespace) | 0–1 minimalist element | single column | “Minimal reset card. Either a single neutral icon or clean whitespace with a small anchor mark in head palette undertone. No text blocks.” |

## Per-Type Details

### reveal
**Inherit from head:** palette, accent color, background treatment, typography.  
**Include (locked):** `textMode: preserve`; `imageOptions.source: ai_generated`; ≤2 visual elements with one clear focal; single-column layout; `additionalInstructions` template above.  
**CANNOT include:** secondary illustrations, extra text boxes, decorative gradients beyond head background, multi-column layout.

### emphasis-shift
**Inherit from head:** accent color, typography, spacing.  
**Include (locked):** `textMode: preserve`; `imageOptions.source: none`; isolate one text block from the head; single-column; `additionalInstructions` template above.  
**CANNOT include:** imagery, multiple emphasized blocks, drop shadows, badges, banners.

### bridge-text
**Inherit from head:** atmospheric background, palette, typography.  
**Include (locked):** `textMode: preserve`; `imageOptions.source: none`; single large phrase; centered single-column layout; `additionalInstructions` template above.  
**CANNOT include:** photos/illustrations/icons, bullets, data tables, secondary text.

### simplification
**Inherit from head:** palette, accent color, typography, chart style.  
**Include (locked):** `textMode: preserve`; `imageOptions.source: ai_generated`; 1 data series only; disable multi-column; `additionalInstructions` template above.  
**CANNOT include:** multiple charts, multi-series visuals, pictograms, background photos, callout stickers.

### pace-reset
**Inherit from head:** palette undertone, typography scale for any minimal mark.  
**Include (locked):** `textMode: custom` (short); `imageOptions.source: ai_generated` when an icon is used, otherwise `none`; 0–1 minimalist element; single-column; `additionalInstructions` template above.  
**CANNOT include:** body text, lists, charts, photos, gradients stronger than head undertone, decorative frames.

## Implementation Notes for Story 21-2
- Treat these as hard overrides in prompt construction. Merge style guide defaults, then replace fields with the locked values above for interstitial cards.
- Map element caps to `numCards=1` and constrain visual density in `additionalInstructions`; do not request more than one card per interstitial.
- When `imageOptions.source: none`, omit image generation fields entirely to avoid Gamma adding imagery.
- For clustered runs, keep cluster metadata untouched; these constraints only affect visual parameters.

## References
- `skills/bmad-agent-content-creator/references/interstitial-brief-specification.md`
- `skills/bmad-agent-gamma/references/parameter-recommendation.md`
- `skills/bmad-agent-gamma/references/style-guide-integration.md`
- `state/config/gamma-style-presets.yaml`
