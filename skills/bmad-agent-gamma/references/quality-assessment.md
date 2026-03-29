# Output Quality Assessment (QA)

Evaluate generated slides for execution-quality only and return structured self-assessment to Marcus.

## Perception Before Assessment

Before scoring any dimension, invoke the image sensory bridge on each generated PNG to confirm what was actually produced. Follow the universal perception protocol (`skills/sensory-bridges/references/perception-protocol.md`):

1. For each downloaded PNG: invoke `perceive(png_path, "image", "G3", "gamma-specialist")`
2. Confirm interpretation: "I see Slide N shows [description]. Confidence: HIGH/MEDIUM/LOW."
3. Score dimensions based on confirmed perception, not assumed output
4. If perception confidence is LOW, flag to Marcus before reporting quality scores

Within a production run, perception results are cached per `(artifact_path, modality)` — if Vera has already perceived the same PNG, Gary reads the cached result (see `skills/sensory-bridges/references/validator-handoff.md`).

## Lane Boundaries

Gary's QA lane is execution-only. Gary self-assesses:
- layout integrity
- parameter confidence
- embellishment risk

Gary does not self-score these dimensions:
- learning objective alignment or pedagogical soundness (Irene and Quinn-R lanes)
- brand consistency or accessibility compliance (Quinn-R lane)
- source-faithfulness, provenance, or traceability (Vera lane)
- learner-effect intent fidelity (Quinn-R lane)

## Assessment Dimensions

Score each dimension 0.0-1.0:

| Dimension | What to Check | Weight (L1-L2) | Weight (L3-L4) |
|-----------|--------------|:---:|:---:|
| **Layout integrity** | Requested visual structure is correctly executed (parallel columns, cards, hierarchy, spacing) | 0.45 | 0.40 |
| **Parameter confidence** | Selected API parameters are appropriate and stable for the requested pattern | 0.35 | 0.30 |
| **Embellishment risk control** | Unauthorized additions are absent or explicitly flagged with impact | 0.20 | 0.30 |

## Embellishment Detection

Flag any content Gamma added that was not in the input:
- Added subtitles, bullet points, or steps not in the original
- Decorative elements or diagrams not requested
- Expanded or paraphrased text beyond what was provided

Report as: `embellishment_detected: true/false`, with specific items listed.

## Self-Assessment Return Format

```yaml
quality_assessment:
  overall_score: 0.86
  dimensions:
    layout_integrity: 0.9
    parameter_confidence: 0.82
    embellishment_risk_control: 0.86
  embellishment_detected: true
  embellishment_details:
    - "Gamma added a subtitle 'Bridging Two Worlds' not in the input"
  flags:
    - "Unauthorized subtitle added; flagged for downstream Quinn-R and Vera review"
  recommendation: "approve_with_note"
```

## Scoring Guidelines

- **0.9-1.0**: Meets or exceeds standards
- **0.7-0.89**: Acceptable with minor notes
- **0.5-0.69**: Needs revision — flag specific issues
- **Below 0.5**: Reject — provide root cause for rework

Be conservative. Honest execution self-assessment protects the pipeline from avoidable downstream rework.
