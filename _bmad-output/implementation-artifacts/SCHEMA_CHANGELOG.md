# Schema Changelog

Authoritative record of extraction-report schema versions and the contracts pinned by `skills/bmad-agent-texas/scripts/retrieval/contracts.py`. Every non-patch bump requires a new entry here — the schema-pin contract test (`tests/contracts/test_acceptance_criteria_schema_stable.py`) enforces this gate.

Per semver-for-schemas:
- **Major (X.0)** — breaking: renamed field, changed type, removed field, changed required↔optional for an existing field.
- **Minor (1.X)** — additive only: new optional fields with v1.0-compatible defaults, new enum values that don't break old consumers.
- **Patch (1.0.X)** — docs / clarifications / typo fixes; no machine-readable change.

## Modality Registry v1.0 — 2026-04-18 — Story 31-3 Registries

**Type:** Initial shape (no predecessor).

**Reason for introduction:** 31-3 ships the TARGETING SURFACE — the frozen
closed-set catalog of atomic producer targets. Marcus-Orchestrator reads the
registry at plan-lock to route `scope_decision.delegated-to-modality-X` entries
to concrete producers; Irene references `modality_ref` validity; Tracy dispatches
based on composite composition.

**Shapes pinned (live in `marcus/lesson_plan/modality_registry.py`):**

- `ModalityRef`: `Literal["slides", "blueprint", "leader-guide", "handout",
  "classroom-exercise"]` — closed set of 5 entries at MVP. Widening requires
  ruling amendment + schema-version bump (minor if additive, major if
  renaming or status-semantics change) + SCHEMA_CHANGELOG entry (AC-C.4).
- `ModalityEntry`: `modality_ref` (ModalityRef) / `status`
  (`Literal["ready", "pending"]`) / `producer_class_path` (`str | None`) /
  `description` (free-text). `ConfigDict(extra="forbid", frozen=True,
  validate_assignment=True)`. AC-C.6 invariant via
  `@model_validator(mode="after")`: `status == "pending"` implies
  `producer_class_path is None`.
- `MODALITY_REGISTRY`: `types.MappingProxyType` wrapping the seeded dict.
  `isinstance(MODALITY_REGISTRY, MappingProxyType)` is the pinned type.
  Any mutation attempt raises (`TypeError` from MappingProxyType or
  `AttributeError` from missing methods).
- Query API: `get_modality_entry(modality_ref) -> ModalityEntry | None`
  (no warn / no raise on unknown — closed-set discipline);
  `list_ready_modalities() -> frozenset[str]` (returns `{"slides",
  "blueprint"}` at MVP); `list_pending_modalities() -> frozenset[str]`
  (returns `{"leader-guide", "handout", "classroom-exercise"}` at MVP).

**Semantics pinned:**

- CLOSED SET at MVP. Unlike `event_type_registry` (which WARNs on unknown for
  Gagné-seam extensibility), `modality_registry` rejects silently via `None`
  return — widening is not an extensibility surface; it's a governed change.
- At 31-3 MVP every entry has `producer_class_path=None`. Gary/slides
  backfills via separate amendment; 31-4 backfills `blueprint` via minor
  schema bump; `pending` modalities stay `None`.
- R2 rider S-2 carry-forward: `description` is free-text, no `min_length`.

**Anti-patterns locked down:**

- No runtime registry extension, no plugin discovery hooks, no per-tenant
  variation (AC-C.7).
- `MODALITY_REGISTRY["slides"] = ...` / `del` / `clear` / `update` / `pop` /
  `popitem` / `setdefault` / attribute set all raise. AC-T.2 parametrized
  matrix enforces at CI.
- `intake` / `orchestrator` tokens forbidden in user-facing strings (AC-T.8 /
  R1 amendment 17 / R2 rider S-3 carry-forward).

**Migration:** N/A (initial shape).

