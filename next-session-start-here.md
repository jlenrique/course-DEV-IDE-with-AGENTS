# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> **Current objective:** Start `29-2-gagne-diagnostician` (5 pts, **dual-gate**, §6-E binding PDG). 29-2 is the next story on the critical path — 29-1 BMAD-closed this session. 29-2 authoring must land the §6-E PDG wiring (5x-consecutive flake gate + Gagné p95≤30s + diagnosis-stability) BEFORE dev-story opens.

## Immediate Next Action (pick-up point)

1. **Run BMAD Session Protocol Session START.**
2. **Confirm branch**: `dev/lesson-planner`. The Epic 31 foundation trio (`31-1`, `31-2`, `31-3`) + Epic 29's first story (`29-1`) are BMAD-closed. 32-2 support-lane closeout is in the worktree. Uncommitted work from this session is load-bearing for 29-2.
3. **Use `_bmad-output/implementation-artifacts/sprint-status.yaml` as the canonical status source.** Epic 29 is `in-progress` (29-1 `done`; 29-2 + 29-3 backlog). Epic 31 remains `in-progress` (31-4 + 31-5 backlog).
4. **Commit hygiene first.** This session's uncommitted work includes: 29-1 full implementation (fit_report.py + 6 test files + __init__.py / event_type_registry.py / log.py / spec edits), 32-2 full closeout (coverage_manifest.py + tests + spec + artifact), plus status-file edits. Recommended approach: two commits — `feat(29-1): BMAD-close fit-report-v1 validator + serializer + emission wiring` and `feat(32-2): BMAD-close plan-ref envelope coverage manifest`. Then a session-wrapup commit for sprint-status + next-session-start-here + SESSION-HANDOFF.md.
5. **Author `29-2-gagne-diagnostician` via `bmad-create-story 29-2-gagne-diagnostician`.** Policy for 29-2 per [docs/dev-guide/lesson-planner-story-governance.json](docs/dev-guide/lesson-planner-story-governance.json):
   - `expected_gate_mode: dual-gate` (R2 party-mode pre-dev green-light round REQUIRED)
   - `schema_story: false`
   - `require_t1_readiness: true`
   - §6-E binding PDG: 5x-consecutive smoke + p95≤30s over 20-run batch + 0-variance-on-taxonomy across 10 runs + per-story `tests_added ≥ 10` MUST be wired BEFORE dev-story begins.
6. **Run the governance validator** on the authored 29-2 spec before dev-story begins. PASS required.
7. **29-1's emission wiring is the import surface 29-2 consumes**: `from marcus.lesson_plan.fit_report import emit_fit_report, validate_fit_report, serialize_fit_report, deserialize_fit_report, StaleFitReportError, UnknownUnitIdError` resolves and all six names work. 29-2's dev-story imports these and wraps Gagné diagnostic logic around them.
8. **Critical-path reminder after 29-2**: `30-1 → 30-2a → 30-2b → 30-3a → 28-1 → 28-2 → 28-3 → 30-5 → 30-3b → 30-4 → 31-4 → 29-3 → 31-5 → 32-1 → 32-3 → 32-4`. (32-2 is BMAD-closed in-worktree — remove from the tail.)

## 29-2 Launch Readiness

`29-2-gagne-diagnostician` is unblocked in principle but gated by §6-E PDG setup.

