# Kling Model Feature Matrix

Live repo guidance for what Kling features are actually usable from this project as of `2026-04-07`.

## Reading This Matrix

- `native`: works through the current repo client path
- `partial`: publicly documented or strongly indicated, but only some behavior is validated here
- `blocked`: public model may exist, but the current repo client cannot use it yet
- `unknown`: no repo validation yet

## Matrix

| Model | Repo client status | Text-to-video | Image-to-video | Native audio | Best current use | Notes |
|---|---:|---:|---:|---:|---|---|
| `kling-v1-6` | native | native | assumed | unknown | cheap exploratory motion probes | Keep short and low-stakes |
| `kling-v2-6` | native | native | native | blocked on current repo client | production-safe motion work, especially approved-slide `image2video` | Silent text/image generation is validated; native-audio probe failed with provider code `1201` |
| `kling-v3` | validation-only exploratory | blocked on old default endpoint | native on Singapore-surface client | still blocked by request-body failure on probed request shape | not yet for repo production | Singapore-surface live probe accepted `model_name='kling-v3'`; native-audio probe still failed with provider code `1201` |

## Current Best Defaults

### Production-safe default

- operation: `image2video`
- model: `kling-v2-6`
- mode: `std`
- duration: `5`
- audio: `silent`

Why:
- preserves Gary's approved slide composition
- is already live-tested in this repo using a public Git-hosted PNG
- keeps cost and risk lower than a `pro` or `3.0` first attempt
- current live probe receipts show `std` silent cases at about `1.5` units and `pro` silent image-to-video at about `2.5`
- static-to-life Gamma/Gary probes are now strongly validated and should be treated as the first-choice instructional motion pattern

### When to use `pro`

Escalate to `pro` only when:
- the clip is highly visible in the final lesson
- subtle depth/camera quality matters
- `std` quality is visibly weak on the comparison clip

### When not to use `3.0` yet

Do not route production through `3.0` until the Singapore-surface client has live receipts for your account and the exact provider-exposed model id is confirmed. Public availability is not the same thing as current repo support.

## Public Guidance vs Repo Reality

These are different layers:

- **Public guidance**: Kling's public docs and app UI show newer capabilities, including `3.0`, longer durations, and richer storytelling.
- **Repo reality**: the current project client is wired to `https://api.klingai.com` with JWT auth from AK/SK and is proven for `2.6`. A separate validation-only Singapore-surface client now targets `https://api-singapore.klingai.com` with the same AK/SK token flow, but `3.0` is still exploratory there.

That means:
- use public docs to guide what to explore next
- use repo validation receipts to decide what is safe to automate now

## Breadth Proven On The Repo-Safe Lane

The current `kling-v2-6` `std` silent lane is now live-proven for:

- approved-slide `image2video`
- Gamma static-to-life instructional visuals
- product macro editorial motion
- beauty / fashion portrait close-up
- healthcare hallway atmosphere
- neon cityscape environment motion
- stylized 3D mascot idle

## Source Links

- Kling docs: https://klingapi.com/docs
- Kling quickstart: https://kling.ai/quickstart
- Kling pricing: https://klingapi.com/pricing
- Kling 3.0 model page: https://klingapi.com/de/models/kling-3-0
- Kling FAQ: https://klingapi.com/ja/faq