**Consumer compatibility:** 30-3 / 29-2 / 28-2 / 31-4 / 30-4 consume via the
public query API. Direct `MODALITY_REGISTRY[key]` access is PERMITTED
(public Mapping) but the query helpers are preferred because they return
`None` on miss.

## Component Type Registry v1.0 — 2026-04-18 — Story 31-3 Registries

**Type:** Initial shape (no predecessor).

**Reason for introduction:** Names the N=2 composite-package shapes at MVP —
the minimum needed to prove both single-modality and multi-modality composite
shapes using only `ready` modalities. Prompt-pack authors compose packages
against these entries; Tracy dispatches enrichment per composite.

**Shapes pinned (live in `marcus/lesson_plan/component_type_registry.py`):**

- `ComponentTypeEntry`: `component_type_ref` (str, min_length=1) /
  `modality_refs` (`tuple[ModalityRef, ...]`, every element must be a key in
  MODALITY_REGISTRY) / `description` (free-text) / `prompt_pack_version`
  (`str | None`). `ConfigDict(extra="forbid", frozen=True,
  validate_assignment=True)`. Composition-validity enforced at TWO layers:
  (a) `ModalityRef` Literal closed-set check at field-validation time,
  (b) `@model_validator(mode="after")` explicit lookup against
  `MODALITY_REGISTRY` (defense in depth against `ModalityRef` widening
  without registry update).
- `COMPONENT_TYPE_REGISTRY`: `types.MappingProxyType` with 2 entries:
  `narrated-deck` composes `("slides",)`;
  `motion-enabled-narrated-lesson` composes `("slides", "blueprint")`.
  Both `prompt_pack_version=None` at MVP.
- Query API: `get_component_type_entry(component_type_ref) ->
  ComponentTypeEntry | None`.

**Semantics pinned:**

- N=2 ENTRIES FROZEN at MVP. Widening requires ruling amendment +
  schema-version bump + SCHEMA_CHANGELOG entry (AC-C.5).
- Composites compose ONLY `ready` modalities at MVP (cross-status coupling
  out-of-scope).
- Recursive composites (a composite of composites) are out-of-scope
  (AC-C.7 (f)).
- Import-time assertion in the module: every seeded
  `component_type_ref.modality_refs` element is a key in
  `MODALITY_REGISTRY` (belt-and-suspenders against typos in the seed dict).

**Anti-patterns locked down:**

- Same immutability + no-runtime-extension discipline as Modality Registry.
- `modality_refs` is a `tuple` (frozen-by-value); not a `list`.

**Migration:** N/A (initial shape).

**Consumer compatibility:** 28-2 / prompt-pack authors consume via
`get_component_type_entry` or direct registry iteration.

## ModalityProducer ABC v1.0 — 2026-04-18 — Story 31-3 Registries

**Type:** Initial shape (no predecessor).

**Reason for introduction:** Names the producer contract every modality
producer subclasses. 31-4 (blueprint-producer, 5pt single story) implements
this ABC first; Gary/Gamma slides adopts via separate amendment. R1 ruling
amendment 7 binding: ABC MUST be complete-enough that 31-4 lands without
splitting.

**Shapes pinned (live in `marcus/lesson_plan/modality_producer.py` and
`marcus/lesson_plan/produced_asset.py`):**

- `ModalityProducer` (ABC):
  - `modality_ref: ClassVar[str]` — pinned by subclass.
  - `status: ClassVar[Literal["ready", "pending"]]` — pinned by subclass.
  - `@abstractmethod produce(self, plan_unit, context) -> ProducedAsset`.
  - **M-AM-2 (Murat R2 BINDING) `__init_subclass__` hook:** CPython does NOT
    check `ClassVar[...]` type hints at class-definition or instantiation
    time; the hook raises `TypeError` at class-definition time on missing /
    wrong-type `modality_ref`, missing `status`, or status outside the
    closed set. This is the actual enforcement — the annotations are
    documentation-only without this hook.
  - ABC membership enforced separately via `abc.ABC` + abstract method:
    subclass missing `produce()` → `TypeError` at instantiation.
