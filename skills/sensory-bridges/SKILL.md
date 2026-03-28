---
name: sensory-bridges
description: Shared perception infrastructure converting multimodal artifacts into structured agent-interpretable representations. Use when any agent needs to perceive images, audio, PDF, PPTX, or video.
---

# Sensory Bridges

## Overview

Shared skill providing modality-specific perception scripts that convert non-text artifacts into structured, schema-conformant representations any agent can interpret. Implements the Sensory Horizon principle: an agent cannot verify what it cannot perceive.

## Modality Inventory

| Modality | Bridge Script | Input | Primary Use | Perception Type |
|----------|--------------|-------|-------------|----------------|
| **PPTX** | `pptx_to_agent.py` | .pptx files | G3 text verification (deterministic) | Deterministic |
| **Image** | `png_to_agent.py` | .png, .jpg | G3 visual/layout verification | Agentic (LLM vision) |
| **Audio** | `audio_to_agent.py` | .mp3, .wav | G5 spoken content verification | Deterministic (STT API) |
| **PDF** | `pdf_to_agent.py` | .pdf | G0 source extraction verification | Deterministic |
| **Video** | `video_to_agent.py` | .mp4, .webm | G6 composition verification | Hybrid (ffmpeg + STT) |

## Invocation

All bridges follow the same pattern:

```python
from skills.sensory_bridges.scripts.bridge_utils import perceive

result = perceive(
    artifact_path="path/to/file.pptx",
    modality="pptx",
    gate="G3",
    requesting_agent="fidelity-assessor"
)
# result is a dict conforming to the perception response schema
```

## References

- `references/perception-schema.md` — Canonical request/response JSON schema
- `references/perception-protocol.md` — Five-step protocol all consuming agents must follow
- `references/confidence-rubric.md` — Modality-specific calibration for HIGH/MEDIUM/LOW
- `references/validator-handoff.md` — How bridge outputs feed Fidelity Assessor and Quinn-R

## Key Design Decisions

- **PPTX is the primary path for G3 text verification** — deterministic extraction of exact text objects, no OCR confidence issues
- **Image bridge supplements PPTX** — provides visual/layout assessment where PPTX extraction shows structure but not rendering
- **Audio bridge uses ElevenLabs Scribe v2 STT** — word-level timestamps, keyterm prompting for medical terminology, ≤5% WER for English
- **Video bridge accepts video files directly** via ElevenLabs STT (which supports video input) plus ffmpeg for keyframe extraction
- All bridges return the canonical perception schema — no free-form output
