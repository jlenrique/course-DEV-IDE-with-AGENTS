# Schema Changelog

Authoritative record of extraction-report schema versions and the contracts pinned by `skills/bmad-agent-texas/scripts/retrieval/contracts.py`. Every non-patch bump requires a new entry here — the schema-pin contract test (`tests/contracts/test_acceptance_criteria_schema_stable.py`) enforces this gate.

Per semver-for-schemas:
- **Major (X.0)** — breaking: renamed field, changed type, removed field, changed required↔optional for an existing field.
- **Minor (1.X)** — additive only: new optional fields with v1.0-compatible defaults, new enum values that don't break old consumers.
- **Patch (1.0.X)** — docs / clarifications / typo fixes; no machine-readable change.

## Lesson Plan v1.0 — 2026-04-18 — Story 31-1 Lesson Plan Schema Foundation

**Type:** Initial shape (no predecessor).

**Reason for introduction:** Lesson Planner MVP foundation (R1 orchestrator
ruling amendment 5). Ships the `LessonPlan` / `PlanUnit` / `Dials` /
`IdentifiedGap` primitives + the `schema_version: "1.0"` root field + the
`weather_band` abundance-framed enum (gold / green / amber / gray; no red).

**Shapes pinned:**

- `LessonPlan`: `schema_version`, `learning_model`, `structure`, `plan_units`,
  `revision`, `updated_at`, `digest`.
- `PlanUnit`: `unit_id`, `event_type`, `source_fitness_diagnosis`,
  `scope_decision`, `weather_band`, `modality_ref`, `rationale`, `gaps`,
  `dials`.
- `Dials`: `enrichment`, `corroboration` (both `float | None` in `[0.0, 1.0]`).
- `IdentifiedGap`: `gap_id`, `description`, `suggested_posture`
  (`embellish | corroborate | gap_fill`).

**Anti-patterns locked down:** `rationale` is free text verbatim (no trimming,
no coercion, no enum); `weather_band` rejects `"red"` at three validation
layers.

**Migration**: N/A (initial shape; no predecessor artifacts exist).

## Fit Report v1.0 — 2026-04-18 — Story 31-1 Lesson Plan Schema Foundation

**Type:** Initial shape (absorbed from original 29-1 per R1 ruling amendment 5).

**Reason for introduction:** Irene's diagnostic output carrier. 31-1 ships
the shape only; 29-1 ships the validator + serializer + emission wiring on
top of the shape.

**Shapes pinned:**

- `FitReport`: `schema_version`, `source_ref`, `plan_ref`, `diagnoses`,
  `generated_at`, `irene_budget_ms`.
- `FitDiagnosis`: `unit_id`, `fitness` (`sufficient | partial | absent`),
  `commentary`, `recommended_scope_decision`, `recommended_weather_band`.

**Migration**: N/A (initial shape; no predecessor artifacts exist).

## Scope Decision v1.0 — 2026-04-18 — Story 31-1 Lesson Plan Schema Foundation

**Type:** Initial shape (absorbed from 30-3a / implicit 31-1 per R1 ruling
amendment 5; R2 rider S-4 adds the two-level actor surface; R2 rider W-1
adds the generic event envelope; R2 rider Q-5 adds the locked-bypass guard).

**Reason for introduction:** Jurisdictional primitive for the Lesson
Planner bilateral typed contract. Maya is the sole signatory; internal
audit tooling receives a separate private actor surface.

**Shapes pinned:**

- `ScopeDecision`: `state` (`proposed | ratified | locked`), `scope`
  (`in-scope | out-of-scope | delegated | blueprint`), `proposed_by`
  (`system | operator` — public), `internal_proposed_by` (five-valued
  internal Marcus-duality taxonomy; `Field(exclude=True)` +
  `SkipJsonSchema`), `ratified_by` (`"maya" | None`), `locked_at`.
- `ScopeDecisionTransition`: `event_type` (Literal
  `"scope_decision_transition"`), `unit_id`, `plan_revision`, `from_state`,
  `to_state`, `from_scope`, `to_scope`, `actor` (`system | operator` —
  public), `internal_actor` (private + `SkipJsonSchema`), `timestamp`,
  `rationale_snapshot`.
- `EventEnvelope`: `event_id`, `timestamp`, `plan_revision`, `event_type`,
  `payload`. Generic envelope every future log event in 31-2 conforms to.

**Anti-patterns locked down:** direct `state="locked", ratified_by=None`
construction is rejected by a `model_validator(mode="after")` bypass guard
(Q-5); `_internal_proposed_by` and `_internal_actor` never leak into
default `model_dump` or the published JSON Schema.

**Migration**: N/A (initial shape; no predecessor artifacts exist).

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
