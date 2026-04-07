# Kling Production Decision Tree

Use this as the concise operational decision tree for Kira and Marcus when choosing and executing Kling work.

## 1. Choose the source mode

### Prefer `image2video` when:

- an approved Gary or Gamma still already carries the intended meaning
- the goal is to bring a static instructional visual to life
- composition preservation matters more than scene reinvention
- the source still is primarily graphical, conceptual, atmospheric, or illustrative rather than text-dense

### Prefer `text2video` when:

- no approved still exists
- the need is atmosphere, B-roll, or a concept scene that is not already designed
- a slide should be supported by motion rather than directly animated from the slide itself

## 2. Choose the repo-safe model lane

### Default production lane

- model family: `kling-v2-6`
- mode: start with `std` unless quality risk justifies `pro`
- audio: silent-by-omission

### Validation-only / exploratory lane

- native audio
- `3.0` / latest API surface
- advanced motion-control probes not yet validated from this repo

## 3. Decide whether to spend `pro`

Use `pro` only when the gain is likely visible and instructionally meaningful:

- portrait realism where face stability matters
- product macro where materials/reflections matter
- a production-bound clip that failed quality in `std`

Stay in `std` when:

- the clip is exploratory
- the motion is subtle
- the source image already does most of the work

## 4. Budget handling

- one `pro -> std` downgrade is allowed per over-budget clip
- if the downgraded clip still exceeds budget, pause for operator action
- do not silently continue with an out-of-policy spend

## 5. Audio policy

### Production

- `requested_audio_mode: silent`
- omit Kling native-audio field from the API request
- ElevenLabs owns audio

### Validation

- native audio may be probed only in the validation lane
- failed audio probes do not promote that feature into production readiness

## 6. Submission and resume rules

- if a run-scoped `.progress.json` exists for the same slide, resume that task
- do not submit a second job blindly
- duplicate active runners are a failure condition

## 7. Completion rule

Provider success is not enough.

A production clip is complete only when all of the following are true:

1. provider reached terminal success
2. MP4 downloaded locally
3. local validation passed
4. `motion_plan.yaml` patched with the validated asset path and status

## 8. Quality escalation

If output quality is weak, iterate with one concrete lever at a time:

- strengthen prompt specificity
- reduce motion complexity
- switch source mode
- shorten duration
- upgrade `std -> pro` if justified
- use a stronger source image

Do not change multiple major variables at once unless the clip is purely exploratory.

## 9. Text-Heavy Slide Rule

Do not assume that gentle `image2video` motion is automatically useful for a text-based slide.

Current live guidance from this repo:

- slow push-ins on text-heavy slides often soften or blur legibility
- the same motion pattern performs much better on graphical stills, roadmap visuals, conceptual illustrations, and low-text compositions

So:

- prefer `static` for text-heavy instructional slides unless there is a very specific alternate motion treatment to test
- prefer `image2video` for graphical Gamma/Gary stills that benefit from depth, emphasis, or scene life
