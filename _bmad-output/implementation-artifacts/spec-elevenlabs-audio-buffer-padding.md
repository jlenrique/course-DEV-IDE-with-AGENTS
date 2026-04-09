---
title: 'ElevenLabs audio buffer padding'
type: 'feature'
created: '2026-04-09'
status: 'in-review'
baseline_commit: '56b696132fdce01080d5390bff8f609b884220b0'
context: ['docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md']
---

<frozen-after-approval reason="human-owned intent -- do not modify unless human renegotiates">

## Intent

**Problem:** ElevenLabs narration clips are generated without a configurable lead-in or lead-out buffer, and the operator cannot confirm or adjust padding before synthesis.

**Approach:** Add a governed audio buffer option (default 1.5s on both ends), surface it during voice preview and selection, and apply it to each narrated clip during manifest synthesis with VTT cue offsets and duration updates.

## Boundaries & Constraints

**Always:** Preserve narration text and voice selection logic; apply buffering post-synthesis using ffmpeg; default to 1.5s unless the operator overrides; store the operator-confirmed buffer in the voice selection output; offset VTT cues by the lead-in buffer; update `narration_duration` to include lead-in and tail padding.

**Ask First:** Change the default buffer away from 1.5s, introduce asymmetric start/end buffers, or apply buffering to non-narration audio (SFX, music, or final mixes).

**Never:** Regenerate narration text, reorder segments, skip buffering when a non-zero buffer is requested, or bypass hash verification in the voice selection workflow.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Default buffer | No override provided | Each clip gets 1.5s lead-in and 1.5s tail; VTT cues offset by +1.5s; `narration_duration` includes buffers | N/A |
| Operator override | `--audio-buffer-seconds 0.75` or value chosen in voice selection | Buffer uses override for all clips; VTT offset by 0.75s; duration reflects override | N/A |
| Zero buffer | `--audio-buffer-seconds 0` | No padding applied; VTT and duration unchanged | N/A |
| Invalid buffer | Negative buffer value | Abort before synthesis and do not write audio or VTT | Fail closed with ValueError |
| Missing ffmpeg | Buffer requested and ffmpeg not resolvable | Abort before processing any clip | Fail closed with clear error |

</frozen-after-approval>

## Code Map

- `skills/elevenlabs-audio/scripts/elevenlabs_operations.py` -- CLI args, voice preview/selection, manifest narration generation, VTT writing; add buffer validation and post-processing
- `skills/elevenlabs-audio/scripts/tests/test_elevenlabs_operations.py` -- unit tests for buffer validation and VTT offset behavior
- `state/config/style_guide.yaml` -- ElevenLabs defaults; add `audio_buffer_seconds`
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` -- Prompt 11/12 operator guidance; add buffer confirmation and CLI flag
- `scripts/utilities/ffmpeg.py` -- ffmpeg resolution utility used by buffer padding

## Tasks & Acceptance

**Execution:**
- [x] `skills/elevenlabs-audio/scripts/elevenlabs_operations.py` -- add `audio_buffer_seconds` handling for voice preview, voice selection output, and manifest synthesis; validate non-negative values; apply ffmpeg padding; offset VTT cues; update `narration_duration` -- ensures operator-confirmed buffers are enforced end to end
- [x] `state/config/style_guide.yaml` -- add `audio_buffer_seconds: 1.5` under ElevenLabs tool defaults -- establishes governed default
- [x] `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` -- add operator confirmation step for buffer and include `--audio-buffer-seconds` in Prompt 11/12 guidance -- codifies HIL requirement
- [x] `skills/elevenlabs-audio/scripts/tests/test_elevenlabs_operations.py` -- add tests for negative buffer validation, zero-buffer no-op, and VTT offset with buffer -- protects regressions

**Acceptance Criteria:**
- Given the operator confirms a buffer during voice selection, when manifest synthesis runs with `--voice-selection`, then the buffer in `voice-selection.json` is used for all clips and recorded in updated manifest fields.
- Given no override is provided, when voice selection is created, then `audio_buffer_seconds` defaults to 1.5 and is preserved through synthesis.
- Given a non-zero buffer, when narration is generated, then audio files are padded and VTT cues are shifted by the lead-in buffer.
- Given a negative buffer, when any ElevenLabs command is executed, then the run fails before any synthesis or file writes.

## Spec Change Log

## Design Notes

Use `scripts.utilities.ffmpeg.resolve_ffmpeg_binary` to add silence before and after each clip. Apply padding after ElevenLabs returns audio and alignment, then update VTT cues by the lead-in seconds only. Update `narration_duration` by adding lead-in and tail seconds to the original duration.

## Verification

**Commands:**
- `c:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/.venv/Scripts/python.exe -m pytest skills/elevenlabs-audio/scripts/tests/test_elevenlabs_operations.py` -- expected: PASS
