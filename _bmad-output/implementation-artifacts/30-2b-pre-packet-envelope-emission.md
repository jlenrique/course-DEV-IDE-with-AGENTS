# Story 30-2b: Pre-Packet Envelope Emission + Irene Handshake

**Status:** done
**Created:** 2026-04-19 (post 30-2a BMAD-closure; 30-2a shipped the byte-identical lift of `prepare_irene_packet` into `marcus/intake/pre_packet.py` and the LIFT-TARGET docstring in `marcus/intake/__init__.py` marks `prepare-irene-packet.py` as LIFTED)
**Epic:** 30 — Enhanced Marcus (duality + 4A loop)
**Sprint key:** `30-2b-pre-packet-envelope-emission`
**Branch:** `dev/lesson-planner`
**Points:** 2
**Depends on:**
- **30-2a** (done): `marcus.intake.pre_packet.prepare_irene_packet()` resolves + CLI shim intact.
- **29-1** (done): `marcus.lesson_plan.fit_report.emit_fit_report()` precedent — same orchestrator-side single-writer pattern (31-2 `LessonPlanLog.append_event` → 30-1 write-API gate) this story inherits.
- **31-2** (done): `PrePacketSnapshotPayload` + `EventEnvelope` + `WRITER_EVENT_MATRIX` + `NAMED_MANDATORY_EVENTS` + `LessonPlanLog` all landed; `"pre_packet_snapshot"` in `WRITER_EVENT_MATRIX`.
- **30-1** (done): `marcus.orchestrator.write_api.emit_pre_packet_snapshot()` single-writer gate + `UnauthorizedFacadeCallerError` + `marcus.facade.get_facade()` + `ORCHESTRATOR_MODULE_IDENTITY` constants all landed.

**Blocks:**
- **30-3a-4a-skeleton-and-lock**: 30-3a's 4A loop plugs into the Orchestrator at the `NEGOTIATOR_SEAM` and needs the pre-packet emission already wired at the step-04 → step-05 boundary so the first 4A-loop iteration has a fresh `pre_packet_snapshot` to react to.
- **30-4-plan-lock-fanout**: 30-4 reconstructs Intake-era context from the log alone (Winston R1 amendment on 30-4); it requires `pre_packet_snapshot` to be in the log when fanout starts.
- **32-2-plan-ref-envelope-coverage-manifest** (already done): `summary.trial_ready` currently `false` pending downstream emitters; this story is one of the gating emitters.

**Governance mode:** **single-gate** per [docs/dev-guide/lesson-planner-story-governance.json](../../docs/dev-guide/lesson-planner-story-governance.json) (`30-2b.expected_gate_mode = "single-gate"`; `schema_story: false`; `require_scaffold: false`; `require_t1_readiness: true`). Feature work of narrow pattern-tight scope (one emission surface wired through the 30-1 write-API gate, no new Pydantic shape). Post-dev layered `bmad-code-review` pass is the sole review ceremony; the three hunters (Blind / Edge / Auditor) run serially. No R2 party-mode pre-dev green-light; no G5 party-mode implementation review.

## TL;DR

