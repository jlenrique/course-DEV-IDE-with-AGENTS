# Trial Run Pass 2 Artifacts Contract

Purpose: define lightweight, canonical structures for prompt-pack artifacts used in Marcus -> Irene Pass 2 trial runs.

Scope:
- run-constants.yaml (optional file; when present, validated by tooling — see §1B)
- Source authority map rows
- operator-directives.md
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

## 1A) operator-directives.md

Purpose: record the operator's source-processing directives before ingestion begins.

This artifact is **mandatory**. Ingestion (Prompt 3) cannot proceed without either explicit directives or an explicit "no special directives" acknowledgment.

Required sections:
- run_id
- timestamp
- operator
- focus_directives: list of emphasis instructions (sections, topics, content to prioritize)
- exclusion_directives: list of content to ignore or deprioritize
- special_treatment_directives: list of content requiring non-default handling (fidelity overrides, routing overrides)

If the operator has no directives, the file must contain: `"No operator directives — process all source content at default authority levels."`

Governance rules:
- **Exclusion directives are scope-binding provenance records.** Vera G0 must not flag excluded content as an omission when the exclusion is recorded in this artifact.
- **Focus directives are emphasis signals.** They prioritize but do not exclude unmentioned content.
- **Special treatment directives override default fidelity classification** for the specified content only (e.g., forcing a section to literal-visual that would otherwise be creative).
- This artifact is a first-class input to Source Wrangler (ingestion), Irene (planning), and Vera (gate evaluation).
- Downstream agents must reference `operator-directives.md` by path in their provenance chains.

## 1B) run-constants.yaml

Purpose: machine-readable, **frozen** per-run values aligned with the v4 prompt pack “Run Constants” block (`RUN_ID`, `lesson_slug`, `bundle_path`, primary source path, optional context assets, theme keys, execution mode, quality preset).

Location: bundle root, filename **`run-constants.yaml`** (same directory as `metadata.json` / `extracted.md` once ingestion exists).

Governance:

- **bundle_path** must be repo-relative (forward slashes) and resolve to the directory that contains this file (the loader fails closed if the path does not match).
- Downstream scripts and session readiness may load this file; agents should still treat it as authoritative when present and must not contradict it in chat.
- Optional fields such as `schema_version`, `frozen_at_utc`, and `frozen_note` are allowed for operator audit.

Tooling:

- Load/validate: `python -m scripts.utilities.run_constants --bundle-dir <path> [--verify-paths] [--json]`
- Session readiness (optional): append `--bundle-dir <path>` to `app_session_readiness` when a frozen bundle exists — adds check `bundle_run_constants`.
- Source bundle confidence validator: if `run-constants.yaml` exists, validates it (CLI `--repo-root` only when the bundle is resolved against a non-default root, e.g. tests).

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
- operator_directive_applied: yes | no (if yes, include directive reference from operator-directives.md)

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

## 10) Validation Policy

Before Gary dispatch:
- required files must exist:
  - g2-slide-brief.md
  - gary-slide-content.json
  - gary-fidelity-slides.json
  - gary-diagram-cards.json
  - gary-theme-resolution.json
  - gary-outbound-envelope.yaml
- all files must satisfy the field rules in this contract.

Contract version: 1.2 (added run-constants.yaml §1B + tooling hooks; 1.1 operator-directives.md)
