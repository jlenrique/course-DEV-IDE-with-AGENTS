# Context Envelope Schema

Defines the delegation contract between Marcus (sender) and Kira (receiver) for instructional video generation.

## Inbound Envelope (Marcus ? Kira)

```yaml
schema_version: "1.0"

# REQUIRED
production_run_id: "C1-M1-P1-VID-001"
video_type: "concept-visualization"      # b-roll | concept-visualization | image-to-video-transition | lip-sync-overlay | section-bridge
instructional_purpose: "Show the divergence from clinical reactor to systemic innovator"
learning_objectives:
  - "Define the innovation mindset and connect clinical competencies to innovation frameworks"

# OPTIONAL
module_lesson: "C1 > M1 > Slide 1"
user_constraints:
  - "Keep it visually restrained"
  - "Medical blues and teal only"
style_bible_sections:
  - "Color Palette"
  - "Visual Tone"
source_assets:
  slide_png: "course-content/staging/.../slide.png"
  narration_audio: null
  presenter_image: null
  bridge_graphic: null
target_duration: "5"
run_mode: "default"
negative_prompt_overrides:
  - "no text overlays"
  - "no watermarks"
```

### Required Field Rules

| Field | Required | Notes |
|-------|:--------:|-------|
| `production_run_id` | yes | Unique run identifier |
| `video_type` | yes | Must map to a known type in content-type-mapping.md |
| `instructional_purpose` | yes | Why this clip exists in the lesson |
| `learning_objectives` | yes | Kira never generates without clear pedagogical grounding |

## Outbound Return (Kira ? Marcus)

```yaml
schema_version: "1.0"
production_run_id: "C1-M1-P1-VID-001"
status: "success"                        # success | revision_needed | failed | plan_only
artifact_paths:
  - "course-content/staging/story-3.3-samples/V2-pathway-concept.mp4"
video_operation: "text2video"            # text2video | image2video | lip-sync | extend
generation_choices:
  model_name: "kling-v1-6"
  mode: "std"
  duration: "5"
  aspect_ratio: "16:9"
  negative_prompt:
    - "text overlays"
    - "watermarks"
quality_assessment:
  motion_clarity: "strong"
  educational_focus: "strong"
  professionalism: "strong"
  risks:
    - "minor background drift in final second"
recommendations:
  - "Usable as-is for Slide 1 concept overlay"
errors: []
```

### Return Rules

- `artifact_paths` is empty if generation failed or if Kira returned a plan only
- `status: plan_only` is used when a required source asset is missing but Kira can still specify the next step
- `generation_choices` always records the exact model, mode, duration, and exclusions used
- `quality_assessment` is Kira's self-assessment before Quinn-R review
