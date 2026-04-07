# Kling Mini-Production Roadmap

Recommended slate for expanding repo-native Kling capability across current `2.6`-safe work, latest-API / `3.0` exploration, and future hybrid production integration.

## Coverage Principle

The goal is not just to make attractive clips. The goal is to exercise distinct source modes, motion behaviors, style families, and production handoff patterns.

## Core 12

| ID | Mini-production | Style family | Source mode | Phase |
|---|---|---|---|---|
| K01 | Beauty glam close-up | single-subject portrait | `image2video` or reference-driven | `2.6-safe` |
| K02 | Clean fashion portrait | editorial portrait | `image2video` or reference-driven | `2.6-safe` |
| K03 | Luxury product macro | product macro | `image2video` | `2.6-safe` |
| K04 | Macro surreal detail | close-up surreal macro | `image2video` | `2.6-safe` |
| K05 | Slide-preserving motion card | static slide brought to life | `image2video` from approved slide PNG | `2.6-safe` |
| K06 | Infographic / roadmap reveal | minimal diagram animation | `image2video` from approved graphic | `2.6-safe` |
| K07 | Clinical hallway atmosphere | restrained healthcare realism | `text2video` | `2.6-safe` |
| K08 | Neon cityscape | environment / lighting | `text2video` | `2.6-safe` |
| K09 | Stylized 3D mascot idle | stylized character motion | `text2video` or reference-driven | `2.6-safe` |
| K10 | Anthropomorphic animal comedy | expressive stylized realism | reference-driven | `mid-tier exploratory` |
| K11 | Anime action / kinetic POV | stylized action | latest API / motion-control / `3.0` | `latest-API / 3.0` |
| K12 | Slide-to-scene bridge | hybrid instructional cinematic | slide PNG into richer scene | `hybrid / future` |

## Gamma Static-to-Life Sub-Suite

Highest-priority instructional extension to the main slate: bring selected static Gamma visuals to life through reference-based Kling motion.

| ID | Visual | File | Source mode | Why it belongs |
|---|---|---|---|---|
| G01 | Roadmap / Pathway Forward | `resources/Gamma-visuals/3ZC7NcG8Zx-weVZu.png` | `image2video` | best sequence/pathway probe |
| G02 | Clinician at the Hospital Crossroads | `resources/Gamma-visuals/FWoSQ8zvy6Ebxnuk.png` | `image2video` | strong directional / role-tension probe |
| G03 | Constrained System vs Innovator Breakout | `resources/Gamma-visuals/i-06FJd5m8U-QTlM.png` | `image2video` | split-scene contrast and transformation probe |
| G04 | Physician at the Fork: Paperwork vs Digital Innovation | `resources/Gamma-visuals/Znhdq4eYdG1UpByd.png` | `image2video` | best overall static-to-life instructional probe |

## Recommended Execution Order

### Phase 1: clean early probes

- `K03` Luxury product macro
- `K05` Slide-preserving motion card
- `K06` Infographic / roadmap reveal
- `K01` Beauty glam close-up

Status on `2026-04-07`:

- completed successfully in validation lane as `20260407-kling-phase1-fourpack-a`
- all `4/4` succeeded on the first pass

### Phase 2: environmental and character breadth

- `K02` Clean fashion portrait
- `K07` Clinical hallway atmosphere
- `K08` Neon cityscape
- `K09` Stylized 3D mascot idle

Status on `2026-04-07`:

- completed successfully in validation lane as `20260407-kling-phase2-fourpack-a`
- all `4/4` succeeded on the first pass

### Phase 3: instructional static-to-life suite

- `G04` Physician at the Fork
- `G02` Clinician at the Hospital Crossroads
- `G01` Roadmap / Pathway Forward
- `G03` Constrained System vs Innovator Breakout

Status on `2026-04-07`:

- completed successfully in validation lane across:
  - `20260407-gamma-static-to-life-a`
  - `20260407-gamma-static-to-life-a-retry1`
- final result: `4/4` successful clips
- note: two clips required one bounded retry after Pages propagation delay

### Phase 4: stretch stylization

- `K10` Anthropomorphic animal comedy

### Phase 5: latest-API / 3.0 future-facing

- `K11` Anime action / kinetic POV
- `K12` Slide-to-scene bridge

## Practical Notes

- For the current repo-safe path, prefer `kling-v2-6`, `std`, silent-by-omission, and short durations.
- For the Gamma sub-suite, publish or otherwise make each selected PNG available at a stable public URL before execution.
- Keep all Gamma sub-suite experiments in the validation lane until a specific asset is approved for production use.
- Treat static-to-life `image2video` from approved stills as the leading instructional Kling pattern currently proven in this repo.
- The current roadmap front half (`Phase 1`, `Phase 2`, and the Gamma static-to-life suite) is now fully proven on the repo-safe lane.