- **Dependency check**: `29-1` is `done` in-worktree — fit-report surface (validator + serializer + emitter + two exception types + FIT_REPORT_EMITTED_EVENT_TYPE) is imported via `from marcus.lesson_plan.fit_report import ...`. Canonical-caller invariant (AC-B.5.1 on 29-1): Marcus-Orchestrator is sole caller of `emit_fit_report`; 29-2's Irene code MUST NOT import `emit_fit_report` directly — it hands FitReport instances to Marcus. Grep-test `tests/contracts/test_fit_report_canonical_caller.py` enforces.
- **§6-E PDG binding gate** MUST land before 29-2 dev-story opens: the smoke battery (`test_4a_loop_idempotent.py` + `test_trial_run_e2e.py`) must pass 5x-consecutive in CI. Gagné diagnostic pass must hit p95 ≤30s over a 20-run batch with no single run >45s. Diagnosis stability: same input → same `source_fitness_diagnosis` across 10 consecutive runs, 0 variance on taxonomy label. See `_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md` §6-E.
- **29-1 deferred findings may land in 29-2 scope**: `[Review][Defer][#3-dedup]` duplicate `unit_id` entries in `report.diagnoses` — natural home is 29-2's construction layer. See [_bmad-output/maps/deferred-work.md](_bmad-output/maps/deferred-work.md) `## 29-1 code-review deferred findings`.
- Test baseline after 29-1 landing: `--run-live` 1340 passed / 4 skipped / 2 deselected / 2 xfailed / 0 failed (80.67s). Default 1318 passed / 1 skipped / 27 deselected / 2 xfailed / 0 failed.

## Startup Commands

```bash
# Verify branch
git status                 # expect clean on dev/lesson-planner
git log --oneline -5       # expect 696982b / 8b6f6e5 / bfdecde / 21b2d83 / 15f68b1

# Open the canonical sprint status + current plan
cat _bmad-output/implementation-artifacts/sprint-status.yaml
cat _bmad-output/planning-artifacts/lesson-planner-mvp-plan.md
```

## Hot-Start Summary

**Prior session (2026-04-18, `dev/lesson-planner`) — five Lesson Planner stories closed:**

| Story | Commit | Points | Test delta | Summary |
|---|---|---|---|---|
| 31-1 Lesson Plan Schema | `15f68b1` | 5 | +197 | Seven-item absorption (lesson_plan + plan_unit + fit-report-v1 + ScopeDecision state-machine + scope_decision_transition + weather_band + event_type seam + dials-spec.md). 11 R2 riders applied. G5+G6 → 24 APPLY + 12 DEFER + 23 DISMISSED. |
| 31-2 Lesson Plan Log | `21b2d83` | 3 | +99 | Append-only JSONL + single-writer WriterIdentity matrix + assert_plan_fresh staleness detector + named mandatory events + pre_packet_snapshot reserved. 7 R2 riders. G5+G6 → 19 APPLY + 10 DEFER + 20 DISMISSED. |
| 31-3 Registries | `bfdecde` + `8b6f6e5` | 2 | +156 | modality_registry + component_type_registry + ModalityProducer ABC + 3 consumer fixtures. 9 R2 riders. G5+G6 (self-conducted per 2pt pattern-tight) → 6 APPLY + 2 DEFER + 4 DISMISSED. |
| 32-2 Coverage Manifest | worktree | 3 | +10 targeted / +186 focused LP regression | `coverage_manifest.py` landed with explicit 05→13 inventory, AST/import-path-aware `assert_plan_fresh` detection, canonical emitted artifact, and self-conducted post-dev code review (2 APPLY, no defers). `summary.trial_ready` currently remains `false` until downstream emitting stories land. |
| 29-1 fit-report-v1 | worktree | 3 | +15 collecting / +26 pytest nodeids | `marcus/lesson_plan/fit_report.py` (~280 lines): `validate_fit_report` + `serialize_fit_report`/`deserialize_fit_report` + `emit_fit_report` + `StaleFitReportError` + `UnknownUnitIdError` + `FIT_REPORT_EMITTED_EVENT_TYPE`. Pre-dev bmad-party-mode review → 12 APPLY + 1 DISMISS (J-1 relitigated R1 am.5) + 1 DEFER (J-3 partial). Post-dev bmad-code-review three-layer → 0 decision-needed / 3 PATCH (docstring retraction, logger.warning on log=None, Raises block expansion) / 2 DEFER (duplicate unit_id to 29-2, UnknownUnitIdError list-leak to later hardening) / 9 DISMISS per §3 rubric. All PATCHes applied. Discovered cross-cut: `log.py` WRITER_EVENT_MATRIX extended by one row (spec erratum — required by import-time assertion). One pre-existing test UPDATE (amendment-8 equality → subset). Final: --run-live 1340 passed / 0 failed. |