- `ProductionContext` (Pydantic):
  - `lesson_plan_revision: int ge=0` / `lesson_plan_digest: str min_length=1`.
  - `ConfigDict(extra="forbid", frozen=True, validate_assignment=True)`.
  - **W-2 (Winston R2) extensibility seam:** 31-4 MAY subclass for
    blueprint-specific fields WITHOUT a schema version bump; subclasses MUST
    preserve `lesson_plan_revision` + `lesson_plan_digest` as the
    staleness-gate primitives. Subclass stories document extensions in their
    own SCHEMA_CHANGELOG entry.
- `ProducedAsset` (Pydantic):
  - `asset_ref` / `modality_ref` / `source_plan_unit_id` / `created_at`
    (tz-aware UTC) / `asset_path` / `fulfills`.
  - `fulfills` regex: `^[a-z0-9._-]+@(?:0|[1-9]\d*)$`. Accepts zero revision
    (`unit@0`); rejects leading-zero (`unit@007` — M-AM-3 strict-monotonic
    integer discipline), negative, non-integer, uppercase, unicode, multi-@,
    whitespace.
  - **Q-R2-A (Quinn R2) cross-field validator:** `source_plan_unit_id ==
    fulfills.split("@", 1)[0]` — rejects counterfeit-fulfillment with the
    explicit `"counterfeit-fulfillment seam; tri-phasic contract violation"`
    error message.

**Semantics pinned:**

- Every `ProducedAsset` carries `fulfills: {plan_unit_id}@{plan_revision}` —
  Quinn's Tri-Phasic Contract execution-phase artifact.
- The ABC does NOT enforce registry membership at instantiation
  (`modality_ref="unknown-but-a-str"` is still instantiable at the ABC
  layer). That's a consumer-site check — see
  `tests/fixtures/consumers/fixture_30_3_marcus_consumer.py`
  staleness-gate-at-consumer-boundary pattern (Q-R2-B).

**Anti-patterns locked down:**

- No hooks beyond `produce()` on the ABC (no `setup()` / `teardown()` /
  `validate()`). If 31-4 needs more, widen here, not there (R1 amendment 7
  binding).
- `ProducedAsset.fulfills` must pass regex AND cross-field validator —
  either failure rejects.

**Migration:** N/A (initial shape).

**Consumer compatibility:** 31-4 subclasses `ModalityProducer`; 30-4 + 31-5
read `ProducedAsset.fulfills` for fanout tracking + Quinn-R gate.

## Lesson Plan Log v1.0 — 2026-04-18 — Story 31-2 Lesson Plan Log

**Type:** Initial shape (no predecessor log file exists).

**Reason for introduction:** 31-2 ships the write-path on top of the 31-1
shape foundation. Surfaces the append-only JSONL log + single-writer
enforcement + monotonic-revision gate (plan.locked only, per R2 M-2) +
staleness detector + `pre_packet_snapshot` payload shape (Winston R1
amendment on 30-4).

**Shapes pinned (live in `marcus/lesson_plan/log.py`):**

- `LessonPlanLog`: write API (`append_event(envelope, writer_identity)`),
  read API (`read_events(since_revision, event_types)`), helpers
  (`latest_plan_revision`, `latest_plan_digest`), property (`path`).
- `WriterIdentity`: `Literal["marcus-orchestrator", "marcus-intake"]`
  (closed set per AC-C.5; widening requires ruling amendment + major
  schema bump).
- `WRITER_EVENT_MATRIX`: `dict[str, frozenset[WriterIdentity]]` — AC-B.3
  single-writer enforcement matrix. Only the `pre_packet_snapshot` row
  permits `marcus-intake`; the other five rows are
  Marcus-Orchestrator-only per R1 ruling amendment 13.
