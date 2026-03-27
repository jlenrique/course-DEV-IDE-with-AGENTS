# Content Type Mapping (CT)

Map educational content types to optimal Gamma API parameter configurations. Each template represents a starting point — merge with style guide defaults and context envelope overrides.

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
additionalInstructions: "Clean, professional medical education layout. Montserrat headings, clear hierarchy. One key concept per slide."
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
additionalInstructions: "Case study format: presenting complaint, clinical findings, differential diagnosis, management. Clear section breaks between case elements."
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
additionalInstructions: "Data visualization layout. Clean chart presentation with labeled axes and clear legend. Dark background, light data colors. Emphasis on signal over noise."
exportAs: pdf
```

## Assessment / Comprehension Check

```yaml
format: presentation
numCards: 1
textMode: preserve
additionalInstructions: "Interactive assessment layout. Question prompt should be prominent. Answer options or categorization items clearly separated. This is a pedagogical assessment slide, not content delivery."
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
additionalInstructions: "Bold, clean layout with strong title statement. Minimal supporting text. This slide sets the tone — it should be visually striking and conceptually clear."
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
additionalInstructions: "Progressive narrative layout with three escalating beats. Each beat should convey forward momentum — past to present to future. Not three equal columns; this is a STORY with rising energy."
imageOptions:
  source: noImages
exportAs: pdf
```

## Gamma Template-Based Generation

When a custom Gamma template has been created for a specific course, module, or content type, Gary uses the `POST /generations/from-template` endpoint instead of text generation. Templates encode visual layout, brand standards, and structural patterns directly in Gamma — reducing the need for `additionalInstructions` and `textOptions` overrides.

### Template Registry

Custom templates are registered in `state/config/style_guide.yaml` → `tool_parameters.gamma.templates`:

```yaml
gamma:
  templates:
    # Scope → gammaId mapping
    - scope: "C1"                              # Course-level default
      content_type: "lecture-slides"
      gamma_id: "gamma_abc123"
      description: "JCPH branded lecture template for Course 1"
    - scope: "C1 > M1"                         # Module-level override
      content_type: "data-visualization"
      gamma_id: "gamma_def456"
      description: "Dark navy data viz template for Module 1"
    - scope: "*"                               # Global fallback
      content_type: "module-intro"
      gamma_id: "gamma_ghi789"
      description: "Bold intro slide template — all courses"
```

### Template Resolution Order

1. Check for `template_id` in context envelope (Marcus explicitly specified)
2. Check registry for scope + content_type match (most specific scope wins: lesson > module > course > global)
3. If template found: recommend to Marcus. If Marcus confirms or envelope already contains it, use from-template endpoint
4. If no template found: fall back to text generation with parameter templates above

### Template vs Text Generation

| Scenario | Endpoint | Notes |
|----------|---------|-------|
| `template_id` in envelope | from-template | Template encodes visuals; `template_prompt` provides content |
| Registry match found, no override | Recommend template to Marcus | Gary suggests, Marcus decides |
| No template available | text generation | Use content-type parameter templates above |
| Woodshed faithful reproduction | text generation | Exemplar reproduction uses precise parameter control, not templates |

### Template + Exemplar Relationship

A custom Gamma template can itself be an exemplar source — the template defines the visual pattern, and an exemplar validates that Gary can produce quality output using that template. When creating exemplars from templates, the exemplar's `reproduction-spec.yaml` should use the from-template endpoint with the `gammaId` rather than text generation parameters.

## Usage (Fallback — No Template)

When Marcus delegates a content type Gary doesn't have a template for, Gary:
1. Analyzes the request characteristics (content density, visual complexity, pedagogical function)
2. Selects the closest parameter template as a starting point
3. Adjusts parameters based on specific requirements
4. Documents the new combination in `patterns.md` if it produces good results
