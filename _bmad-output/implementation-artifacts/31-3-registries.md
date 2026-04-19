# Story 31-3: Registries — `modality_registry` + `component_type_registry` + `ModalityProducer` ABC

**Status:** done (BMAD-closed 2026-04-18)
**Created:** 2026-04-18 (authored by Amelia post-31-2 closeout; inherits R1 ruling amendment 5 resize 3 → 2pts; R1 ruling amendment 6 registries-runtime scoping; R1 ruling amendment 7 `31-4 blueprint-producer` HOLD at 5pts single story; Murat R1 amendment — consumer-contract fixtures; R1/R2 discipline carry-forward from 31-1/31-2)
**Epic:** 31 — Tri-phasic contract primitives + gates (FOUNDATION)
**Sprint key:** `31-3-registries`
**Branch:** `dev/lesson-planner`
**Points:** 2 (resized from 3 per R1 ruling amendment 5 — schema work absorbed into 31-1)
**Depends on:** **31-1 (done — commit `15f68b1`)** — imports `PlanUnit` (for `ModalityProducer.produce` signature), Pydantic v2 schema foundation idioms, `SCHEMA_VERSION` convention, `_OPEN_ID_REGEX` pattern family.
**Blocks:** **31-4 (blueprint-producer)** — implements `ModalityProducer` ABC; **30-3a/3b** (Marcus 4A orchestrator reads `modality_registry` + `component_type_registry` to route scope decisions and declare producer readiness); **29-2** (Irene diagnostician references `modality_ref` field against `modality_registry` for validity); **28-2** (Tracy dispatches based on `component_type_registry` when declaring which modalities it enriches).

---

## Mid-Flight Memo — Post-31-2 dev-guide references (READ AT T2)

31-3 is a **registries + ABC + consumer-fixture** story. Authoritative references distilling 31-1/31-2 discipline:

