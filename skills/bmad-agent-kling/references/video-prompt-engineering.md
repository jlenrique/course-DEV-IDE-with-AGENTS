# Video Prompt Engineering

Kira turns educational intent into strong Kling prompts.

## Core Rule

Describe what the learner should see and feel, not just the topic. Strong prompts specify subject, motion, camera behavior, atmosphere, and restraint.

## Prompt Structure

For most clips, structure prompts in this order:
1. **Scene / subject** — what is visible
2. **Motion** — what moves and how
3. **Camera behavior** — push-in, hold, drift, pan, etc.
4. **Visual tone** — professional, clinical, restrained, modern
5. **Color / aesthetic cues** — style bible alignment
6. **Negative prompt** — what to exclude

## Clip-Type Guidance

### B-roll
Keep prompts simple and concrete. Use a real environment, light motion, and minimal visual complexity.

**Good:**
- "Modern hospital corridor with clinicians moving through frame, cool medical blues, shallow depth of field, subtle camera drift, professional atmosphere."

### Concept Animation
Use visual metaphor with explicit structure. Avoid overloaded scenes.

**Good:**
- "A clean dark-navy background with a straight clinical workflow line that splits into a branching innovator pathway marked by teal nodes. Smooth motion, restrained corporate healthcare aesthetic."

**Rhythm note:**
- Even concept clips need emotional pacing. Use calm setup → visible shift → clear payoff. The learner should feel the transition, not just observe moving shapes.

### Image-to-Video Transition
Assume the source image already carries the visual composition. Prompt should focus on motion, not re-description.

**Good:**
- "Add subtle push-in motion and layered depth to this slide, preserving all layout relationships and typography."

### Lip-Sync Overlay
Prompt should focus on framing, professionalism, and facial naturalness. Let the audio lead the performance.

**Good:**
- "Professional talking-head delivery in a softly lit office, natural eye contact, restrained gestures, credible healthcare leadership presence."

**Rhythm note:**
- Talking-head clips should feel paced by thought, not by animation. Favor restrained gesture and natural pauses over theatrical movement.

## Negative Prompt Discipline

Default exclusions for professional course content:
- text overlays
- watermarks
- cartoon style
- exaggerated facial motion
- chaotic camera movement
- irrelevant background subjects

## Quality Self-Assessment Lens

After generation, assess:
- **Motion clarity** — is the motion understandable, not noisy?
- **Educational focus** — does the clip support the lesson rather than distract?
- **Professionalism** — would this fit naturally in a physician-facing course?
- **Risk** — any visual drift, artifacting, unnatural lip-sync, or thematic mismatch?
