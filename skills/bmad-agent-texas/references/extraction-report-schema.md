---
name: extraction-report-schema
description: Canonical schema for the extraction-report.yaml artifact emitted by run_wrangler.py
code: ERS
---

# Extraction Report Schema

## Purpose

`extraction-report.yaml` is Texas's canonical quality report for a source-wrangling run. It is written to `<bundle-dir>/extraction-report.yaml` by `skills/bmad-agent-texas/scripts/run_wrangler.py` and consumed by Marcus (who reads it into the production envelope) and Vera (who will read it when the Vera-side G0 gate runner lands as a follow-up story).

This schema is the single source of truth. The runner writes against it, tests validate against it, and any downstream consumer (Vera, HUD, trace-report tooling) keys off it.

## Schema Version

`schema_version: "1.0"` — bump on any breaking field change.

## Top-Level Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `schema_version` | string | yes | Literal `"1.0"` for this version |
| `run_id` | string | yes | From the wrangling directive; matches `run-constants.yaml` RUN_ID |
| `generated_at` | string (ISO 8601) | yes | UTC timestamp when the report was written |
| `overall_status` | string | yes | One of: `complete`, `complete_with_warnings`, `blocked` |
| `validator_version` | string | yes | Version of `extraction_validator.py` that produced the tier judgments (e.g., `"extraction_validator.py@2026-04-16"`) |
| `sources` | list[Source] | yes | One entry per source in the directive, in directive order |
| `cross_validation` | list[CrossValidationEntry] | yes | One entry per validation-role asset run; empty list when no validation assets |
| `evidence_summary` | list[string] | yes | 2-5 human-readable sentences summarizing the extraction session |
| `recommendations` | list[string] | no | Advisory, non-blocking actions for the operator |
| `blocking_issues` | list[BlockingIssue] | no | Present only when `overall_status == "blocked"` |

## Source Entry

Each element of `sources[]`:

| Field | Type | Required | Description |
|---|---|---|---|
| `ref_id` | string | yes | From the directive (`src-001`, etc.); unique across `sources[]` |
| `provider` | string | yes | `local_file` \| `pdf` \| `url` \| `notion` \| `playwright_html`. The runner rejects any other value at directive-load time. |
| `locator` | string | yes | Provider-specific address (path, URL, page ID) |
| `role` | string | yes | `primary` \| `validation` \| `supplementary` (directive must declare ≥1 primary; supplementary sources are recorded in provenance but do not contribute to `extracted.md`) |
| `tier` | string | yes | Enum name from `QualityTier`: `FULL_FIDELITY` \| `ADEQUATE_WITH_GAPS` \| `DEGRADED` \| `FAILED` |
| `tier_value` | integer | yes | 1, 2, 3, or 4 |
| `passed` | boolean | yes | `tier in (FULL_FIDELITY, ADEQUATE_WITH_GAPS)` |
| `counts` | Counts | yes | Word / line / heading counts + expected minimum |
| `structural_fidelity` | string | yes | `high` \| `medium` \| `low` \| `none` |
| `completeness_ratio` | float | yes | Actual / expected; rounded to 3 decimal places |
| `extractor_used` | string | yes | Which fetch helper produced the content (`pypdf`, `requests+html_to_text`, `notion_client`, `playwright_file`, `local_text_read`) |
| `fetched_at` | string (ISO 8601 UTC, `Z` suffix) | yes | Timestamp applied to every artifact produced in this run; identical across all artifacts for the same run |
| `content_path` | string \| null | yes | Relative path to the source's contribution to `extracted.md` for `role: primary` (always `"extracted.md"`); `null` for `role: validation` and `role: supplementary` because they do not contribute content to `extracted.md`. Consumers must tolerate the `null` case for non-primary sources. |
| `evidence` | list[string] | yes | Carried from `ExtractionReport.evidence`; the line beginning `"Expected minimum:"` is rewritten by the runner when the directive supplies an operator-declared floor so the trail does not lie about what was checked |
| `known_losses` | list[string] | yes | Carried from `ExtractionReport.known_losses`; empty list when none |
| `recommendations` | list[string] | yes | Per-source recommendations; empty list when none |

### Counts (sub-object)

```yaml
counts:
  words: <int>
  lines: <int>
  headings: <int>
  expected_min_words: <int>
```

## Cross-Validation Entry

Each element of `cross_validation[]`:

| Field | Type | Required | Description |
|---|---|---|---|
| `primary_ref_id` | string | yes | `ref_id` of the primary source this validates |
| `asset_ref_id` | string | yes | `ref_id` of the validation-role source |
| `asset_description` | string | yes | Human-readable description of the validation asset |
| `coverage_scope` | string | yes | From the directive (`full_module`, `part_1_only`, etc.) |
| `sections_in_reference` | integer | yes | Heading count in the validation asset |
| `sections_matched` | integer | yes | Headings also present (fuzzy match) in the extraction |
| `key_terms_total` | integer | yes | Key terms extracted from the validation asset |
| `key_terms_found` | integer | yes | Key terms also present in the primary extraction |
| `key_terms_coverage` | float | yes | `key_terms_found / key_terms_total`, rounded to 3 decimal places |
| `word_count_ratio` | float | yes | Primary extraction words / validation asset words, rounded to 2 decimal places |
| `verdict` | string | yes | Human-readable sentence, e.g. `"confirms extraction completeness for Part 1 scope"` |
| `passed` | boolean | yes | `key_terms_coverage >= 0.70 AND sections_matched > 0` |
| `missing_sections` | list[string] | yes | Up to 10 headings present in the reference but not in the extraction |
| `missing_key_terms` | list[string] | yes | Up to 10 key terms; capped per `cross_validator.py` |

