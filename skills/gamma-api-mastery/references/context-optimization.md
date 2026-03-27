# Context Optimization — Content-Type Parameter Templates

Pre-built Gamma API parameter templates optimized for medical education content types. Gary's CT capability selects the appropriate template, then PR merges with style guide and envelope overrides.

These templates are passed to `gamma_operations.py` for execution — they are never called directly against the API.

## Medical Lecture Slides
```yaml
format: presentation
numCards: auto
textMode: generate
textOptions:
  amount: medium
  tone: "Professional medical education, clear and evidence-based"
  audience: "Practicing physicians and health sciences graduate students"
imageOptions:
  source: pexels
additionalInstructions: "Clean, professional medical education layout. One key concept per slide. Clear heading hierarchy."
exportAs: pdf
```

## Case Study Presentation
```yaml
format: presentation
numCards: 3-5
textMode: generate
textOptions:
  amount: detailed
  tone: "Clinical narrative, patient-centered"
  audience: "Medical professionals analyzing clinical scenarios"
imageOptions:
  source: noImages
additionalInstructions: "Case study format: presenting complaint, clinical findings, differential diagnosis, management. Clear section breaks."
exportAs: pdf
```

## Data Visualization Slide
```yaml
format: presentation
numCards: 1
textMode: preserve
textOptions:
  amount: brief
imageOptions:
  source: noImages
additionalInstructions: "Data visualization layout. Clean chart presentation with labeled axes and clear legend. Dark background, light data colors."
exportAs: pdf
```

## Assessment / Comprehension Check
```yaml
format: presentation
numCards: 1
textMode: preserve
additionalInstructions: "Interactive assessment layout. Question prompt prominent. Answer options or categorization items clearly separated. Pedagogical assessment slide, not content delivery."
imageOptions:
  source: noImages
exportAs: pdf
```

## Module Introduction / Conclusion
```yaml
format: presentation
numCards: 1-2
textMode: preserve
textOptions:
  amount: brief
additionalInstructions: "Bold, clean layout with strong title statement. Minimal supporting text. Visually striking and conceptually clear."
imageOptions:
  source: noImages
exportAs: pdf
```

## Storytelling / Narrative Arc
```yaml
format: presentation
numCards: 1
textMode: preserve
textOptions:
  amount: brief
additionalInstructions: "Progressive narrative layout with three escalating beats. Forward momentum — past to present to future. Not three equal columns; a STORY with rising energy."
imageOptions:
  source: noImages
exportAs: pdf
```

## Template Extension

When Gary encounters a content type not listed here, the process is:
1. Analyze request characteristics (density, visual complexity, pedagogical function)
2. Select the closest template as starting point
3. Adjust parameters for the specific request
4. If the combination produces good results, record in `patterns.md` for reuse
