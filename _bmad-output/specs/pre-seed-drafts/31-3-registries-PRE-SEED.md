# Story 31-3: Registries — `modality_registry` + `component_type_registry` + `ModalityProducer` ABC

> **⚠️ PRE-SEED DRAFT — NOT AUTHORITATIVE ⚠️**
>
> This file is a **pre-seed skeleton** authored 2026-04-18 in neutral orchestrator voice
> during a late Cowork-side session to save cycle time on the Lesson Planner MVP. It
> was **NOT authored via the real `bmad-create-story` workflow** and has **not been
> through R2 party-mode review**. The **authoritative 31-3 story spec** will be written
> by the Cursor + Claude-Code side via `bmad-create-story` invoked as Amelia, landing
> at `_bmad-output/implementation-artifacts/31-3-registries.md`. When that spec lands,
> this file becomes historical reference only.
>
> **Use this file as:** mid-flight input material for the Cursor-side authoring pass —
> architecture sketches (Pydantic registry models, ABC shape), AC candidates, T-task
> candidates, file-impact table, K-floor floor. The Cursor-side authoring must still
> run the discover-inputs protocol, template.md section-fill, and the checklist
> validation pass from `.agents/skills/bmad-create-story/`.
>
> **Do not set status to `ready-for-dev`, `in-progress`, `review`, or `done` from this
> file.** Sprint-status.yaml authority for 31-3 is driven by the authoritative spec,
> not by this pre-seed.
>
> **Relocated** 2026-04-18 from `_bmad-output/implementation-artifacts/31-3-registries.md`
> to avoid collision with the Cursor-side `bmad-create-story` write (which targets the
> original path). See sprint-status.yaml § EPIC 31 → `31-3-registries` for the pointer.

---

