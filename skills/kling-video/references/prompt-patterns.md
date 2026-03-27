# Kling Prompt Patterns

Effective prompt structures for educational video generation in this repo. These patterns are grounded in the live-tested Kling pipeline and the approved C1-M1 validation set.

## Core Rule

Prompt what the learner should **see**, how the scene should **move**, and what the motion should **teach**. The best Kling prompt is not a screenplay - it is a visually specific, instructionally purposeful scene description.

## Standard Prompt Shape

For most clips, build prompts in this order:
1. **Scene / subject**
2. **Motion**
3. **Camera behavior**
4. **Visual tone**
5. **Color / style-bible alignment**
6. **Negative prompt exclusions**

## Default Negative Prompt Set

Use these unless the request explicitly needs something different:
- text overlays
- watermarks
- cartoon style
- exaggerated facial movement
- chaotic camera movement
- irrelevant background subjects

## Clip-Type Patterns

### 1. Hospital / Clinic B-roll

Use for atmosphere, urgency, and operational realism.

**Pattern**
> [professional healthcare environment], [human activity], [subtle camera movement], [cool medical palette], [credible professional tone]

**Example**
> Modern hospital corridor with clinicians moving through frame, soft natural light, shallow depth of field, subtle camera drift, cool medical blues and clean whites, professional atmosphere.

### 2. Concept Visualization

Use for frameworks, pathways, system transitions, and abstract instructional ideas.

**Pattern**
> [clean visual metaphor] on [restrained background], [explicit transition or transformation], [smooth motion], [corporate medical aesthetic]

**Example**
> A clean dark-navy background with a straight clinical workflow line that splits into a branching innovator pathway marked by glowing teal nodes. Smooth motion, restrained healthcare design aesthetic.

**Rhythm guidance**
- Start calm
- Make the transition visible
- Land clearly on the new state

### 3. Slide-to-Video Transition

Use when Gary already owns the static visual and the goal is to add motion, not redesign.

**Pattern**
> Add [subtle camera or depth motion] to this slide while preserving composition, hierarchy, typography, and all text relationships.

**Example**
> Add a subtle push-in and layered depth motion to this slide, preserving all layout relationships and typography. No new visual elements.

### 4. Talking-Head / Lip-Sync Overlay

Use for presenter presence, authority, and emotional credibility. The audio leads the performance.

**Pattern**
> [professional presenter framing], [natural eye contact], [restrained gestures], [credible healthcare authority], [softly lit environment]

**Example**
> Professional talking-head delivery in a softly lit office, natural eye contact, restrained gestures, credible healthcare leadership presence.

**Rhythm guidance**
- Let the audio carry the pacing
- Keep visual movement restrained
- Favor credibility over performance

### 5. Section-Bridge Transition

Use to orient the learner between major blocks.

**Pattern**
> [clean transition visual], [clear directional movement], [minimal complexity], [professional palette], [short duration]

**Example**
> A minimal dark-navy bridge graphic connecting Module 1 to Module 2 with a smooth lateral sweep and restrained teal accent motion.

## Validation Set Mapping

| Validation Clip | Best Pattern |
|-----------------|-------------|
| V1 Hospital B-roll | B-roll pattern |
| V2 Clinical-to-innovator pathway | Concept visualization pattern |
| V3 Animated Gary slide | Slide-to-video transition pattern |
| V4 Knowledge-explosion timeline | Concept visualization pattern with stronger pacing |
| V5 Talking-head overlay | Talking-head / lip-sync pattern |
| V6 Module bridge | Section-bridge transition pattern |
