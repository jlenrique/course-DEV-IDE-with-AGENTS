# Context Envelope Schema

Defines the contract between Marcus (sender) and the Voice Director (receiver).

## Inbound Envelope (Marcus -> Voice Director)

```yaml
schema_version: "1.0"
production_run_id: "C1-M1-L1-RUN-001"
content_type: "narrated-lesson"
module_lesson: "C1 > M1 > L1"
segment_manifest: "course-content/staging/C1-M1-L1/manifest.yaml"
script_path: "course-content/staging/C1-M1-L1/narration-script.md"
voice_id: null
previous_request_ids: []
next_request_ids: []
user_constraints: []
run_mode: "default"
```

## Outbound Return (Voice Director -> Marcus)

```yaml
schema_version: "1.0"
production_run_id: "C1-M1-L1-RUN-001"
status: "success"
artifact_paths:
  - "course-content/staging/C1-M1-L1/audio/seg-01.mp3"
  - "course-content/staging/C1-M1-L1/captions/seg-01.vtt"
narration_outputs:
  - segment_id: "seg-01"
    request_id: "req-123"
    narration_duration: 8.2
    narration_file: "course-content/staging/C1-M1-L1/audio/seg-01.mp3"
    narration_vtt: "course-content/staging/C1-M1-L1/captions/seg-01.vtt"
parameter_decisions:
  voice_id: "voice-abc"
  model_id: "eleven_multilingual_v2"
  output_format: "mp3_44100_128"
recommendations: []
errors: []
```
