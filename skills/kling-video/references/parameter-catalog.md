# Kling Parameter Catalog

Live-tested parameter and endpoint reference for the Kling API implementation used in this repo.

## Gate 7E Operational Note

- Use `skills/production-coordination/scripts/run_motion_generation.py` for production motion rows.
- The production entrypoint delegates to the Kling backend, which submits or resumes an existing `task_id`, polls to terminal state, downloads the MP4, validates the local file, patches `motion_plan.yaml`, and writes run-scoped receipts.
- The runner defaults to silent generation by omitting Kling's native-audio field entirely for instructional content.
- If a `.progress.json` receipt already contains a live `task_id`, the runner resumes polling instead of submitting a duplicate job.
- If the slide already has a valid terminal local asset in `motion_plan.yaml`, the runner returns a no-op receipt and does not resubmit.

## Live-Tested Reality

These details are not theoretical. They were confirmed against the working API in this project:

- Base URL: `https://api.klingai.com`
- Auth: JWT generated from `KLING_ACCESS_KEY` + `KLING_SECRET_KEY`
- Request field: `model_name` (not `model`)
- `mode` values: `std` / `pro`
- `duration` should be sent as a string (`"5"`, `"10"`, `"15"`)
- Status endpoint is type-specific: `/v1/videos/{task_type}/{task_id}`
- Status field is `task_status`
- Success value is `succeed`
- Video URL is nested under `data.task_result.videos[0].url`
- public Git-hosted PNGs work as `image2video` sources on the current client
- silent generation for instructional work must omit Kling's native-audio field entirely

## Auth

JWT payload fields:
- `iss`: access key
- `exp`: current time + 1800 seconds
- `nbf`: current time - 5 seconds

Authorization header:
```text
Authorization: Bearer <jwt_token>
```

## Endpoints

### `POST /v1/videos/text2video`

Generate a video from prompt text.

**Primary body fields**
- `model_name`
- `prompt`
- `duration`
- `aspect_ratio`
- `mode`
- `negative_prompt`

### `POST /v1/videos/image2video`

Generate a video from a source image.

**Primary body fields**
- `model_name`
- `image`
- `prompt`
- `duration`
- `aspect_ratio`
- `mode`
- `end_image`
- `negative_prompt`

### `POST /v1/videos/lip-sync`

Apply lip-sync using source video and audio.

**Primary body fields**
- `video_url`
- `audio_url`

### `POST /v1/videos/extend`

Extend a generated or existing clip.

**Primary body fields**
- `video_url`
- `prompt`
- `duration`

### `GET /v1/videos/{task_type}/{task_id}`

Poll for status.

Examples:
- `/v1/videos/text2video/866367381512265804`
- `/v1/videos/image2video/{task_id}`

## Parameters

### `model_name`

Known usable values from repo research and live testing:
- `kling-v1-6`
- `kling-v2-1-master`
- `kling-v2-5`
- `kling-v2-6`

Research note:
- public docs and the Kling app UI advertise `kling-v3-0`
- the current repo client returned provider error `model_name value 'kling-v3-0' is invalid`
- treat `3.0` as researched but **not yet supported by this repo client**

### `mode`

- `std`
- `pro`

Do not use `"standard"` or `"professional"` with this API surface.

### `duration`

Send as a string.

Typical values:
- `"5"`
- `"10"`
- `"15"` where supported

For non-native delivery shapes such as an 8-second final clip or a deliberate
slow-motion ending, generate the nearest supported source clip first and then
derive the delivery version in post. This repo's standard post-process path is
`skills/kling-video/scripts/clip_postprocess.py`.

### `aspect_ratio`

- `16:9`
- `9:16`
- `1:1`

### `negative_prompt`

Use to exclude:
- text overlays
- watermarks
- cartoon drift
- chaotic camera movement
- irrelevant background subjects

## Response Notes

### Generation Response

Typical success envelope:
```json
{
  "code": 0,
  "message": "SUCCEED",
  "data": {
    "task_id": "...",
    "task_status": "submitted"
  }
}
```

### Status Response

Look for:
- `data.task_status`
- `data.task_result.videos[0].url`
- `data.task_result.videos[0].duration`
- `data.final_unit_deduction`

### Download

Always download immediately after success. Do not rely on the CDN URL remaining stable.

## Audio Semantics

### Silent production

For instructional production:
- keep Kling video silent
- omit the native-audio field from the request body
- let ElevenLabs own narration and deliberate sound design

Do **not** assume `sound=False` is equivalent to silence. The provider rejected that request shape in this repo's hardening pass.

### Native-audio exploration

Use native audio only in the validation lane. If you probe it:
- set `requested_audio_mode: native`
- send `sound=True`
- keep the result out of production motion state until it is deliberately approved

Current repo finding:
- a live `kling-v2-6` `pro` native-audio probe returned provider code `1201` with message `Failed to resolve the request body`
- treat native audio as blocked on the current repo client surface until proven otherwise

## Repo-Specific Guidance

- Default validation runs should prefer `kling-v2-6`, `std`, `"5"`
- Keep test and sample clips short
- Prefer Gary PNG reuse for image-to-video
- Prefer ElevenLabs audio reuse for lip-sync
- Use `skills/kling-video/scripts/kling_validation_runner.py` for exploratory cases and `run_motion_generation.py` for Gate 7E production rows
