# Kling Live Validation Findings

Snapshot of live Kling observations from this repo on `2026-04-07`.

## Confirmed Working

### 1. Silent `text2video` on the current repo client

- API surface: `https://api.klingai.com`
- auth: JWT from `KLING_ACCESS_KEY` + `KLING_SECRET_KEY`
- operational rule: encode silent generation by omitting the native-audio field entirely
- live receipt: `T1-text2video-std-silent`
- observed provider deduction: `1.5`

Important outcome:
- sending `sound=False` is not the same as silent-by-omission
- the provider rejected the `sound=False` request body in the hardening pass

### 2. Approved-slide `image2video`

Confirmed live:
- a public Git-hosted PNG from the storyboard publish lane works as an `image2video` source
- the current repo client can submit, poll, download, and validate the resulting MP4
- live receipts:
  - `I1-image2video-std-silent` -> provider deduction `1.5`
  - `I2-image2video-pro-silent` -> provider deduction `2.5`

This is the highest-value current Kling pattern for the APP because it preserves Gary's approved slide look while adding motion.

### 3. Static-to-life instructional visuals are now strongly validated

The highest-priority instructional pattern is no longer just theoretical.

Confirmed live on `2026-04-07`:
- four selected Gamma visuals were published to stable public URLs
- all four were successfully turned into usable motion clips through `kling-v2-6` `std` `image2video`
- two succeeded immediately and two succeeded on one bounded retry after Pages propagation delay

Practical meaning:
- bringing approved static visuals to life is currently the strongest instructional Kling use case in this repo
- Gamma/Gary stills should be treated as first-choice motion sources before inventing brand-new scenes
- Pages propagation delay can matter immediately after publish; a single bounded retry is justified when the provider fails to read a just-published file

### 4. Phase 1 four-pack succeeded cleanly

Confirmed live on `2026-04-07`:
- `K03` Luxury product macro (`text2video`)
- `K05` Slide-preserving motion card (`image2video`)
- `K06` Infographic / roadmap reveal (`image2video`)
- `K01` Beauty glam close-up (`text2video`)

All four succeeded on the first pass.

Practical meaning:
- the current repo-safe `kling-v2-6` `std` silent lane is broad enough for:
  - product-style editorial motion
  - portrait glamour close-up
  - approved-slide motion preservation
  - structured diagram/reveal motion
- early exploration should continue favoring breadth-first style probes on the `2.6` lane before spending effort on `3.0`

Operator reaction from the live review matters here:

- the glamour / fashion photo-realistic clips were especially strong
- the structured animated group / collaboration-circle clip from our own Gamma stills was especially strong
- slow zoom on text-heavy slides was a weak pattern because it softened or blurred legibility without adding enough value

So the validated interpretation is:
- `image2video` is strongest when the source still is primarily graphical, conceptual, or illustrative
- `image2video` is weaker when the source still is text-dense and the motion is just a gentle push-in
- for text-heavy slides, static display or a different motion treatment is usually preferable to zoom-based motion

### 5. Phase 2 four-pack also succeeded cleanly

Confirmed live on `2026-04-07`:
- `K02` Clean fashion portrait (`text2video`)
- `K07` Clinical hallway atmosphere (`text2video`)
- `K08` Neon cityscape (`text2video`)
- `K09` Stylized 3D mascot idle (`text2video`)

All four succeeded on the first pass.

Practical meaning:
- the repo-safe lane now has live wins across:
  - editorial portrait realism
  - healthcare atmosphere
  - environmental lighting / cityscape motion
  - stylized 3D character idles
- this materially expands confidence in `kling-v2-6` `std` as a broad exploratory lane, not just a narrow instructional-image lane
- the current validation program should continue delaying `3.0` work until the `2.6` breadth map is saturated

### 6. Downloads are authoritative, not the website library

The reliable success proof is:
- provider task reaches terminal success
- video URL is returned
- local MP4 is downloaded and validated

The Kling website listing is not a trustworthy source of truth for API-run reconciliation in this repo.

## Confirmed Gaps

### 1. Kling `3.0` is now partially wired on the Singapore validation surface

Confirmed live on `2026-04-07`:
- the older default endpoint still rejected `model_name='kling-v3-0'`
- the newer Singapore endpoint accepted `model_name='kling-v3'`
- a silent `text2video` probe succeeded, downloaded, and validated locally

Practical meaning:
- `3.0` is no longer blocked by missing credentials
- it is now a live validation capability on the Singapore surface
- it is still **not** production-safe until the request shapes and quality profile are better mapped

### 2. Native audio is still exploratory and still blocked on the probed request shape

Public pricing/docs indicate audio-on behavior exists, but repo production policy remains:
- instructional video should stay silent
- ElevenLabs owns narration and deliberate sound design

So native audio belongs in the validation lane, not the production lane, unless a future workflow explicitly authorizes it.

Current repo-specific findings:
- live `kling-v2-6` `pro` native-audio probe returned provider code `1201`
- live `kling-v3` Singapore-surface native-audio probe also returned provider code `1201`
- message in both cases: `Failed to resolve the request body`
- treat native audio as still blocked on the currently probed request shapes until proven otherwise

Open validation target:
- find a proven successful Kling API example for native audio / SFX request bodies, then compare that exact request shape against this repo's current probes

## Best Current Defaults

1. Start with `image2video` when you already have an approved visual.
2. Use `kling-v2-6` `std` for the first pass.
3. Keep clips short.
4. Encode silence by omitting the native-audio field.
5. Download immediately and validate locally.
6. Patch production state only after local validation succeeds.
7. For instructional work, prioritize static-to-life motion from approved Gamma/Gary stills.
8. For exploratory breadth, the current clean follow-on set is product macro, portrait close-up, slide-preserving motion, and structured infographic reveal.
9. The repo-safe `2.6` lane is now live-proven across both instructional still-based motion and broader text-driven style probes.
10. Avoid slow-zoom motion on text-heavy slides; it tends to reduce legibility without enough instructional gain.

## Source Links

- Kling docs: https://klingapi.com/docs
- Kling quickstart: https://kling.ai/quickstart
- Kling pricing: https://klingapi.com/pricing
- Kling 3.0 model page: https://klingapi.com/de/models/kling-3-0
- Kling FAQ: https://klingapi.com/ja/faq
