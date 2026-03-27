# Slide Brief Template

**Pass 1 artifact** — produced before Gary generates slides. This brief tells Gary what each slide needs to accomplish pedagogically. Irene writes narration *after* Gary generates slides (Pass 2), ensuring narration complements Gary's actual output. Do not pre-write narration in this brief.

## Header

- **Lesson Plan Reference:** LP-{module_id}{lesson_id}
- **Brief ID:** SB-{module_id}{lesson_id}-{sequence}
- **Narration Script (Pass 2 — produced after Gary):** NS-{module_id}{lesson_id}-{sequence}
- **Learning Objective:** {specific objective this slide serves}
- **Bloom's Level:** {level}
- **Pass:** 1 (input to Gary's generation; narration written after Gary's output reviewed)

## Slide Specifications

### Slide {N}

**Content:**
{Primary text content for this slide — what appears on screen}

**Visual Guidance:**
- Layout: {two-column parallel | title-plus-body | three-column cards | data visualization | full-bleed image}
- Hero Element: {what draws the eye first}
- Visual Density: {minimal/sparse | balanced | data-rich}
- Image Guidance: {description of needed visual, or "no image — text focus"}

**Learning Purpose:**
{Why this slide exists in the sequence — what cognitive step it serves}

## Downstream Consumption — Gary (Gamma)

- **Suggested Parameters:**
  - `numCards`: {count}
  - `textMode`: {generate | condense | preserve}
  - `textOptions.amount`: {brief | medium | detailed}
  - `additionalInstructions`: {layout and constraint guidance for Gamma}
  - `imageOptions.source`: {aiGenerated | noImages | pexels}
- **Format:** presentation
- **Export:** PNG (production) or PDF (review)
- **Pairing Note:** Narration script NS-{id} is produced in Pass 2 *after* Gary's slides are approved. Gary uses this brief to generate slides; Irene then writes narration that complements what Gary actually produced.
- **Downstream Kira:** segments that need video animation should note `visual_mode: video` suggestion here so Kira knows which slides to animate after ElevenLabs provides durations.
  - `visual_mode`: static-hold | video (suggestion for segment manifest)
  - `visual_source`: gary | kira (suggestion)