**Governance format fix**: commit `696982b` split `**Status:**` line in 31-3 spec + moved sprint-status inline comment for 31-3 to a YAML comment above the status line — allowed the validator's `accepted_historical_deviation` to activate for story-status=done + sprint-status=done. Validator now PASSES on 31-3.

## Branch Metadata

- **Repository baseline branch**: `master`
- **Current working branch**: `dev/lesson-planner` (created 2026-04-18 from `dev/epic-27-texas-intake` @ `883f742`)
- **Latest commit pushed**: `696982b` (governance format fix)
- **Progress on branch/worktree**: 31-1 / 31-2 / 31-3 done and 32-2 support-lane closeout is present in the worktree. Epic 31 foundation trio complete.
- **Why not merged to master**: Epic 31 is still in-progress (31-4 + 31-5 backlog). Per session-wrapup §12, merge-to-master is default-skipped for scoped checkpoints that should stay isolated on the working branch.

## Support-lane Artifacts (ambient worktree state)

The support lane produced governance infrastructure during this session that is operational on disk but has not yet been committed by the support-lane author:

- **Governance docs** (untracked): `docs/dev-guide/lesson-planner-story-governance.json` · `docs/dev-guide/story-cycle-efficiency.md` · `docs/dev-guide/lesson-planner-story-readiness-checklist.md` · `docs/dev-guide/dev-agent-anti-patterns.md` · `docs/dev-guide/pydantic-v2-schema-checklist.md`
- **Scaffolds** (untracked): `docs/dev-guide/scaffolds/`
- **Validator scripts** (untracked): `scripts/utilities/validate_lesson_planner_story_governance.py` · `scripts/utilities/instantiate_schema_story_scaffold.py` · `scripts/utilities/capture_marcus_golden_trace.py` · `scripts/utilities/validate_marcus_golden_trace_fixture.py`
- **Governance tests** (untracked): `tests/test_lesson_planner_story_governance_validator.py` · `tests/test_story_cycle_efficiency_tools.py`
- **Support-lane specs** (untracked): `_bmad-output/specs/30-1-golden-trace-baseline-capture-plan.md` · `_bmad-output/specs/pre-seed-drafts/` · `_bmad-output/specs/story-cycle-efficiency-remediation-1pager-2026-04-18.md`
- **Cycle-efficiency report** (untracked): `docs/dev-guide/lesson-planner-cycle-efficiency-report-2026-04-18.md`
- **Tooling notes** (untracked): `maintenance/efficiency prompts 2026-04-18.txt`
- **Tracked files modified by support lane (not committed this session)**: `CLAUDE.md` · `.cursor/rules/bmad-sprint-governance.mdc` · `.github/copilot-instructions.md` · `_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md`
- **Fixtures for 30-1 prep** (untracked): `tests/fixtures/golden_trace/` · `tests/fixtures/trial_corpus/`

**Next session should**: consult the support-lane author for commit timing on these files. They are load-bearing for 29-1 (scaffold + validator + anti-patterns checklist) and should land before or alongside 29-1's commit.

## Unresolved Issues / Gotchas for the Next Session

1. **Support-lane ambient worktree state** (see above) — the governance infrastructure used by this session is operational on disk but not committed. If the worktree gets cleaned or the next session starts fresh, these files may disappear. Confirm they persist at session-start.

2. **`dev/lesson-planner` branch is not merged to master**. Epic 31 foundation complete (3 of 5 stories); 31-4 + 31-5 pending. Keep branch isolated until Epic 31 or a broader Lesson Planner milestone closes.