## Blocking Issue

Each element of `blocking_issues[]` (present only when `overall_status == "blocked"`):

| Field | Type | Required | Description |
|---|---|---|---|
| `ref_id` | string | yes | Source that triggered the block |
| `reason` | string | yes | Short category: `insufficient_content` \| `fetch_failed` \| `unsupported_provider` \| `malformed_directive` |
| `detail` | string | yes | One-sentence human-readable explanation |
| `operator_question` | string | no | Direct question the operator can answer to unblock |

## Status Derivation Rules

The `overall_status` field is computed from the per-source `tier` values:

1. If any source has `tier == FAILED` → `overall_status: blocked`
2. Else if any source has `tier == DEGRADED` → `overall_status: blocked` (a future follow-up story will add a fallback chain between the FAILED/DEGRADED detection and the block decision; today's runner blocks immediately)
3. Else if any source has `tier == ADEQUATE_WITH_GAPS` → `overall_status: complete_with_warnings`
4. Else (all sources `FULL_FIDELITY`) → `overall_status: complete`

When the directive supplies an operator-declared `expected_min_words` floor, the runner re-derives the per-source tier using the override-adjusted completeness ratio (≥0.80 → FULL_FIDELITY, ≥0.50 → ADEQUATE_WITH_GAPS, ≥0.20 → DEGRADED, else FAILED). This keeps the tier-driven status derivation honest against operator expectations.

Cross-validation failures (`passed: false`) do not automatically block; they generate a warning in `evidence_summary` and may elevate `complete` to `complete_with_warnings` if a primary's cross-validation failed.

### Directive-level preconditions

Before any source is fetched the runner validates the directive shape. The following cases exit 30 (`directive/IO error`) before any artifact is written:

- Directive file missing, non-UTF-8, or non-YAML
- Directive root is not a mapping
- Required top-level fields (`run_id`, `sources`) missing
- `sources` is empty or not a list
- Any source missing `ref_id` / `provider` / `locator` / `role`
- `provider` not in the supported enum
- `role` not in `primary` / `validation` / `supplementary`
- Duplicate `ref_id` values across sources
- No `role: primary` source declared (at least one primary is required so `extracted.md` has content)

## Example

```yaml
schema_version: "1.0"
run_id: "C1-M1-PRES-20260417"
generated_at: "2026-04-17T05:12:00Z"
overall_status: "complete_with_warnings"
validator_version: "extraction_validator.py@2026-04-16"

sources:
  - ref_id: "src-001"
    provider: "local_file"
    locator: "course-content/courses/tejal-APC-C1/APC_C1-M1_Tejal_2026-03-29.pdf"
    role: "primary"
    tier: "ADEQUATE_WITH_GAPS"
    tier_value: 2
    passed: true
    counts:
      words: 4620
      lines: 512
      headings: 18
      expected_min_words: 4800
    structural_fidelity: "high"
    completeness_ratio: 0.963
    extractor_used: "pypdf"
    fetched_at: "2026-04-17T05:11:42Z"
    content_path: "extracted.md"
    evidence:
      - "Extracted 4620 words / 512 lines / 18 headings from 'APC_C1-M1_Tejal_2026-03-29.pdf'"
      - "Expected minimum: 4800 words (completeness ratio: 96.3%)"
      - "Structural fidelity: high"
      - "PASS WITH GAPS: Content is usable but has known losses"
    known_losses:
      - "Content may be 4% below expected volume"
    recommendations: []

cross_validation:
  - primary_ref_id: "src-001"
    asset_ref_id: "src-002"
    asset_description: "Part 1 MD reference"
    coverage_scope: "part_1_only"
    sections_in_reference: 6
    sections_matched: 6
    key_terms_total: 48
    key_terms_found: 44
    key_terms_coverage: 0.917
    word_count_ratio: 2.08
    verdict: "confirms extraction completeness for Part 1 scope"
    passed: true
    missing_sections: []
    missing_key_terms:
      - "pharmacokinetic half-life"
      - "dose adjustment nomogram"

evidence_summary:
  - "All 1 primary source extracted at Tier 2 (Adequate with Gaps)."
  - "Cross-validation against 1 reference asset passed (92% key-term coverage)."
  - "Primary source extraction is 4% below expected volume — acceptable for production."

recommendations: []
```

## Versioning

- `schema_version: "1.0"` is the initial version.
- Additive field changes (e.g., adding a new optional field to a Source entry) do NOT bump the version.
- Breaking changes (removing a field, changing a field's type, changing `status` enum values) bump the version and require updating `run_wrangler.py`, the tests, and any downstream consumer.

## Consumers

- **Marcus** — reads `overall_status`, `sources[].tier`, and `blocking_issues[]` to decide whether to proceed, surface warnings, or halt.
- **Vera (future G0 runner)** — reads the full report to apply `state/config/fidelity-contracts/g0-source-bundle.yaml` criteria and emit `gates/gate-03-result.yaml`.
- **HUD** — reads `overall_status` and per-source `tier` for dashboard rendering.
- **Trace-report tooling** — reads `evidence_summary` and `blocking_issues` for human-readable session logs.
