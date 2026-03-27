# Content Type Mapping

Maps educational video needs to Kling operations, source assets, and cost-aware defaults.

## Default Strategy

Use the cheapest operation that still achieves the instructional purpose.
- Default to **5s** clips
- Use **10s** only when a longer sequence materially improves understanding
- Use **15s** only by explicit exception
- Prefer `std` unless `pro` meaningfully improves the result

## Clip Types

| Clip Type | Pedagogical Use Case | Kling Operation | Typical Inputs | Default Generation Choice | Notes |
|----------|----------------------|-----------------|----------------|---------------------------|-------|
| Hospital / clinic B-roll | Establish atmosphere, urgency, and system context without over-explaining | `text2video` | Prompt only | `kling-v1-6`, `std`, `5` | Best for atmosphere and context-setting |
| Concept visualization | Make abstract frameworks, pathways, and system relationships visually legible | `text2video` | Prompt only | `kling-v2-6`, `std`, `5` | Use stronger motion language only when it clarifies the concept |
| Slide-to-video transition | Add motion to an already-approved static teaching visual | `image2video` | Gary PNG slide | `kling-v2-6`, `std`, `5` | Preserve Gary's composition; add motion, not redesign |
| Talking-head overlay | Deliver human presence, authority, and emotional credibility with synchronized narration | `lip-sync` | Video/image asset + ElevenLabs audio | asset-dependent | Use native audio only as secondary option |
| Section-bridge transition | Connect one lesson section to the next and orient the learner to progression | `image2video` or `text2video` | Graphic or prompt | `kling-v1-6`, `std`, `5` | Keep clean and short |
| Hero / flagship visual | Support a major lesson moment where extra polish materially improves impact | `text2video` | Prompt only | `kling-v2-6`, `pro`, `10` | Reserve `pro` for truly high-value clips |

## Model Selection Heuristics

### `kling-v1-6`
Use for:
- cheap exploratory B-roll
- fast early validation
- simple motion clips

### `kling-v2-6`
Use for:
- stronger motion quality
- better general-purpose production work
- cases where native audio may matter

### `kling-v3-0`
Use for:
- newer capability testing
- cases where the upgrade justifies the extra cost
- future advanced workflows after more repo-level validation

## Pipeline Reuse Rules

- If Gary already produced the static visual, prefer **image-to-video** over regenerating from text
- If ElevenLabs already produced narration, prefer **lip-sync** using that audio instead of Kling-native narration
- If Irene already provided a content brief, use that to craft the prompt rather than inventing scene logic from scratch

## Validation Set Mapping

The six Story 3.3 validation clips are not random demos. They are the acceptance bridge between the API and real production workflow:

| Validation Clip | Clip Type | Pedagogical Function |
|-----------------|----------|----------------------|
| V1 Hospital B-roll | B-roll | Establishes the emotional and operational reality of modern clinical work |
| V2 Clinical-to-innovator pathway | Concept visualization | Makes a conceptual reframing visually legible |
| V3 Animated Gary slide | Slide-to-video transition | Reuses an approved slide while adding motion for engagement |
| V4 Knowledge-explosion timeline | Concept visualization | Shows acceleration and scale more clearly than static text |
| V5 Talking-head overlay | Talking-head overlay | Adds human guidance and authority to narrated content |
| V6 Module bridge | Section-bridge transition | Signals progression and prepares the learner for the next concept block |

## Fallback Rules

- If `pro` is not worth the cost, downgrade to `std`
- If image asset is missing, convert the request to a text-to-video plan if the prompt can carry the visual intent
- If lip-sync asset pair is incomplete, return a generation plan and list the missing asset
