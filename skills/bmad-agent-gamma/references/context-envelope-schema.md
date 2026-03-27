# Context Envelope Schema

Defines the contract between Marcus (sender) and Gary (receiver) for delegated slide production.

## Inbound Envelope (Marcus → Gary)

```yaml
schema_version: "1.0"

# REQUIRED — Gary will not proceed without these
production_run_id: "C1-M1-P2S1-VID-001"
content_type: "data-visualization"          # See content-type-mapping.md for valid types
input_text: |
  U.S. healthcare spending continues to rise...

# REQUIRED — Gary flags to Marcus if missing
learning_objectives:
  - "Analyze macro-economic trends (CLO #2, Bloom's: Analyze)"

# OPTIONAL — Gary uses defaults if absent
module_lesson: "C1 > M1 > Part 2 > Slide 1"
user_constraints:
  - "Dark navy background, not light"
  - "Dual-axis layout: line graph left, bar charts right"
style_bible_sections:
  - "Chart and Data Visualization"
  - "Color Palette — Primary and Supporting"
  - "Typography System"
exemplar_references:
  - "L1-two-processes-one-mind"
export_format: "png"                        # png | pdf | pptx (default: png for production)
template_id: null                           # Gamma gammaId — if set, use from-template endpoint
template_prompt: null                       # prompt text for template-based generation
parameters_ready: false                     # true = skip greet/mastery, fast-path to execution
parameter_overrides:                        # explicit Gamma API params that override all defaults
  numCards: 1
  textMode: "preserve"
  additionalInstructions: "Chart layout with labeled axes"
run_mode: "default"                         # default | ad-hoc
```

### Field Rules

| Field | Required | Default | Notes |
|-------|:--------:|---------|-------|
| `schema_version` | yes | — | Currently `"1.0"` |
| `production_run_id` | yes | — | Unique run identifier for state tracking |
| `content_type` | yes | — | Must map to a known type in content-type-mapping.md |
| `input_text` | yes | — | The source content for slide generation |
| `learning_objectives` | yes | — | Gary flags to Marcus if missing; never guesses |
| `module_lesson` | no | null | Course hierarchy context for metadata |
| `user_constraints` | no | [] | Free-text constraints from the user |
| `style_bible_sections` | no | [] | Specific sections Gary should re-read from style bible |
| `exemplar_references` | no | [] | Exemplar IDs for pattern matching |
| `export_format` | no | `"png"` | PNG for production (video/embed), PDF for review/archival, PPTX for editing |
| `template_id` | no | null | Gamma `gammaId` for template-based generation; when set, Gary uses `POST /generations/from-template` instead of text generation |
| `template_prompt` | no | null | Prompt text for template-based generation; required when `template_id` is set |
| `parameters_ready` | no | `false` | When `true`, triggers expert fast-path |
| `parameter_overrides` | no | {} | Explicit Gamma API params; override all merge levels |
| `run_mode` | no | `"default"` | Controls memory write behavior |

## Outbound Return (Gary → Marcus)

```yaml
schema_version: "1.0"
production_run_id: "C1-M1-P2S1-VID-001"
status: "success"                           # success | revision_needed | failed

artifact_paths:
  - "course-content/staging/C1-M1-P2S1-slide-001.pdf"

quality_assessment:
  overall_score: 0.87
  dimensions:
    brand_compliance: 0.9
    content_fidelity: 0.85
    layout_integrity: 0.9
    accessibility: 1.0
    pedagogical_alignment: 0.8
  embellishment_detected: true
  embellishment_details:
    - "Gamma added subtitle 'Bridging Two Worlds' not in input"

generation_mode: "text"                     # text | from-template
template_used: null                         # gammaId if from-template, null if text generation

parameter_decisions:
  theme_id: "theme_abc123"
  text_mode: "preserve"
  additional_instructions: "Two-column parallel comparison layout. Output ONLY provided text."
  text_options:
    amount: "brief"
  image_options:
    source: "noImages"
  export_as: "pdf"

recommendations:
  - "Content fidelity below 0.9 — recommend human review of added subtitle"
  - "Consider accepting subtitle if it aids comprehension"

flags:
  embellishment_control_used: true
  constraint_phrasing: "Output ONLY the provided text. Do not add content."
  constraint_effectiveness: 0.85

save_to_style_guide:
  theme_preference: "theme_abc123"
  effective_constraint: "Output ONLY the provided text. Do not add content."

errors: []

memory_mode: "default"
```

### Return Field Rules

| Field | Always Present | Notes |
|-------|:--------------:|-------|
| `schema_version` | yes | Match inbound version |
| `production_run_id` | yes | Echo from inbound |
| `status` | yes | `success`, `revision_needed`, or `failed` |
| `artifact_paths` | yes | Empty array if failed |
| `quality_assessment` | yes | Structured scores; see quality-assessment.md for dimensions |
| `generation_mode` | yes | `"text"` or `"from-template"` — which endpoint was used |
| `template_used` | if from-template | The `gammaId` used; null for text generation |
| `parameter_decisions` | yes | Exact Gamma API params used (for learning and reproducibility) |
| `recommendations` | yes | Empty array if none; human-readable notes for Marcus |
| `flags` | yes | Embellishment control, constraint effectiveness |
| `save_to_style_guide` | if default mode | Params to persist; absent in ad-hoc mode |
| `errors` | yes | Empty array if none; structured error details if failed |
| `memory_mode` | yes | Echo the active run mode |
