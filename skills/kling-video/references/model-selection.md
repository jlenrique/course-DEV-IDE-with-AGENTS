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

## Clip-Type Defaults

| Clip Type | Default Model | Default Mode | Default Duration | Escalate When |
|----------|---------------|--------------|------------------|---------------|
| Hospital / clinic B-roll | `kling-v1-6` | `std` | `"5"` | only if atmosphere quality is central to the lesson |
| Concept visualization | `kling-v2-6` | `std` | `"5"` | `pro` if motion subtlety materially improves comprehension |
| Slide-to-video transition | `kling-v2-6` | `std` | `"5"` | only if the motion looks visibly weak |
| Talking-head / lip-sync | depends on asset path | n/a | `"5"` or `"10"` | extend only when the narration requires it |
| Section-bridge transition | `kling-v1-6` | `std` | `"5"` | almost never |
| Hero / flagship clip | `kling-v2-6` | `pro` | `"10"` | only for highly visible key moments |

## Fallback Rules

1. **Pro too expensive?** Downgrade to `std`
2. **Image asset missing for image-to-video?** Return a text-to-video plan if visual intent is still clear
3. **Lip-sync asset pair incomplete?** Return `plan_only` with missing asset list
4. **Output too busy?** Reduce motion complexity before increasing model cost

## Cost Awareness

Known live-tested observation from this repo:
- `kling-v1-6`, `std`, `5s` produced a usable MP4 and consumed approximately **2 credits**

This is the baseline validation configuration. Use it first unless a different clip type clearly requires something better.
