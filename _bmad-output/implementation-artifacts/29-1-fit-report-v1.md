# Story 29-1: fit-report-v1 validator + serializer + emission wiring

**Status:** done
**Created:** 2026-04-18 (authored post Epic 31 foundation trio closure at `ca133ab`; governance infra committed at `5e4d6fd`)
**Epic:** 29 — Enhanced Irene (Gagné diagnostician + blueprint co-author)
**Sprint key:** `29-1-fit-report-v1`
**Branch:** `dev/lesson-planner`
**Points:** 3
**Depends on:** 31-1 (FitReport + FitDiagnosis shapes + JSON Schema — landed at commit `15f68b1`), 31-2 (Lesson Plan log single-writer + WriterIdentity + assert_plan_fresh — landed at commit `21b2d83`).
**Blocks:** 29-2 (gagne-diagnostician — constructs FitReport instances and calls 29-1's emission wiring); transitively 28-3 (Irene↔Tracy bridge) and 30-3b (sync reassessment).

## TL;DR

- **What:** A thin wrapper module `marcus/lesson_plan/fit_report.py` that adds the three Python surfaces 29-2 will call on top of the already-landed `FitReport` / `FitDiagnosis` Pydantic shapes: (1) `validate_fit_report(...)` — re-validates a constructed or deserialized `FitReport` against a live `LessonPlan`, raising on staleness or unit_id drift (staleness takes precedence when both fire); (2) `serialize_fit_report(...)` / `deserialize_fit_report(...)` — canonical-JSON surface so emitted fit reports are byte-deterministic; (3) `emit_fit_report(...)` — single-writer-enforced append to the Lesson Plan log via 31-2's write API, with Marcus-Orchestrator named as the canonical caller (Irene does NOT import `emit_fit_report` directly — she hands FitReport instances to Marcus via the existing orchestration seam).
- **Why:** 29-2 (gagne-diagnostician, next in the critical path) needs to produce a `FitReport` per Irene-run and hand it to downstream consumers (Maya's weather ribbon, Tracy's IdentifiedGap auto-dispatch at plan-lock, 30-3b sync reassessment) through a stable, tested, reviewed surface — not inline dict manipulation. Landing this wrapper before 29-2 prevents 29-2 from both inventing the API and testing it.
- **29-2 unblock handshake (single-line completion signal, AC-B.9):** `from marcus.lesson_plan.fit_report import validate_fit_report, serialize_fit_report, deserialize_fit_report, emit_fit_report, StaleFitReportError, UnknownUnitIdError` resolves + a smoke test passes. That is the one thing 29-2 must be able to do the moment 29-1 is `done`.
- **Done when:** `fit_report.py` module shipped + validator + serializer + emitter green + `tests_added ≥ 10` with realistic landing 12-15 + single-gate post-dev review (Edge Case Hunter recommended; per `docs/dev-guide/story-cycle-efficiency.md` §2) + governance validator PASS + sprint-status flipped `ready-for-dev → in-progress → done`.
- **Scope discipline:** 29-1 ships NO new Pydantic shape and NO edit to `marcus/lesson_plan/schema.py` or `fit_report.v1.schema.json`. The shapes and JSON-Schema artifact are already landed by 31-1 (AC-B.9 + AC-T.9). 29-1 is pure wrapper.

## Story

As the **Lesson Planner MVP wrapper-layer author**,
I want **the fit-report-v1 validator + serializer + emission surface landed on top of 31-1's Pydantic shapes**,
So that **29-2 (gagne-diagnostician) can construct `FitReport` instances, validate them against the live plan, serialize them canonically, and emit them to the Lesson Plan log without inventing any of those surfaces itself** — and so that the single-writer rule from 31-2 continues to hold across all fit-report writes.

## Background — Why This Story Exists

The R1 orchestrator ruling amendment 5 (2026-04-18) absorbed the `fit-report-v1` **schema** into 31-1, leaving 29-1 as the **wrapper-implementation** story. 31-1 landed `FitReport` (with `schema_version`, `source_ref`, `plan_ref`, `diagnoses[]`, `generated_at`, `irene_budget_ms`) and `FitDiagnosis` (with `unit_id`, `fitness`, `commentary`, `recommended_scope_decision`, `recommended_weather_band`) at [marcus/lesson_plan/schema.py](../../marcus/lesson_plan/schema.py) lines 478–522 plus the JSON Schema at [marcus/lesson_plan/schema/fit_report.v1.schema.json](../../marcus/lesson_plan/schema/fit_report.v1.schema.json). Contract pin test at `tests/contracts/test_fit_shape_stable.py` already asserts the shape.

What is missing and what 29-1 lands:

1. **Validation against a live `LessonPlan`**. 31-1's `FitReport` validates its own internal shape but cannot check whether `plan_ref.lesson_plan_revision` / `lesson_plan_digest` still match the current plan, nor whether every `diagnoses[*].unit_id` exists on that plan. That cross-model check is the validator's job.
2. **Canonical-JSON serialization**. 31-2's log-write path takes a string; the caller owns the serialization. Without a canonical-JSON surface, each caller could produce different byte sequences for semantically-identical reports, breaking byte-identical log-replay and golden-trace invariants (R5 risk, 30-1 golden-trace binding PDG).
3. **Emission wiring that honors the single-writer rule**. 31-2 enforces `WriterIdentity == marcus-orchestrator` at `append_event` time. 29-2 (and any other future fit-report emitter) must route through a sanctioned surface that enforces this up front with a clean error, not by letting the 31-2 log raise at the last mile.

**Unblocked when 29-1 closes:** 29-2 (gagne-diagnostician) opens next; it constructs a `FitReport` per Irene-run, hands it to 29-1's validator + serializer + emitter, and moves on. 28-3 (Irene↔Tracy bridge) becomes buildable once 29-2 lands because auto-dispatch at plan-lock reads `FitReport.diagnoses[*].fitness` to decide which units need Tracy gap-fill. 30-3b (sync reassessment) consumes 29-1's serializer to produce deterministic diff payloads for Marcus's conversational surface.

## T1 Readiness

- **Gate mode:** `single-gate` per `docs/dev-guide/story-cycle-efficiency.md` §2. 29-1 is a wrapper atop an already-landed precedent (31-1 schema); post-dev single-layer review suffices. Edge Case Hunter is the highest-value single layer (per §2 "Why G6 stays non-negotiable"). **Note:** A belt-and-suspenders pre-dev party-mode review was run on this spec (2026-04-18); findings + dispositions logged in §Pre-Dev Review Record below. K-floor bumped from 8 (MVP-plan floor) to 10 to accommodate five rider-added coverage-gap tests (W-3 / M-3 / M-4 / Q-1 grep / Q-4 tamper detection); per story-cycle-efficiency §1 "Coverage-gap tests that emerge from thinking through the AC matrix are added without count discipline — that's legitimate," this K-bump is coverage-grounded, not parametrization theater.
- **K floor:** `K = 10` (bumped from MVP-plan §6-E4 floor of 8 after pre-dev party-mode review added five coverage-gap AC-Ts).
- **Target collecting-test range:** 12-15 (1.2×K to 1.5×K per `docs/dev-guide/story-cycle-efficiency.md` §1).
- **Realistic landing estimate:** 12-15.
- **Required readings** (dev agent reads at T1 before any code):
  - `docs/dev-guide/pydantic-v2-schema-checklist.md` §§ "validate_assignment", "datetime awareness", "serialization discipline", "Field(exclude=True) audit-surface pattern" — for the validator's re-validation path and the serializer's canonical-form discipline.
  - `docs/dev-guide/dev-agent-anti-patterns.md` §§ "schema", "test-authoring", "review-ceremony" — fit_report wrapper must NOT re-author the Pydantic shape landed by 31-1; the anti-pattern is re-deriving from memory.
  - `docs/dev-guide/story-cycle-efficiency.md` §1 (K-floor discipline), §2 (single-gate policy), §3 (aggressive DISMISS rubric for post-dev review), §4A (validator gate — run before every status flip).
- **Scaffold requirement:** References the schema-story scaffold at [docs/dev-guide/scaffolds/schema-story/](../../docs/dev-guide/scaffolds/schema-story/). **Partial instantiation only** — see §Scaffold Applicability Note below. `tests/test_no_intake_orchestrator_leak.py.tmpl` is the directly-reusable scaffold piece for this story.
- **Runway pre-work available:** `_bmad-output/specs/30-1-golden-trace-baseline-capture-plan.md` (Murat binding PDG; independent of 29-1 progress) — spawnable as a side task.

## Scaffold Applicability Note

29-1 ships NO new Pydantic model and NO new JSON Schema artifact. The schema-story scaffold at `docs/dev-guide/scaffolds/schema-story/` is designed for stories where the core deliverable is a Pydantic v2 model family + emitted JSON Schema + shape-pin tests. For 29-1:

- `src/schema.py.tmpl` — **NOT INSTANTIATED**. Shape is already landed (`marcus/lesson_plan/schema.py` — `FitReport`, `FitDiagnosis`, `PlanRef`). Re-instantiating would duplicate and create drift risk.
- `src/digest.py.tmpl` — **NOT INSTANTIATED**. 29-1 uses the canonical-JSON discipline from `marcus/lesson_plan/digest.py` (landed by 31-1); the fit-report serializer reuses `compute_digest`'s serialization rules rather than re-deriving.
- `schema/*.schema.json` — **NOT INSTANTIATED**. Already landed at `marcus/lesson_plan/schema/fit_report.v1.schema.json`.
- `tests/test_shape_stable.py.tmpl` — **NOT INSTANTIATED**. Already landed at `tests/contracts/test_fit_shape_stable.py` (31-1 AC-T.1, AM-1 three-file split).
- `tests/test_json_schema_parity.py.tmpl` — **NOT INSTANTIATED**. Already landed at the 31-1 parity suite (AC-T.2).
- `tests/test_no_intake_orchestrator_leak.py.tmpl` — **INSTANTIATED** at `tests/contracts/test_no_intake_orchestrator_leak_fit_report.py` scoped to `marcus/lesson_plan/fit_report.py` and the fit-report public error messages surface (R1 amendment 17 / R2 rider S-3 enforcement).
- `CHANGELOG-entry.md.tmpl` — **NOT INSTANTIATED**. No `SCHEMA_CHANGELOG.md` edit; 29-1 ships no schema-version-visible change. (31-1 already recorded the fit-report-v1 entry under "Fit Report v1.0".)

Governance-validator reference to the scaffold path is satisfied by the no-leak-test instantiation above plus this section's explicit applicability carve-out.

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — `fit_report.py` module lands at `marcus/lesson_plan/fit_report.py`.** Module docstring mirrors the 31-1 `schema.py` audience-layered style (module purpose + discipline notes + cross-references). New module re-exports `FitReport`, `FitDiagnosis`, `PlanRef` from `marcus.lesson_plan.schema` so callers have one import path for the whole fit-report surface; it does NOT re-define them.

2. **AC-B.2 — `validate_fit_report(report, *, plan) -> FitReport`.** Public function. Accepts either a `FitReport` instance, a plain `dict`, or a JSON `str`; normalizes to a `FitReport` via `FitReport.model_validate(...)` / `FitReport.model_validate_json(...)`. Raises the following domain exceptions:
   - `StaleFitReportError` (new, inherits `ValueError`) if `report.plan_ref.lesson_plan_revision != plan.revision` **or** `report.plan_ref.lesson_plan_digest != plan.digest`. Error message names both sides of the mismatch verbatim.
   - `UnknownUnitIdError` (new, inherits `ValueError`) if any `diagnoses[*].unit_id` is absent from `{pu.unit_id for pu in plan.plan_units}`. Error message names the offending unit_id set.
   - Raises the Pydantic `ValidationError` surface unchanged on shape violations (does NOT swallow or rewrap — dev-agent anti-pattern trap).

   **AC-B.2.1 — Error precedence (Q-2 rider).** When both stale `plan_ref` AND unknown `unit_id` conditions are true (common failure mode: stale plan has had its `plan_units` restructured), `StaleFitReportError` MUST be raised FIRST. The `unit_id` existence check runs ONLY if `plan_ref` validates clean. Rationale: staleness is the root cause; unknown-unit-id diagnostics would lead the caller to hunt for a typo when the real problem is revision drift. Wrong-direction debugging is worse than a silent failure because it burns caller attention.

   **AC-B.2.2 — Validator idempotency (W-2 rider).** When `validate_fit_report` is passed an already-constructed `FitReport` instance (not a dict / JSON str), the function MUST NOT re-trigger `FitReport.model_validate(...)` or `model_dump()` in any path. Cross-model checks (staleness + unit_id) operate on the passed instance's attributes directly. Perf-shape pin test (AC-T.10) catches silent regressions where a well-meaning refactor adds a defensive re-parse.

3. **AC-B.3 — `serialize_fit_report(report: FitReport) -> str`.** Deterministic canonical-JSON output: `json.dumps(report.model_dump(mode="json"), sort_keys=True, ensure_ascii=True, separators=(",", ":"))`. Semantically-identical FitReport instances ALWAYS produce byte-identical output. The `mode="json"` argument is mandatory — without it, `datetime` fields round-trip as `datetime` objects and `json.dumps` picks a non-canonical ISO format. Datetime fields serialize to ISO-8601 UTC with `+00:00` suffix (31-1's invariant).

4. **AC-B.4 — `deserialize_fit_report(s: str) -> FitReport`.** Inverse of AC-B.3. For any `s` that was produced by `serialize_fit_report`, `serialize_fit_report(deserialize_fit_report(s)) == s` byte-identical. For inputs not produced by the canonical serializer (e.g., pretty-printed JSON), deserialization succeeds if the JSON is valid + shape conforms, but round-trip is not guaranteed.

5. **AC-B.5 — `emit_fit_report(report: FitReport, *, writer: WriterIdentity, plan: LessonPlan) -> None`.** Appends a single event to the Lesson Plan log via 31-2's write path. Contract:
   - Calls `validate_fit_report(report, plan=plan)` first — emission of a stale or unit-id-invalid report is forbidden (fail-fast, not tolerated).
   - Event shape conforms to 31-1's `EventEnvelope`: `event_id` (uuid4), `timestamp` (UTC), `plan_revision == report.plan_ref.lesson_plan_revision`, `event_type == "fit_report.emitted"`, `payload == serialize_fit_report(report)` parsed back to a dict (so the log's JSONL line is canonical).
   - The `event_type` value `"fit_report.emitted"` is registered in `marcus/lesson_plan/event_type_registry.py` — either in the RESERVED list (if 31-2's contract hasn't expanded KNOWN to cover it yet) or in a new FIT_REPORT_EMITTED_EVENT_TYPE constant. Registration change is the only `event_type_registry.py` edit 29-1 performs.
   - Single-writer enforcement is not duplicated in 29-1; the call flows through 31-2's `append_event(..., writer=writer)` which already enforces `writer == WriterIdentity.MARCUS_ORCHESTRATOR`. 29-1 adds NO redundant up-front check; the 31-2 error bubbles up unchanged. Test confirms a non-orchestrator writer raises the 31-2 permission error through this path.

   **AC-B.5.1 — Canonical caller invariant (Q-1 rider — LOAD-BEARING).** The canonical caller of `emit_fit_report` is **Marcus-Orchestrator**. Irene produces `FitReport` instances (in 29-2's scope) and hands them to Marcus via the existing orchestration seam; Irene MUST NOT import or call `emit_fit_report` directly. The docstring on `emit_fit_report` names this invariant verbatim: *"Canonical caller: Marcus-Orchestrator. Irene produces FitReport instances and hands them off via the orchestration seam. Calling this function from any non-Marcus code path — including direct invocation by Irene, Tracy, or any specialist — is a contract violation that the 31-2 single-writer enforcement will catch, but should never reach."* Grep-test (AC-T.11) asserts that no file under `marcus/lesson_plan/` imports `emit_fit_report` from outside `marcus.lesson_plan.fit_report` itself; 29-2's future emission path, when it lands, must route through Marcus.

   **AC-B.5.2 — `plan_revision` redundancy is tamper-detection (Q-4 rider).** The envelope's `plan_revision` and the payload's `report.plan_ref.lesson_plan_revision` are two copies of the same integer. This duplication is **load-bearing**: the envelope field is the 31-2 log's index key (used for monotonic-revision assertion at append time); the payload field is inside the canonical-JSON blob that is digested for integrity. Drift between them signals either envelope tampering or post-serialization payload mutation. `emit_fit_report` MUST set both from the same source (`report.plan_ref.lesson_plan_revision`), and a one-line inline comment at the assignment site names this invariant verbatim: *"# Load-bearing redundancy — envelope/payload drift is tamper detection. Do not DRY."* AC-T.12 asserts mutation-in-isolation is detectable by equality on read-back.

   **AC-B.5.3 — Canonical payload excludes `event_id` and `timestamp` (M-3 rider).** Payload canonicalization for log-replay equality MUST exclude the two envelope-level non-deterministic fields (`event_id` uuid4 + `timestamp` datetime). Implementation: `emit_fit_report`'s "payload == serialize_fit_report(report) parsed back to dict" refers to the FitReport payload itself (which is deterministic given the report inputs); the envelope-level `event_id` and `timestamp` live outside the payload and are NOT part of the hash/digest domain. 29-2's §6-E 5x-consecutive replay harness asserts equality on payload-excluding-those-two-fields. AC-C.1 names this contract explicitly.

   **AC-B.5.4 — Event-type taxonomy grammar (W-1 rider).** The string `"fit_report.emitted"` seeds a taxonomy convention: `<domain_noun>.<past_tense_verb>`. The `event_type_registry.py` edit that registers `"fit_report.emitted"` MUST also add (if not already present) a one-line comment naming the grammar: `# Event-type naming: <domain_noun>.<past_tense_verb>. E.g. "fit_report.emitted", "gagne_diagnosis.completed", "plan.locked".` This is cheap now (one line) and expensive at taxonomy story 6 to retrofit. If a grammar comment already exists from the 31-2 RESERVED list, no addition needed — just confirm the new registration follows the convention.

6. **AC-B.6 — Timezone-awareness guarantee.** 31-1's `FitReport.generated_at` field validator rejects naive datetime. 29-1 does NOT add a second check; instead, `emit_fit_report` relies on the Pydantic surface raising early. Test AC-T.6 confirms construction of a `FitReport` with a naive datetime raises at the Pydantic layer with the 31-1 error message, before any log write is attempted.

7. **AC-B.7 — No new schema version; no SCHEMA_CHANGELOG entry.** Fit-report-v1 remains at `schema_version == "1.0"` (31-1's pinned value). 29-1 does not bump the version, does not add a changelog row, and does not modify the `fit_report.v1.schema.json` artifact.

8. **AC-B.8 — Public error messages are Marcus-duality-clean.** All exception messages raised by `fit_report.py` public surface (`StaleFitReportError`, `UnknownUnitIdError`, any emission-path user-facing string) are scanned by `tests/contracts/test_no_intake_orchestrator_leak_fit_report.py` for the forbidden tokens `"intake"` and `"orchestrator"` (case-insensitive). Internal module and field names may contain these tokens — only public-facing strings are constrained. (R1 amendment 17 / R2 rider S-3; matches 31-1 AC-T.14.)

9. **AC-B.9 — 29-2 unblock handshake (J-2 rider — explicit completion signal).** When 29-1 closes, 29-2 MUST be able to run: `from marcus.lesson_plan.fit_report import validate_fit_report, serialize_fit_report, deserialize_fit_report, emit_fit_report, StaleFitReportError, UnknownUnitIdError` and immediately use those six names without further import ceremony. `marcus/lesson_plan/__init__.py` re-exports are a convenience; the canonical import path for 29-2 is `marcus.lesson_plan.fit_report`. This is the single-line completion signal: if the import resolves and each name is callable / raiseable, 29-1 has landed its unblock contract. A smoke test in `tests/test_fit_report_smoke.py::test_29_1_unblock_handshake` asserts the import + attribute presence.

### Test (AC-T.*)

1. **AC-T.1 — Validator happy path.** `tests/test_fit_report_validator.py::test_validate_fit_report_fresh_plan_succeeds`: given a plan at revision N + digest D and a fit report whose `plan_ref` matches, `validate_fit_report(report, plan=plan)` returns the `FitReport` instance unchanged. Covers all three input forms (FitReport, dict, JSON str).

2. **AC-T.2 — Stale-revision and stale-digest rejection (with precedence parametrize per Q-2).** `tests/test_fit_report_validator.py::test_validate_fit_report_rejects_stale[*]`: parametrized over four cases — `(stale_revision, same_digest)`, `(same_revision, stale_digest)`, `(stale_revision, stale_digest)`, and `(stale_revision, stale_digest, unit_ids_unknown_in_new_plan)` — the fourth case asserts `StaleFitReportError` is raised (NOT `UnknownUnitIdError`), confirming AC-B.2.1 error precedence. All cases verify the error message names both sides of the plan_ref mismatch verbatim.

3. **AC-T.3 — Unknown-unit-id rejection.** `tests/test_fit_report_validator.py::test_validate_fit_report_rejects_unknown_unit_id`: diagnosis for `unit_id == "gagne-event-99"` (not in plan, but plan_ref fresh) raises `UnknownUnitIdError` naming the offending id set.

4. **AC-T.4 — Serializer determinism (M-1 key-order expansion).** `tests/test_fit_report_serializer.py::test_serialize_fit_report_deterministic`: same `FitReport` → byte-identical output across 100 invocations AND key-order-independent input tests produce identical output across: (a) forward-insertion-order dict, (b) reverse-insertion-order dict, (c) shuffled dict built via `dict(sorted(items, key=lambda _: rng.random()))` with `rng = random.Random(42)` (fixed seed — deterministic on CI). Without the fixed seed, the shuffle case is itself non-deterministic and defeats the purpose.

5. **AC-T.5 — Round-trip identity.** `tests/test_fit_report_serializer.py::test_serialize_deserialize_roundtrip`: for a parametrized matrix of FitReport instances (empty diagnoses / single diagnosis / multiple diagnoses / all-optional-fields-None / unicode commentary / multi-line commentary), `serialize_fit_report(deserialize_fit_report(serialize_fit_report(r))) == serialize_fit_report(r)` byte-identical.

6. **AC-T.6 — Naive-datetime rejection surface.** `tests/test_fit_report_validator.py::test_fit_report_rejects_naive_generated_at`: constructing `FitReport(..., generated_at=datetime(2026, 4, 18))` (naive) raises the Pydantic `ValidationError` with 31-1's error message; `emit_fit_report` is NOT reached.

7. **AC-T.7 — Single-writer enforcement via 31-2.** `tests/test_fit_report_emitter.py::test_emit_fit_report_rejects_non_orchestrator_writer`: calling `emit_fit_report(..., writer=WriterIdentity.MARCUS_INTAKE)` raises the exact 31-2 permission error (surface test — 29-1 does NOT add its own check; 31-2's is sufficient).

8. **AC-T.8 — No-leak grep.** `tests/contracts/test_no_intake_orchestrator_leak_fit_report.py` (scaffold-instantiated, dormant-skip removed): grep scans all strings returned by `StaleFitReportError`, `UnknownUnitIdError`, and any public emission-path error; asserts neither `"intake"` nor `"orchestrator"` appears in any user-facing message. Internal identifiers (WriterIdentity.MARCUS_ORCHESTRATOR enum value) are exempt via an explicit allowlist.

9. **AC-T.9 — Emit-ordering negative test (M-4 rider — single-gate compensator).** `tests/test_fit_report_emitter.py::test_emit_fit_report_does_not_write_on_validation_failure`: mock 31-2's `append_event` with a `MagicMock` that tracks call count. Call `emit_fit_report` with a stale plan_ref. Assert: (a) `StaleFitReportError` raised, (b) `append_event.call_count == 0`. Confirms the AC-B.5 "validate FIRST" ordering invariant at runtime. This is the single-gate-story compensator for skipping G5 party-mode implementation review — it pins the seam contract that a runtime reviewer would have caught by inspection.

10. **AC-T.10 — Validator idempotency perf-shape pin (W-2 rider).** `tests/test_fit_report_validator.py::test_validate_fit_report_does_not_re_parse_instance_input`: patch `FitReport.model_validate` and `FitReport.model_dump` with `MagicMock` wrappers. Pass an already-constructed `FitReport` instance. Assert neither mock was called (cross-model checks operate on passed attributes directly). Protects against silent regressions where a defensive refactor adds re-parse cost.

11. **AC-T.11 — Canonical-caller grep invariant (Q-1 rider — LOAD-BEARING).** `tests/contracts/test_fit_report_canonical_caller.py`: grep-walks the `marcus/` tree (excluding `marcus/lesson_plan/fit_report.py` itself + test files under `tests/` where mocking is legitimate) for imports of `emit_fit_report`. Assertion: **zero** matches in production code paths outside Marcus-Orchestrator's module. Irene-side code (when 29-2 lands) MUST NOT import `emit_fit_report` directly. At authoring time this test is trivially green (no other module imports it); the test is load-bearing for 29-2 and beyond — it fails the moment someone violates the canonical-caller invariant by expedient import. Test docstring names the AC-B.5.1 invariant verbatim.

12. **AC-T.12 — Envelope/payload `plan_revision` tamper detection (Q-4 rider).** `tests/test_fit_report_emitter.py::test_envelope_payload_plan_revision_consistency`: emit a report; read the JSONL line from the log; assert envelope-level `plan_revision` equals payload-nested `plan_ref.lesson_plan_revision`. Separately, construct a malformed log line where the two differ by one; assert a simple equality check on read-back detects the drift. Confirms AC-B.5.2 redundancy is not silently DRY'd away in a future refactor.

### Contract pinning (AC-C.*)

1. **AC-C.1 — Emission event is log-replayable, with datetime round-trip + payload canonicalization (M-2 + M-3 riders).** `tests/test_fit_report_emitter.py::test_emit_fit_report_roundtrip_via_log`: emit a report; read it back via 31-2's `read_events(event_type="fit_report.emitted")`; deserialize the payload via `deserialize_fit_report`. Assertions:
   - (a) Payload bytes, **excluding envelope-level `event_id` and `timestamp`** (per AC-B.5.3 — those two are non-deterministic envelope fields, outside the canonical-payload domain), are byte-identical to the original canonical serialization.
   - (b) **Datetime round-trip (M-2):** `replayed.generated_at.tzinfo is not None` (not silently dropped to naive by `datetime.fromisoformat` on some payload shapes) AND `replayed.generated_at == original.generated_at` (equality, not just offset-match).
   - (c) All other `FitReport` fields (`schema_version`, `source_ref`, `plan_ref`, `diagnoses`, `irene_budget_ms`) equal the originals.

2. **AC-C.2 — Event-type registration.** `tests/test_fit_report_emitter.py::test_fit_report_emitted_event_type_registered`: the string `"fit_report.emitted"` appears in the event_type_registry (either RESERVED or KNOWN). Registration change to `event_type_registry.py` is the only edit 29-1 makes to that module. Adjacent sub-assertion: the event_type_registry contains the grammar comment `# Event-type naming: <domain_noun>.<past_tense_verb>` near the registration (AC-B.5.4 rider).

## File Impact (preliminary — refined at bmad-dev-story T1)

- **NEW:** `marcus/lesson_plan/fit_report.py` — validator + serializer + emitter + exception types. Re-exports `FitReport`/`FitDiagnosis`/`PlanRef`.
- **NEW:** `tests/test_fit_report_validator.py` — AC-T.1 + AC-T.2 + AC-T.3 + AC-T.6 + AC-T.10.
- **NEW:** `tests/test_fit_report_serializer.py` — AC-T.4 + AC-T.5.
- **NEW:** `tests/test_fit_report_emitter.py` — AC-T.7 + AC-T.9 + AC-T.12 + AC-C.1 + AC-C.2.
- **NEW:** `tests/test_fit_report_smoke.py` — AC-B.9 29-2 unblock handshake.
- **NEW:** `tests/contracts/test_no_intake_orchestrator_leak_fit_report.py` — AC-T.8 (scaffold-instantiated from `docs/dev-guide/scaffolds/schema-story/tests/test_no_intake_orchestrator_leak.py.tmpl`, dormant-skip removed).
- **NEW:** `tests/contracts/test_fit_report_canonical_caller.py` — AC-T.11 grep-walk asserting no production module outside `marcus.lesson_plan.fit_report` imports `emit_fit_report`.
- **TOUCHED:** `marcus/lesson_plan/__init__.py` — re-export the four new names (`validate_fit_report`, `serialize_fit_report`, `deserialize_fit_report`, `emit_fit_report`) + the two new exceptions (`StaleFitReportError`, `UnknownUnitIdError`) for discoverability. **Coordinate with 32-2 parallel agent** — see §Cross-Lane Coordination below.
- **TOUCHED:** `marcus/lesson_plan/event_type_registry.py` — register `"fit_report.emitted"` + grammar comment (`# Event-type naming: <domain_noun>.<past_tense_verb>.`). **Does NOT touch** `schema.py`, `schema/fit_report.v1.schema.json`, `digest.py`, `log.py`, or any existing test.

## Cross-Lane Coordination

The 32-2 plan-ref envelope coverage manifest story is in flight on `dev/lesson-planner` in a parallel worktree. At 29-1 authoring time (this session, 2026-04-18), 32-2's uncommitted working tree modifies `marcus/lesson_plan/__init__.py` to re-export 14 coverage_manifest symbols and `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` with a coverage-manifest-v1.0 entry.

**29-1's touch on `__init__.py` must be additive** — add the four fit-report functions + two exceptions alongside (not replacing) whatever 32-2 lands. At dev-story T2, the dev agent should:
1. Pull latest `origin/dev/lesson-planner` to pick up 32-2's `__init__.py` edits if already merged.
2. If 32-2 is still uncommitted locally, coordinate with the 32-2 agent before editing `__init__.py` (or rebase onto 32-2's branch if 32-2 is work-in-flight on a child branch).
3. 29-1 does NOT touch `SCHEMA_CHANGELOG.md` regardless.

## Tasks / Subtasks (preliminary — refined at bmad-dev-story T1)

- [x] **T1 — T1 Readiness.** Read the three required-reading docs (pydantic-v2 checklist, anti-patterns catalog, story-cycle-efficiency). Confirm understanding of the canonical-JSON invariant from 31-1 (`marcus/lesson_plan/digest.py`). Confirm scaffold applicability carve-outs in §Scaffold Applicability Note. Re-run governance validator as a smoke check.
- [x] **T2 — Module shell + exceptions.** Create `marcus/lesson_plan/fit_report.py` with module docstring, re-exports, `StaleFitReportError` + `UnknownUnitIdError` class stubs.
- [x] **T3 — Validator.** Implement `validate_fit_report(report, *, plan)`. Writes AC-T.1 + AC-T.2 + AC-T.3 tests alongside.
- [x] **T4 — Serializer + deserializer.** Implement `serialize_fit_report` + `deserialize_fit_report`. Writes AC-T.4 + AC-T.5 tests.
- [x] **T5 — Event-type registration.** Add `"fit_report.emitted"` to `event_type_registry.py`. Writes AC-C.2 test. **Discovered coupling:** `log.py` import-time assertion `frozenset(WRITER_EVENT_MATRIX.keys()) == NAMED_MANDATORY_EVENTS` requires the event_type also be added to `WRITER_EVENT_MATRIX` — see §Dev Agent Record.
- [x] **T6 — Emitter.** Implement `emit_fit_report`. Writes AC-T.7 + AC-C.1 tests.
- [x] **T7 — Naive-datetime surface test.** Writes AC-T.6.
- [x] **T8 — No-leak grep test.** Instantiate `test_no_intake_orchestrator_leak_fit_report.py`; scope to `fit_report.py` public error-message surfaces. Writes AC-T.8. (Source-file-scan portion of scaffold template dropped as out-of-AC-T.8-scope — AC-T.8 specifies runtime error-message scan only.)
- [x] **T9 — Rider-added tests (AC-T.9 / .10 / .11 / .12).**
- [x] **T10 — 29-2 unblock handshake smoke test.** Writes `tests/test_fit_report_smoke.py::test_29_1_unblock_handshake` (AC-B.9, J-2).
- [x] **T11 — `__init__.py` re-export coordination.** Additive edit coexisting with 32-2 agent's uncommitted coverage_manifest re-exports. No conflict.
- [x] **T12 — Full regression + ruff + governance validator re-run.**
  - `python -m pytest tests/ --run-live` — **1339 passed / 4 skipped / 2 deselected / 2 xfailed / 0 failed** in 77.55s.
  - `python -m ruff check` on all 29-1-touched files — all checks pass.
  - `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/29-1-fit-report-v1.md` — PASS.
  - One pre-existing test (`tests/test_lesson_plan_log_named_events.py::test_named_mandatory_events_contains_all_six_amendment_8_events`) required update: equality assertion relaxed to subset assertion because R1 amendment 8 is a minimum set, not a ceiling; 29-1's addition of `fit_report.emitted` per R1 amendment 5 is legitimate. Classification: UPDATE (preserves invariant, accepts new amendment). Per memory rule on regression-proof tests.
- [x] **T13 — Single-gate post-dev review (bmad-code-review).** Full three-layer pass executed 2026-04-18 (Blind Hunter + Edge Case Hunter + Acceptance Auditor). Triage: 3 PATCH / 2 DEFER / 9 DISMISS per §3 aggressive rubric. Findings recorded below in `### Review Findings`.
- [x] **T14 — Close to done.** All 3 PATCH findings applied 2026-04-18 (docstring retraction + logger.warning + Raises block expansion). Regression green: `--run-live` 1340 passed / 0 failed; default 1318 passed / 0 failed. Ruff clean. Governance validator PASS. Status flipped `review → done`. Sprint-status + next-session-start-here.md updated in closure commit.

### Review Findings

**From bmad-code-review 2026-04-18 (three-layer pass: Blind Hunter + Edge Case Hunter + Acceptance Auditor).**

Triage tally: 0 decision-needed · 3 patch · 2 defer · 9 dismiss. Dismiss rationale logged in the post-dev Review Record below.

**Patches (applied 2026-04-18):**

- [x] [Review][Patch] Retract `serialize_fit_report` digest-parity docstring overclaim — module docstring rewritten to describe canonical-JSON per AC-B.3 and explicitly note that `compute_digest` additionally applies `_strip_none` (so hashing this serializer's output is NOT comparable to `LessonPlan.digest`). Serializer function docstring mirrors the clarification. Applied at marcus/lesson_plan/fit_report.py module docstring + `serialize_fit_report` docstring.
- [x] [Review][Patch] Add `logger.warning` when `log=None` in `emit_fit_report` — `logging.getLogger(__name__)` added at module level; `emit_fit_report` step 3 now emits a WARNING when `log is None` before the fallback instantiation, surfacing the production-log fallback in CI output so accidental test omissions don't silently contaminate `state/runtime/lesson_plan_log.jsonl`.
- [x] [Review][Patch] Add `ValueError` and `TypeError` to `emit_fit_report` docstring Raises block — Raises block expanded to name six exceptions: `StaleFitReportError`, `UnknownUnitIdError`, `pydantic.ValidationError`, `TypeError`, `ValueError`, `UnauthorizedWriterError`. Args-block for `writer` also notes the step-3 typo-guard distinction.

**Deferred (pre-existing or future-story scope):**

- [x] [Review][Defer] Duplicate `unit_id` entries in `report.diagnoses` silently accepted [marcus/lesson_plan/fit_report.py:156-164] — deferred, natural home is 29-2 (gagne-diagnostician) where Irene constructs diagnoses. Set-collapse masks conflicting fitness verdicts. Irene should not produce duplicates; duplicate-prevention logic lives at construction-time, not validation-time.
- [x] [Review][Defer] `UnknownUnitIdError` exposes full sorted plan unit_id list [marcus/lesson_plan/fit_report.py:160-164] — deferred, future-proofing surface. At MVP unit_ids are Gagne labels (safe); future plans may have sensitive identifiers. Defer to a later hardening pass.

## Post-Dev Review Record

**Date:** 2026-04-18
**Format:** bmad-code-review three-layer pass (Blind Hunter + Edge Case Hunter + Acceptance Auditor).
**Invocation:** single-gate post-dev review per `docs/dev-guide/story-cycle-efficiency.md` §2; full layered pass rather than Edge-Case-Hunter-only, applying §3 aggressive DISMISS rubric at triage.

### Layer outcomes

- **Blind Hunter (4 findings):** 1 MED (digest-parity overclaim), 3 LOW (docstring-Raises-gap, log=None fallback, tamper-detection-is-writer-side).
- **Edge Case Hunter (8 findings):** 1 HIGH (same digest-parity — dedup'd), 2 MED (log=None fallback — dedup'd; duplicate unit_ids), 5 LOW (UnknownUnitIdError list leak, TypeError untested, re-validate on emit, file-creation path untested, numeric-string edge no-issue).
- **Acceptance Auditor:** All ACs PASS or documented PARTIAL. 1 MED (log.py touched — documented erratum), 4 LOW (inline-comment string drift, W-3 folded not standalone, WriterIdentity spec-vs-code drift spec-side-only, test-count/K-floor consistency confirmations).

### Triage tally

| Bucket | Count | Rationale |
|---|---|---|
| decision-needed | 0 | No ambiguous design choices required operator input |
| patch | 3 | See action items above |
| defer | 2 | See deferred items above |
| dismiss | 9 | See dismissal list below |

### DISMISS rubric applied (§3 aggressive)

| Finding | Dismissal reason |
|---|---|
| log.py touched contra spec | Already documented as erratum in Dev Agent Record + Completion Notes; functional change is correct (required by import-time assertion); paperwork in place |
| Q-4 inline-comment exact-string drift | Cosmetic (§3 cosmetic rubric); semantic intent preserved; AC-T.12 catches functional regressions |
| W-3 race-test folded not standalone | Already acknowledged in Pre-Dev Review Record rider table; 31-2 owns monotonic-revision assertion |
| WriterIdentity enum vs Literal form drift | Spec-documentation drift only; code + tests correctly use the landed `Literal` API |
| B4 tamper-detection writer-side trivial | §3 test-theater rubric (reviewer self-classified); equivalence is established at construction-time, tamper is read-side invariant |
| E6 emit re-validates on every call | Reviewer self-classified "Not a correctness bug"; idempotency pin already skips model_validate on FitReport instance |
| E7 no test for file-creation path | Out of scope — 31-2 owns log-file creation path |
| E8 json.loads numeric-string edge | Reviewer self-classified "No edge issue found" |
| TypeError untested for non-(FitReport/dict/str) | §3 test-theater ("could add one more parametrize case for symmetry"); type signature is the contract; defensive code works |

### Remediation discipline

Applying the 3 patches in this session before flipping to `done` per CLAUDE.md BMAD governance rule 3 (must run bmad-code-review before done).

## Test Plan

`tests_added ≥ K` with **K = 10** (bumped from MVP-plan §6-E4 floor of 8 per pre-dev party-mode review; see §Pre-Dev Review Record — W-3 / M-3 / M-4 / Q-1 / Q-4 each added a genuinely-new coverage surface). Target range 12-15 (1.2×K-1.5×K per story-cycle-efficiency §1). Collecting-test count discipline: parametrize matrices count as ONE test (per §1 "parametrized cases over enum values are ONE test, not N tests"). Example: AC-T.2 parametrizes four rejection cases but counts as ONE test.

**Hard cap:** if the dev agent finds itself over 15 collecting tests, it must name the specific coverage justification per §1 "the Dev Agent Record must name the specific coverage justification per extra ~5 tests." Rider-driven coverage-gap tests (AC-T.9 / .10 / .11 / .12) are inside budget by construction.

**Expected collecting tests:**

| AC | File | Notes |
|---|---|---|
| AC-T.1 | test_fit_report_validator.py | happy path (3 input forms, parametrized → 1 test) |
| AC-T.2 | test_fit_report_validator.py | rejection (4 cases parametrized → 1 test, Q-2 precedence included) |
| AC-T.3 | test_fit_report_validator.py | unknown_unit_id |
| AC-T.4 | test_fit_report_serializer.py | determinism (3 key-order cases parametrized, M-1) |
| AC-T.5 | test_fit_report_serializer.py | round-trip identity (6-case parametrize → 1 test) |
| AC-T.6 | test_fit_report_validator.py | naive-datetime rejection |
| AC-T.7 | test_fit_report_emitter.py | non-orchestrator writer → 31-2 error |
| AC-T.8 | test_no_intake_orchestrator_leak_fit_report.py | no-leak grep |
| AC-T.9 | test_fit_report_emitter.py | validation-failure-no-write (M-4) |
| AC-T.10 | test_fit_report_validator.py | idempotency perf-shape pin (W-2) |
| AC-T.11 | test_fit_report_canonical_caller.py | canonical-caller grep invariant (Q-1) |
| AC-T.12 | test_fit_report_emitter.py | envelope/payload tamper detection (Q-4) |
| AC-C.1 | test_fit_report_emitter.py | log-replay + datetime tz + payload-sans-envelope-fields (M-2 + M-3) |
| AC-C.2 | test_fit_report_emitter.py | event-type registration + grammar comment (W-1) |
| AC-B.9 | test_fit_report_smoke.py | 29-2 unblock handshake (J-2) |

15 collecting-test rows. Exactly inside target 12-15. 1.5×K = 15 hard cap not breached.

## Out-of-scope

- Any change to `marcus/lesson_plan/schema.py` — `FitReport` / `FitDiagnosis` / `PlanRef` shapes are pinned. 29-1 is wrapper-only.
- Any change to `marcus/lesson_plan/schema/fit_report.v1.schema.json` — JSON Schema artifact is pinned.
- Any bump to `fit_report` `schema_version` — stays at `"1.0"`.
- Gagné diagnostic logic — that is 29-2's scope. 29-1 ships only the API surface 29-2 will call.
- Tracy-side gap auto-dispatch on `FitDiagnosis.fitness == "absent"` — 28-3's scope.
- Sync reassessment payload format — 30-3b's scope. 29-1 provides the serializer; 30-3b decides how to wrap it.
- Consensus cross-validation on FitReport outputs — 27-2.5 consensus adapter is blocked and out of MVP.
- **Declined-rationale join (Q-3 rider).** The fit-report carries NO back-pointer to prior `scope_decision` rationale events. The consumer — 29-2 (gagne-diagnostician, per R1 ruling amendment 15 "Declined-with-rationale consumer") — is responsible for joining `FitDiagnosis.unit_id` against the Lesson Plan log's `scope_decision` event stream to locate prior Declined rationales. This is a **join responsibility, not a schema responsibility**. 29-1 does NOT add a back-pointer field to the FitReport shape and does NOT provide a join helper. 29-2 owns the join; 31-2's log API is sufficient for the lookup.
- **Emit splitting to 29-2 (J-1 dismissed).** Pre-dev party-mode review raised the question of whether `emit_fit_report` should be deferred out of 29-1 into 29-2 (resizing 29-1 to ~1.5pt). **Dismissed** as relitigation of R1 ruling amendment 5, which explicitly scoped "fit-report-v1 validator + serializer + **emission wiring**" to 29-1. The PM push for MVP minimalism is acknowledged but does not override a settled ratification. Emission stays in 29-1; 29-2 calls the emit function it will find already wired.

## Dependencies on ruling amendments + R2 riders

- **R1 amendment 5** — fit-report-v1 schema absorbed into 31-1; 29-1 reduced to validator + serializer + emission wiring. This story's existence is the direct consequence.
- **R1 amendment 13** — Single-writer rule on Lesson Plan log. 29-1's emitter relies on the 31-2 enforcement surface landed at commit `21b2d83`; does NOT add a redundant check.
- **R1 amendment 17 + R2 rider S-3** — No user-facing "intake" / "orchestrator" strings. AC-T.8 enforces via scaffold-instantiated grep test.
- **31-1 R2 rider AM-2** — Bidirectional required/optional parity. NOT re-enforced in 29-1 (31-1's test suite already owns it); referenced here as the discipline 29-1's code must not break.
- **31-2 R2 rider M-2** — "non-plan.locked stale ACCEPTED" invariant. 29-1's `StaleFitReportError` check runs BEFORE any log-write; does not race with the 31-2 log-level freshness gate.

## Risks

- **R-A: Staleness check race.** Between `validate_fit_report(report, plan=plan)` returning successfully and `emit_fit_report` reaching the 31-2 log-write, another writer could advance `plan.revision`. **Mitigation:** 29-1's validator re-reads from the passed-in `plan` argument (not a fresh log read); caller is responsible for passing the plan snapshot they're committing to. 31-2's `append_event` surface already asserts monotonic revision at the log level, catching the race on the way down. 29-1 does NOT attempt to acquire a log-level lock.
- **R-B: Serializer drift from `compute_digest`.** If `serialize_fit_report` uses different separators or key-order rules from `marcus/lesson_plan/digest.compute_digest`, the digest of a `FitReport` embedded in a `LessonPlan` will NOT match a digest computed from the serialized form. **Mitigation:** dev agent at T4 literally references `compute_digest`'s `json.dumps` kwargs and reuses them; AC-T.4 exercises determinism on the exact same surface.
- **R-C: `event_type` registry collision.** If 32-2 or another parallel story registers a `"fit_report.emitted"` event_type before 29-1 lands, the registration becomes a double-add or a conflict. **Mitigation:** dev agent at T5 greps `event_type_registry.py` for the string before registering; if present, asserts the existing registration matches 29-1's semantics and moves on. Else registers.
- **R-D: `__init__.py` merge conflict with 32-2.** See §Cross-Lane Coordination. **Mitigation:** dev agent pulls latest before editing; if 32-2 is still uncommitted, coordinates through the human operator.

## Dev Notes

### Architecture

29-1 slots in between 31-1 (schema) and 29-2 (gagne-diagnostician) as the narrowest possible wrapper. It does not own any domain logic — just the three surfaces 29-2 will import. The canonical-JSON serialization invariant is lifted from 31-1's `digest.py` (not re-derived). The single-writer rule is delegated to 31-2 (not re-enforced). This is deliberate: 29-1 is a glue story, and glue stories that add their own policy are the anti-pattern 31-1 / 31-2 carefully avoided.

### Anti-patterns (dev-agent WILL get these wrong without explicit warning)

Reference [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) for the shared catalog. Story-specific traps:

- **Re-authoring the Pydantic shape.** `FitReport` and `FitDiagnosis` are landed. Do not add them to `fit_report.py` — re-export from `schema.py`. If the dev agent's T2 file starts with `class FitReport(BaseModel)`, delete and re-plan.
- **Duplicating `compute_digest`'s JSON kwargs.** Use `json.dumps(..., sort_keys=True, ensure_ascii=True, separators=(",", ":"))` — lift verbatim from `digest.py`. Do not pick different values; the digest-parity invariant breaks silently.
- **Adding a second single-writer check in `emit_fit_report`.** 31-2's `append_event` already enforces `WriterIdentity.MARCUS_ORCHESTRATOR`. Do not add a redundant check — that's the "defensive coding in internal code" anti-pattern; it also splits the authoritative error message into two surfaces.
- **Using `model_dump()` without `mode="json"` for serialization.** `datetime` fields round-trip as `datetime` objects, then `json.dumps` picks a non-canonical ISO format (missing the `+00:00` suffix). Canonical-JSON breaks.
- **Rewrapping Pydantic `ValidationError`.** Let it propagate. Callers (29-2) expect the standard Pydantic surface for shape errors and the domain surface (`StaleFitReportError`, `UnknownUnitIdError`) for cross-model errors.
- **Checking `unknown_unit_id` before `plan_ref` staleness (Q-2).** The two errors can both fire on a stale plan with restructured units. Staleness MUST precede unit-id check, or the caller goes hunting for a unit-id typo when the real cause is revision drift. AC-B.2.1 + AC-T.2 pin this.
- **Re-parsing an already-constructed FitReport instance (W-2).** If the dev agent writes `return FitReport.model_validate(report.model_dump())` in the validator's "accept-FitReport-instance" branch, delete. That's a silent perf regression and AC-T.10 catches it.
- **Importing `emit_fit_report` from any non-Marcus code path (Q-1 — LOAD-BEARING).** Irene's code, Tracy's code, specialists' code — none may `from marcus.lesson_plan.fit_report import emit_fit_report`. The contract is: Irene *produces* a validated FitReport, hands it to Marcus-Orchestrator, and Marcus emits. If the dev agent finds themselves writing `from marcus.lesson_plan.fit_report import emit_fit_report` in any module under `marcus/irene/` or `marcus/tracy/` (when those land), STOP — the single-writer rule is being end-run. AC-T.11 grep-test pins this.
- **DRY'ing the envelope-vs-payload `plan_revision` duplication (Q-4).** At AC-B.5.2 the envelope and payload both carry `plan_revision` — intentionally. Do NOT refactor to set just one. The duplication is tamper-detection, not sloppy design. Inline comment at the assignment site names this verbatim; AC-T.12 asserts detection.
- **Including `event_id` or `timestamp` in the canonical-payload equality domain (M-3).** Those two are envelope-level non-deterministic fields; comparing across runs on a canonical-payload with them included will always diverge. AC-B.5.3 + AC-C.1 spell out the exclusion.
- **Over-parametrizing to inflate the test count.** §1 K-floor discipline: parametrized cases are ONE test. If the collecting-test count hits 16+, the dev agent owes a per-extra-5 coverage justification. Target is 12-15.

### Source tree (new + touched)

```
marcus/lesson_plan/fit_report.py                                          [NEW]
marcus/lesson_plan/__init__.py                                            [TOUCHED — coordinate w/ 32-2]
marcus/lesson_plan/event_type_registry.py                                 [TOUCHED — one-line + grammar comment]
tests/test_fit_report_validator.py                                        [NEW]
tests/test_fit_report_serializer.py                                       [NEW]
tests/test_fit_report_emitter.py                                          [NEW]
tests/test_fit_report_smoke.py                                            [NEW — 29-2 unblock handshake]
tests/contracts/test_no_intake_orchestrator_leak_fit_report.py            [NEW, scaffold-instantiated]
tests/contracts/test_fit_report_canonical_caller.py                       [NEW — Q-1 grep-walk invariant]
```

### Testing standards (inherited)

- Pydantic v2 idioms per [docs/dev-guide/pydantic-v2-schema-checklist.md](../../docs/dev-guide/pydantic-v2-schema-checklist.md).
- Anti-patterns per [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md).
- K-floor / single-gate policy per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md).
- Governance validator gate per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §4A — run at ready-for-dev flip and again before bmad-dev-story opens.

### References

- [_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md](../planning-artifacts/lesson-planner-mvp-plan.md) — parent plan; §Epic 29 / §6-E4 K-floor row / R1 amendment 5.
- [_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md](31-1-lesson-plan-schema.md) — schema precedent; AC-B.9 / AC-T.9 for fit-report-v1 shape.
- [_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md](31-2-lesson-plan-log.md) — log + WriterIdentity + append_event API that 29-1's emitter calls.
- [marcus/lesson_plan/schema.py](../../marcus/lesson_plan/schema.py) — `FitReport` / `FitDiagnosis` / `PlanRef` live here.
- [marcus/lesson_plan/schema/fit_report.v1.schema.json](../../marcus/lesson_plan/schema/fit_report.v1.schema.json) — JSON Schema artifact (already landed).
- [marcus/lesson_plan/digest.py](../../marcus/lesson_plan/digest.py) — canonical-JSON invariant source; 29-1's serializer lifts kwargs.
- [marcus/lesson_plan/log.py](../../marcus/lesson_plan/log.py) — 31-2's `append_event(writer=...)` surface.
- [marcus/lesson_plan/event_type_registry.py](../../marcus/lesson_plan/event_type_registry.py) — where `"fit_report.emitted"` registers.
- [docs/dev-guide/scaffolds/schema-story/](../../docs/dev-guide/scaffolds/schema-story/) — scaffold referenced for the no-leak test template; see §Scaffold Applicability Note for carve-outs.

## Governance Closure Gates (per CLAUDE.md)

- [ ] All ACs met (behavioral + test + contract-pinning).
- [ ] Automated verification green: `python -m pytest tests/ --run-live` + `python -m ruff check marcus/ tests/` + `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/29-1-fit-report-v1.md`.
- [ ] Single-gate post-dev review completed (Edge Case Hunter layer, per story-cycle-efficiency §2).
- [ ] Remediated review record (APPLY / DEFER / DISMISS tally logged).
- [ ] Sprint-status flip `ready-for-dev → in-progress → done` in `_bmad-output/implementation-artifacts/sprint-status.yaml`.
- [ ] `next-session-start-here.md` advanced to 29-2 as next anchor.

## Dev Agent Record

### Agent Model Used

Claude Opus 4.7 (1M context).

### Debug Log References

- `python -m pytest tests/ --run-live -q` → 1339 passed / 4 skipped / 2 deselected / 2 xfailed / 0 failed in 77.55s.
- `python -m pytest tests/ -q` → 1317 passed / 1 skipped / 27 deselected / 2 xfailed / 0 failed in 23.53s.
- `python -m ruff check` on all 29-1 files → All checks passed.
- `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/29-1-fit-report-v1.md` → PASSED.

### Completion Notes List

- **29-1 deliverable scope landed as specified.** Wrapper module `marcus/lesson_plan/fit_report.py` ships three public surfaces (validate / serialize+deserialize / emit) atop 31-1's landed `FitReport`/`FitDiagnosis`/`PlanRef` shapes plus two new domain exception types (`StaleFitReportError`, `UnknownUnitIdError`) and a module constant `FIT_REPORT_EMITTED_EVENT_TYPE`.

- **All 12 APPLY riders from pre-dev party-mode review landed:** W-1 (taxonomy grammar comment in `event_type_registry.py`), W-2 (AC-T.10 idempotency perf pin via `MagicMock` on `model_validate`/`model_validate_json`), W-3 (folded into AC-C.1 log-replay round-trip), M-1 (AC-T.4 fixed-seed shuffle for determinism), M-2 (AC-C.1 sub-assertion (b) — `tzinfo is not None` + equality), M-3 (AC-C.1 sub-assertion (a) — canonical-payload equality scoped to payload, not envelope `event_id`/`timestamp`), M-4 (AC-T.9 zero-call assertion on `append_event` when validation fails), Q-1 (AC-B.5.1 docstring + AC-T.11 grep-walk invariant in `tests/contracts/test_fit_report_canonical_caller.py`; zero offenders at this commit — test is load-bearing for 29-2 and beyond), Q-2 (AC-B.2.1 staleness-precedes-unit-id-check + fourth parametrize case in AC-T.2), Q-3 (out-of-scope addition documenting 29-2's join responsibility for Declined rationales), Q-4 (AC-B.5.2 inline comment on envelope/payload `plan_revision` redundancy + AC-T.12 mutation-detection test), J-2 (AC-B.9 + `tests/test_fit_report_smoke.py`).

- **DISCOVERED CROSS-CUT: `log.py` WAS touched — spec was wrong.** The 29-1 spec asserted "Does NOT touch log.py". At dev time this turned out to be infeasible: `log.py` carries an import-time assertion `frozenset(WRITER_EVENT_MATRIX.keys()) == NAMED_MANDATORY_EVENTS` (line ~180). Because `NAMED_MANDATORY_EVENTS` is aliased from `RESERVED_LOG_EVENT_TYPES` in `event_type_registry.py`, registering `"fit_report.emitted"` there forces a corresponding addition to `WRITER_EVENT_MATRIX` in `log.py` — otherwise the module fails to import. The single-line addition to `WRITER_EVENT_MATRIX` (`"fit_report.emitted": frozenset({"marcus-orchestrator"})`) is the minimum touch that satisfies the invariant. Semantically, this does NOT change any existing 31-2 behavior — it extends the matrix by one row permitting Marcus-Orchestrator to write the new event type. The spec's "does not touch log.py" assertion is an erratum; File List records the reality.

- **Pre-existing test updated (classified UPDATE, not restore-or-delete):** `tests/test_lesson_plan_log_named_events.py::test_named_mandatory_events_contains_all_six_amendment_8_events` asserted strict equality `expected == NAMED_MANDATORY_EVENTS`. The test's stated intent (docstring: "R1 ruling amendment 8 — six named mandatory event_types") is that the amendment-8 set is the MINIMUM contract, not a ceiling. Adding a seventh event via a separate ruling amendment (here: R1 amendment 5 / 29-1's spec) is legitimate. Assertion relaxed to subset (`r1_amendment_8_minimum - NAMED_MANDATORY_EVENTS` empty) with updated docstring explaining the invariant. Original intent preserved; 29-1 addition accepted. Per memory rule on regression-proof tests: classified, updated rather than restored-or-deleted, original contract invariant preserved.

- **Collecting-test count landed at 15 exactly** (K=10, target 12-15). Breakdown per the Test Plan table in the spec. pytest node-id count is 26 (parametrize cases); per story-cycle-efficiency §1 parametrize matrices count as ONE collecting test.

- **Scaffold-template adoption honored the applicability carve-out.** Only the no-leak grep template was instantiated. `test_no_forbidden_tokens_in_fit_report_source` (source-file scan from the template) was dropped because AC-T.8 specifies runtime error-message scan only; the source-file scan would have pushed collecting-test count to 16 (1 over the 1.5×K cap). Clean interpretation of AC-T.8 lets the count stay at 15. The runtime scan via `test_public_error_messages_no_leak` (parametrized over StaleFitReportError + UnknownUnitIdError) is the AC-T.8-required assertion.

- **Canonical-caller grep test (AC-T.11 / Q-1) passes trivially at 29-1.** No production module outside `marcus/lesson_plan/fit_report.py` imports `emit_fit_report`. The test is deliberately load-bearing for 29-2 and beyond — it fails the moment a future contributor adds `from marcus.lesson_plan.fit_report import emit_fit_report` outside the allowed-prefix list. The allowed list pre-seeds `marcus/orchestrator/` (the 30-1 Marcus-duality split target) so that story doesn't need to modify the test.

- **Cross-lane coordination with 32-2 agent was clean.** 32-2's uncommitted `__init__.py` modifications added 14 coverage_manifest re-exports. My 29-1 edit added 8 fit-report symbols to the same file. No overlap, no conflict. `__all__` alphabetical ordering preserved.

- **Import-time invariants hold:** `frozenset(WRITER_EVENT_MATRIX.keys()) == NAMED_MANDATORY_EVENTS` ✓; `"fit_report.emitted" in REGISTERED_EVENT_TYPES` ✓; top-level `from marcus.lesson_plan import emit_fit_report` works ✓; module-level `from marcus.lesson_plan.fit_report import ...` works ✓.

### File List

**NEW — module code:**

- `marcus/lesson_plan/fit_report.py` (~220 lines) — validator + serializer + deserializer + emitter + two domain exceptions + FIT_REPORT_EMITTED_EVENT_TYPE constant; canonical-JSON kwargs lifted from `digest.py`; AC-B.5.1 canonical-caller docstring; AC-B.5.2 inline comment on envelope/payload redundancy.

**NEW — tests:**

- `tests/test_fit_report_validator.py` — AC-T.1 (3 input forms parametrize), AC-T.2 (4-case stale-rejection parametrize with Q-2 precedence), AC-T.3 (unknown-unit-id), AC-T.6 (naive-datetime Pydantic rejection), AC-T.10 (idempotency perf-shape pin with `MagicMock` on `model_validate`/`model_validate_json`). 5 collecting tests / 10 pytest nodeids.

- `tests/test_fit_report_serializer.py` — AC-T.4 (determinism with 100-invocation byte-identity + fixed-seed shuffle for key-order independence), AC-T.5 (6-case round-trip matrix: empty / single / multiple / all-optional-None / unicode / multi-line). 2 collecting tests / 7 nodeids.

- `tests/test_fit_report_emitter.py` — AC-T.7 (non-orchestrator rejection via 31-2 `UnauthorizedWriterError` surface), AC-T.9 (validation-failure-no-write — `MagicMock` on `append_event`, zero-call assertion), AC-T.12 (envelope/payload `plan_revision` tamper detection + mutation detection), AC-C.1 (log-replay with datetime-tz pin + canonical-payload-sans-envelope-fields equality), AC-C.2 (event-type registration + grammar-comment text scan). 5 collecting tests / 5 nodeids.

- `tests/test_fit_report_smoke.py` — AC-B.9 (29-2 unblock handshake — six public names importable + callable/raiseable). 1 collecting test.

- `tests/contracts/test_no_intake_orchestrator_leak_fit_report.py` — AC-T.8 (parametrized error-message scan over StaleFitReportError + UnknownUnitIdError). 1 collecting test / 2 nodeids.

- `tests/contracts/test_fit_report_canonical_caller.py` — AC-T.11 (Q-1 grep-walk: no production file outside `marcus/lesson_plan/fit_report.py`, `marcus/lesson_plan/__init__.py`, `marcus/orchestrator/` imports `emit_fit_report`). 1 collecting test.

**TOUCHED — production code:**

- `marcus/lesson_plan/__init__.py` — added 8 fit-report re-exports (additive with 32-2's coverage_manifest exports). No conflict.
- `marcus/lesson_plan/event_type_registry.py` — added `"fit_report.emitted"` to `RESERVED_LOG_EVENT_TYPES` + taxonomy grammar comment (`<domain_noun>.<past_tense_verb>`) per W-1 rider.
- `marcus/lesson_plan/log.py` — added `"fit_report.emitted": frozenset({"marcus-orchestrator"})` row to `WRITER_EVENT_MATRIX` (required by module-level assertion — see Completion Notes "DISCOVERED CROSS-CUT"). Spec's "does not touch log.py" was an erratum.

**TOUCHED — tests:**

- `tests/test_lesson_plan_log_named_events.py::test_named_mandatory_events_contains_all_six_amendment_8_events` — equality assertion relaxed to subset; docstring updated to clarify amendment-8 is a minimum, not a ceiling. Classification: UPDATE.

**TOUCHED — story:**

- `_bmad-output/implementation-artifacts/29-1-fit-report-v1.md` — tasks T1-T12 marked complete; Dev Agent Record populated; Status flipped `in-progress → review`.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — 29-1 flipped `in-progress → review`.

### Change Log

- **2026-04-18** — 29-1 dev-story execution. All 12 APPLY riders from pre-dev party-mode landed. One cross-cut discovery: `log.py` `WRITER_EVENT_MATRIX` had to be extended (spec erratum); single-row additive edit preserving existing behavior. One regression-test UPDATE: `test_named_mandatory_events_contains_all_six_amendment_8_events` equality → subset (amendment-8 is a minimum contract, not a ceiling). Post-implementation: 1339 passed `--run-live` / 0 failed; ruff clean; governance validator PASS. Status flipped `in-progress → review`.

## Pre-Dev Review Record

**Date:** 2026-04-18
**Format:** bmad-party-mode — belt-and-suspenders pre-dev green-light round even though 29-1 is single-gate by policy (pre-dev party-mode not required per story-cycle-efficiency §2).
**Panel:** Winston (architect), Murat (test architect), Dr. Quinn (problem-solver), John (PM).
**Verdict:** Green with 12 APPLY riders + 1 DISMISS + 1 DEFER.

### Rider tally

| ID | Source | Short description | Landed via |
|---|---|---|---|
| W-1 | Winston | Event-type naming-grammar comment (`<domain_noun>.<past_tense_verb>`) | AC-B.5.4 + AC-C.2 sub-assertion |
| W-2 | Winston | Validator idempotency — already-validated FitReport does NOT re-trigger model_validate | AC-B.2.2 + AC-T.10 |
| W-3 | Winston | Explicit race test: plan-revision bump between validate return and append_event; asserts 31-2 monotonic assertion fires | Folded into AC-C.1 log-replay + implicit in AC-T.9 |
| M-1 | Murat | Serializer determinism expansion — reverse + shuffled-with-fixed-seed key-order | AC-T.4 parametrize expansion |
| M-2 | Murat | Log-replay datetime round-trip assertion (`tzinfo is not None` + equality) | AC-C.1 sub-assertion (b) |
| M-3 | Murat | `event_id` + `timestamp` excluded from canonical-payload equality domain | AC-B.5.3 + AC-C.1 sub-assertion (a) |
| M-4 | Murat | Negative test: validation failure → `append_event.call_count == 0` | AC-T.9 (single-gate compensator) |
| Q-1 | Quinn | Canonical-caller invariant — Marcus-Orchestrator is sole caller of `emit_fit_report`; Irene does NOT import it | AC-B.5.1 + AC-T.11 grep-walk (LOAD-BEARING) |
| Q-2 | Quinn | Error precedence — staleness check before unit-id check | AC-B.2.1 + AC-T.2 precedence parametrize |
| Q-3 | Quinn | Declined-rationale join responsibility belongs to 29-2, not 29-1 schema | Out-of-scope § addition |
| Q-4 | Quinn | Envelope/payload `plan_revision` duplication is load-bearing tamper detection; preserve + comment + test | AC-B.5.2 + AC-T.12 |
| J-2 | John | Name the 29-2 unblock handshake as an explicit single-line completion-signal AC | AC-B.9 + AC-T.* via test_fit_report_smoke.py |

### Dismissed / deferred

- **J-1 DISMISSED (policy):** Defer `emit_fit_report` out of 29-1 to 29-2 (resize to 1.5pt). John's push was to find the smallest-thing-unblocks. The rider was dismissed because it relitigates R1 ruling amendment 5 ("29-1 implements the validator + serializer + **emission wiring**"). Emission was explicitly scoped to 29-1 at the ratified-plan level. Rationale: a PM scope challenge is legitimate at spec time but not a unilateral override of a settled multi-round party-mode amendment. Dismissal is documented in §Out-of-scope so it doesn't get re-raised by a future reviewer.
- **J-3 PARTIAL DEFER:** John proposed consolidating AC-B.6 (datetime) + AC-T.6 into AC-B.2, and collapsing AC-B.8 + AC-T.8 (no-leak) as redundant with 31-1. Datetime consolidation — accepted in spirit: AC-B.6 stays as-is because the "fit-report construction raises at Pydantic layer" path is a distinct assertion from validator cross-model checks. No-leak consolidation — rejected: 31-1's no-leak scans `schema.py`; 29-1 needs its own scan on `fit_report.py` public surface (different module, different public error messages). Kept as separate ACs.

### K-floor bump rationale

- MVP-plan §6-E4 sets 29-1 K≥8 (floor).
- Five rider-added AC-Ts (AC-T.9 / .10 / .11 / .12 + AC-C.1 sub-assertions) push collecting-test count from 10 → 15.
- Target range 10-12 (1.2-1.5×8) no longer accommodates; K bumped to 10, target 12-15, landing 12-15 exactly.
- Per story-cycle-efficiency §1: "Coverage-gap tests that emerge from thinking through the AC matrix are added without count discipline — that's legitimate." The K-bump is coverage-grounded, not parametrization theater.

### Consensus summary (for any future reviewer)

The load-bearing finding was Q-1 (writer-identity fiction). Without it, 29-2's author picks one of three interpretations by accident for who calls `emit_fit_report`. All four panelists independently surfaced variants of the same concern (Winston at Rider 3, Murat implicit in M-4 negative test, Quinn explicit at Q-1). AC-B.5.1 + AC-T.11 pin the contract.

The other 11 riders are lower-stakes but individually APPLY-worthy. K-bump from 8 to 10 is the only governance-level change in the post-rider spec.

## Review Record

[Populated at post-dev review time — this is the single-gate post-dev Edge Case Hunter layer, separate from the Pre-Dev Review Record above.]

### Edge Case Hunter Pass

### Remediation Tally (APPLY / DEFER / DISMISS)

### Closure Note
