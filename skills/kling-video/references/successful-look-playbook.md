# Kling Successful Look Playbook

Reusable look/feel recipes that are now proven or strongly supported by live validation in this repo.

## Purpose

This is the practical playbook for reproducing success, not just the factual matrix.

Use it when you want:

- a known-good starting prompt shape
- a known-good model/mode/duration choice
- a reminder of what source types work best for a given visual goal

Default baseline unless noted otherwise:

- model: `kling-v2-6`
- mode: `std`
- duration: `5`
- audio: silent-by-omission

Native-audio / SFX note:

- successful looks in this playbook are still defined against the validated silent lane
- native ambience / SFX is now part of the exploratory `3.0` Singapore-surface validation plan, but not yet a promoted reproducible pattern

## Audio Boundary

- this playbook's reusable production-safe looks assume silent output unless a look is explicitly marked `validation-only`
- any look involving Kling-native audio, SFX, or `3.0` should be treated as `validation-only` until separately promoted

## Top Validated Kling Looks

- `Static-to-life instructional graphic` via `image2video`
  Best current repo-safe use. Works especially well for pathway, split-screen, collaboration-circle, and conceptual stills. Preserve composition; add restrained depth and emphasis.
- `Beauty / fashion portrait close-up` via `text2video`
  Clean single-subject realism. Good for face stability, micro-motion, and lighting evaluation.
- `Luxury product / macro object` via `text2video`
  Strong for one-subject detail, reflections, and slow controlled camera motion.
- `Clinical hallway atmosphere` via `text2video`
  Good for healthcare mood and restrained environmental motion without story complexity.
- `Stylized 3D mascot idle` via `text2video`
  Good stylized-character probe; simple idle motion reads cleanly.
- `Anthropomorphic character comedy` via `text2video`
  Strong when the brief is simple and character-forward rather than choreography-heavy.
- `Whimsical hand-painted healthcare` via `text2video`
  Strong stylized mood-builder for reflective or transitional lesson moments.

Validated by:

- Gamma static-to-life suite: `G01-G04`
- Core motion slate: `K01-K10`
- style probe: `E01`

## Look 1: Static-To-Life Instructional Graphic

Best for:

- approved Gamma or Gary stills
- conceptual visuals
- pathway, split-screen, comparison, or collaborative diagrams

Source mode:

- `image2video`

What worked:

- restrained depth
- subtle directional emphasis
- preserving composition rather than redesigning the scene

Prompt shape:

> Bring this visual to life with restrained depth, gentle camera drift, and emphasis on the key conceptual relationships while preserving all text, icon, and layout relationships. No redesign and no new elements.

Avoid:

- strong zoom on text-heavy slides
- asking for new props or new people
- cinematic sequence language

## Look 2: Structured Graphic / Collaboration Motion

Best for:

- node-and-relationship visuals
- circle or network collaboration scenes
- roadmap or infographic stills with strong composition

Source mode:

- `image2video`

What worked:

- calm reveal rhythm
- slight relationship emphasis
- preserving node placement and conceptual balance

Prompt shape:

> Animate this structured graphic with subtle depth, gentle relationship emphasis, and a calm reveal rhythm while preserving all text, node placement, and conceptual clarity. No redesign.

## Look 3: Glamour / Beauty Close-Up

Best for:

- photoreal face close-ups
- soft editorial glamour
- hair/light/skin realism tests

Source mode:

- `text2video`
- or reference-driven if you later have a controlled source still

What worked:

- one subject
- micro-expression
- soft lighting
- calm camera drift

Prompt shape:

> Cinematic beauty close-up of a woman in soft editorial styling, luminous skin, delicate eyelashes, gentle hair movement, warm diffused studio lighting, shallow depth of field, calm micro-expression, slow camera drift, elegant glamour aesthetic, no text.

Avoid:

- strong acting beats
- choreography
- multiple subjects

## Look 4: Clean Fashion Portrait

Best for:

- editorial human portrait realism
- polished controlled motion
- wardrobe and pose stability

Source mode:

- `text2video`

What worked:

- poised subject
- one environment
- subtle breathing and eye focus shift
- refined lighting

Prompt shape:

> Editorial fashion portrait of a poised subject in a refined interior, subtle breathing and eye focus shift, soft camera drift, clean lighting, polished modern portrait realism, no text.

## Look 5: Luxury Product Macro

Best for:

- premium object/product feel
- reflective materials
- shallow depth of field
- elegant commercial motion

Source mode:

- `text2video`

What worked:

- one hero object
- styled surrounding materials
- slow push-in
- controlled shimmer and reflections

Prompt shape:

> Editorial luxury product macro shot of a premium object in a styled environment, glossy materials, warm rim light, shallow depth of field, slow elegant push-in, subtle reflection shimmer, refined commercial aesthetic, no text.

## Look 6: Clinical Hallway Atmosphere

Best for:

- healthcare mood
- realistic environmental motion
- narrated-video B-roll

Source mode:

- `text2video`

What worked:

- realistic hallway
- distant clinician movement
- restrained forward drift
- no storytelling complexity

Prompt shape:

> Modern hospital hallway at shift change, restrained camera drift forward, soft natural movement of clinicians in the distance, clean medical lighting, credible professional atmosphere, calm realistic healthcare tone, no text overlays.

## Look 7: Neon Cityscape

Best for:

- lighting
- wet reflections
- urban environment motion
- stylized atmosphere without character complexity

Source mode:

- `text2video`

What worked:

- one environment
- rain/wet pavement
- slow elevated drift
- ambient light shimmer

Prompt shape:

> Rainy neon city intersection at night, glowing signs reflected on wet pavement, slow elevated camera drift, gentle traffic motion and ambient light shimmer, cinematic urban atmosphere, no text.

## Look 8: Stylized 3D Mascot Idle

Best for:

- simple stylized character tests
- readable idle motion
- clean playful rendering

Source mode:

- `text2video`

What worked:

- one mascot
- tiny head turn
- breathing
- expressive eyes

Prompt shape:

> Stylized 3D mascot standing on a softly lit stage, subtle idle movement, gentle breathing, tiny head turn, expressive eyes, colorful backlights, clean playful character rendering, no text.

## Global Anti-Patterns

Do not default to:

- slow zoom on text-heavy slides
- multi-shot sequence language
- dramatic transformation
- adding new people or props to an approved still
- audio wording in production-safe probes
- text animation when legibility matters
- treating text-heavy slides as automatic `image2video` candidates

## Current Best Instructional Rule

If the approved still already communicates the lesson well, start with `image2video`.

If the still is text-heavy and the only motion idea is a slow push-in, prefer `static` or a different treatment.
