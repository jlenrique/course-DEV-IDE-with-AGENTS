# Motion-Enhanced Workflow Design

**Epic:** 14 - Motion-Enhanced Presentation Workflow  
**Status:** done  
**Validated:** 2026-04-05  
**Source:** Party Mode consensus + Epic 14 implementation

## Pipeline

Static remains the default path. Motion is additive and only activates when `motion_enabled: true`.

```text
Irene Pass 1
-> Gary slide generation
-> Gate 2
-> Gate 2M (motion designation)
-> motion generation/import
-> Motion Gate
-> Irene Pass 2
-> ElevenLabs
-> Compositor
```

### Gate Behavior

- `Gate 2`: approve winner slide deck
- `Gate 2M`: designate each approved slide as `static`, `video`, or `animation`
- `Motion Gate`: approve generated/imported motion assets before Irene Pass 2
- `motion_enabled: false`: skip Gate 2M, motion generation/import, and Motion Gate entirely

## Control Plane

### Run Constants

`run-constants.yaml` now supports:

```yaml
motion_enabled: boolean
motion_budget:
  max_credits: number
  model_preference: std | pro
```

### Run-Scoped Sidecar

Gate 2M decisions persist in a run-scoped `motion_plan.yaml`, not in the segment manifest.

Reason:
- the authorized winner deck exists before Irene Pass 2
- the segment manifest does not exist until Irene Pass 2
- motion linkage therefore has to live in a pre-manifest sidecar keyed by `slide_id`

### Motion Plan Shape

```yaml
motion_enabled: true
motion_budget:
  max_credits: 24
  model_preference: pro
summary:
  static: 1
  video: 1
  animation: 1
  estimated_credits: 8.0
slides:
  - slide_id: slide-02
    motion_type: video
    motion_brief: Animate the chart trend upward
    motion_asset_path: motion/slide-02_motion.mp4
    motion_source: kling
    motion_duration_seconds: 5.0
    motion_status: approved
```

## Role Matrix

| Stage | Owner | Responsibility |
|---|---|---|
| Gate 2M | Human with Marcus | designate motion per approved slide |
| Motion plan persistence | Production coordination | write/read `motion_plan.yaml` |
| Video generation | Kira/Kling | generate budget-aware MP4 clips |
| Manual animation guidance | Irene-side helper | generate tool-agnostic guidance and validate imports |
| Motion Gate | Human with Marcus | approve generated/imported motion assets |
| Motion perception | Irene | perceive approved motion assets before Pass 2 writing |
| Assembly | Compositor | sync motion assets and emit motion placement instructions |

## Manifest Extensions

Segments hydrate these fields from `motion_plan.yaml` during Irene Pass 2:

```yaml
motion_type: static | video | animation
motion_asset_path: string | null
motion_source: kling | manual | null
motion_duration_seconds: float | null
motion_brief: string | null
motion_status: pending | generated | imported | approved | null
```

Fail-closed rule:
- `motion_type != static` requires an approved readable `motion_asset_path` before Irene Pass 2 and before compositor assembly

## Budget Guardrails

- Kira prefers image-to-video when a source image URL exists
- fallback is text-to-video when no image URL is available
- `model_preference: pro` may downgrade once to `std` if estimated credits exceed `max_credits`
- if `std` still exceeds ceiling, halt rather than silently skip or partially generate

## Compatibility Rules

- Gate 2M must bind to the Epic 12 authorized winner deck, never unresolved A/B pairs
- Epic 13 visual reference traceability rules still apply to motion-aware narration
- Static-only runs must preserve prior behavior with zero motion checks or routing

## Consensus Record

Party Mode consensus used for implementation:
- contract-first sequence: `14.1 -> 14.2 -> 14.3 -> 14.4/14.5 -> 14.6 -> 14.7`
- run-scoped `motion_plan.yaml` sidecar
- no new DB/state layer
- no new UI surface required beyond Gate 2M presentation
- QA exit requires both mixed-motion proof and static control proof
