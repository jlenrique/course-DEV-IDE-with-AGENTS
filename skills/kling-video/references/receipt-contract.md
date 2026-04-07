# Kling Receipt Contract

Canonical receipt expectations for the repo's Kling production and validation lanes.

## Purpose

Receipts are not optional notes. They are operational state.

They exist to make Kling work:

- resumable
- auditable
- fail-closed
- safe against duplicate submission

## Production Lane Receipts

Gate `7E` production generation uses the wrapper:

`skills/production-coordination/scripts/run_motion_generation.py`

That wrapper delegates to the Kling backend and must maintain these receipt types per generated slide.

### Progress receipt

Expected shape: run-scoped `.progress.json`

Purpose:

- record the active provider `task_id`
- support resume / reconciliation
- prevent duplicate job submission for the same slide

Required fields:

- `run_id`
- `slide_id`
- `task_id`
- `provider`
- `operation`
- `model_name`
- `mode`
- `status`
- `submitted_at`
- `requested_audio_mode`

Operational rule:

- if a progress receipt already exists for the same slide, resume polling that `task_id`
- do not submit a second job blindly

### Terminal result receipt

Expected shape: run-scoped terminal `.json`

Purpose:

- record final provider status
- record local asset path
- record credits consumed and validation outcome

Required fields:

- `run_id`
- `slide_id`
- `task_id`
- `provider_status`
- `terminal_status`
- `local_asset_path`
- `download_status`
- `validation_status`
- `credits_consumed`
- `requested_audio_mode`
- `model_name`
- `mode`
- `duration_seconds`
- `completed_at`

Operational rule:

- `motion_plan.yaml` is not patched until this receipt reflects successful local validation

## Validation Lane Receipts

Validation runs use:

`skills/kling-video/scripts/kling_validation_runner.py`

Artifacts live under:

`reports/kling-validation/<run-label>/`

Expected files:

- `summary.json`
- `receipts/<case-id>.json`
- downloaded MP4s for successful runs

Validation receipts should preserve:

- provider request shape used
- case id
- model and mode
- task id if submission occurred
- status or error
- local MP4 path when present
- validation notes

## Required Canonical Examples

The repo should always keep example receipts for:

- successful silent text-to-video
- successful silent image-to-video
- successful `3.0` / Singapore-surface silent text-to-video
- structured native-audio failure
- structured unsupported-model failure from the old default endpoint

These examples function as regression fixtures, not just historical artifacts.

## Terminal Status Meaning

| Status | Meaning | Production action |
|---|---|---|
| `submitted` | job accepted, not finished | keep polling |
| `running` | provider still processing | keep polling |
| `succeed` / `completed` | provider claims success | download, validate locally, then patch plan |
| `failed` | provider rejected or generation failed | stop, write terminal receipt, escalate or retry according to policy |
| `reconciled` | local state recovered from existing task or artifact | safe to continue only if validation passed |

## Non-Negotiable Rules

- No plan patch before local MP4 validation passes.
- No silent partial continuation after provider failure.
- No duplicate active runners for the same slide.
- Production silence must be encoded as `requested_audio_mode: silent` with Kling native-audio omitted from the request.