3. **27-2.5 Consensus adapter stays blocked** on the binding 27-2.5 Pre-Development Gate MUST-HAVE (CI 3x-run flake-detection gate must be wired before dev-story starts). Explicitly out of Lesson Planner MVP scope per user directive.

4. **§6 PDG binding gate applies to 29-2** (downstream of 29-1). 5x-consecutive smoke + p95≤30s + diagnosis-stability + per-story tests_added floor MUST be wired before 29-2 opens. 29-1 is upstream — it must not undermine.

5. **30-1 Golden-Trace Baseline** is now captured and validator-clean in the worktree at `tests/fixtures/golden_trace/marcus_pre_30-1/`. It was synthesized from the committed tracked bundle `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409-motion/` against the canonical source `course-content/courses/tejal-APC-C1/APC C1-M1 Tejal 2026-03-29.pdf`. Treat the precondition as satisfied for planning purposes; if the worktree is cleaned before commit, rerun the capture command from the plan doc.

6. **Deferred findings from 31-1/31-2/31-3 G6 reviews** are logged at [_bmad-output/maps/deferred-work.md](_bmad-output/maps/deferred-work.md) under `## 31-1 G5+G6 deferred findings`, `## 31-2 G5+G6 deferred findings`, `## 31-3 G5+G6 deferred findings`. Review the 31-1 and 31-2 subsections if the 29-1 scope touches the same modules (fit-report serializer is in 29-1 scope; 31-1 deferred items may be relevant).

## Context Flags for Session-START

- **Cora §1a tripwire**: NOT fired — this session had no deferred Audra L1/L2 findings. Default `since-handoff` scope fine for any opening `/harmonize`.
- **Stories 31-1 + 31-2 + 31-3 are `done`** in sprint-status. Epic 31 remains in-progress because `31-4` + `31-5` are backlog.
- **Governance validator is active** — run it before treating any Lesson Planner story as `ready-for-dev`.
- **Epic 27**: 27-0/1/2 done; 27-2.5 blocked; 27-3+ deferred. No new work.
- **Epic 28**: 4 stories queued per Amelia's plan; 28-1 Tracy reshape charter blocked on 27-2 (done) + 28-2 dispatcher; 28-3 blocked on 28-2.
- **Epic 29**: `29-1` done in the worktree. `29-2` is NEXT (dual-gate, §6-E binding PDG). `29-3` backlog.
- **Epic 30**: all 7 stories backlog; 30-1 golden-trace baseline PDG is satisfied in the worktree; 30-2a/2b are post-30-1; 30-5 must land before 30-3b.
- **Epic 32**: `32-2` done in the worktree; `32-1`, `32-3`, `32-4` backlog.
- **Test baseline after 29-1 closure**: `--run-live` 1340 / 4 skip / 2 dese / 2 xfail / 0 fail (80.67s); default 1318 / 1 skip / 27 dese / 2 xfail / 0 fail (22.80s).

## Critical-Path Reminder

**Epic 29 is now in-flight (29-1 done, 29-2 next).** 29-2 (gagne-diagnostician, 5pts, dual-gate) is the next story — it consumes 29-1's emission wiring via `from marcus.lesson_plan.fit_report import emit_fit_report, ...`. 29-2's §6-E binding PDG (5x-consecutive flake gate + Gagné p95≤30s + diagnosis-stability 0-variance-on-taxonomy over 10 runs) MUST be wired before dev-story opens.

After 29-2: `30-1` (Marcus duality split — golden-trace baseline PDG already satisfied in the worktree) → `30-2a` → `30-2b` → `30-3a` → `28-1` → `28-2` → `28-3` → `30-5` → `30-3b` → `30-4` → `31-4` → `29-3` → `31-5` → `32-1` → `32-3` → `32-4`. 32-2 is BMAD-closed in-worktree; drop from the tail.
