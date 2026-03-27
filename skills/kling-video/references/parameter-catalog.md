# Kling Parameter Catalog

Live-tested parameter and endpoint reference for the Kling API implementation used in this repo.

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
- `kling-v3-0`

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

## Repo-Specific Guidance

- Default validation runs should prefer `kling-v1-6`, `std`, `"5"`
- Keep test and sample clips short
- Prefer Gary PNG reuse for image-to-video
- Prefer ElevenLabs audio reuse for lip-sync
