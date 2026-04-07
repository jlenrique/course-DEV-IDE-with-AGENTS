---
name: kling-video
description: Kling API video generation mastery skill with prompt patterns, model selection guidance, validation cases, and execution wrapper scripts. Invoked by Kira (bmad-agent-kling) for all Kling API operations.
---

# Kling Video Mastery

## Purpose

Provides complete Kling API tool expertise for Kira (Video Director). This skill handles Kling generation, polling, download, execution wrapping, validation-lane exploration, and the live-tested reference material Kira uses to produce educational video clips.

This is the **skill layer** in the three-layer architecture:
Kira (agent - judgment) -> kling-video (skill - tool expertise) -> KlingClient (API client - connectivity)

## Key Paths

| Path | Purpose |
|------|---------|
| `./references/prompt-patterns.md` | Effective prompt structures for each educational video type |
| `./references/model-selection.md` | Model, mode, and duration tradeoffs with cost-aware guidance |
| `./references/parameter-catalog.md` | Complete live-tested Kling API parameter reference |
| `./references/model-capabilities.yaml` | Machine-readable model/feature registry for shared production + validation reasoning |
| `./references/model-feature-matrix.md` | Human-readable summary of what is currently usable from this repo |
| `./references/receipt-contract.md` | Canonical receipt expectations for production and validation lanes |
| `./references/production-decision-tree.md` | Concise operational decision tree for source mode, model lane, budget, and completion rules |
| `./references/kling-mini-production-roadmap.md` | Recommended 12-piece Kling slate plus the Gamma static-to-life sub-suite |
| `./references/successful-look-playbook.md` | Reusable recipes for the looks and motion treatments that have actually worked well in this repo |
| `./references/validation-cases.yaml` | Checked-in exploratory validation cases for the Kling validation lane |
| `./references/live-validation-findings-2026-04-07.md` | Snapshot of live-tested learnings and current gaps |
| `./scripts/kling_operations.py` | Agent-level KlingClient wrapper: submit, poll, extract, download, return structured results |
| `./scripts/kling_validation_runner.py` | Reusable exploratory validation runner that executes checked-in cases and writes receipts outside active bundles |
| `./scripts/run_motion_generation.py` | Gate 7E implementation backing the production-coordination entrypoint; submits or resumes, polls, downloads, validates, patches `motion_plan.yaml`, and writes receipts |

## Script Index

| Script | Purpose | Invoked By |
|--------|---------|------------|
| `kling_operations.py` | Execute Kling operations, poll for completion, download MP4s, and return structured generation results | Kira (`VP`, `MS`, `CT`, `VQ`) |
| `kling_validation_runner.py` | Run reusable validation cases into repo-scoped receipts without touching production bundle state | Marcus / Kira during exploration and hardening |
| `run_motion_generation.py` | Fulfill one run-scoped `video` row with idempotent resume and fail-closed receipts | Production-coordination wrapper during Gate 7E |

## Reference Index

| Reference | Purpose | Loaded When |
|-----------|---------|-------------|
| `prompt-patterns.md` | Prompt structures, clip-type patterns, negative prompt defaults, rhythm guidance | Kira needs clip-specific prompt craft |
| `model-selection.md` | Cost/quality/speed tradeoffs, fallback logic, and clip-type defaults | Kira chooses model, mode, and duration |
| `parameter-catalog.md` | Live-tested field names, endpoint patterns, response structures, and quirks | Kira needs exact API behavior |
| `model-capabilities.yaml` | Shared machine-readable statement of what models/operations are native, partial, blocked, or unknown | A runner or agent needs a current support matrix |
| `receipt-contract.md` | Receipt schema expectations and terminal-status meaning | Implementing or auditing production/validation resumability |
| `production-decision-tree.md` | Fast operational rules for image-vs-text, `std` vs `pro`, and stop conditions | Kira or Marcus is deciding how to execute a clip |
| `kling-mini-production-roadmap.md` | Consolidated mini-production slate for breadth-first Kling exploration | Planning the next validation batches |
| `successful-look-playbook.md` | Concrete prompt/source recipes for reproducing successful looks | Reusing proven aesthetics rather than inventing from scratch |
| `validation-cases.yaml` | Reusable case definitions for ongoing provider exploration | Running probes without inventing prompts or payloads from scratch |
| `live-validation-findings-2026-04-07.md` | High-signal summary of what the repo has proven versus what remains speculative | Human review, planning the next hardening pass |

## Production vs Validation Lanes

### Production lane

- operator entrypoint: `skills/production-coordination/scripts/run_motion_generation.py`
- implementation: `run_motion_generation.py`
- authority source: `motion_plan.yaml`
- artifact scope: active source bundle only
- rule: fail closed; patch production state only after local MP4 validation
- contract: `./references/receipt-contract.md` and `./references/production-decision-tree.md`

### Validation lane

- runner: `kling_validation_runner.py`
- authority source: `validation-cases.yaml`
- artifact scope: `reports/kling-validation/<run-label>/`
- rule: learn aggressively without mutating production bundle state
- contract: `./references/receipt-contract.md`

## Supported Operations

| Operation | Client Method | When |
|-----------|---------------|------|
| **Text to video** | `text_to_video()` | B-roll, concept visualizations, hero visuals |
| **Image to video** | `image_to_video()` | Animate Gary PNGs, bridge graphics, approved static visuals |
| **Lip-sync** | `lip_sync()` | Presenter overlays or character sync using pre-existing audio |
| **Extend** | `extend_video()` | Lengthen a useful clip without rebuilding from scratch |
| **Polling** | `get_task_status()` / `wait_for_completion()` | Required for async task completion |
| **Download** | `download_video()` | Required for every successful production run |
