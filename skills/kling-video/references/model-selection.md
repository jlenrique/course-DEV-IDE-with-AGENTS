# Kling Model Selection

Model, mode, and duration tradeoffs for educational video generation.

## Core Principle

Choose the cheapest configuration that still meets the instructional need. Kira is not optimizing for spectacle - only for educational usefulness, professionalism, and production fit.

## Default Duration Policy

- **5 seconds**: default for most clips
- **10 seconds**: use when a longer sequence materially improves understanding
- **15 seconds**: exception only

## Model Defaults

### `kling-v1-6`

Use for:
- cheap exploratory B-roll
- short validation clips
- simple section bridges
- basic concept clips when motion complexity is low

Recommended defaults:
- `mode: std`
- `duration: "5"`

### `kling-v2-6`

Use for:
- stronger motion quality
- more demanding concept animations
- slide-to-video transitions where motion quality matters
- cases where native audio might help as a secondary option

Recommended defaults:
- `mode: std` for most
- `mode: pro` only when the quality gain matters
- `duration: "5"` or `"10"`

### `kling-v3-0`

Use for:
- newer capability testing
- cases where higher-end motion or expanded duration is justified
- future advanced production after more repo validation

Recommended defaults:
- `mode: std` first
- escalate only when the educational gain is clear

Current repo note:
- public docs and the Kling app UI advertise `3.0`
- the old JWT repo client is **not 3.0-ready**
- a separate Singapore-surface validation client now exists for `api-singapore.klingai.com`
- do not route production through `3.0` until that Singapore-surface lane has live receipts for your account and the exact provider-exposed model id is confirmed

## Clip-Type Defaults

| Clip Type | Default Model | Default Mode | Default Duration | Escalate When |
|----------|---------------|--------------|------------------|---------------|
| Hospital / clinic B-roll | `kling-v1-6` or `kling-v2-6` | `std` | `"5"` | use `v2.6` if realism or polish matters |
| Concept visualization | `kling-v2-6` | `std` | `"5"` | `pro` if motion subtlety materially improves comprehension |
| Slide-to-video transition / approved-slide motion | `kling-v2-6` | `std` | `"5"` | only if the motion looks visibly weak |
| Talking-head / lip-sync | depends on asset path | n/a | `"5"` or `"10"` | extend only when the narration requires it |
| Section-bridge transition | `kling-v1-6` | `std` | `"5"` | almost never |
| Hero / flagship clip | `kling-v2-6` | `pro` | `"10"` | only for highly visible key moments |

## Fallback Rules

1. **Pro too expensive?** Downgrade to `std`
2. **Image asset missing for image-to-video?** Return a text-to-video plan if visual intent is still clear
3. **Lip-sync asset pair incomplete?** Return `plan_only` with missing asset list
4. **Output too busy?** Reduce motion complexity before increasing model cost

## Cost Awareness

Known live-tested observations from this repo:
- `kling-v2-6`, `std`, `5s`, `image2video` from a public Git-hosted slide PNG produced a usable MP4
- a prior short `kling-v2-6` text/video run reported roughly **2.5 credits** provider-side

Current best baseline:
- start with `kling-v2-6`, `std`, `5s`
- prefer `image2video` when you already have an approved still

New stronger guidance from live validation on `2026-04-07`:
- approved-static `image2video` is not only a baseline, it is now the leading instructional pattern validated in this repo
- the strongest current instructional use case is bringing approved Gamma/Gary visuals to life with restrained motion
- the current clean style-expansion set that also works on the repo-safe lane is:
  - product macro
  - beauty portrait close-up
  - slide-preserving motion
  - structured infographic / roadmap reveal

Important refinement from operator review:
- photoreal glamour / fashion portrait work is especially strong
- graphical Gamma stills such as the collaboration-circle / structured reveal style are especially strong
- simple slow-zoom motion on text-heavy slides is not a good default and should usually be avoided

Additional 3.0 reference:
- Kling quickstart: https://kling.ai/quickstart
