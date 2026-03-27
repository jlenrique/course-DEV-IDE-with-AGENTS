---
name: kling-video
description: Kling API video generation mastery skill with prompt patterns, model selection guidance, parameter catalog, and execution wrapper scripts. Invoked by Kira (bmad-agent-kling) for all Kling API operations.
---

# Kling Video Mastery

## Purpose

Provides complete Kling API tool expertise for Kira (Video Director). This skill handles all Kling API operations - generation, polling, download, and execution wrapping - and contains the prompt guidance, model selection logic, parameter documentation, and scripts Kira uses to produce educational video clips.

This is the **skill layer** in the three-layer architecture: Kira (agent - judgment) -> kling-video (skill - tool expertise) -> KlingClient (API client - connectivity).

## Key Paths

| Path | Purpose |
|------|---------|
| `./references/prompt-patterns.md` | Effective prompt structures for each educational video type |
| `./references/model-selection.md` | Model, mode, and duration tradeoffs with cost-aware guidance |
| `./references/parameter-catalog.md` | Complete live-tested Kling API parameter reference |
| `./scripts/kling_operations.py` | Agent-level KlingClient wrapper: submit, poll, extract, download, return structured results |

## Script Index

| Script | Purpose | Invoked By |
|--------|---------|------------|
| `kling_operations.py` | Execute Kling operations, poll for completion, download MP4s, and return structured generation results | Kira (`VP`, `MS`, `CT`, `VQ`) |

## Reference Index

| Reference | Purpose | Loaded When |
|-----------|---------|-------------|
| `prompt-patterns.md` | Prompt structures, clip-type patterns, negative prompt defaults, rhythm guidance | Kira needs clip-specific prompt craft |
| `model-selection.md` | Cost/quality/speed tradeoffs, fallback logic, and clip-type defaults | Kira chooses model, mode, and duration |
| `parameter-catalog.md` | Live-tested field names, endpoint patterns, response structures, and quirks | Kira needs exact API behavior |

## Supported Operations

| Operation | Client Method | When |
|-----------|---------------|------|
| **Text to video** | `text_to_video()` | B-roll, concept visualizations, hero visuals |
| **Image to video** | `image_to_video()` | Animate Gary PNGs, bridge graphics, approved static visuals |
| **Lip-sync** | `lip_sync()` | Presenter overlays or character sync using pre-existing audio |
| **Extend** | `extend_video()` | Lengthen a useful clip without rebuilding from scratch |
| **Polling** | `get_task_status()` / `wait_for_completion()` | Required for async task completion |
| **Download** | `download_video()` | Required for every successful production run |
---
name: kling-video
description: Kling API video generation mastery skill with prompt patterns, model selection guidance, parameter catalog, and execution wrapper scripts. Invoked by Kira (bmad-agent-kling) for all Kling API operations.
---

# Kling Video Mastery

## Purpose

Provides complete Kling API tool expertise for Kira (Video Director). This skill handles all Kling API operations - generation, polling, download, and execution wrapping - and contains the prompt guidance, model selection logic, parameter documentation, and scripts Kira uses to produce educational video clips.

This is the **skill layer** in the three-layer architecture:
Kira (agent - judgment) -> kling-video (skill - tool expertise) -> KlingClient (API client - connectivity)

## Key Paths

| Path | Purpose |
|------|---------|
| `./references/prompt-patterns.md` | Effective prompt structures for each educational video type |
| `./references/model-selection.md` | Model, mode, and duration tradeoffs with cost-aware guidance |
| `./references/parameter-catalog.md` | Complete live-tested Kling API parameter reference |
| `./scripts/kling_operations.py` | Agent-level KlingClient wrapper: submit, poll, extract, download, return structured results |

## Script Index

| Script | Purpose | Invoked By |
|--------|---------|------------|
| `kling_operations.py` | Execute Kling operations, poll for completion, download MP4s, and return structured generation results | Kira (`VP`, `MS`, `CT`, `VQ`) |

## Reference Index

| Reference | Purpose | Loaded When |
|-----------|---------|-------------|
| `prompt-patterns.md` | Prompt structures, clip-type patterns, negative prompt defaults, rhythm guidance | Kira needs clip-specific prompt craft |
| `model-selection.md` | Cost/quality/speed tradeoffs, fallback logic, and clip-type defaults | Kira chooses model, mode, and duration |
| `parameter-catalog.md` | Live-tested field names, endpoint patterns, response structures, and quirks | Kira needs exact API behavior, not proxy assumptions |

## Supported Operations

| Operation | Client Method | When |
|-----------|---------------|------|
| **Text to video** | `text_to_video()` | B-roll, concept visualizations, hero visuals |
| **Image to video** | `image_to_video()` | Animate Gary PNGs, bridge graphics, approved static visuals |
| **Lip-sync** | `lip_sync()` | Presenter overlays or character sync using pre-existing audio |
| **Extend** | `extend_video()` | Lengthen a useful clip without rebuilding from scratch |
| **Polling** | `get_task_status()` / `wait_for_completion()` | Required for async task completion |
| **Download** | `download_video()` | Required for every successful production run |
