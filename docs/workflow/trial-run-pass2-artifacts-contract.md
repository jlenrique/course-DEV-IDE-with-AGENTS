# Trial Run Pass 2 Artifacts Contract

Purpose: define lightweight, canonical structures for prompt-pack artifacts used in Marcus -> Irene Pass 2 trial runs.

Scope:
- Source authority map rows
- ingestion-evidence.md
- irene-packet.md
- g2-slide-brief.md
- gary-slide-content.json
- gary-fidelity-slides.json
- gary-diagram-cards.json
- literal-visual-operator-packet.md
- gary-theme-resolution.json
- gary-outbound-envelope.yaml
- authorized-storyboard.json
- variant-selection.json (double-dispatch runs only)
- motion-designations.json and motion_plan.yaml (motion-enabled runs only)

Core invariant:
- Each slide has exactly one mode: creative, literal-text, or literal-visual.
- Mixed-mode slides are not allowed.

## 1) Source Authority Map Row

Use one row per source in Prompt 2.

Required fields:
- source_id: stable short ID (e.g., SRC-PRIMARY-PDF-01)
- source_type: local_pdf | notion_page | box_file | playwright_html | url
- authority_level: primary | framing-only | excluded
- downstream_consumers_direct: list of direct consumers of this source
- downstream_consumers_indirect: list of agents consuming derived artifacts only
- extraction_pathway: official source-wrangler pathway used
- expected_confidence: high | medium | low
- known_risks: list of short risk statements

Rule:
- Vera is usually an indirect consumer (via source bundle), not a direct consumer of raw source files.

## 2) ingestion-evidence.md

Use a markdown table with one row per ingested source.

Required columns:
- source_id
- pathway_used
- extraction_status: pass | warn | fail
- coverage_metric: human-readable ratio or percentage
- confidence: high | medium | low
- bundle_location
- provenance_summary
- planning_readiness: ready | conditional | blocked

Confidence inheritance rules:
- If `extracted.md` includes a source-level confidence statement from an official bridge or Source Wrangler pathway, downstream artifacts must inherit that level unless a later reviewer records an explicit downgrade with evidence.
- A `high` confidence source may still carry non-blocking caution text (for example, minor wording variance on smallest labels). That caution does not by itself force `planning_readiness` below `ready`.
- Only `medium` or `low` confidence on planning-critical content, or an explicit evidenced downgrade, triggers conditional/blocked handling and spot-check escalation.

Validator parsing compatibility notes:
- Source extraction headings are accepted as either `## <source_id> — sensory bridge (G0)` or `## <source_id> - sensory bridge (G0)`.
- Ingestion lines may use either `on \`<absolute-or-relative-path>\`` or `source file <path>; ...` formats.

Minimum footer block:
- preflight_reference: path to preflight-results.json
- blocked_sources: comma-separated source_id list or none
- next_action: one line

## 3) irene-packet.md

Required sections in this order:
1. Executive framing
2. Normalized concept map
3. CLO-ranked opportunities
4. Conflict and ambiguity notes
5. Recommendation set with source anchors
6. Fidelity-sensitive zones (literal-text, literal-visual candidates)
7. Dispatch readiness note for Irene Pass 1

Rules:
- Every recommendation must include a source anchor.
- Any low-confidence recommendation must be labeled.
- A non-blocking caution inherited from a `high` confidence source should be surfaced as HIL context only; it must not be rewritten downstream as a blocker without explicit evidence.

Gate 1 decision framing:
- Include one explicit decision line summarizing:
  - total planned slides
  - mode distribution
  - CLO coverage summary
  - confidence warnings requiring HIL attention

## 4) g2-slide-brief.md

Purpose: machine-friendly extraction of Irene Pass 1 slide plan for Gary pre-dispatch checks.

Required sections:
1. Header: run_id, lesson_slug, source artifact path
2. Slide index table with columns:
   - slide_number
   - mode (creative | literal-text | literal-visual)
   - CLO
   - source_anchors
   - literal_requirements
3. Gate 1 alignment summary

Rule:
- `g2-slide-brief.md` is derived from `irene-pass1.md` and should not introduce new pedagogical content.

## 5) gary-fidelity-slides.json

Purpose: canonical machine payload for per-slide fidelity and queue split.

JSON schema (lightweight):

