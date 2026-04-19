# Story 31-1: Lesson Plan Schema — Foundation Primitives + ScopeDecision State Machine + fit-report-v1 + dials-spec

**Status:** done (BMAD-CLOSED 2026-04-18; party-mode 2026-04-19 follow-on consensus added construction-time invariants for Edge#5 + Edge#6, Auditor Coverage #12 by_alias=True audit-path test, deleted Edge#7 dead validator, exported `EVENT_PRE_PACKET_SNAPSHOT` constants closing 30-1 G6-D2 cross-story slip, and consolidated `_OPEN_ID_REGEX` to single source of truth in `event_type_registry.py`.)
**Created:** 2026-04-18 (authored by Amelia post-R1 orchestrator ruling; R2 green-light 2026-04-18 with 11 riders applied; dev-story executing T2–T24 in-session)
**Epic:** 31 — Tri-phasic contract primitives + gates (FOUNDATION)
**Sprint key:** `31-1-lesson-plan-schema`
**Branch:** `dev/lesson-planner`
**Points:** 5 (bumped 3→5 per R1 orchestrator ruling amendment 5, absorbing six additional in-scope items + one companion artifact)
**Depends on:** none (foundation — nothing upstream).
**Blocks:** **31-2 (log)**, **31-3 (registries)**, **29-1 (fit-report-v1 validator + serializer)**, **30-1 (marcus duality split)**, **30-2b (pre-packet envelope emission)**, and transitively all of Epic 28 / 29 / 30 / 32.

## TL;DR

- **What:** The `marcus/lesson_plan/` foundation package — Pydantic models + JSON Schema + validators for `lesson_plan`, `plan_unit`, `dials`, `gaps[]`, **revision/digest**, **`fit-report-v1` artifact class**, **`ScopeDecision` value-object + state machine** (proposed → ratified → locked), **`scope_decision_transition` temporal-audit event primitive**, **`weather_band` first-class field** (gold | green | amber | gray — no red), **`no-red` validator constraint**, **`event_type` open-string validator** (Gagné seam). Companion artifact: **`dials-spec.md`** documenting dial semantics (ranges, interactions, operator-facing wording).
- **Why:** The entire Lesson Planner MVP is a **bilateral typed contract** (Quinn's tri-phasic framing). Every downstream story — log (31-2), registries (31-3), Marcus duality split (30-1), pre-packet emission (30-2b), 4A loop (30-3a/b), plan-lock fanout (30-4), blueprint producer (31-4), Quinn-R two-branch (31-5), envelope audit (32-2), trial-run smoke (32-3) — reads and writes artifacts shaped by this schema. Authoring the schema as one reviewable PR before any consumer exists prevents "first-consumer shapes the contract poorly" failure mode (Amelia + Murat principle from 27-0).
- **Absorption rationale (ruling amendment 5):** The seven items absorbed into 31-1 are ALL schema-shaped and ALL cross-referenced by ≥3 downstream stories. Splitting them would force re-reviewing the same shape under multiple story headings. Bumped 3→5pts; 31-3 resized 3→2 to balance epic-level totals.
- **Done when:** schema shipped + `dials-spec.md` companion shipped + validators (incl. no-red, ScopeDecision state-machine transitions, weather_band enum, event_type open-string, digest-determinism, locked-without-maya bypass guard, two-level actor surface, user-facing-string grep) all green + `tests_added ≥ 25` + party-mode R2 green-light + `bmad-code-review` layered pass + sprint-status.yaml flipped `ready-for-dev → in-progress → review → done`.
- **W-1 generic event envelope shape + reserved `pre_packet_snapshot` registry entry; AC-T.14 no-leak grep; AC-T.15 two-level actor serialization safety.**

## Story

As the **Lesson Planner MVP foundation author**,
I want **the `lesson_plan` schema + `ScopeDecision` state machine + `fit-report-v1` artifact class + `dials-spec.md` companion landed as one reviewable PR before any consumer ships**,
So that **every downstream story (log, registries, Marcus duality, 4A loop, plan-lock fanout, Quinn-R two-branch, envelope audit, trial-run harness) reads and writes artifacts against a stable, tested, human-reviewed contract** — eliminating schema drift during feature development and preserving Quinn's tri-phasic contract discipline.

## Background — Why This Story Exists

The Lesson Planner MVP plan (`_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md`) locked the tri-phasic contract framing across four party-mode rounds. The R1 plan-review ruling (2026-04-18 orchestrator adjudication, amendment 5) consolidated six additional schema-shaped items into this story — items originally scattered across 29-1, 30-1, 30-3a, and "implicit in 31-2" — on the principle that **one schema PR is cleaner than six**.

The seven absorption items (per ruling amendment 5):

1. `lesson_plan` dataclass + JSON schema (original 31-1 scope).
2. `plan_unit` + `dials` + `gaps[]` + `revision`/`digest` (original 31-1 scope).
3. **`fit-report-v1` artifact class schema** (was 29-1 — Irene's diagnostic output).
4. **`ScopeDecision` value-object + state machine** with transitions `proposed → ratified → locked` and who-can-transition rules (Winston).
5. **`scope_decision_transition` event primitive** for when/why a ScopeDecision flipped; temporal-audit primitive (Quinn).
6. **`weather_band` as first-class field on `plan_unit`** — enum `gold | green | amber | gray`; no red (Sally UX primitive).
7. **`no-red` policy as schema validator constraint** (Sally — Maya didn't fail; source is what it is).
8. **`event_type` as open string with validator**, not closed enum (Quinn — Gagné seam for future learning models).
9. **Companion artifact `dials-spec.md`** — dial semantics, ranges, interactions, operator-facing wording (Quinn hedge for deferred UI polish).

(Amendment 5 enumerates these as "seven items" — items 8 (`event_type` validator) and 9 (`dials-spec.md`) are counted alongside; spec captures all nine touchpoints.)

## Acceptance Criteria

### Behavioral / Schema (AC-B.*)

1. **AC-B.1 — `lesson_plan` root shape.** Pydantic model + JSON Schema at `marcus/lesson_plan/schema.py` and `marcus/lesson_plan/schema/lesson_plan.v1.schema.json`:
   ```yaml
   learning_model: {id: str, version: int}     # hardcoded "gagne-9" / 1 at MVP; seam for future models
   structure: dict                              # opaque-to-platform; free-shape per learning model
   plan_units: list[PlanUnit]
   revision: int                                # monotonic
   updated_at: datetime                         # ISO 8601 UTC
   digest: str                                  # sha256 of canonical JSON serialization
   ```
   Serialization is **canonical-JSON** (sorted keys, no trailing whitespace, `ensure_ascii=True`) so `digest` is deterministic.

2. **AC-B.2 — `PlanUnit` shape.** Each plan_unit carries:
   ```yaml
   unit_id: str                                 # e.g. "gagne-event-3" (open string per AC-B.8)
   event_type: str                              # open string; validated via AC-B.8 registry
   source_fitness_diagnosis: str                # Irene's commentary; required
   scope_decision: ScopeDecision                # value-object (AC-B.4)
   weather_band: Literal["gold", "green", "amber", "gray"]  # AC-B.6; NEVER red (AC-B.7 validator)
   modality_ref: str | None                     # "slides" | "leader-guide" | ... | "blueprint"; null unless delegated
   rationale: str                               # free text, stored verbatim, surfaced verbatim (ruling amendment 16)
   gaps: list[IdentifiedGap]                    # only non-empty when scope_decision.state == in-scope
   dials: Dials | None                          # only valid when scope_decision.state in {in-scope, delegated}
   ```

3. **AC-B.3 — `Dials`, `IdentifiedGap`, dial semantics.** `Dials` model: `{enrichment: float | None, corroboration: float | None}`; both 0.0–1.0 inclusive. `IdentifiedGap`: `{gap_id: str, description: str, suggested_posture: Literal["embellish", "corroborate", "gap_fill"]}`. Unit tests cover boundary values (0.0, 1.0, out-of-range rejection).

4. **AC-B.4 — `ScopeDecision` value-object + state machine (Winston, R2 S-4 two-level actor surface).** `ScopeDecision` is a Pydantic model with a **public** (Maya-facing) surface and a **private** (audit-only) surface:
   ```yaml
   state: Literal["proposed", "ratified", "locked"]
   scope: Literal["in-scope", "out-of-scope", "delegated", "blueprint"]
   proposed_by: Literal["system", "operator"]                      # PUBLIC — Maya-facing serialization
   _internal_proposed_by: Literal[                                  # PRIVATE — audit-only (Field(exclude=True))
       "marcus", "marcus-intake", "marcus-orchestrator", "irene", "maya"
   ]
   ratified_by: Literal["maya"] | None                             # Maya is SOLE signatory (Quinn attestor/signatory split)
   locked_at: datetime | None                                       # set only when state == locked
   ```
   `_internal_proposed_by` uses `Field(exclude=True)` so it DOES NOT appear in default `model_dump()` / `model_dump_json()` output (S-4 anti-leak discipline). Private-audit tooling may opt in via `model_dump(by_alias=True)` or equivalent; Maya-facing payloads never carry it.
   **Transitions:** `proposed → ratified` requires `ratified_by == "maya"` (Maya-sole-signatory invariant). `ratified → locked` requires plan-lock trigger (30-3a); cannot be reversed. `proposed → proposed` permitted (re-proposal with different scope). `locked → *` forbidden (terminal). Validator rejects any other transition with explicit error message identifying the forbidden transition.

5. **AC-B.5 — `scope_decision_transition` event primitive (Quinn — temporal audit; R2 S-4 two-level actor surface).** Separate event model at `marcus/lesson_plan/events.py`, envelope-wrapped per AC-B.5a:
   ```yaml
   event_type: Literal["scope_decision_transition"]
   unit_id: str
   plan_revision: int                              # plan revision AT transition
   from_state: Literal["proposed", "ratified"]     # never "locked" (terminal)
   to_state: Literal["proposed", "ratified", "locked"]
   from_scope: Literal["in-scope", "out-of-scope", "delegated", "blueprint"] | None
   to_scope: Literal["in-scope", "out-of-scope", "delegated", "blueprint"]
   actor: Literal["system", "operator"]            # PUBLIC — Maya-facing serialization
   _internal_actor: Literal[                       # PRIVATE — audit-only (Field(exclude=True))
       "marcus", "marcus-intake", "marcus-orchestrator", "irene", "maya"
   ]
   timestamp: datetime
   rationale_snapshot: str                         # verbatim rationale at transition time (may differ from current)
   ```
   `_internal_actor` uses `Field(exclude=True)` so default serialization keeps the Maya-facing surface clean. Helper `to_internal_actor(actor, hint)` maps `system → marcus-* | irene` via `actor_hint`, and `operator → maya`. Mapping documented in `events.py` docstring.
   This is emitted (not just stored) — log write-path lives in 31-2, but the **shape** is pinned here.

5a. **AC-B.5a — Generic event envelope (R2 W-1).** ALL events in 31-2's append-only log MUST conform to the generic envelope:
   ```yaml
   event_id: str          # uuid4
   timestamp: datetime    # UTC
   plan_revision: int     # monotonic
   event_type: str        # open string; validated via registry (AC-B.8 semantics)
   payload: dict          # event-type-specific body (e.g. the scope_decision_transition shape above)
   ```
   31-1 ships the envelope Pydantic model (`EventEnvelope`) in `events.py` and the shape-pin test (AC-T.4a). 31-2 emits. Future event types (`pre_packet_snapshot`, `plan_unit.created`, `plan.locked`, `fanout.envelope.emitted`, `scope_decision.set`) inherit this envelope. Pre-registration of `pre_packet_snapshot` lives in `event_type_registry.py` RESERVED list (see AC-B.8); 31-1 does NOT emit it (single-writer rule — R1 ruling amendment 13).

6. **AC-B.6 — `weather_band` first-class field (Sally; R2 S-1 abundance framing).** Enum on `PlanUnit`. Semantics documented in `dials-spec.md` with abundance phrasing (never "insufficient," never "failed," never deficit framing): gold = "you've got this cold" — source strongly supports event (auto-in-scope default); green = "we're in step" — source supports with light enrichment; amber = "your call" — partial support, operator judgment needed; gray = "Marcus leans in more" — Marcus proposes additional support (delegation or blueprint) for this unit. Field docstring in `schema.py` mirrors the abundance phrasing per S-1 rider.

7. **AC-B.7 — `no-red` validator constraint (Sally).** Pydantic validator on `PlanUnit.weather_band` rejects the string `"red"` with explicit error message: `"weather_band 'red' is forbidden; Maya did not fail — source is what it is (see lesson-planner-mvp-plan.md §Sally's UX Primitives)"`. Covers (a) raw dict inputs, (b) JSON deserialization, (c) direct model instantiation. Schema-level: `weather_band` enum in JSON Schema explicitly enumerates the four allowed values and rejects any other.

8. **AC-B.8 — `event_type` open-string validator (Quinn Gagné seam; R2 W-1 reserved-event registration).** `unit_id` and `event_type` accept any non-empty string matching regex `^[a-z0-9._-]+$` (permits `.` for dotted event names like `plan.locked`). A **registry** at `marcus/lesson_plan/event_type_registry.py` ships with: (a) the nine Gagné event type labels (`gagne-event-1` through `gagne-event-9`) as KNOWN plan-unit event-type labels; (b) a RESERVED set of log event_types pre-registered for 31-2 emission — `pre_packet_snapshot`, `plan_unit.created`, `scope_decision.set`, `scope_decision_transition`, `plan.locked`, `fanout.envelope.emitted`. 31-1 registers these as reserved but does NOT emit them. Comment on `pre_packet_snapshot`: "Reserved for 31-2 pre_packet_snapshot emission per R1 ruling amendment 13 (single-writer rule)." Validator WARNS (does not reject) on event_types not in the known-or-reserved registry, logging `"event_type '{value}' not in known registry; permitted for Gagné-seam extensibility"`. Future learning-model additions (second story outside MVP) extend the registry without schema churn.

9. **AC-B.9 — `fit-report-v1` artifact class schema (absorbed from 29-1).** Separate Pydantic model + JSON Schema at `marcus/lesson_plan/schema/fit_report.v1.schema.json`:
   ```yaml
   source_ref: str                                  # pointer to SME input fixture
   plan_ref: {lesson_plan_revision: int, lesson_plan_digest: str}
   diagnoses: list[FitDiagnosis]
   generated_at: datetime
   irene_budget_ms: int                             # observed diagnostic latency; for p95 tracking per §6-E2
   ```
   `FitDiagnosis` shape:
   ```yaml
   unit_id: str
   fitness: Literal["sufficient", "partial", "absent"]
   commentary: str
   recommended_scope_decision: Literal["in-scope", "out-of-scope", "delegated", "blueprint"] | None
   recommended_weather_band: Literal["gold", "green", "amber", "gray"] | None
   ```
   **29-1 implements the validator + serializer + emission wiring** atop this schema — 31-1 ships the shape only.

10. **AC-B.10 — `digest` determinism.** `lesson_plan.digest` is sha256 of `json.dumps(plan.model_dump(), sort_keys=True, ensure_ascii=True, separators=(",", ":"))`. Helper `compute_digest(plan: LessonPlan) -> str` in `marcus/lesson_plan/digest.py`. Test: same plan instance → same digest across 100 invocations (AC-T.7). Helper `assert_digest_matches(plan)` validates the stored `digest` against a recompute.

### Test (AC-T.*)

1. **AC-T.1 — Schema-pin contract tests (R2 AM-1 three-file split).** Split into three shape-family pin files, each with its own SCHEMA_CHANGELOG entry gate:
   - `tests/contracts/test_lesson_plan_shape_stable.py` → pins `LessonPlan` + `PlanUnit` + `Dials` + `IdentifiedGap`
   - `tests/contracts/test_fit_shape_stable.py` → pins `FitReport` + `FitDiagnosis`
   - `tests/contracts/test_scope_shape_stable.py` → pins `ScopeDecision` + `ScopeDecisionTransition` + `EventEnvelope`
   Any change to these shapes without explicit migration → test fails. Same snapshot + allowlist + CHANGELOG gate pattern as 27-0 AC-T.1 (Murat mandatory). Per AM-1, one SCHEMA_CHANGELOG entry PER shape-family (`Lesson Plan v1.0`, `Fit Report v1.0`, `Scope Decision v1.0`), not one mega-entry. [Inherits: **Ruling amendment 5**, R2 rider **AM-1**]

2. **AC-T.2 — JSON-schema ↔ dataclass parity test.** `tests/contracts/test_lesson_plan_json_schema_parity.py` validates that (a) every field in the Pydantic model appears in the JSON Schema with matching type, (b) every JSON Schema enum matches the Literal set in the Pydantic model, (c) a `model.model_dump()` round-trip through the JSON Schema validator passes, (d) **AC-T.2.d (R2 AM-2): required-vs-optional bidirectional parity** — every Pydantic field declared without a default (or with the `...` marker) MUST appear in the JSON Schema `"required"` array; every Pydantic field with a default (including `Optional` / `None`-default) MUST NOT appear in `"required"`. Failure → explicit error naming the drift field.

3. **AC-T.3 — ScopeDecision state-machine transition tests (R2 S-4 two-level actor matrix).** `tests/test_scope_decision_transitions.py` enumerates every legal and illegal transition in a parametrized test matrix that exercises BOTH the public `proposed_by: Literal["system", "operator"]` surface AND the private `_internal_proposed_by: Literal["marcus", "marcus-intake", "marcus-orchestrator", "irene", "maya"]` audit surface:
   - Legal: `proposed(system/marcus) → proposed(operator/maya)`, `proposed(operator/maya) → ratified(ratified_by=maya)`, `ratified → locked (via plan-lock trigger)`, `proposed → proposed (re-propose with different scope)`.
   - Illegal: `proposed → ratified (ratified_by != maya)`, `ratified → proposed (no revert)`, `locked → *` (terminal), any direct `proposed → locked` skipping ratified, and the Q-5 bypass: direct construction of `state="locked", ratified_by=None`.
   - Each illegal transition asserts explicit error message naming the forbidden pair. Every legal pair also asserts the `_internal_proposed_by` mapping is preserved internally.
   - Dedicated Q-5 test `test_scope_decision_locked_without_maya_rejected` (within the same state-machine test module) covers: (a) `state="locked", ratified_by="maya"` valid; (b) `state="locked", ratified_by=None` rejected via `model_validator(mode="after")` with Q-5 error message; (c) `state="locked", ratified_by="marcus"` rejected at the `Literal["maya"] | None` type layer; (d) direct field mutation `sd.state = "locked"` (bypassing `transition_to()`) also rejected via re-validation. [Ruling amendment 5 — Winston; R2 riders S-4 + Q-5]

4. **AC-T.4 — `scope_decision_transition` event-shape test.** `tests/contracts/test_scope_decision_transition_event.py` validates the event primitive: required fields present, `from_state` never `"locked"`, `to_state` valid, `rationale_snapshot` is verbatim free-text (tests with multi-line / unicode / embedded quotes / whitespace — ruling amendment 16 surface). Exercises the two-level actor model (S-4): public `actor` Literal `["system", "operator"]`; `_internal_actor` Literal `["marcus", "marcus-intake", "marcus-orchestrator", "irene", "maya"]`; `to_internal_actor()` mapping asserted. [Ruling amendment 5 — Quinn; R2 rider S-4]

4a. **AC-T.4a — Event envelope shape-pin test (R2 W-1).** `tests/contracts/test_event_envelope_shape_stable.py` pins the generic `EventEnvelope` fields `{event_id, timestamp, plan_revision, event_type, payload}` via the snapshot + allowlist + CHANGELOG gate pattern. Any future event type (`pre_packet_snapshot`, `plan_unit.created`, etc.) MUST conform to this envelope — this test is the contract that 31-2 and all downstream emitters inherit.

5. **AC-T.5 — `weather_band` enum + no-red validator tests.** `tests/test_weather_band_validator.py` — four tests:
   - Each of `gold | green | amber | gray` accepted on construction and round-trip.
   - `red` rejected with explicit error message on direct construction.
   - `red` rejected on JSON deserialization (via Pydantic `model_validate`).
   - `red` rejected in JSON Schema validation path. [Ruling amendment 5 — Sally]

6. **AC-T.6 — `event_type` open-string validator tests.** `tests/test_event_type_validator.py`:
   - All nine `gagne-event-{1..9}` accepted silently (no warning log).
   - Unknown event_type `"custom-event-42"` accepted with WARNING log asserting the registered warning message.
   - Invalid regex `"Gagne Event 1"` (spaces / caps) rejected with explicit error.
   - Empty string rejected. [Ruling amendment 5 — Quinn Gagné seam]

7. **AC-T.7 — Digest determinism test (R2 AM-3 tamper-swap).** `tests/test_digest_determinism.py`:
   - Same `LessonPlan` instance → same digest across 100 computations.
   - Semantically-equivalent plans with different key-insertion-order → same digest (canonical-JSON proof).
   - Mutating any field → digest changes (sensitivity proof).
   - **Nested-list-order sensitivity (R2 AM-3)**: `PlanUnit.gaps = [a, b, c]` digests DIFFER from `PlanUnit.gaps = [a, c, b]` — list order is semantic on this field.
   - **None-vs-missing-field contract (R2 AM-3)**: a plan where `scope_decision=None` must digest IDENTICALLY to a plan where `scope_decision` is absent. Chosen behavior documented in `digest.py` docstring.
   - Tamper sub-assertion REMOVED per AM-3 (tautological w/ mutation sensitivity).

8. **AC-T.8 — `dials-spec.md` companion existence + substance test (R2 Q-3).** `tests/contracts/test_dials_spec_companion_exists.py` asserts `marcus/lesson_plan/dials-spec.md` exists, is non-empty, contains the four required sections: `## Dial: enrichment`, `## Dial: corroboration`, `## Interactions`, `## Operator-facing wording`. **Q-3 substance upgrade**: for EACH of the four sections, parse the section body and assert:
   - ≥1 default-value statement matching regex `/default[:\s]+[^\n]+/i` within the section body.
   - ≥1 interaction example matching regex `/example|e\.g\./i` within the section body.
   Mirrors 27-0's `test_retrieval_contract_doc_exists.py` pattern. [Ruling amendment 5 — Quinn; R2 rider Q-3]

9. **AC-T.9 — fit-report-v1 schema pin.** `tests/contracts/test_fit_report_v1_schema_stable.py` pins the fit-report shape from day one. [Ruling amendment 5 — absorbed from 29-1]

10. **AC-T.10 — Plan-revision monotonicity test.** `tests/test_plan_revision_monotonicity.py`: `revision` field only increases; mutating a plan with stale revision number raises `StaleRevisionError`.

11. **AC-T.11 — Rationale verbatim round-trip test (R2 S-2 + M-extra parametrize expansion).** `tests/test_rationale_verbatim_roundtrip.py` (ruling amendment 16 surface): construct `PlanUnit` with a parametrized matrix of rationale payloads; serialize → JSON → deserialize; assert byte-identical string preservation. No parsing, no coercion, no enum collapse, no trim. Parametrize MUST include:
   - Multi-line (`\n`) rationale with unicode + embedded quotes.
   - `\r\n` CRLF newlines (M-extra).
   - `\t` tab characters (M-extra).
   - Emoji (e.g. `"revisit 🔬"`) (M-extra).
   - Empty string `""` (S-2 — `rationale: str` accepts empty; no `min_length`).
   - Single character `"R"` (S-2).
   - Single word `"revisit"` (S-2).
   - Leading + trailing whitespace `"  revisit  "` (S-2 — preserved verbatim, no trim).

12. **AC-T.12 — Scope-state ↔ dials/gaps consistency validator.** `tests/test_scope_dials_gaps_consistency.py`:
    - `scope == in-scope` AND `gaps not empty` → valid.
    - `scope != in-scope` AND `gaps not empty` → validator error ("gaps only valid on in-scope units").
    - `scope in {in-scope, delegated}` AND `dials set` → valid.
    - `scope in {out-of-scope, blueprint}` AND `dials set` → validator error ("dials only valid on in|delegated units").

13. **AC-T.13 — Suite-level gate (non-collecting AC).** Baseline from 27-2 closeout: 1149 passed / 2 skipped / 0 failed / 2 xfailed. Expected after 31-1: **+25 collecting tests minimum** (floor per §6-E4, bumped 22→25 per R2 riders AM-1 / S-3 / S-4 net-new mandatory). No xfail, no new skips, no new `live_api`, no new `trial_critical`.

14. **AC-T.14 — No user-facing `intake` / `orchestrator` leak grep test (R2 S-3, NON-NEGOTIABLE).** `tests/contracts/test_no_intake_orchestrator_in_user_facing_strings.py` scans ALL Python source files under `marcus/lesson_plan/` + all JSON Schema files + `dials-spec.md` and asserts NO match of regex `r"(?i)\b(intake|orchestrator)\b"` in USER-FACING STRING VALUES. User-facing surfaces include: Pydantic `Field(description=...)`, Pydantic validator error messages, Literal enum values, JSON Schema `"description"` / `"title"` / `"errorMessage"`, and `dials-spec.md` prose. Internal field names, class names, import paths (e.g. module names like `marcus-intake`) are exempt. Failure → explicit error naming file + line + offending string. Blocking at merge (R1 ruling amendment 17 enforcement).

15. **AC-T.15 — Two-level actor serialization safety (R2 S-4).** `tests/test_actor_fields_maya_serialization_safe.py` asserts that `model_dump()` and `model_dump_json()` on `ScopeDecision` and `ScopeDecisionTransition` NEVER produce the strings `marcus`, `marcus-intake`, `marcus-orchestrator`, `irene` as VALUES (actor-field output is only `system` or `operator`). Asserts that `model_dump(by_alias=True)` with appropriate `exclude` override CAN include the internal fields when the private-audit surface is explicitly requested. Anti-leak discipline for the Maya-facing payload contract.

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Foundation lives at `marcus/lesson_plan/`.** New package. Files: `__init__.py`, `schema.py` (Pydantic models), `events.py` (`ScopeDecisionTransition`), `digest.py` (canonical serialization + sha256), `event_type_registry.py` (Gagné labels + extensibility helpers), `schema/lesson_plan.v1.schema.json`, `schema/fit_report.v1.schema.json`, `dials-spec.md` (companion artifact).

2. **AC-C.2 — Schema version field present.** Every emitted `lesson_plan` artifact MUST carry `schema_version: "1.0"` at the root level. Pydantic model sets a default `ClassVar` + serializer hook. `tests/contracts/test_lesson_plan_schema_version_field_present.py` asserts presence (pattern inherited from 27-0 AC-T).

3. **AC-C.3 — `SCHEMA_CHANGELOG.md` updated.** Extend `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` with a new `## Lesson Plan Schema v1.0 (2026-04-18)` entry under the existing `Texas retrieval` entry. Documents: absorbed items from 29-1 (fit-report-v1), ScopeDecision state machine, weather_band / no-red, event_type open-string, dials-spec companion. Reinforces lockstep with Winston schema-change policy (§6-D1).

4. **AC-C.4 — `digest` is canonical-JSON sha256.** No alternative hash. No format drift. Hard-pinned by AC-T.7.

5. **AC-C.5 — Maya is SOLE signatory.** `ScopeDecision.ratified_by` type is `Literal["maya"] | None`. No alternative actors. Enforces Quinn tri-phasic attestor/signatory split at the type level.

6. **AC-C.6 — `rationale` is free_text verbatim (ruling amendment 16).** `PlanUnit.rationale` is `str`; no custom parser; serialized/deserialized as-is. Comment on the field attribute references ruling amendment 16 explicitly so future maintainers don't "helpfully" add enum coercion.

7. **AC-C.7 — No write-path code in 31-1.** 31-1 ships shape, validators, digest helpers, and companion doc ONLY. Log write-path (append-only JSONL, `plan_unit.created` event emission, single-writer enforcement) lives in 31-2. Registries live in 31-3. Downstream consumers explicitly out of scope (see §Out-of-scope).

8. **AC-C.8 — ScopeDecision locked-without-Maya bypass guard (R2 Q-5).** `ScopeDecision` carries a Pydantic `model_validator(mode="after")` that rejects any construction where `state == "locked"` AND `ratified_by != "maya"`. Explicit error message: `"ScopeDecision locked state requires ratified_by='maya' (tri-phasic contract: Maya is sole signatory; see R1 ruling amendment 5)"`. Covers direct construction, JSON deserialization, and post-construction field mutation (mutation re-validates and rejects the bypass). Paired with the type-level `ratified_by: Literal["maya"] | None` constraint — the type layer prevents non-Maya actor strings; the validator layer prevents `None`-in-locked-state bypass.

## File Impact (preliminary — refined at bmad-dev-story)

| File | Change | Lines (est.) |
|------|--------|-------|
| `marcus/lesson_plan/__init__.py` | **New** package marker + public surface exports | +20 |
| `marcus/lesson_plan/schema.py` | **New** — Pydantic models: `LessonPlan`, `PlanUnit`, `Dials`, `IdentifiedGap`, `ScopeDecision`, `FitReport`, `FitDiagnosis` | +280 |
| `marcus/lesson_plan/events.py` | **New** — `ScopeDecisionTransition` event primitive | +70 |
| `marcus/lesson_plan/digest.py` | **New** — canonical-JSON helpers + sha256 + `assert_digest_matches` | +60 |
| `marcus/lesson_plan/event_type_registry.py` | **New** — Gagné label registry + extensibility helpers | +50 |
| `marcus/lesson_plan/schema/lesson_plan.v1.schema.json` | **New** — JSON Schema for lesson_plan root | +180 |
| `marcus/lesson_plan/schema/fit_report.v1.schema.json` | **New** — JSON Schema for fit-report-v1 | +90 |
| `marcus/lesson_plan/dials-spec.md` | **New** companion artifact (ruling amendment 5 — Quinn hedge) | +120 |
| `tests/contracts/test_lesson_plan_shape_stable.py` | **New** — AC-T.1 LessonPlan/PlanUnit/Dials/IdentifiedGap pin (R2 AM-1) | +90 |
| `tests/contracts/test_fit_shape_stable.py` | **New** — AC-T.1 FitReport/FitDiagnosis pin (R2 AM-1) | +60 |
| `tests/contracts/test_scope_shape_stable.py` | **New** — AC-T.1 ScopeDecision/ScopeDecisionTransition/EventEnvelope pin (R2 AM-1) | +70 |
| `tests/contracts/test_event_envelope_shape_stable.py` | **New** — AC-T.4a generic envelope shape-pin (R2 W-1) | +40 |
| `tests/contracts/test_fit_report_v1_schema_stable.py` | **New** — AC-T.9 fit-report JSON Schema pin | +60 |
| `tests/contracts/test_lesson_plan_json_schema_parity.py` | **New** — AC-T.2 + AC-T.2.d required-optional parity (R2 AM-2) | +110 |
| `tests/contracts/test_scope_decision_transition_event.py` | **New** — AC-T.4 | +70 |
| `tests/contracts/test_dials_spec_companion_exists.py` | **New** — AC-T.8 + Q-3 substance assertions (R2 Q-3) | +60 |
| `tests/contracts/test_lesson_plan_schema_version_field_present.py` | **New** — AC-C.2 | +25 |
| `tests/contracts/test_no_intake_orchestrator_in_user_facing_strings.py` | **New** — AC-T.14 no-leak grep (R2 S-3) | +80 |
| `tests/test_scope_decision_transitions.py` | **New** — AC-T.3 parametrized state-machine + Q-5 bypass guard | +220 |
| `tests/test_actor_fields_maya_serialization_safe.py` | **New** — AC-T.15 two-level actor serialization safety (R2 S-4) | +70 |
| `tests/test_weather_band_validator.py` | **New** — AC-T.5 | +60 |
| `tests/test_event_type_validator.py` | **New** — AC-T.6 | +70 |
| `tests/test_digest_determinism.py` | **New** — AC-T.7 (with AM-3 nested-list-order + None-vs-missing) | +110 |
| `tests/test_plan_revision_monotonicity.py` | **New** — AC-T.10 | +50 |
| `tests/test_rationale_verbatim_roundtrip.py` | **New** — AC-T.11 (R2 S-2 + M-extra expanded parametrize) | +90 |
| `tests/test_scope_dials_gaps_consistency.py` | **New** — AC-T.12 | +80 |
| `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` | **Touch** — Lesson Plan Schema v1.0 entry | +40 |
| `pyproject.toml` | **Touch** — add `marcus` package to pythonpath if not already surfaced | +1 |

## Tasks / Subtasks (preliminary — refined at bmad-dev-story)

- [x] T1 — Resolve R2 party-mode green-light on this spec. **(2026-04-18 — 0 RED / 4 YELLOW; 11 riders applied.)**
- [x] T2 — Author `LessonPlan` + `PlanUnit` + `Dials` + `IdentifiedGap` in `schema.py`.
- [x] T3 — Author `ScopeDecision` value-object + state machine with transition validator + Q-5 bypass guard.
- [x] T4 — Author `ScopeDecisionTransition` + `EventEnvelope` + `to_internal_actor` in `events.py`.
- [x] T5 — Author `FitReport` + `FitDiagnosis` models (AC-B.9).
- [x] T6 — Author `digest.py` canonical-JSON + sha256 helpers (AM-3 contracts documented).
- [x] T7 — Author `event_type_registry.py` with Gagné labels + reserved log event_types + warn-on-unknown validator.
- [x] T8 — Author `weather_band` enum + no-red validator (Pydantic + JSON Schema layers); abundance framing per S-1.
- [x] T9 — Author JSON Schema files for lesson_plan and fit-report (internal fields wrapped in SkipJsonSchema).
- [x] T10 — Author `dials-spec.md` companion with four required sections + Q-3 substance + S-1 abundance framing.
- [x] T11 — Schema-pin contract tests — three files per R2 AM-1 + envelope pin + fit-report-v1 pin.
- [x] T12 — JSON-Schema ↔ dataclass parity test (AC-T.2) with AC-T.2.d required-optional parity.
- [x] T13 — ScopeDecision state-machine tests (AC-T.3) + Q-5 dedicated tests.
- [x] T14 — `scope_decision_transition` event-shape test (AC-T.4) + envelope pin (AC-T.4a).
- [x] T15 — weather_band validator tests (AC-T.5).
- [x] T16 — event_type validator tests (AC-T.6).
- [x] T17 — Digest determinism tests (AC-T.7) + AM-3 nested-list-order + None-vs-missing.
- [x] T18 — `dials-spec.md` companion existence + substance test (AC-T.8, Q-3).
- [x] T19 — Plan-revision monotonicity test (AC-T.10).
- [x] T20 — Rationale verbatim round-trip test (AC-T.11, S-2 + M-extra expanded parametrize).
- [x] T21 — Scope-state ↔ dials/gaps consistency validator + test (AC-T.12).
- [x] T22 — Schema version field presence test (AC-C.2).
- [x] T23 — Extend `SCHEMA_CHANGELOG.md` (AC-C.3) with THREE per-family entries per R2 AM-1.
- [x] T24 — Full regression suite + ruff clean. **Baseline 1149 passed → 1280 passed (+131); 2 skipped, 2 xfailed; no new skips/xfails/live_api/trial_critical.** Ruff clean on all 31-1 files. Orphan-detector + co-commit green.
- [x] T25 — Party-mode implementation review. **(G5 complete 2026-04-18: Winston GREEN, Murat GREEN-pending-TypeAdapter, Paige YELLOW w/ 4 doc remediations, Amelia self-review HIGH. All 5 G5 riders landed in patch cycle.)**
- [x] T26 — `bmad-code-review` layered pass. **(G6 complete 2026-04-18: 6 MUST-FIX + 13 SHOULD-FIX + 5 G5 riders applied; 12 SHOULD-FIX deferred to `_bmad-output/maps/deferred-work.md`; 23 NITs dismissed.)**
- [x] T27 — Close to done; 31-2 / 31-3 / 29-1 / 30-1 unblocked. **(Sprint-status.yaml flip + downstream unblock pending operator confirmation.)**

## Test Plan

`tests_added ≥ K` with **K = 25** (floor, bumped from 22 per R2 riders AM-1 three-file split + S-3 grep test + S-4 actor serialization + W-1 envelope shape-pin). Defense: the seven absorbed items each require ≥2 tests (schema pin + behavioral validator), plus digest determinism (5 sub-assertions incl. AM-3 nested-list-order + None-vs-missing), plus two cross-cutting invariants (revision monotonicity, scope-state↔dials/gaps consistency), plus parametrized state-machine matrix (≥8 legal + illegal pairs counted as parametrized cases), plus three R2-added mandatory tests (AC-T.4a envelope pin, AC-T.14 no-leak grep, AC-T.15 actor serialization safety). The realistic landing is higher (likely 30–40 collecting tests once parametrized matrices expand), but **25 is the pass/fail contract for §6-E4**.

| Test | AC | Level | Mocked? | Blocking at merge? |
|------|----|-------|---------|---------------------|
| `test_lesson_plan_shape_stable` (snapshot + allowlist; R2 AM-1) | T.1 | Contract | N/A | **Yes — Murat's #1 priority** |
| `test_fit_shape_stable` (snapshot + allowlist; R2 AM-1) | T.1 | Contract | N/A | Yes |
| `test_scope_shape_stable` (snapshot + allowlist; R2 AM-1) | T.1 | Contract | N/A | Yes |
| `test_event_envelope_shape_stable` (snapshot + allowlist; R2 W-1) | T.4a | Contract | N/A | Yes |
| `test_fit_report_v1_schema_stable` | T.9 | Contract | N/A | Yes |
| `test_lesson_plan_json_schema_parity` | T.2 | Contract | N/A | Yes |
| `test_required_optional_parity` (R2 AM-2) | T.2.d | Contract | N/A | Yes |
| `test_scope_decision_transition_event_shape` | T.4 | Contract | N/A | Yes |
| `test_scope_decision_transitions_parametrized` (matrix, two-level actor) | T.3 | Unit | N/A | Yes |
| `test_scope_decision_locked_without_maya_rejected` (R2 Q-5) | T.3 / C.8 | Unit | N/A | Yes |
| `test_actor_fields_maya_serialization_safe` (R2 S-4) | T.15 | Unit | N/A | Yes |
| `test_no_intake_orchestrator_in_user_facing_strings` (R2 S-3) | T.14 | Contract | N/A | **Yes — R1 amendment 17** |
| `test_weather_band_accepts_four_bands` (parametrized over 4) | T.5 | Unit | N/A | Yes |
| `test_weather_band_rejects_red_on_direct_construction` | T.5 | Unit | N/A | Yes |
| `test_weather_band_rejects_red_on_json_deserialization` | T.5 | Unit | N/A | Yes |
| `test_weather_band_rejects_red_via_json_schema_path` | T.5 | Unit | N/A | Yes |
| `test_event_type_accepts_all_gagne_nine` (parametrized) | T.6 | Unit | N/A | Yes |
| `test_event_type_warns_on_unknown_registered` | T.6 | Unit | `caplog` | Yes |
| `test_event_type_rejects_invalid_regex` | T.6 | Unit | N/A | Yes |
| `test_event_type_rejects_empty` | T.6 | Unit | N/A | Yes |
| `test_digest_deterministic_across_100_invocations` | T.7 | Unit | N/A | Yes |
| `test_digest_stable_across_key_insertion_order` | T.7 | Unit | N/A | Yes |
| `test_digest_sensitive_to_field_mutation` | T.7 | Unit | N/A | Yes |
| `test_digest_sensitive_to_nested_list_order` (R2 AM-3) | T.7 | Unit | N/A | Yes |
| `test_digest_none_equals_missing` (R2 AM-3) | T.7 | Unit | N/A | Yes |
| `test_dials_spec_companion_exists_and_substantive` (R2 Q-3) | T.8 | Contract | N/A | Yes |
| `test_plan_revision_monotonicity` | T.10 | Unit | N/A | Yes |
| `test_rationale_verbatim_parametrized` (expanded per R2 S-2 + M-extra) | T.11 | Unit | N/A | **Yes — ruling amendment 16 surface** |
| `test_gaps_valid_only_on_in_scope_units` | T.12 | Unit | N/A | Yes |
| `test_dials_valid_only_on_in_or_delegated_units` | T.12 | Unit | N/A | Yes |
| `test_lesson_plan_schema_version_field_present` | AC-C.2 | Contract | N/A | Yes |

**Target baseline delta: ≥25 collecting tests** (floor — realistic landing estimated 30–40, unchanged despite K-floor bump). Baseline from 27-2 closeout: 1149 passed / 2 skipped / 0 failed / 2 xfailed. Expected after 31-1: **≥1174 passed** with no new skips, xfails, `live_api`, or `trial_critical`.

## Out-of-scope

Per Quinn's tri-phasic contract framing and ruling amendment 5's absorption list, 31-1 is **shape-only**. Explicitly excluded:

- **Log write-path / append-only JSONL / mandatory log events emission** — 31-2 scope (including `plan_unit.created`, `scope_decision.set`, `scope_decision_transition`, `plan.locked`, `fanout.envelope.emitted`, `pre_packet_snapshot`).
- **Single-writer enforcement on log** — 31-2 scope (schema-level enforcement of "Marcus-Orchestrator sole writer" per ruling amendment 13).
- **`modality_registry` / `component_type_registry` / `ModalityProducer` ABC** — 31-3 scope.
- **Blueprint producer implementation** — 31-4 scope.
- **Consumer-contract fixtures** for downstream stories (30-3, 29-2, 28-2) — 31-3 burden (stubbed there).
- **Marcus duality split / facade-leak detector / golden-trace baseline** — 30-1 scope (Murat RED binding per ruling amendment 12).
- **Pre-packet envelope emission** — 30-2b scope.
- **4A conversation loop** — 30-3a / 30-3b scope.
- **Plan-lock fanout** — 30-4 scope.
- **Quinn-R two-branch gate** — 31-5 scope (including Declined-with-rationale emission consumed by next-run Irene per ruling amendment 15).
- **Envelope plan-ref coverage manifest** — 32-2 scope (per ruling amendment 14 refinement).
- **Maya journey walkthrough** — 32-4 scope.
- **Retrieval-narration-grammar sentence templates** — 30-5 scope (Sally RED — ruling amendment 3).
- **Tracy posture matrix / negative tests** — 28-1 / 28-2 scope (ruling amendments 9, 10).
- **Gagné diagnostician wiring / p95 instrumentation** — 29-2 scope; 31-1 only ships the `irene_budget_ms` field shape.
- **fit-report-v1 validator + serializer + emission wiring** — 29-1 scope; 31-1 only ships the schema.
- **Profile runs / real-SME fixture** — §6-A1 scope (trial corpus commit per §6 readiness).
- **`ScopeDecisionTransition` JSON Schema parity** — intentionally deferred (party-mode 2026-04-19 consensus on G6 Auditor#4). The transition primitive is an internal orchestration artifact; emission is via the Pydantic model serializer in 31-2, not via a separately-maintained external JSON Schema. Future MCP boundaries needing schema-based validation of these events MUST regenerate the JSON Schema from the Pydantic model via `model_json_schema()` rather than maintaining a hand-edited counterpart, to avoid drift. The shape-pin contract test in `tests/contracts/test_scope_decision_transition_event.py` is the authoritative drift detector.

## Dependencies on Ruling Amendments

Every reference below cites the R1 orchestrator ruling amendment number for traceability.

- **Absorption scope (seven items + companion)** — **Ruling amendment 5**. Governs AC-B.4, AC-B.5, AC-B.6, AC-B.7, AC-B.8, AC-B.9, companion doc AC-T.8.
- **`weather_band` first-class + no-red validator** — **Ruling amendment 5** (Sally absorption item). AC-B.6, AC-B.7, AC-T.5.
- **`event_type` open-string validator (Gagné seam)** — **Ruling amendment 5** (Quinn absorption item). AC-B.8, AC-T.6.
- **`dials-spec.md` companion** — **Ruling amendment 5** (Quinn hedge for deferred UI). AC-T.8.
- **`ScopeDecision` state machine + who-can-transition rules** — **Ruling amendment 5** (Winston absorption item). AC-B.4, AC-T.3.
- **`scope_decision_transition` event primitive (temporal audit)** — **Ruling amendment 5** (Quinn absorption item). AC-B.5, AC-T.4.
- **`fit-report-v1` schema absorption from 29-1** — **Ruling amendment 5**. AC-B.9, AC-T.9.
- **Rationale = free_text verbatim** — **Ruling amendment 16**. AC-C.6, AC-T.11. Field commentary references amendment explicitly so future maintainers don't add coercion.
- **No user-facing "Intake" or "Orchestrator" strings** — **Ruling amendment 17**. Not directly exercised in 31-1 schema, but 31-1 MUST NOT leak "marcus-intake" or "marcus-orchestrator" strings into any field name, enum value, or error message. Enforced via grep check in `bmad-code-review` layered pass.
- **Single-writer rule** — **Ruling amendment 13**. 31-1 does not implement; 31-2 does. Field-level comment in `events.py` references the amendment so the 31-2 author inherits the constraint.
- **Named mandatory log events** — **Ruling amendment 8**. 31-1 pins event-shape for `scope_decision_transition` (AC-B.5); other event shapes pinned in 31-2.
- **Declined-with-rationale consumer** — **Ruling amendment 15**. 31-1's `rationale` + `scope_decision.scope == "out-of-scope"` data structures are what 31-5 emits and 29-2 consumes; this story pins the shape.

## Forward References — §6 PDG Gate

31-1 does **not** trigger §6 First-Trial-Run Readiness PDG satisfaction, but:

- **29-2 cannot open** until §6-E2 (Gagné p95 ≤30s over 20-run batch) fallback contract is drafted.
- **30-1 cannot open** until §6-D1 (golden-trace baseline fixture) is captured.
- **30-3a cannot close** until §6-E1 (5x-consecutive smoke battery) gate is wired.
- **31-5 must emit the Declined-with-rationale structure** that satisfies §6-A2 (Lesson Plan artifact content floor).
- **32-3 must assert** the §6-A3 trial-run-pass signal.
- **32-4 must demonstrate** the §6-C1 Sally Tuesday-morning experiential AC (under 12 minutes, one-sentence Declined articulation).

31-1 is **purely foundational** — every downstream story's PDG contribution is pinned to schema shape defined here.

## Risks

| Risk | Mitigation |
|------|------------|
| **Schema evolution forced by first consumer** (Amelia/Murat first-consumer bias) | Schema PR landed BEFORE any consumer (31-2 / 30-1 / 29-1 all depend on 31-1). Snapshot + allowlist + CHANGELOG gate (AC-T.1) catches silent drift. |
| **Validators miss ruling amendments** (weather_band red, rationale coercion, event_type closed enum) | Every amendment has an AC-T assertion. AC-T.5 triple-layer weather_band-red rejection (construction / JSON deser / JSON Schema). AC-T.11 rationale verbatim round-trip with multi-line + unicode + quotes + whitespace. AC-T.6 event_type warn-not-reject on unknown. |
| **JSON Schema ↔ Pydantic parity drifts silently** | AC-T.2 parity test runs every build. Any mismatch (field type, enum set, required/optional) blocks merge. |
| **Digest non-determinism across platforms/locales** | Canonical-JSON with sorted keys, `ensure_ascii=True`, `separators=(",", ":")`. AC-T.7 runs digest 100 times + proves order-insensitivity + proves mutation-sensitivity. |
| **ScopeDecision state machine leaks transitions to unrelated code** | Transition logic lives in `ScopeDecision.transition_to()` classmethod; external code constructs new `ScopeDecision` values, doesn't mutate state fields directly. AC-T.3 asserts illegal transitions with explicit error messages. |
| **`rationale` helpful-coercion by future maintainer** (ruling amendment 16 violation) | Field docstring + code comment references amendment 16 explicitly. AC-T.11 round-trip test catches any coercion. |
| **`dials-spec.md` drifts from dial schema** | AC-T.8 asserts companion exists + four required sections. Dev note: future dial-semantic changes MUST co-commit schema + companion edits (add to code-review checklist). |
| **31-1 over-scoped; R2 party-mode rejects single-PR approach** | Fallback: if party mode rejects absorption, split into 31-1a (core schema + dials) and 31-1b (ScopeDecision + events + fit-report + dials-spec). But absorption is RATIFIED per ruling amendment 5; splitting would require orchestrator-level ruling reversal. |

## Dev Notes

### Architecture (per R1 orchestrator ruling amendment 5)

- **One schema, one PR.** The absorbed items are all schema-shaped. Splitting them forces reviewing the same structure under multiple story headings, which is how schema drift lands.
- **Shape-only, not emission-path.** Log writing, registries, validators beyond shape-validation, and all consumer wiring are explicitly out-of-scope.
- **Maya-sole-signatory discipline at the type level.** `ScopeDecision.ratified_by: Literal["maya"] | None` makes the Quinn attestor/signatory invariant unforgeable.
- **Canonical-JSON digest.** Sorted keys + ASCII-safe + tight separators. Proves semantic equivalence not syntactic equivalence. Inherits 27-0 digest discipline.
- **Open `event_type` with warn-not-reject on unknown** (Quinn Gagné seam). Future learning models extend the registry without schema churn; unknown labels log a warning so drift is visible in observability, not a merge-blocker.

### Anti-patterns (dev-agent WILL get these wrong without explicit warning)

- **Do NOT collapse `rationale` into an enum or parse it.** Free text, stored verbatim, surfaced verbatim (ruling amendment 16). Any "normalization" — even whitespace trimming — violates the contract.
- **Do NOT allow `scope_decision.ratified_by` to be anything other than `"maya"` or `None`.** Maya is SOLE signatory. Marcus proposes, Irene attests, Maya ratifies. No other actor can enter this field.
- **Do NOT add `"red"` to the `weather_band` enum "for future flexibility."** Sally's UX primitive is non-negotiable for MVP. AC-T.5's three-layer check exists precisely because this is the most-likely drift.
- **Do NOT close the `event_type` enum.** Gagné is hardcoded at MVP but named as a seam (John MVP Discipline). Registry extends without schema version bump.
- **Do NOT write log / emission / append-only code in 31-1.** That's 31-2. This story ships shape + validators + digest helpers + companion doc, nothing more.
- **Do NOT use Python's default `json.dumps` for digest.** Must use canonical form (sorted keys, ASCII-safe, `(",", ":")` separators). AC-T.7 order-sensitivity test exists to catch this.
- **Do NOT name any field, enum value, or error message "marcus-intake" or "marcus-orchestrator"** (ruling amendment 17). Marcus is Marcus, one voice. Internal module names are fine; user-facing surface is not.
- **Do NOT implement 29-1's fit-report validator or serializer here.** 31-1 ships the SHAPE. 29-1 ships the validator + serializer + emission wiring on top of it.
- **Do NOT default-serialize `_internal_actor` / `_internal_proposed_by` into Maya-facing payloads (R2 S-4).** The internal granularity exists for 30-1 golden-trace + 30-4 fanout + bmad-code-review audit ONLY. `model_dump()` and `model_dump_json()` MUST NOT leak `marcus`, `marcus-intake`, `marcus-orchestrator`, or `irene` as actor values in default serialization. Use `Field(exclude=True)` on the internal fields; the public actor field outputs only `system` or `operator`. AC-T.15 enforces.
- **Do NOT use deficit framing on weather_band semantics (R2 S-1).** Never "insufficient," never "failed." Abundance phrasing only: gold = "you've got this cold"; green = "we're in step"; amber = "your call"; gray = "Marcus leans in more." Field docstring + `dials-spec.md` operator-facing wording must mirror.
- **Do NOT skip the Q-5 `model_validator(mode="after")` bypass guard on ScopeDecision.** The type-level `Literal["maya"] | None` stops non-Maya strings, but `None`-in-locked-state still bypasses without the validator. AC-C.8 + AC-T.3's Q-5 dedicated test enforce.
- **Do NOT leave "intake" or "orchestrator" in any user-facing string surface (R2 S-3 / R1 amendment 17).** Not in `Field(description=...)`, not in error messages, not in enum values, not in JSON Schema descriptions, not in `dials-spec.md` prose. AC-T.14 grep scans all of these and fails the build if detected. Internal module/class/import-path names are exempt.

### Source tree (new + touched)

```
marcus/
└── lesson_plan/                            [NEW directory]
    ├── __init__.py                         [NEW +20]   Public surface exports
    ├── schema.py                           [NEW +280]  Pydantic: LessonPlan, PlanUnit, Dials, IdentifiedGap, ScopeDecision, FitReport, FitDiagnosis
    ├── events.py                           [NEW +70]   ScopeDecisionTransition event primitive
    ├── digest.py                           [NEW +60]   Canonical-JSON sha256 helpers + assert_digest_matches
    ├── event_type_registry.py              [NEW +50]   Gagné label registry + warn-on-unknown validator
    ├── schema/
    │   ├── lesson_plan.v1.schema.json      [NEW +180]  JSON Schema for lesson_plan root
    │   └── fit_report.v1.schema.json       [NEW +90]   JSON Schema for fit-report-v1
    └── dials-spec.md                       [NEW +120]  Companion artifact (ruling amendment 5)

tests/contracts/
├── test_lesson_plan_shape_stable.py                    [NEW +90]   AC-T.1 LessonPlan/PlanUnit/Dials/IdentifiedGap pin (R2 AM-1)
├── test_fit_shape_stable.py                            [NEW +60]   AC-T.1 FitReport/FitDiagnosis pin (R2 AM-1)
├── test_scope_shape_stable.py                          [NEW +70]   AC-T.1 ScopeDecision/ScopeDecisionTransition/EventEnvelope pin (R2 AM-1)
├── test_event_envelope_shape_stable.py                 [NEW +40]   AC-T.4a generic envelope (R2 W-1)
├── test_fit_report_v1_schema_stable.py                 [NEW +60]   AC-T.9
├── test_lesson_plan_json_schema_parity.py              [NEW +110]  AC-T.2 + AC-T.2.d required-optional parity (R2 AM-2)
├── test_scope_decision_transition_event.py             [NEW +70]   AC-T.4
├── test_dials_spec_companion_exists.py                 [NEW +60]   AC-T.8 + Q-3 substance (R2 Q-3)
├── test_lesson_plan_schema_version_field_present.py    [NEW +25]   AC-C.2
└── test_no_intake_orchestrator_in_user_facing_strings.py [NEW +80] AC-T.14 no-leak grep (R2 S-3)

tests/
├── test_scope_decision_transitions.py                  [NEW +220]  AC-T.3 state-machine + Q-5 bypass + S-4 two-level actor
├── test_actor_fields_maya_serialization_safe.py        [NEW +70]   AC-T.15 two-level actor serialization safety (R2 S-4)
├── test_weather_band_validator.py                      [NEW +60]   AC-T.5
├── test_event_type_validator.py                        [NEW +70]   AC-T.6
├── test_digest_determinism.py                          [NEW +110]  AC-T.7 incl. AM-3 nested-list-order + None-vs-missing
├── test_plan_revision_monotonicity.py                  [NEW +50]   AC-T.10
├── test_rationale_verbatim_roundtrip.py                [NEW +90]   AC-T.11 expanded parametrize (R2 S-2 + M-extra)
└── test_scope_dials_gaps_consistency.py                [NEW +80]   AC-T.12

_bmad-output/implementation-artifacts/
└── SCHEMA_CHANGELOG.md                                 [TOUCH +40] Lesson Plan Schema v1.0 entry

pyproject.toml                                           [TOUCH +1]  marcus package pythonpath if not surfaced
```

### Testing standards (inherited from 27-0 discipline)

- **No `live_api`, no `trial_critical`, no `xfail`, no `skip`** added to default suite.
- **Schema pins use snapshot + allowlist + CHANGELOG gate** (Murat AC-T.1 mechanism from 27-0).
- **Deterministic fixtures only.** No stateful mocks, no async, no stdio. This is a schema story — nothing here should need concurrency or I/O.
- **Fixture hygiene.** Canonical plan JSON fixtures under `tests/fixtures/lesson_plan/` as plain-text; diff-friendly; no binaries.
- **Per `feedback_regression_proof_tests.md`:** no xfail, no skip, classify every failure (update/restore/delete), measure coverage.

### References

- **Plan doc (post-R1 ruling):** [`_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md`](../planning-artifacts/lesson-planner-mvp-plan.md) — all 17 amendments recorded in §Orchestrator Ruling Record.
- **Governance:** [`CLAUDE.md`](../../CLAUDE.md) — BMAD sprint governance (party-mode + bmad-code-review before `done`, stop-on-impasse-only).
- **Pattern source (schema-foundation story):** [`27-0-retrieval-foundation.md`](./27-0-retrieval-foundation.md) — snapshot + allowlist + CHANGELOG gate pattern; anti-pattern three-beat style; layered code-review discipline.
- **Downstream dependents:**
  - `31-2-lesson-plan-log` — append-only JSONL + mandatory events + single-writer enforcement.
  - `31-3-registries` — modality / component-type / ModalityProducer ABC + consumer-contract fixtures.
  - `29-1-fit-report-v1` — validator + serializer + emission on top of 31-1 schema.
  - `30-1-marcus-duality-split` — facade-leak detector AC + golden-trace baseline (Murat RED).
  - `30-2b-pre-packet-envelope-emission` — first Marcus-Intake consumer of lesson_plan log.
- **SCHEMA_CHANGELOG:** [`SCHEMA_CHANGELOG.md`](./SCHEMA_CHANGELOG.md) — extended by AC-C.3.
- **Tri-phasic contract source:** `§Quinn's Tri-Phasic Contract` in plan doc (Diagnosis → Authorization → Execution).
- **Operator-memory alignment:** `project_enrichment_vs_gap_filling_control.md` — three parameter families (enrichment / gap-filling / evidence-bolster) consumed by `Dials` + `IdentifiedGap.suggested_posture`.

### Non-goals

- **No real consumer in 31-1.** Shape, validators, digest, companion doc only.
- **No LLM calls, no network, no async, no concurrency.** Pure data-and-functions story.
- **No migration path for v0 artifacts.** There is no v0 — this is the first schema. v1.1+ migration docs are future-story work (mirrors 27-0's schema v1.0 establishment).
- **No Marcus / Irene / Tracy / Maya-facing prose copy.** Companion `dials-spec.md` ships operator-facing wording, but Marcus's actual chat copy / weather-ribbon UI strings / Tracy posture-sentence-templates are downstream stories (30-3a, 30-5, Sally UX).
- **No performance optimization.** Schema validation is O(plan_units) — for MVP plan sizes (≤9 units), no complexity management needed. Benchmarking is a post-trial-run follow-up.

## Governance Closure Gates (per CLAUDE.md)

31-1 closes `done` only when ALL below satisfied:

- [x] **G1. R2 party-mode green-light** on this spec (2026-04-18 — 0 RED / 4 YELLOW; 11 riders applied). Panel: Winston / Murat / Quinn / Sally.
- [x] **G2. `bmad-dev-story` execution** with all T1–T27 subtasks checked (post G5/G6 patch cycle).
- [x] **G3. `tests_added ≥ 25`** collecting — actual landing 131 + N_new tests (see Dev Agent Record below). Full suite baseline: 1149 passed → ≥1174 passed after 31-1 achieved.
- [x] **G4. Ruff clean + pre-commit green + co-commit test+impl discipline** (27-2 pattern).
- [x] **G5. Party-mode implementation review** — Winston GREEN / Murat GREEN-pending-TypeAdapter / Paige YELLOW w/ 4 doc remediations / Amelia self-review HIGH. All 5 G5 riders landed in patch cycle 2026-04-18.
- [x] **G6. `bmad-code-review` layered pass** — Blind Hunter + Edge Case Hunter + Acceptance Auditor. Triage: 24 APPLY (6 MUST-FIX + 5 G5 riders + 13 SHOULD-FIX) / 12 DEFER / 23 DISMISS. See Review Record §G6 above for full tally.
- [ ] **G7. `sprint-status.yaml` flipped** `ready-for-dev → in-progress → review → done` per bmm workflow. **(Pending operator confirmation.)**
- [ ] **G8. `bmm-workflow-status.yaml` updated** with closure note naming test delta + absorbed-item summary. **(Pending operator confirmation.)**
- [ ] **G9. Unblocks downstream.** Verify 31-2 / 31-3 / 29-1 / 30-1 / 30-2b all now have a green dependency. **(Pending operator confirmation.)**

## Dev Agent Record

**Executed by:** Amelia (💻 BMAD Developer Agent)
**Date:** 2026-04-18 (R2 green-light + T2–T24 execution, single session)

**Landed artifacts:**

- `marcus/__init__.py` — namespace package.
- `marcus/lesson_plan/__init__.py` — public surface exports.
- `marcus/lesson_plan/schema.py` — Pydantic models for `LessonPlan`, `PlanUnit`, `Dials`, `IdentifiedGap`, `ScopeDecision` (with two-level actor surface + Q-5 bypass guard + scope/dials/gaps consistency validator), `LearningModel`, `PlanRef`, `FitReport`, `FitDiagnosis`, `StaleRevisionError`.
- `marcus/lesson_plan/events.py` — `EventEnvelope` (W-1 generic), `ScopeDecisionTransition` (two-level actor), `to_internal_actor` helper.
- `marcus/lesson_plan/digest.py` — canonical-JSON sha256 + `compute_digest` / `assert_digest_matches`; AM-3 None-vs-missing + list-order contracts documented.
- `marcus/lesson_plan/event_type_registry.py` — Gagné-9 labels + reserved log event_types (incl. `pre_packet_snapshot`) + `validate_event_type` warn-on-unknown.
- `marcus/lesson_plan/schema/lesson_plan.v1.schema.json` — emitted JSON Schema.
- `marcus/lesson_plan/schema/fit_report.v1.schema.json` — emitted JSON Schema.
- `marcus/lesson_plan/dials-spec.md` — four-section companion with Q-3 substance and S-1 abundance framing.

**Tests (18 files, 131 collected tests — well above K=25 floor):**

- `tests/contracts/test_lesson_plan_shape_stable.py` (5)
- `tests/contracts/test_fit_shape_stable.py` (3)
- `tests/contracts/test_scope_shape_stable.py` (4)
- `tests/contracts/test_event_envelope_shape_stable.py` (3)
- `tests/contracts/test_lesson_plan_json_schema_parity.py` (10)
- `tests/contracts/test_scope_decision_transition_event.py` (9; parametrized)
- `tests/contracts/test_dials_spec_companion_exists.py` (3)
- `tests/contracts/test_lesson_plan_schema_version_field_present.py` (3)
- `tests/contracts/test_no_intake_orchestrator_in_user_facing_strings.py` (4)
- `tests/contracts/test_fit_report_v1_schema_stable.py` (5)
- `tests/test_scope_decision_transitions.py` (13)
- `tests/test_actor_fields_maya_serialization_safe.py` (6)
- `tests/test_weather_band_validator.py` (8; parametrized)
- `tests/test_event_type_validator.py` (23; parametrized)
- `tests/test_digest_determinism.py` (8)
- `tests/test_plan_revision_monotonicity.py` (4)
- `tests/test_rationale_verbatim_roundtrip.py` (12; parametrized)
- `tests/test_scope_dials_gaps_consistency.py` (8; parametrized)

**Regression result:** baseline 1149 passed / 2 skipped / 2 xfailed → after 31-1 G3: **1280 passed / 2 skipped / 27 deselected / 2 xfailed** in 33s. Net delta: **+131 passing tests**, zero regressions. After G5+G6 patch cycle (2026-04-18): **1346 passed / 2 skipped / 27 deselected / 2 xfailed** in 34.6s. Net G5+G6 delta: **+66 passing tests** (MF-1..6 landings + SF-1..13 landings + G5 riders), zero regressions. No new `live_api`, `trial_critical`, `xfail`, or `skip`.

**Ruff:** clean across all 31-1 files (`marcus/lesson_plan/` + all 31-1-scope test files).

**Pre-commit:** orphan-reference detector + co-commit invariant both green. Ruff hook passes on 31-1 scope; pre-existing failures in unrelated files (`skills/bmad-agent-content-creator/scripts/init-sanctum.py`, `scripts/utilities/prepare-irene-packet.py`, etc.) are out-of-scope for 31-1.

**R2 rider applicability:** all 11 riders (W-1, AM-1, AM-2, AM-3, M-extra, Q-3, Q-5, S-1, S-2, S-3, S-4) landed cleanly with no impasses. Two implementation-detail notes documented in Dev Notes: (1) `_internal_*` fields use `Field(exclude=True) + SkipJsonSchema` plus an explicit `to_audit_dump()` opt-in helper (because Pydantic v2 `Field(exclude=True)` cannot be overridden via `exclude=set()`); (2) `_internal_*` fields carry a `default="marcus"` so Maya-facing payloads round-trip through `model_validate_json` without requiring the internal field — audit callers that need the precise provenance emit it via `to_audit_dump()`.

**G5+G6 patch cycle closure (2026-04-18):**
- **24 APPLY** landed: 6 MUST-FIX (MF-1 through MF-6) + 5 G5 riders (G5-Murat, G5-Paige-1/2/3/4) + 13 SHOULD-FIX (SF-1 through SF-13).
- **12 DEFER** logged to `_bmad-output/maps/deferred-work.md` §"31-1 G5+G6 deferred findings".
- **23 NITs DISMISSED** (cosmetic: re-export cleanup, DRY regex duplication, pragma style, etc.) — counted in commit, not persisted to deferred-work.md.
- **Key behavioral adds:**
  - `LessonPlan.apply_revision()` method with real `StaleRevisionError` raise (MF-6).
  - `validate_assignment=True` on `EventEnvelope`, `ScopeDecisionTransition`, `PlanUnit` — mutations re-validate (MF-1, MF-2, MF-3).
  - Timezone-aware datetime enforcement across all 5 datetime fields (MF-4).
  - SF-4 warn-once dedup on `validate_event_type` for unknown event_types.
  - SF-5 UUID4 validator on `EventEnvelope.event_id`.
  - `jsonschema` added to dev-dependencies in `pyproject.toml` for SF-10's real `jsonschema.validate` red-rejection surface.
- **New test files (4):** `test_event_envelope_mutation_revalidates.py`, `test_datetime_utc_enforcement.py`, `test_dials_boundary_values.py`, `test_identified_gap_suggested_posture_enum.py`.
- **Test files with new cases:** `test_plan_revision_monotonicity.py` (rewritten), `test_weather_band_validator.py` (+2 cases), `test_event_type_validator.py` (+2 cases), `test_scope_decision_transitions.py` (parametrize expansion), `test_lesson_plan_json_schema_parity.py` (+3 parametrized cases).

## Review Record

### Party-mode R2 green-light — COMPLETE (2026-04-18)

**Panel:** Winston / Murat / Quinn / Sally.
**Verdict:** 0 RED, 4 YELLOW with 11 rider amendments (all applied before dev-story execution). See §R2 Green-Light Record below for the rider-by-rider index.

### G5 Party-Mode Implementation Review — COMPLETE (2026-04-18)

**Panel:** Winston (Architect) / Murat (TEA) / Paige (Tech Writer) / Amelia (Dev self-review).

**Verdicts:**
- **Winston:** GREEN — architecture + invariants land as specified.
- **Murat:** GREEN-pending-TypeAdapter-test — fourth red-rejection surface (TypeAdapter) missing from AC-T.5 coverage; landed as G5-Murat patch in this cycle.
- **Paige:** YELLOW with 4 doc remediations — (1) authority of record in `dials-spec.md`, (2) `Migration: N/A` lines in all three new SCHEMA_CHANGELOG entries, (3) `_internal_*` docstring WHY, (4) spec TL;DR update naming W-1 envelope + AC-T.14 + AC-T.15. All four landed as G5-Paige-1/2/3/4 patches.
- **Amelia self-review:** HIGH confidence with proactive `_internal_actor` docstring WHY flag; landed as G5-Paige-3 extension to cover both `internal_proposed_by` and `internal_actor`.

### G6 bmad-code-review layered pass — COMPLETE (2026-04-18)

Three adversarial layers run in parallel: Blind Hunter / Edge Case Hunter / Acceptance Auditor.

**Findings tally:**

| Layer | MUST-FIX | SHOULD-FIX | NITs | Notes |
|-------|----------|------------|------|-------|
| Blind Hunter | 0 | 13 | 10 | Surface-coverage sweep on models, helpers, tests |
| Edge Case Hunter | 4 | 7 | 7 | 40 branching conditions walked across state machine + validators |
| Acceptance Auditor | 2 | 5 | 6 | 28/36 ACs strong enforcement; AC-B.3 zero-coverage gap flagged |

**Orchestrator triage:**

- **24 APPLY** = 6 MUST-FIX (MF-1 through MF-6) + 5 G5 riders (G5-Murat, G5-Paige-1..4) + 13 high-value SHOULD-FIX (SF-1 through SF-13)
- **12 DEFER** → `_bmad-output/maps/deferred-work.md` §"31-1 G5+G6 deferred findings"
- **23 DISMISS** — cosmetic NITs (re-export cleanup, DRY regex duplication, pragma style, etc.); not persisted to deferred-work.md

All 24 APPLY items landed in the G5/G6 patch cycle dated 2026-04-18. Patch items and their landing surfaces:

- MF-1..4: `validate_assignment=True` on `EventEnvelope` / `ScopeDecisionTransition` / `PlanUnit` + `@field_validator` timezone-aware enforcement across all 5 datetime fields; new tests `test_event_envelope_mutation_revalidates.py` + `test_datetime_utc_enforcement.py`.
- MF-5: AC-B.3 `Dials` boundary-values test — new `test_dials_boundary_values.py` with accept/reject parametrized over 0.0, 1.0, out-of-range, NaN, +inf, -inf.
- MF-6: `LessonPlan.apply_revision()` now raises `StaleRevisionError` for real (replaces tautological in-test helper); `test_plan_revision_monotonicity.py` rewritten to exercise the real method.
- G5-Murat: `test_weather_band_rejects_red_via_type_adapter` in `test_weather_band_validator.py` (fourth red-rejection surface).
- G5-Paige-1: authority-of-record sentence at top of `dials-spec.md`.
- G5-Paige-2: `Migration: N/A` lines in the three new SCHEMA_CHANGELOG entries.
- G5-Paige-3: `_internal_*` field docstring WHY on both `ScopeDecision.internal_proposed_by` and `ScopeDecisionTransition.internal_actor`.
- G5-Paige-4: spec TL;DR bullet naming W-1 envelope + AC-T.14 + AC-T.15.
- SF-1..13: see Dev Agent Record closure notes.

## R1 Orchestrator Ruling Traceability

All nine absorption touchpoints (per ruling amendment 5):

| Item | Originally in | AC / artifact landing in 31-1 |
|------|---------------|-------------------------------|
| 1. `lesson_plan` dataclass + JSON schema | 31-1 (original) | AC-B.1 + `schema.py` + `schema/lesson_plan.v1.schema.json` |
| 2. `plan_unit` + `dials` + `gaps[]` + revision/digest | 31-1 (original) | AC-B.2, AC-B.3, AC-B.10 + `digest.py` |
| 3. `fit-report-v1` schema | 29-1 (moved) | AC-B.9 + `schema/fit_report.v1.schema.json` + AC-T.9 |
| 4. `ScopeDecision` value-object + state machine (Winston) | 30-3a / implicit 31-1 | AC-B.4 + `schema.py::ScopeDecision` + AC-T.3 |
| 5. `scope_decision_transition` event primitive (Quinn) | implicit 31-2 | AC-B.5 + `events.py` + AC-T.4 |
| 6. `weather_band` first-class field (Sally) | implicit 30-3a | AC-B.6 + `PlanUnit.weather_band` |
| 7. `no-red` policy as schema validator (Sally) | implicit 30-3a | AC-B.7 + AC-T.5 (triple-layer) |
| 8. `event_type` open-string validator, Gagné seam (Quinn) | implicit 31-1 | AC-B.8 + `event_type_registry.py` + AC-T.6 |
| 9. `dials-spec.md` companion artifact (Quinn hedge) | implicit 30-3a deferred-UI | AC-T.8 + `dials-spec.md` |

All nine items land in one reviewable schema PR (ruling amendment 5 intent).

## R2 Green-Light Record

**Date:** 2026-04-18
**Review panel:** Winston (Architect) / Murat (TEA / Test) / Quinn (Problem-Solver) / Sally (UX)
**Verdict:** 0 RED, 4 YELLOW with 11 rider amendments — all applied to this spec before dev-story execution.

### Panel verdicts (R2)

- **Winston (W):** YELLOW — one rider (W-1) requiring generic event envelope + pre-registration of `pre_packet_snapshot`.
- **Murat (AM):** YELLOW — three riders (AM-1 schema-pin file split + per-family CHANGELOG entries; AM-2 required-vs-optional parity; AM-3 swap tamper-test for nested-list-order + None-vs-missing) plus one test-detail expansion (M-extra rationale parametrize: CRLF, tab, emoji).
- **Quinn (Q):** YELLOW — two riders (Q-3 dials-spec substance test; Q-5 ScopeDecision locked-without-Maya `model_validator(mode="after")` bypass guard).
- **Sally (S):** YELLOW — four riders (S-1 abundance framing; S-2 rationale edges + no `min_length`; S-3 user-facing-string no-leak grep NON-NEGOTIABLE; S-4 two-level actor surface separating Maya-facing `system|operator` from audit `marcus|marcus-intake|marcus-orchestrator|irene|maya`).

### 11 rider amendments applied (tag → section)

| Rider | Tag | Applied to |
|-------|-----|------------|
| 1 | W-1  | AC-B.5 (envelope-wrapped), AC-B.5a NEW, AC-B.8 (pre_packet_snapshot reserved), AC-T.4a NEW, File Impact, Source Tree, Test Plan |
| 2 | AM-1 | AC-T.1 (three-file split), File Impact, Source Tree, Test Plan, T11, T23, K floor 22→25 |
| 3 | AM-2 | AC-T.2.d NEW (required-vs-optional parity), Test Plan |
| 4 | AM-3 | AC-T.7 (tamper swap for nested-list-order + None-vs-missing), Test Plan |
| 5 | M-extra | AC-T.11 (CRLF / tab / emoji parametrize), Test Plan |
| 6 | Q-3  | AC-T.8 (substance regex for default + example per section), Test Plan |
| 7 | Q-5  | AC-C.8 NEW, AC-T.3 (dedicated Q-5 subtest), Test Plan, Dev Notes anti-pattern |
| 8 | S-1  | AC-B.6 (abundance framing gray rephrase), Dev Notes anti-pattern |
| 9 | S-2  | AC-T.11 (empty / single char / single word / leading-trailing whitespace), `rationale` no `min_length` |
| 10 | S-3  | AC-T.14 NEW, File Impact, Source Tree, Test Plan, Dev Notes anti-pattern |
| 11 | S-4  | AC-B.4 + AC-B.5 (two-level actor surface with `_internal_*` Field(exclude=True)), AC-T.3 (matrix), AC-T.15 NEW, Test Plan, Dev Notes anti-pattern |

**Net-new mandatory tests:** +3 (AC-T.4a envelope pin, AC-T.14 no-leak grep, AC-T.15 actor serialization). **K floor:** 22 → 25. Realistic landing estimate unchanged at 30–40.

**Decision:** R2 green-light ratified, spec amended, proceed to `bmad-dev-story` execution T2–T24 (T25–T27 pending subsequent gates G5/G6/G7-9).
