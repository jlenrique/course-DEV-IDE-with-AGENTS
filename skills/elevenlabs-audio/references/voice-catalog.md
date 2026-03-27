# Voice Catalog

Use the style guide's `tool_parameters.elevenlabs.default_voice_id` as the lesson-level default unless Marcus or the segment manifest overrides it.

## Selection Heuristics

| Use Case | Voice Qualities | Notes |
|----------|-----------------|-------|
| Standard lesson narration | Warm, credible, mid-career authority | Default production path |
| Complex explanatory content | Calm, deliberate, low-hype | Prefer intelligibility over personality |
| Case discussion | Confident but conversational | Works for narrated clinical reasoning |
| Dialogue | Distinct voices with clear contrast | Use segment-level `voice_id` overrides |

## Decision Rules

- Favor voices that remain clear at 130-170 WPM.
- Avoid novelty or highly stylized voices for physician-facing content.
- When a segment-level `voice_id` exists in the manifest, use it for that segment only.
- When no override is provided, fall back to the style-guide default.