```json
{
  "run_id": "string",
  "lesson_slug": "string",
  "slides": [
    {
      "slide_number": 1,
      "fidelity": "creative",
      "fidelity_rationale": "string",
      "source_anchors": ["string"],
      "queue": "creative"
    }
  ]
}
```

Rules:
- `fidelity` must be one of: creative, literal-text, literal-visual.
- `queue` must be: creative for creative slides; literal for literal-text and literal-visual slides.
- slide_number values must be unique and strictly increasing.

## 5A) gary-slide-content.json

Purpose: canonical content-bearing machine payload for Gary dispatch input.

JSON schema (lightweight):

```json
{
  "run_id": "string",
  "lesson_slug": "string",
  "slides": [
    {
      "slide_number": 1,
      "content": "string",
      "source_ref": "string"
    }
  ]
}
```

Rules:
- One row per slide_number in the planned deck.
- content must be non-empty for every slide.
- source_ref must be non-empty for every slide.
- For literal-visual slides, `content` must be URL-only (HTTPS image URL or APP-staged URL); explanatory/support text on-slide is not allowed and must move to narration/script.
- This artifact carries the generation text payload. `gary-fidelity-slides.json` carries mode/fidelity metadata and queue split.

## 6) gary-diagram-cards.json

Purpose: literal-visual card mapping for Gary dispatch, supporting either already-hosted HTTPS images or tracked-mode local preintegration PNG staging.

JSON schema (lightweight):

