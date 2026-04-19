# Story 33-4: Cora Pre-Closure Block-Mode + Audra L1 Gate Wiring

**Status:** done
**Created:** 2026-04-19 (authored against Epic 33 party-mode consensus — makes the 33-2/33-3 substrate load-bearing)
**Epic:** 33 — Pipeline Lockstep Substrate
**Sprint key:** `33-4-cora-audra-block-mode`
**Branch:** `dev/epic-33-lockstep` (continued from 33-3)
**Points:** 2
**Depends on:** 33-3 (done — regenerated v4.2 is the first green substrate baseline block-mode can gate against)
**Blocks:** 15-1-lite-marcus (meta-test — the block-mode hook must be live for 15-1-lite's substrate-validation to mean anything)
**Governance mode:** **single-gate** — governance/policy story. Updates two SKILL files + lands one new hook script + one contract test + one integration smoke. No schema shapes. Post-dev three-layer `bmad-code-review` (Blind + Edge + Auditor) is the sole review ceremony. BMAD sprint governance per [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance applies; Lesson Planner governance validator does NOT (Epic 33 out of scope).

## TL;DR

- **What:** Promote Cora's pre-closure hook (PC capability in [skills/bmad-agent-cora/SKILL.md](../../skills/bmad-agent-cora/SKILL.md)) from warn-mode default to **block-mode for workflow-stage-touching stories**. Land the hook as executable code at [`skills/bmad-agent-cora/scripts/preclosure_hook.py`](../../skills/bmad-agent-cora/scripts/preclosure_hook.py) (new) with a change-window detector whose path-classification rules come from [`state/config/pipeline-manifest.yaml`](../../state/config/pipeline-manifest.yaml) (the manifest 33-2 authored) — **NOT hardcoded `workflows/` globs**. Wire [`scripts/utilities/check_pipeline_manifest_lockstep.py`](../../scripts/utilities/check_pipeline_manifest_lockstep.py) (landed in 33-2) into the hook as the L1 deterministic gate: non-zero exit code blocks story closure. Update [skills/bmad-agent-cora/SKILL.md](../../skills/bmad-agent-cora/SKILL.md) §HZ + §Capabilities to document the promotion; update [skills/bmad-agent-audra/SKILL.md](../../skills/bmad-agent-audra/SKILL.md) §Capabilities (CA row) to document the L1-wired-into-closure-gate contract. Extend Cora's HUD scope union to include learning-event contract paths so 15-1-lite-marcus's new surfaces are in-scope.
- **Why:** Cora's party-mode self-audit on 2026-04-19 named three failure modes that produced DC-1..DC-5 at session-close: **FM-A** (HZ sweep invocation advisory, not load-bearing), **FM-B** (HUD scope union prose, not wired code), **FM-C** (no SSOT means no check is authoritative). 33-2 closed FM-C (manifest + L1 check); 33-3 exercised the cure on live v4.2; 33-4 closes FM-A by making the hook load-bearing in block-mode AND closes FM-B by extending the scope union to cover 15-1-lite-marcus's incoming contracts. **Without 33-4, the substrate is a paper contract** — warn-mode lets closures proceed even when L1 fails. Block-mode is the governance primitive that makes the substrate self-enforcing.
- **Done when:** (1) `preclosure_hook.py` exists and invokes `check_pipeline_manifest_lockstep.py` as the L1 gate when the change-window is classified as workflow-stage-touching; (2) change-window detector reads path-classification rules from `state/config/pipeline-manifest.yaml` — a new top-level `block_mode_trigger_paths` list declares which manifest-adjacent paths trigger block-mode; (3) warn-mode remains the default for non-workflow-stage edits (prose drift, doc harmonization, test-only changes outside the trigger paths); (4) pre-flight smoke test at `tests/test_pre_closure_hook_block_mode.py` simulates a learning-event-schema edit and asserts block-mode fires; (5) HUD scope union in Cora's SKILL §HZ extends to include `state/config/learning-event-schema.yaml` (path exists once 15-1-lite-marcus lands; until then, the union declares it by path for lockstep-on-arrival); (6) Cora's SKILL + Audra's SKILL updated to reflect the promotion + L1 wiring; (7) K=6 floor cleared at 8-9 collecting tests; (8) single-gate post-dev `bmad-code-review` layered pass (Blind + Edge + Auditor); (9) sprint-status flipped `ready-for-dev → in-progress → review → done`; (10) `bmad-party-mode` green-light before 15-1-lite-marcus opens (party confirms the block-mode hook fires correctly on real workflow-stage diffs).
- **Scope discipline:** 33-4 ships **zero changes to the manifest schema** (33-2's scope; 33-4 only *reads* the manifest's declared trigger paths). 33-4 ships **zero changes to the L1 check** (33-2's scope; 33-4 only *invokes* it). 33-4 ships **zero changes to 33-3's regenerated v4.2** (33-3's scope). The only new code is the hook itself + its detector + its tests + its smoke. SKILL edits are doc-only (no code shipped in skill markdown). **Do not** implement 15-1-lite-marcus's learning-event machinery here (that's its own story — 33-4 only needs to declare the trigger-path for it in the manifest, not author the schema).

## Story

As **Cora (dev-session orchestrator) and Audra (internal-artifact fidelity auditor)**,
we want **our pre-closure hook upgraded from advisory warn-mode to block-mode on workflow-stage-touching stories, with Audra's L1 lockstep check wired in as the deterministic gate and our HUD scope union extended to 15-1-lite-marcus's learning-event contracts**,
So that **the failure modes FM-A (invocation advisory), FM-B (scope union prose), and FM-C (no SSOT) that let DC-1..DC-5 reach session-close 2026-04-19 cannot recur — the substrate 33-2 and 33-3 landed is now self-enforcing through governance, not just available for voluntary use**.

## Background — Why This Story Exists

Cora's 2026-04-19 party-mode self-audit named the failure modes directly:

- **FM-A — HZ sweep invocation was advisory, not load-bearing.** Her SKILL names the lockstep surfaces ("prompt packs, operator cards, structural-walk manifests, Marcus workflow templates") but the close-out hook on 32-1 ran in warn mode; warn warned and closure proceeded. For workflow-stage edits this is the wrong default.
- **FM-B — HUD scope union was described but never wired to a deterministic checker.** "Every sweep unions `run_hud.py`, `progress_map.py`, `tests/test_run_hud.py`, `tests/test_progress_map.py` into Audra's change window" was prose in her SKILL. It was not a function Audra actually ran.
- **FM-C — No SSOT means no check is authoritative even if it runs.** Without `state/config/pipeline-manifest.yaml`, any lockstep check was a three-way string comparison across three files that each believed they were canonical.

33-2 closed FM-C by landing the manifest + the L1 check. 33-3 exercised the cure on live v4.2. **33-4 closes FM-A and FM-B.**

**FM-A closure — block-mode with class discrimination.** Cora's party-mode governance mandate:

> "Block-mode triggers on edits to any path declared in `pipeline-manifest.yaml` as a gate-boundary contract, not only paths under `workflows/`. The change-window detector's path-classification logic is itself declared in the manifest (so adding a new contract surface like learning-events is a manifest edit, not a detector-code edit — this is FM-C's own medicine applied to my own tool)."

Translation: the manifest gains a new top-level field `block_mode_trigger_paths: list[str]` that names the glob patterns Cora's detector treats as workflow-stage-touching. Adding a new contract surface (e.g., `state/config/learning-event-schema.yaml` when 15-1-lite-marcus lands) is a manifest edit — the detector code doesn't change. This is the "FM-C medicine applied to Cora's own tool" — her hook's classification rules are data, not code.

**FM-B closure — wire the scope union as actual code.** The SKILL prose "HUD scope union includes `run_hud.py`, `progress_map.py`, tests/test_run_hud.py, tests/test_progress_map.py" becomes the same `block_mode_trigger_paths` list in the manifest, with the learning-event paths added in preparation for 15-1-lite-marcus. The hook reads this list at run-time; the SKILL's prose becomes a pointer to the manifest, not a duplicated list.

**Warn-mode stays the default** for non-workflow-stage edits per Cora Principle 5 — the common case (prose drift, doc harmonization, test-only changes outside the trigger paths) continues to surface findings without blocking. Only edits intersecting the manifest-declared trigger paths flip to block-mode.

**Audra's CA (closure-artifact audit) wiring.** Audra's SKILL §External Capabilities CA row currently names the CA capability as planned/advisory. 33-4 wires it: when Cora's hook fires in block-mode, it invokes Audra's CA capability, which runs `check_pipeline_manifest_lockstep.py` and requires exit 0 before the hook permits closure. The L1 check's trace output lands at `reports/dev-coherence/<ts>/` per 33-2's AC-B.7.

**Why 2 points (and not 1 or 3):** the hook itself is a small module (change-window detector + L1 invocation + exit-code bubbling + Maya-safe error reporting). The SKILL edits are doc-only. The pre-flight smoke test is a single parametrized scenario. What earns the second point is the **new manifest field** (`block_mode_trigger_paths`) which requires careful R1-level scoping: what patterns do we declare today vs defer? Defaults are the existing HUD scope union + `state/config/pipeline-manifest.yaml` itself + pre-emptive entries for 15-1-lite-marcus. If scope creeps into "let's also add telemetry, cost ledgers, retrospectives to the trigger list" — that's a different story; 33-4 declares the minimum viable set.

## T1 Readiness

- **Gate mode:** `single-gate` — governance story with no new schema shapes, no new contracts beyond wiring existing ones. Post-dev `bmad-code-review` layered pass (Blind + Edge + Auditor) is the sole review ceremony. Not dual-gate because the design decisions (block-mode class discrimination, manifest-driven trigger paths, SKILL updates) were fully resolved in the 2026-04-19 party-mode round — R1/R2 ceremony here would be re-litigation.
- **K floor:** `K = 6` per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 for a 2pt single-gate governance story. Derivation: 1 detector unit test (change-window classification against fixture diffs), 1 hook unit test (block on L1 fail; pass on L1 green), 1 pre-flight smoke (simulates learning-event-schema edit, asserts block fires), 1 warn-mode regression (non-workflow-stage edit stays warn), 1 manifest field validation (`block_mode_trigger_paths` is a list of valid glob patterns), 1 SKILL-consistency contract test (Cora SKILL + Audra SKILL mention block-mode promotion). Sum: 6. Target 8-9 accommodates G6 additions.
- **Target collecting-test range:** 8–9.
- **Realistic landing estimate:** 7-9 at T2-T6 close; 1-2 more possible at G6 remediation.
- **Required readings** (dev agent reads at T1 before any code):
  - [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance — governance umbrella.
  - [skills/bmad-agent-cora/SKILL.md](../../skills/bmad-agent-cora/SKILL.md) full file — current warn-mode contract, HZ capability, Principle 5 (warn-not-block default), Hot-Start Pair Discipline. 33-4's SKILL edits are targeted: §HZ gets a "block-mode promotion" paragraph; §Capabilities PC row updates; Principle 5 gets a bifurcation note (warn default for most edits; block for workflow-stage).
  - [skills/bmad-agent-cora/references/harmonization-protocol.md](../../skills/bmad-agent-cora/references/harmonization-protocol.md) (if exists) — the HZ capability's current spec; 33-4 updates it to name the block-mode promotion.
  - [skills/bmad-agent-cora/references/preclosure-protocol.md](../../skills/bmad-agent-cora/references/preclosure-protocol.md) — the PC capability's current spec; 33-4 updates it to describe block-mode triggering on workflow-stage touches.
  - [skills/bmad-agent-audra/SKILL.md](../../skills/bmad-agent-audra/SKILL.md) full file — L1/L2 principles, CA capability, trace-report format contract. 33-4's SKILL edits are targeted: §Capabilities CA row gets "wired into Cora's block-mode closure gate" language; §External Skills table gets `check_pipeline_manifest_lockstep.py` promoted from planned to active.
  - [skills/bmad-agent-audra/references/closure-artifact-audit.md](../../skills/bmad-agent-audra/references/closure-artifact-audit.md) (if exists) — the CA capability's current spec; 33-4 updates it to name the L1-exit-0 requirement.
  - [state/config/pipeline-manifest.yaml](../../state/config/pipeline-manifest.yaml) (from 33-2) — the manifest whose new `block_mode_trigger_paths` field 33-4 adds.
  - [scripts/utilities/check_pipeline_manifest_lockstep.py](../../scripts/utilities/check_pipeline_manifest_lockstep.py) (from 33-2) — the L1 check the hook invokes.
  - [_bmad-output/implementation-artifacts/33-2-pipeline-manifest-ssot.md](33-2-pipeline-manifest-ssot.md) + [_bmad-output/implementation-artifacts/33-3-regenerate-v42-and-validate.md](33-3-regenerate-v42-and-validate.md) — the substrate stories 33-4 makes load-bearing.
  - [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) — general anti-patterns catalog. Specifically: DO NOT hardcode trigger paths in the detector code (the FM-C-applied-to-Cora's-own-tool guard). DO NOT duplicate the scope union list in SKILL prose AND in the manifest (DRY violation and drift reopener). SKILL prose points at the manifest field by name.
  - [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 (K-floor), §2 (single-gate policy), §3 (aggressive DISMISS rubric).
- **Scaffold requirement:** `require_scaffold: false` — governance story, no schema shape.
- **Runway pre-work consumed:** 33-2 (manifest + L1 check) + 33-3 (regenerated v4.2, first green substrate baseline). If 33-3 closed with a DEFER that leaves the L1 check not-exit-0 on the current repo state, 33-4 cannot close — the block-mode hook invoking a perpetually-failing L1 check would block all future closures. Dev agent verifies L1 exit 0 at T1 before any work.

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — Manifest gains `block_mode_trigger_paths` field.** [`state/config/pipeline-manifest.yaml`](../../state/config/pipeline-manifest.yaml) adds a new top-level key `block_mode_trigger_paths: list[str]` listing glob patterns that trigger block-mode when touched in a diff. Initial list (minimum viable for 33-4): `state/config/pipeline-manifest.yaml`, `scripts/utilities/check_pipeline_manifest_lockstep.py`, `scripts/utilities/run_hud.py`, `scripts/utilities/progress_map.py`, `marcus/orchestrator/workflow_runner.py`, `tests/test_run_hud.py`, `tests/test_progress_map.py`, `docs/workflow/production-prompt-pack-v4.2-*.md`, plus pre-emptive `state/config/learning-event-schema.yaml` + `scripts/utilities/learning_event_capture.py` entries for 15-1-lite-marcus. The manifest's Pydantic loader (`scripts/utilities/pipeline_manifest.py`, from 33-2) is extended to validate the new field — list of non-empty strings, each a valid glob pattern per `fnmatch`. Extension is additive; no existing field changes.

2. **AC-B.2 — Cora's pre-closure hook module lands.** New file [`skills/bmad-agent-cora/scripts/preclosure_hook.py`](../../skills/bmad-agent-cora/scripts/preclosure_hook.py) implements:
   - `classify_change_window(diff_paths: list[str], manifest_path: str = "state/config/pipeline-manifest.yaml") -> Literal["warn", "block"]` — reads the manifest's `block_mode_trigger_paths`, matches each diff path against each glob, returns `"block"` if any match, `"warn"` otherwise.
   - `run_preclosure_check(story_id: str, diff_paths: list[str], *, skip_l1: bool = False) -> PreClosureResult` — the main entry point. Calls `classify_change_window()`; if block-mode, invokes `check_pipeline_manifest_lockstep.py` via subprocess; on exit 0 permits closure; on non-zero exit returns a `PreClosureResult` with `permit_closure: False` + the L1 trace path + a Maya-safe operator message.
   - `PreClosureResult` Pydantic model with `story_id: str`, `classification: Literal["warn", "block"]`, `l1_exit_code: int | None` (None when classification=warn), `l1_trace_path: str | None`, `permit_closure: bool`, `operator_message: str`. `model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)` per 31-1 schema-checklist precedent.
   - Maya-safe error message on block: "Story close-out blocked: lockstep check flagged divergence. See <trace path> for the specific finding." No Intake/Orchestrator/dispatch/facade/loop token leaks (Voice Register discipline borrowed from 30-1 precedent).

3. **AC-B.3 — Hook invokes `check_pipeline_manifest_lockstep.py` via subprocess.** The invocation uses `subprocess.run([sys.executable, "scripts/utilities/check_pipeline_manifest_lockstep.py"], capture_output=True)` and reads the exit code. Rationale: the L1 check has strict exit-code semantics (0/1/2) that the hook must honor; subprocess isolation prevents the hook's Python session state from affecting the check. Hook respects L1 check's trace output path at `reports/dev-coherence/<ts>/`.

4. **AC-B.4 — Warn-mode preserved as default.** If `classify_change_window()` returns `"warn"`, the hook does NOT invoke the L1 check; it emits the existing warn-mode findings via Cora's existing HZ capability surface. `permit_closure: True` is unconditional for warn-mode. Cora Principle 5 preserved for the common case.

5. **AC-B.5 — Pre-flight smoke test simulates learning-event-schema edit.** `tests/test_pre_closure_hook_block_mode.py::test_learning_event_schema_edit_fires_block_mode` constructs a synthetic diff-paths list containing `state/config/learning-event-schema.yaml`; calls `classify_change_window()`; asserts result is `"block"`. Then constructs a synthetic L1-fail scenario (using a fixture manifest that intentionally fails check 3 name-equality); calls `run_preclosure_check()`; asserts `permit_closure: False`. This test is the META-TEST the operator named in the party round — 15-1-lite-marcus's substrate-validation depends on this passing.

6. **AC-B.6 — Pre-flight smoke test simulates warn-mode non-regression.** `tests/test_pre_closure_hook_block_mode.py::test_prose_edit_stays_warn_mode` constructs a diff-paths list containing only files outside the trigger paths (e.g., `docs/project-context.md`, `SESSION-HANDOFF.md`); asserts classification is `"warn"`; asserts `permit_closure: True` unconditionally.

7. **AC-B.7 — Cora SKILL updated.** [skills/bmad-agent-cora/SKILL.md](../../skills/bmad-agent-cora/SKILL.md) edits:
   - §Capabilities table PC row: "triggered by operator intent to flip a story to `done` in `sprint-status.yaml`; invokes Audra closure-artifact audit; **relays finding in warn mode for non-workflow-stage edits; escalates to block mode for workflow-stage-touching stories per `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`** | Load `./references/preclosure-protocol.md`"
   - §HZ capability description: append a sentence "When the change-window intersects `block_mode_trigger_paths` declared in `state/config/pipeline-manifest.yaml`, the pre-closure check runs Audra's `check_pipeline_manifest_lockstep.py` as a deterministic block gate; non-zero exit blocks story closure until remediated."
   - §Principles §5: bifurcation note: "Pre-closure hook is warn-by-default (the common case); block-mode is the narrow exception for workflow-stage-touching stories. Both modes are triggered by the same hook; classification happens at invocation time via `classify_change_window()` in `scripts/preclosure_hook.py`."
   - §References: add pointer to `./scripts/preclosure_hook.py` + `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`.

8. **AC-B.8 — Audra SKILL updated.** [skills/bmad-agent-audra/SKILL.md](../../skills/bmad-agent-audra/SKILL.md) edits:
   - §External Skills table: move `check_pipeline_manifest_lockstep.py` (or whatever line exists post-33-2) from "planned" to "active" status if not already done by 33-2; add a note that the check is invoked via Cora's block-mode pre-closure hook.
   - §Capabilities table CA row: append "block-mode gate wiring: when invoked via Cora's pre-closure hook, CA requires `check_pipeline_manifest_lockstep.py` exit 0 before permitting story closure on workflow-stage-touching stories."

9. **AC-B.9 — HUD scope union extension.** Cora SKILL §HZ capability currently names the HUD scope union as `run_hud.py`, `progress_map.py`, `tests/test_run_hud.py`, `tests/test_progress_map.py`. 33-4 extends this to include `state/config/learning-event-schema.yaml` and `scripts/utilities/learning_event_capture.py` (paths will exist once 15-1-lite-marcus lands; until then, the union declares them by path for lockstep-on-arrival). The union is NOT duplicated in SKILL prose AND in the manifest — SKILL prose names the union and points at the manifest's `block_mode_trigger_paths` list as the load-bearing source; the manifest's list is the single source of truth.

### Contract (AC-C.*)

1. **AC-C.1 — SKILL-manifest consistency.** One contract test at `tests/contracts/test_33_4_skill_manifest_consistency.py::test_cora_skill_hud_scope_union_matches_manifest_trigger_paths` reads both Cora's SKILL §HZ prose AND the manifest's `block_mode_trigger_paths` list; asserts every path the SKILL names as HUD-scope-union is present in the manifest's trigger paths. Catches the drift class where a future SKILL edit adds a path without updating the manifest.

2. **AC-C.2 — No hardcoded trigger paths.** One AST contract test at `tests/contracts/test_33_4_no_hardcoded_trigger_paths.py::test_preclosure_hook_reads_triggers_from_manifest` asserts `skills/bmad-agent-cora/scripts/preclosure_hook.py` does NOT contain any hardcoded path string matching the pipeline-step-id-or-path pattern outside of reading the manifest. This is the "FM-C medicine applied to Cora's own tool" guard — classification rules MUST live in the manifest, not in detector code.

### Test (AC-T.*)

1. **AC-T.1 — `classify_change_window` unit coverage.** Two parametrized tests at `tests/test_preclosure_hook.py`:
   - `test_classify_workflow_stage_paths_returns_block[path]` — parametrized over at least 5 paths from `block_mode_trigger_paths`; asserts each returns `"block"`.
   - `test_classify_non_trigger_paths_returns_warn[path]` — parametrized over at least 3 paths outside the trigger list (e.g., `README.md`, `docs/project-context.md`, `tests/test_unrelated.py`); asserts each returns `"warn"`.

2. **AC-T.2 — `run_preclosure_check` block-on-L1-fail.** One test that patches subprocess to return non-zero exit; calls `run_preclosure_check` with block-classified diff; asserts `permit_closure: False` + trace path captured + operator_message is Voice-Register-clean.

3. **AC-T.3 — `run_preclosure_check` permit-on-L1-pass.** One test that patches subprocess to return 0; calls with block-classified diff; asserts `permit_closure: True` + `l1_exit_code: 0`.

4. **AC-T.4 — `run_preclosure_check` warn-mode short-circuits.** One test that calls with warn-classified diff; asserts L1 check is NOT invoked (subprocess spy records zero invocations); asserts `permit_closure: True`.

5. **AC-T.5 — Learning-event-schema edit triggers block.** Per AC-B.5.

6. **AC-T.6 — Prose edit stays warn.** Per AC-B.6.

7. **AC-T.7 — SKILL-manifest consistency.** Per AC-C.1.

8. **AC-T.8 — No-hardcoded-triggers contract.** Per AC-C.2.

## Tasks / Subtasks

### T1 — Readiness gate (before any code)

- [x] Confirm 33-3 is `done` in [sprint-status.yaml](sprint-status.yaml); verify L1 check (`check_pipeline_manifest_lockstep.py`) exits 0 on current repo state BEFORE any 33-4 code lands.
- [x] Read all required readings enumerated in §T1 Readiness.
- [x] Confirm `state/config/pipeline-manifest.yaml` + the loader at `scripts/utilities/pipeline_manifest.py` exist (from 33-2).
- [x] Confirm Cora's SKILL + Audra's SKILL are readable; note their current Capabilities tables for surgical edits.

### T2 — Extend manifest + loader (AC-B.1)

- [x] Add `block_mode_trigger_paths: list[str]` top-level field to `state/config/pipeline-manifest.yaml` with the minimum viable path list named in AC-B.1.
- [x] Extend `scripts/utilities/pipeline_manifest.py` Pydantic shape: new field `block_mode_trigger_paths: list[str] = Field(default_factory=list)` with field validator asserting each entry is a non-empty string and a valid `fnmatch`-compatible glob pattern.
- [x] Add shape-pin test for the new field at `tests/test_pipeline_manifest_loader.py` (file from 33-2) — field presence + validator rejects empty strings and non-string elements.

### T3 — Land Cora's pre-closure hook (AC-B.2, AC-B.3, AC-B.4)

- [x] Create `skills/bmad-agent-cora/scripts/` directory if absent.
- [x] Land `skills/bmad-agent-cora/scripts/preclosure_hook.py` with:
  - `classify_change_window(diff_paths, manifest_path)` reading manifest's trigger paths.
  - `PreClosureResult` Pydantic model per AC-B.2 spec.
  - `run_preclosure_check(story_id, diff_paths, *, skip_l1)` main entry point.
  - Subprocess invocation of L1 check per AC-B.3.
  - Maya-safe error message on block per AC-B.2.
- [x] Ruff-clean + type-hint-clean.
- [x] Module-level `__all__` exports: `("classify_change_window", "run_preclosure_check", "PreClosureResult")`.

### T4 — Update Cora + Audra SKILLs (AC-B.7, AC-B.8, AC-B.9)

- [x] Apply Cora SKILL edits per AC-B.7 (§Capabilities PC row; §HZ addition; §Principles §5 bifurcation note; §References addition).
- [x] Apply Audra SKILL edits per AC-B.8 (§External Skills check_pipeline_manifest_lockstep.py status promotion; §Capabilities CA row block-mode-gate wiring note).
- [x] Extend Cora SKILL §HZ HUD scope union language to name `state/config/learning-event-schema.yaml` and `scripts/utilities/learning_event_capture.py` (AC-B.9) — with an explicit note that these paths will exist once 15-1-lite-marcus lands; the union declares them by path for lockstep-on-arrival.
- [x] Verify no duplicated list in SKILL prose AND manifest; SKILL points at manifest as the load-bearing source.

### T5 — Tests + smoke (AC-T.1..AC-T.8)

- [x] Land `tests/test_preclosure_hook.py` with AC-T.1 + AC-T.2 + AC-T.3 + AC-T.4.
- [x] Land `tests/test_pre_closure_hook_block_mode.py` with AC-T.5 (learning-event-schema edit fires block) + AC-T.6 (prose edit stays warn).
- [x] Land `tests/contracts/test_33_4_skill_manifest_consistency.py` (AC-C.1 / AC-T.7).
- [x] Land `tests/contracts/test_33_4_no_hardcoded_trigger_paths.py` (AC-C.2 / AC-T.8).
- [x] Focused 33-4 suite: `python -m pytest tests/test_preclosure_hook.py tests/test_pre_closure_hook_block_mode.py tests/contracts/test_33_4_*.py -p no:cacheprovider` — expect green.

### T6 — Close

- [x] Full regression: `python -m pytest -p no:cacheprovider` — expect no new failures vs the 33-3-close baseline.
- [x] Ruff clean on all new modules + tests + touched SKILL files.
- [x] Pre-commit clean on all touched files.
- [x] Layered post-dev `bmad-code-review` (Blind + Edge + Auditor) per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §3. Expected shape: CLEAN PASS (0-1 PATCH / ≤3 DEFER / several DISMISS per aggressive rubric). Any MUST-FIX likely indicates a substrate or SKILL inconsistency; dev agent STOPS and escalates if a reviewer flags a classification-rule bug (that's a FM-C-on-Cora's-own-tool recurrence).
- [x] Update [sprint-status.yaml](sprint-status.yaml) — 33-4 status `ready-for-dev → in-progress → review → done`.
- [x] Log any DEFER decisions to [_bmad-output/maps/deferred-work.md](../maps/deferred-work.md) §33-4.
- [x] Update this spec's §Dev Agent Record + §Post-Dev Review Record sections.
- [x] **`bmad-party-mode` green-light before 15-1-lite-marcus opens** — party confirms the block-mode hook fires correctly on real workflow-stage diffs by running the pre-flight smoke against a committed-but-unclosed 33-4 branch state. This is the gate that unblocks 15-1-lite-marcus's meta-test.

## Known Risks + Kill-Switches

Dev agent STOPS and escalates (does not silently patch) if:

1. **L1 check exits non-zero on current repo state at T1.** 33-3 was supposed to leave it green. If it's red, that's a substrate-level finding routing back to 33-2 or 33-3 reopen. 33-4 cannot land a block-mode hook that would block all future closures.

2. **Manifest loader refuses the new `block_mode_trigger_paths` field.** 33-2's Pydantic shape may have `ConfigDict(extra="forbid")` per 31-1 precedent; the field addition is a schema evolution that 33-2's import-time invariant assertion must accept. If it doesn't, the fix routes back to 33-2 (reopen).

3. **SKILL edit breaks an existing skill invocation.** E.g., if Cora's SKILL is parsed by a skill-loader that requires specific section ordering, the edits here must preserve it. Dev agent runs any skill-loader self-tests before marking T4 done; if a test fails, STOPS.

4. **`tests/test_pre_closure_hook_block_mode.py` META-TEST fails — block-mode doesn't fire on learning-event-schema edit.** This is the headline AC; if it fails after T3+T4 land, the hook is broken. Dev agent STOPS and root-causes — does NOT skip the test or weaken the assertion (the 27-2 pattern).

5. **Discovery of a sixth workflow-stage-touching path set not named in the party-mode round.** E.g., dev agent realizes structural-walk manifests at `docs/structural-walk.md` should also be trigger paths. Route this to party-mode for a consensus vote on scope expansion; do NOT silently add the path in 33-4.

## Dev Notes

### Project Structure Notes

- `skills/bmad-agent-cora/scripts/` is a new directory under the Cora skill. Matches the existing `skills/bmad-agent-marcus/scripts/` pattern. The hook module lives here because it's SKILL infrastructure, not a general-purpose utility.
- `tests/test_pre_closure_hook_block_mode.py` is deliberately named with the **full block-mode phrase** so a future editor grep for "block_mode" finds it immediately. Murat's naming-discipline concern from prior rounds.
- The manifest's `block_mode_trigger_paths` field is a `list[str]` (not `set[str]`) to preserve author ordering — the SKILL prose can cite them in a consistent reading order. The hook's classification is order-independent (glob-match is commutative over the list).

### Alignment Notes

- 33-4 is the FIRST story that makes the substrate from 33-2 + 33-3 *load-bearing*. Every subsequent pipeline edit flows through block-mode. Dev agent authoring 33-4 should treat the hook as a production-path piece of code — it's the guardrail for every future Epic 33+ story.
- The "HUD scope union" language in Cora's SKILL has historical precedent ([skills/bmad-agent-cora/SKILL.md](../../skills/bmad-agent-cora/SKILL.md) §HZ). 33-4 doesn't rename it, just wires it. If a future story wants to rename it (e.g., to "block-mode trigger path set"), that's a SKILL-refactor story outside 33-4's scope.
- Pre-emptive inclusion of `learning-event-schema.yaml` + `learning_event_capture.py` in the manifest's `block_mode_trigger_paths` is deliberate — when 15-1-lite-marcus opens, touching those paths automatically fires block-mode, which is the whole point of the meta-test. Dev agent confirms these paths are in the list before closing 33-4.

### References

- [33-2-pipeline-manifest-ssot.md](33-2-pipeline-manifest-ssot.md) — manifest schema this story extends with one field.
- [33-3-regenerate-v42-and-validate.md](33-3-regenerate-v42-and-validate.md) — first green substrate baseline.
- [skills/bmad-agent-cora/SKILL.md](../../skills/bmad-agent-cora/SKILL.md) — warn-mode default + HZ capability + HUD scope union + Principles.
- [skills/bmad-agent-audra/SKILL.md](../../skills/bmad-agent-audra/SKILL.md) — L1/L2 principles + CA capability + trace-report format.
- [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance — bmad-code-review + party-mode green-light discipline.
- [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) — generic anti-patterns; FM-C-on-Cora's-own-tool guard (no hardcoded classification rules).
- [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) — K-floor + aggressive DISMISS rubric.
- **Epic 33 party-mode consensus (2026-04-19)** — Cora's FM-A / FM-B / FM-C self-audit + governance mandate quoted in §Background. Transcript in session log.

## Dev Agent Record

### Agent Model Used

Codex 5.3

### Debug Log References

- `python -m pytest tests/test_preclosure_hook.py tests/test_pre_closure_hook_block_mode.py tests/contracts/test_33_4_skill_manifest_consistency.py tests/contracts/test_33_4_no_hardcoded_trigger_paths.py tests/test_pipeline_manifest_loader.py -p no:cacheprovider`
- `python -m scripts.utilities.check_pipeline_manifest_lockstep` (post-change PASS)

### Completion Notes List

- Manifest field added: `block_mode_trigger_paths` list with 10 entries.
- Hook module landed at `skills/bmad-agent-cora/scripts/preclosure_hook.py` (block/warn classifier + lockstep subprocess gate).
- SKILL edits applied: Cora (`§Capabilities`, `§HZ`, Principle 5, references) + Audra (`§Capabilities` CA row, external-skill active lockstep gate).
- Pre-flight smoke outcome: block fires on `state/config/learning-event-schema.yaml` edit (AC-B.5 GREEN).
- Warn-mode non-regression: prose edit stays warn and bypasses L1 subprocess (AC-B.6 GREEN).
- Party-mode green-light date: 2026-04-19 (`LEGITIMATE`, unblock for `15-1-lite-marcus`).
- DEFERs logged to [_bmad-output/maps/deferred-work.md](../maps/deferred-work.md) §33-4: `0`.

### File List

- `state/config/pipeline-manifest.yaml` (modified — new top-level `block_mode_trigger_paths` field)
- `scripts/utilities/pipeline_manifest.py` (modified — Pydantic shape extended; shape-pin test added)
- `skills/bmad-agent-cora/scripts/preclosure_hook.py` (new)
- `skills/bmad-agent-cora/SKILL.md` (modified — §Capabilities PC row + §HZ + §Principle 5 + §References)
- `skills/bmad-agent-audra/SKILL.md` (modified — §External Skills + §Capabilities CA row)
- `skills/bmad-agent-cora/references/preclosure-protocol.md` (modified if exists — block-mode trigger described)
- `skills/bmad-agent-cora/references/harmonization-protocol.md` (modified if exists — block-mode promotion noted)
- `skills/bmad-agent-audra/references/closure-artifact-audit.md` (modified if exists — L1 exit-0 requirement noted)
- `tests/test_preclosure_hook.py` (new)
- `tests/test_pre_closure_hook_block_mode.py` (new)
- `tests/contracts/test_33_4_skill_manifest_consistency.py` (new)
- `tests/contracts/test_33_4_no_hardcoded_trigger_paths.py` (new)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (updated — 33-4 status transitions)

## Post-Dev Review Record

### Layered `bmad-code-review` Pass

- **Blind Hunter:** `MUST-FIX=1` (subprocess invocation initially not module-safe), `SHOULD-FIX=1` (Pydantic rebuild for dynamic import context), both patched.
- **Edge Case Hunter:** exercised missing manifest structural path, multi-pattern match short-circuit, and L1 exit `1`/`2` handling in block mode.
- **Acceptance Auditor:** AC coverage complete for 33-4 implementation + contract suite (`22/22 focused tests passing`).
- **Orchestrator triage:** `PATCH=2 / DEFER=0 / DISMISS=0`.

### Party-Mode Green-Light (PRE-15-1-lite-marcus)

Party validated block-mode gate wiring as legitimate and load-bearing for workflow-stage touches.

### Closure Verdict

CLEAN-CLOSE
