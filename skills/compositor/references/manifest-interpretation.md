# Manifest Interpretation

## Core Rules

- `narration_file` -> Track `A1`
- `music_bed` or music assets -> Track `A2`
- `sfx_file` -> Track `A3`
- `visual_file` -> approved still/poster-frame reference (after **`sync-visuals`**, expect repo-relative paths under the assembly bundle’s `visuals/` folder next to the manifest)
- `motion_asset_path` -> active `V1` playback source whenever `motion_type != static`

## Duration Rules

- Use `narration_duration` as the canonical segment duration
- If `visual_duration` exists and differs, note the mismatch and tell the human how to trim or hold
- For `static-hold`, hold the still visual for the narration duration
- For `pause-beat`, preserve the beat rather than collapsing it
- For `motion_type != static`, play `motion_asset_path` on `V1` and keep `visual_file` available as the approved still reference/poster frame

## Behavioral Intent

`behavioral_intent` should become an explicit edit note. Examples:

- `credible` -> restrained transitions, no flashy emphasis
- `alarming` -> allow sharper transition and stronger visual consequence
- `moving` -> allow a slower hold and emotional space
- `attention-reset` -> simplify the screen and create a pacing reset
- `reflective` -> avoid busy overlays or abrupt cuts

## Missing Fields

- If a required assembly field is missing, fail fast with a clear error
- Required per segment: `id`, `narration_duration`, `narration_file`, `visual_file`
- Additional motion requirement: when `motion_type != static`, require `motion_asset_path` and keep `visual_file` non-video
