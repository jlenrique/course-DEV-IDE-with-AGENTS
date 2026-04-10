# Validator Handoff — Sensory Bridges to Consumers

Sensory bridge outputs are shared infrastructure consumed by multiple agents.
This document specifies which fields each consumer reads and how the handoff works.

## Architecture

```
Sensory Bridge Output (canonical perception schema)
        ↓                         ↓
Fidelity Assessor              Quinn-R
(source traceability)          (quality standards)
```

The bridges produce ONE output per artifact. Both the Fidelity Assessor and Quinn-R
read from the same perception response — no duplicate perception runs.

## Consumer Field Map

### Fidelity Assessor reads:

| Modality | Fields Used | Purpose |
|----------|-------------|---------|
| PPTX | `slides[].text_frames[]` | Verbatim text comparison against slide brief content_items |
| Image | `extracted_text`, `text_blocks[]` | Visual coverage verification, layout analysis |
| Audio | `transcript_text`, `timestamped_words[]` | Script-to-spoken comparison, word-level fidelity |
| PDF | `pages[].text`, `pages[].is_scanned` | Source extraction completeness, degraded source detection |
| Video | `audio_transcript`, `keyframes[]` | Composition fidelity, segment order verification |
| All | `confidence`, `confidence_rationale` | Gate threshold enforcement |

### Quinn-R reads:

| Modality | Fields Used | Purpose |
|----------|-------------|---------|
| PPTX | `slides[].text_frames[]` | Learning objective alignment, content density |
| Image | `layout_description`, `visual_elements[]`, `visual_complexity_level`, `visual_complexity_summary` | Brand consistency (colors, fonts), accessibility (contrast), narration-support burden |
| Audio | `wpm`, `total_duration_ms` | Audio quality metrics, pacing assessment |
| PDF | `total_pages`, `scanned_pages` | Source quality flag for upstream review |
| Video | `keyframes[]`, `scene_changes`, `temporal_event_density_level`, `temporal_event_density_summary` | Composition integrity, transition quality, motion-aware narration fit |

### Existing Deterministic Validators

Quinn-R's existing validators consume bridge outputs:

- `accessibility_checker.py` — reads image `layout_description` and `visual_elements[]` for contrast ratios, alt text presence
- `brand_validator.py` — reads image `visual_elements[]` for color/font compliance against style bible
- Reserved audio validator — reads audio `wpm`, `total_duration_ms` for quality metrics
- Reserved composition validator — reads video `keyframes[]`, `scene_changes` for assembly integrity

These validators are NOT replaced by sensory bridges. Bridges provide the **perception**;
validators provide the **judgment** on specific quality dimensions.

## Caching

Within a single production run, perception results for an artifact are cached.
If both the Fidelity Assessor and Quinn-R need to assess the same PNG,
the bridge runs once and both consumers read the cached result.

Cache key: `(artifact_path, modality)`. Cache scope: production run.

Implementation notes:

- Runtime cache utility: `skills/sensory-bridges/scripts/perception_cache.py`
- Dispatcher integration: `skills/sensory-bridges/scripts/bridge_utils.py::perceive(..., run_id=..., run_mode=...)`
- Cache storage path: `state/runtime/perception-cache/{run_id}.json`
- Cache lifecycle: run-scoped; clear at run completion/cancel for strict run isolation

Observability linkage:

- Cache hit/miss events are emitted through `skills/production-coordination/scripts/observability_hooks.py`
- Each event carries `run_mode` so downstream rollups can exclude ad-hoc runs from course progress metrics
