# Story 32-5: Step 04A Production HIL Intake Callable

**Status:** done
**Created:** 2026-04-19 (surfaced during trial run C1-M1-PRES-20260419 at Step 04A pause)
**Epic:** 32 — Step 4A landing + trial-run harness
**Sprint key:** `32-5-step-04a-production-hil-intake-callable`
**Branch:** `trial/2026-04-19` (trial is paused here; dev work lands on this branch, trial resumes after close)
**Points:** 2
**Depends on:** 32-1 (workflow wiring — done), 32-4 (maya walkthrough — done), 30-3a (FourALoop skeleton — done), 30-3b (dials + sync reassessment — done), 31-1 (LessonPlan schema — done).
**Blocks:** Trial run C1-M1-PRES-20260419 Step 04A resume; Epic 32 full trial validation.
**Governance mode:** **single-gate** per [docs/dev-guide/lesson-planner-story-governance.json](../../docs/dev-guide/lesson-planner-story-governance.json) (`32-5` is not a schema-shape story; no new Pydantic family; post-dev three-layer `bmad-code-review` is the sole review gate).

---

## TL;DR

- **What:** Implement `MarcusPreCollectedIntakeCallable` in `marcus/orchestrator/hil_intake.py` — a production `IntakeCallable` that serves pre-collected operator scope decisions to `FourALoop.run_4a()`, closing the gap between the conversational Step 04A ratification and the programmatic lesson plan log.
- **Why:** `Facade.run_4a()` requires an `intake_callable: IntakeCallable` to drive the per-unit scope loop. All prior stories (30-3a, 30-3b, 32-1, 32-3, 32-4) wired the machinery but left only test stubs at the intake seam. During trial run 2026-04-19, `run_maya_walkthrough()` was incorrectly used as a workaround, contaminating the lesson-plan-log.jsonl with fixture unit IDs instead of the real plan units. Production trial runs cannot validate the Lesson Planner MVP functions without this callable.
- **Done when:** (1) `marcus/orchestrator/hil_intake.py` ships `MarcusPreCollectedIntakeCallable` + `build_hil_intake_callable()` factory; (2) `route_step_04_gate_to_step_05()` in `workflow_runner.py` accepts pre-collected decisions and passes them to `Facade.run_4a()` via the new callable; (3) `reset_lesson_plan_log()` utility in `hil_intake.py` archives stale log entries before a fresh 4A run; (4) focused test coverage at 9-10 collecting tests (K=7); (5) single-gate post-dev `bmad-code-review` layered pass; (6) governance validator PASS; (7) sprint-status flipped to done.
- **Scope discipline:** Zero new schema shapes. Zero new Pydantic models exported via `marcus/lesson_plan/`. Zero new log event types. No changes to `FourALoop`, `FourAState`, `IntakeCallable` type, or `ScopeDecision`. This story is a pure wiring story — it connects existing machinery to the production conversation context.

---

## Story

As the **Lesson Planner trial operator**,
I want **Step 04A to emit correct `scope_decision.set` / `plan.locked` / `fanout.envelope.emitted` events for the actual plan units I ratified in conversation**,
So that **every downstream Lesson Planner gate (Quinn-R step 13, coverage manifest, fanout consumers) operates on the real locked plan, not test fixture data**.

---

## Background — Why This Story Exists

The **four-gate activation (4A) loop** is the checkpoint where Marcus and the operator co-author which plan units enter production execution — deciding in-scope vs out-of-scope for every candidate slide or activity. `FourALoop.run_4a()` (30-3a) expects an `intake_callable: IntakeCallable` — a function that, for each pending unit, returns the operator's decision and rationale:

```python
IntakeCallable = Callable[[FourAState, str], tuple[ScopeDecision, str]]
```

The production use pattern in a conversational Marcus session is **three steps**:

1. **Conversational ratification** — Marcus presents each plan unit; operator says in-scope or out-of-scope with rationale. Already implemented in pack Step 04A.
2. **Decision collection** — Marcus assembles the operator's decisions into a `{unit_id: (scope, rationale)}` mapping.
3. **Programmatic lock** — Marcus calls `Facade.run_4a()` with a callable that serves the collected decisions to `FourALoop`, which emits `scope_decision.set` / `plan.locked` / fanout events to the lesson plan log.