```json
{
  "run_id": "string",
  "cards": [
    {
      "card_number": 3,
      "image_url": "https://...",
      "preintegration_png_path": "course-content/staging/.../diagram-03.png",
      "source_asset": "`metadata.json#media_references[2]`",
      "source_ref": "`extracted.md#Extracted text (roadmap transcription)`",
      "derivation_type": "source-crop",
      "placement_note": "Primary visual, full-width",
      "required": true
    }
  ]
}
```

Rules:
- Provide exactly one dispatch-ready image source per card:
  - **Hosted path:** `image_url` is HTTPS and content-type resolvable as image.
  - **Tracked-mode staged path:** `preintegration_png_path` points to a local source PNG that APP will publish to managed Git hosting immediately before Gary dispatch.
- If `preintegration_png_path` is used, the dispatch envelope must also supply `site_repo_url`, execution mode must be tracked/default, and the resulting dispatch payload must record additive `literal_visual_publish` metadata with `preintegration_ready=true` before Gate 2 review.
- In ad-hoc mode, `preintegration_png_path` is not allowed for production dispatch; pre-host the image and provide HTTPS `image_url` instead.
- `required=true` means dispatch must block if image is unavailable.
- `source_asset` must point to the Irene-approved origin for the literal-visual card.
- `source_ref` must point to the governing source text or structured extraction used to justify the card.
- `derivation_type` must be explicit for auditability: `source-crop`, `rebranded-source`, `user-provided-exact`, or `generated-image`.
- If Irene Pass 1 specifies `image_treatment: source-crop` or equivalent non-fabrication language, `derivation_type` must be source-derived and `image_url` must not point to Gamma `generated-images` output.
- Literal-visual presentation policy is full-slide image-only. Any explanatory text belongs in Irene Pass 2 narration, not on the slide payload.

## 7) gary-theme-resolution.json

Purpose: frozen theme mapping handshake artifact carried from pre-dispatch to dispatch.

Required fields:
- requested_theme_key
- resolved_theme_key
- resolved_parameter_set
- mapping_source
- mapping_version
- user_confirmation

Rule:
- This artifact must be carried forward unchanged from pre-dispatch into dispatch outputs.

## 8) gary-outbound-envelope.yaml

Purpose: final machine envelope for Gary dispatch.

Required fields:
- schema_version
- exemplar_references
- governance.allowed_outputs (must include gary_slide_output)
- fidelity_per_slide (or equivalent mapped payload)
- theme_resolution block (matching gary-theme-resolution.json)

Carry-forward integrity rule:
- `theme_resolution` and `fidelity_per_slide` values in `gary-outbound-envelope.yaml` must be carried forward unchanged from `gary-theme-resolution.json` and `gary-fidelity-slides.json`.

## 8A) authorized-storyboard.json

Purpose: canonical approved storyboard payload for all downstream work after Gate 2.

Rules:
- Must represent the authoritative approved deck for the run.
- If double-dispatch was enabled, this artifact must contain only the selected winner deck, never unresolved A/B variants.
- Downstream motion planning and Irene Pass 2 consume this artifact, not the raw storyboard review payload.

Storyboard review surface notes:
- `storyboard/storyboard.json` remains the canonical machine-readable manifest.
- `storyboard/index.html` is a static reviewer projection of that manifest, not a separate source of truth.
- The HTML review surface should present slide thumbnails, script status/text, script notes, orientation/provenance metadata, and related assets in a form usable for human Gate 2 review.
- Review HTML must stay view-only; approval is captured conversationally and then persisted through `authorized-storyboard.json`.

## 8B) variant-selection.json

Purpose: per-slide winner selection record for double-dispatch runs.

Required fields:
- run_id
- timestamp
- selections (per-slide selected variant)
- operator confirmation flag

Rules:
- Required only when `DOUBLE_DISPATCH` is enabled.
- Every slide in the reviewed deck must have exactly one selected variant before authorization can collapse the deck.

## 8C) motion-designations.json

Purpose: operator's Gate 2M choices captured before motion plan application.

Required fields per slide:
- slide_id
- motion_type (`static` | `video` | `animation`)
- optional motion_brief
- optional guidance_notes

Rules:
- Required only when `MOTION_ENABLED` is true.
- Must cover every slide in the authorized winner deck.
- Unknown slide IDs or omitted authorized slides are blocking contract failures.

## 8D) motion_plan.yaml

Purpose: run-scoped motion sidecar that binds Gate 2M choices to the authorized winner deck and later records approved/imported assets.

Required fields:
- run_id
- motion_enabled
- motion budget fields
- per-slide rows keyed to authorized slide IDs

Rules:
- Required only when `MOTION_ENABLED` is true.
- Must be derived from `authorized-storyboard.json`, not unresolved storyboard review payloads.
- Static runs skip this artifact entirely.
- Irene Pass 2 hydrates manifest motion fields from this sidecar and fails closed on incomplete coverage for non-static rows.

## 9) Vera Gate Contracts (Authority Source)

Gate contracts live in: `state/config/fidelity-contracts/`

- G0: `g0-source-bundle.yaml`
- G1: `g1-lesson-plan.yaml`
- G2: `g2-slide-brief.yaml`
- G3: `g3-generated-slides.yaml`
- G4: `g4-narration-script.yaml` (8 criteria, incl. G4-07 source depth utilization and G4-08 perception lineage binding)

Shared schema: `state/config/fidelity-contracts/_schema.yaml`

### G4 supporting config files

The G4 narration contract depends on two peer config files that govern Irene's
narration strategy. G4-07 evaluation explicitly references both:

- `state/config/narration-grounding-profiles.yaml` — per-fidelity channel balance
  (creative: source-primary; literal-text: slide-primary; literal-visual: balanced)
- `state/config/narration-script-parameters.yaml` — script-wide style knobs
  (density, slide_echo, visual_narration, terminology, bridging, engagement,
  source_depth, pronunciation)

These files are consumed by Irene Pass 2 during generation and by Vera during
G4 evaluation. Changes to profile defaults may cause G4-07 failures — check
config alignment before attributing failures to narration writing quality.

## 10) literal-visual-operator-packet.md

Purpose: deterministic operator checkpoint artifact that binds Irene literal-visual
requirements to user preintegration build actions before Gary dispatch.

Required fields per literal-visual slide row:
- slide_number
- graphic_id
- source_anchors
- extracted_context_summary
- labels_or_claims_to_preserve
- prohibited_embellishments
- acceptance_checks
- preintegration_png_path
- operator_ready (true | false)

Rules:
- Prompt 7 dispatch is blocked until every `required=true` literal-visual card is
  `operator_ready=true`.
- Packet content must be derived from Irene Pass 1 literal-visual cards and
  `gary-diagram-cards.json` only; do not invent new pedagogical requirements.

## 11) Validation Policy

Before Gary dispatch:
- required files must exist:
  - g2-slide-brief.md
  - gary-slide-content.json
  - gary-fidelity-slides.json
  - gary-diagram-cards.json
  - literal-visual-operator-packet.md (required when any literal-visual slide exists)
  - gary-theme-resolution.json
  - gary-outbound-envelope.yaml
- all files must satisfy the field rules in this contract.

Contract version: 1.0