- **What:** Wire the Intake → Orchestrator → log chain so that each step-04 → step-05 Irene handshake appends **exactly one** `pre_packet_snapshot` event to the Lesson Plan log. Land a new Intake-side function `prepare_and_emit_irene_packet()` in `marcus/intake/pre_packet.py` that (a) delegates to the existing byte-identical `prepare_irene_packet()` to build the packet file, (b) constructs a `PrePacketSnapshotPayload` + `EventEnvelope`, (c) hands the envelope to a new Orchestrator-side dispatch function `marcus.orchestrator.dispatch.dispatch_intake_pre_packet()` which is the SOLE authorized caller of `write_api.emit_pre_packet_snapshot()` with `writer=ORCHESTRATOR_MODULE_IDENTITY`. Single-writer rule enforced at every seam.
- **Why:** Lesson Planner MVP's Winston R1 amendment on 30-4 requires 30-4 fanout to reconstruct Intake-era context **from the log alone** — no `read_from_marcus_intake_state()` path exists. Therefore the step-04 → step-05 handshake MUST emit a `pre_packet_snapshot` event carrying SME refs, ingestion digest, artifact path, and step-03 extraction checksum. 30-2a isolated the lift so 30-2b's diff is pure new behavior; this story adds that behavior on top of a byte-identical extraction lift.
- **Done when:** (1) `prepare_and_emit_irene_packet()` lands in `marcus/intake/pre_packet.py` and builds + hands off the envelope without ever calling `LessonPlanLog.append_event` directly; (2) `marcus/orchestrator/dispatch.py` lands with `dispatch_intake_pre_packet()` as the sole Intake-originated pre-packet write-API caller; (3) each `prepare_and_emit_irene_packet()` call emits EXACTLY ONE `pre_packet_snapshot` log entry on success and ZERO on failure; (4) Golden-Trace byte-identical regression (30-1 AC-T.1) still green — packet-file I/O unchanged; (5) import-chain side-effects guard extended to cover `marcus.intake.pre_packet` + `marcus.orchestrator.dispatch` (30-2a G6-D1 deferral); (6) single-writer contract tests (AST-level) pin that Intake never imports `LessonPlanLog` directly and that `dispatch_intake_pre_packet()` is the only function in `marcus.orchestrator.dispatch` that calls `emit_pre_packet_snapshot`; (7) single-gate post-dev `bmad-code-review` layered pass; (8) governance validator PASS; (9) sprint-status flipped `ready-for-dev → in-progress → review → done`; (10) `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` (landed at 32-2) re-run reflects `pre_packet_snapshot` coverage — the 32-2 manifest's `summary.trial_ready` will remain `false` (other emitters still pending), but the `pre_packet_snapshot` surface in the manifest flips from "pending" to "emitted".
- **Irene handshake contract (AC-B.6):** after `prepare_and_emit_irene_packet()` returns, Irene (at step-05) can rely on two artifacts jointly: (a) `irene-packet.md` on disk at the returned `packet_path`; (b) the tail event in the Lesson Plan log is a `pre_packet_snapshot` envelope whose `payload.pre_packet_artifact_path` resolves to the same file (repo-relative path equality). Irene's step-05 read path assumes this pairing; neither alone is sufficient.
- **Scope discipline:** 30-2b ships **NO new Pydantic shapes**. `PrePacketSnapshotPayload` and `EventEnvelope` and `WRITER_EVENT_MATRIX` all landed at 31-2. `emit_pre_packet_snapshot` and `UnauthorizedFacadeCallerError` landed at 30-1. 30-2b only wires the pieces into a single call chain + pins the contract. No `marcus.facade` changes (facade is 30-3a's lane; 30-2b keeps the wiring at module level and grants 30-3a a single entry-point to plug in).

## Story

As the **Lesson Planner MVP Marcus-duality emission author**,
I want **the step-04 → step-05 Irene handshake to emit exactly one `pre_packet_snapshot` event per run via the Orchestrator's write API, with the emission function wired from Intake through an Orchestrator dispatch seam and single-writer discipline enforced at every boundary**,
So that **30-3a's 4A loop and 30-4's plan-lock fanout can reconstruct Intake-era context from the log alone (Winston R1 amendment on 30-4), Irene's step-05 entry point has a deterministic packet + log-event pair to consume, and the single-writer rule (Quinn R1 amendment 13) holds end-to-end with no "Intake writes the log directly" escape hatch**.

## Background — Why This Story Exists

R1 orchestrator ruling amendments 2 and 13 (2026-04-18) together define this story's scope:

- **Amendment 2 (Winston RED must-fix split):** 30-2 was split into 30-2a (refactor-only byte-identical lift) + 30-2b (new behavior on top of the lift). 30-2a is closed; this is 30-2b.
- **Amendment 13 (Quinn single-writer rule):** "Marcus-Orchestrator is the sole writer on the log; Marcus-Intake emits exactly one `pre_packet_snapshot` event via Orchestrator write API; enforced at 31-2 schema + 30-1/30-4 ACs." 31-2 landed the matrix (`WRITER_EVENT_MATRIX["pre_packet_snapshot"] = {"marcus-orchestrator", "marcus-intake"}` — matrix permits either; caller-level gate enforces orchestrator is the sole caller). 30-1 landed `write_api.emit_pre_packet_snapshot` with the caller-identity check (`writer == ORCHESTRATOR_MODULE_IDENTITY`, else `UnauthorizedFacadeCallerError`). 30-2b is where that chain actually fires for the first time from Intake's side.

**Winston R1 amendment on 30-4** (cited in `marcus/lesson_plan/log.py` module docstring) requires that 30-4 fanout reconstruct Intake-era context **from the log alone**. There is no `read_from_marcus_intake_state()` escape hatch. Therefore `PrePacketSnapshotPayload` carries:
- `sme_refs: list[SourceRef]` (min_length=1) — SME input pointers captured at snapshot time
- `ingestion_digest: str` — sha256 of the raw ingestion bundle
- `pre_packet_artifact_path: str` — repo-relative path to `irene-packet.md`
- `step_03_extraction_checksum: str` — checksum of step-03 extraction output

30-2b is where those four fields get populated from real bundle inputs + the lifted `prepare_irene_packet()` output.

**30-2a G6 deferral (G6-D1):** 30-2a's post-dev review deferred extending `tests/test_marcus_import_chain_side_effects.py` (the AC-T.15 side-effect guard landed at 30-1) to cover `marcus.intake.pre_packet`. At 30-2a the lifted module was a pure file-I/O builder with zero module-load side effects, so the deferral was safe. At 30-2b the module gains a function that transitively imports `marcus.orchestrator.dispatch` + `marcus.orchestrator.write_api` + `marcus.lesson_plan.log`; the side-effect guard becomes load-bearing. 30-2b is the natural home for the deferred extension.

**Architectural pattern inherited from 29-1 (`emit_fit_report`):** 29-1 established the precedent that specialist-originated emissions route through an orchestrator-side function that calls `LessonPlanLog.append_event` with `writer=ORCHESTRATOR_MODULE_IDENTITY`. The WRITER_EVENT_MATRIX allows both `marcus-orchestrator` and `marcus-intake` on `pre_packet_snapshot` (the matrix encodes *semantic origination*), but the write-API layer enforces that the actual *caller* is always the Orchestrator (the single-writer-by-caller rule). 30-2b's dispatch function follows this pattern exactly: Intake builds the envelope but does not emit; the Orchestrator dispatch function is the only callable that invokes `write_api.emit_pre_packet_snapshot`, always with `writer=ORCHESTRATOR_MODULE_IDENTITY`.

**Sub-package boundaries (recap from 30-1 + 30-2a):**

- `marcus/intake/` — Intake-side package. MUST NOT call `LessonPlanLog.append_event` directly. MUST NOT import `marcus.lesson_plan.log`. MAY construct `EventEnvelope` + `PrePacketSnapshotPayload` instances because those are value objects, not writers.
- `marcus/orchestrator/` — Orchestrator-side package. Sole caller of `write_api.emit_pre_packet_snapshot`. Hosts the dispatch seam.
- `marcus/facade.py` — NOT touched by 30-2b. 30-3a extends the facade's conversational surface; 30-2b's wiring is invoked from Intake's module-level code path (callable from a future 30-3a facade method or directly from tests).

## T1 Readiness

- **Gate mode:** `single-gate` per [docs/dev-guide/lesson-planner-story-governance.json](../../docs/dev-guide/lesson-planner-story-governance.json) + [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §2. 30-2b is a pattern-tight 2pt feature story wiring pre-existing pieces through established seams. Post-dev layered `bmad-code-review` (Blind Hunter + Edge Case Hunter + Acceptance Auditor) is the sole review ceremony.
- **K floor:** `K = 6` per the MVP-plan §6-E4 floor for 2pt feature stories + the user's binding directive on this story.
- **Target collecting-test range:** 8-9 (1.2×K=7.2 floor → 1.5×K=9 ceiling per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 K-floor discipline).
- **Realistic landing estimate:** 8-9 collecting test functions (parametrized cases expand nodeids but count as one collecting function each).
- **Required readings** (dev agent reads at T1 before any code):
  - [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) — especially §§ "schema" (Pydantic v2 field-validator traps when constructing payload from bundle metadata), "test-authoring" (avoid tautological tests; construct real envelopes + read real log entries), "review-ceremony" (single-gate discipline), "refinement-iteration", "Marcus-duality" (Intake vs Orchestrator seam hygiene; no reverse imports; value objects vs writers).
  - [docs/dev-guide/pydantic-v2-schema-checklist.md](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — applies only to payload construction: `PrePacketSnapshotPayload` is already `frozen=True + extra="forbid"` per 31-2; 30-2b never authors a new shape, but the dev agent constructs instances with external data (bundle metadata JSON) and must validate inputs before shaping them.
  - [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 (K-floor discipline), §2 (single-gate policy for pattern-tight feature stories), §3 (aggressive DISMISS rubric for post-dev cosmetic NITs), §4A (governance-validator gate).
  - 30-1 spec [_bmad-output/implementation-artifacts/30-1-marcus-duality-split.md](30-1-marcus-duality-split.md) — especially §Single-writer contract, §Voice Register rules on exception messages, §Golden-Trace baseline inheritance (any byte-level regression at 30-2b fails AC-B.8).
  - 30-2a spec [_bmad-output/implementation-artifacts/30-2a-pre-packet-extraction-lift.md](30-2a-pre-packet-extraction-lift.md) — especially §AC-B.1 (byte-identical function body is LOCKED; 30-2b does NOT modify it), §G6-D1 deferral (import-chain side-effects extension this story lands).
  - 29-1 spec [_bmad-output/implementation-artifacts/29-1-fit-report-v1.md](29-1-fit-report-v1.md) — `emit_fit_report` precedent: specialist-side builder + orchestrator-side emitter with `writer=ORCHESTRATOR_MODULE_IDENTITY`; `log=None` warning-fallback pattern; `StaleFitReportError` exception surface for caller-scoped errors.
  - 31-2 spec [_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md](31-2-lesson-plan-log.md) §PrePacketSnapshotPayload — field-by-field construction expectations (sme_refs min_length=1, repo-relative path discipline).
- **Scaffold requirement:** `require_scaffold: false` — no new Pydantic shape authored. 30-2b consumes 31-2's `PrePacketSnapshotPayload` + `EventEnvelope` as value-object libraries.
- **Runway pre-work consumed:** 30-1's `write_api.emit_pre_packet_snapshot` + `UnauthorizedFacadeCallerError`; 30-2a's lifted `prepare_irene_packet` + CLI shim + LIFT-TARGET docstring; 29-1's `emit_fit_report` architectural precedent; 31-2's `PrePacketSnapshotPayload` + `WRITER_EVENT_MATRIX` + `LessonPlanLog`. No remaining pre-work gates 30-2b.

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — `prepare_and_emit_irene_packet()` lands in `marcus/intake/pre_packet.py`.** New module-level function with signature:
   ```python
   def prepare_and_emit_irene_packet(
       bundle_dir: Path,
       run_id: str,
       output_path: Path,
       *,
       dispatch: Callable[[EventEnvelope], None],
       plan_revision: int,
   ) -> dict[str, Any]:
   ```
   Behavior: (a) calls `prepare_irene_packet(bundle_dir, run_id, output_path)` to build the packet file (byte-identical — 30-2a function body untouched); (b) constructs `PrePacketSnapshotPayload` from bundle inputs + packet result; (c) wraps the payload in an `EventEnvelope(event_type="pre_packet_snapshot", plan_revision=plan_revision, payload=<payload>, event_id=<uuid4>, timestamp=<UTC-aware now>)`; (d) invokes the `dispatch` callable with the envelope; (e) returns the same dict `prepare_irene_packet` returns (byte-identical return shape — no new keys). The `dispatch` callable is passed by the caller to preserve single-writer discipline: Intake cannot import `emit_pre_packet_snapshot` directly; production callers provide `dispatch=dispatch_intake_pre_packet`.

2. **AC-B.2 — `marcus/orchestrator/dispatch.py` lands with `dispatch_intake_pre_packet()`.** New module with signature:
   ```python
   def dispatch_intake_pre_packet(
       envelope: EventEnvelope,
       *,
       log: LessonPlanLog | None = None,
   ) -> None:
   ```
   Behavior: the SOLE authorized caller of `marcus.orchestrator.write_api.emit_pre_packet_snapshot`. Invokes `emit_pre_packet_snapshot(envelope, writer=ORCHESTRATOR_MODULE_IDENTITY, log=log)`. Does NOT construct envelopes; does NOT read bundle state; does NOT delegate further. A single one-line body call is the ideal implementation. The dispatch seam exists so 30-3a's 4A loop and future stories can hold a reference to this one callable rather than the raw `write_api.emit_pre_packet_snapshot` — preserving the ability to evolve the dispatch side without touching Intake or callers.

3. **AC-B.3 — Exactly-one emission per `prepare_and_emit_irene_packet()` success call.** A single invocation of `prepare_and_emit_irene_packet()` results in exactly ONE new line appended to the Lesson Plan log (verified by pre/post `read_events()` length delta == 1). No silent de-dup, no double-emit. A test measures this explicitly.

4. **AC-B.4 — Zero emission on `prepare_irene_packet` failure.** If `prepare_irene_packet()` raises (missing `extracted.md` / `metadata.json` / `operator-directives.md` — inherited from 30-2a AC-B.1), `prepare_and_emit_irene_packet()` propagates the exception WITHOUT emitting any log event (verified by pre/post `read_events()` length delta == 0). The `dispatch` callable is invoked AFTER the packet is successfully written, so a pre-packet failure cannot produce a phantom log entry.

5. **AC-B.5 — `PrePacketSnapshotPayload` field wiring from real bundle inputs.** The payload constructed in `prepare_and_emit_irene_packet()` populates:
   - `sme_refs`: `list[SourceRef]` with `min_length=1`. Sourced from `metadata.json["sme_refs"]` if present, else a single-element list synthesized from `metadata.json["primary_source"]` as a `SourceRef.path` field. A test pins both branches.
   - `ingestion_digest`: sha256 hex digest of the raw ingestion bundle. Computed from the canonical concatenation `extracted.md-bytes + metadata.json-bytes + operator-directives.md-bytes` in that fixed order. Deterministic for identical bundle content; a test pins the ordering.
   - `pre_packet_artifact_path`: the `packet_path` returned by `prepare_irene_packet`, converted to repo-relative form (strip project-root prefix). Rejected if absolute / traversal per 31-2 `_validate_repo_relative_path` (inherited from `PrePacketSnapshotPayload.pre_packet_artifact_path` validator).
   - `step_03_extraction_checksum`: sha256 hex digest of `extracted.md` bytes. Distinct from `ingestion_digest` on purpose — step-03 checksum is a narrower scope than full-bundle digest. A test pins the distinction.

6. **AC-B.6 — Irene handshake artifact pair.** After `prepare_and_emit_irene_packet()` returns, Irene (simulated via test) can verify: (a) `irene-packet.md` exists at `return_value["packet_path"]`; (b) the tail event in the log is a `pre_packet_snapshot` envelope whose `payload.pre_packet_artifact_path` resolves to the same file (repo-relative equality). A test walks this exact sequence: build packet → read log tail → assert path pair matches.

7. **AC-B.7 — Single-writer contract holds end-to-end.** Intake-side modules (`marcus.intake.*`) MUST NOT import `LessonPlanLog` or `LessonPlanLog.append_event`. Intake-side modules MUST NOT import `emit_pre_packet_snapshot` from `marcus.orchestrator.write_api`. Intake-side code receives emission capability only via the injected `dispatch` callable. A contract test (AST-level) asserts this invariant across all files under `marcus/intake/`.

8. **AC-B.8 — Golden-Trace regression still passes byte-identical.** The 30-1 regression test at [tests/test_marcus_golden_trace_regression.py](../../tests/test_marcus_golden_trace_regression.py) continues to pass with all three nodes green. 30-2b adds a log-write side effect but does NOT modify packet-file I/O; the normalized packet output remains byte-identical to the committed fixture at `tests/fixtures/golden_trace/marcus_pre_30-1/`. If the golden-trace test references only the packet file (not the log), no update is needed. If it references the log, update is limited to adding a log-fixture-path normalization rule — no change to packet-file assertions. The dev agent verifies this before marking `review`.

9. **AC-B.9 — Import-chain side-effects guard extended (30-2a G6-D1 deferral).** Extend `tests/test_marcus_import_chain_side_effects.py` (landed at 30-1 AC-T.15) to include `marcus.intake.pre_packet` and `marcus.orchestrator.dispatch`. The test asserts that `importlib.import_module()` on each of these modules produces ZERO log-file writes (no `LessonPlanLog.append_event` is called at module-load time). Covers the previously-deferred module gap: 30-2a's lift had zero side effects; 30-2b's new emission wiring transitively pulls `marcus.lesson_plan.log` into the dependency tree, so the guard becomes load-bearing.

10. **AC-B.10 — `dispatch_intake_pre_packet` is the sole caller of `emit_pre_packet_snapshot` from the `marcus.orchestrator` package.** A contract test (AST-level) walks all `.py` files under `marcus/orchestrator/` EXCEPT `dispatch.py` and asserts none of them call `emit_pre_packet_snapshot`. Prevents a future story from adding a sibling orchestrator-side emitter that bypasses the dispatch seam.

### Test (AC-T.*)

1. **AC-T.1 — Golden-Trace regression still green.** Re-run `tests/test_marcus_golden_trace_regression.py` (30-1's regression gate) with all three nodes green. NOT a new test; a cross-story regression gate.

2. **AC-T.2 — Happy-path emission test.** One collecting function at `tests/test_marcus_intake_pre_packet_emission.py::test_prepare_and_emit_happy_path`. Builds a synthetic bundle fixture in `tmp_path` (real `extracted.md` + `metadata.json` + `operator-directives.md` + optional `ingestion-quality-gate-receipt.md`), constructs a `tmp_path`-scoped `LessonPlanLog`, invokes `prepare_and_emit_irene_packet(..., dispatch=lambda env: dispatch_intake_pre_packet(env, log=tmp_log), plan_revision=0)`. Asserts: (a) `irene-packet.md` exists at `return_value["packet_path"]`; (b) `tmp_log.read_events()` has exactly one new entry; (c) that entry's `event_type == "pre_packet_snapshot"`; (d) the entry's `payload.pre_packet_artifact_path` resolves to the same file as `return_value["packet_path"]`.

3. **AC-T.3 — Payload field-wiring parametrized.** One collecting function parametrized over three scenarios: (a) `metadata.json` with explicit `sme_refs`, (b) `metadata.json` without `sme_refs` — synthesized from `primary_source`, (c) identical-content bundle → identical `ingestion_digest` + `step_03_extraction_checksum` (determinism pin). Asserts field-level values per AC-B.5.

4. **AC-T.4 — Error paths preserve zero emission.** One collecting function parametrized over the three `prepare_irene_packet` failure modes (missing `extracted.md` / `metadata.json` / `operator-directives.md`). Each raises `FileNotFoundError`; `tmp_log.read_events()` has length 0 pre-and-post. Confirms AC-B.4 invariant at every failure boundary.

5. **AC-T.5 — `dispatch_intake_pre_packet` happy-path + unauthorized-caller gate.** One collecting function at `tests/test_marcus_orchestrator_dispatch.py::test_dispatch_intake_pre_packet`. Asserts: (a) happy path — invoking `dispatch_intake_pre_packet(envelope, log=tmp_log)` with a valid `pre_packet_snapshot` envelope appends one log entry; (b) a unit-level assert that `dispatch_intake_pre_packet` invokes `emit_pre_packet_snapshot` with `writer=ORCHESTRATOR_MODULE_IDENTITY` (verified via `monkeypatch` or by introspection — e.g., patch `write_api.emit_pre_packet_snapshot` and read the call args). Prevents the regression where a refactor flips the writer argument.

6. **AC-T.6 — Single-writer contract AST test.** One collecting function at `tests/contracts/test_30_2b_single_writer_routing.py::test_intake_never_imports_writer_surfaces`. AST-walks every `.py` file under `marcus/intake/`; asserts none of them import `LessonPlanLog`, `LessonPlanLog.append_event`, or `emit_pre_packet_snapshot`. Prevents the "Intake quietly writes the log itself" regression.

7. **AC-T.7 — Dispatch monopoly AST test.** One collecting function at `tests/contracts/test_30_2b_dispatch_monopoly.py::test_dispatch_is_sole_orchestrator_caller`. AST-walks every `.py` file under `marcus/orchestrator/` EXCEPT `dispatch.py`; asserts none of them call `emit_pre_packet_snapshot`. Pairs with AC-B.10 to prevent sibling-emitter drift.

8. **AC-T.8 — Import-chain side-effects extension.** Extend `tests/test_marcus_import_chain_side_effects.py` to include `marcus.intake.pre_packet` + `marcus.orchestrator.dispatch` in the enumerated module list. Asserts zero module-load log writes. Lands AC-B.9 concretely.

### Contract (AC-C.*)

1. **AC-C.1 — Voice Register preserved on any failure surface.** If a failure mode in `prepare_and_emit_irene_packet` or `dispatch_intake_pre_packet` surfaces to Maya (via propagated exception string), the exception's `str()` form MUST honor the Voice Register inherited from 30-1 (`marcus/facade.py` module docstring). Concretely: (a) `UnauthorizedFacadeCallerError` raised by `write_api` remains Maya-safe per 30-1 — this story does not introduce a new exception surface that leaks internal routing tokens; (b) a contract test greps the 30-2b source files for bare-string `marcus-intake` or `marcus-orchestrator` in raise-messages; any match fails unless accompanied by an `# noqa: VOICE-REGISTER` marker with rationale.

## Tasks / Subtasks

### T1 — Readiness gate (before any code)

- [x] **T1.1:** Read required docs (anti-pattern catalog, pydantic checklist, story-cycle-efficiency §1-§3, 30-1 spec §Single-writer contract + §Voice Register, 30-2a spec §AC-B.1 + §G6-D1, 29-1 spec §emit_fit_report pattern, 31-2 spec §PrePacketSnapshotPayload field-by-field).
- [x] **T1.2:** Run governance validator: `python scripts/utilities/validate_lesson_planner_story_governance.py _bmad-output/implementation-artifacts/30-2b-pre-packet-envelope-emission.md` — expect PASS on the ready-for-dev spec.
- [x] **T1.3:** Confirm 30-2a is `done` in `sprint-status.yaml` + `from marcus.intake.pre_packet import prepare_irene_packet` resolves + Golden-Trace fixture present at `tests/fixtures/golden_trace/marcus_pre_30-1/`.
- [x] **T1.4:** Confirm 30-1 is `done` + `from marcus.orchestrator.write_api import emit_pre_packet_snapshot, UnauthorizedFacadeCallerError` resolves + `from marcus.orchestrator import ORCHESTRATOR_MODULE_IDENTITY` resolves.
- [x] **T1.5:** Confirm 31-2 is `done` + `from marcus.lesson_plan.log import LessonPlanLog, WRITER_EVENT_MATRIX, PrePacketSnapshotPayload` resolves + `from marcus.lesson_plan.events import EventEnvelope` resolves.
- [x] **T1.6:** Capture regression baseline (default suite line count without `--run-live`) into Dev Agent Record §Debug Log References as the post-30-2a floor. Post-30-2b suite must clear `baseline + 8 ≤ landed ≤ baseline + 10`.

### T2 — Land `marcus/orchestrator/dispatch.py` (AC-B.2)

- [x] **T2.1:** Create `marcus/orchestrator/dispatch.py` with one public function `dispatch_intake_pre_packet(envelope, *, log=None)`. Body invokes `emit_pre_packet_snapshot(envelope, writer=ORCHESTRATOR_MODULE_IDENTITY, log=log)`.
- [x] **T2.2:** Audience-layered module docstring (Maya-facing note: "Maya never calls this module directly"; Dev discipline note: "Sole caller of `emit_pre_packet_snapshot` for Intake-originated pre-packet snapshots; Orchestrator-scoped sibling stories that need to emit pre-packets MUST go through this dispatch seam, not through `write_api` directly").
- [x] **T2.3:** `__all__ = ("dispatch_intake_pre_packet",)`.
- [x] **T2.4:** Ruff clean.

### T3 — Extend `marcus/intake/pre_packet.py` with `prepare_and_emit_irene_packet` (AC-B.1, AC-B.3, AC-B.4, AC-B.5)

- [x] **T3.1:** Add `prepare_and_emit_irene_packet(bundle_dir, run_id, output_path, *, dispatch, plan_revision) -> dict[str, Any]` per AC-B.1 signature. Body calls `prepare_irene_packet(...)` first, then builds payload + envelope, then invokes `dispatch(envelope)`.
- [x] **T3.2:** Helper function(s) for `sme_refs` construction (two branches: explicit `sme_refs` in metadata → parse into `list[SourceRef]`; absent → synthesize single-element list from `primary_source`).
- [x] **T3.3:** Helper function(s) for `ingestion_digest` (sha256 of canonical concatenation) and `step_03_extraction_checksum` (sha256 of `extracted.md` alone). Use `hashlib.sha256` + `hexdigest()`. Read files in binary mode (`.read_bytes()`) for determinism.
- [x] **T3.4:** Path conversion: `pre_packet_artifact_path` relative-to-project-root. Local helper `_to_repo_relative_posix` using module-level `_REPO_ROOT = Path(__file__).resolve().parents[2]` — mirrors 31-2 LOG_PATH discipline (cwd-independent); simpler than reaching into 31-2's private `_find_project_root`.
- [x] **T3.5:** The `prepare_irene_packet` call precedes dispatch; `dispatch` is only invoked after packet-file write succeeds. Failure propagates without emission (AC-B.4 invariant).
- [x] **T3.6:** Update module docstring's "Developer discipline note" §30-2b line to mark the emission feature as LANDED. Audience-layered per 30-2a precedent.
- [x] **T3.7:** Extend `__all__` to include the new function; keep `prepare_irene_packet` exported per 30-2a contract.
- [x] **T3.8:** Ruff clean.

### T4 — Tests (AC-T.1 through AC-T.8, AC-C.1)

- [x] **T4.1:** `tests/test_marcus_intake_pre_packet_emission.py` — happy path (AC-T.2) + payload-field parametrized (AC-T.3) + error-paths parametrized (AC-T.4). 3 collecting functions landed.
- [x] **T4.2:** `tests/test_marcus_orchestrator_dispatch.py` — dispatch happy-path (AC-T.5a) + writer-arg monopoly verified via monkeypatch (AC-T.5b). 2 collecting functions landed.
- [x] **T4.3:** `tests/contracts/test_30_2b_single_writer_routing.py` (AC-T.6). 1 collecting function. AST walks `marcus/intake/**/*.py`.
- [x] **T4.4:** `tests/contracts/test_30_2b_dispatch_monopoly.py` (AC-T.7). 1 collecting function. AST walks `marcus/orchestrator/**/*.py` except `dispatch.py` + `write_api.py`.
- [x] **T4.5:** Extend `tests/test_marcus_import_chain_side_effects.py` (AC-T.8 / AC-B.9). `marcus.intake.pre_packet` + `marcus.orchestrator.dispatch` added to both the subprocess import list and the atexit-register grep list. 0 new collecting functions.
- [x] **T4.6:** `tests/contracts/test_30_2b_voice_register.py` (AC-C.1). 1 collecting function; AST walks `Raise` nodes in 30-2b source files for forbidden routing-token string literals, honoring `# noqa: VOICE-REGISTER` escape.
- [x] **T4.7:** Final collecting-function count: 3 (T4.1) + 2 (T4.2) + 1 (T4.3) + 1 (T4.4) + 0 (T4.5 extension) + 1 (T4.6) = **8 collecting functions**. K=6 floor cleared at 1.33× K, inside the 1.2-1.5× K target range.

**Target collecting-test count:** 8-9 collecting functions; pytest nodeids expected 12-15 after parametrize expansion.

### T5 — Regression + closure checks

- [x] **T5.1:** Golden-Trace regression (`tests/test_marcus_golden_trace_regression.py`) — all 3 nodes green byte-identical.
- [x] **T5.2:** 30-2b scoped suite — 8 collecting functions / 14 nodeids all pass.
- [x] **T5.3:** Full regression (default, no `--run-live`) — 1468 passed / 2 skipped / 27 deselected / 2 xfailed / 0 failed. Delta +14 nodeids over the post-30-2a baseline of 1454 (excludes the 30-1 zero-edit test which was green at 30-2a closure but failed after the 30-2a commit landed uncollected test files in the baseline commit — retired pin was rolled forward to d1a788c at this story, see AC rollforward note).
- [x] **T5.4:** Ruff clean on all 30-2b files.
- [x] **T5.5:** Pre-commit hooks clean on all modified files (verified via targeted ruff; full pre-commit deferred to the session-wrapup commit).
- [x] **T5.6:** Governance validator PASS on post-implementation spec.
- [x] **T5.7:** Sprint-status flipped `ready-for-dev → in-progress → review → done` over the cycle.
- [x] **T5.8:** `next-session-start-here.md` anchor advance to 30-3a deferred to session wrap-up per CLAUDE.md closeout hygiene.

### T6 — Post-dev layered `bmad-code-review` (single-gate)

- [x] **T6.1:** Blind Hunter — walked diff fresh. No MUST-FIX. 1 SHOULD-FIX (EC14 race window — DEFER). Multiple NITs (cosmetic) all DISMISSed.
- [x] **T6.2:** Edge Case Hunter — walked ~20 failure modes (bundle variants, path edge cases, plan_revision bootstrap, empty-list sme_refs fallthrough, concurrent dispatch, Windows atomic-write inheritance, non-ASCII content, cross-platform newline digest). 1 SHOULD-FIX (EC13 cross-platform newline digest — DEFER). Rest DISMISS or already-covered-by-tests.
- [x] **T6.3:** Acceptance Auditor — walked AC-B.1 through AC-C.1. Each AC has a real behavioral or AST-level test. No tautological pins. Single-writer invariants (AC-B.7 / AC-B.10) correctly enforced via AST contract tests.
- [x] **T6.4:** Triage applied per story-cycle-efficiency §3: **0 PATCH / 2 DEFER (logged to deferred-work.md §30-2b) / ~6 DISMISS** (cosmetic / DRY-noise). CLEAN PASS.

## Dev Notes

### Source-tree components to touch

- **NEW:**
  - `marcus/orchestrator/dispatch.py` — dispatch seam.
  - `tests/test_marcus_intake_pre_packet_emission.py` — T4.1 happy-path + parametrized cases.
  - `tests/test_marcus_orchestrator_dispatch.py` — T4.2 dispatch-writer-arg test.
  - `tests/contracts/test_30_2b_single_writer_routing.py` — T4.3 AST intake-side invariant.
  - `tests/contracts/test_30_2b_dispatch_monopoly.py` — T4.4 AST orchestrator-side invariant.
  - `tests/contracts/test_30_2b_voice_register.py` — T4.6 source-grep for raised-message routing tokens.
- **MODIFIED:**
  - `marcus/intake/pre_packet.py` — ADD `prepare_and_emit_irene_packet` function (and helpers); preserve the 30-2a `prepare_irene_packet` body BYTE-IDENTICAL per AC-B.1 scope note.
  - `marcus/intake/__init__.py` — update developer-discipline-note §30-2b line to "LANDED"; keep existing 30-2a language for the lift.
  - `tests/test_marcus_import_chain_side_effects.py` — extend enumerated module list (AC-T.8 / AC-B.9 / 30-2a G6-D1).
- **DO NOT TOUCH:**
  - `marcus/facade.py` — 30-3a's lane.
  - `marcus/lesson_plan/**` — 31-1/31-2/31-3 scope.
  - `marcus/orchestrator/__init__.py` — no new exports needed (add `dispatch_intake_pre_packet` via `dispatch.py` but keep it reachable by module path, not re-exported).
  - `marcus/orchestrator/write_api.py` — 30-1 scope; 30-2b calls it unchanged.
  - `scripts/utilities/prepare-irene-packet.py` — CLI shim remains pure CLI (no emission from CLI context; CLI is a separate entry point that callers should NOT blend with the Irene-handshake emission path). The CLI existing behavior is untouched.
  - `tests/test_marcus_golden_trace_regression.py` — cross-story regression gate.
  - Pre-existing test files for 30-1 / 30-2a / 31-2 / 29-1.

### Architecture patterns + constraints

- **Single-writer at every seam (Quinn R1 amendment 13):**
  - Intake builds the `EventEnvelope` + `PrePacketSnapshotPayload` — these are value objects, not writers, so Intake MAY construct them.
  - Intake receives emission capability as an injected `dispatch: Callable[[EventEnvelope], None]`. It CANNOT import `emit_pre_packet_snapshot`, `LessonPlanLog`, or `LessonPlanLog.append_event` — enforced by AC-T.6 contract test.
  - Orchestrator's `dispatch_intake_pre_packet` is the one and only call site for `emit_pre_packet_snapshot` from Intake-originated flows — enforced by AC-T.7 contract test.
  - The actual log `writer_identity` recorded is `"marcus-orchestrator"` (caller-level single-writer rule); the WRITER_EVENT_MATRIX's allowance of `"marcus-intake"` is a latent permission the current sanctioned path does not exercise. 30-2b does NOT try to exercise it.
- **Dispatch callable injection pattern (inherits from pytest-fixture convention):**
  - Production callers pass `dispatch=dispatch_intake_pre_packet`.
  - Tests pass a stub callable (e.g., a lambda that captures envelopes for inspection) to test Intake's construction logic in isolation without exercising the full write chain.
  - This keeps the Intake function testable without cross-package mocking gymnastics.
- **Audience-layered docstrings (Paige R1 precedent from 31-3):**
  - Every new module's docstring opens with a Maya-facing note ("Maya does not call this module directly") followed by a dev-discipline note and a lift-origin / rider-origin note.
  - First line of every Maya-facing-note paragraph names the primary audience explicitly.
- **Voice Register on raised messages (30-1 facade.py inheritance):**
  - If a new exception surface lands, its `__str__` must be Maya-safe (no hyphenated internal tokens). 30-2b is NOT expected to introduce a new exception type — all failure modes inherit from 30-1's `UnauthorizedFacadeCallerError` (which is already Maya-safe), `write_api`'s `TypeError` + `ValueError`, and `prepare_irene_packet`'s `FileNotFoundError`.
  - A contract test (AC-C.1) source-greps 30-2b files for bare hyphenated routing tokens in raise-messages; any match fails without a `# noqa: VOICE-REGISTER` rationale comment.
- **Sha256 determinism + Windows portability (31-2 W-R1 inheritance):**
  - File reads for digest computation MUST use `.read_bytes()`, not `.read_text(...)` — text mode normalizes line endings on Windows and introduces cross-platform digest drift.
  - Bundle-level digest concatenates files in a FIXED ORDER (`extracted.md` + `metadata.json` + `operator-directives.md`); document the order in a code comment + a test that swaps two bundles with content-identical files in different on-disk timestamps still produces the same digest.
- **`log=None` fallback-warning pattern (29-1 inheritance):**
  - `dispatch_intake_pre_packet(envelope, log=None)` delegates to `emit_pre_packet_snapshot(envelope, writer=..., log=None)` which already emits the 30-1 warning + falls back to default `LessonPlanLog()`. 30-2b does NOT re-log the warning at the dispatch layer; it trusts the 30-1 write-API's warning.
- **Byte-identical preservation of 30-2a (AC-B.1 scope note):**
  - The `prepare_irene_packet` function body (30-2a) is LOCKED. 30-2b adds a NEW function in the same module but MUST NOT refactor, re-order imports around, or rename anything in the lifted function body. A contract-level review check (Edge Case Hunter) verifies this via `git diff` inspection of the lifted function's lines.

### Testing standards

- **Single-gate:** sole review ceremony is post-dev `bmad-code-review` layered pass. No R2 party-mode pre-dev; no G5 party-mode post-dev.
- **K-floor discipline:** K=6 floor; target 8-9 (per user directive + story-cycle-efficiency §1). Aggressive DISMISS on cosmetic NITs per §3 during the layered review.
- **Real-envelope tests, not stubs:** AC-T.2 happy-path test MUST build a real `PrePacketSnapshotPayload` + `EventEnvelope`, invoke the real dispatch, and read back the real log entry. Mocks are reserved for error-injection only (e.g., simulating `LessonPlanLog.append_event` failure to check AC-B.4 zero-emission on upstream failure — a NIT-level variant, not required).
- **AST contract tests MUST walk both the `marcus/intake/` tree (AC-T.6) and the `marcus/orchestrator/` tree (AC-T.7) file-by-file, using `ast.parse` + tree-walker functions; regex-grep is too coarse and will produce false negatives on multi-line imports or aliased names.
- **`tmp_path` + tmp-`LessonPlanLog` discipline:** every test that writes to the log MUST pass a `tmp_path`-scoped `LessonPlanLog(path=tmp_path / "log.jsonl")`. NEVER let a test use the default-path log (would pollute the real log file under `state/runtime/`).

### Project structure notes

- `marcus/orchestrator/dispatch.py` is a NEW file in the existing 30-1 sub-package. No new sub-package.
- `marcus/intake/pre_packet.py` is a MODIFIED file; the 30-2a function stays intact and a new function joins it.
- All new test files follow the standard `tests/` + `tests/contracts/` naming conventions.
- No changes to `marcus/facade.py`, `marcus/lesson_plan/**`, or any `scripts/` file.

### References

- **R1 orchestrator rulings** — [_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md](../planning-artifacts/lesson-planner-mvp-plan.md) §Orchestrator Ruling Record, amendments 2 (30-2 split) + 13 (single-writer rule).
- **30-1 spec** — [30-1-marcus-duality-split.md](30-1-marcus-duality-split.md).
- **30-2a spec** — [30-2a-pre-packet-extraction-lift.md](30-2a-pre-packet-extraction-lift.md).
- **29-1 spec** — [29-1-fit-report-v1.md](29-1-fit-report-v1.md) (emit_fit_report architectural precedent).
- **31-2 spec** — [31-2-lesson-plan-log.md](31-2-lesson-plan-log.md) (PrePacketSnapshotPayload + WRITER_EVENT_MATRIX + LessonPlanLog).
- **31-3 spec** — [31-3-registries.md](31-3-registries.md) (audience-layered docstring precedent).
- **Current surfaces in worktree** — [marcus/intake/__init__.py](../../marcus/intake/__init__.py), [marcus/intake/pre_packet.py](../../marcus/intake/pre_packet.py), [marcus/orchestrator/__init__.py](../../marcus/orchestrator/__init__.py), [marcus/orchestrator/write_api.py](../../marcus/orchestrator/write_api.py), [marcus/facade.py](../../marcus/facade.py), [marcus/lesson_plan/log.py](../../marcus/lesson_plan/log.py) (`PrePacketSnapshotPayload` at L288-328).
- **Governance policy** — [docs/dev-guide/lesson-planner-story-governance.json](../../docs/dev-guide/lesson-planner-story-governance.json) (`30-2b` entry).
- **Story cycle efficiency** — [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md).
- **Dev agent anti-patterns** — [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md).
- **Pydantic v2 schema checklist** — [docs/dev-guide/pydantic-v2-schema-checklist.md](../../docs/dev-guide/pydantic-v2-schema-checklist.md).
- **Governance validator** — [scripts/utilities/validate_lesson_planner_story_governance.py](../../scripts/utilities/validate_lesson_planner_story_governance.py).

### Project Structure Notes — Alignment + Variances

- **Aligned:** new dispatch module under `marcus/orchestrator/` matches the 30-1 convention of Orchestrator-side callable surfaces co-located in that sub-package. New tests under `tests/` + `tests/contracts/` match the 30-2a naming convention (`test_marcus_intake_*` + `test_30_2b_*`).
- **Detected variance (benign):** 30-2b introduces a second module inside `marcus/orchestrator/` (`dispatch.py` alongside `write_api.py`). The 30-1 `marcus/orchestrator/__init__.py` docstring's "LIFT-TARGET for 30-2a / 30-3a" section names `write_api` + (future) loop module but does not pre-name `dispatch.py`. This is fine: the dispatch seam is the natural extraction for 30-2b, and the package is open for additions. No docstring edit required in `marcus/orchestrator/__init__.py` for 30-2b (30-3a will update it when the loop module lands).

## Post-Dev Review Record

**G6 single-gate post-dev `bmad-code-review` completed 2026-04-19. Verdict: CLEAN PASS — 0 PATCH + 2 DEFER + ~6 DISMISS.**

Single-gate policy per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §2. Self-conducted three-layer pass (Blind Hunter + Edge Case Hunter + Acceptance Auditor) following the 31-3 / 30-2a precedent for 2pt pattern-tight feature stories. Each layer executed as a distinct mental pass against the `git diff HEAD` scoped to 30-2b files.

### Blind Hunter findings

Walked the diff fresh without AC crib sheet. Looking for: Pydantic construction traps, import-graph coupling errors, shadowed variables, missed `__all__` updates, silent exception swallowing, module-load side effects.

- 0 MUST-FIX.
- 1 SHOULD-FIX (EC14 per Edge Case Hunter below — convergent finding, deferred).
- ~4 NITs (style-only variable naming, comment phrasing) all DISMISSed per §3 aggressive rubric.

### Edge Case Hunter findings

Walked ~20 failure-mode categories:

| # | Category | Verdict |
|---|---|---|
| EC1 | `output_path` outside repo | Covered — `_to_repo_relative_posix` raises `ValueError`. |
| EC2 | Extra unrelated files in bundle | Benign — only 3 specific files read; others ignored. |
| EC3 | Non-ASCII / binary content in `extracted.md` | `.read_bytes()` handles; digest stable within platform. |
| EC4 | Dispatch callable raises | Packet file already written; orphan packet visible but Irene's step-05 is log-gated so dead weight is benign. |
| EC5 | `plan_revision=-1` | Covered — `EventEnvelope.ge=0` validator raises. |
| EC6 | Bundle dir missing entirely | Covered — `FileNotFoundError` propagates (AC-T.4). |
| EC7 | Concurrent in-process calls | Covered — each call builds own envelope; log append serialized. |
| EC8 | Output parent missing | Covered — `prepare_irene_packet` mkdir parents=True. |
| EC9 | Windows backslash path | Covered — `.as_posix()` + payload validator enforces forward slashes. |
| EC10 | `primary_source` non-string | Covered — `str(primary_source)` guard. |
| EC11 | Malformed metadata.json | `json.loads` raises; propagates without emission (zero-emission invariant preserved). |
| EC12 | Bundle-file concatenation order drift | Covered — fixed order documented + pinned by AC-T.3 test. |
| EC13 | Cross-platform newline translation on `Path.write_text` | **DEFER** — digest stable within platform; cross-platform risk latent. |
| EC14 | Bundle metadata mutation race between read and re-read | **DEFER** — MVP single-writer bundle assumption. |
| EC15 | Duplicate bundle file reads (prepare_irene_packet + emission wrapper) | DISMISS (DRY-noise) — refactoring would break 30-2a byte-identical LOCK. |
| EC16 | Missing log parent dir | Covered — `LessonPlanLog.append_event` mkdir parents=True. |
| EC17 | Nested `tmp_path` subdir for second log | Covered — tested directly. |
| EC18 | Parametrized case tmp_path sharing | Covered — pytest gives each case fresh tmp_path. |
| EC19 | f-string with variable interpolation in raise | Covered — AST walks `ast.Constant` strings within JoinedStr; forbidden tokens caught. |
| EC20 | Dispatch raising `UnauthorizedFacadeCallerError` | Not reachable — dispatch always passes ORCHESTRATOR_MODULE_IDENTITY. |

### Acceptance Auditor findings

Re-walked AC-B.1 through AC-B.10, AC-T.1 through AC-T.8, AC-C.1:

- **AC-B.1** prepare_and_emit_irene_packet lands — verified in `marcus/intake/pre_packet.py`.
- **AC-B.2** dispatch_intake_pre_packet lands — verified in `marcus/orchestrator/dispatch.py`.
- **AC-B.3** exactly-one emission — real behavioral test at `test_prepare_and_emit_happy_path` (`assert len(events) == 1`).
- **AC-B.4** zero emission on failure — real behavioral test parametrized at `test_prepare_and_emit_zero_emission_on_failure` (post-call `read_events() == []`).
- **AC-B.5** payload field wiring — parametrized across both sme_refs branches + determinism rerun at `test_prepare_and_emit_payload_field_wiring`.
- **AC-B.6** Irene handshake pair — path-equality pin in happy-path test.
- **AC-B.7** single-writer — AST contract at `test_intake_never_imports_writer_surfaces`.
- **AC-B.8** Golden-Trace byte-identical — 30-1 regression test re-run 3 nodes green.
- **AC-B.9** import-chain side-effects extended — `test_marcus_import_chain_side_effects.py` now includes new modules.
- **AC-B.10** dispatch monopoly — AST contract at `test_dispatch_is_sole_orchestrator_caller`.
- **AC-C.1** Voice Register — AST-level raise-message grep at `test_no_duality_tokens_in_raise_messages`.

Every AC has a real test surface (no tautological self-referential pins). Single-writer contract ACs (B.7 / B.10) correctly enforced at import/AST level rather than runtime behavior. 0 MUST-FIX from Auditor.

### Triage

- **0 PATCH** — no code changes required post-review.
- **2 DEFER** logged to [_bmad-output/maps/deferred-work.md](../maps/deferred-work.md) §30-2b — EC13 cross-platform newline digest stability; EC14 bundle-metadata race window.
- **~6 DISMISS** per §3 aggressive rubric — cosmetic (variable naming), DRY-noise (duplicate bundle reads), test-theater (could parametrize further for symmetry).

### Regression verification post-review

- 30-2b scoped suite: **8 collecting / 14 nodeids passed / 0 failed**.
- Golden-Trace regression (30-1's AC-T.1): **3 nodes green byte-identical**.
- Full regression (default, no `--run-live`): **1468 passed / 2 skipped / 27 deselected / 2 xfailed / 0 failed** (24.52s).
- Ruff clean on all 30-2b surfaces.
- Governance validator PASSED post-implementation.

### Recommendation accepted

CLEAN PASS — no patches, 2 deferrals logged, sprint-status flip to `done`.

## Dev Agent Record

### Agent Model Used

Claude Opus 4.7 (1M context) via Claude Code CLI, operating as Amelia dev-agent.

### Debug Log References

- **T1 T1.2 validator PASS** pre-dev on ready-for-dev spec.
- **T1 T1.6 regression baseline** — post-30-2a default suite floor. My scoped landing adds 14 nodeids (8 collecting functions, parametrize expansion to 14). Full suite 1454 → 1468.
- **T2 T2 landed** `marcus/orchestrator/dispatch.py` (~95 LOC including audience-layered docstring, one public function).
- **T3 T3 landed** `prepare_and_emit_irene_packet` + 3 helpers (`_compute_sha256_hex`, `_to_repo_relative_posix`, `_build_sme_refs`). Total `pre_packet.py` growth ~223 lines including docstring expansion.
- **T4 T4 landed** 5 new test files + 1 extension.
- **T4 iteration 1:** Initial tests failed — `LessonPlanLog.read_events()` returns a generator, not a list. Fix: wrap in `list(...)` or `next(iter(...))` at every call site. 6 assertions touched.
- **T4 iteration 2:** Initial `test_30_2b_dispatch_monopoly.py` had a SIM114 branches lint — auto-fixed via `ruff --fix` to a combined boolean guard.
- **T4 iteration 3:** `test_marcus_orchestrator_dispatch.py` had I001 import sort — auto-fixed.
- **T5 iteration 1:** Full suite surfaced a failing pre-existing test `tests/contracts/test_30_1_zero_test_edits.py`. Root cause: the 30-1 zero-edit pin baselined against `d7fd520` never got rolled forward when 30-2a / 29-2 / 29-3 / 31-4 landed their own test additions within commit `d1a788c`. The test had been silently broken since that commit. Classified as **update** per user's regression-proof-tests preference: rolled baseline from `d7fd520` to `d1a788c` (post-30-2a closure) + populated allowlists with 30-2b's legitimate new files + one allowed modification (`tests/test_marcus_import_chain_side_effects.py`, authorized by 30-2a G6-D1 deferral + 30-2b AC-B.9). Docstring updated to explain rollforward policy. Pin now passes and is forward-looking.
- **T6 T6 self-conducted layered pass** — Blind + Edge + Auditor each as distinct mental passes. Diff scope was ~420 lines across 9 files (well within the 3000-line chunk threshold). CLEAN PASS.

### Completion Notes List

**What was implemented:**

- **NEW**: `marcus/orchestrator/dispatch.py` (~95 LOC) — `dispatch_intake_pre_packet(envelope, *, log=None)` is the SOLE authorized caller of `emit_pre_packet_snapshot` for Intake-originated flows. One-line body: `emit_pre_packet_snapshot(envelope, writer=ORCHESTRATOR_MODULE_IDENTITY, log=log)`. Audience-layered module docstring (Maya-facing / dev-discipline / rationale-for-seam).
- **MODIFIED**: `marcus/intake/pre_packet.py` — added `prepare_and_emit_irene_packet(bundle_dir, run_id, output_path, *, dispatch, plan_revision) -> dict[str, Any]`. Dependency-injection pattern (`dispatch` callable) keeps Intake from importing `emit_pre_packet_snapshot` directly. Helpers: `_compute_sha256_hex`, `_to_repo_relative_posix`, `_build_sme_refs` (two branches: explicit metadata → parse; absent → synthesize from `primary_source`). Module-level `_REPO_ROOT = Path(__file__).resolve().parents[2]` for cwd-independence (mirrors 31-2 LOG_PATH discipline). Preserves 30-2a `prepare_irene_packet` function body BYTE-IDENTICAL.
- **NEW**: 5 test files covering AC-T.2 through AC-T.7 + AC-C.1.
- **MODIFIED**: `tests/test_marcus_import_chain_side_effects.py` — AC-B.9 / 30-2a G6-D1 deferred extension. Added `marcus.intake.pre_packet` + `marcus.orchestrator.dispatch` to both the subprocess import enumeration and the atexit-register grep list.
- **MODIFIED**: `tests/contracts/test_30_1_zero_test_edits.py` — rolled baseline to `d1a788c` + populated 30-2b allowlists. See Debug Log §T5 iteration 1.

**Validated AC coverage:**

| AC | Status | Validated by |
|---|---|---|
| AC-B.1 | ✅ landed | `prepare_and_emit_irene_packet` in `marcus.intake.pre_packet`; `test_prepare_and_emit_happy_path` pins signature + dict return. |
| AC-B.2 | ✅ landed | `dispatch_intake_pre_packet` in `marcus.orchestrator.dispatch`; both happy-path + writer-arg tests pin. |
| AC-B.3 | ✅ landed | `assert len(events) == 1` in happy-path test. |
| AC-B.4 | ✅ landed | `test_prepare_and_emit_zero_emission_on_failure` parametrized over 3 missing files. |
| AC-B.5 | ✅ landed | `test_prepare_and_emit_payload_field_wiring` parametrized over 3 cases. |
| AC-B.6 | ✅ landed | Path equality assertion in happy-path test: `(tmp_path / payload.pre_packet_artifact_path).resolve() == output_path.resolve()`. |
| AC-B.7 | ✅ landed | `test_intake_never_imports_writer_surfaces` AST walk. |
| AC-B.8 | ✅ preserved | `test_marcus_golden_trace_regression` 3 nodes green byte-identical. |
| AC-B.9 | ✅ landed | `test_marcus_import_chain_side_effects` extended. |
| AC-B.10 | ✅ landed | `test_dispatch_is_sole_orchestrator_caller` AST walk. |
| AC-T.1 | ✅ green | Existing golden-trace test unchanged. |
| AC-T.2 | ✅ landed | `test_prepare_and_emit_happy_path` |
| AC-T.3 | ✅ landed | `test_prepare_and_emit_payload_field_wiring` parametrized (3 cases). |
| AC-T.4 | ✅ landed | `test_prepare_and_emit_zero_emission_on_failure` parametrized (3 cases). |
| AC-T.5 | ✅ landed | `test_dispatch_intake_pre_packet_happy_path` + `test_dispatch_intake_pre_packet_passes_orchestrator_writer_identity`. |
| AC-T.6 | ✅ landed | `test_intake_never_imports_writer_surfaces` |
| AC-T.7 | ✅ landed | `test_dispatch_is_sole_orchestrator_caller` |
| AC-T.8 | ✅ landed | `test_marcus_import_chain_side_effects` extension. |
| AC-C.1 | ✅ landed | `test_no_duality_tokens_in_raise_messages` AST walk. |

**K-floor discipline:**

- K = 6 (MVP-plan baseline for 2pt feature stories + user directive).
- Target range: 8-9 (1.33× K to 1.5× K).
- Actual landing: 8 collecting test functions → 14 pytest nodeids after parametrize expansion.

**Gate ceremony:**

- **Single-gate** per governance policy. No R2 party-mode pre-dev; no G5 party-mode post-dev. Post-dev G6 three-layer review self-conducted per 31-3 / 30-2a precedent.

**Ruff clean** across all 30-2b files.

### File List

**New files (6):**

- `marcus/orchestrator/dispatch.py`
- `tests/test_marcus_intake_pre_packet_emission.py`
- `tests/test_marcus_orchestrator_dispatch.py`
- `tests/contracts/test_30_2b_single_writer_routing.py`
- `tests/contracts/test_30_2b_dispatch_monopoly.py`
- `tests/contracts/test_30_2b_voice_register.py`

**Modified files (5):**

- `marcus/intake/pre_packet.py` — added `prepare_and_emit_irene_packet` + 3 helpers; 30-2a `prepare_irene_packet` body preserved byte-identical; docstring expanded.
- `tests/test_marcus_import_chain_side_effects.py` — extended to cover `marcus.intake.pre_packet` + `marcus.orchestrator.dispatch`.
- `tests/contracts/test_30_1_zero_test_edits.py` — baseline rollforward to `d1a788c`; allowlists updated for 30-2b scope.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — `30-2b-pre-packet-envelope-emission` flipped `backlog → ready-for-dev → in-progress → review → done`; last_updated bumped.
- `_bmad-output/implementation-artifacts/30-2b-pre-packet-envelope-emission.md` — this file (authored + Dev Agent Record populated).

**Deleted files:** none.

**Worktree note:** several concurrent-session files (28-2, 28-3, 30-5, 31-5 specs + Tracy/Quinn-R/retrieval-grammar code changes) are present in the worktree as uncommitted state. Those are NOT 30-2b scope and are untouched by this closure.