Without step 3, either the loop can't run (no callable), or a test stub is used (wrong data in log), or `run_maya_walkthrough()` is abused (fixture contamination — what happened on trial 2026-04-19). The contaminated log then silently propagates wrong unit_ids to every downstream gate.

`MarcusPreCollectedIntakeCallable` bridges steps 2 and 3.

---

## T1 Readiness

- **Gate mode:** `single-gate`. Pure wiring story; no new schema; post-dev three-layer `bmad-code-review` is the sole review ceremony.
- **K floor:** `K = 7` — elevated from K=6 (2pt baseline) per party-mode R1 (Murat binding rider): log-contamination risk profile warrants reset→run integration test + ordering + disjoint + idempotent assertions. 10 distinct test behaviors identified at story authoring; K=7 reflects this elevated coverage floor.
- **Target collecting-test range:** 9-10 (1.2×K to 1.5×K per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1).
- **Realistic landing estimate:** 9-10 collecting tests.
- **Scaffold:** not required (no new schema shape; no scaffold template applies).
- **Required readings** (dev agent reads at T1 before any code):
  - [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) — especially Marcus-duality section: callable MUST NOT reference Intake/Orchestrator internals; all Maya-facing strings must honor Voice Register.
  - [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 (K-floor), §2 (single-gate), §3 (DISMISS rubric).
  - [docs/dev-guide/pydantic-v2-schema-checklist.md](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — no new Pydantic models needed, but confirm any dataclasses are not accidentally exported through the wrong package boundary.
  - [docs/dev-guide/pipeline-manifest-regime.md](../../docs/dev-guide/pipeline-manifest-regime.md) — **`workflow_runner.py` is in `block_mode_trigger_paths`**. Read this document before touching it. This is a Tier-1 change (adding an optional `pre_collected_decisions=None` param — no behavioral change to pipeline topology, no step addition or removal). Cora's block-mode hook fires at story close.

---

## Acceptance Criteria

### AC-A: `MarcusPreCollectedIntakeCallable` lands in `marcus/orchestrator/hil_intake.py`

**AC-A.1** — `hil_intake.py` exports `MarcusPreCollectedIntakeCallable` callable class and `build_hil_intake_callable()` factory function. Both importable from `marcus.orchestrator.hil_intake`.

**AC-A.2** — `build_hil_intake_callable(decisions: dict[str, tuple[str, str]]) -> IntakeCallable` accepts a mapping of `{unit_id: (scope_value, rationale)}` where `scope_value ∈ {"in-scope", "out-of-scope", "delegated", "blueprint"}` and `rationale` is any string (including empty). Validates at construction time that no duplicate unit_id appears in the source input (if constructed from a list rather than a dict directly) — raises `ValueError` with a clear message. Dict construction at call sites is idempotent; this guard protects against future call-path bugs.

**AC-A.3** — When invoked as `callable(state, unit_id)`:
- Looks up `unit_id` in the pre-collected decisions dict.
- Constructs a **new** `ScopeDecision` instance per call — does not mutate or alias any existing `ScopeDecision` on `state` (aliasing trap: `FourAState` carries scope decisions; the callable must create a fresh instance).
- `ScopeDecision(state="ratified", scope=scope_value, proposed_by="operator", ratified_by="maya")` — `extra="forbid"` on `ScopeDecision` means no extra fields; do NOT pass `modality`, `decided_by`, or any undeclared fields.
- Returns `(decision, rationale)` where `rationale` is stored **verbatim** — no `.strip()`, no coercion, no parsing (R1 amendment 16). The callable is NOT responsible for normalizing whitespace; the caller is responsible for providing the rationale exactly as the operator stated it.

**AC-A.4** — If `unit_id` is not in the decisions dict, raises `MissingIntakeDecisionError(unit_id)` with:
- A Maya-safe message — no tokens "intake", "orchestrator", or "dispatch"; natural language, first-person Marcus voice, ends with an invitation.
- The message must use the `unit_id` value in a human-readable way (e.g., referring to it as "this unit" or by its label if available — never expose a raw technical key as a cold ID).
- **Voice Register compliance example:**
  - ❌ Bad: `"Decision record for plan unit u-03 is absent from the decision registry."`
  - ✓ Good: `"It looks like we haven't made a call on this unit yet — want to mark it in-scope or out-of-scope?"`
- `MissingIntakeDecisionError` is a named exception exported from `hil_intake.py`, not a bare `KeyError` or `ValueError`. The Voice Register constraint must be verifiable by a test (see AC-T.3).

### AC-B: `reset_lesson_plan_log()` utility

**AC-B.1** — `reset_lesson_plan_log(bundle_dir: Path, *, confirm: bool = False) -> Path | None` in `hil_intake.py` renames the existing `lesson-plan-log.jsonl` to `lesson-plan-log.STALE-<timestamp>.jsonl` within the same bundle directory (non-destructive archive — rename, not delete).

**Rename format (binding):** `lesson-plan-log.STALE-{YYYYMMDDTHHMMSS_ffffff}.jsonl` where `ffffff` is microseconds — e.g., `lesson-plan-log.STALE-20260419T221305_423817.jsonl`. Microsecond precision avoids collision on rapid successive resets in CI. All `reset_lesson_plan_log` callers must produce archives in this exact format so recovery tooling can sort them deterministically.

**AC-B.2** — Raises `LogResetNotConfirmedError` if `confirm=False` (default). Caller must explicitly pass `confirm=True` — accidental reset is not possible.

**AC-B.3** — Returns the `Path` to the archived stale file. The archive file must exist at that path after the call — test must verify `archive_path.exists()`, not just that a non-None value was returned.

**AC-B.4** — If no log exists, returns `None` (idempotent — not an error).

**AC-B.5** — If called twice on the same log within the same second, each call must produce a distinct archive path (microsecond precision handles this for clock-derived timestamps; if the system clock is mocked in tests, ensure the mock provides distinct values).

### AC-C: `route_step_04_gate_to_step_05()` wired for production intake

**AC-C.0** — Before modifying `workflow_runner.py`, verify the call-site audit: grep for all callers of `route_step_04_gate_to_step_05()` in the test suite. Confirm all existing calls either use keyword arguments or tolerate a new positional-default trailing parameter. If any caller would break, address before opening the file.

**AC-C.1** — `route_step_04_gate_to_step_05()` in `marcus/orchestrator/workflow_runner.py` gains a keyword-only optional parameter `pre_collected_decisions: dict[str, tuple[str, str]] | None = None`.

**AC-C.2** — When `pre_collected_decisions` is provided, `route_step_04_gate_to_step_05()` calls `build_hil_intake_callable(pre_collected_decisions)` and passes the result as `intake_callable` to `Facade.run_4a()`.

**AC-C.3** — When `pre_collected_decisions` is `None` (existing default), behavior is unchanged — existing stub/test path remains valid (no regression on 32-1 tests).

**AC-C.4** — After `Facade.run_4a()` returns the locked plan, the baton handoff (lesson_plan_revision + lesson_plan_digest) reflects the locked plan's values — same contract as 32-1 AC-B.3.

### AC-D: Log correctness after full 04A production run

**AC-D.1** — After invoking `route_step_04_gate_to_step_05()` with `pre_collected_decisions` for 5 in-scope + 3 out-of-scope units, reading the lesson plan log must satisfy **all** of:
- Exactly 8 `plan_unit.created` events.
- Exactly 8 `scope_decision.set` events (one per unit, including out-of-scope).
- Exactly 1 `plan.locked` event.
- **Event ordering:** `plan.locked` index > max(all `scope_decision.set` indices). A `plan.locked` event emitted before all `scope_decision.set` events is a correctness defect — the test must assert ordering, not just count.
- All event `unit_id` values match the unit_ids from the pre_collected_decisions dict exactly.

**AC-D.2** — Out-of-scope unit rationales are stored verbatim in their `scope_decision.set` events — no stripping, no empty-string substitution, no truncation. Rationale strings up to at least 10,000 characters must survive the full emission + log + read-back cycle intact.

**AC-D.3** — `LessonPlanLog.latest_plan_revision()` returns a revision ≥ 1 after the locked plan.

### AC-E: No cross-boundary contamination

**AC-E.1** — `hil_intake.py` does NOT import from `marcus.intake.*` (Intake boundary isolation). An AST-based contract test must assert this — a source comment or docstring prohibition has no enforcement power. The test must fail CI if the import appears. Additionally: `hil_intake.py` must not import `LessonPlanLog` directly (defense-in-depth for AC-E.2 — if the callable can't reference the log class, it can't write to it).

**AC-E.2** — `MarcusPreCollectedIntakeCallable` does NOT write directly to `LessonPlanLog` — event emission is the loop's responsibility (AC from 30-3a preserved). A mock-patch test asserting `LessonPlanLog.append_event` (or equivalent write method) is never called during callable execution covers this.

**AC-E.3** — No Maya-facing string in `hil_intake.py` (error messages, docstrings surfaced to operators) contains the words "intake", "orchestrator", or "dispatch" (R1 amendment 17 — Voice Register). A test must instantiate `MissingIntakeDecisionError` and assert the `.args[0]` message contains none of the forbidden terms.

---

## Implementation Notes

### File layout

```
marcus/
  orchestrator/
    hil_intake.py          ← NEW (this story)
    workflow_runner.py     ← MODIFY: add pre_collected_decisions keyword-only param
    loop.py                ← NO CHANGE
    dispatch.py            ← NO CHANGE
    fanout.py              ← NO CHANGE
tests/
  test_hil_intake.py       ← NEW (this story)
  contracts/
    test_hil_intake_boundary.py  ← NEW (AC-E AST contracts)
```

### IntakeCallable type (from loop.py — import, do NOT redefine)

```python
# IntakeCallable lives in marcus/orchestrator/loop.py — NOT in marcus/intake/
# Verify this import resolves before writing any code:
from marcus.orchestrator.loop import IntakeCallable, FourAState
```

**Verify the import resolves:** `IntakeCallable` is defined in `marcus/orchestrator/loop.py`. If it were under `marcus/intake/`, AC-E.1 would prevent importing it. Confirm the canonical home is `marcus.orchestrator.loop` before opening `hil_intake.py`.

### ScopeDecision construction (correct fields per schema)

```python
from marcus.lesson_plan.schema import ScopeDecision

# ALWAYS construct a new instance — never alias or mutate state's existing decisions
decision = ScopeDecision(
    state="ratified",
    scope=scope_value,       # "in-scope" | "out-of-scope" | "delegated" | "blueprint"
    proposed_by="operator",
    ratified_by="maya",
)
# ScopeDecision has extra="forbid" — do NOT pass modality, decided_by, or any undeclared field
```

### Pre-collected decisions format

```python
decisions = {
    "u-01": ("in-scope", "Motion candidate — video with practitioners in motion."),
    "u-02": ("in-scope", ""),                    # empty rationale is valid
    "u-03": ("out-of-scope", "Learner activity — not a produced slide."),
    "u-04": ("in-scope", "Cluster head."),
    "u-05": ("in-scope", "Innovation mindset framework."),
    "u-06": ("out-of-scope", "Curated resource reference — not a produced slide."),
    "u-07": ("in-scope", "Likely singleton. Recap content."),
    "u-08": ("out-of-scope", "Assessment artifact — not a produced slide."),
}
```

Rationale strings are passed through verbatim — the callable does NOT strip, coerce, or parse them. If operator code provides a string with leading/trailing whitespace, that whitespace is part of the rationale.

### Trial log reset procedure (for use after this story lands)

**When to invoke:** Before resuming trial run C1-M1-PRES-20260419 at Step 04A — once and only once, immediately before re-running Step 04A with the correct plan units. Marcus confirms with the operator before invoking (default `confirm=False` enforces this).

```python
from marcus.orchestrator.hil_intake import reset_lesson_plan_log
from pathlib import Path

bundle = Path("course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419-motion")
archived = reset_lesson_plan_log(bundle, confirm=True)
print(f"Stale log archived to: {archived}")
# → lesson-plan-log.STALE-20260419T221305_423817.jsonl
```

Then re-invoke `route_step_04_gate_to_step_05()` with the real plan units. The new log will contain only the correct run's events.

---

## Tests Specification

**K = 7, target 9-10 collecting tests.** (K elevated from 6 per party-mode R1 — Murat binding rider: log-contamination risk profile warrants reset→run integration test + ordering + disjoint + idempotent reset. 10 distinct test behaviors identified.)

| Test ID | Description | Type |
|---|---|---|
| AC-T.1 | `build_hil_intake_callable` returns callable; invoked with known unit_id returns `(ScopeDecision, rationale)` with rationale verbatim; returned ScopeDecision is a fresh instance (not aliased from state) | unit |
| AC-T.2 | Rationale verbatim: 5 parametrized cases — empty string, emoji, 10K chars (assert full length survives log round-trip), non-ASCII, leading/trailing whitespace preserved. Cases injected directly into dict, NOT via any normalizing helper | parametrized unit (5 cases) |
| AC-T.3 | Missing unit_id raises `MissingIntakeDecisionError`; `str(error)` contains none of {"intake", "orchestrator", "dispatch"}; message is human-readable natural language | unit |
| AC-T.4 | `reset_lesson_plan_log` without `confirm=True` raises `LogResetNotConfirmedError`; with `confirm=True` archives file at `STALE-<timestamp>` path, archive exists at returned path, original is gone | unit |
| AC-T.5 | `reset_lesson_plan_log` on missing log returns `None` (idempotent) | unit |
| AC-T.5b | Idempotent double-reset: two successive resets produce two distinct archive paths; second call on already-reset directory (no log) returns `None` | unit |
| AC-T.6 | Full 5+3 loop via `route_step_04_gate_to_step_05(pre_collected_decisions=...)`: exactly 8 plan_unit.created + 8 scope_decision.set + 1 plan.locked events; plan.locked index > max(scope_decision.set indices); real FourALoop execution (not mocked loop) | integration |
| AC-T.7 | Log unit_ids after full run: `set(log_unit_ids) == set(pre_collected_decisions.keys())`; and `set(KNOWN_FIXTURE_IDS).isdisjoint(set(log_unit_ids))` — explicit contamination exclusion | integration |
| AC-T.8 | Reset→run recovery: after `reset_lesson_plan_log(confirm=True)` on a contaminated log, a subsequent 5+3 run produces a log containing ONLY the new run's events (no stale events from prior run) | integration |
| AC-T.9 | AST contracts: `hil_intake.py` has no `import` from `marcus.intake.*`; `hil_intake.py` has no direct `import` of `LessonPlanLog`; `MissingIntakeDecisionError` message has no forbidden tokens | contract |

---

## Post-Dev Review Record

*To be completed by dev agent after implementation.*

### G6 Three-Layer bmad-code-review

- Blind Hunter findings:
- Edge Case Hunter findings:
- Acceptance Auditor findings:
- Triage (PATCH / DEFER / DISMISS):

### Verification

- Governance validator: [ ] PASS
- Focused test suite: [ ] N passed / 0 failed
- Full regression: [ ] N passed / 0 failed
- Ruff clean: [ ]
- Pre-commit clean on touched files: [ ]

### Dev Agent Notes

*Surprises, scope discoveries, deferred items.*

---

## Definition of Done

- [ ] `marcus/orchestrator/hil_intake.py` ships with `MarcusPreCollectedIntakeCallable`, `build_hil_intake_callable()`, `reset_lesson_plan_log()`, `MissingIntakeDecisionError`, `LogResetNotConfirmedError`
- [ ] `workflow_runner.py` `route_step_04_gate_to_step_05()` accepts keyword-only optional `pre_collected_decisions`; call-site audit confirmed clean before modification
- [ ] All ACs AC-A through AC-E satisfied
- [ ] K=7 floor cleared; 9-10 collecting tests
- [ ] Single-gate `bmad-code-review` layered pass (Blind + Edge + Auditor)
- [ ] Governance validator PASS
- [ ] Sprint-status updated: `32-5-step-04a-production-hil-intake-callable: done`
- [ ] Trial log reset procedure confirmed executable against actual bundle
