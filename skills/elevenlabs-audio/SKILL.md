---
name: elevenlabs-audio
description: ElevenLabs audio mastery skill with narration, timestamps, pronunciation dictionary, dialogue, SFX, and music wrappers. Invoked by the Voice Director agent for all ElevenLabs API operations.
---

# ElevenLabs Audio Mastery

## Purpose

Provides complete ElevenLabs tool expertise for the Voice Director specialist. This skill handles narration generation, timestamp extraction, WebVTT companion output, manifest-driven narration write-back, pronunciation dictionary creation, dialogue generation, sound effects, and music composition through the shared `ElevenLabsClient`.

This is the **skill layer** in the repo's three-layer architecture:
Voice Director (agent - judgment) -> elevenlabs-audio (skill - tool expertise) -> ElevenLabsClient (API client - connectivity)

## Key Paths

| Path | Purpose |
|------|---------|
| `./references/voice-catalog.md` | Voice-selection guidance for medical education contexts |
| `./references/optimization-patterns.md` | Default parameter patterns for narration, continuity, and pacing |
| `./references/pronunciation-management.md` | Pronunciation dictionary workflow and PLS guidance |
| `./references/sound-design-patterns.md` | SFX/music usage patterns and conservative production rules |
| `./scripts/elevenlabs_operations.py` | Agent-level wrapper around `ElevenLabsClient`, including manifest-driven batch narration |

## Script Index

| Script | Purpose | Invoked By |
|--------|---------|------------|
| `elevenlabs_operations.py` | Load style-guide defaults, generate narration + VTT, process segment manifests, build/upload pronunciation dictionaries, generate dialogue/SFX/music, and return structured results | Voice Director (`VR`, `PM`, `AQ`, `SD`) |

## Supported Operations

| Operation | Client Method | When |
|-----------|---------------|------|
| Narration with timestamps | `text_to_speech_with_timestamps()` | Primary instructional narration path |
| Manifest-driven narration | `generate_manifest_narration()` | Standard Marcus -> ElevenLabs production path |
| Pronunciation dictionaries | `create_pronunciation_dictionary_from_file()` / `list_pronunciation_dictionaries()` | Medical terminology support |
| Dialogue | `text_to_dialogue()` | Case-study multi-speaker outputs |
| Sound effects | `text_to_sound_effect()` | Transition and emphasis cues |
| Music | `generate_music()` | Intro/outro or low-bed underscore when explicitly desired |

## Operating Rules

- Always prefer style-guide defaults from `state/config/style_guide.yaml` before inventing per-request settings.
- Narration is the primary path. Dialogue, SFX, and music are secondary and should never obscure instructional clarity.
- For narrated lesson production, return both audio and timestamp-derived VTT output.
- Use pronunciation dictionaries for repeated medical terminology rather than one-off prompt hacks.
- Continuity across multi-slide sequences should use `previous_request_ids` / `next_request_ids` when Marcus provides them.
- Output files belong in `course-content/staging/` unless Marcus explicitly sets a different path.
