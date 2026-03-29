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
  additionalInstructions: "Chart layout with labeled axes"  # creative slides only — literal slides use fidelity-control vocabulary (text_treatment, image_treatment, layout_constraint, content_scope) via merge_parameters()
run_mode: "default"                         # default | ad-hoc
governance:
  invocation_mode: "delegated"             # delegated | standalone
  current_gate: "G3"
  authority_chain: ["marcus", "quality-reviewer"]
  decision_scope:
    owned_dimensions:
      - "tool_execution_quality.slides"
    restricted_dimensions:
      - "source_fidelity"
      - "quality_standards"
      - "instructional_design"
  allowed_outputs:
    - "artifact_paths"
    - "gary_slide_output"
    - "quality_assessment"
    - "parameter_decisions"
    - "recommendations"
    - "flags"

# FIDELITY — per-slide classification from Irene's slide brief (Story 3.11)
fidelity_per_slide:                          # populated by Marcus from Irene's slide brief
  - slide_number: 1
    fidelity: "creative"                     # creative | literal-text | literal-visual
  - slide_number: 10
    fidelity: "literal-text"
    fidelity_rationale: "Knowledge check teaser — exact topics from source"

fidelity_guidance:                           # user's fidelity preferences from Marcus discovery
  literal_visuals:
    - description: "Dual-axis chart from page 7"
      source_ref: "TEJAL_Notes.pdf#page7"
      rebranded_asset_path: "course-content/staging/.../rebranded-assets/slide-03-chart.png"
  literal_text:
    - description: "10 KC topics from Chapters 2 & 3"
      source_ref: "extracted.md#Chapter 2 Knowledge Check"

diagram_cards:                               # literal-visual slides with hosted image URLs
  - card_number: 3
    image_url: "https://gamma.app/hosted/..."  # HTTPS, publicly accessible, image extension
    placement_note: "Primary visual, full-width"
    required: true

# DECK MODE — multi-slide generation
deck_mode: false                            # true = apply deck parameter guidance
num_cards: null                             # explicit override; null = Gary decides per content type
card_split: "auto"                          # auto | inputTextBreaks
theme_selection_required: false             # true = Gary presents TP preview before generating
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
| `governance` | yes | — | Delegation authority contract: invocation mode, gate, authority chain, decision scope, allowed outputs |
| `deck_mode` | no | `false` | When `true`, applies deck-specific parameter guidance (numCards ranges, cardSplit, deck additionalInstructions) |
| `num_cards` | no | null | Explicit numCards override; null = Gary decides per content type guidance |
| `card_split` | no | `"auto"` | `"auto"` (Gamma decides) or `"inputTextBreaks"` (split on `\n---\n`) |
| `theme_selection_required` | no | `false` | When `true`, Gary presents theme/template preview (TP capability) and waits for selection before generating |

### Governance Enforcement

Before generation, Gary validates:

- planned outputs are a subset of `governance.allowed_outputs`
- planned judgments stay within `governance.decision_scope.owned_dimensions` (canonical values in `docs/governance-dimensions-taxonomy.md`)

If not, Gary must return a scope violation to `governance.authority_chain[0]` and not execute out-of-scope work.

`scope_violation.route_to` must equal `governance.authority_chain[0]`.

## Outbound Return (Gary → Marcus)

```yaml
schema_version: "1.0"
production_run_id: "C1-M1-P2S1-VID-001"
status: "success"                           # success | revision_needed | failed

artifact_paths:
  - "course-content/staging/C1-M1-P2S1-slide-001.pdf"
  - "course-content/staging/C1-M1-P2S1-slides/card-01.png"
  - "course-content/staging/C1-M1-P2S1-slides/card-02.png"

# Pipeline field: passed to Irene Pass 2 as gary_slide_output
gary_slide_output:
  - slide_id: "C1-M1-P2S1-card-01"
    file_path: "course-content/staging/C1-M1-P2S1-slides/card-01.png"
    card_number: 1
    visual_description: "Economic overview: three-column comparison of physician practice models across decades"
    source_ref: "slide-brief.md#Slide 1"     # Provenance: traces this generated card back to its slide brief source
  - slide_id: "C1-M1-P2S1-card-02"
    file_path: "course-content/staging/C1-M1-P2S1-slides/card-02.png"
    card_number: 2
    visual_description: "Revenue gap timeline: dual-axis chart with declining solo practice revenue vs. consolidation trend"
    source_ref: "slide-brief.md#Slide 2"     # Provenance: traces this generated card back to its slide brief source

quality_assessment:
  overall_score: 0.87
  dimensions:
    layout_integrity: 0.9
    parameter_confidence: 0.84
    embellishment_risk_control: 0.87
  embellishment_detected: true
  embellishment_details:
    - "Gamma added subtitle 'Bridging Two Worlds' not in input"

provenance:                                  # per-card fidelity provenance (Story 3.11)
  - card_number: 1
    source_call: "creative"                  # creative | literal (which Gamma API call)
    generation_id: "abc123"                  # Gamma generation ID
    fidelity: "creative"                     # fidelity class from slide brief
  - card_number: 10
    source_call: "literal"
    generation_id: "def456"
    fidelity: "literal-text"

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

scope_violation: null                        # object when out-of-scope work is requested
```

### Return Field Rules

| Field | Always Present | Notes |
|-------|:--------------:|-------|
| `schema_version` | yes | Match inbound version |
| `production_run_id` | yes | Echo from inbound |
| `status` | yes | `success`, `revision_needed`, or `failed` |
| `artifact_paths` | yes | Empty array if failed; includes both PDF (review) and PNG per card (production) |
| `gary_slide_output` | yes | Array of `{slide_id, file_path, card_number, visual_description, source_ref}` — one per generated card; passed to Irene Pass 2. `source_ref` traces each card to its slide brief origin. |
| `quality_assessment` | yes | Structured execution-quality scores (`layout_integrity`, `parameter_confidence`, `embellishment_risk_control`); see quality-assessment.md |
| `generation_mode` | yes | `"text"` or `"from-template"` — which endpoint was used |
| `template_used` | if from-template | The `gammaId` used; null for text generation |
| `parameter_decisions` | yes | Exact Gamma API params used (for learning and reproducibility) |
| `recommendations` | yes | Empty array if none; human-readable notes for Marcus |
| `flags` | yes | Embellishment control, constraint effectiveness |
| `save_to_style_guide` | if default mode | Params to persist; absent in ad-hoc mode |
| `errors` | yes | Empty array if none; structured error details if failed |
| `memory_mode` | yes | Echo the active run mode |
| `scope_violation` | if out-of-scope | `{detected, reason, requested_work, route_to, details}` for authority-chain rerouting |
