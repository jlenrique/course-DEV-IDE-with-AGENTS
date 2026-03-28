# Perception Schema — Canonical Request/Response Format

All sensory bridge invocations use this schema. No free-form output is permitted.

## Request Schema

```yaml
artifact_path: string    # Absolute or project-relative path to the artifact file
modality: enum           # image | audio | pdf | pptx | video
gate: string             # Production gate identifier (G0–G6)
requesting_agent: string # Agent requesting perception (e.g., "fidelity-assessor", "irene")
purpose: string          # Brief description of why perception is needed (optional)
```

## Response Schema (Common Fields)

```yaml
schema_version: "1.0"
modality: enum                # Same as request
artifact_path: string         # Same as request
confidence: enum              # HIGH | MEDIUM | LOW (per confidence-rubric.md)
confidence_rationale: string  # Why this confidence level was assigned
perception_timestamp: string  # ISO-8601 UTC timestamp
```

## Modality-Specific Response Fields

### Image

```yaml
extracted_text: string            # All text visible in the image
layout_description: string       # Description of visual layout
visual_elements: list             # Identified visual elements [{type, description, position}]
slide_title: string               # Title text if identifiable
text_blocks: list[string]         # Individual text blocks on the slide
```

### Audio

```yaml
transcript_text: string           # Full transcript of spoken content
timestamped_words: list           # [{text, start_ms, end_ms, type, speaker_id}]
total_duration_ms: integer        # Total audio duration
wpm: float                       # Words per minute
pronunciation_flags: list         # Terms with potential pronunciation issues
language_code: string             # Detected language (ISO 639-3)
```

### PDF

```yaml
pages: list                       # [{page_number, text, is_scanned, char_count}]
total_pages: integer              # Total page count
scanned_pages: integer            # Count of detected scanned/OCR pages
```

### PPTX

```yaml
slides: list                      # [{slide_number, text_frames[], image_refs[], notes}]
total_slides: integer             # Total slide count
```

### Video

```yaml
keyframes: list                   # [{frame_index, frame_path, timestamp_ms}]
audio_transcript: string          # Full audio transcript
total_duration_ms: integer        # Total video duration
scene_changes: integer            # Number of detected scene changes
```

## Validation

Use `bridge_utils.validate_response(response_dict)` to check schema conformance.
All bridges must pass validation before returning results.
