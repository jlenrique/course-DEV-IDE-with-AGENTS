# Output Quality Assessment (QA)

Evaluate generated slides against style bible standards and return structured self-assessment to Marcus.

## Assessment Dimensions

Score each dimension 0.0-1.0:

| Dimension | What to Check | Weight (L1-L2) | Weight (L3-L4) |
|-----------|--------------|:---:|:---:|
| **Brand compliance** | Correct palette, typography per style bible, professional medical aesthetic | 0.25 | 0.20 |
| **Content fidelity** | Input content preserved without unauthorized additions, correct text, no hallucinated data | 0.30 | 0.25 |
| **Layout integrity** | Requested layout pattern achieved (parallel columns, cards, narrative arc, etc.) | 0.25 | 0.20 |
| **Accessibility** | WCAG 2.1 AA contrast, color independence, readable at target sizes | 0.10 | 0.10 |
| **Pedagogical alignment** | Slide serves stated learning objective, appropriate Bloom's level treatment | 0.10 | 0.15 |
| **Intent fidelity** | Visual rhetoric and emphasis match the requested behavioral/affective effect | — | 0.10 |
| **Content completeness** | All required content elements present, nothing critical missing | — | 0.10 |

## Embellishment Detection

Flag any content Gamma added that was not in the input:
- Added subtitles, bullet points, or steps not in the original
- Decorative elements or diagrams not requested
- Expanded or paraphrased text beyond what was provided

Report as: `embellishment_detected: true/false`, with specific items listed.

## Self-Assessment Return Format

```yaml
quality_assessment:
  overall_score: 0.87
  dimensions:
    brand_compliance: 0.9
    content_fidelity: 0.85
    layout_integrity: 0.9
    accessibility: 1.0
    pedagogical_alignment: 0.8
    intent_fidelity: 0.85
  embellishment_detected: true
  embellishment_details:
    - "Gamma added a subtitle 'Bridging Two Worlds' not in the input"
  flags:
    - "Content fidelity below 0.9 — recommend human review of added subtitle"
  recommendation: "approve_with_note"
```

## Scoring Guidelines

- **0.9-1.0**: Meets or exceeds standards
- **0.7-0.89**: Acceptable with minor notes
- **0.5-0.69**: Needs revision — flag specific issues
- **Below 0.5**: Reject — provide root cause for rework

Be conservative. Honest assessment protects the user from publishing subpar content.

## Intent-Fidelity Guidance

If Irene or Marcus specifies `behavioral_intent`, assess whether the slide's hierarchy, contrast, density, and imagery support that effect:

- `credible` -> restrained, professional, evidence-forward
- `alarming` -> tension without melodrama; strong contrast and visual consequence
- `moving` -> emotionally resonant, human-centered, not sentimental clutter
- `attention-reset` -> visual simplification, pause beat, deliberate focus shift
- `reflective` -> slower, calmer visual rhythm with space to think

If the output is technically correct but emotionally flat or mismatched, score `intent_fidelity` down and flag for Gate 2 review.
