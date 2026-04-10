# Optimization Patterns

## Default Narration Pattern

Use these defaults unless Marcus or the style guide overrides them:

```yaml
model_id: eleven_multilingual_v2
stability: 0.5
emotional_variability: 0.5
similarity_boost: 0.75
style: 0.0
speed: 1.0
pace_variability: 0.05
output_format: mp3_44100_128
```

## Narrated Slide Sequence

- Use `text_to_speech_with_timestamps` for all production narration.
- Write both `.mp3` and `.vtt`.
- Treat `normalized_alignment` as the preferred VTT source when present.
- Use `previous_request_ids` / `next_request_ids` when Marcus is stitching a sequence and request ids are available.

## Timing Guidance

- Educational target pace: 130-170 WPM.
- Let Quinn-R validate actual pace against `narration_duration`.
- If a segment feels rushed because the script is too short for its intended runtime, revise the script first.
- Use `speed` only for mild delivery nudges, not to force exact clip lengths.
- Lower `stability` broadens emotional range; the pipeline-level `emotional_variability` abstraction maps onto that behavior when raw `stability` is not set directly.

## Continuity Guidance

- Use the same `voice_id`, `model_id`, and core voice settings across a continuous lesson sequence.
- Prefer continuity metadata over ad hoc wording tricks when regenerating a middle segment.