**Status:** PRE-SEED DRAFT (NOT authoritative; skeleton authored post-31-1 closeout; inherits R1 ruling amendment 6 resize 3 → 2pts; Murat amendment — ships with stubbed consumer-contract fixtures from 30-3, 29-2, 28-2)
**Created:** 2026-04-18 (skeleton; final spec ratified at R2 party-mode review)
**Epic:** 31 — Tri-phasic contract primitives + gates (FOUNDATION)
**Sprint key:** `31-3-registries`
**Branch:** `dev/lesson-planner`
**Points:** 2
**Depends on:** **31-1 (done — commit `15f68b1`)** — consumes `LessonPlan`, `PlanUnit`, `weather_band` Literal, `schema_version` typing conventions; imports canonical JSON utilities and pydantic idioms.
**Blocks:** **31-4** (blueprint-producer implements `ModalityProducer` ABC), **30-3** (4A loop reassessment reads modality readiness from `modality_registry`), **32-2** (coverage-manifest audit checks each emitted envelope's modality is in the registry).

---

## Mid-Flight Memo — Post-31-1 dev-guide references (READ AT T1)

31-3 is classified **single-gate** per `docs/dev-guide/story-cycle-efficiency.md` §2 (schema-shape story with clear precedent). Full R2 + G5 + G6 dual-gate ceremony is NOT required. Execute as:

```
bmad-create-story  →  single-gate R2 (lightweight, Winston + Murat only)  →  dev execution  →  single post-dev review (G6 layered pass)  →  closure
```

**Mandatory reading at T1 (before any code is written):**

- [`docs/dev-guide/pydantic-v2-schema-checklist.md`](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — 14 idioms; 31-3's two registry shapes + `ModalityProducer` ABC must adopt §1 (`ConfigDict(extra="forbid", validate_assignment=True)`), §4 (closed enums get three red-rejection surfaces — relevant for `ModalityStatus`), §8 (per-family shape pin), §9 (bidirectional parity), §11 (no-leak grep), §14 (`additionalProperties: false`).
- [`docs/dev-guide/dev-agent-anti-patterns.md`](../../docs/dev-guide/dev-agent-anti-patterns.md) — A1 silent mutation, A4 closed-enum single surface, B1 K-floor becomes ceiling-multiplier (K=8 floor for 31-3, target 10–12 tests, NOT 40+), B4 per-family shape pins, C1 treating every story as foundation-tier (31-3 is NOT; single-gate applies), E1-E3 intake/orchestrator leak.
- [`docs/dev-guide/scaffolds/schema-story/`](../../docs/dev-guide/scaffolds/schema-story/) — **USE THE SCAFFOLD.** 31-3 is the first story to exercise the scaffold-adoption contract. Pre-instantiated stubs at target paths BEFORE `bmad-dev-story` begins; dev agent extends stubs, does NOT re-derive from 31-1 precedent.
- [`docs/dev-guide/story-cycle-efficiency.md`](../../docs/dev-guide/story-cycle-efficiency.md) — §1 K-floor (1.2–1.5× K), §2 single-gate policy, §4 template-reuse, §5 T-task parallelism (batch shape-pin tests into one tool-call burst).

**Scaffold instantiation expected at T1.** Pre-instantiated stubs live at:

- `marcus/lesson_plan/registries.py` (copy of scaffold's `schema.py.tmpl`, placeholders: `{{SCHEMA_NAME}}` → `ModalityRegistryEntry` / `ComponentTypeRegistryEntry`, `{{schema_name}}` → `modality_registry_entry`, `{{MODULE_PATH}}` → `marcus.lesson_plan.registries`).
- `tests/contracts/test_modality_registry_shape_stable.py` (per-family per AC-T.1).
- `tests/contracts/test_component_type_registry_shape_stable.py` (per-family per AC-T.1).
- `tests/contracts/test_no_intake_orchestrator_leak_registries.py` (per R1 amendment 17).

---

## TL;DR

- **What:** `marcus/lesson_plan/registries.py` ships (a) `modality_registry` — the atomic-producer catalog naming what producers exist, their readiness status, and the `ModalityProducer` ABC they implement; (b) `component_type_registry` — composite-package catalog (N=2 at MVP to prove shape); (c) `ModalityProducer` abstract base class. Plus stubbed consumer-contract fixtures (Murat amendment) that 30-3, 29-2, 28-2 can import to author their consumer tests before those stories land.
- **Why:** Ruling amendment 6 moved schema work to 31-1; 31-3 now scoped to the registry runtime surface + producer ABC + consumer fixture stubs. The registry is the single-point-of-truth naming what Marcus-Orchestrator can fan out to at plan-lock. Composite-package ComponentType (N=2 at MVP) proves the abstraction without requiring all 8 modality producers to exist.
- **Done when:** `marcus/lesson_plan/registries.py` landed with both registries + ABC + `ModalityStatus` closed enum + `tests_added ≥ 8` (K-floor, target 10–12) + scaffold idioms present + single-gate R2 lightweight + `bmad-code-review` layered pass (Edge Case Hunter minimum) + `sprint-status.yaml` flipped done.

## Story

As the **Lesson Planner MVP fanout-targeting author**,
I want **the `modality_registry` + `component_type_registry` + `ModalityProducer` ABC landed as one reviewable PR with consumer-contract fixtures stubbed for 30-3 / 29-2 / 28-2**,
So that **Marcus-Orchestrator has a single authoritative naming surface for "what can we produce?" at plan-lock fanout (30-4), Irene's diagnosis (29-2) can refer to modalities by registry key, Tracy (28-2) can declare which modalities it enriches, and 31-4 has a concrete `ModalityProducer` ABC to implement**.

## Background — Why This Story Exists

Ruling amendment 6 resized 31-3 from 3 → 2 points by moving schema work (LessonPlan / PlanUnit / fit-report-v1 / weather_band) into 31-1. What remains in 31-3 is the RUNTIME REGISTRY surface: the lookup tables naming atomic producers and composite packages, the `ModalityProducer` ABC that concrete producers implement, and — per Murat amendment — stubbed consumer-contract fixtures so 30-3 / 29-2 / 28-2 can author their consumer tests against a contract surface that is frozen before those stories open.

Three binding carry-forwards from R1 rulings land in 31-3:

1. **Ruling amendment 6 — Schema in 31-1; runtime in 31-3.** No Pydantic-model proliferation in 31-3. The two registry entries ARE Pydantic models (minimal shape) but the bulk of schema work already shipped. 31-3 is thin.

2. **Murat amendment — Consumer-contract fixtures.** 31-3 ships `tests/fixtures/registries/` containing canned registry entries that 30-3, 29-2, 28-2 import in their test suites. This lets downstream stories have a frozen contract surface to test against, and keeps 31-3 from being a soft dependency that changes under downstream stories' feet.

3. **R1 ruling amendment 17 — Marcus is one voice.** The registry MUST NOT name `intake` / `orchestrator` in entry descriptions or status strings. No-leak grep test ships.

## Pre-Development Gate (lightweight — single-gate)

31-3 cannot enter `bmad-dev-story` until:

- [ ] **PDG-1.** R2 lightweight green-light: Winston + Murat sign off on the registry shapes + consumer-contract fixture list. (Full party-mode NOT required per `story-cycle-efficiency.md` §2 single-gate policy.)
- [ ] **PDG-2.** Scaffold pre-instantiated at `marcus/lesson_plan/registries.py` + 3 contract test stubs. Dev agent extends, does not re-derive.

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — `modality_registry` shape.** Exposed as module constant `MODALITY_REGISTRY: dict[str, ModalityRegistryEntry]` in `marcus/lesson_plan/registries.py`. Initial entries (per R1 plan §60):

   | Key | Producer target | Status |
   |---|---|---|
   | `slides` | slide-deck producer (existing, pre-MVP work) | `ready` |
   | `blueprint` | blueprint-producer (31-4 target) | `ready` |
   | `exercises` | exercise-producer (post-MVP) | `pending` |
   | `audio_narration` | narration producer (post-MVP) | `pending` |
   | `video` | video producer (post-MVP) | `pending` |
   | `motion_graphics` | motion producer (post-MVP) | `pending` |

   `ModalityRegistryEntry` Pydantic shape: `{modality_key: str, description: str, status: ModalityStatus, producer_class: str | None, schema_version: str}`.

2. **AC-B.2 — `component_type_registry` shape.** Exposed as module constant `COMPONENT_TYPE_REGISTRY: dict[str, ComponentTypeRegistryEntry]` in `marcus/lesson_plan/registries.py`. At MVP, N=2 entries (proves shape without requiring all composite packages):

   | Key | Composes | Status |
   |---|---|---|
   | `lecture_unit` | `[slides, blueprint]` | `ready` |
   | `practice_unit` | `[blueprint, exercises]` | `pending` (blocks on exercises producer) |

   `ComponentTypeRegistryEntry` Pydantic shape: `{component_type_key: str, description: str, composes: list[str], status: ComponentTypeStatus, schema_version: str}`. The `composes` list members MUST all be keys present in `MODALITY_REGISTRY`; validator enforces (AC-T.3).

3. **AC-B.3 — `ModalityStatus` + `ComponentTypeStatus` closed enums.** `Literal["ready", "pending", "deprecated"]`. Both registries use the same closed set. Triple red-rejection per pydantic-v2 checklist §4.

4. **AC-B.4 — `ModalityProducer` ABC.** Abstract base class in `marcus/lesson_plan/registries.py`:
   ```python
   class ModalityProducer(ABC):
       modality_key: ClassVar[str]              # must match a MODALITY_REGISTRY key

       @abstractmethod
       def produce(self, plan_unit: PlanUnit) -> ProducerOutput: ...

       @abstractmethod
       def modality_schema_version(self) -> str: ...
   ```
   Concrete producers (31-4 blueprint-producer first) inherit. Registry self-check: any producer class claiming `modality_key=X` must have an entry in `MODALITY_REGISTRY` (AC-T.5 enforces at import-time via a test).

5. **AC-B.5 — Lookup helpers.** Module-level functions: `get_modality(key: str) -> ModalityRegistryEntry` (raises `KeyError` with explicit message on miss); `get_component_type(key: str) -> ComponentTypeRegistryEntry`; `list_ready_modalities() -> list[str]` (filters `status == "ready"`); `list_ready_component_types() -> list[str]`.

6. **AC-B.6 — Consumer-contract fixtures (Murat amendment).** Ships `tests/fixtures/registries/` with:
   - `canned_modality_registry.json` — serialization of MVP registry; 30-3/29-2/28-2 import this to avoid coupling to Python module state.
   - `canned_component_type_registry.json` — same, for component types.
   - `contract_guarantees.md` — human-readable doc naming the guarantees 31-3 ships (registry shape frozen, key set frozen at MVP, status closed enum, ABC signature frozen).

7. **AC-B.7 — No producer-instantiation in 31-3.** The ABC is defined; NO concrete producer ships in 31-3. 31-4 ships the first concrete (blueprint-producer). This keeps 31-3 at 2pts and defers producer-implementation risk.

### Test (AC-T.*)

1. **AC-T.1 — Per-family shape-pin tests.** Two separate files (not batched, per R2 rider AM-1 from 31-1):
   - `tests/contracts/test_modality_registry_shape_stable.py` — pins `ModalityRegistryEntry` Pydantic shape + snapshot + allowlist + CHANGELOG gate.
   - `tests/contracts/test_component_type_registry_shape_stable.py` — pins `ComponentTypeRegistryEntry` Pydantic shape + same gates.

2. **AC-T.2 — `ModalityStatus` + `ComponentTypeStatus` triple red-rejection.** For each enum: Pydantic Literal validator rejects; JSON Schema `enum` array enumerates valid set; `TypeAdapter` round-trip rejects external invalid values. Per pydantic-v2 checklist §4.

3. **AC-T.3 — Composition validity.** `test_component_type_composes_valid_modalities.py`: every `component_type_registry` entry's `composes` list contains only keys present in `modality_registry`. Parametrized over all MVP component types.

4. **AC-T.4 — ABC contract.** `test_modality_producer_abc.py`: attempting to instantiate `ModalityProducer()` directly raises `TypeError`; subclass missing `produce()` or `modality_schema_version()` raises `TypeError` on instantiation.

5. **AC-T.5 — Producer-registry cross-check (deferred-to-31-4).** 31-3 ships the CONTRACT that 31-4 must adhere to. 31-3's test stubs this as: `test_concrete_producer_modality_key_in_registry_contract.py` contains a documented test function that 31-4 activates. Landing this stub early lets 31-4 extend it without re-authoring.

6. **AC-T.6 — Lookup helpers positive + negative.** `get_modality("slides")` returns ready entry; `get_modality("nonexistent")` raises `KeyError` with message naming the missed key; `list_ready_modalities()` returns exactly `["slides", "blueprint"]` at MVP.

7. **AC-T.7 — No-leak grep (R1 amendment 17).** `tests/contracts/test_no_intake_orchestrator_leak_registries.py`: scans all field `description=` strings + registry entry descriptions + `contract_guarantees.md` for forbidden tokens `intake` / `orchestrator`. Per R2 rider S-3 on 31-1.

8. **AC-T.8 — Consumer-contract fixture stability.** `test_canned_registry_fixtures_match_module.py`: the JSON fixtures under `tests/fixtures/registries/` deserialize to the same shape as the live `MODALITY_REGISTRY` / `COMPONENT_TYPE_REGISTRY` module constants. Prevents fixtures from drifting silently.

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Foundation at `marcus/lesson_plan/registries.py`.** New module; extends `marcus/lesson_plan/__init__.py::__all__` with `MODALITY_REGISTRY`, `COMPONENT_TYPE_REGISTRY`, `ModalityRegistryEntry`, `ComponentTypeRegistryEntry`, `ModalityStatus`, `ComponentTypeStatus`, `ModalityProducer`, `get_modality`, `get_component_type`, `list_ready_modalities`, `list_ready_component_types`.

2. **AC-C.2 — `SCHEMA_CHANGELOG.md` entry.** `## Registries v1.0 — 2026-04-MM — Story 31-3 Registries` describing the two registry shapes, the ABC signature, and the closed-enum sets.

3. **AC-C.3 — Widening MVP registry requires changelog bump.** Adding a new `MODALITY_REGISTRY` key or bumping a status is a schema-level change; requires `SCHEMA_CHANGELOG` entry. Not every config change — only registry shape/key-set changes.

## File Impact (preliminary)

| File | Change | Lines (est.) |
|------|--------|-------|
| `marcus/lesson_plan/registries.py` | **New** (from scaffold stub) — both registries + ABC + enums + lookup helpers | +180 |
| `marcus/lesson_plan/__init__.py` | **Touch** — extend `__all__` (11 new names) | +14 |
| `tests/contracts/test_modality_registry_shape_stable.py` | **New** (from scaffold stub) | +70 |
| `tests/contracts/test_component_type_registry_shape_stable.py` | **New** (from scaffold stub) | +70 |
| `tests/contracts/test_no_intake_orchestrator_leak_registries.py` | **New** (from scaffold stub) | +40 |
| `tests/test_modality_producer_abc.py` | **New** | +50 |
| `tests/test_modality_registry_composition.py` | **New** (AC-T.3) | +40 |
| `tests/test_registries_lookup_helpers.py` | **New** (AC-T.6) | +50 |
| `tests/test_canned_registry_fixtures.py` | **New** (AC-T.8) | +40 |
| `tests/fixtures/registries/canned_modality_registry.json` | **New** | +30 |
| `tests/fixtures/registries/canned_component_type_registry.json` | **New** | +15 |
| `tests/fixtures/registries/contract_guarantees.md` | **New** (Murat amendment) | +40 |
| `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` | **Touch** — Registries v1.0 entry | +20 |

## Tasks / Subtasks (preliminary)

**Serial group 1 (schema landing):**
- [ ] T1 — Lightweight R2 green-light (Winston + Murat) on registry shapes + consumer-contract fixture list.
- [ ] T2 — Scaffold stubs pre-instantiated at target paths (pre-T3 action item; handled by orchestrator, not dev agent).
- [ ] T3 — Author `registries.py`: enums (`ModalityStatus`, `ComponentTypeStatus`) → registry entry Pydantic shapes (`ModalityRegistryEntry`, `ComponentTypeRegistryEntry`) → registry constants → ABC (`ModalityProducer`) → lookup helpers.
- [ ] T4 — Extend `marcus/lesson_plan/__init__.py::__all__` with the 11 new names.

**Parallel burst 1 (independent test files — batch into one tool-call burst per §5 T-task parallelism):**
- [ ] T5 — AC-T.1 shape-pin: `test_modality_registry_shape_stable.py`.
- [ ] T6 — AC-T.1 shape-pin: `test_component_type_registry_shape_stable.py`.
- [ ] T7 — AC-T.2 triple red-rejection on both status enums.
- [ ] T8 — AC-T.3 composition validity test.
- [ ] T9 — AC-T.4 ABC contract test.
- [ ] T10 — AC-T.6 lookup helpers test.
- [ ] T11 — AC-T.7 no-leak grep test.
- [ ] T12 — AC-T.8 canned-fixture-stability test.

**Serial group 2 (fixtures + docs):**
- [ ] T13 — Generate `tests/fixtures/registries/*.json` fixtures.
- [ ] T14 — Author `contract_guarantees.md`.
- [ ] T15 — Extend `SCHEMA_CHANGELOG.md` with Registries v1.0 entry.

**Serial group 3 (closure):**
- [ ] T16 — Full regression suite + ruff clean + pre-commit green.
- [ ] T17 — Single post-dev review: `bmad-code-review` layered pass (Edge Case Hunter minimum per §2 single-gate policy).
- [ ] T18 — Close to done; unblocks 31-4 / 30-3 / 29-2 / 28-2 consumer contracts.

## Test Plan

`tests_added ≥ K` with **K = 8** (floor per `story-cycle-efficiency.md` §1). **Target: 10–12 collecting tests (1.2–1.5× K).** The scaffold-adoption pattern keeps the test count tight — most of the cycle-efficiency savings here are in not over-parametrizing.

Landing estimate: 12 tests (8 AC-T files, 4 of which have 1–2 parametrized cases). **If the count exceeds 15, the dev agent must name the coverage gap per extra ~5 tests per §1.**

Baseline before 31-3 = 31-2 closeout baseline (TBD pending 31-2 close). Expected after 31-3: **≥(31-2 baseline + 8) passed**, zero new skips / xfails / live_api / trial_critical.

## Out-of-scope

- **Concrete producer implementations.** 31-4 ships blueprint-producer. 31-3 ships the ABC only.
- **Post-MVP modalities.** `exercises`, `audio_narration`, `video`, `motion_graphics` are pending-status entries only; no producer logic.
- **Dynamic registry modification.** The registries are module constants at MVP. Runtime registration is out-of-scope.
- **Version conflict resolution between producers.** Out-of-scope. Producers that ship schema drift from the registry are a 32-2 coverage-manifest concern.
- **Cross-modality dependency graph.** `component_type_registry.composes` is a flat list; DAG resolution for composite packages is out-of-scope.

## Dependencies on Ruling Amendments

- **Ruling amendment 6** — Schema in 31-1, runtime in 31-3. AC-B.1 / AC-B.2 / AC-C.1.
- **Murat amendment — Consumer-contract fixtures.** AC-B.6 + AC-T.8. `tests/fixtures/registries/` ships frozen for 30-3 / 29-2 / 28-2.
- **R1 ruling amendment 17 — Marcus is one voice.** AC-T.7 no-leak grep test.
- **R2 rider AM-1 (carry-forward from 31-1)** — Per-family shape pins. AC-T.1 (two files, not batched).
- **Pydantic-v2 checklist §4** — Closed-enum triple red-rejection. AC-T.2.

## Risks

| Risk | Mitigation |
|------|------------|
| **Registry keys drift between MVP and post-MVP, breaking downstream fixtures** | AC-C.3: widening registry requires SCHEMA_CHANGELOG entry. AC-T.8 canned-fixture test catches silent drift. |
| **Concrete producers ship before 31-3 and drift from the ABC** | 31-3 blocks 31-4; PR ordering enforces ABC-first. `dev/lesson-planner` branch discipline. |
| **Consumer-contract fixtures go stale after 30-3/29-2/28-2 land** | 31-3's fixtures are the FROZEN contract. Downstream stories that need additional fixture shape propose a minor bump with a `SCHEMA_CHANGELOG` entry. |
| **K-floor discipline slips; story over-tests** | `story-cycle-efficiency.md` §1: target 10–12 tests. Dev agent names coverage gap if exceeding 15. G6 DISMISS rubric for parametrize-theater. |

## Dev Notes

### Architecture (thin)

- **Two registry constants + one ABC + eight functions.** That's the entire runtime surface. Resist the urge to add a `RegistryManager` class.
- **Pydantic for registry entry shapes.** Same idioms as 31-1 (`ConfigDict(extra="forbid", validate_assignment=True)`). Not every module gets a class — these two do because downstream serialization needs Pydantic-grade validation.
- **ABC is minimal.** `produce()` + `modality_schema_version()` + `modality_key: ClassVar[str]`. No additional hooks. 31-4 will push against this if it needs more; resist until concrete need surfaces.

### Anti-patterns (dev-agent WILL get these wrong)

- **Do NOT proliferate classes.** One module, two entry shapes, one ABC, two enums, registry constants, lookup helpers. No `RegistryManager`. No `ProducerRegistry`. No `ComponentTypeResolver`.
- **Do NOT batch shape-pin tests.** Per R2 rider AM-1 on 31-1: two separate files. Ruff-clean naming: `test_modality_registry_shape_stable.py` + `test_component_type_registry_shape_stable.py`.
- **Do NOT miss the TypeAdapter surface on status enums.** Pydantic Literal + JSON Schema enum + TypeAdapter. All three. Per pydantic-v2 checklist §4.
- **Do NOT instantiate concrete producers in 31-3.** Blueprint-producer is 31-4. 31-3 ships the ABC only.
- **Do NOT leak `intake` / `orchestrator` in descriptions.** Registry entry descriptions are Maya-facing (eventually). No-leak grep AC-T.7 catches.
- **Do NOT skip the canned-fixture test (AC-T.8).** The fixtures are the downstream contract. Drift between `registries.py` module state and the JSON fixtures will silently break 30-3 / 29-2 / 28-2 test suites.

### Source tree (new + touched)

```
marcus/lesson_plan/                                [EXISTS — 31-1]
├── __init__.py                                    [TOUCH +14]
├── registries.py                                  [NEW +180]  Both registries + ABC + enums + lookup helpers
├── log.py                                         [EXISTS — 31-2; unchanged]
├── schema.py                                      [EXISTS — 31-1; unchanged]
├── events.py, digest.py, event_type_registry.py   [EXISTS — 31-1; unchanged]
└── schema/                                        [EXISTS — 31-1; unchanged]

tests/contracts/
├── test_modality_registry_shape_stable.py         [NEW +70]   AC-T.1
├── test_component_type_registry_shape_stable.py   [NEW +70]   AC-T.1
└── test_no_intake_orchestrator_leak_registries.py [NEW +40]   AC-T.7

tests/
├── test_modality_producer_abc.py                  [NEW +50]   AC-T.4
├── test_modality_registry_composition.py          [NEW +40]   AC-T.3
├── test_registries_lookup_helpers.py              [NEW +50]   AC-T.6
├── test_canned_registry_fixtures.py               [NEW +40]   AC-T.8
└── (status-enum tests fold into shape-pin tests)              AC-T.2

tests/fixtures/registries/
├── canned_modality_registry.json                  [NEW +30]
├── canned_component_type_registry.json            [NEW +15]
└── contract_guarantees.md                         [NEW +40]

_bmad-output/implementation-artifacts/
└── SCHEMA_CHANGELOG.md                            [TOUCH +20]
```

### Testing standards

Per 31-1 discipline inherited via scaffold: no `live_api`, no `trial_critical`, no `xfail`, no `skip` on default suite. Schema pins use snapshot + allowlist + CHANGELOG gate. Deterministic fixtures — JSON files in `tests/fixtures/registries/`.

### References

- **Scaffold:** [`docs/dev-guide/scaffolds/schema-story/`](../../docs/dev-guide/scaffolds/schema-story/)
- **Pydantic-v2 checklist:** [`docs/dev-guide/pydantic-v2-schema-checklist.md`](../../docs/dev-guide/pydantic-v2-schema-checklist.md)
- **Anti-patterns:** [`docs/dev-guide/dev-agent-anti-patterns.md`](../../docs/dev-guide/dev-agent-anti-patterns.md)
- **Cycle efficiency:** [`docs/dev-guide/story-cycle-efficiency.md`](../../docs/dev-guide/story-cycle-efficiency.md)
- **Pattern source:** [`31-1-lesson-plan-schema.md`](./31-1-lesson-plan-schema.md) — governance closure template
- **Plan doc:** [`../planning-artifacts/lesson-planner-mvp-plan.md`](../planning-artifacts/lesson-planner-mvp-plan.md) §Epic 31, ruling amendment 6, Murat consumer-contract fixtures amendment

### Non-goals

- No concrete producer implementations (31-4+).
- No runtime registry mutation.
- No cross-version conflict resolution.
- No multi-level composite packaging (composes is flat).

## Governance Closure Gates (per CLAUDE.md — single-gate variant)

31-3 closes `done` only when ALL below satisfied:

- [ ] **G1. R2 lightweight green-light** (Winston + Murat; full party-mode NOT required per `story-cycle-efficiency.md` §2).
- [ ] **G2. Scaffold stubs pre-instantiated** at target paths before `bmad-dev-story` starts.
- [ ] **G3. `bmad-dev-story` execution** with all T1–T18 subtasks checked.
- [ ] **G4. `tests_added ≥ 8`** collecting (K-floor). Target 10–12.
- [ ] **G5. Ruff clean + pre-commit green + co-commit test+impl discipline.**
- [ ] **G6. `bmad-code-review` layered pass** — at minimum Edge Case Hunter (single-gate policy; full 3-layer optional).
- [ ] **G7. `sprint-status.yaml` flipped** `ready-for-dev → in-progress → review → done`.
- [ ] **G8. Consumer-contract fixtures committed** under `tests/fixtures/registries/`; downstream stories (30-3, 29-2, 28-2) unblocked.

## Dev Agent Record

**Executed by:** pending.
**Date:** pending.

_[Populated during `bmad-dev-story` execution.]_

## Review Record

### Post-dev review — PENDING

_[Single-gate policy per `story-cycle-efficiency.md` §2: one post-dev review pass (Edge Case Hunter minimum). Triage into APPLY / DEFER / DISMISS._]_

## R1 + R2 Orchestrator Ruling Traceability

| Ruling | Source | Applied in 31-3 |
|---|---|---|
| **R1 amendment 6** — Schema in 31-1; runtime in 31-3 | Plan doc §Orchestrator Ruling Record item 6 | AC-B.1 / AC-B.2 / AC-C.1; entire story scope |
| **Murat amendment — Consumer-contract fixtures** | Plan doc §Epic 31 31-3 row | AC-B.6 + AC-T.8; `tests/fixtures/registries/` ships frozen |
| **R1 amendment 17** — Marcus is one voice | Plan doc §Orchestrator Ruling Record item 17 | AC-T.7 no-leak grep |
| **R2 rider AM-1 carry-forward** — Per-family shape pins | 31-1 R2 Review Record | AC-T.1 two separate files |
| **Pydantic-v2 checklist §4** — Closed-enum triple red-rejection | `docs/dev-guide/pydantic-v2-schema-checklist.md` | AC-T.2 |
| **Story-cycle-efficiency §1** — K-floor discipline | `docs/dev-guide/story-cycle-efficiency.md` | K=8 floor; target 10–12; >15 requires coverage-gap justification |
| **Story-cycle-efficiency §2** — Single-gate policy | `docs/dev-guide/story-cycle-efficiency.md` | 31-3 is single-gate; G5 party-mode NOT required |
| **Story-cycle-efficiency §4** — Template reuse | `docs/dev-guide/story-cycle-efficiency.md` | Scaffold pre-instantiated at T2 |
