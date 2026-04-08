# Audio Direction

## Default Production Posture

- Warm professionalism
- Measured pace
- High intelligibility
- Minimal performative excess

## Voice Selection Rules

- Use the style-guide default voice unless the manifest sets `voice_id` for a segment.
- Before any ElevenLabs synthesis spend, support a preview-only HIL checkpoint using existing catalog sample links.
- For an existing presentation, carry forward the previously approved lesson voice as the anchor candidate when available.
- For a new presentation, anchor the preview set on the style-guide default voice.
- Present exactly three previewable candidates per round:
  - anchor voice (previously used presentation voice or style-guide default)
  - two APP-selected alternatives based on presentation attributes
- If the operator supplies an ideal voice description instead, replace the standard round with three description-led recommendations from the catalog.
- If dialogue is being generated, ensure distinct voice assignments for different speakers.
- If the requested voice feels too stylized for physician-facing instruction, recommend a plainer alternative to Marcus.
- Treat `state/config/elevenlabs-voice-profiles.yaml` as the governed tuning surface for how APP ranks catalog voices; do not scatter ad hoc heuristics across prompts.

## Preview Output Rules

- Every candidate must include `voice_id`, display name, and a catalog `preview_url`.
- Preview links must point to existing ElevenLabs catalog samples, never to newly generated audio.
- Candidate rationales should explain audience fit and intelligibility, not just metadata labels.
- Record the operator's final choice separately from the locked Pass 2 package so voice selection does not reopen Storyboard B.
- If the operator selects a non-primary candidate, require an explicit override reason before downstream synthesis.
- If fewer than three previewable catalog voices are available, stop and return the blocker rather than improvising candidates or generating fresh samples.

## Self-Assessment Dimensions

- Pronunciation accuracy
- Pace suitability
- Tone fit for audience
- Continuity across adjacent segments
- Timing completeness (audio + VTT)
- Preview candidate quality and preview-link availability before synthesis