- `NAMED_MANDATORY_EVENTS`: alias of
  `event_type_registry.RESERVED_LOG_EVENT_TYPES` (single source of truth,
  two naming surfaces). Frozenset — M-3 immutability asserted via
  `.add()` raising `AttributeError`.
- `SourceRef`: `source_id`, `path` (Optional), `content_digest`.
- `PrePacketSnapshotPayload`: `sme_refs` (list[SourceRef]),
  `ingestion_digest`, `pre_packet_artifact_path`,
  `step_03_extraction_checksum` — the four fields 30-4 needs to
  reconstruct Intake-era context from the log alone (Winston R1).
- `PlanLockedPayload`: `lesson_plan_digest` — the digest field
  `latest_plan_digest()` reads.
- `StalePlanRefError`: new exception (subclass of `ValueError`) raised by
  `assert_plan_fresh` when envelope revision and/or digest mismatches
  log. R2 M-1 axis-named message format: `"StalePlanRefError: revision
  mismatch (envelope=N, log=M); digest mismatch (envelope='x', log='y')"`.
- `UnauthorizedWriterError`: new exception (subclass of
  `PermissionError`) raised by `append_event` on writer/event-type mismatch.
- `assert_plan_fresh`: module-level staleness detector; duck-typed on
  `lesson_plan_revision` + `lesson_plan_digest` attributes. Called by
  every envelope 05→13 before downstream processing; 32-2 coverage
  manifest audits call-site coverage.
- `LOG_PATH`: `Path("state/runtime/lesson_plan_log.jsonl")` — module
  constant; tests override via fixture or explicit `path=` kwarg.

**Semantics pinned:**

- Append-only JSONL — one canonical-JSON line per event + newline.
  `open("a") + write + flush + fsync`. Atomic on POSIX for writes <
  `PIPE_BUF`; single-process single-writer assumption bridges the
  Windows NTFS gap (see W-R1 future-hardening note below).
- Monotonic revision on `plan.locked` ONLY (R2 M-2). Non-`plan.locked`
  events at stale revision are LEGAL (interleave semantics).
- Re-read-after-write consistency (R2 M-5 / AC-T.11): immediate
  `read_events()` after `append_event()` MUST yield the just-appended
  event.
- No dedup on `event_id`; no compaction; no rotation; no multi-process
  writer coordination (all explicitly out-of-scope per AC-C.7).

**Anti-patterns locked down:**

- No direct `open(LOG_PATH, "a")` in downstream code; `bmad-code-review`
  Blind Hunter layer scans for bypasses (AC-C.8).
- No writer_identity spoofing (Q-R2-R1 R2 rider): modules pass only
  their own writer identity; grep-detectable in code review.
- `NAMED_MANDATORY_EVENTS.add()` raises `AttributeError` (M-3 frozenset
  immutability).
- Unknown event_types are REJECTED at write time (governance artifact,
  not extensibility surface) — AC-B.2 (b) / AC-T.7.

**R2 party-mode GREEN with 7 riders (2026-04-18):**

- W-R1 — Windows atomic-write future-hardening caveat (docstring only).
- Q-R2-R1 — writer_identity anti-pattern discipline (Dev Notes +
  code-review grep).
- M-1 — AC-T.4 2×2 staleness matrix + axis-named error message.
- M-2 — Monotonic gate ONLY on plan.locked (non-plan.locked stale
  ACCEPTED).
- M-3 — `NAMED_MANDATORY_EVENTS` frozenset immutability test.
- M-4 — Baseline rebase to commit `15f68b1` HEAD (1023 `--run-live` /
  1001 default).
- M-5 — AC-T.11 re-read-after-write consistency + K floor 15 → 17.

**Migration:** N/A (initial shape; no predecessor log file exists —
`state/runtime/lesson_plan_log.jsonl` is created by first `append_event`
call).

**Consumer compatibility:** 30-1 / 30-4 / 32-2 consume via the public
`LessonPlanLog.read_events` API. Direct `open(LOG_PATH)` reads in
consumer code are a code-review block (AC-C.8).

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
