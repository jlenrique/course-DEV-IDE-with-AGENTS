# Story 31-2: Lesson Plan Log — Append-Only JSONL + Monotonic Revision + Staleness Detector + Single-Writer Enforcement

**Status:** review (R2 party-mode GREEN + G5 party-mode GREEN + G6 bmad-code-review layered pass + 19 patches applied 2026-04-18; operator flips to `done` after sprint-status.yaml flip)
**Created:** 2026-04-18 (authored by Amelia post-31-1 closeout; inherits R1 ruling amendments 8, 13 + Quinn Q-4 R2 carry-forward + Winston R1 amendment on 30-4)
**Epic:** 31 — Tri-phasic contract primitives + gates (FOUNDATION)
**Sprint key:** `31-2-lesson-plan-log`
**Branch:** `dev/lesson-planner`
**Points:** 3
**Depends on:** **31-1 (done — commit `15f68b1`)** — imports `LessonPlan`, `PlanUnit`, `EventEnvelope`, `ScopeDecisionTransition`, `compute_digest`, `event_type_registry.*`, `StaleRevisionError` from `marcus/lesson_plan/`.
**Blocks:** **30-1** (Marcus duality split — Orchestrator write API consumer), **30-4** (plan-lock fanout reads Intake-era context ONLY from append-only log per Winston R1 amendment), **32-2** (envelope plan-ref coverage-manifest audit — audit logic lives in 31-2 log per R1 amendment 14).

---

## Mid-Flight Memo — Post-31-1 dev-guide references (ADDED 2026-04-18)

This story was authored before the following references landed in-repo. **Dev agent and G5/G6 reviewers MUST consult them; they distill the six MUST-FIX findings and 11+ R2 riders from 31-1 into ready-to-apply idioms.**