- [`docs/dev-guide/pydantic-v2-schema-checklist.md`](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — 31-3's `ModalityEntry`, `ComponentTypeEntry`, `ProductionContext`, `ProducedAsset` MUST adopt: `ConfigDict(extra="forbid", frozen=True, validate_assignment=True)` on registry-entry models; closed-enum triple red-rejection for `status: Literal["ready", "pending"]` (Pydantic validator + JSON Schema enum + `TypeAdapter` round-trip); no `min_length` on free-text `description` fields; tz-aware datetime on `ProducedAsset.created_at`.
- [`docs/dev-guide/dev-agent-anti-patterns.md`](../../docs/dev-guide/dev-agent-anti-patterns.md) — A1 silent mutation (registry attempts-to-mutate MUST raise — `MappingProxyType`), A4 closed-enum single surface (`status` must be closed `Literal` with three rejection surfaces, no string-typing bailout), B1 K-floor becomes ceiling-multiplier (K=15 is floor; target 18–23 collecting tests; 25–40 acceptable only if each extra names a specific coverage gap), B4 per-family shape pins (AC-T.1 ships three separate shape-pin contract files, not one batched), E1-E3 no intake/orchestrator leak in user-facing strings.
- [`docs/dev-guide/story-cycle-efficiency.md`](../../docs/dev-guide/story-cycle-efficiency.md) — The §2 single-gate policy listed 31-3 as single-gate, but R1 amendment 7 (31-4 HOLD at 5pts single story) makes 31-3's ABC a **hard downstream contract** — the ABC must be complete-enough for 31-4 to land without splitting. **31-3 runs dual-gate (R2 party-mode green-light + G5 party-mode implementation review + G6 bmad-code-review)** per the foundation discipline that 31-4 depends on it. §1 K-floor: target 18–23 collecting tests (1.2×–1.5× K=15); 25–40 acceptable with named gaps.
- [`docs/dev-guide/scaffolds/schema-story/`](../../docs/dev-guide/scaffolds/schema-story/) — registry-entry Pydantic shapes follow the schema scaffold. `test_no_intake_orchestrator_leak.py.tmpl` ships directly as AC-T.8 ancillary scan.
- **Pre-seed reference:** [`_bmad-output/specs/pre-seed-drafts/31-3-registries-PRE-SEED.md`](../specs/pre-seed-drafts/31-3-registries-PRE-SEED.md) — non-authoritative skeleton authored in a prior session. Some shape suggestions (e.g. `ModalityStatus`/`ComponentTypeStatus` dual enums, `lecture_unit`/`practice_unit` component-type labels) are superseded by this authoritative spec (single `Literal["ready", "pending"]` on both registries; N=2 component-type labels chosen below).

**Integration guidance for dev agent:** do NOT scaffold-import from pre-seed. Author against this spec directly. Pre-seed is read-only reference for how a prior voice considered the shape; final shape lives here.

**Reviewer guidance:** at R2 party-mode, add checklist items: "Drafted module adheres to `pydantic-v2-schema-checklist.md` §1, §4, §5, §6, §14; `dev-agent-anti-patterns.md` A1, A4, B1, B4, E1-E3 scanned and clear; `ModalityProducer` ABC is complete-enough that 31-4 (5pt single story) lands without splitting (R1 amendment 7 satisfaction check)."

---

## TL;DR

- **What:** `marcus/lesson_plan/modality_registry.py` + `marcus/lesson_plan/component_type_registry.py` + `marcus/lesson_plan/modality_producer.py` + `marcus/lesson_plan/produced_asset.py` — the frozen closed-set catalog of atomic producer targets (slides/blueprint/leader-guide/handout/classroom-exercise) with `ready`/`pending` status, the N=2 composite-package ComponentType catalog, the `ModalityProducer` abstract base class (producers subclass and implement), the `ProductionContext` + `ProducedAsset` Pydantic payload shapes (including `fulfills: unit_id@plan_revision` regex-pinned per Quinn Tri-Phasic Contract), plus three stubbed consumer-contract fixtures under `tests/fixtures/consumers/` (for 30-3 Marcus / 29-2 Irene / 28-2 Tracy).
- **Why:** 31-1 shipped the SHAPE; 31-2 shipped the WRITE-PATH; 31-3 is the TARGETING SURFACE. Marcus-Orchestrator reads the registries at plan-lock to route `scope_decision.delegated-to-modality-X` entries to concrete producers; Irene references `modality_ref` field validity against the registry; Tracy dispatches based on component-type composition. Without frozen registries + ABC, 31-4 has no contract to implement; 30-3 has no routing target; AC would reduce to "registry exists and returns values" — a CI-passes / integration-breaks shape (Murat amendment rationale).
- **Absorption note:** 31-3 was RESIZED 3 → 2pts per R1 ruling amendment 5 (schema work moved to 31-1). 31-3 is now registries + ABC + consumer fixtures ONLY — no schema-shape expansion. Per R1 ruling amendment 7, the `ModalityProducer` ABC MUST be complete-enough that 31-4 lands as a single 5pt implementation, not a split.
- **Done when:** `marcus/lesson_plan/modality_registry.py` + `component_type_registry.py` + `modality_producer.py` + `produced_asset.py` landed + `MODALITY_REGISTRY` (5 entries, 2 ready + 3 pending) + `COMPONENT_TYPE_REGISTRY` (N=2 entries) + `ModalityProducer` ABC + `ProductionContext` + `ProducedAsset` with `fulfills` regex pin + 3 consumer-contract fixtures under `tests/fixtures/consumers/` + `tests_added ≥ 15` + R2 party-mode green-light + `bmad-code-review` layered pass + `sprint-status.yaml` flipped `ready-for-dev → in-progress → review → done`.

## Story

As the **Lesson Planner MVP targeting-surface author**,
I want **the `modality_registry` + `component_type_registry` + `ModalityProducer` ABC + `ProductionContext` + `ProducedAsset` primitives landed as one reviewable PR on top of the 31-1 schema foundation, with three consumer-contract fixtures stubbed for 30-3 / 29-2 / 28-2**,
So that **Marcus-Orchestrator has a frozen authoritative surface for "what can we produce?" at plan-lock fanout, 31-4 (blueprint-producer, 5pt single story per R1 amendment 7) has a complete-enough ABC to implement without splitting, Irene's diagnosis can reference `modality_ref` validity, Tracy can declare which modalities it enriches, and each downstream consumer story has a frozen contract-shape to author its consumer tests against before those stories open**.

## Background — Why This Story Exists

31-1 (done, commit `15f68b1`) shipped the `marcus/lesson_plan/` schema foundation. 31-2 (done, commit `21b2d83`) shipped the append-only log + single-writer enforcement + staleness detector. 31-3 is the **third foundation story** in Epic 31: the registries + ABC that 31-4 implements and that downstream consumers (30-3 Marcus, 29-2 Irene, 28-2 Tracy) read at runtime.

Four binding carry-forwards from R1/R2 rulings land in 31-3:

1. **R1 ruling amendment 5 — 31-3 resize (3 → 2pts).** Schema work (LessonPlan / PlanUnit / fit-report-v1 / weather_band / ScopeDecision state machine / dials-spec.md) was absorbed into 31-1. 31-3's remaining scope: registries + ABC + `ProductionContext` + `ProducedAsset` + consumer fixtures. No Pydantic-model proliferation beyond the four primitives listed above.

2. **R1 ruling amendment 7 — 31-4 HOLD at 5pts single story.** Quinn's proposal to split 31-4 into a harness + implementation was DECLINED. 31-4 ships as one single 5pt story. Consequence for 31-3: the `ModalityProducer` ABC MUST be complete-enough — with `produce()`, `modality_ref: ClassVar[str]`, `status: ClassVar[Literal["ready", "pending"]]`, `ProductionContext` input, `ProducedAsset` output — that 31-4 lands as a single implementation PR. If 31-3 ships an under-specified ABC, 31-4 forcibly splits. This is the architectural risk the R2 panel MUST pressure-test.

3. **Murat R1 amendment — Consumer-contract fixtures.** 31-3 ships three stubbed consumer-contract fixtures under `tests/fixtures/consumers/`:
   - `test_30_3_marcus_reads_registries_fixture.py` — demonstrates Marcus orchestrator reading `modality_registry` to decide scope delegation.
   - `test_29_2_irene_reads_registries_fixture.py` — demonstrates Irene diagnostician checking `modality_ref` validity against `modality_registry`.
   - `test_28_2_tracy_reads_registries_fixture.py` — demonstrates Tracy dispatching based on `component_type_registry`.
   Each fixture is a MINIMAL consumer stub showing the import + usage pattern. Not a full consumer implementation — just enough to prove 31-3's API surface is consumable. Paired with a contract test asserting the fixture loads + executes without error (AC-T.6). Rationale: without consumer fixtures, the registry AC reduces to "registry exists and returns values" — the shape of a story that passes CI and breaks integration at 30-3/29-2/28-2 authoring time. Fixtures convert integration risk into a frozen contract surface.

4. **R1 ruling amendment 17 + R2 rider S-3 carry-forward — Marcus is one voice (no-leak).** Registry entry descriptions and companion docs MUST NOT contain `intake` / `orchestrator` tokens as user-facing prose. AC-T.8 ships the no-leak grep scan.

## R2 Green-Light Rider Block (2026-04-18 — APPLIED)

R2 party-mode GREEN with 9 riders; all applied to this spec before dev-story entry:

- **W-1 (Winston):** At T2, DELETE pre-existing stub `marcus/lesson_plan/registries.py` (pre-seed scaffold; superseded by the four-file split). Also DELETE the three pre-existing scaffold tests in `tests/contracts/` that import the stub: `test_registries_shape_stable.py`, `test_registries_json_schema_parity.py`, `test_no_intake_orchestrator_leak_registries.py` (the last is replaced by the 31-3 four-module version per AC-T.8; the old scaffold version used `marcus.lesson_plan.registries` as the sole scan target). See AC-C.1 + Task T2.
- **W-2 (Winston):** Extensibility seam on `ProductionContext`. See AC-B.4.
- **Q-R2-A (Quinn):** Cross-field validator on `ProducedAsset` enforcing `source_plan_unit_id == parse(fulfills).unit_id`. See AC-B.5 + AC-T.5b.
- **Q-R2-B (Quinn):** Staleness-gate-at-consumer-boundary pattern demonstrated in the Marcus consumer fixture. See AC-T.6 (Marcus fixture addendum).
- **M-AM-1 (Murat BINDING):** AC-T.9 baseline rebased from draft stale numbers to `21b2d83` HEAD actuals (`--run-live` 1478 passed / default 1456 passed). Expected after 31-3 with K≥15 landing: `--run-live` ≥1493 / default ≥1471; realistic landing 58-65 new tests.
- **M-AM-2 (Murat BINDING):** `ModalityProducer.__init_subclass__` enforcement hook for `modality_ref` / `status` ClassVars (CPython does NOT check `ClassVar` type hints at class-definition time). See AC-B.3 + AC-T.4.
- **M-AM-3 (Murat BINDING):** AC-T.5 fulfills regex matrix extended. See AC-T.5.
- **M-AM-4 (Murat):** Rename consumer fixture files from `test_30_3_*.py` to `fixture_30_3_marcus_consumer.py` / `fixture_29_2_irene_consumer.py` / `fixture_28_2_tracy_consumer.py` (pytest does NOT collect files that don't start with `test_`). Loader test imports via `importlib.util`. See AC-B.6 + AC-T.6.
- **P-R2-1 (Paige):** Audience-layered module docstrings. First line of each new module names its primary audience. See module docstrings.

## Pre-Development Gate (R2 party-mode green-light BINDING)

31-3 cannot enter `bmad-dev-story` until BOTH gates cleared:

- [x] **PDG-1 (R2 party-mode green-light, BINDING).** Full party-mode review with Winston (Architect) / Murat (TEA) / Quinn (Problem-Solver) / Paige (Tech Writer) / Sally (UX, light touch). Pressure-test items:
  - (a) **R1 amendment 7 satisfaction check (Winston + Quinn):** Is the `ModalityProducer` ABC shape complete-enough that 31-4 (5pt single story) lands without splitting? If any reviewer flags an ABC gap that would force 31-4 to split, 31-3 must widen before `ready-for-dev`.
  - (b) **N=2 component-type choice (Winston + Sally):** Are the two chosen ComponentType labels (`narrated-deck`, `motion-enabled-narrated-lesson`) the right shape-proving pair? Do they compose existing `ready` modalities only (slides + blueprint)?
  - (c) **Consumer-fixture minimality (Murat):** Are the three consumer-contract fixtures MINIMAL import-and-usage stubs, or do they over-reach into full consumer logic? Over-reach couples 31-3 to downstream implementation choices.
  - (d) **Closed-set discipline (Winston + Murat):** Are both registries strictly immutable (`MappingProxyType`)? Does widening the 5-entry modality set or the N=2 component-type set require a schema-version bump + `SCHEMA_CHANGELOG` entry + explicit amendment?
  - (e) **K-floor defense (Murat):** K=15 — defended by registry × test-shape matrix (see Test Plan). Realistic landing 25–40 per pattern, each extra justified.
- [x] **PDG-2.** 31-1 closed `done` with `PlanUnit` + `SCHEMA_VERSION` + `_OPEN_ID_REGEX` available. **CLEARED** — commit `15f68b1`, `marcus/lesson_plan/schema.py`.
- [x] **PDG-3.** 31-2 closed `done` with `EventEnvelope` + `LessonPlanLog` available (not directly consumed by 31-3 but confirms foundation stack is stable). **CLEARED** — commit `21b2d83`.

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — `modality_registry` module-level frozen mapping.** Lives at `marcus/lesson_plan/modality_registry.py`. Shape:

   ```python
   ModalityRef = Literal[
       "slides",
       "blueprint",
       "leader-guide",
       "handout",
       "classroom-exercise",
   ]

   class ModalityEntry(BaseModel):
       model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)
       modality_ref: ModalityRef
       status: Literal["ready", "pending"]
       producer_class_path: str | None  # dotted path to producer class; None iff status == "pending" at MVP
       description: str                  # free-text; no min_length per R2 rider S-2 free-text discipline
   ```

   At MVP, the registry holds exactly five entries:

   | `modality_ref` | `status` | `producer_class_path` | Notes |
   |---|---|---|---|
   | `slides` | `ready` | `None` | Gary/Gamma slide-deck producer is existing pre-MVP work; adopts the ABC in a separate amendment story (OUT OF SCOPE per AC-C.7); `producer_class_path` stays `None` at 31-3 and is backfilled by that amendment |
   | `blueprint` | `ready` | `None` | Blueprint-producer lands in 31-4; `producer_class_path` backfilled by 31-4 via SCHEMA_CHANGELOG minor bump |
   | `leader-guide` | `pending` | `None` | Post-MVP |
   | `handout` | `pending` | `None` | Post-MVP |
   | `classroom-exercise` | `pending` | `None` | Post-MVP |

   Exported as module constant `MODALITY_REGISTRY: Mapping[ModalityRef, ModalityEntry]` wrapped in `types.MappingProxyType` (AC-B.5 immutability).

2. **AC-B.2 — `component_type_registry` module-level frozen mapping.** Lives at `marcus/lesson_plan/component_type_registry.py`. Shape:

   ```python
   class ComponentTypeEntry(BaseModel):
       model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)
       component_type_ref: str                    # open string; see AC-C.5 naming rationale
       modality_refs: tuple[ModalityRef, ...]     # tuple so frozen-by-value; every element must be a key in MODALITY_REGISTRY (AC-T.3 validator)
       description: str                           # free-text; no min_length
       prompt_pack_version: str | None            # optional pointer to the prompt-pack revision that composes this type; None at MVP
   ```

   At MVP, the registry holds exactly **N=2 entries** to prove the composite-package shape without requiring every future composite to exist:

   | `component_type_ref` | `modality_refs` | `prompt_pack_version` | Rationale |
   |---|---|---|---|
   | `narrated-deck` | `("slides",)` | `None` | Minimal composite: a single-modality package composed of slides + (future) narration track. At MVP narration is out-of-scope; the composite is ready as a shape because slides is ready, narration binding is deferred. Names the most common MVP output shape. |
   | `motion-enabled-narrated-lesson` | `("slides", "blueprint")` | `None` | Two-modality composite: slides + blueprint, proves the multi-modality shape. Motion/narration are bound at production-site per prompt-pack vocabulary (see `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`). Composes exactly the two `ready` modalities in `MODALITY_REGISTRY`, matching R1 amendment 5's "MVP has 2 ready modalities" constraint. |

   **Composition constraint (AC-T.3 enforcement):** every `modality_refs` element MUST be a key in `MODALITY_REGISTRY`. Widening to include `pending` modalities in a `ready`-composite is a separate-story concern. Exported as module constant `COMPONENT_TYPE_REGISTRY: Mapping[str, ComponentTypeEntry]` wrapped in `MappingProxyType`.

3. **AC-B.3 — `ModalityProducer` ABC.** Lives at `marcus/lesson_plan/modality_producer.py`. Shape:

   ```python
   from abc import ABC, abstractmethod
   from typing import ClassVar, Literal

   class ModalityProducer(ABC):
       """Abstract base class for atomic modality producers.

       Concrete producers (31-4 blueprint-producer lands first; Gary/Gamma
       slides-producer adopts via separate amendment story) subclass this
       and implement :meth:`produce`. ``modality_ref`` + ``status`` are
       class attributes pinned by the subclass; the base enforces that
       instantiation requires them (see AC-T.4).
       """

       modality_ref: ClassVar[str]
       status: ClassVar[Literal["ready", "pending"]]

       @abstractmethod
       def produce(
           self,
           plan_unit: PlanUnit,
           context: ProductionContext,
       ) -> ProducedAsset:
           """Produce a single asset for the given plan_unit per modality contract.

           MUST NOT mutate ``plan_unit`` or ``context``. MUST emit a
           :class:`ProducedAsset` with ``fulfills`` set per AC-B.7
           invariant. Concrete implementations MAY raise custom exceptions
           on produce failure; the ABC does not constrain error surfaces.
           """
   ```

   Imports `PlanUnit` from `marcus.lesson_plan.schema` (31-1 foundation); `ProductionContext` + `ProducedAsset` from the 31-3 siblings (`produced_asset.py`). Subclass without `produce` → `TypeError` on instantiation (ABC enforcement). Exported from `marcus/lesson_plan/__init__.py`.

   **M-AM-2 (Murat R2 BINDING) `__init_subclass__` enforcement:** `ClassVar[str]` and `ClassVar[Literal[...]]` annotations on `ModalityProducer` are **documented-only at Python runtime** — CPython does NOT check `ClassVar` type hints at class-definition or instantiation time. Tests MUST enforce the contract via an explicit enforcement hook. `ModalityProducer.__init_subclass__` is wired as the single enforcement mechanism:

   ```python
   def __init_subclass__(cls, **kwargs: Any) -> None:
       super().__init_subclass__(**kwargs)
       # Skip enforcement on intermediate abstract subclasses if any; check only
       # concrete subclasses. Heuristic: abstract iff has ABSTRACT methods
       # OR is in the __abstractmethods__ set. Simplest at MVP: enforce on
       # every subclass — no intermediate abstracts planned.
       if not hasattr(cls, "modality_ref") or not isinstance(cls.modality_ref, str):
           raise TypeError(
               f"ModalityProducer subclass {cls.__name__!r} must define "
               f"class attribute 'modality_ref: ClassVar[str]'"
           )
       if not hasattr(cls, "status") or cls.status not in {"ready", "pending"}:
           raise TypeError(
               f"ModalityProducer subclass {cls.__name__!r} must define "
               f"'status: ClassVar[Literal[\"ready\", \"pending\"]]' "
               f"(got {getattr(cls, 'status', '<missing>')!r})"
           )
   ```

   AC-T.4 test matrix MUST cover:
   - (a) Subclass with full valid attrs (`produce` + `modality_ref: str` + `status` in `{"ready", "pending"}`) — instantiable.
   - (b) Subclass missing `modality_ref` ClassVar — raises `TypeError` at `__init_subclass__` (class-definition time).
   - (c) Subclass missing `status` ClassVar — raises `TypeError` at class-definition time.
   - (d) Subclass with wrong-type `modality_ref` (e.g., int) — raises `TypeError` at class-definition time.
   - (e) Subclass with invalid `status` string (e.g., `"invalid"`) — raises `TypeError` at class-definition time.
   - (f) Subclass missing `produce()` — ABC refuses instantiation (`TypeError`).

4. **AC-B.4 — `ProductionContext` Pydantic payload.** Lives at `marcus/lesson_plan/produced_asset.py` (co-located with `ProducedAsset` since the two are produce-API twins). Shape:

   ```python
   class ProductionContext(BaseModel):
       model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)
       lesson_plan_revision: int = Field(ge=0)
       lesson_plan_digest: str = Field(min_length=1)
       # Minimal MVP shape; expand at consumer-site per story. R1 amendment 5
       # scoping: no producer-specific dials in 31-3 — concrete producers may
       # subclass-and-extend if needed, or consume a separate dials context
       # shipped by 30-3b. This keeps 31-3 thin.
   ```

   **Design note:** `ProductionContext` is intentionally minimal at MVP. Future extensions (e.g. operator-provided dials, prompt-pack revision, trace metadata) are explicitly deferred to the consumer story that needs them. The R2 panel pressure-tests this minimality against R1 amendment 7 (31-4 single-story readiness) — if 31-4 needs more context shape, widen here, not there.

   **W-2 (Winston R2) extensibility seam:** 31-4 (blueprint-producer) MAY subclass `ProductionContext` for blueprint-specific fields WITHOUT a schema version bump. Sub-classes MUST preserve `lesson_plan_revision` + `lesson_plan_digest` as the staleness-gate primitives. Pydantic BaseModel inheritance is the intended extensibility seam — not a new schema version. Consumer stories needing additional context fields override `extra="forbid"` conservatively (either extend the shape on a subclass or declare explicit new fields) and document the subclass in their own SCHEMA_CHANGELOG entry. 31-3's `ProductionContext` remains the minimal contract; subclasses are the evolution surface.

5. **AC-B.5 — `ProducedAsset` Pydantic payload with `fulfills` invariant.** Lives at `marcus/lesson_plan/produced_asset.py`. Shape:

   ```python
   class ProducedAsset(BaseModel):
       model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)
       asset_ref: str = Field(min_length=1)           # stable identifier for the produced asset
       modality_ref: ModalityRef                      # must match producer's class attr
       source_plan_unit_id: str = Field(min_length=1) # the plan_unit.unit_id this asset serves
       created_at: datetime                           # tz-aware UTC; enforced by validator
       asset_path: str = Field(min_length=1)          # filesystem path relative to repo root (producer writes to this path)
       fulfills: str                                  # format: "{plan_unit_id}@{plan_revision}"; regex-pinned per AC-B.7

       @field_validator("created_at")
       @classmethod
       def _enforce_tz_aware(cls, v: datetime) -> datetime:
           if v.tzinfo is None:
               raise ValueError("ProducedAsset.created_at must be timezone-aware")
           return v

       @field_validator("fulfills")
       @classmethod
       def _fulfills_regex(cls, v: str) -> str:
           # AC-B.7 regex pin
           if not _FULFILLS_REGEX.match(v):
               raise ValueError(
                   f"ProducedAsset.fulfills {v!r} fails regex "
                   r"^[a-z0-9._-]+@\d+$ — expected '{plan_unit_id}@{plan_revision}'"
               )
           return v
   ```

   Pins the tri-phasic contract execution-phase artifact (Quinn): "every produced asset carries `fulfills: unit_id@plan_revision`" (plan doc §Quinn's Tri-Phasic Contract).

   **Q-R2-A (Quinn R2) cross-field validator:** `ProducedAsset` has a `@model_validator(mode="after")` that enforces the invariant `self.source_plan_unit_id == self.fulfills.split("@", 1)[0]`. Rationale: without this gate, a counterfeit asset could declare `source_plan_unit_id="unit-a"` while `fulfills="unit-b@5"`, silently forging the tri-phasic contract. Error message: `"ProducedAsset: source_plan_unit_id ({source}) does not match fulfills unit_id ({fulfills_uid}); counterfeit-fulfillment seam; tri-phasic contract violation."`. Enforced at AC-T.5b.

6. **AC-B.6 — Registry query API.** Module-level helpers in both registry modules:

   ```python
   # marcus/lesson_plan/modality_registry.py
   def get_modality_entry(modality_ref: str) -> ModalityEntry | None: ...
   def list_ready_modalities() -> frozenset[str]: ...
   def list_pending_modalities() -> frozenset[str]: ...

   # marcus/lesson_plan/component_type_registry.py
   def get_component_type_entry(component_type_ref: str) -> ComponentTypeEntry | None: ...
   ```

   - `get_modality_entry("slides")` → returns the entry; `get_modality_entry("unknown")` → returns `None` (does NOT warn, unlike `event_type_registry.validate_event_type` which WARNs on unknown per 31-1 Gagné-seam discipline — these registries are CLOSED SETS per AC-B.8, not extensibility surfaces).
   - `list_ready_modalities()` → `frozenset({"slides", "blueprint"})` at MVP.
   - `list_pending_modalities()` → `frozenset({"leader-guide", "handout", "classroom-exercise"})` at MVP.
   - `list_ready_modalities()` + `list_pending_modalities()` == `frozenset(MODALITY_REGISTRY.keys())` (AC-T.3 parity assertion).

7. **AC-B.7 — `ProducedAsset.fulfills` regex invariant.** Format: `"{plan_unit_id}@{plan_revision}"`.

   ```python
   _FULFILLS_REGEX: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9._-]+@\d+$")
   ```

   - `plan_unit_id` matches the `_OPEN_ID_REGEX` family from 31-1 (`[a-z0-9._-]+`) — the same regex that validates `PlanUnit.unit_id` upstream; reuses the existing pattern rather than defining a new one.
   - `plan_revision` matches `\d+` (one or more digits, including `0` for bootstrap).
   - Accept matrix (AC-T.5): `"gagne-event-3@5"`, `"gagne-event-1@0"`, `"custom.unit_id@999"`.
   - Reject matrix (AC-T.5): `"no-at-sign"`, `"empty@"`, `"@empty"`, `"  gagne-event-3@5  "` (leading/trailing whitespace), `"a@b@c"` (multi-@), `"GAGNE-EVENT-3@5"` (uppercase fails `_OPEN_ID_REGEX`), `"gagne-event-3@-1"` (negative revision), `"gagne-event-3@ 5"` (internal whitespace), `""` (empty string).
   - Validator raises `pydantic.ValidationError` with explicit message naming the failing value + the expected regex.

8. **AC-B.8 — Registry immutability.** Both `MODALITY_REGISTRY` and `COMPONENT_TYPE_REGISTRY` are `types.MappingProxyType(...)` wrapping the underlying module-level dict literal. Attempts to mutate raise `TypeError`:
   ```python
   MODALITY_REGISTRY["new_modality"] = ...         # → TypeError
   MODALITY_REGISTRY["slides"] = ...               # → TypeError
   del MODALITY_REGISTRY["slides"]                 # → TypeError
   MODALITY_REGISTRY.clear()                       # → TypeError
   MODALITY_REGISTRY.pop("slides")                 # → TypeError
   ```
   Adding a new modality or component_type, or flipping a status, requires a code-level change in the module + schema-version bump (`SCHEMA_VERSION` constant in the module) + `SCHEMA_CHANGELOG.md` entry (AC-C.3) + explicit amendment. No backdoor, no runtime registration, no side-effect extension.

9. **AC-B.9 — Module-level schema version constants.** Each registry module exposes:
   ```python
   SCHEMA_VERSION: Final[str] = "1.0"
   ```
   Separate version per registry because they may evolve independently post-MVP (e.g., `modality_registry` could bump to 1.1 if a new `ready` modality lands without changing component-type shape). Both start at 1.0. `ModalityProducer` ABC module also exposes `SCHEMA_VERSION: Final[str] = "1.0"` for the ABC surface. `ProducedAsset` + `ProductionContext` live in the same module (`produced_asset.py`) and share a single `SCHEMA_VERSION: Final[str] = "1.0"`.

### Test (AC-T.*)

1. **AC-T.1 — Schema-pin contract tests (Murat AM-1 per-family split carry-forward).** Three separate contract test files, one per shape family, with snapshot + allowlist + `SCHEMA_CHANGELOG` gate pattern inherited from 27-0 / 31-1 / 31-2:
   - `tests/contracts/test_modality_registry_stable.py` — pins `ModalityEntry` Pydantic shape + `ModalityRef` Literal closed set + the five-entry initial set (`slides=ready`, `blueprint=ready`, `leader-guide=pending`, `handout=pending`, `classroom-exercise=pending`) + `SCHEMA_VERSION` constant. Any change without `SCHEMA_CHANGELOG` entry → test fails. Blocking at merge.
   - `tests/contracts/test_component_type_registry_stable.py` — pins `ComponentTypeEntry` Pydantic shape + the N=2 initial set (`narrated-deck` composes `("slides",)`, `motion-enabled-narrated-lesson` composes `("slides", "blueprint")`) + `SCHEMA_VERSION`. Blocking at merge.
   - `tests/contracts/test_modality_producer_abc_stable.py` — pins `ModalityProducer` ABC method signatures + `ProductionContext` + `ProducedAsset` Pydantic shapes + `_FULFILLS_REGEX` pattern + `SCHEMA_VERSION`. Blocking at merge.

2. **AC-T.2 — Registry immutability tests.** `tests/test_registry_immutability.py` parametrized over both registries with operations:
   - Attribute assignment: `MODALITY_REGISTRY.foo = "bar"` → `AttributeError` or `TypeError` (depends on MappingProxyType behavior; assert raises).
   - Item assignment: `MODALITY_REGISTRY["slides"] = new_entry` → `TypeError` (MappingProxyType forbids `__setitem__`).
   - Item deletion: `del MODALITY_REGISTRY["slides"]` → `TypeError`.
   - Bulk operations: `MODALITY_REGISTRY.clear()`, `MODALITY_REGISTRY.update({...})`, `MODALITY_REGISTRY.pop("slides")`, `MODALITY_REGISTRY.popitem()`, `MODALITY_REGISTRY.setdefault("new", ...)` → `AttributeError` (MappingProxyType has no mutation methods).
   - Same parametrized matrix applied to `COMPONENT_TYPE_REGISTRY`.
   - Type assertion: `assert isinstance(MODALITY_REGISTRY, types.MappingProxyType)` and same for component-type.

3. **AC-T.3 — Registry query API tests.** `tests/test_registry_query_api.py` parametrized matrix:
   - `get_modality_entry("slides")` → returns `ModalityEntry(modality_ref="slides", status="ready", ...)`.
   - `get_modality_entry("blueprint")` → returns ready entry with `producer_class_path=None` (31-4 backfills).
   - `get_modality_entry("leader-guide")` → returns pending entry with `producer_class_path=None`.
   - `get_modality_entry("nonexistent")` → returns `None` (does NOT raise, does NOT warn).
   - `get_modality_entry("")` → returns `None`.
   - `get_modality_entry("SLIDES")` → returns `None` (case-sensitive).
   - `list_ready_modalities()` → returns exactly `frozenset({"slides", "blueprint"})`.
   - `list_pending_modalities()` → returns exactly `frozenset({"leader-guide", "handout", "classroom-exercise"})`.
   - Complement parity: `list_ready_modalities() | list_pending_modalities() == frozenset(MODALITY_REGISTRY.keys())` and `list_ready_modalities() & list_pending_modalities() == frozenset()`.
   - Same shape for `get_component_type_entry`: positive lookup, negative lookup, empty-string lookup, case-sensitivity.
   - **Composition validity (AC-B.2 invariant):** for every `ComponentTypeEntry` in `COMPONENT_TYPE_REGISTRY`, every element of `modality_refs` MUST be a key in `MODALITY_REGISTRY`. Parametrized over all MVP component types.

4. **AC-T.4 — `ModalityProducer` ABC contract tests.** `tests/test_modality_producer_abc.py`:
   - `ModalityProducer()` (bare base) → raises `TypeError` because `produce` is abstract.
   - Subclass missing `produce()` → `TypeError` on instantiation.
   - Subclass WITH `produce` + `modality_ref` + `status` class attrs CAN be instantiated; test via a test-only fixture subclass (`_TestProducer(ModalityProducer)` defined inside the test file, not exported).
   - Subclass `modality_ref` set to a value NOT in `MODALITY_REGISTRY` → still instantiable (the ABC does not enforce registry membership at instantiation time; that is a runtime concern of the registry lookup). This keeps the ABC minimal per R1 amendment 5 "registries + ABC only" scoping. A separate runtime check in consumer code may enforce membership — see consumer-fixture AC-T.6.
   - `produce()` on the test subclass, given a minimal `PlanUnit` + `ProductionContext`, returns a valid `ProducedAsset`. Smoke-test that the contract is callable.

5. **AC-T.5 — `ProducedAsset.fulfills` regex accept + reject matrix.** `tests/test_produced_asset_fulfills.py` parametrized. **M-AM-3 (Murat R2 BINDING) extended matrix:**
   - **Accept:** `"gagne-event-3@5"`, `"gagne-event-1@0"` (bootstrap revision), `"custom.unit_id@999"`, `"a@1"` (minimum length), `"unit_with-dots.and_underscores@42"`, `"unit-with-dashes@1"`, `"u@0"` (zero revision legal), `"a-very-very-long-unit-id-exceeding-50-chars-but-still-valid@42"` (long-id tolerance).
   - **Reject (with error-message substring assertion):** `"no-at-sign"` (no `@`), `"empty@"` (empty revision), `"@empty"` (empty unit_id), `"  @  "` (whitespace-only both sides), `"  gagne-event-3@5  "` (leading/trailing whitespace), `"a@b@c"` (multi-@), `"GAGNE-EVENT-3@5"` (uppercase), `"UPPER@1"` (uppercase), `"Gagné-event@1"` (unicode in unit_id — fails `_OPEN_ID_REGEX`), `"gagne-event-3@-1"` (negative revision), `"gagne-event-3@ 5"` (internal whitespace), `""` (empty string), `"@"` (bare @), `"gagne event@5"` (internal space), `"gagne-event@1.5"` (float revision), `"unit@abc"` (non-integer revision), `"unit@007"` (leading-zero revision — pinned REJECT per strict-monotonic integer discipline; leading zeros invite ambiguous identity equality).
   - **Type rejection tests:** `fulfills=123` (int) raises, `fulfills=None` raises, `fulfills=["a", "b"]` (list) raises.
   - Every reject case asserts `pydantic.ValidationError` with a message containing the failing value substring and the expected regex substring.

5b. **AC-T.5b — Q-R2-A cross-field validator enforcement.** `tests/test_produced_asset_fulfills.py`:
   - Given `source_plan_unit_id="unit-foo"` and `fulfills="unit-foo@5"` — `ProducedAsset` instantiable.
   - Given `source_plan_unit_id="unit-foo"` and `fulfills="unit-bar@5"` — raises `pydantic.ValidationError` with message substring `"counterfeit-fulfillment seam"` AND `"source_plan_unit_id"` AND both values.
   - Given `source_plan_unit_id="unit-a"` and `fulfills="unit-a@0"` (bootstrap) — instantiable.
   - Parametrized over 3+ counterfeit-mismatch pairs exercising the cross-field invariant.

6. **AC-T.6 — Consumer-fixture contract tests (Murat R1 amendment + M-AM-4 R2 rename).** Three consumer-stub files live under `tests/fixtures/consumers/` and are **NOT** pytest-collected (M-AM-4): pytest only collects files starting with `test_`. These files are named `fixture_<story>_<agent>_consumer.py` and are imported + executed by a dedicated loader test:

   - `tests/fixtures/consumers/fixture_30_3_marcus_consumer.py` — minimal Marcus consumer stub: imports `MODALITY_REGISTRY`, demonstrates the scope-delegation + routing pattern (e.g., `modality_ref="blueprint"` → `get_modality_entry("blueprint").status == "ready"` → routing proceeds). **Q-R2-B (Quinn R2) staleness-gate-at-consumer-boundary pattern:** additionally demonstrates that given `context = ProductionContext(lesson_plan_revision=5, lesson_plan_digest="...")` and a `ProducedAsset` with `fulfills="unit-foo@5"`, the Marcus consumer verifies `int(asset.fulfills.split("@", 1)[1]) == context.lesson_plan_revision`. Documented as the "staleness gate at consumer boundary" pattern — downstream 30-3 / 30-4 will replicate.
   - `tests/fixtures/consumers/fixture_29_2_irene_consumer.py` — minimal Irene consumer stub: imports `MODALITY_REGISTRY`, demonstrates Irene's `modality_ref` validity check pattern. Given a `PlanUnit` with `modality_ref="slides"`, asserts `get_modality_entry("slides") is not None`; given `modality_ref="invalid"`, asserts `get_modality_entry("invalid") is None` (invalid modality_ref → Irene's diagnosis would flag it).
   - `tests/fixtures/consumers/fixture_28_2_tracy_consumer.py` — minimal Tracy consumer stub: imports `COMPONENT_TYPE_REGISTRY`, demonstrates Tracy dispatching based on composite (e.g., `component_type_ref="narrated-deck"` → routes enrichment against `modality_refs=("slides",)`).

   - **Loader contract test** (`tests/contracts/test_consumer_fixtures_load.py`) — imports each of the three fixture files via `importlib.util.spec_from_file_location` (because pytest does not auto-collect non-`test_` filenames), invokes each fixture's `demonstrate()` callable, and asserts no error. Blocks merge if any fixture breaks its API surface. Each fixture module defines a `demonstrate() -> None` function that the loader invokes.

7. **AC-T.7 — Stability snapshot.** After any registry change, snapshot diff shows expected drift and the `SCHEMA_CHANGELOG.md` entry is updated. Pattern from 31-1 AC-T.1 + 31-2 AC-T.1: each of the three AC-T.1 shape-pin tests ships a snapshot against the current module surface; any drift without a corresponding CHANGELOG entry → test fails. Keeps the registries governance-bound, not drift-tolerant.

8. **AC-T.8 — No-intake-orchestrator-leak grep (R1 amendment 17 + R2 rider S-3 carry-forward).** `tests/contracts/test_no_intake_orchestrator_leak_registries.py` scans all public-facing strings in:
   - `marcus/lesson_plan/modality_registry.py` field `description=` values + docstrings + module docstring.
   - `marcus/lesson_plan/component_type_registry.py` field `description=` values + docstrings + module docstring.
   - `marcus/lesson_plan/modality_producer.py` docstrings + module docstring.
   - `marcus/lesson_plan/produced_asset.py` docstrings + module docstring.
   - Each `ModalityEntry.description` / `ComponentTypeEntry.description` literal in the registry dict literals.

   Forbidden tokens: `intake`, `orchestrator` (case-insensitive). Internal taxonomy tokens (`marcus-intake` / `marcus-orchestrator` in the `log.py` WriterIdentity sense) are explicitly not public-facing on 31-3's surface — they do not appear in 31-3 modules at all. Test fails if any forbidden token is found.

9. **AC-T.9 — Suite-level gate (non-collecting AC).** **M-AM-1 (Murat R2 BINDING)** — baseline at commit `21b2d83` HEAD (31-2 closeout, rebased to actuals):
   - `--run-live`: **1478 passed** / 6 skipped / 2 deselected / 2 xfailed / 0 failed.
   - Default: **1456 passed** / 3 skipped / 27 deselected / 2 xfailed / 0 failed.

   Expected after 31-3 with K≥15 landing (realistic 58-65 new tests):
   - `--run-live`: **≥1493 passed** (K=15 floor) / target `≥1536 passed` (58 realistic).
   - Default: **≥1471 passed** / target `≥1514 passed`.

   No new `xfail`, no new `skip`, no new `live_api`, no new `trial_critical`, per `feedback_regression_proof_tests.md`. 31-3 is a pure-Python / Pydantic / file-read module with no network, no async, no platform-gated code — no expected `skipif`s.

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Package layout.** Four new modules under existing `marcus/lesson_plan/` package established by 31-1:
   - `marcus/lesson_plan/modality_registry.py` — `ModalityRef` Literal + `ModalityEntry` Pydantic + `MODALITY_REGISTRY` MappingProxyType + `get_modality_entry` + `list_ready_modalities` + `list_pending_modalities` + `SCHEMA_VERSION`.
   - `marcus/lesson_plan/component_type_registry.py` — `ComponentTypeEntry` Pydantic + `COMPONENT_TYPE_REGISTRY` MappingProxyType + `get_component_type_entry` + `SCHEMA_VERSION`.
   - `marcus/lesson_plan/modality_producer.py` — `ModalityProducer` ABC + `SCHEMA_VERSION`.
   - `marcus/lesson_plan/produced_asset.py` — `ProductionContext` Pydantic + `ProducedAsset` Pydantic + `_FULFILLS_REGEX` + `SCHEMA_VERSION`.

   **Judgment call on file split (Amelia):** pre-seed suggested a single `registries.py` consolidating everything. I'm splitting into four files because (a) each module has a focused single responsibility; (b) the three AC-T.1 shape-pin contract files map 1:1 to three separate modules (clean seam for Murat per-family rule); (c) `ProductionContext` + `ProducedAsset` co-locate in `produced_asset.py` because they're the produce-API input/output twins; (d) the four-file split makes the R1 amendment 7 "ABC complete-enough" review easier to conduct because the ABC surface lives in one file. If the R2 panel votes to consolidate (e.g., Winston prefers a single `registries.py`), I'll collapse — this is a judgment call, not a hard AC.

2. **AC-C.2 — `marcus/lesson_plan/__init__.py` extended.** Public surface added to `__all__` and imports:
   - From `modality_registry`: `MODALITY_REGISTRY`, `ModalityEntry`, `ModalityRef`, `get_modality_entry`, `list_ready_modalities`, `list_pending_modalities`.
   - From `component_type_registry`: `COMPONENT_TYPE_REGISTRY`, `ComponentTypeEntry`, `get_component_type_entry`.
   - From `modality_producer`: `ModalityProducer`.
   - From `produced_asset`: `ProductionContext`, `ProducedAsset`.

   Twelve new names total. Alphabetical ordering preserved in `__all__` per 31-1 / 31-2 convention.

3. **AC-C.3 — `SCHEMA_CHANGELOG.md` updated.** Extend `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` with three per-family entries (pattern from 31-2 AM-1 split):
   - `## Modality Registry v1.0 — 2026-04-18 — Story 31-3 Registries` — documents `ModalityEntry` shape, `ModalityRef` closed set (5 entries), initial registry state (2 ready + 3 pending), `MappingProxyType` immutability, query API.
   - `## Component Type Registry v1.0 — 2026-04-18 — Story 31-3 Registries` — documents `ComponentTypeEntry` shape, N=2 initial entries with rationale, composition constraint, query API.
   - `## ModalityProducer ABC v1.0 — 2026-04-18 — Story 31-3 Registries` — documents ABC surface, `ProductionContext` + `ProducedAsset` shapes, `fulfills` regex pin, produce-method contract.

   Each entry follows the 31-2 Lesson Plan Log entry pattern: Type, Reason, Shapes pinned, Semantics pinned, Migration (N/A — initial shape), Consumer surface.

4. **AC-C.4 — Initial modality set frozen at MVP.** The five `ModalityRef` values (`slides`, `blueprint`, `leader-guide`, `handout`, `classroom-exercise`) are the closed set at MVP. Adding a new modality requires:
   - (a) R1/R2-equivalent ruling amendment authorizing the widening.
   - (b) `modality_registry.SCHEMA_VERSION` minor bump (1.0 → 1.1) if additive, major bump (1.0 → 2.0) if renaming or status-semantics change.
   - (c) `SCHEMA_CHANGELOG.md` entry documenting the delta.
   - (d) Update to `ModalityRef` Literal + `MODALITY_REGISTRY` dict + all consumer tests.

   No backdoor. No runtime registration. No string-typed modality slipping through at a consumer site.

5. **AC-C.5 — Initial component_type set frozen at MVP (N=2, with rationale).** The two `component_type_ref` labels are:
   - **`narrated-deck`** — a single-modality composite (`modality_refs=("slides",)`). Names the minimal composite shape: an existing ready modality packaged for downstream narration binding (deferred to post-MVP). Chosen because slides is the pre-MVP existing producer (Gary/Gamma) and a narrated-deck is the Lesson Planner MVP's representative output shape.
   - **`motion-enabled-narrated-lesson`** — a two-modality composite (`modality_refs=("slides", "blueprint")`). Names a multi-modality composite composing the two `ready` modalities. Drawn from the existing prompt-pack vocabulary at [`docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`](../../docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md). Motion + narration are bound at the production-site (Kira/etc) outside 31-3's scope; the composite declares the shape at the package level.

   **Amelia rationale (R2 pressure-test target):** N=2 is mandated by R1 amendment 5; my chosen labels compose ONLY `ready` modalities to avoid cross-status coupling (a `pending` modality inside a composite would imply the composite is `pending` too, which adds a status-cascade rule the ABC doesn't model at MVP). `narrated-deck` + `motion-enabled-narrated-lesson` prove single-modality and multi-modality composite shapes respectively — the minimum needed to exercise the `modality_refs: tuple[str, ...]` field and the composition-validity check (AC-T.3).

   Widening beyond N=2 or adding `pending`-composite entries requires the same governance as AC-C.4 (amendment + version bump + CHANGELOG entry).

6. **AC-C.6 — `ModalityProducer.status` closed set + `producer_class_path` invariant.** `status` values are `Literal["ready", "pending"]` — closed set of two. A `pending` modality MUST have `producer_class_path: None`. A `ready` modality MAY have `producer_class_path: None` at 31-3 (Gary/Gamma slides and 31-4 blueprint are both `ready` but `producer_class_path` is backfilled by separate amendment stories; AC-B.1 table). The invariant that tests enforce (AC-T.1 shape-pin): if `status == "pending"`, `producer_class_path` MUST be `None`; if `status == "ready"`, `producer_class_path` MAY be `None` OR a dotted string path. Declared as a `model_validator(mode="after")` on `ModalityEntry`.

7. **AC-C.7 — Out-of-scope for 31-3.** Explicitly:
   - (a) **No actual producer implementations.** 31-4 ships blueprint-producer as a separate story. 31-3 ships ABC + registries + consumer fixtures only.
   - (b) **No retrofitting Gary (slides) to the ABC.** Gary/Gamma slides-producer is existing pre-MVP code that will adopt the ABC in a separate amendment story; that story backfills `MODALITY_REGISTRY["slides"].producer_class_path` via a minor schema bump. 31-3 ships `producer_class_path=None` for slides. Do NOT attempt a Gary-adoption refactor in 31-3 — it is out-of-scope and would break the 2pt sizing.
   - (c) **No multi-tenant registries.** Single-process in-memory module constants only. Per-tenant / per-run registry variation is out-of-scope.
   - (d) **No runtime registry extension.** Registries are compile-time / module-import-time only. Adding an entry at runtime (e.g., via a plugin discovery hook) is out-of-scope.
   - (e) **No cross-version conflict resolution between producers.** If two producers claim the same `modality_ref`, 31-3 does not resolve — that's a consumer-site concern.
   - (f) **No DAG resolution for composite packages.** `ComponentTypeEntry.modality_refs` is a flat tuple. Recursive composition (a composite composing another composite) is out-of-scope.
   - (g) **No operator-facing UI.** 31-3 is an internal targeting surface. Maya-facing descriptions are free-text but not rendered in this story.
   - (h) **No producer-specific dials in `ProductionContext`.** 30-3b ships dials; concrete producers subclass `ProductionContext` or consume a separate dial context at that time.

8. **AC-C.8 — Blocking rule for downstream.** 30-3 / 29-2 / 28-2 / 31-4 MUST consume the registries via the public query API (`get_modality_entry`, `get_component_type_entry`, `list_ready_modalities`, `list_pending_modalities`). Direct `MODALITY_REGISTRY[key]` access is PERMITTED (it's a public Mapping) but the query helpers are preferred because they return `None` on miss (dict KeyError is a sharper failure surface). `bmad-code-review` Blind Hunter scans for silent mutation attempts.

## File Impact (preliminary — refined at bmad-dev-story)

| File | Change | Lines (est.) | Tests (est.) |
|------|--------|-------|-------|
| `marcus/lesson_plan/modality_registry.py` | **New** — `ModalityRef` Literal + `ModalityEntry` + `MODALITY_REGISTRY` MappingProxyType + query helpers + `SCHEMA_VERSION` | +85 | — |
| `marcus/lesson_plan/component_type_registry.py` | **New** — `ComponentTypeEntry` + `COMPONENT_TYPE_REGISTRY` MappingProxyType + `get_component_type_entry` + `SCHEMA_VERSION` | +70 | — |
| `marcus/lesson_plan/modality_producer.py` | **New** — `ModalityProducer` ABC + `SCHEMA_VERSION` | +55 | — |
| `marcus/lesson_plan/produced_asset.py` | **New** — `ProductionContext` + `ProducedAsset` + `_FULFILLS_REGEX` + `SCHEMA_VERSION` | +90 | — |
| `marcus/lesson_plan/__init__.py` | **Touch** — extend `__all__` + imports (12 new names) | +20 | — |
| `tests/contracts/test_modality_registry_stable.py` | **New** — AC-T.1 shape-pin (snapshot + allowlist + CHANGELOG gate) | +110 | ~5 |
| `tests/contracts/test_component_type_registry_stable.py` | **New** — AC-T.1 shape-pin | +90 | ~4 |
| `tests/contracts/test_modality_producer_abc_stable.py` | **New** — AC-T.1 ABC + ProductionContext + ProducedAsset shape-pin | +110 | ~5 |
| `tests/contracts/test_consumer_fixtures_load.py` | **New** — AC-T.6 consumer-fixture loader contract (blocks merge if any fixture breaks) | +60 | ~3 |
| `tests/contracts/test_no_intake_orchestrator_leak_registries.py` | **New** — AC-T.8 no-leak grep | +70 | ~3 |
| `tests/test_registry_immutability.py` | **New** — AC-T.2 immutability matrix (parametrized over both registries) | +110 | ~8 |
| `tests/test_registry_query_api.py` | **New** — AC-T.3 query API matrix + composition validity | +120 | ~10 |
| `tests/test_modality_producer_abc.py` | **New** — AC-T.4 ABC contract (instantiation, abstract-method enforcement) | +90 | ~5 |
| `tests/test_produced_asset_fulfills.py` | **New** — AC-T.5 accept/reject matrix (M-AM-3 extended) + AC-T.5b Q-R2-A counterfeit matrix | +140 | ~28 |
| `tests/fixtures/consumers/__init__.py` | **New** — package marker | +1 | — |
| `tests/fixtures/consumers/fixture_30_3_marcus_consumer.py` | **New** (M-AM-4 rename) — Murat R1 amendment consumer stub (Marcus) + Q-R2-B staleness-gate pattern | +75 | not pytest-collected |
| `tests/fixtures/consumers/fixture_29_2_irene_consumer.py` | **New** (M-AM-4 rename) — Murat R1 amendment consumer stub (Irene) | +55 | not pytest-collected |
| `tests/fixtures/consumers/fixture_28_2_tracy_consumer.py` | **New** (M-AM-4 rename) — Murat R1 amendment consumer stub (Tracy) | +55 | not pytest-collected |
| `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` | **Touch** — three per-family entries (Modality / ComponentType / ModalityProducer ABC) | +75 | — |

**File count:** 4 new modules + 1 touched `__init__.py` + 5 new `tests/contracts/` files + 4 new `tests/` files + 4 new `tests/fixtures/consumers/` files + 1 touched SCHEMA_CHANGELOG. Target module LOC ~320; target total test LOC ~930. **Estimated collecting tests:** ~59 across all files (well above K=15 floor; many parametrized expansions per AC-T.5 fulfills regex and AC-T.2 immutability matrix bring the count up, but each family is ≤8 tests so per-family discipline holds).

## Tasks / Subtasks (preliminary — refined at bmad-dev-story)

- [x] **T1 — R2 party-mode green-light.** Panel: Winston (Architect) / Murat (TEA) / Quinn (Problem-Solver) / Paige (Tech Writer) / Sally (UX, light touch). Pressure-test the five PDG-1 items: R1 amendment 7 ABC completeness, N=2 label choice, consumer-fixture minimality, closed-set discipline, K-floor defense. Apply riders to spec if any. Flip status `ready-for-dev → in-progress` on T2 start.
- [x] **T2 — Pre-step: delete pre-seed scaffold files + land `marcus/lesson_plan/modality_registry.py`.** **W-1 (Winston R2):** DELETE `marcus/lesson_plan/registries.py` (pre-seed stub superseded by the four-file split), and DELETE the three pre-existing scaffold tests that import it: `tests/contracts/test_registries_shape_stable.py`, `tests/contracts/test_registries_json_schema_parity.py`, `tests/contracts/test_no_intake_orchestrator_leak_registries.py` (the last is replaced by the 31-3 four-module scan per AC-T.8). Then land `modality_registry.py`: `ModalityRef` Literal (5 values) + `ModalityEntry` Pydantic (with `model_validator(mode="after")` for AC-C.6 status×producer_class_path invariant) + `MODALITY_REGISTRY` dict literal → `MappingProxyType` + `SCHEMA_VERSION = "1.0"` + `get_modality_entry` + `list_ready_modalities` + `list_pending_modalities`.
- [x] **T3 — `marcus/lesson_plan/component_type_registry.py` landed.** `ComponentTypeEntry` Pydantic + `COMPONENT_TYPE_REGISTRY` dict literal → `MappingProxyType` + `SCHEMA_VERSION = "1.0"` + `get_component_type_entry` + composition-validity validator (every `modality_refs` element must be in `MODALITY_REGISTRY`). Imports `ModalityRef` from `modality_registry` module.
- [x] **T4 — `marcus/lesson_plan/modality_producer.py` landed.** `ModalityProducer` ABC with `modality_ref: ClassVar[str]`, `status: ClassVar[Literal["ready", "pending"]]`, `@abstractmethod def produce(self, plan_unit: PlanUnit, context: ProductionContext) -> ProducedAsset`. **M-AM-2:** `__init_subclass__` enforcement hook (CPython does NOT check ClassVar type hints — the hook is the actual enforcement). Imports `PlanUnit` from `marcus.lesson_plan.schema`, `ProductionContext` + `ProducedAsset` from sibling `produced_asset.py`.
- [x] **T5 — `marcus/lesson_plan/produced_asset.py` landed.** `ProductionContext` Pydantic (`lesson_plan_revision` ge=0, `lesson_plan_digest` min_length=1) + `ProducedAsset` Pydantic (with `fulfills` regex validator, `created_at` tz-aware validator, `modality_ref` typed as `ModalityRef`) + `_FULFILLS_REGEX` + `SCHEMA_VERSION = "1.0"`.
- [x] **T6 — `marcus/lesson_plan/__init__.py` extended.** `__all__` + imports for 12 new names (alphabetical order preserved).
- [x] **T7 — AC-T.1 shape-pin contract tests landed (three files).** `test_modality_registry_stable.py` + `test_component_type_registry_stable.py` + `test_modality_producer_abc_stable.py`. Snapshot + allowlist + CHANGELOG gate pattern from 31-1/31-2.
- [x] **T8 — AC-T.2 immutability tests landed.** `test_registry_immutability.py` parametrized over both registries × (set, del, clear, update, pop, popitem, setdefault, attribute assignment).
- [x] **T9 — AC-T.3 query API tests landed.** `test_registry_query_api.py` — positive/negative/edge-case lookup matrix + `list_ready` / `list_pending` parity + composition validity parametrized over component types.
- [x] **T10 — AC-T.4 ABC contract tests landed.** `test_modality_producer_abc.py` — bare instantiation raises, incomplete subclass raises, complete subclass works, smoke-test `produce()` call.
- [x] **T11 — AC-T.5 fulfills regex tests + AC-T.5b cross-field validator tests landed.** `tests/test_produced_asset_fulfills.py` — extended accept matrix (8+ cases per M-AM-3) + extended reject matrix (17+ cases per M-AM-3) + type-rejection tests + AC-T.5b Q-R2-A counterfeit-fulfillment matrix.
- [x] **T12 — AC-T.6 consumer-fixture files landed (3 files, M-AM-4 renamed) + contract loader test.** `tests/fixtures/consumers/__init__.py` + three `fixture_<story>_<agent>_consumer.py` files (NOT pytest-collected) + `tests/contracts/test_consumer_fixtures_load.py` (uses `importlib.util.spec_from_file_location` to import each fixture file and invoke its `demonstrate()` function). Each fixture is minimal import-and-usage + exposes a `demonstrate()` callable.
- [x] **T13 — AC-T.8 no-leak grep test landed.** `tests/contracts/test_no_intake_orchestrator_leak_registries.py` scans all four 31-3 modules for forbidden tokens.
- [x] **T14 — `SCHEMA_CHANGELOG.md` extended with three per-family entries.** Modality Registry v1.0 / Component Type Registry v1.0 / ModalityProducer ABC v1.0.
- [x] **T15 — Full regression green.** `--run-live` ≥ 1117 passed (K=15 floor) / target ≥1127; default ≥1095 / target ≥1105. Ruff clean. Pre-commit clean (ruff-lint + orphan-detector + co-commit-invariant all pass).
- [x] **T16 — G5 party-mode implementation review.** Panel: Winston / Murat / Quinn / Paige. Verify R1 amendment 7 ABC completeness, R1 amendment 5 resize scoping, Murat consumer-fixture landing. Apply G5 riders if any.
- [x] **T17 — G6 `bmad-code-review` layered pass.** Blind Hunter / Edge Case Hunter / Acceptance Auditor. Triage into APPLY / DEFER / DISMISS per story-cycle-efficiency §3 aggressive-DISMISS rubric. Apply MUST-FIX + SHOULD-FIX items.
- [x] **T18 — Close to `review`.** Flip status `in-progress → review`. Operator adjudicates `review → done` after sprint-status.yaml flip.

## Test Plan

`tests_added ≥ K` with **K = 15** (floor).

**K-floor defense:**
- 3 schema-pin contract files × ≥2 core tests each = ≥6 (AC-T.1)
- 1 immutability test file with ≥8 parametrized cases = 8 collecting (AC-T.2)
- 1 query API test file with ≥10 cases (positive + negative + parity + composition) = 10 collecting (AC-T.3)
- 1 ABC contract test file with ≥5 cases = 5 collecting (AC-T.4)
- 1 fulfills regex test file with 5 accept + 12 reject = 17 collecting (AC-T.5)
- 1 consumer-fixture loader test with 3 cases = 3 collecting (AC-T.6)
- 3 consumer fixture files with minimal stubs = 6 collecting (AC-T.6 per-file tests)
- 1 no-leak grep test with ≥3 cases = 3 collecting (AC-T.8)

**Realistic landing: ~58-65 collecting tests** (well above K=15 floor; per §1 cycle-efficiency, each extra is justified by specific coverage gap: parametrized expansion on fulfills regex and immutability matrix walks concrete attack surfaces, not theoretical parametrization inflation).

**K=15 is the pass/fail contract for §6-E4.** Landing estimate ~58–65. If count drops below 30, dev agent re-examines coverage gaps.

| Test | AC | Level | Mocked? | Blocking at merge? |
|------|----|-------|---------|---------------------|
| `test_modality_registry_stable` (snapshot + allowlist) | T.1 | Contract | N/A | **Yes — Murat per-family #1** |
| `test_component_type_registry_stable` (snapshot + allowlist) | T.1 | Contract | N/A | **Yes — Murat per-family #2** |
| `test_modality_producer_abc_stable` (snapshot + allowlist) | T.1 | Contract | N/A | **Yes — Murat per-family #3; R1 amendment 7 satisfaction surface** |
| `test_registry_immutability` (parametrized matrix) | T.2 | Unit | N/A | Yes |
| `test_registry_query_api` (parametrized positive/negative/parity/composition) | T.3 | Unit | N/A | Yes |
| `test_modality_producer_abc` (instantiation + abstract enforcement) | T.4 | Unit | N/A | Yes |
| `test_produced_asset_fulfills` (accept + reject + AC-T.5b counterfeit matrix) | T.5 / T.5b | Unit | N/A | **Yes — Quinn Tri-Phasic Contract + Q-R2-A surface** |
| `test_consumer_fixtures_load` (loader contract via `importlib.util`) | T.6 | Contract | N/A | **Yes — Murat R1 amendment + M-AM-4** |
| `test_no_intake_orchestrator_leak_registries` | T.8 | Contract | N/A | **Yes — R1 amendment 17 / R2 rider S-3 carry-forward** |

Baseline at commit `21b2d83` HEAD (31-2 closeout): `--run-live` ≥1102 passed / default ≥1080. Expected after 31-3: `--run-live` ≥1117 (K floor) / target ≥1127; default ≥1095 / target ≥1105. No new `xfail` / `skip` / `live_api` / `trial_critical`.

## Out-of-scope

31-3 is the **registries + ABC + consumer-fixture targeting surface** — it ships the closed-set catalogs, the abstract base class 31-4 implements, the produce-API payload shapes, and three minimal consumer stubs. Explicitly excluded:

- **Concrete producer implementations.** 31-4 ships blueprint-producer; Gary/Gamma slides-producer adopts the ABC in a separate amendment story. 31-3 ships the ABC only.
- **Gary retrofit to ABC.** Existing slides producer is pre-MVP; its ABC adoption is a separate integration story. `MODALITY_REGISTRY["slides"].producer_class_path = None` at 31-3; backfilled later.
- **Multi-tenant registries.** Single-process in-memory module constants. Per-tenant variation is out-of-scope.
- **Runtime registry extension.** Registries are module-import-time only. Plugin discovery hooks, dynamic registration, hot-reload — all out-of-scope.
- **DAG resolution for composite packages.** `ComponentTypeEntry.modality_refs` is a flat tuple. Recursive composites are out-of-scope.
- **Cross-version producer conflict resolution.** If two producers claim the same `modality_ref`, 31-3 does not arbitrate.
- **Operator-facing UI rendering.** `description` fields are free-text; rendering is a future story.
- **Producer-specific dials in `ProductionContext`.** 30-3b ships operator dials; concrete producers extend `ProductionContext` at 31-4 or via a separate dial-context primitive.
- **Actual `plan.locked` fanout wiring.** 30-4 reads `MODALITY_REGISTRY` at fanout time; 31-3 ships the registry only.
- **Envelope emission for `modality_ref`.** 30-3a/3b / 30-4 emit envelopes that carry `modality_ref`; 31-3 ships the registry they check against.

## Dependencies on Ruling Amendments

- **R1 ruling amendment 5 — 31-3 resize (3 → 2pts).** Entire story scope: registries + ABC + consumer fixtures only; no schema-shape expansion. AC-B.1 / AC-B.2 / AC-B.3 / AC-B.4 / AC-B.5 / AC-C.1 / AC-C.7.
- **R1 ruling amendment 7 — 31-4 HOLD at 5pts single story.** `ModalityProducer` ABC MUST be complete-enough that 31-4 lands without splitting. AC-B.3 (ABC surface) + AC-B.4 (ProductionContext minimality) + AC-B.5 (ProducedAsset fulfills) + PDG-1 (a) R2 pressure-test item.
- **Murat R1 amendment — Consumer-contract fixtures.** AC-B.6 query API + AC-T.6 consumer fixtures × 3 + AC-T.6 loader contract test. `tests/fixtures/consumers/` ships frozen for 30-3 / 29-2 / 28-2 to author against.
- **R1 ruling amendment 17 — Marcus is one voice.** AC-T.8 no-leak grep test across all four 31-3 modules.
- **R2 rider S-3 carry-forward (31-1) — Automated no-leak grep.** AC-T.8 ships the mandatory automated scan.
- **R2 rider AM-1 carry-forward (31-1/31-2) — Per-family shape pins.** AC-T.1 ships three separate contract files (not batched).
- **R2 rider S-2 carry-forward (31-1) — Free-text `description` has NO `min_length`.** AC-B.1 + AC-B.2 field descriptions.
- **Paige + Winston discipline carry-forward.** `SCHEMA_CHANGELOG.md` three per-family entries + audience-layered module docstrings.
- **Murat §6-E4 K-floor.** K=15; realistic landing 25–40; no new xfail/skip/live_api/trial_critical.

## Forward References — §6 PDG Gate

31-3 satisfies these §6 entries directly:
- **§6-E4** — Per-story `tests_added ≥ K` floor: K=15 for 31-3.

31-3 is upstream of §6-A1-5 (trial run readiness — Tracy modes exercised, blueprint producer failure-mode) via:
- 31-4 implements `ModalityProducer` → uses 31-3's ABC.
- 30-3 reads `MODALITY_REGISTRY` + `COMPONENT_TYPE_REGISTRY` → unblocked by 31-3.
- 29-2 references `modality_ref` validity → consumer fixture stub ships in 31-3.
- 28-2 dispatches based on `component_type_registry` → consumer fixture stub ships in 31-3.

31-3 does NOT satisfy §6-A / §6-B / §6-C / §6-D / §6-E1-3; those land on downstream stories.

**Concrete downstream unblocks:**
- 30-3a/3b cannot close until registry query API stable (31-3 AC-B.6 satisfies).
- 31-4 cannot open until `ModalityProducer` ABC landed (31-3 AC-B.3 satisfies).
- 29-2 cannot author `modality_ref` validity check without `MODALITY_REGISTRY` public API (31-3 AC-B.1 + AC-B.6 satisfies).
- 28-2 cannot author component-type dispatch without `COMPONENT_TYPE_REGISTRY` public API (31-3 AC-B.2 + AC-B.6 satisfies).

## Risks

| Risk | Mitigation |
|------|------------|
| **`ModalityProducer` ABC under-specified; forces 31-4 to split (violates R1 amendment 7)** | PDG-1 (a) R2 pressure-test item; Winston + Quinn jointly assert ABC completeness before `ready-for-dev`. If any gap flagged, 31-3 widens before dev-story. |
| **N=2 component-type labels are the wrong shape; downstream composes don't exercise the matrix** | PDG-1 (b) R2 pressure-test; `narrated-deck` + `motion-enabled-narrated-lesson` chosen to exercise single-modality and multi-modality shapes using only `ready` modalities. Widening requires schema-version bump + amendment. |
| **Consumer-contract fixtures over-reach into real consumer implementation; couples 31-3 to downstream impl choices** | PDG-1 (c) R2 pressure-test; AC-T.6 fixtures are MINIMAL import-and-usage stubs only — imports the registry, demonstrates the pattern, asserts API surface is consumable. No mock of downstream business logic. |
| **Registry silently widened at a consumer call-site (e.g., `MODALITY_REGISTRY = {...extra}` assignment)** | AC-B.8 `MappingProxyType` makes this impossible; `TypeError` raised. AC-T.2 immutability matrix enforces at CI. `bmad-code-review` Blind Hunter grep for `MODALITY_REGISTRY =` / `COMPONENT_TYPE_REGISTRY =` assignment attempts. |
| **Gary (slides) retrofit accidentally attempted in 31-3 scope creep** | AC-C.7 out-of-scope explicit; PDG-1 review surface. Retrofit is a separate amendment story; 31-3 ships `producer_class_path=None` for slides. |
| **`fulfills` regex accepts a malformed value via edge case** | AC-T.5 ships 5 accept + 12 reject matrix; each reject asserts explicit error message substring. Quinn Tri-Phasic Contract surface — must not leak malformed fulfills. |
| **Registry closed sets silently widened via a code path that doesn't bump SCHEMA_VERSION** | AC-T.1 snapshot + CHANGELOG gate pattern — any registry drift without a CHANGELOG entry → test fails. Same pattern 31-1/31-2 used. |
| **`ProductionContext` too minimal — 31-4 needs more shape** | PDG-1 (a) R2 pressure-test; if 31-4 needs more context, widen in 31-3 (not 31-4). Winston + Quinn joint call. |
| **Concrete producer at runtime has `modality_ref` not in `MODALITY_REGISTRY`** | AC-B.3 notes ABC does NOT enforce at instantiation; that's a consumer-site runtime check. Consumer fixture `test_30_3_marcus_reads_registries_fixture.py` demonstrates the pattern (check `get_modality_entry(producer.modality_ref)` before routing). |
| **R2 party-mode missed R1 amendment 7 satisfaction check** | PDG-1 (a) BINDING — 31-3 NOT authorized to enter `bmad-dev-story` until Winston + Quinn sign off on ABC completeness. Checklist item is BINDING, not optional. |

## Dev Notes

### Architecture (per R1 rulings 5 + 6 + 7, Murat consumer-fixture amendment)

- **Two registries + one ABC + two payload shapes.** That's the entire 31-3 surface. Resist adding `RegistryManager`, `ProducerRegistry`, `ComponentTypeResolver`. The module-level `MappingProxyType` constants + query helpers are the entire runtime API.
- **Registries are CLOSED at MVP.** Unlike `event_type_registry` (which WARNs on unknown for Gagné-seam extensibility), `modality_registry` and `component_type_registry` are closed sets. Widening requires schema-version bump + amendment + CHANGELOG entry. This is a deliberate divergence from the event-type registry's semantics.
- **ABC is minimal + complete-enough for 31-4 (R1 amendment 7).** `produce()` + `modality_ref: ClassVar[str]` + `status: ClassVar[Literal["ready", "pending"]]`. No additional hooks. No `setup()`, no `teardown()`, no `validate()`. 31-4 will push against this if it needs more; resist until concrete need surfaces. The R2 panel's job is to pressure-test this exact minimality.
- **Consumer fixtures are import-and-usage stubs, not mocks.** `tests/fixtures/consumers/test_30_3_*_fixture.py` imports the registry, demonstrates the pattern, asserts the surface works. No mock of Marcus business logic, no mock of Irene diagnosis flow, no mock of Tracy dispatch. Downstream stories (30-3 / 29-2 / 28-2) import the fixture as a reference shape for their consumer tests.
- **`ProducedAsset.fulfills` is the tri-phasic contract surface.** Every produced asset carries `fulfills: {unit_id}@{plan_revision}`. This is Quinn's execution-phase pin from the plan doc §Quinn's Tri-Phasic Contract. 31-5 Quinn-R gate consumes this at step 13.
- **Four-file split is intentional.** Each module has one responsibility; `produced_asset.py` co-locates the produce-API twins. If R2 panel votes for consolidation, collapse — this is a judgment call.

### Anti-patterns (dev-agent WILL get these wrong without explicit warning)

- **Do NOT widen the `ModalityRef` Literal at a consumer site.** `Literal["slides", "blueprint", "leader-guide", "handout", "classroom-exercise"]` is the closed set per AC-C.4. Widening requires schema-version bump + amendment + `SCHEMA_CHANGELOG` entry + update to `MODALITY_REGISTRY` dict + test updates. No backdoor. No `ModalityRef | str` union type.
- **Do NOT widen the N=2 component-type set at a consumer site.** Same discipline as above; AC-C.5.
- **Do NOT attempt to mutate the registries at runtime.** `MappingProxyType` enforces at import + assignment time. Any mutation attempt is a `TypeError`. AC-T.2 parametrized matrix catches at CI.
- **Do NOT retrofit Gary (slides) to the ABC in 31-3.** Out-of-scope per AC-C.7 (b). Gary's ABC adoption is a separate amendment story; 31-3 ships `producer_class_path=None` for slides and moves on.
- **Do NOT add a `RegistryManager` / `ProducerRegistry` / `ComponentTypeResolver` class.** Two module-level constants + eight module-level functions. That's it. Proliferation is a code-review MUST-FIX.
- **Do NOT batch shape-pin tests into one file.** Per R2 rider AM-1 carry-forward on 31-1/31-2: three separate contract files, one per shape family. `test_modality_registry_stable.py` + `test_component_type_registry_stable.py` + `test_modality_producer_abc_stable.py`.
- **Do NOT leak `intake` / `orchestrator` in Maya-facing prose.** Registry entry descriptions, module docstrings, companion docs — all scanned by AC-T.8. Internal module names (`marcus.lesson_plan.*`) are exempt because they're not user-facing, but any `description=` literal or docstring is.
- **Do NOT let consumer fixtures over-reach into real consumer impl.** AC-T.6 fixtures are IMPORT-AND-USAGE stubs. No mock of Marcus business logic. No fake 4A loop. No simulated Irene diagnosis. Just: "here's how a consumer imports and uses the registry."
- **Do NOT let `ProducedAsset.fulfills` accept anything the regex rejects.** AC-B.7 + AC-T.5 matrix. If a reject case slips through, the tri-phasic contract is broken.
- **Do NOT add `xfail` or `skip` to the default suite.** Per `feedback_regression_proof_tests.md`. 31-3 has no platform-gated code, no network, no async — no expected `skipif`s. Any skip is a red flag.
- **Do NOT bypass the query helpers for exotic lookup patterns.** `get_modality_entry` / `get_component_type_entry` / `list_ready_modalities` / `list_pending_modalities` cover every legitimate use case. If a consumer needs something else, propose a new helper via amendment — don't reach into the dict directly with exotic slicing. (Direct `MODALITY_REGISTRY["slides"]` access IS permitted for known-key reads; the KeyError vs None distinction is intentional.)

### Source tree (new + touched)

```
marcus/lesson_plan/                                  [EXISTS — 31-1 + 31-2]
├── __init__.py                                      [TOUCH +20]  Extend __all__ with 12 new names
├── modality_registry.py                             [NEW +85]    ModalityRef Literal + ModalityEntry + MODALITY_REGISTRY MappingProxyType + query helpers
├── component_type_registry.py                       [NEW +70]    ComponentTypeEntry + COMPONENT_TYPE_REGISTRY MappingProxyType + query helper
├── modality_producer.py                             [NEW +55]    ModalityProducer ABC
├── produced_asset.py                                [NEW +90]    ProductionContext + ProducedAsset + _FULFILLS_REGEX
├── schema.py                                        [EXISTS — 31-1; unchanged]
├── events.py                                        [EXISTS — 31-1; unchanged]
├── digest.py                                        [EXISTS — 31-1; unchanged]
├── event_type_registry.py                           [EXISTS — 31-1; unchanged]
├── log.py                                           [EXISTS — 31-2; unchanged]
├── dials-spec.md                                    [EXISTS — 31-1; unchanged]
├── registries.py                                    [EXISTS — scaffold stub from pre-seed; SUPERSEDED by four new files; operator adjudicates deletion or retention per AC-C.1 judgment call]
└── schema/                                          [EXISTS — 31-1; unchanged]

tests/contracts/
├── test_modality_registry_stable.py                 [NEW +110]   AC-T.1 per-family shape pin
├── test_component_type_registry_stable.py           [NEW +90]    AC-T.1 per-family shape pin
├── test_modality_producer_abc_stable.py             [NEW +110]   AC-T.1 per-family shape pin (ABC + ProductionContext + ProducedAsset)
├── test_consumer_fixtures_load.py                   [NEW +60]    AC-T.6 loader contract (blocks merge if any fixture breaks)
└── test_no_intake_orchestrator_leak_registries.py   [NEW +70]    AC-T.8 no-leak grep

tests/
├── test_registry_immutability.py                    [NEW +110]   AC-T.2 MappingProxyType immutability matrix
├── test_registry_query_api.py                       [NEW +120]   AC-T.3 query API + composition validity
├── test_modality_producer_abc.py                    [NEW +90]    AC-T.4 ABC instantiation + abstract enforcement
└── test_produced_asset_fulfills.py                  [NEW +140]   AC-T.5 accept+reject matrix (M-AM-3) + AC-T.5b Q-R2-A counterfeit cross-field

tests/fixtures/consumers/
├── __init__.py                                      [NEW +1]     package marker
├── fixture_30_3_marcus_consumer.py                  [NEW +75]    AC-T.6 Marcus stub + Q-R2-B staleness-gate pattern (NOT auto-collected; loader imports)
├── fixture_29_2_irene_consumer.py                   [NEW +55]    AC-T.6 Irene stub (NOT auto-collected; loader imports)
└── fixture_28_2_tracy_consumer.py                   [NEW +55]    AC-T.6 Tracy stub (NOT auto-collected; loader imports)

_bmad-output/implementation-artifacts/
└── SCHEMA_CHANGELOG.md                              [TOUCH +75]  Three per-family entries
```

### Testing standards (inherited from 27-0 / 31-1 / 31-2 discipline)

- **No `live_api`, no `trial_critical`, no `xfail`, no `skip`** on the default suite. 31-3 has no platform-gated code, no network, no async — zero skipif expected.
- **Schema pins use snapshot + allowlist + CHANGELOG gate** (Murat pattern from 27-0 / 31-1 / 31-2 AC-T.1).
- **Deterministic fixtures only.** Registries are compile-time constants; tests read module state directly. No stateful mocks, no tmp_path (nothing to write).
- **Three separate shape-pin contract files** (Murat per-family AM-1 rule carry-forward from 31-1/31-2).
- **Consumer fixtures are minimal.** Import + assert API-surface-is-consumable. No business-logic simulation.
- **Per `feedback_regression_proof_tests.md`:** no xfail, no skip, classify every failure (update/restore/delete), measure coverage.

### References

- **Pattern source (closest shape):** [`31-2-lesson-plan-log.md`](./31-2-lesson-plan-log.md) — metadata header, AC layering, File Impact, Tasks, Test Plan, Dev Notes, Governance Closure Gates, R1/R2 traceability table.
- **Pre-seed reference (non-authoritative):** [`../specs/pre-seed-drafts/31-3-registries-PRE-SEED.md`](../specs/pre-seed-drafts/31-3-registries-PRE-SEED.md).
- **Plan doc (R1 orchestrator ruling):** [`../planning-artifacts/lesson-planner-mvp-plan.md`](../planning-artifacts/lesson-planner-mvp-plan.md) — §Orchestrator Ruling Record amendments 5, 6, 7, 17; §Epic 31 31-3 row; §Quinn's Tri-Phasic Contract; §Winston's Data Primitives.
- **Governance:** [`CLAUDE.md`](../../CLAUDE.md) — BMAD sprint governance; R2 party-mode green-light + `bmad-code-review` before `done`; stop-on-impasse-only.
- **Prompt-pack vocabulary:** [`docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`](../../docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md) — source for `motion-enabled-narrated-lesson` component-type label (AC-C.5).
- **Foundation consumed (31-1):** `marcus/lesson_plan/schema.py` (`PlanUnit`, `_OPEN_ID_REGEX`, `SCHEMA_VERSION` convention), `marcus/lesson_plan/__init__.py`.
- **Foundation consumed (31-2):** `marcus/lesson_plan/log.py` (not directly imported; 31-3 does NOT write to the log — producers emit `ProducedAsset` which downstream 30-4 fanout writes). Log is background context, not a 31-3 dependency.
- **Dev-guides:** [`docs/dev-guide/pydantic-v2-schema-checklist.md`](../../docs/dev-guide/pydantic-v2-schema-checklist.md), [`docs/dev-guide/dev-agent-anti-patterns.md`](../../docs/dev-guide/dev-agent-anti-patterns.md), [`docs/dev-guide/story-cycle-efficiency.md`](../../docs/dev-guide/story-cycle-efficiency.md).
- **MEMORY:** `project_enrichment_vs_gap_filling_control.md` (three-parameter family observed by producers at runtime), `feedback_regression_proof_tests.md` (no-xfail-no-skip discipline), `feedback_bmad_workflow_discipline.md` (R2 party-mode + code-review before `done`).

### Non-goals

- **No real 31-4 producer emission from 31-3.** 31-4 lands separately; 31-3 ships the ABC shell.
- **No Gary (slides) retrofit.** Separate amendment story.
- **No `MODALITY_REGISTRY["slides"].producer_class_path` backfill.** Happens in Gary-retrofit story.
- **No `MODALITY_REGISTRY["blueprint"].producer_class_path` backfill.** Happens in 31-4.
- **No LLM calls, no network, no async, no concurrency.** Pure Python + Pydantic + module constants.
- **No performance optimization.** Registries are O(1) dict lookups; N=5 + N=2 entries.
- **No migration path for v0.** This is v1.0 for all three shape families; first ship.
- **No operator-facing prose rendering.** Descriptions are internal.

## Governance Closure Gates (per CLAUDE.md)

31-3 closes `done` only when ALL below satisfied:

- [x] **G1. R2 party-mode green-light** on this spec. Panel: Winston / Murat / Quinn / Paige / Sally (light). PDG-1 binding checklist items (a)-(e) all surfaced explicitly. Verdict recorded in §R2 Green-Light Record.
- [x] **G2. `bmad-dev-story` execution** with all T1–T18 subtasks checked.
- [x] **G3. `tests_added ≥ 15`** collecting (§6-E4 floor). Target 18–23 minimum; realistic landing 25–40.
- [x] **G4. Ruff clean + pre-commit green + co-commit test+impl discipline** (27-2 / 31-1 / 31-2 pattern).
- [x] **G5. Party-mode implementation review.** Winston GREEN on architecture (including R1 amendment 7 satisfaction on delivered ABC) + Murat GREEN on test coverage of registries + consumer fixtures + Quinn GREEN on tri-phasic contract surface (`fulfills` regex) + Paige on docstring / anti-pattern discipline.
- [x] **G6. `bmad-code-review` layered pass** — Blind Hunter / Edge Case Hunter / Acceptance Auditor. Triage: APPLY (MUST-FIX + high-value SHOULD-FIX) / DEFER (logged to `_bmad-output/maps/deferred-work.md`) / DISMISS (cosmetic NITs per aggressive-DISMISS rubric).
- [x] **G7. `sprint-status.yaml` flipped** `ready-for-dev → in-progress → review → done` per bmm workflow. Operator-gated flip to `done`.
- [x] **G8. `bmm-workflow-status.yaml` updated** with closure note naming test delta + R1 amendment 7 ABC-completeness landing. Operator-gated flip.
- [x] **G9. Unblocks downstream.** Verify 31-4 / 30-3 / 29-2 / 28-2 all now have a green 31-3 dependency. Consumer fixtures committed under `tests/fixtures/consumers/` ready for downstream consumption.

## Dev Agent Record

**Executed by:** Amelia (bmad-agent-dev), Claude Opus 4.7 (1M context).
**Date:** 2026-04-18.
**Commit:** `<to be filled by closing commit>` (on branch `dev/lesson-planner`).

**T2–T14 landed files (line counts):**
- `marcus/lesson_plan/modality_registry.py` — 218 lines (new)
- `marcus/lesson_plan/component_type_registry.py` — 160 lines (new)
- `marcus/lesson_plan/modality_producer.py` — 126 lines (new)
- `marcus/lesson_plan/produced_asset.py` — 196 lines (new)
- `marcus/lesson_plan/__init__.py` — 125 lines (+42 from 90)
- `tests/contracts/test_modality_registry_stable.py` — 162 lines (new)
- `tests/contracts/test_component_type_registry_stable.py` — 139 lines (new)
- `tests/contracts/test_modality_producer_abc_stable.py` — 169 lines (new)
- `tests/contracts/test_consumer_fixtures_load.py` — 80 lines (new)
- `tests/contracts/test_no_intake_orchestrator_leak_registries.py` — 111 lines (replaces W-1 deleted scaffold)
- `tests/contracts/test_lesson_plan_package_exports_31_3.py` — 45 lines (new, G6 SHOULD-FIX)
- `tests/test_modality_registry_immutability.py` — 120 lines (new)
- `tests/test_modality_registry_query_api.py` — 254 lines (new; includes G6 AC-C.6 + AC-B.4 additions)
- `tests/test_modality_producer_abc_contract.py` — 204 lines (new)
- `tests/test_produced_asset_fulfills.py` — 177 lines (new)
- `tests/fixtures/consumers/__init__.py` — 7 lines (new)
- `tests/fixtures/consumers/fixture_30_3_marcus_consumer.py` — 84 lines (new; Q-R2-B staleness-gate)
- `tests/fixtures/consumers/fixture_29_2_irene_consumer.py` — 33 lines (new)
- `tests/fixtures/consumers/fixture_28_2_tracy_consumer.py` — 41 lines (new)
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — three per-family entries added.

**W-1 deletions:**
- `marcus/lesson_plan/registries.py` (78-line pre-seed stub).
- `tests/contracts/test_registries_shape_stable.py` (58-line scaffold).
- `tests/contracts/test_registries_json_schema_parity.py` (70-line scaffold).
- Pre-existing `tests/contracts/test_no_intake_orchestrator_leak_registries.py` (71-line scaffold with `pytestmark = pytest.mark.skip`) — replaced by the 31-3 four-module version.

**Total: 4 new modules + 1 touched __init__.py + 10 new test files + 3 consumer fixtures + 1 fixture package marker + SCHEMA_CHANGELOG extended. LOC: ~820 module (incl. __init__ delta) + ~1600 test/fixture. 156 collecting tests.**

**Test regression:**
- `--run-live`: 1644 passed / 6 skipped / 2 deselected / 2 xfailed / 0 failed (baseline 1478; delta +166; floor ≥1493 cleared by 151).
- Default: 1622 passed / 3 skipped / 27 deselected / 2 xfailed / 0 failed (baseline 1456; delta +166; floor ≥1471 cleared by 151).
- Zero new `xfail` / `skip` / `live_api` / `trial_critical`.

**Gate summary:** G1 R2 GREEN + 9 riders applied; G2 T1–T18 [x]; G3 tests_added 156 ≥ K=15 (10.4×); G4 ruff clean + pre-commit green on all 31-3 files; G5 self-conducted GREEN after one Murat rider (applied); G6 self-conducted 6 APPLY + 2 DEFER + 4 DISMISS; G7/G8 YAMLs updated; G9 downstream unblocks (31-4 / 30-3 / 29-2 / 28-2 / 30-4 / 31-5) enumerated.

## Review Record

### Party-mode R2 green-light — APPLIED (2026-04-18)

**Panel:** Winston (Architect) / Murat (TEA) / Quinn (Problem-Solver) / Paige (Tech Writer) / Sally (UX, light).

**PDG-1 binding checklist — all cleared with 9 riders applied:** see §R2 Green-Light Rider Block above.

**Panel:** Winston (Architect) / Murat (TEA) / Quinn (Problem-Solver) / Paige (Tech Writer) / Sally (UX, light).

**PDG-1 binding checklist:**
- [x] (a) R1 amendment 7 satisfaction — `ModalityProducer` ABC is complete-enough for 31-4 (5pt single story) to land without splitting. Winston + Quinn joint verdict.
- [x] (b) N=2 component-type choice — `narrated-deck` + `motion-enabled-narrated-lesson` prove single-modality and multi-modality shapes, compose only `ready` modalities. Winston + Sally verdict.
- [x] (c) Consumer-fixture minimality — three `tests/fixtures/consumers/*.py` files are import-and-usage stubs, not mocked consumer logic. Murat verdict.
- [x] (d) Closed-set discipline — `MODALITY_REGISTRY` + `COMPONENT_TYPE_REGISTRY` wrapped in `MappingProxyType`; widening requires amendment + version bump + CHANGELOG entry. Winston + Murat verdict.
- [x] (e) K-floor defense — K=15; realistic landing 25–40 with coverage-gap justification per extra ~5 tests beyond 22. Murat verdict.

_[Verdict + rider amendments recorded here at T1 completion.]_

### G5 Party-mode implementation review — SELF-CONDUCTED (2026-04-18)

**Mode:** Self-conducted by Amelia per operator directive (31-3 is pattern-tight 2pt; pattern discipline mirrors 31-1/31-2). Panel voices synthesized from landed code + tests.

**Winston (Architecture) — GREEN.**
- R1 amendment 7 ABC completeness: `ModalityProducer` surface (`modality_ref` + `status` ClassVars + `produce()` abstract + `__init_subclass__` M-AM-2 hook) + `ProductionContext` (minimal + W-2 extensibility seam) + `ProducedAsset` (regex-pinned `fulfills` + Q-R2-A cross-field) — 31-4 can land without splitting.
- Four-file split: one responsibility per module; `produced_asset.py` correctly co-locates `ProductionContext` + `ProducedAsset` produce-API twins.
- `MappingProxyType` wrapping dict literal — textbook closed-set discipline. Import-time assertion in `component_type_registry.py` adds defense-in-depth against seed typos.
- `collections.abc.Mapping` used correctly (not `typing.Mapping` — deprecated).
- AC-C.6 invariant (`status == "pending"` implies `producer_class_path is None`) enforced by `@model_validator(mode="after")`; smoke-probed at G5.

**Murat (Test coverage) — GREEN-after-rider.**
- 148 collecting tests against K=15 floor (9.9×). Landing above 58-65 realistic target.
- AC-T.1 three separate shape-pin files — per-family discipline.
- AC-T.2 parametrized matrix exercises every MappingProxyType attack vector × both registries; 24 tests.
- AC-T.3 query API: 28 tests including positive, negative, edge-case, parity, composition validity.
- AC-T.4 ABC contract: 10 tests covering all 6 M-AM-2 matrix items (a-f) + abstract + registry-membership note.
- AC-T.5 fulfills regex + AC-T.5b Q-R2-A: 35 tests total (8 accept + 17 reject + 3 type-rej + 7 Q-R2-A).
- AC-T.6 consumer fixtures: 10 tests (3 × file-exists + 3 × imports/demonstrate + 3 × demonstrate-runs + 1 no-auto-collect sanity).
- AC-T.8 no-leak: 10 tests (4 files + 4 models + registry entries + dump).
- **Rider (applied in-place):** G5-M-1 — strengthen `test_valid_subclass_is_instantiable` to additionally assert ClassVar values on the instance AND on the class (previously only `isinstance` check). Applied.

**Paige (Doc discipline) — GREEN.**
- P-R2-1 audience-layered module docstrings: all 4 modules first-line audience. Note: "Marcus (30-3 consumer)" used instead of "Marcus-Orchestrator (30-3)" to respect AC-T.8 no-leak grep — the audience signal is preserved without triggering the forbidden-token scan. Judgment call flagged transparently.
- Free-text `description` fields: no `min_length` (R2 rider S-2 carry-forward). Verified.
- R1 amendment 17 / R2 rider S-3 no-leak scan passes (10/10 test cases).
- Anti-pattern documentation in module docstrings covers runtime registry extension, mutation, Gary retrofit, producer proliferation.

**Amelia (Self-review) — HIGH confidence.**
- Judgment calls transparently flagged: (a) "Marcus (30-3 consumer)" softening per above; (b) `tests/fixtures/consumers/__init__.py` is intentional package marker — verified pytest does not auto-collect the dir (confirmed via `pytest --collect-only tests/fixtures/consumers/` → 0 collected).
- Pre-existing scaffold files deleted per W-1: `marcus/lesson_plan/registries.py` + three scaffold test files that imported it (`test_registries_shape_stable.py`, `test_registries_json_schema_parity.py`, `test_no_intake_orchestrator_leak_registries.py`). The last was replaced by the 31-3 four-module version.
- All imports wire cleanly; `__init__.py` extended with 13 new names (alphabetical); full suite imports without error.
- Ruff clean on all new/touched files. Pre-commit passes on all 31-3 files (the repo-wide 199 pre-existing ruff errors are pre-existing in unrelated modules; not introduced by 31-3).

**G5 verdict:** GREEN (all four voices; one small Murat rider applied in-place). Proceed to G6.

### G6 bmad-code-review layered pass — SELF-CONDUCTED (2026-04-18)

**Mode:** Self-conducted by Amelia per operator directive. Three layers walked: Blind Hunter (correctness / dead code / brittle patterns), Edge Case Hunter (branch/boundary), Acceptance Auditor (every AC walked against its enforcing test).

**Blind Hunter — 0 MUST-FIX / 1 SHOULD-FIX / 4 NITs.**
- SHOULD-FIX: `_fulfills_regex` inner `isinstance(value, str)` guard is dead code — Pydantic v2 rejects non-string types at the field level before the validator runs. Belt-and-suspenders clarity; DEFER.
- NIT: `_MODALITY_REGISTRY_UNDERLYING` + `_COMPONENT_TYPE_REGISTRY_UNDERLYING` are leading-underscore shadowed dicts — determined code can bypass `MappingProxyType` by importing the underlying. Acceptable at MVP; DEFER note.
- NIT: `# noqa: S101` in `component_type_registry.py` references Bandit rules not in the active ruff select list; harmless forward-compat. DEFER.
- NIT (x2 more): inline function-local imports in a few tests; could be moved to module top. DISMISS (style-only).

**Edge Case Hunter — 0 MUST-FIX / 1 SHOULD-FIX / 0 NITs.**
- Walked: empty registry, frozen-entry mutation, leading-zero/multi-zero revision edges, empty unit_id in counterfeit, `@` in `source_plan_unit_id`, negative/empty ProductionContext fields, unregistered-modality-Literal-widening defense-in-depth, all covered or defensibly documented.
- SHOULD-FIX: `ProducedAsset.source_plan_unit_id` has `min_length=1` but NO regex — could accept `"unit-a@"` (with `@`) while practical flow always sources from `PlanUnit.unit_id` which IS regex-clean. The Q-R2-A validator catches the `@`-including case as counterfeit because `fulfills.split("@", 1)[0]` differs, but a stricter regex on `source_plan_unit_id` is defensive. DEFER — likely a 31-4 / 30-4 follow-up.

**Acceptance Auditor — 1 MUST-FIX / 2 SHOULD-FIX / 0 NITs.**
- MUST-FIX (APPLIED): AC-C.6 invariant (`status == "pending"` implies `producer_class_path is None`) — validator exists on `ModalityEntry` but NO dedicated test asserted rejection of a hand-built `ModalityEntry(status="pending", producer_class_path="x.y.z")`. Smoke-probed at G5 but no persistent test. Added three tests: `test_ac_c_6_pending_status_implies_null_producer_class_path`, `test_ac_c_6_ready_may_have_null_producer_class_path`, `test_ac_c_6_ready_may_have_dotted_producer_class_path`.
- SHOULD-FIX (APPLIED): AC-B.4 negative ProductionContext construction tests — added `test_production_context_rejects_negative_revision`, `test_production_context_rejects_empty_digest`, `test_production_context_accepts_zero_revision_bootstrap`.
- SHOULD-FIX (APPLIED): AC-C.2 direct test on `marcus/lesson_plan/__init__.py` public surface — new file `tests/contracts/test_lesson_plan_package_exports_31_3.py` with two tests asserting all 12 new names are in `__all__` AND importable.

**G6 triage summary:**
- **APPLY: 6** (1 MUST-FIX + 5 SHOULD-FIX) — all 4 Acceptance-Auditor issues addressed via 8 new tests.
- **DEFER: 2** (1 Blind SHOULD-FIX [_fulfills_regex dead guard] + 1 Edge SHOULD-FIX [source_plan_unit_id regex]) — logged to `_bmad-output/maps/deferred-work.md §31-3 G5+G6 deferred findings`.
- **DISMISS: 4** (cosmetic NITs per aggressive-DISMISS rubric) — counted transparently.

**G6 verdict:** CLEAR after in-place remediation. Test landing updated to 156 collecting (148 at T2-T13 + 8 G6 remediation). Ruff clean maintained. Pre-commit clean maintained.

## R1 + R2 Orchestrator Ruling Traceability

| Ruling | Source | Applied in 31-3 |
|---|---|---|
| **R1 amendment 5** — 31-3 resize (3 → 2pts); schema work moved to 31-1 | Plan doc §Orchestrator Ruling Record item 5 | Entire story scope; AC-B.1-5 / AC-C.1 / AC-C.7 |
| **R1 amendment 6** — Registries + ABC + consumer fixtures only | Plan doc §Epic 31 31-3 row | AC-B.1 / AC-B.2 / AC-B.3 / AC-B.6 / AC-T.6 |
| **R1 amendment 7** — 31-4 HOLD at 5pts single story; ABC must be complete-enough | Plan doc §Orchestrator Ruling Record item 7 | AC-B.3 / AC-B.4 / AC-B.5 / PDG-1 (a) R2 pressure-test |
| **Murat R1 amendment** — Consumer-contract fixtures | Plan doc §Epic 31 31-3 row | AC-B.6 + AC-T.6 × 3 fixtures + loader contract test |
| **R1 amendment 17** — Marcus is one voice | Plan doc §Orchestrator Ruling Record item 17 | AC-T.8 no-leak grep test |
| **R2 rider S-3 carry-forward (31-1)** — Automated no-leak grep | 31-1 R2 Review Record | AC-T.8 |
| **R2 rider AM-1 carry-forward (31-1/31-2)** — Per-family shape pins | 31-1 / 31-2 R2 Review Records | AC-T.1 three separate contract files |
| **R2 rider S-2 carry-forward (31-1)** — Free-text no min_length | 31-1 R2 Review Record | AC-B.1 / AC-B.2 description fields |
| **Pydantic-v2 checklist §4** — Closed-enum triple red-rejection | `docs/dev-guide/pydantic-v2-schema-checklist.md` | AC-B.1 / AC-B.3 status Literal + AC-T.1 shape pin |
| **Murat §6-E4** — Per-story K-floor | Plan doc §6 Readiness PDG | K=15 floor; §Test Plan defense |
| **Story-cycle-efficiency §1** — K-floor discipline (1.2–1.5× K target) | `docs/dev-guide/story-cycle-efficiency.md` | §Test Plan realistic landing 25–40 with named gaps |
| **Quinn Tri-Phasic Contract** — `fulfills: unit_id@plan_revision` | Plan doc §Quinn's Tri-Phasic Contract | AC-B.5 + AC-B.7 + AC-T.5 accept/reject matrix |
| **Winston Data Primitives** — two-registry separation; ModalityProducer ABC | Plan doc §Winston's Data Primitives | AC-B.1 / AC-B.2 / AC-B.3 |
