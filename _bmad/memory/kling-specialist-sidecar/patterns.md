# Learned Patterns ó Kira (Kling Specialist)

*Append-only. Default mode writes only. Condense periodically.*

## Prompt Effectiveness

- **Approved / production-worthy so far**
  - `V1-hospital-broll__kling-v1-6_std_5s` ó strong atmospheric medical B-roll
  - `V5-physician-innovator-lineage__kling-v1-6_std_5s`
  - `V5-physician-innovator-lineage__kling-v2-6_std_5s`
  - `V5-physician-innovator-lineage__kling-v2-6_pro_5s`
  - Montage-style and atmosphere-first prompts are currently Kira's strongest category

## Model / Mode Tradeoffs

- `kling-v1-6` + `std` + `"5"` validated as the cheapest known baseline that still returns usable MP4 output in this repo.

## Source Asset Pairings

- *No approved Gary/ElevenLabs reuse patterns recorded yet.*

## Common Failure Patterns

- Text-bearing concept animations (roadmaps, timelines, infographic-like sequences) produce garbled characters when Kling is expected to render readable on-screen text directly.
- Kling is currently unsuitable as the primary renderer for readable text-heavy conceptual visuals.
- Safer pattern: let Gary own text-bearing visuals; let Kira provide atmosphere, transitions, and non-text-dependent motion.
### 2026-03-27 ù Story 3.3 validation set
- **Goal**: Compare Kling visual outputs across baseline and premium tiers for medical-education clip types
- **Baseline**: `kling-v2-6` + `std` + `5s` + sound off billed at 1.5 credits and produced usable outputs
- **Premium**: `kling-v2-6` + `pro` + `5s` billed at 2.5 credits and functions as the practical top tier on the live API surface
- **Source asset lesson**: text-to-video is sufficient for the current C1-M1 demo pass; image-to-video remains valuable later when Gary-generated PNGs are central
- **Failure pattern**: `kling-v3-0` returned invalid `model_name` on the reachable live API surface; do not assume 3.0 availability without proving the endpoint/account path
- **Operational rule**: Kling enforces a concurrency/resource-pack limit (`1303`) - serialize generation requests and download immediately
