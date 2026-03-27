# Brand Validation Rules

Style bible compliance checking for production artifacts.

## Brand Markers (extracted from style bible)

### Color Palette
| Marker | Hex | Detection Pattern |
|--------|-----|------------------|
| JCPH Navy | #1e3a5f | Hex code in content, CSS, or annotations |
| Medical Teal | #4a90a4 | Hex code in content, CSS, or annotations |
| Clean White | #ffffff | Background references |

Non-palette colors in visual specifications trigger a medium-severity finding.

### Typography
| Element | Expected Font | Detection Pattern |
|---------|--------------|------------------|
| Headlines | Montserrat | Font name in slide briefs, style annotations |
| Body/Data | Source Sans Pro | Font name in content specifications |

Unrecognized font references trigger a medium-severity finding.

### Voice and Tone
| Attribute | Expected | Detection Approach |
|-----------|----------|-------------------|
| Formality | Professional-academic | Keyword density: clinical terminology, evidence-based language |
| Authority | Authoritative, evidence-based | Absence of hedging, speculation, casual phrasing |
| Accessibility | Clear, inclusive | Reading level check, jargon management |

Voice deviations are judgment-based (Quinn-R), not fully automatable.

## Compliance Scoring

- Start at 1.0
- Each color violation: -0.1
- Each typography violation: -0.1
- Each voice/tone violation: -0.05 (judgment-weighted)
- Pass threshold: 0.7
