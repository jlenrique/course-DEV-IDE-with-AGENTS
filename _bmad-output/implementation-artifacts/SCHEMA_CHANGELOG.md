# Schema Changelog

Authoritative record of extraction-report schema versions and the contracts pinned by `skills/bmad-agent-texas/scripts/retrieval/contracts.py`. Every non-patch bump requires a new entry here — the schema-pin contract test (`tests/contracts/test_acceptance_criteria_schema_stable.py`) enforces this gate.

Per semver-for-schemas:
- **Major (X.0)** — breaking: renamed field, changed type, removed field, changed required↔optional for an existing field.
- **Minor (1.X)** — additive only: new optional fields with v1.0-compatible defaults, new enum values that don't break old consumers.
- **Patch (1.0.X)** — docs / clarifications / typo fixes; no machine-readable change.

## v1.1 — 2026-04-18 — Story 27-0 Retrieval Foundation

**Type:** Minor (additive, backwards-compatible)

**Reason for bump:** Shape 3-Disciplined retrieval architecture (Epic 27) adds retrieval-shape provenance to the per-source entry in `extraction-report.yaml`. Every new field is optional with a v1.0-compatible default so pre-Shape-3 consumers remain correct. See `skills/bmad-agent-texas/references/extraction-report-schema.md#changelog` for the full migration note.

**Additive fields (all optional, default to null / false / []):**

- `sources[].retrieval_intent: string | null`
- `sources[].provider_hints: list[{provider, params}]`
- `sources[].cross_validate: boolean`
- `sources[].convergence_signal: {providers_agreeing, providers_disagreeing, single_source_only} | null`
- `sources[].source_origin: "operator-named" | "tracy-suggested"` (default `operator-named`)
- `sources[].tracy_row_ref: string | null`

**Contracts pinned (`retrieval/contracts.py`):**

- `RetrievalIntent` — `intent`, `provider_hints: list[ProviderHint]`, `kind`, `acceptance_criteria`, `iteration_budget`, `convergence_required`, `cross_validate`
- `ProviderHint` — `provider`, `params` (AC-C.10, Winston MUST-FIX #2)
- `AcceptanceCriteria` — `mechanical`, `provider_scored`, `semantic_deferred`
- `TexasRow` — `source_id`, `title`, `body`, `authors`, `date`, `provider`, `provider_metadata`, `source_origin`, `tracy_row_ref`, `convergence_signal`, `authority_tier`, `completeness_ratio`, `structural_fidelity`
- `ConvergenceSignal` — `providers_agreeing`, `providers_disagreeing`, `single_source_only` (structural per AC-C.11 dumbness clause)
- `ProviderInfo` — `id`, `shape`, `status`, `capabilities`, `auth_env_vars`, `spec_ref`, `notes` (AC-B.8 operator amendment 2026-04-18)

**Consumer compatibility matrix:**

| Consumer reads | Writer emits v1.0 | Writer emits v1.1 |
|---|---|---|
| v1.0 | ✓ native | ✓ new fields invisible (ignored) |
| v1.1 | ✓ new fields default | ✓ native |

**Rollback:** N/A — no breaking change. Revert via `schema_version: "1.0"` on writer side; consumers continue to work.

## v1.0 — pre-2026-04-18 — baseline

Original extraction-report schema shipped with Epic 25 (Story 25-1, Texas runtime wrangling runner). See `skills/bmad-agent-texas/references/extraction-report-schema.md` (v1.0 block) for the baseline field set.
