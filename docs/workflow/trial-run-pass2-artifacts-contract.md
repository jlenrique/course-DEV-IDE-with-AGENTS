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
- gary-theme-resolution.json
- gary-outbound-envelope.yaml

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
- This artifact carries the generation text payload. `gary-fidelity-slides.json` carries mode/fidelity metadata and queue split.

## 6) gary-diagram-cards.json

Purpose: literal-visual card mapping with hosted image locations for Gary dispatch.

JSON schema (lightweight):

```json
{
  "run_id": "string",
  "cards": [
    {
      "card_number": 3,
      "image_url": "https://...",
      "placement_note": "Primary visual, full-width",
      "required": true
    }
  ]
}
```

Rules:
- `image_url` must be HTTPS and content-type resolvable as image.
- `required=true` means dispatch must block if image is unavailable.

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

## 9) Vera Gate Contracts (Authority Source)

Gate contracts live in: `state/config/fidelity-contracts/`

- G0: `g0-source-bundle.yaml`
- G1: `g1-lesson-plan.yaml`
- G2: `g2-slide-brief.yaml`
- G3: `g3-generated-slides.yaml`
- G4: `g4-narration-script.yaml`

Shared schema: `state/config/fidelity-contracts/_schema.yaml`

## 10) Validation Policy

Before Gary dispatch:
- required files must exist:
  - g2-slide-brief.md
  - gary-fidelity-slides.json
  - gary-diagram-cards.json
  - gary-theme-resolution.json
  - gary-outbound-envelope.yaml
- all files must satisfy the field rules in this contract.

Contract version: 1.0
