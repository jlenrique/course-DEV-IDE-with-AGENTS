# Voice Catalog

Use the style guide's `tool_parameters.elevenlabs.default_voice_id` as the lesson-level default unless Marcus or the segment manifest overrides it.
Use `state/config/elevenlabs-voice-profiles.yaml` for governed recommendation profiles and description-keyword tuning. Use `state/config/style_guide.yaml` only for mutable operational defaults such as the current lesson-default `voice_selection_profile` and `default_voice_id`.

Before narration generation, the preferred operator flow is:
- preview the previously approved lesson voice when this presentation already has one
- otherwise preview the style-guide default voice
- add exactly two APP-selected alternatives using presentation metadata
- if the operator describes an ideal voice instead, return three description-led recommendations from the ElevenLabs catalog

Samples must come from existing ElevenLabs catalog preview links. Do not generate ad hoc sample audio just to audition voices.

## Governed Preview Modes

- `continuity_preview` — use the previously approved lesson voice when a trusted prior voice-selection receipt exists; otherwise fall back explicitly to the style-guide default.
- `default_plus_alternatives` — for a new presentation, anchor on the style-guide default voice and add two APP-ranked alternatives.
- `description_driven_search` — when the operator describes the ideal narrator, rank three previewable catalog voices from that description plus presentation context.

Recommended artifacts:
- `voice-preview-options.json` — preview candidates, preview URLs, locked script/manifest hashes, and recommendation rationale
- `voice-selection.json` — the operator-approved `selected_voice_id`, notes, and any override reason

Fail-closed rule:
- Do not proceed to synthesis unless the selection receipt exists and identifies one approved voice for the lesson-level default.

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
- For preview rounds, require a catalog `preview_url`; voices without preview links are not HIL-ready candidates.
- When the operator approves a lesson-level voice, record it separately as voice-selection state and pass it into synthesis without mutating the locked Pass 2 script/manifest.
- If the operator selects a non-primary candidate, record an explicit override reason so continuity changes stay auditable.
