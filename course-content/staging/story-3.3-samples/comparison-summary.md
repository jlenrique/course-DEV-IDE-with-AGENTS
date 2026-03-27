# Story 3.3 Kling Comparison Summary

## Completed Variants

| Clip | Filename | Model | Mode | Duration | Status | Notes |
|---|---|---|---|---|---|---|
| V1-hospital-broll | `V1-hospital-broll__kling-v1-6_std_5s.mp4` | `kling-v1-6` | `std` | `5` | downloaded | initial live validation clip |
| V2-clinical-to-innovator-pathway | `V2-clinical-to-innovator-pathway__kling-v2-6_std_5s.mp4` | `kling-v2-6` | `std` | `5` | downloaded | downloaded baseline comparison clip |
| V3-heros-journey-roadmap | `V3-heros-journey-roadmap__kling-v1-6_std_5s.mp4` | `kling-v1-6` | `std` | `5` | downloaded | legacy baseline clip |
| V3-heros-journey-roadmap | `V3-heros-journey-roadmap__kling-v2-6_std_5s.mp4` | `kling-v2-6` | `std` | `5` | downloaded | downloaded baseline comparison clip |
| V4-knowledge-explosion-timeline | `V4-knowledge-explosion-timeline__kling-v1-6_std_5s.mp4` | `kling-v1-6` | `std` | `5` | downloaded | legacy baseline clip |
| V4-knowledge-explosion-timeline | `V4-knowledge-explosion-timeline__kling-v2-6_std_5s.mp4` | `kling-v2-6` | `std` | `5` | downloaded | downloaded baseline comparison clip |
| V5-physician-innovator-lineage | `V5-physician-innovator-lineage__kling-v1-6_std_5s.mp4` | `kling-v1-6` | `std` | `5` | downloaded | legacy baseline clip |
| V5-physician-innovator-lineage | `V5-physician-innovator-lineage__kling-v2-6_std_5s.mp4` | `kling-v2-6` | `std` | `5` | downloaded | downloaded baseline comparison clip |
| V6-module-bridge-transition | `V6-module-bridge-transition__kling-v1-6_std_5s.mp4` | `kling-v1-6` | `std` | `5` | downloaded | legacy baseline clip |
| V6-module-bridge-transition | `V6-module-bridge-transition__kling-v2-6_std_5s.mp4` | `kling-v2-6` | `std` | `5` | downloaded | downloaded baseline comparison clip |
| V1-hospital-broll | `V1-hospital-broll__kling-v2-6_std_5s.mp4` | `kling-v2-6` | `std` | `5` | downloaded | downloaded baseline comparison clip |
| V1-hospital-broll | `V1-hospital-broll__kling-v2-6_pro_5s.mp4` | `kling-v2-6` | `pro` | `5` | downloaded | downloaded premium comparison clip |
| V2-clinical-to-innovator-pathway | `V2-clinical-to-innovator-pathway__kling-v2-6_pro_5s.mp4` | `kling-v2-6` | `pro` | `5` | downloaded | downloaded premium comparison clip |
| V3-heros-journey-roadmap | `V3-heros-journey-roadmap__kling-v2-6_pro_5s.mp4` | `kling-v2-6` | `pro` | `5` | downloaded | downloaded premium comparison clip |
| V4-knowledge-explosion-timeline | `V4-knowledge-explosion-timeline__kling-v2-6_pro_5s.mp4` | `kling-v2-6` | `pro` | `5` | downloaded | downloaded premium comparison clip |
| V5-physician-innovator-lineage | `V5-physician-innovator-lineage__kling-v2-6_pro_5s.mp4` | `kling-v2-6` | `pro` | `5` | submitted / pending-finalization | premium comparison in progress |
| V6-module-bridge-transition | `V6-module-bridge-transition__kling-v2-6_pro_5s.mp4` | `kling-v2-6` | `pro` | `5` | downloaded | downloaded premium comparison clip |
| V2-clinical-to-innovator-pathway | `V2-clinical-to-innovator-pathway__kling-v3-0_pro_5s.mp4` | `kling-v3-0` | `pro` | `5` | failed | `model_name` invalid on live API surface |

## Key Findings

- `kling-v2-6 std sound off 5s` is the preferred **baseline tier**. It billed at **1.5 credits** and produced usable visual results.
- `kling-v2-6 pro 5s` is the practical **premium tier** on the API surface currently available in this repo. It billed at **2.5 credits**.
- `kling-v3-0` is **not accepted** by the live API surface currently reachable with this account and endpoint combination. The API returned `model_name value 'kling-v3-0' is invalid`.
- Kling enforces a **parallel task over resource pack limit**, so serialized submission is required.
- Native sound remains optional and request-shape-sensitive. Story 3.3 acceptance remains **visual-first**.

## Human Review Outcome

### Most Production-Worthy Clips

- `V1-hospital-broll__kling-v1-6_std_5s.mp4`
- `V5-physician-innovator-lineage__kling-v2-6_pro_5s.mp4`
- `V5-physician-innovator-lineage__kling-v1-6_std_5s.mp4`
- `V5-physician-innovator-lineage__kling-v2-6_std_5s.mp4`

### Key Rejection Pattern

- Clips that depended on **embedded text rendered inside the video itself** (for example, concept/timeline/roadmap animations such as Hero's Journey or other text-bearing conceptual visuals) produced **garbled characters** and are not production-worthy in their current Kling-only form.

### Implication

Kira is currently strongest for:
- atmospheric B-roll
- montage-style visual storytelling
- non-text-dependent motion sequences

Kira is currently weak for:
- concept animations that require readable text inside the generated video
- infographic/timeline/roadmap sequences where textual fidelity matters

### Production Guidance Going Forward

- Use **Gary / static designed slides** for text-heavy conceptual visuals.
- Use Kira to create **motion support around non-text visuals**, atmosphere, transitions, and montage sequences.
- Do **not** rely on Kling alone for readable on-screen text until a better workflow is established.

## Current Recommendation

For Kira's production defaults in this repo:

- **Baseline / fast-cheap:** `kling-v2-6`, `std`, `5s`, sound off
- **Higher-quality comparison:** `kling-v2-6`, `pro`, `5s`
- **Do not assume `kling-v3-0` is available** until a different endpoint or account path proves it live