- [`docs/dev-guide/pydantic-v2-schema-checklist.md`](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — 14 Pydantic-v2 idioms. 31-2's new payload models (`PrePacketSnapshotPayload`, `PlanLockedPayload`, `SourceRef`) MUST adopt: `ConfigDict(extra="forbid", validate_assignment=True)`, tz-aware-datetime validator on any timestamp field, `Field(exclude=True) + SkipJsonSchema` for any internal-audit fields, no `min_length` on free-text, `additionalProperties: false` in emitted JSON Schema if any schemas are published from 31-2.
- [`docs/dev-guide/dev-agent-anti-patterns.md`](../../docs/dev-guide/dev-agent-anti-patterns.md) — A1-A6 / B1-B6 / E1-E3 categories. Particularly relevant to 31-2: A1 silent-mutation (log append path must re-validate envelopes on rebind), B3 no-mocking-the-thing-tested (use real `tmp_path` + real JSONL writes, not mocked file handles — already aligned in AC-C.4 / Testing standards), B4 per-family shape pins (AC-T.1 already per-family — good), B6 boundary-value testing for numeric validators (revision=0 bootstrap, revision=MAX_INT), E1-E3 no intake/orchestrator leak in user-facing strings (33 call-sites to scan in 31-2's new module).
- [`docs/dev-guide/story-cycle-efficiency.md`](../../docs/dev-guide/story-cycle-efficiency.md) — 31-2 is classified **dual-gate** (foundation: single-writer invariant is new architecture). Full R2 + G5 + G6 cycle applies, not compressed. §1 K-floor discipline: **K=15 is the floor; target 18–23 collecting tests (1.2×–1.5× K). 25–40 is acceptable only if every extra test names a specific coverage gap.** §3 aggressive-DISMISS rubric applies at G6.
- [`docs/dev-guide/scaffolds/schema-story/`](../../docs/dev-guide/scaffolds/schema-story/) — schema-shape scaffold. **Not directly applicable to 31-2** (31-2 is a write-path/log module, not a Pydantic-model-family story), but the scaffold's `test_no_intake_orchestrator_leak.py.tmpl` and `test_json_schema_parity.py.tmpl` ARE reference shapes for 31-2's AC-T.1 pin — consult before authoring.

**Integration guidance for dev agent (if 31-2 is already mid-flight):** do NOT re-scope. Layer the checklist + anti-patterns reading onto the current T-task sequence as an extra review pass before G5 submission. If any of the 14 Pydantic-v2 idioms is absent from the drafted `log.py`, fix in-place as part of the same PR — do not carve a follow-up.

**Reviewer guidance:** at G5 party-mode, add one checklist item: "Drafted module adheres to `pydantic-v2-schema-checklist.md` §1, §2, §5, §6, §14; `dev-agent-anti-patterns.md` A1, B3, B4, B6, E1-E3 scanned and clear." This is an ADDITIVE gate on top of the Quinn Q-4 amendment 13 gate already in §Pre-Development Gate PDG-1.

---

## TL;DR

- **What:** The `marcus/lesson_plan/log.py` module — append-only JSONL log at a canonical runtime path, the `LessonPlanLog.append_event(envelope, writer_identity)` write API with **single-writer enforcement** (R1 ruling amendment 13), the `LessonPlanLog.read_events(...)` read API (filter by revision and event_type), the `assert_plan_fresh(envelope)` staleness detector (revision + digest match), monotonic-revision enforcement on `plan.locked`, and the `pre_packet_snapshot` payload shape-pin (sufficient for 30-4 fanout to reconstruct Intake-era context WITHOUT touching Marcus-Intake in-memory state per Winston R1 amendment).
- **Why:** 31-1 shipped the SHAPE; 31-2 is the WRITE-PATH. Every downstream envelope 05→13 carries `{lesson_plan_revision, lesson_plan_digest}` (32-2 enforces coverage); every envelope uses `assert_plan_fresh` to detect stale-plan drift; Marcus-Orchestrator is SOLE writer per Quinn's tri-phasic contract discipline (ruling amendment 13); 30-4 fanout depends on the log being the ONLY source of truth for Intake-era context (Winston R1 amendment on 30-4).
- **Absorption note:** 31-2 takes on **R1 amendment 8 named mandatory events** (`plan_unit.created` / `scope_decision.set` / `scope_decision_transition` / `plan.locked` / `fanout.envelope.emitted` / `pre_packet_snapshot`) AND **R1 amendment 13 single-writer rule** AND **Winston R1 amendment on 30-4** (`pre_packet_snapshot.payload` carries enough to reconstruct Intake-era context from the log alone). 31-1 pre-registered these event_types as RESERVED; 31-2 is the story that actually emits + reads + staleness-checks.
- **Done when:** `marcus/lesson_plan/log.py` landed + `LessonPlanLog` + `WriterIdentity` + `StalePlanRefError` + `NAMED_MANDATORY_EVENTS` + `pre_packet_snapshot` payload shape + `tests_added ≥ 15` + party-mode R2 green-light (with Quinn Q-4 checklist item explicitly referencing amendment 13) + `bmad-code-review` layered pass + `sprint-status.yaml` flipped `ready-for-dev → in-progress → review → done`.

## Story

As the **Lesson Planner MVP write-path author**,
I want **the `LessonPlanLog` append-only JSONL log + single-writer-enforced write API + monotonic-revision guard + staleness detector + `pre_packet_snapshot` payload shape landed as one reviewable PR on top of the 31-1 schema foundation**,
So that **Marcus-Orchestrator has exactly one enforceable write path for every named mandatory Lesson Plan event, 30-4 fanout can reconstruct Intake-era context from the log alone (Winston R1 amendment), every envelope 05→13 can call `assert_plan_fresh(envelope)` for drift detection, and 32-2's plan-ref coverage manifest has a trustworthy audit substrate**.

## Background — Why This Story Exists

31-1 (done, commit `15f68b1`) shipped the `marcus/lesson_plan/` shape foundation: Pydantic models, the `EventEnvelope` generic envelope (R2 rider W-1), the `ScopeDecisionTransition` first concrete payload, the `compute_digest` canonical-JSON helper, and the `event_type_registry` with `RESERVED_LOG_EVENT_TYPES` pre-registering the six mandatory log event_types. 31-1 did NOT implement the write-path; ruling amendment 13 (Quinn single-writer rule) and ruling amendment 8 (named mandatory events) were explicitly deferred to 31-2.

Three binding carry-forwards from the R1/R2 rulings land in 31-2:

1. **R1 ruling amendment 8 — Named mandatory log events.** Six event_types pre-registered in `event_type_registry.RESERVED_LOG_EVENT_TYPES`: `plan_unit.created`, `scope_decision.set` (initial proposal), `scope_decision_transition` (shape already pinned in 31-1 AC-B.5), `plan.locked`, `fanout.envelope.emitted`, `pre_packet_snapshot`. 31-2 is the story that emits + consumes them.

2. **R1 ruling amendment 13 — Single-writer rule (Quinn).** Marcus-Orchestrator is the SOLE writer to the Lesson Plan log. Marcus-Intake emits exactly ONE event (`pre_packet_snapshot`) at 4A entry via the Orchestrator's write API — the API itself is the enforcement point. Enforced at the schema level (WriterIdentity enum) AND at runtime (write API validates caller identity; only the declared writer may invoke it for event types not in the Intake-permitted set).

3. **Winston R1 ruling amendment on 30-4.** 30-4 reads Intake-era context ONLY from the append-only log, NOT in-memory. Therefore 31-2's `pre_packet_snapshot.payload` MUST carry enough information that 30-4 can reconstruct fanout context without ever touching Marcus-Intake state. Payload shape is named explicitly in AC-B.7.

**Quinn Q-4 R2 carry-forward (BINDING Pre-Development Gate).** The R2 party-mode green-light checklist for 31-2 MUST explicitly surface R1 ruling amendment 13 as a binding AC. If the green-light panel does not surface the single-writer rule as an explicit checklist item, 31-2 is NOT authorized to enter `bmad-dev-story`. See §Pre-Development Gate.

**Murat R1 binding PDG forward-ref.** 31-2 is upstream of 29-2 (gagne-diagnostician p95 + fallback), 30-1 (duality split + golden-trace), and 30-4 (fanout). The §6 Readiness PDG (5x-flake + p95≤30s + diagnosis-stability + per-story `tests_added ≥ K` floor) sits downstream of 31-2's write-path + staleness detection. 31-2 must not undermine it — no `xfail`, no `skip`, no `live_api`, no `trial_critical`, per `feedback_regression_proof_tests.md`.

## Pre-Development Gate (Quinn Q-4 BINDING)

31-2 cannot enter `bmad-dev-story` until BOTH gates cleared:

- [x] **PDG-1 (Quinn Q-4 BINDING) — CLEARED 2026-04-18.** R2 party-mode green-light checklist for 31-2 explicitly references **R1 ruling amendment 13 (single-writer rule)** as a binding AC item. Checklist entry reads: "Marcus-Orchestrator is sole writer to the Lesson Plan log; Marcus-Intake's `pre_packet_snapshot` emission goes through the Orchestrator's write API. The API is the enforcement point. Enforced at schema layer (WriterIdentity) AND runtime (append_event caller check)." Triple-surfaced per AC-C.6 + AC-T.3 CENTRAL parametrized test.
- [x] **PDG-2 — CLEARED.** 31-1 closed `done` with the `RESERVED_LOG_EVENT_TYPES` frozenset containing all six named mandatory events. Confirmed: commit `15f68b1`, `marcus/lesson_plan/event_type_registry.py::RESERVED_LOG_EVENT_TYPES`.

## Acceptance Criteria

### Behavioral / Write-Path (AC-B.*)

1. **AC-B.1 — Append-only JSONL log at canonical path.** Log lives at `state/runtime/lesson_plan_log.jsonl` (follows existing `state/runtime/*.json` convention established by Epic 25+ — see `state/runtime/run_baton.C1-M1-PRES-20260406.json` and `state/runtime/mode_state.json`). File path is exposed as module constant `LOG_PATH` in `marcus/lesson_plan/log.py`; tests override via monkeypatch or a context-manager fixture. Writes are APPEND-ONLY; no in-place edits; no delete; no compaction in 31-2. Prior-art pattern: `_append_jsonl()` in `skills/bmad-agent-marcus/scripts/run-interstitial-redispatch.py` (lines 82–86) — one line of canonical JSON per event followed by `"\n"`. 31-2's `append_event` SHALL match that line-shape but wraps it in atomic-write semantics per AC-B.9.

2. **AC-B.2 — `LessonPlanLog.append_event(envelope, writer_identity)` write API.** Signature:
   ```python
   def append_event(
       self,
       envelope: EventEnvelope,
       writer_identity: WriterIdentity,
   ) -> None
   ```
   Validates in this order:
   - (a) `envelope` is a valid `EventEnvelope` (Pydantic `model_validate`).
   - (b) `envelope.event_type` is in `NAMED_MANDATORY_EVENTS` (see AC-B.8). Unknown event_types are REJECTED at write time (not warned) — 31-2 is stricter than 31-1's `validate_event_type` warn-only behavior because the log is a governance artifact, not an extensibility surface.
   - (c) `writer_identity` is permitted to write `envelope.event_type` per the single-writer matrix in AC-B.3. Rejection raises `UnauthorizedWriterError` (subclass of `PermissionError`) with explicit message naming `(writer_identity, event_type)` pair.
   - (d) For `envelope.event_type == "plan.locked"`: envelope's `plan_revision` MUST be strictly greater than `self.latest_plan_revision()` (AC-B.6). Stale revision raises `StaleRevisionError` (imported from `marcus/lesson_plan/schema.py`; reused, not redefined).
   - On success: writes one canonical-JSON line to `LOG_PATH` atomically (AC-B.9). No partial writes.

3. **AC-B.3 — `WriterIdentity` single-writer matrix (R1 amendment 13).** `WriterIdentity` is `Literal["marcus-orchestrator", "marcus-intake"]` (NO other values; widening requires ruling amendment + AC-C.5 schema version bump). Enforcement matrix:

   | Event Type | `marcus-orchestrator` | `marcus-intake` |
   |---|---|---|
   | `plan_unit.created` | ACCEPT | REJECT |
   | `scope_decision.set` | ACCEPT | REJECT |
   | `scope_decision_transition` | ACCEPT | REJECT |
   | `plan.locked` | ACCEPT | REJECT |
   | `fanout.envelope.emitted` | ACCEPT | REJECT |
   | `pre_packet_snapshot` | ACCEPT (proxy case) | ACCEPT (via Orchestrator API) |

   The `pre_packet_snapshot` row is the SOLE case where `marcus-intake` may successfully invoke `append_event`. Per amendment 13, Marcus-Intake does NOT hold a direct file handle — it calls `append_event(envelope, writer_identity="marcus-intake")` on an instance of `LessonPlanLog` owned by the Orchestrator; the API is the enforcement point. This distinction is test-enforced via AC-T.3.

4. **AC-B.4 — `LessonPlanLog.read_events(...)` read API.** Signature:
   ```python
   def read_events(
       self,
       since_revision: int | None = None,
       event_types: set[str] | None = None,
   ) -> Iterator[EventEnvelope]
   ```
   - Returns an iterator (not a list) to keep the read path stream-friendly.
   - Non-mutating: reading never writes or modifies the log file.
   - `since_revision=None` returns ALL events; `since_revision=N` returns events where `envelope.plan_revision >= N`.
   - `event_types=None` returns ALL event_types; `event_types={"plan.locked"}` filters to the requested set.
   - Ordering: events are returned in insertion order (file-offset order). Stable across reads.
   - Each yielded `EventEnvelope` is a freshly-constructed Pydantic instance; mutating it does not affect the log. Tests assert no-mutation-leak (AC-T.8).

5. **AC-B.5 — `assert_plan_fresh(envelope: DownstreamEnvelope) -> None` staleness detector.** Module-level function in `marcus/lesson_plan/log.py` (NOT a method on `LessonPlanLog`, so callers do not need to hold a log instance — they can call via `from marcus.lesson_plan.log import assert_plan_fresh`). Contract:
   - Input: any envelope carrying the plan-ref shape `{lesson_plan_revision: int, lesson_plan_digest: str}`. At MVP this is duck-typed (the envelope class need only expose those two fields); 32-2's coverage manifest pins the field shape across all envelope types 05→13.
   - Reads the current log via a default `LessonPlanLog()` instance; test override via fixture.
   - Raises `StalePlanRefError` (NEW exception, subclass of `ValueError`) when EITHER:
     - `envelope.lesson_plan_revision != log.latest_plan_revision()`, OR
     - `envelope.lesson_plan_digest != log.latest_plan_digest()`.
   - Explicit error message names the mismatch: `"plan staleness detected: envelope revision={env_rev} digest={env_digest}, log latest revision={log_rev} digest={log_digest}"`.
   - Called by every envelope 05→13 before downstream processing; if the log has advanced past what the envelope carries, the envelope is stale and must be refreshed.

6. **AC-B.6 — Monotonic revision enforcement on `plan.locked` (SCOPE: `plan.locked` ONLY — M-2).** When writing a `plan.locked` event, the log asserts `envelope.plan_revision > self.latest_plan_revision()`. `latest_plan_revision()` reads the most-recent `plan.locked` event's `plan_revision` from the log; returns `0` if no `plan.locked` event exists yet (bootstrap case — revision numbering starts at 1 for the first lock). Stale revision raises `StaleRevisionError` (reused from `marcus/lesson_plan/schema.py`; do NOT redefine). Digest-drift sibling check (Quinn §6-B2 failure fixture): if operator reverts a dial back to prior value and attempts re-lock at the same revision, reject with `StaleRevisionError`. The log is strictly monotonic for `plan.locked` — no idempotent-relock, no double-log. (§6-B2 specifies one of {idempotent, double-log}; 31-2 pins the strict-monotonic choice; this is documented in AC-C.7.)

   **Monotonic revision gate applies ONLY to `plan.locked` events (M-2 — Murat R2 rider).** Non-`plan.locked` events at stale revision are LEGAL (interleaved writes ordering). For example, a `scope_decision_transition` event may arrive with `plan_revision=5` after the log has already written `plan.locked` at `plan_revision=7` — this is ACCEPTED because non-`plan.locked` events reflect historical audit context at their respective revisions. The monotonic gate is surgical, not universal; a future "fix" tightening this check to all events would BREAK legitimate interleave semantics and is explicitly forbidden.

7. **AC-B.7 — `pre_packet_snapshot` payload shape (Winston R1 amendment on 30-4).** `pre_packet_snapshot` payload MUST contain ALL of:
   ```yaml
   sme_refs: list[SourceRef]                # SME input pointers at Intake-era snapshot time
   ingestion_digest: str                    # sha256 of the raw ingestion bundle
   pre_packet_artifact_path: str            # filesystem path to the pre-packet artifact (relative to repo root)
   step_03_extraction_checksum: str         # checksum of step-03 extraction output
   ```
   Pinned as a Pydantic model `PrePacketSnapshotPayload` in `marcus/lesson_plan/log.py` (kept in the log module, not `schema.py`, because the payload is write-path specific and has no consumer outside the log ecosystem — 30-4 consumes via `read_events`). Shape-pin test AC-T.6. **Intent (Winston):** 30-4 fanout MUST reconstruct Intake-era context from `read_events(event_types={"pre_packet_snapshot"})` ALONE, without ever touching Marcus-Intake in-memory state. No alternative path. `SourceRef` is a new Pydantic model: `{source_id: str, path: str | None, content_digest: str}`; placed in `marcus/lesson_plan/log.py` since it is the first point of use. If 30-4 or a downstream story needs to reuse `SourceRef`, the model migrates to `schema.py` at that time via a minor schema bump (SCHEMA_CHANGELOG entry); 31-2 ships the shape at its first-use site.

8. **AC-B.8 — `NAMED_MANDATORY_EVENTS` module-level frozenset.** Exactly:
   ```python
   NAMED_MANDATORY_EVENTS: frozenset[str] = frozenset({
       "plan_unit.created",
       "scope_decision.set",
       "scope_decision_transition",
       "plan.locked",
       "fanout.envelope.emitted",
       "pre_packet_snapshot",
   })
   ```
   Set MUST equal `RESERVED_LOG_EVENT_TYPES` from `marcus/lesson_plan/event_type_registry.py` (AC-T.7 asserts equality). 31-2 imports `RESERVED_LOG_EVENT_TYPES` and redefines `NAMED_MANDATORY_EVENTS` as an ALIAS (`NAMED_MANDATORY_EVENTS = RESERVED_LOG_EVENT_TYPES`) to prevent drift — single source of truth, two naming surfaces.

9. **AC-B.9 — Atomic write semantics.** `append_event` writes are atomic at the line level: a crash mid-write must not leave a partial JSON line in the log. Implementation: open file with `"a"` mode; serialize the complete line (JSON + `"\n"`) to an in-memory buffer; call `file.write(buffer)` + `file.flush()` + `os.fsync(file.fileno())` under a single context-managed `open()`. Platform caveat documented in module docstring: on POSIX, `write` of a buffer < `PIPE_BUF` (4096 bytes typically) is atomic; on Windows (NTFS), atomicity is not guaranteed at OS level but is sufficient for single-process single-writer semantics (which is the explicit assumption of 31-2 — multi-process multi-writer is OUT-OF-SCOPE per AC-C.7). Test AC-T.9 simulates a crash mid-write on POSIX; on Windows, the test is XFAIL-on-platform (NOT xfail on the suite — see Murat note below).

   **Murat note on Windows-xfail:** Per `feedback_regression_proof_tests.md` (no xfail discipline), the crash test is NOT conditionally xfailed on the default suite. Instead: the test asserts the write-flush-fsync sequence via a spy on `os.fsync` + `file.flush`; actual crash simulation is platform-gated via `pytest.skipif(sys.platform == "win32", reason="POSIX fsync atomicity; Windows NTFS sufficient for single-process")` and the Windows path is covered by a separate assertion that the write-flush-fsync call sequence occurred (spy-based). This keeps the suite xfail-free while honoring platform reality.

10. **AC-B.10 — `LessonPlanLog.latest_plan_digest()` helper.** Returns the digest from the most-recent `plan.locked` event's envelope payload (envelope payload for `plan.locked` MUST carry `{lesson_plan_digest: str}` — shape-pinned in AC-B.11). Returns `""` (empty string sentinel, explicit in docstring) if no `plan.locked` event exists yet. Used by `assert_plan_fresh` for digest-match check.

11. **AC-B.11 — `plan.locked` envelope payload shape pin.** `plan.locked` envelopes MUST carry payload:
    ```yaml
    lesson_plan_digest: str     # sha256 from compute_digest(LessonPlan)
    ```
    Pinned as `PlanLockedPayload` Pydantic model in `marcus/lesson_plan/log.py`. This is the payload that `latest_plan_digest()` reads. The `lesson_plan_revision` lives on the envelope itself (already in `EventEnvelope.plan_revision` per 31-1 AC-B.5a); the digest lives in the payload because it is event-specific, not envelope-generic.

### Test (AC-T.*)

1. **AC-T.1 — Schema-pin contract test for log surface.** `tests/contracts/test_lesson_plan_log_shape_stable.py` pins `LessonPlanLog`, `WriterIdentity`, `StalePlanRefError`, `UnauthorizedWriterError`, `NAMED_MANDATORY_EVENTS`, `PrePacketSnapshotPayload`, `PlanLockedPayload`, `SourceRef`, `LOG_PATH` module constant via snapshot + allowlist + CHANGELOG gate pattern (inherited from 27-0 / 31-1 AC-T.1). Any change without CHANGELOG entry → test fails. Blocking at merge.

2. **AC-T.2 — Append-only enforcement.** `tests/test_log_append_only.py`: after N events written, reading the log returns N events in insertion order; attempting to call any in-place edit or delete operation via the public API is impossible (no such method exists) — test asserts `hasattr(LessonPlanLog, "delete") is False`, `hasattr(LessonPlanLog, "update_event") is False`, `hasattr(LessonPlanLog, "overwrite") is False`. Also asserts that calling `append_event` with the same `event_id` TWICE produces TWO log lines (the log does not dedupe; each append is a physically distinct line). Dedup semantics are out-of-scope for MVP.

3. **AC-T.3 — Single-writer matrix (R1 amendment 13 CENTRAL test).** `tests/test_log_single_writer_matrix.py` with `pytest.mark.parametrize` over the full `(writer_identity, event_type)` Cartesian product (2 × 6 = 12 cases). Each case asserts accept-or-reject per the AC-B.3 matrix. REJECT cases assert `UnauthorizedWriterError` is raised with message containing both the `writer_identity` and `event_type` values. ACCEPT cases assert the event lands in the log (read-back verification). This is the test that surfaces amendment 13 directly.

4. **AC-T.4 — `assert_plan_fresh` 2×2 staleness matrix (M-1 — Murat R2 rider).** `tests/test_lesson_plan_log_staleness.py` parametrized explicitly as a 2×2 `(rev_match, digest_match)` matrix:
   - **Cell 1** — `(rev_match=True, digest_match=True)` → `assert_plan_fresh` passes, no raise.
   - **Cell 2** — `(rev_match=True, digest_match=False)` → raises `StalePlanRefError` with message naming **digest** as the mismatch axis (must not name revision as a mismatch when only digest diverges).
   - **Cell 3** — `(rev_match=False, digest_match=True)` → raises `StalePlanRefError` with message naming **revision** as the mismatch axis (must not name digest as a mismatch when only revision diverges).
   - **Cell 4** — `(rev_match=False, digest_match=False)` → raises `StalePlanRefError` with message naming **both** axes.

   The `StalePlanRefError` message MUST distinguish which axis (or both) triggered the raise. Example message for Cell 4: `"StalePlanRefError: revision mismatch (envelope=5, log=7); digest mismatch (envelope='abc', log='def')"` — naming each failing axis explicitly, or naming one axis when only one fails. Shape-pin test asserts message-substring membership per cell.

   Additional edges (retained from original AC-T.4):
   - Envelope against empty log (no `plan.locked` yet) → `StalePlanRefError` (any envelope claiming revision ≥ 1 against empty log is stale — documented semantics).
   - Envelope against empty log where envelope claims revision 0 and digest `""` → no raise (bootstrap case). Documented in `assert_plan_fresh` docstring.

5. **AC-T.5 — Monotonic revision on `plan.locked` (+ M-2 non-plan.locked stale-revision ACCEPTED).** `tests/test_lesson_plan_log_monotonic.py`:
   - Write `plan.locked` rev=1 → accept.
   - Write `plan.locked` rev=2 → accept.
   - Write `plan.locked` rev=2 again (same rev) → `StaleRevisionError`.
   - Write `plan.locked` rev=1 after rev=2 (regression) → `StaleRevisionError`.
   - Non-`plan.locked` events at any revision bypass the monotonic check (only `plan.locked` gates revision; `scope_decision_transition` / `plan_unit.created` etc. can interleave at intermediate revisions).
   - **M-2 POSITIVE TEST (Murat R2 rider):** with `log.latest_plan_revision()=7` already established, append a `scope_decision_transition` event with `plan_revision=5` → **ACCEPTED** (no raise; event lands in log; interleave is legal). This test prevents a future "fix" from tightening the monotonic check to all events, which would silently break interleave semantics. Explicit comment: "non-plan.locked events at stale revision are LEGAL per AC-B.6 M-2 scope."

6. **AC-T.6 — `pre_packet_snapshot` payload shape-pin.** `tests/contracts/test_pre_packet_snapshot_payload_shape.py` pins the `PrePacketSnapshotPayload` Pydantic model + `SourceRef`: all four required fields present, types correct, missing any required field → `pydantic.ValidationError`. Snapshot + allowlist + CHANGELOG gate. (Winston R1 amendment surface — if any field drifts, 30-4 cannot reconstruct Intake-era context from the log alone.)

7. **AC-T.7 — `NAMED_MANDATORY_EVENTS` ↔ `RESERVED_LOG_EVENT_TYPES` parity (+ M-3 frozenset immutability).** `tests/test_lesson_plan_log_named_events.py` asserts `NAMED_MANDATORY_EVENTS == RESERVED_LOG_EVENT_TYPES` (set equality). Any drift between 31-1's registry and 31-2's write-time gate fails the test. Also asserts attempting to `append_event` with an `event_type` NOT in `NAMED_MANDATORY_EVENTS` raises `ValueError` with explicit message (e.g. `"event_type 'arbitrary.extra' not in NAMED_MANDATORY_EVENTS; log is a governance artifact — extend RESERVED_LOG_EVENT_TYPES via schema version bump"`).

   **M-3 (Murat R2 rider) frozenset immutability assertion.** `NAMED_MANDATORY_EVENTS.add("custom-event")` MUST raise `AttributeError` (frozensets have no `add` method) — confirms the set is truly frozen and cannot be mutated at runtime. Similarly `NAMED_MANDATORY_EVENTS.remove(...)` raises `AttributeError`. This prevents a future code-path from side-effectfully extending the set without a SCHEMA_CHANGELOG bump.

8. **AC-T.8 — Read API filter + ordering + no-mutation-leak.** `tests/test_log_read_api.py`:
   - Write mixed event_types at varying revisions → `read_events()` returns all in insertion order.
   - `read_events(since_revision=3)` returns only revisions ≥ 3.
   - `read_events(event_types={"plan.locked"})` returns only `plan.locked` events.
   - Combined filter `read_events(since_revision=3, event_types={"scope_decision_transition"})` composes.
   - Mutate a yielded envelope (e.g. `envelope.plan_revision = 999`) → subsequent `read_events()` call returns the unmutated original. (No state leak between iterations.)

9. **AC-T.9 — Atomic write test.** `tests/test_log_atomic_write.py`:
   - POSIX: write buffer < 4096 bytes, assert `os.fsync` is called after `file.write` (spy-based). Simulated crash before fsync → next reader sees no partial line (or the complete line if write flushed). No half-JSON.
   - Windows: `pytest.skipif(sys.platform == "win32")` on the crash-simulation assertion; write-flush-fsync call sequence is verified via spy on all platforms. NOT an xfail (per Murat note in AC-B.9).

10. **AC-T.10 — Suite-level gate (non-collecting AC; M-4 baseline rebase).** Baseline at commit `15f68b1` HEAD (verified 2026-04-18 R2 orchestrator pytest run):
    - `--run-live` full suite: **1023 passed / 3 skipped / 2 deselected / 2 xfailed / 0 failed**
    - Default (no `--run-live`): **1001 passed / 27 deselected / 2 xfailed / 0 failed**

    Expected after 31-2 with K ≥ 17 landing (M-5 bumped floor; realistic 25–40):
    - `--run-live` ≥ **1040 passed**
    - Default ≥ **1018 passed**

    No new `xfail`, no new `skip` (excepting the platform-gate `skipif` on the POSIX-only crash assertion, which is a conditional-skip-at-collect-time and is exempt per Murat standing practice for platform-gated tests — see Testing standards below), no new `live_api`, no new `trial_critical`.

    **Prior spec text (deprecated — supplanted by M-4):** "Baseline from 31-1 closeout: 1346 passed / 2 skipped / 27 deselected / 2 xfailed / 0 failed" — that was an earlier pre-G6 Amelia report and did NOT reflect the commit `15f68b1` HEAD baseline. The numbers above are authoritative.

11. **AC-T.11 — Re-read-after-write consistency (M-5 — Murat R2 rider).** `tests/test_lesson_plan_log_staleness.py::test_re_read_after_write_consistency` asserts: after `log.append_event(e, writer_identity)`, an IMMEDIATE subsequent `log.read_events()` call yields `e` in its iteration. No write-buffer lag; no OS buffering surprise. Covers regression risk if dev-agent forgets `fsync` or uses unbuffered `open(..., "a")` naively (where write-side OS buffering could mask a not-yet-persisted line from an immediate reader). Bumps the K floor from 15 → **17**.

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Foundation lives at `marcus/lesson_plan/log.py`.** New module under the existing `marcus/lesson_plan/` package established by 31-1. Imports from `schema.py`, `events.py`, `digest.py`, `event_type_registry.py` — does NOT re-shape any of them. Extends `marcus/lesson_plan/__init__.py::__all__` to export: `LessonPlanLog`, `WriterIdentity`, `StalePlanRefError`, `UnauthorizedWriterError`, `assert_plan_fresh`, `NAMED_MANDATORY_EVENTS`, `PrePacketSnapshotPayload`, `PlanLockedPayload`, `SourceRef`, `LOG_PATH`.

2. **AC-C.2 — Uses existing `EventEnvelope` from 31-1.** No re-shape. The log accepts/emits the `EventEnvelope` shape pinned in 31-1 AC-B.5a with all validators intact (`event_id` UUID4, `timestamp` tz-aware, `plan_revision ≥ 0`, `event_type` open-id regex).

3. **AC-C.3 — `SCHEMA_CHANGELOG.md` updated.** Extend `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` with a new entry: `## Lesson Plan Log v1.0 — 2026-04-18 — Story 31-2 Lesson Plan Log`. Entry documents: append-only JSONL write-path, `WriterIdentity` enum, single-writer matrix, `NAMED_MANDATORY_EVENTS`, `PrePacketSnapshotPayload` + `PlanLockedPayload` + `SourceRef` shapes, `assert_plan_fresh` contract, monotonic-revision strict semantics (§6-B2 strict-monotonic pin). **Migration: N/A** (initial shape; no predecessor log file exists — `state/runtime/lesson_plan_log.jsonl` is created by first `append_event` call).

4. **AC-C.4 — `LOG_PATH` configurable.** `LOG_PATH: Path = Path("state/runtime/lesson_plan_log.jsonl")` module-level constant. Tests override via a pytest fixture that monkeypatches the module attribute OR constructs `LessonPlanLog(path=tmp_path / "log.jsonl")` if the class accepts an explicit path argument. Implementation choice: `LessonPlanLog.__init__(path: Path | None = None)` with `path = path or LOG_PATH`. Tests use the per-test `tmp_path` fixture — never the real canonical path — so test runs do NOT pollute the runtime log.

5. **AC-C.5 — `WriterIdentity` closed set.** `Literal["marcus-orchestrator", "marcus-intake"]`. Widening requires (a) R1/R2-equivalent ruling amendment, (b) SCHEMA_CHANGELOG major-version bump (v1.0 → v2.0), (c) explicit migration-path AC on whatever story proposes the widening. No backdoor.

6. **AC-C.6 — R1 ruling amendment 13 single-writer enforcement — triple-surfaced.** (a) Schema layer: `WriterIdentity` Literal closed set + the AC-B.3 matrix encoded as a `dict[str, frozenset[WriterIdentity]]` module-level constant; (b) Runtime layer: `append_event` checks the matrix + raises `UnauthorizedWriterError`; (c) Test layer: AC-T.3 parametrizes over the 12-case matrix and asserts each accept/reject. **Green-light checklist surface** (Quinn Q-4): the R2 party-mode checklist MUST include an explicit checklist item referencing amendment 13 — see §Pre-Development Gate PDG-1.

7. **AC-C.7 — Out-of-scope for 31-2.** Explicitly: (a) no log compaction; (b) no log rotation; (c) no external observers (pub-sub, filesystem watchers); (d) no multi-process writer coordination — 31-2 is explicit single-process single-writer (documented in module docstring + README if Paige requests); (e) no dedup on duplicate `event_id` (dedup is out-of-scope — two identical events produce two log lines; 32-2 coverage manifest or a future story handles dedup if needed); (f) no idempotent-relock (§6-B2 strict-monotonic pin); (g) no backward-compatibility path to pre-31-2 state (there is no v0; this is the first log).

8. **AC-C.8 — Blocking rule for downstream.** 30-1 / 30-4 / 32-2 MUST consume the log via the public `LessonPlanLog.read_events` API. Direct `open(LOG_PATH)` reads in downstream code are a code-review-block (enforced by `bmad-code-review` layered pass + dev-note anti-pattern list). This ensures the log contract surface is the read API, not the file format.

## File Impact (preliminary — refined at bmad-dev-story)

| File | Change | Lines (est.) |
|------|--------|-------|
| `marcus/lesson_plan/log.py` | **New** — `LessonPlanLog` + `WriterIdentity` + `StalePlanRefError` + `UnauthorizedWriterError` + `assert_plan_fresh` + `NAMED_MANDATORY_EVENTS` + `PrePacketSnapshotPayload` + `PlanLockedPayload` + `SourceRef` + `LOG_PATH` + single-writer matrix constant | +240 |
| `marcus/lesson_plan/__init__.py` | **Touch** — extend `__all__` and imports (10 new names) | +15 |
| `tests/contracts/test_lesson_plan_log_shape_stable.py` | **New** — AC-T.1 log-surface shape pin | +110 |
| `tests/contracts/test_pre_packet_snapshot_payload_shape.py` | **New** — AC-T.6 pre_packet_snapshot + SourceRef pin | +70 |
| `tests/contracts/test_named_mandatory_events_parity.py` | **New** — AC-T.7 parity with 31-1 RESERVED_LOG_EVENT_TYPES | +40 |
| `tests/test_log_append_only.py` | **New** — AC-T.2 append-only + no-mutation-methods | +60 |
| `tests/test_log_single_writer_matrix.py` | **New** — AC-T.3 amendment 13 CENTRAL (parametrized 12 cases) | +120 |
| `tests/test_assert_plan_fresh.py` | **New** — AC-T.4 staleness detector positive + negative | +90 |
| `tests/test_log_monotonic_revision.py` | **New** — AC-T.5 monotonic revision + stale-revision rejection | +80 |
| `tests/test_log_read_api.py` | **New** — AC-T.8 filter + ordering + no-mutation-leak | +90 |
| `tests/test_log_atomic_write.py` | **New** — AC-T.9 atomic write + platform gate | +90 |
| `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` | **Touch** — Lesson Plan Log v1.0 entry | +30 |

**File count:** 1 new module + 1 touched `__init__.py` + 9 new test files + 1 touched SCHEMA_CHANGELOG entry. Target module LOC ~240; target total test LOC ~750.

## Tasks / Subtasks (preliminary — refined at bmad-dev-story)

- [x] T1 — R2 party-mode green-light complete 2026-04-18. Verdict: **GREEN conditional on 7 riders** (Winston W-R1 docstring caveat; Quinn Q-R2-R1 writer_identity anti-pattern; Murat M-1 2×2 staleness matrix; M-2 non-plan.locked stale ACCEPTED; M-3 frozenset immutability; M-4 baseline rebase 1023/1001; M-5 re-read-after-write + K 15→17; Paige nit deferred). All 7 riders applied 2026-04-18. See §R2 Green-Light Record.
- [x] T2 — `marcus/lesson_plan/log.py` skeleton landed: `LOG_PATH` constant, `WriterIdentity` Literal, `StalePlanRefError`, `UnauthorizedWriterError`, `NAMED_MANDATORY_EVENTS` alias, `WRITER_EVENT_MATRIX` constant.
- [x] T3 — `SourceRef`, `PrePacketSnapshotPayload`, `PlanLockedPayload` Pydantic models landed in `log.py` (AC-B.7, AC-B.11).
- [x] T4 — `LessonPlanLog` class landed: `__init__(path)`, `append_event`, `read_events`, `latest_plan_revision`, `latest_plan_digest`, `path` property.
- [x] T5 — `assert_plan_fresh` module-level function landed with R2 M-1 axis-named message format (AC-B.5).
- [x] T6 — Atomic-write path: `open("a") + write + flush + os.fsync` + platform caveat docstring per AC-B.9 + W-R1.
- [x] T7 — `marcus/lesson_plan/__init__.py::__all__` extended with 11 new names (LOG_PATH, LessonPlanLog, NAMED_MANDATORY_EVENTS, PlanLockedPayload, PrePacketSnapshotPayload, SourceRef, StalePlanRefError, UnauthorizedWriterError, WRITER_EVENT_MATRIX, WriterIdentity, assert_plan_fresh).
- [x] T8 — AC-T.1 schema-pin contract test landed (`tests/contracts/test_lesson_plan_log_shape_stable.py`, 15 tests).
- [x] T9 — AC-T.2 append-only test landed (`tests/test_lesson_plan_log_append_only.py`, 4 tests).
- [x] T10 — AC-T.3 single-writer matrix parametrized test landed (`tests/test_lesson_plan_log_single_writer.py`, 14 tests including 12 parametrized matrix cells).
- [x] T11 — AC-T.4 staleness detector 2×2 matrix + AC-T.11 re-read test landed (`tests/test_lesson_plan_log_staleness.py`, 9 tests).
- [x] T12 — AC-T.5 monotonic-revision test landed with M-2 positive test (`tests/test_lesson_plan_log_monotonic.py`, 10 tests).
- [x] T13 — AC-T.6 `pre_packet_snapshot` payload shape test landed (`tests/contracts/test_pre_packet_snapshot_payload_shape.py`, 6 tests).
- [x] T14 — AC-T.7 `NAMED_MANDATORY_EVENTS` ↔ `RESERVED_LOG_EVENT_TYPES` parity test + M-3 frozenset immutability tests landed (`tests/test_lesson_plan_log_named_events.py`, 9 tests).
- [x] T15 — AC-T.8 read-API filter + ordering + no-mutation-leak test landed (`tests/test_lesson_plan_log_read_api.py`, 8 tests).
- [x] T16 — AC-T.9 atomic-write test landed with platform gate — `pytest.skipif` on single crash-sim function only (`tests/test_lesson_plan_log_atomic_write.py`, 5 tests, 1 skipped on Windows).
- [x] T17 — `SCHEMA_CHANGELOG.md` extended with `## Lesson Plan Log v1.0 — 2026-04-18 — Story 31-2 Lesson Plan Log` entry.
- [x] T18 — Full regression green: `--run-live` 1102 passed / 4 skipped / 2 deselected / 2 xfailed / 0 failed; default 1080 passed / 1 skipped / 27 deselected / 2 xfailed / 0 failed. Ruff clean. Pre-commit clean (ruff-lint + orphan-detector + co-commit-invariant all pass).
- [x] T19 — Party-mode implementation review (G5) — **2026-04-18**. Panel: Winston (Architect GREEN) / Murat (TEA GREEN on all 5 R2 amendments verified) / Paige (YELLOW with anti-pattern-count nit, now addressed) / Amelia self-review (HIGH confidence with proactive offer to collapse, applied).
- [x] T20 — `bmad-code-review` layered pass (G6) — **2026-04-18**. Blind Hunter: 4 MUST-FIX + 9 SHOULD-FIX + 8 NITs. Edge Case Hunter: 2 MUST-FIX + 7 SHOULD-FIX + 6 NITs (40 conditions walked). Acceptance Auditor: 0 MUST-FIX + 3 SHOULD-FIX + 6 NITs (24/28 ACs strong enforcement). Orchestrator triage: 19 APPLY (6 MUST-FIX + 1 G5 doc rider + 12 SHOULD-FIX) + 10 DEFER + 20 DISMISSED (cosmetic).
- [x] T21 — Close to done; 30-1 / 30-4 / 32-2 unblocked. Spec flipped `in-progress → review`; operator adjudicates `review → done` after sprint-status.yaml flip.

## Test Plan

`tests_added ≥ K` with **K = 17** (floor, bumped from 15 per M-5 R2 rider — AC-T.11 re-read-after-write consistency; matches §6-E4 original 31-2 K≥12 bumped to 15 per initial R2 rolls + AC-T.1 log-surface shape pin + AC-T.7 registry-parity + AC-T.9 atomic-write, further bumped to 17 per M-5). **Defense:** the six named mandatory events + the single-writer matrix (12 parametrized cases counting as one test file but many collecting cases) + monotonic-revision (6 cases including M-2 positive) + staleness detector 2×2 matrix (4 cells + edges + re-read) + read API (5 cases) + atomic write (3 cases) + shape pins (3 contracts) + frozenset immutability (2 cases) = realistic landing **25–40 collecting tests**, well above the K=17 floor. K=17 is the pass/fail contract for §6-E4.

| Test | AC | Level | Mocked? | Blocking at merge? |
|------|----|-------|---------|---------------------|
| `test_lesson_plan_log_shape_stable` (snapshot + allowlist) | T.1 | Contract | N/A | **Yes — Murat's #1 priority** |
| `test_pre_packet_snapshot_payload_shape` | T.6 | Contract | N/A | **Yes — Winston R1 amendment on 30-4 surface** |
| `test_lesson_plan_log_named_events` parity + frozenset-immutability (M-3) | T.7 | Unit | N/A | **Yes — amendment 8 surface + M-3 immutability** |
| `test_lesson_plan_log_append_only` | T.2 | Unit | N/A | Yes |
| `test_lesson_plan_log_single_writer` (parametrized 12) | T.3 | Unit | N/A | **Yes — R1 amendment 13 CENTRAL** |
| `test_lesson_plan_log_staleness` 2×2 matrix (M-1; 4 cells) | T.4 | Unit | `tmp_path` | Yes |
| `test_lesson_plan_log_staleness::test_empty_log_bootstrap` | T.4 | Unit | `tmp_path` | Yes |
| `test_lesson_plan_log_staleness::test_re_read_after_write_consistency` (M-5) | T.11 | Unit | `tmp_path` | **Yes — M-5 regression shield** |
| `test_lesson_plan_log_monotonic` (6 cases incl. M-2 positive) | T.5 | Unit | `tmp_path` | Yes |
| `test_lesson_plan_log_read_api::test_filter_by_revision` | T.8 | Unit | `tmp_path` | Yes |
| `test_lesson_plan_log_read_api::test_filter_by_event_type` | T.8 | Unit | `tmp_path` | Yes |
| `test_lesson_plan_log_read_api::test_ordering_stable` | T.8 | Unit | `tmp_path` | Yes |
| `test_lesson_plan_log_read_api::test_no_mutation_leak` | T.8 | Unit | `tmp_path` | Yes |
| `test_lesson_plan_log_atomic_write::test_fsync_called` (spy, all platforms) | T.9 | Unit | `os.fsync` spy | Yes |
| `test_lesson_plan_log_atomic_write::test_no_partial_line` (POSIX-only skipif) | T.9 | Unit | `tmp_path` | Yes |

**Target baseline delta: ≥17 collecting tests** (floor per M-5 bump; realistic landing estimated 25–40). Baseline at commit `15f68b1` HEAD: `--run-live` 1023 passed / 3 skipped / 2 deselected / 2 xfailed; default 1001 passed / 27 deselected / 2 xfailed. Expected after 31-2: `--run-live` **≥1040 passed**, default **≥1018 passed**, no new skips (exempting the AC-T.9 POSIX-platform `skipif` noted in AC-B.9), no new xfails, no new `live_api`, no new `trial_critical`.

## Out-of-scope

31-2 is the **log write-path primitive** — it ships the storage surface, the single-writer enforcement, the read API, and the staleness detector, and nothing more. Explicitly excluded:

- **Event emission call-sites.** 31-2 does NOT wire `plan_unit.created` / `scope_decision.set` / `scope_decision_transition` / `plan.locked` / `fanout.envelope.emitted` emission at real Marcus call-sites — those land in 30-1 (duality split + first writes) and 30-3a/b (4A loop emits `plan_unit.created` / `scope_decision.set` / `scope_decision_transition` / `plan.locked`) and 30-4 (fanout emits `fanout.envelope.emitted`). 31-2 ships the API; 30-x populates it.
- **`pre_packet_snapshot` emission call-site.** 30-2b wires the actual Marcus-Intake emission (one event per 4A entry) via the Orchestrator write API. 31-2 ships the payload shape + permission gate; 30-2b emits.
- **`assert_plan_fresh` call-sites in envelopes 05→13.** 32-2 coverage-manifest verifier enforces that every envelope 05→13 carries the plan-ref AND calls `assert_plan_fresh`. 31-2 ships the detector; 32-2 audits coverage.
- **Log compaction, rotation, archival.** Out of MVP scope. If the log grows unmanageable, a future story handles compaction with a migration path.
- **Multi-process writer coordination.** 31-2 is explicit single-process single-writer. Future multi-process coordination requires a separate story (file locks, lease mechanism, etc.).
- **Event dedup on `event_id`.** Two `append_event` calls with the same `event_id` produce two log lines. 32-2 or a future story handles dedup if observed in trial runs.
- **Idempotent relock.** §6-B2 pinned to strict-monotonic; idempotent relock is explicitly rejected.
- **Pub-sub, filesystem watchers, external observers.** Out of scope. Downstream stories consume via `read_events`; they poll, not subscribe.
- **Log format evolution / v2 migration path.** This is v1.0, the first log format. Future evolution is a separate story.
- **30-1 duality split, 30-4 fanout, 32-2 coverage manifest.** All consume 31-2 but are scoped to their own stories.

## Dependencies on Ruling Amendments

- **R1 ruling amendment 8 — Named mandatory events.** AC-B.8 (`NAMED_MANDATORY_EVENTS`), AC-T.7 (parity test).
- **R1 ruling amendment 13 — Single-writer rule.** AC-B.2 (`append_event` enforcement), AC-B.3 (`WriterIdentity` matrix), AC-C.6 (triple-surfaced), AC-T.3 (CENTRAL parametrized test), §Pre-Development Gate PDG-1 (Quinn Q-4 checklist).
- **Quinn Q-4 R2 carry-forward — Green-light checklist surface.** §Pre-Development Gate PDG-1 (BINDING entry criterion).
- **Winston R1 amendment on 30-4 — Log-only Intake-era reconstruction.** AC-B.7 (`pre_packet_snapshot` payload shape), AC-T.6 (payload shape-pin).
- **Murat R1 binding PDG — §6-E4 K-floor + no-flake.** AC-T.10 (suite gate), K=15 floor, no new xfail / skip / live_api / trial_critical.
- **Quinn §6-B2 failure fixture — Digest-drift / revision collision.** AC-B.6 + AC-T.5 (strict-monotonic pinned; idempotent relock explicitly rejected).
- **Winston §6-D2 schema-change lockstep — Single-writer rule invariant automated test.** AC-T.3 (CENTRAL parametrized test satisfies §6-D2 invariant).

## Forward References — §6 PDG Gate

31-2 satisfies these §6 entries directly:
- **§6-D2** — Single-writer rule invariant automated test: AC-T.3 (CENTRAL parametrized) IS this test.
- **§6-D1** — Post-31-1 schema edit lockstep: `SCHEMA_CHANGELOG` entry per AC-C.3 is the lockstep artifact for the log shape.
- **§6-B2** — Digest-drift / revision-collision failure fixture: AC-T.5 pins strict-monotonic semantics; no silent divergence.

31-2 does NOT satisfy §6-E1 / §6-E2 / §6-E3 / §6-C1 / §6-A1-3; those land on downstream stories (29-2, 30-3b, 32-3, 32-4).

## Risks

| Risk | Mitigation |
|------|------------|
| **Amendment 13 single-writer rule silently violated by a future call-site** | AC-T.3 CENTRAL parametrized test runs every build. AC-C.8 dev-note forbids direct `open(LOG_PATH)` reads; enforced via `bmad-code-review`. Quinn Q-4 green-light checklist surfaces it. Triple-layer: schema (Literal) + runtime (`append_event` matrix check) + test (parametrized). |
| **`pre_packet_snapshot` payload drift breaks 30-4 fanout** | AC-T.6 shape-pin test runs every build. Schema changes require SCHEMA_CHANGELOG entry. 30-4 consumes via `read_events`, not in-memory Marcus-Intake state — Winston amendment enforced at the log API surface. |
| **Monotonic revision on `plan.locked` blocks legitimate re-lock workflows** | Out-of-scope for MVP (§6-B2 pins strict-monotonic). If re-lock UX requires idempotent relock in a future story, revision semantics migrate via SCHEMA_CHANGELOG major bump + explicit AC. |
| **Atomic write non-deterministic on Windows** | Platform caveat in module docstring + `skipif` on Windows for crash-simulation test. Spy-based fsync-sequence assertion runs on all platforms. Single-process single-writer assumption makes NTFS sufficient in practice. |
| **Downstream consumer bypasses `read_events` and opens file directly** | AC-C.8 dev-note. `bmad-code-review` Blind Hunter layer scans for `open(LOG_PATH)` / `open(.../lesson_plan_log.jsonl)` in consumer code. |
| **Test suite file-pollution from real `LOG_PATH`** | AC-C.4 test fixture contract: `LessonPlanLog.__init__(path=tmp_path / "log.jsonl")` always constructed with a per-test `tmp_path`. AC-T.1 schema-pin asserts `LOG_PATH` default but never writes to it. |
| **`WriterIdentity` widened silently** | AC-C.5 closed set. Widening requires ruling amendment + SCHEMA_CHANGELOG major bump + migration-path AC. Type-layer + runtime-matrix + parametrized test all catch drift. |
| **R2 green-light missed Quinn Q-4 checklist item (BINDING)** | §Pre-Development Gate PDG-1: 31-2 NOT authorized to enter `bmad-dev-story` until the R2 panel surfaces amendment 13 explicitly. Checklist item is BINDING, not optional. |
| **Log compaction pressure in trial runs** | §6-B2 semantics keep log small at MVP (only one `plan.locked` per revision; typical plan ≤10 revisions; typical units ≤9; log size ≤ a few KB). Out-of-scope deferral is safe for MVP. If trial-run observation reveals bloat, Epic 32 or a follow-up story handles compaction. |

## Dev Notes

### Architecture (per R1 rulings 8 + 13 + Winston-on-30-4)

- **One log, one writer API.** The `append_event` method is the ONLY write path. No direct file I/O in any downstream code. This is the enforcement point for amendment 13.
- **Single-process single-writer (explicit).** 31-2 does NOT ship cross-process coordination. The API is the enforcement point; if two processes hold `LessonPlanLog` instances, behavior is undefined. Multi-process coordination is a separate story (future).
- **Read is stream-friendly.** `read_events` returns an iterator, not a list. Downstream consumers can process events one at a time without loading the whole log.
- **Staleness is detection, not repair.** `assert_plan_fresh` raises when the envelope is stale; downstream is responsible for refreshing. 31-2 does NOT ship a refresh path.
- **Intake reconstructibility is the Winston contract on `pre_packet_snapshot.payload`.** 30-4 reads the log; the payload has ENOUGH state for 30-4 to reconstruct fanout context. No `read_from_marcus_intake_state()` path exists.
- **`SourceRef` ships at first-use site (`log.py`), not `schema.py`.** If 30-4 or a future consumer needs it elsewhere, migrate via minor schema bump. This avoids premature abstraction.

### Anti-patterns (dev-agent WILL get these wrong without explicit warning)

G5-Paige rider (2026-04-18): collapsed from 12 items to 9 by merging the writer-identity discipline pair (Q-R2-R1 + WriterIdentity widening) and folding the 31-1-scope-only "Do NOT emit during schema operations" bullet (it is a 31-1 constraint, not a 31-2 trap).

- **Do NOT mutate existing log events.** Append-only is the entire contract. No in-place edits, no `update_event`, no `overwrite`, no `delete`. AC-T.2 asserts these methods do not exist.
- **Do NOT bypass the `append_event` API.** No direct `open(LOG_PATH, "a")` anywhere in the codebase outside `log.py`. AC-C.8 + `bmad-code-review` catches this. Downstream consumers use `LessonPlanLog.append_event` or nothing.
- **Do NOT use threading, async, asyncio, or multi-process in 31-2.** Single-process single-writer is the EXPLICIT assumption. Any concurrency requires a new story with explicit coordination primitives.
- **Do NOT accept unknown `event_type` silently.** 31-1's `validate_event_type` WARNs on unknown (Gagné seam); 31-2's `append_event` REJECTs on event_type not in `NAMED_MANDATORY_EVENTS`. The log is a governance artifact, not an extensibility surface. AC-T.7 enforces.
- **Do NOT idempotent-relock at the same revision.** §6-B2 strict-monotonic pin. AC-T.5 asserts same-revision relock raises `StaleRevisionError`. If operator reverts a dial and re-locks, the relock bumps revision. **Corollary (G6 MF-EC-2):** the log is append-across-runs; callers writing `plan.locked` MUST consult `latest_plan_revision()` and use `latest + 1`. Do NOT assume the log is empty at caller init.
- **Do NOT dedupe events on `event_id`.** Two `append_event` calls with the same envelope (same `event_id`) produce two log lines. Dedup is out-of-scope; if observed in trial, a follow-up story handles it.
- **Do NOT use `pickle`, `msgpack`, or any non-canonical-JSON format.** Log lines are JSON, one line per event, UTF-8, terminated by `"\n"`. Prior-art pattern in `skills/bmad-agent-marcus/scripts/run-interstitial-redispatch.py::_append_jsonl`.
- **Do NOT let tests write to real `LOG_PATH`.** Every test uses `tmp_path` fixture. AC-C.4. If the test suite ever runs and pollutes `state/runtime/lesson_plan_log.jsonl`, the test is broken.
- **Do NOT add `xfail` or `skip` to the default suite.** Per `feedback_regression_proof_tests.md`. AC-T.9's Windows-platform `skipif` is exempted as platform-conditional-skip-at-collect-time (Murat standing practice); any other skip is a red flag.
- **Writer-identity discipline (merged — Q-R2-R1 + `WriterIdentity` widening).** `Literal["marcus-orchestrator", "marcus-intake"]` is a CLOSED set; widening breaks R1 amendment 13 and requires ruling amendment + SCHEMA_CHANGELOG major bump. At the caller level, Intake modules pass ONLY `"marcus-intake"`; Orchestrator modules pass ONLY `"marcus-orchestrator"`. `bmad-code-review` Blind Hunter SHOULD grep for `writer_identity=` assignments and verify caller-module alignment. Trust-the-caller is the single-process single-writer assumption; grep-detectable discipline converts it from convention to CI-verifiable. A violation at a future call-site (e.g. an Intake helper spoofing `writer_identity="marcus-orchestrator"` to skirt the permission matrix) would silently defeat amendment 13 at the schema layer; Quinn's R2 rider closes this gap via code-review-grep convention. G6 SF-EC-3 additionally separates typos (`ValueError`) from auth failures (`UnauthorizedWriterError`) at the write-path guard.

### Source tree (new + touched)

```
marcus/lesson_plan/                                [EXISTS — 31-1]
├── __init__.py                                    [TOUCH +15]  Extend __all__ with log surface
├── log.py                                         [NEW +240]  LessonPlanLog + write/read API + staleness detector + single-writer matrix + payload shapes
├── schema.py                                      [EXISTS — 31-1; unchanged]
├── events.py                                      [EXISTS — 31-1; unchanged]
├── digest.py                                      [EXISTS — 31-1; unchanged]
├── event_type_registry.py                         [EXISTS — 31-1; unchanged]
├── dials-spec.md                                  [EXISTS — 31-1; unchanged]
└── schema/
    ├── lesson_plan.v1.schema.json                 [EXISTS — 31-1; unchanged]
    └── fit_report.v1.schema.json                  [EXISTS — 31-1; unchanged]

tests/contracts/
├── test_lesson_plan_log_shape_stable.py           [NEW +110]  AC-T.1 log-surface shape pin
├── test_pre_packet_snapshot_payload_shape.py      [NEW +70]   AC-T.6 pre_packet_snapshot + SourceRef shape pin
└── test_named_mandatory_events_parity.py          [NEW +40]   AC-T.7 parity with RESERVED_LOG_EVENT_TYPES

tests/
├── test_log_append_only.py                        [NEW +60]   AC-T.2
├── test_log_single_writer_matrix.py               [NEW +120]  AC-T.3 amendment 13 CENTRAL
├── test_assert_plan_fresh.py                      [NEW +90]   AC-T.4
├── test_log_monotonic_revision.py                 [NEW +80]   AC-T.5
├── test_log_read_api.py                           [NEW +90]   AC-T.8
└── test_log_atomic_write.py                       [NEW +90]   AC-T.9 (platform-gated crash simulation)

_bmad-output/implementation-artifacts/
└── SCHEMA_CHANGELOG.md                            [TOUCH +30] Lesson Plan Log v1.0 entry

state/runtime/
└── lesson_plan_log.jsonl                          [RUNTIME]   Created by first append_event call; NOT committed, NOT pre-populated by 31-2
```

### Testing standards (inherited from 27-0 / 31-1 discipline)

- **No `live_api`, no `trial_critical`, no `xfail`, no `skip`** on the default suite. Sole exception: AC-T.9 crash-simulation line is `pytest.skipif(sys.platform == "win32")` — platform-conditional at collect time (not xfail). All other assertions run on all platforms.
- **Schema pins use snapshot + allowlist + CHANGELOG gate** (Murat pattern from 27-0 / 31-1 AC-T.1).
- **Deterministic fixtures only.** `tmp_path` for every log-writing test. No stateful mocks, no async, no stdio pipes. Single-process single-writer matches the production model.
- **Canonical JSON fixtures** under `tests/fixtures/lesson_plan_log/` as plain-text `.jsonl` files (diff-friendly; no binaries). If fixtures are trivial, inline in test body.
- **Per `feedback_regression_proof_tests.md`:** no xfail, no skip (sole exemption above), classify every failure (update/restore/delete), measure coverage.

### References

- **Pattern source (closest shape):** [`31-1-lesson-plan-schema.md`](./31-1-lesson-plan-schema.md) — metadata header, AC layering, File Impact, Tasks, Test Plan, Dev Notes, Governance Closure Gates, R1/R2 traceability table.
- **Plan doc (R1 orchestrator ruling):** [`../planning-artifacts/lesson-planner-mvp-plan.md`](../planning-artifacts/lesson-planner-mvp-plan.md) — Orchestrator Ruling Record §amendments 8, 13, 14; §6-B2 / §6-D1 / §6-D2 / §6-E4.
- **Governance:** [`CLAUDE.md`](../../CLAUDE.md) — BMAD sprint governance; party-mode green-light + `bmad-code-review` before `done`; stop-on-impasse-only.
- **Prior-art append-only JSONL pattern:** `skills/bmad-agent-marcus/scripts/run-interstitial-redispatch.py::_append_jsonl` (lines 82–86). 31-2 inherits the line-shape; wraps in atomic-write semantics.
- **Foundation consumed (31-1):** `marcus/lesson_plan/schema.py`, `events.py`, `digest.py`, `event_type_registry.py`, `__init__.py`.
- **MEMORY:** `project_enrichment_vs_gap_filling_control.md` (three-parameter family observed by dials + gaps), `feedback_regression_proof_tests.md` (no-xfail-no-skip discipline), `feedback_bmad_workflow_discipline.md` (party-mode + code-review before `done`).

### Non-goals

- **No real Marcus call-site emission in 31-2.** 30-1 / 30-2b / 30-3a/b / 30-4 populate.
- **No `assert_plan_fresh` call-sites in envelopes.** 32-2 coverage manifest audits that.
- **No LLM calls, no network, no async, no concurrency.** Pure file-I/O + Pydantic.
- **No performance optimization.** Log is O(events); MVP plans are ≤10 revisions × ≤9 units = tiny.
- **No migration path for v0.** This is v1.0, the first log.
- **No operator-facing prose.** Log is a governance artifact read by agents, not Maya.

## Governance Closure Gates (per CLAUDE.md)

31-2 closes `done` only when ALL below satisfied:

- [x] **G1. R2 party-mode green-light** on this spec with the Quinn Q-4 checklist item explicitly referencing R1 ruling amendment 13 (BINDING per §Pre-Development Gate PDG-1). Panel: Winston / Murat / Quinn / Paige. **CLEARED 2026-04-18** — GREEN with 7 riders applied.
- [x] **G2. `bmad-dev-story` execution** with all T1–T21 subtasks checked. **CLEARED 2026-04-18**.
- [x] **G3. `tests_added ≥ 17`** collecting (§6-E4 floor; bumped from 15 per M-5 R2 rider). **CLEARED 2026-04-18**: +19 G6-hardening tests layered on top of the initial 80 collecting (total delta ≥99 tests, well above K=17).
- [x] **G4. Ruff clean + pre-commit green + co-commit test+impl discipline** (27-2 / 31-1 pattern). **CLEARED 2026-04-18**.
- [x] **G5. Party-mode implementation review.** Winston GREEN on architecture + Murat GREEN on test-coverage of amendment 13 + Paige YELLOW on anti-pattern count (now addressed) + Amelia self-review HIGH. **CLEARED 2026-04-18**.
- [x] **G6. `bmad-code-review` layered pass** — Blind Hunter / Edge Case Hunter / Acceptance Auditor. Triage: 19 APPLY + 10 DEFER + 20 DISMISSED. **CLEARED 2026-04-18**.
- [ ] **G7. `sprint-status.yaml` flipped** `ready-for-dev → in-progress → review → done` per bmm workflow. Operator-gated flip to `done`.
- [ ] **G8. `bmm-workflow-status.yaml` updated** with closure note naming test delta + amendment 13 enforcement-triple landing. Operator-gated flip.
- [ ] **G9. Unblocks downstream.** Verify 30-1 / 30-4 / 32-2 all now have a green 31-2 dependency.

## Dev Agent Record

**Executed by:** Amelia, 2026-04-18.
**Date:** 2026-04-18 (T2–T21 implementation + G5 party-mode + G6 layered code review + 19 patches applied + regression pass).

### Landed artifacts

| Artifact | Status | Lines |
|----------|--------|-------|
| `marcus/lesson_plan/log.py` | NEW | ~385 |
| `marcus/lesson_plan/__init__.py` | TOUCH — exports extended with 11 log surface names | +32 |
| `tests/contracts/test_lesson_plan_log_shape_stable.py` | NEW — 15 tests | ~235 |
| `tests/contracts/test_pre_packet_snapshot_payload_shape.py` | NEW — 6 tests | ~105 |
| `tests/test_lesson_plan_log_append_only.py` | NEW — 4 tests | ~90 |
| `tests/test_lesson_plan_log_single_writer.py` | NEW — 14 tests (12 parametrized matrix cells + 2) | ~95 |
| `tests/test_lesson_plan_log_staleness.py` | NEW — 9 tests (M-1 2×2 + edges + M-5 re-read) | ~175 |
| `tests/test_lesson_plan_log_monotonic.py` | NEW — 10 tests (incl. M-2 positive) | ~135 |
| `tests/test_lesson_plan_log_named_events.py` | NEW — 9 tests (parity + M-3 immutability) | ~110 |
| `tests/test_lesson_plan_log_read_api.py` | NEW — 8 tests | ~125 |
| `tests/test_lesson_plan_log_atomic_write.py` | NEW — 5 tests (1 Windows-platform skipif) + G6 SF-AA-3 + SF-BH-13 patches | ~125 |
| `tests/test_lesson_plan_log_g6_hardening.py` | **NEW at G6** — 19 tests (MUST-FIX MF-BH-1..4 + MF-EC-1..2 + SHOULD-FIX SF-EC-3/8/9 + SF-BH-6/7 coverage) | ~310 |
| `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` | TOUCH — Lesson Plan Log v1.0 entry | +95 |
| `scripts/utilities/progress_map.py` | TOUCH — WAVE_LABELS for epics 29/30/31/32 (pre-existing-regression-fix, unrelated to 31-2 proper but surfaced during regression) | +4 |
| `_bmad-output/maps/deferred-work.md` | TOUCH — §`31-2 G5+G6 deferred findings` (10 items) | +15 |

### Regression delta

**Baseline at commit `15f68b1` HEAD (verified pre-landing with `git stash -u`):**
- `--run-live`: 1022 passed / **1 failed** (pre-existing `test_progress_map::test_wave_labels_covers_live_epic_ids`) / 3 skipped / 2 deselected / 2 xfailed
- Default: 1000 passed / **1 failed** (same) / 27 deselected / 2 xfailed

Note: orchestrator's R2 rider M-4 baseline number (1023 / 1001 passed) presumed the progress_map failure was not present; true HEAD baseline includes 1 pre-existing failure on master which Amelia repaired per `feedback_regression_proof_tests.md` ("never leave tests failing in master") as part of T18.

**After 31-2 landing + progress_map repair:**
- `--run-live`: **1102 passed / 0 failed** / 4 skipped / 2 deselected / 2 xfailed
- Default: **1080 passed / 0 failed** / 1 skipped / 27 deselected / 2 xfailed

**Delta (T2–T18):** +80 passed --run-live (1022 → 1102; +80 31-2 collecting tests including 1 skipif-Windows crash-sim), well above M-5 K=17 floor.

**After G6 hardening (T19–T21) — 19 additional tests from `test_lesson_plan_log_g6_hardening.py`:**
- `--run-live`: **1478 passed / 0 failed** / 6 skipped / 2 deselected / 2 xfailed
- Default: **1456 passed / 0 failed** / 3 skipped / 27 deselected / 2 xfailed

(The passed-count reflects post-T18 base plus the full sprint/workspace regression delta; the +19 G6 tests are additive to the 80 from T18 within this spec's scope.)

**Total 31-2 test delta:** **+99 collecting tests** over pre-31-2 baseline (80 at T18 + 19 at G6). K=17 floor cleared by >5×.

### Ruff / pre-commit

- Ruff: all checks passed on all new/touched files (re-verified post-G6).
- Pre-commit hooks ran clean (ruff-lint + orphan-detector + co-commit-invariant).

### R2-rider applicability table

| Rider | Landing |
|-------|---------|
| **W-R1** (Winston — Windows atomic-write caveat) | Applied as `marcus/lesson_plan/log.py` module docstring §"Platform caveat" (docstring-only, no code change). |
| **Q-R2-R1** (Quinn — writer_identity anti-pattern) | Applied as `marcus/lesson_plan/log.py` module docstring §"Writer discipline" + Dev Notes anti-patterns bullet in 31-2 spec. |
| **M-1** (Murat — AC-T.4 2×2 matrix + axis-named error) | Applied in `assert_plan_fresh` implementation (axis-named `StalePlanRefError` message) + AC-T.4 / `tests/test_lesson_plan_log_staleness.py` 4-cell parametrized tests. |
| **M-2** (Murat — non-plan.locked stale ACCEPTED) | Applied in `append_event` (monotonic check guarded by `if envelope.event_type == "plan.locked":`) + AC-T.5 / `test_non_plan_locked_stale_revision_is_accepted` positive test. |
| **M-3** (Murat — frozenset immutability) | Applied via `NAMED_MANDATORY_EVENTS = RESERVED_LOG_EVENT_TYPES` (already frozenset) + `tests/test_lesson_plan_log_named_events.py` `.add()` / `.remove()` / `.discard()` / `.clear()` AttributeError assertions (5 tests). |
| **M-4** (Murat — baseline rebase) | AC-T.10 + Test Plan rebased to commit `15f68b1`; but operator's rebase premised 0 failures where 1 pre-existed. Repaired (see progress_map note above). |
| **M-5** (Murat — AC-T.11 re-read + K 15→17) | Applied via `tests/test_lesson_plan_log_staleness.py::test_re_read_after_write_consistency` + `test_re_read_after_multiple_writes` (2 tests). K floor bumped 15→17 in Test Plan + G3.

### Flags / operator adjudication

- **sprint-status.yaml + bmm-workflow-status.yaml updates — NOT APPLIED by Amelia per operator's instruction "flag changes needed but do NOT apply (dual-writer risk; operator adjudicates)."** Suggested edits:
  - `sprint-status.yaml` `epic-31 → 31-2` flip from `ready-for-dev` to `review` (T18 complete; G5/G6 pending).
  - `bmm-workflow-status.yaml` record 31-2 implementation landing.
  - After G5 + G6 pass, flip `31-2` → `done` + mark 30-1 / 30-4 / 32-2 as unblocked.
- **progress_map.py WAVE_LABELS repair:** applied to return suite to green (per regression-proof-tests MEMORY) — operator should confirm the new epic label strings match their taxonomy. Current values: `"29": "Irene Diagnostics & Fit-Report Validator"`, `"30": "Marcus Duality Split + Plan-Lock Fanout"`, `"31": "Tri-phasic Contract Primitives + Gates"`, `"32": "Envelope Audit + Coverage Manifest"`.
- **Spec Status field:** flipped `ready-for-dev` → `in-progress` at top of file. Operator should flip `in-progress → review` at G5, `review → done` after G6.

## Review Record

### Party-mode R2 green-light — 2026-04-18

**Date:** 2026-04-18.
**Review panel:** Winston (Architect) / Murat (TEA / Test) / Quinn (Problem-Solver) / Paige (Tech Writer).
**Verdict:** **GREEN conditional on 7 riders** — all 7 applied.

**Panel verdicts:**

- **Winston (W): GREEN + W-R1.** Architecture sound. W-R1 rider adds a Windows atomic-write future-hardening caveat to the `log.py` module docstring: on Windows NTFS, future hardening via `os.replace()` temp-file-rename is atomic; current append-then-fsync is adequate for single-process single-writer MVP but may be upgraded for multi-writer scenarios. Docstring-only, no code change.
- **Murat (AM): YELLOW → GREEN with M-1 / M-2 / M-3 / M-4 / M-5.** (M-1) AC-T.4 2×2 staleness matrix + axis-named `StalePlanRefError` message; (M-2) AC-T.5 positive-test that non-plan.locked stale-revision is ACCEPTED + AC-B.6 language; (M-3) AC-T.7 frozenset immutability; (M-4) baseline rebase to `--run-live` 1023 / default 1001 at commit `15f68b1`; (M-5) new AC-T.11 re-read-after-write + K floor 15 → 17.
- **Quinn (Q): GREEN + Q-R2-R1.** Q-4 BINDING amendment 13 checklist item surfaced. Q-R2-R1 rider adds the writer_identity anti-pattern discipline to Dev Notes.
- **Paige (P): GREEN + nit (deferred).** Nit deferred to G5 tech-writer review.

**Rider amendments applied:**

| Rider | Tag | Applied to |
|-------|-----|------------|
| **W-R1** | Winston — Windows atomic-write caveat | `marcus/lesson_plan/log.py` module docstring (T2; referenced in AC-B.9 + AC-C.7) |
| **Q-R2-R1** | Quinn — writer_identity anti-pattern discipline | Dev Notes §Anti-patterns (new bullet); code-review-grep convention forward-ref |
| **M-1** | Murat — AC-T.4 2×2 staleness matrix + axis-named error message | AC-T.4 (4 cells + edges); `log.py` error-message format |
| **M-2** | Murat — non-plan.locked stale-revision ACCEPTED | AC-B.6 language + AC-T.5 positive test |
| **M-3** | Murat — frozenset immutability assertion | AC-T.7 (`.add()` raises `AttributeError`) |
| **M-4** | Murat — baseline rebase to 15f68b1 HEAD | AC-T.10 + Test Plan (1023 `--run-live` / 1001 default) |
| **M-5** | Murat — NEW AC-T.11 re-read-after-write + K 15→17 | AC-T.11 (new); Test Plan K floor bump; G3 bump |

**Decision:** GREEN. 31-2 authorized to enter `bmad-dev-story` (T2–T21). All 7 riders folded into spec. Quinn Q-4 BINDING checklist item explicitly references R1 amendment 13 via AC-C.6 + AC-T.3 + §Pre-Development Gate PDG-1 (triple-surfaced).

### G5 Party-mode implementation review — 2026-04-18

**Date:** 2026-04-18.
**Review panel:** Winston (Architect) / Murat (TEA) / Paige (Tech Writer) / Amelia (self-review).
**Verdict:** **GREEN** with 1 doc rider (Paige anti-pattern collapse, applied).

**Panel verdicts:**

- **Winston (Architect): GREEN.** No riders on implementation. W-R1 atomic-write caveat landed as module docstring per R2; code path is clean for single-process MVP. Future hardening via `os.replace()` temp-file-rename is documented as out-of-scope for 31-2 and will land via a future story if multi-writer scenarios arise.
- **Murat (TEA): GREEN.** All 5 R2 amendments verified as landed:
  - M-1 axis-named `StalePlanRefError` message format + 2×2 staleness matrix tests.
  - M-2 non-plan.locked stale-revision ACCEPTED + positive test.
  - M-3 frozenset immutability (`.add()` / `.remove()` / `.discard()` / `.clear()` `AttributeError`).
  - M-4 baseline rebase applied (repaired pre-existing progress_map failure during T18).
  - M-5 re-read-after-write consistency + K floor 15→17.
- **Paige (Tech Writer): YELLOW → GREEN** with anti-pattern-count rider. Initial review noted 12 anti-pattern items with redundancy between "Do NOT widen `WriterIdentity`" + the new Q-R2-R1 writer-identity discipline bullet; and the "Do NOT emit to the log during 31-1 schema operations" bullet concerns 31-1 scope rather than 31-2 traps. Rider applied via G5-Paige: list collapsed from 12 → 9 (writer-identity items merged; 31-1-scope bullet folded; strict-monotonic bullet absorbed MF-EC-2 pre-existing-log corollary). Directionally meets Paige's ~8-10 target.
- **Amelia (self-review): HIGH confidence** with proactive offer to collapse anti-pattern list — applied as part of Paige rider.

### G6 bmad-code-review layered pass — 2026-04-18

**Date:** 2026-04-18.
**Layers:** Blind Hunter / Edge Case Hunter / Acceptance Auditor.
**Triage (Orchestrator):** 19 APPLY (6 MUST-FIX + 1 G5 doc rider + 12 SHOULD-FIX) + 10 DEFER (logged to `_bmad-output/maps/deferred-work.md` §`31-2 G5+G6 deferred findings`) + 20 DISMISSED (cosmetic NITs).

**Layer findings:**

- **Blind Hunter:** 4 MUST-FIX + 9 SHOULD-FIX + 8 NITs.
- **Edge Case Hunter:** 2 MUST-FIX + 7 SHOULD-FIX + 6 NITs (40 conditions walked).
- **Acceptance Auditor:** 0 MUST-FIX + 3 SHOULD-FIX + 6 NITs (24/28 ACs strong enforcement).

**MUST-FIX landed (6 items):**

1. **MF-BH-1** — `LOG_PATH` resolved cwd-independent at module import time via `_find_project_root()` walking up from `__file__` for a `pyproject.toml` / `.git/` marker.
2. **MF-BH-2** — `latest_plan_revision` / `latest_plan_digest` reverse-scan (first match from tail wins by strict-monotonic invariant); moved the helper scan into a shared `_iter_all_lines()` that collects non-empty lines once and iterates reversed.
3. **MF-BH-3** — `latest_plan_digest` strict-raises `LogCorruptError` on a `plan.locked` event whose payload fails `PlanLockedPayload` validation (strict, not tolerant — silent stale-digest drift forbidden).
4. **MF-BH-4** — bootstrap sentinel aligned: `latest_plan_digest()` returns `None` on empty log; `assert_plan_fresh` accepts `env_digest in {"", None}` at bootstrap; `PlanLockedPayload.lesson_plan_digest` remains `min_length=1` at WRITE-time (contract at both sides explicit).
5. **MF-EC-1** — new `LogCorruptError` exception class; `read_events` + `latest_plan_revision` + `latest_plan_digest` all raise `LogCorruptError` on `json.JSONDecodeError` or `pydantic.ValidationError`, with line-number + path context for actionable diagnosis. Exported from `marcus.lesson_plan.__init__`.
6. **MF-EC-2** — pre-existing-log caller contract documented in module docstring and anti-patterns: callers writing `plan.locked` MUST consult `latest_plan_revision() + 1`. New test `test_plan_locked_rev_must_exceed_pre_existing_log` seeds the log with rev=100 then asserts `StaleRevisionError` on a naive revision=1 append.

**G5 doc rider landed:**

- **G5-Paige** — anti-pattern list collapsed from 12 → 9 per Paige's directional ~8-10 target. Merged writer-identity discipline pair (Q-R2-R1 + `WriterIdentity` widening); folded 31-1-scope-only "Do NOT emit during schema operations" bullet; strict-monotonic bullet absorbed MF-EC-2 pre-existing-log corollary.

**High-value SHOULD-FIX landed (12 items):**

- SF-AA-2 — tighten Cell 3 substring assertion to `"envelope=7" / "log=5"` literals (no spurious digest-substring match).
- SF-AA-3 — atomic-write crash-sim test pins real behavior: asserts `LogCorruptError` on corrupted line (no manual recovery).
- SF-EC-3 — invalid `writer_identity` (typo not in `Literal`) → `ValueError` (separates typos from auth-fails).
- SF-EC-4 — `LessonPlanLog.__init__` docstring clarified: constructor-only override; module-level `LOG_PATH` mutation is a no-op on existing instances.
- SF-EC-8 — `PrePacketSnapshotPayload.sme_refs` requires `min_length=1`.
- SF-EC-9 — `SourceRef.path` + `pre_packet_artifact_path` field-validators reject absolute paths + `..`-traversal segments.
- SF-BH-6 — `_json_default` unreachable datetime/date branches removed; only unsupported-type raise path remains, covered by new test.
- SF-BH-7 — module-level `assert frozenset(WRITER_EVENT_MATRIX.keys()) == NAMED_MANDATORY_EVENTS` at import time (import-time safety net; existing test retained as belt-and-suspenders).
- SF-BH-10 — `test_no_mutation_leak_on_yielded_envelope` mutates via `object.__setattr__` to bypass `validate_assignment=True`; assertion focuses on instance identity per patch intent.
- SF-BH-12 — simplified `test_m3_type_is_frozenset_not_set` to a single direct type check (frozenset is not a subclass of set).
- SF-BH-13 — renamed `test_write_flush_fsync_sequence` → `test_fsync_is_final_call` with scope-honest docstring (write→flush ordering is a Python stdlib invariant, not an 31-2 contract).
- G6-test-coverage-landing — new `tests/test_lesson_plan_log_g6_hardening.py` (19 new tests covering every MUST-FIX + SHOULD-FIX surface above).

**DEFER (10 items):** See `_bmad-output/maps/deferred-work.md` §`31-2 G5+G6 deferred findings`. Covers mkdir-on-every-append perf, iterator leak on partial consumption, iterator-across-append snapshot semantics, PIPE_BUF docstring citation, canonical_json duplication, ~20 cosmetic NITs, text-mode CRLF translation, WRITER_EVENT_MATRIX outer dict mutability (MappingProxyType hardening), AC-T.4 Cell 2 dup with SF-AA-2, AC-T.3 REJECT post-condition tightening.

**DISMISSED (~20 NITs):** cosmetic (`__future__` in `__init__`, sort order, misleading comments, docstring citations, etc.). Not persisted per aggressive-DISMISS rubric in `docs/dev-guide/story-cycle-efficiency.md` §3.

## R1 + R2 Orchestrator Ruling Traceability

| Ruling | Source | Applied in 31-2 |
|---|---|---|
| **R1 amendm