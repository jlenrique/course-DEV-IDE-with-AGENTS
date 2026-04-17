# Story 26.6: Marcus Production-Readiness Capabilities

**Status:** ready-for-dev
**Created:** 2026-04-17 (via pretrial-prep run charter + two party-mode rounds)
**Epic:** 26 (BMB Sanctum Migration — Companion Stories)
**Branch:** `dev/epic-26-pretrial-prep`

## Story

As **Marcus** (the SPOC orchestrator), I want four production-readiness capabilities registered in my sanctum (**PR-PF, PR-RC, PR-HC, PR-RS**) with verbose landing-point shape (`ask → default/prior → recommend → proceed?`), so that the operator fires trial production runs without authoring `run-constants.yaml` manually from the prompt pack — eliminating the schema-drift vector that halted the 2026-04-17 APC C1-M1 Tejal trial at Prompt 1.

Scope split per scope-confirmation party consensus (2026-04-17):
- **Full implementation:** PR-PF (Preflight) + PR-RC (Run-Constants author+validate)
- **Stubs with pinned contracts + xfail tests:** PR-HC (Health Check) + PR-RS (Run Selection) — full impl deferred to follow-up story 26-10

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1** Authoring `run-constants.yaml` via PR-RC `execute` mode produces a file that `scripts/utilities/run_constants.py` (`parse_run_constants`) and the pipeline's `emit-preflight-receipt.py` accept on first invocation (exit 0, receipt emitted). **This is the direct fix for the 2026-04-17 Prompt 1 halt.**
2. **AC-B.2** A dry-run of Prompt 1's preflight gate, fed a PR-RC-authored `run-constants.yaml` fixture, returns the PASS signature the halted trial required. Trial-restart proxy without firing the trial.
3. **AC-B.3** Invoking PR-HC or PR-RS returns a structured `NOT_YET_IMPLEMENTED` return envelope carrying the stub's contract ID. Stubs MUST be operator-observable (no silent no-ops).
4. **AC-B.4** Preflight receipt schema matches the schema Prompt 2 consumes (contract-parity check across stage boundary).

### Test (AC-T.*)

1. **AC-T.1** `@pytest.mark.trial_critical` — PR-RC `summarize` mode returns canonical lowercase-nested schema preview. Unit test parametrized over 4 input variants: mixed-case keys, schema aliases, missing-optional fields, fully-populated.
2. **AC-T.2** `@pytest.mark.trial_critical` — PR-RC `execute/validate` rejects the captured 2026-04-17 Prompt-1 failure fixture (UPPERCASE-flat schema) with a structured error surface naming the drift. Regression test; fixture lives at `tests/marcus_capabilities/fixtures/halt-2026-04-17-prompt1.yaml`.
3. **AC-T.3** PR-PF wraps `scripts/utilities/app_session_readiness --with-preflight` and propagates non-zero exit into the `errors[]` envelope field. Subprocess integration test; mocks the underlying readiness call via a patched subprocess runner — does NOT shell out to a real `app_session_readiness` in CI. Uses `sys.executable -m`, explicit `cwd=tmp_path`.
4. **AC-T.4** `@pytest.mark.trial_critical` — PR-HC + PR-RS stubs are registered in the capability router and return `{status: error, errors: [{code: "NOT_YET_IMPLEMENTED", ...}]}` envelope. Unit routing test.
5. **AC-T.5** `@pytest.mark.trial_critical` — All 4 capability scripts emit an identical return-envelope shape (`status, capability_code, run_id, result, landing_point, errors, telemetry`). Shared parametrized contract test over `CAPABILITY_REGISTRY`. Tests envelope shape only, not capability logic.
6. **AC-T.6** PR-HC + PR-RS xfail behavioral tests exist in `tests/marcus_capabilities/test_stubs.py` and are discovered by `pytest --collect-only`. Placeholders for 26-10 follow-up.
7. **AC-T.7** PR-RC `execute` is idempotent: re-authoring the same constants yields byte-equal output. Unit test via hash-compare.
8. **AC-T.8** `@pytest.mark.trial_critical` — Capability router raises `UnknownCapability` exception on typo (`PR-PFT` or empty string). Unit negative test.

**Coverage:** No `pytest --cov` gating for 26-6 (per John's "measure post-trial first" position). Coverage diagnostic-only.

### Documentation (AC-D.*)

1. **AC-D.1** Strip "Run Constants" and "Initialization Instructions" sections from `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` (currently lines ~18–70). Replace with this redirect stub:
   > **Marcus capabilities moved.** Readiness/execution checks (PR-PF, PR-RC, PR-HC, PR-RS) now live in [`docs/dev-guide/marcus-capabilities.md`](../dev-guide/marcus-capabilities.md). Pack doc keeps only operator-facing prompts; capability mechanics are Marcus's concern.

2. **AC-D.2** Archive stripped content verbatim at `docs/workflow/archive/prompt-pack-preprompt-2026-04.md` with a 4-line header: source-commit-SHA + strip-date (2026-04-17) + story-ref (26-6) + pointer-to-canonical-location. Body under `## Preserved content` fence.
3. **AC-D.3** New `docs/dev-guide/marcus-capabilities.md`. Top: 3-row (expandable-to-4) index table `| Code | Purpose | Status |`. One flat section per code with: **Purpose** (1 line) · **Invocation** (operator-ask phrasing + Marcus-offer phrasing) · **Inputs** (what Marcus needs from operator) · **Return shape** (fenced YAML) · **When offered** (trigger conditions) · **Stub note** if applicable.
4. **AC-D.4** `docs/dev-guide.md` § "Testing" now also links `dev-guide/marcus-capabilities.md` (alongside `dev-guide/testing.md`).
5. **AC-D.5** `markdown-link-check` (or equivalent lightweight checker) passes on the three touched files: the pack-doc, the archive, and `marcus-capabilities.md`. No broken internal links.
6. **AC-D.6** Marcus `SKILL.md` capability-code table amended to include all 4 PR-* rows pointing at `capabilities/registry.yaml` + a new "Production Readiness Capabilities" section with a pointer-link to `docs/dev-guide/marcus-capabilities.md`.

### Contract Pinning (AC-C.*)

1. **AC-C.1** Invocation envelope shape (sent from Marcus to capability script):
   ```yaml
   capability_code: PR-PF          # required, must match registry
   mode: summarize | execute       # required
   args: {}                        # capability-specific, schema-validated
   context:                        # optional
     run_id: <uuid>                # optional
     bundle_path: <path>           # optional
     invoked_by: marcus            # always "marcus" in v0.2
   idempotency_key: <hash>         # optional; args+run_id hash
   ```
2. **AC-C.2** Return envelope shape (emitted from capability script to Marcus):
   ```yaml
   status: ok | error | partial    # required
   capability_code: PR-PF          # required
   run_id: <uuid>                  # echoed from invocation
   result: {...}                   # capability-specific payload on status=ok
   landing_point:                  # verbose-posture payload for Marcus to render
     bundle_path: <path>
     manifest: {...}
     sha256: <hex>
   errors:                         # populated when status != ok
     - code: <CONST>
       message: <human>
       remediation: <human>
   telemetry:                      # always present
     duration_ms: <int>
     stage_counts: {...}
   ```
3. **AC-C.3** Capability scripts exit **0** on capability-level failure (errors populated in return envelope). Non-zero exit is reserved for envelope-contract violations (script bug, not capability bug). No Python exceptions cross the Marcus boundary — all paths return an envelope.
4. **AC-C.4** `skills/bmad-agent-marcus/capabilities/registry.yaml` enumerates all 4 codes with `{description, script_module, schema_path, full_or_stub}` entries. `schemas/pr_*.yaml` files exist for each code and validate args/result shape.

## Tasks / Subtasks

- [ ] **Task 1 — Shared infrastructure + registry** (AC-C.1, C.2, C.4, T.5, T.8)
  - [ ] Create `scripts/marcus_capabilities/__init__.py` + `_shared.py` (landing-point dataclass, dual-mode CLI wrapper, stdout-JSON emitter, stderr logger)
  - [ ] Create `scripts/marcus_capabilities/registry.py` with `CAPABILITY_REGISTRY: dict[str, RegistryEntry]`
  - [ ] Create `skills/bmad-agent-marcus/capabilities/registry.yaml` — YAML canonical source
  - [ ] Create `skills/bmad-agent-marcus/capabilities/schemas/` with 4 schema files
  - [ ] Write `tests/marcus_capabilities/test_registry.py` (completeness: all 4 codes present, schema files readable)
  - [ ] Write `tests/marcus_capabilities/test_landing_point_contract.py` (parametrized × 4 caps; envelope shape only)
  - [ ] Write `tests/marcus_capabilities/test_router_negative.py` (AC-T.8 UnknownCapability)

- [ ] **Task 2 — PR-HC + PR-RS stubs** (AC-B.3, T.4, T.6)
  - [ ] `scripts/marcus_capabilities/pr_hc.py` — stub: returns envelope `{status: error, errors: [{code: NOT_YET_IMPLEMENTED, capability_code: PR-HC, follow_up_story: 26-10}]}`
  - [ ] `scripts/marcus_capabilities/pr_rs.py` — same stub shape for PR-RS
  - [ ] `tests/marcus_capabilities/test_stubs.py` — unit routing + xfail behavioral placeholders

- [ ] **Task 3 — PR-PF (Preflight)** (AC-B.4 partial, T.3)
  - [ ] `scripts/marcus_capabilities/pr_pf.py` — summarize + execute modes wrapping `app_session_readiness --with-preflight`
  - [ ] Summarize mode: renders current readiness state + the preflight plan; no side-effects
  - [ ] Execute mode: invokes readiness via `sys.executable -m scripts.utilities.app_session_readiness --with-preflight --json-only`; parses exit code + JSON; populates return envelope
  - [ ] `tests/marcus_capabilities/test_pr_pf.py` — subprocess test with mocked runner, envelope shape assertions

- [ ] **Task 4 — PR-RC (Run-Constants author + validate)** (AC-B.1, B.2, T.1, T.2, T.7)
  - [ ] `scripts/marcus_capabilities/pr_rc.py` — summarize + execute(author) + execute(validate) sub-modes
  - [ ] Summarize mode: renders canonical lowercase-nested YAML preview from operator-provided args; calls `run_constants.parse_run_constants()` internally to confirm shape before presenting
  - [ ] Execute(author) mode: writes canonical `run-constants.yaml` to `bundle_path`; round-trips through `parse_run_constants` to confirm validity
  - [ ] Execute(validate) mode: reads existing file; delegates to `run_constants.parse_run_constants`; returns structured error surface on failure
  - [ ] `tests/marcus_capabilities/fixtures/halt-2026-04-17-prompt1.yaml` — the captured UPPERCASE-flat input that failed
  - [ ] `tests/marcus_capabilities/test_pr_rc.py` — 4-variant parametrized summarize test, halt-fixture regression, idempotency hash-compare, schema-parity-to-Prompt-2 check

- [ ] **Task 5 — Marcus SKILL.md integration** (AC-D.6)
  - [ ] Amend capability-code table with PR-* rows
  - [ ] Add "Production Readiness Capabilities" section with pointer to `docs/dev-guide/marcus-capabilities.md`
  - [ ] Invocation example referencing `python -m scripts.marcus_capabilities.<code>`

- [ ] **Task 6 — Doc surgery + archive + dev-guide** (AC-D.1 through D.5)
  - [ ] Strip pre-prompt sections from pack doc; replace with redirect stub
  - [ ] Write `docs/workflow/archive/prompt-pack-preprompt-2026-04.md` with required header + verbatim preservation
  - [ ] Write `docs/dev-guide/marcus-capabilities.md` per AC-D.3 structure
  - [ ] Update `docs/dev-guide.md` Testing section link block
  - [ ] Run `markdown-link-check` (or equivalent) on all three files; fix any broken links

- [ ] **Task 7 — Final verification**
  - [ ] `pytest` full suite green
  - [ ] `pytest -m trial_critical` green (expected 97 + 5 new trial_critical = ~102 tests)
  - [ ] Pre-commit hooks pass (ruff + orphan-check + co-commit)
  - [ ] All AC-B, AC-T, AC-D, AC-C boxes checked in this artifact's Review Record

## Dev Notes

### Architecture guardrails (from green-light party consensus)

- **Marcus is SPOC.** All HIL landing points belong to Marcus; specialists hand off through him. Capabilities live in Marcus's sanctum, not distributed across specialists. See `memory/feedback_landing_point_posture.md`.
- **Verbose landing-point posture.** Every operator-facing landing point must: (1) ask when options exist, (2) display default/prior value, (3) offer a recommendation or caution. Shape: `ask → default/prior → recommend → proceed?`. This means each capability's summarize-mode output must be rich enough for Marcus to render the verbose turn without re-querying the script.
- **Registry-driven extensibility.** New capability = new registry entry + schema file. Contract envelope fields NEVER change. The 14 downstream agent migrations inherit the pinned contract from this story.
- **Two-location split:**
  - Contract/schemas → `skills/bmad-agent-marcus/capabilities/` (sanctum-owned, BMB conformance; schemas are behavior)
  - Deterministic scripts → `scripts/marcus_capabilities/` (implementation detail; imports schemas from sanctum)
- **No exceptions cross the Marcus boundary.** All capability outcomes return an envelope. Scripts exit 0 on capability-level failure. Non-zero exit = contract violation (script bug) only.

### Source tree (new + touched)

**NEW:**
- `scripts/marcus_capabilities/` (package: `__init__.py`, `_shared.py`, `pr_pf.py`, `pr_rc.py`, `pr_hc.py`, `pr_rs.py`, `registry.py`)
- `skills/bmad-agent-marcus/capabilities/registry.yaml`
- `skills/bmad-agent-marcus/capabilities/schemas/pr_pf.yaml`, `pr_rc.yaml`, `pr_hc.yaml`, `pr_rs.yaml`
- `tests/marcus_capabilities/` (`test_pr_pf.py`, `test_pr_rc.py`, `test_stubs.py`, `test_registry.py`, `test_landing_point_contract.py`, `test_router_negative.py`, `fixtures/halt-2026-04-17-prompt1.yaml`)
- `docs/dev-guide/marcus-capabilities.md`
- `docs/workflow/archive/prompt-pack-preprompt-2026-04.md`

**EDIT:**
- `skills/bmad-agent-marcus/SKILL.md` (capability-code table + new Production Readiness section)
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` (strip pre-prompt sections; replace with redirect stub)
- `docs/dev-guide.md` (Testing section link block)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (flip `26-6-...: ready-for-dev` → `done` at closure; update `last_updated`)

### Testing standards (from Murat's green-light guardrails)

- **Unit-level preferred.** No E2E tests in this story.
- **Subprocess tests** (only AC-T.3) must: invoke via `sys.executable -m <module>`, set `cwd=tmp_path`, mock the underlying readiness call (don't shell out to real `app_session_readiness` in CI). Mock at the subprocess boundary — test the wrapper contract, not downstream script behavior.
- **Filesystem writes** use `tmp_path` always; never repo-relative.
- **No sleeps, no network, no clock** in the test paths.
- **Zero flakiness tolerance.** A flaky test is quarantined on first failure and fixed within 48h or deleted. Tests that lie sometimes are worse than no tests. See `memory/feedback_regression_proof_tests.md`.
- **`trial_critical` marker** applied via module-level `pytestmark = pytest.mark.trial_critical` on: test files covering AC-T.1, T.2, T.4, T.5, T.8 (i.e., `test_pr_rc.py`, `test_stubs.py` for routing subset, `test_landing_point_contract.py`, `test_router_negative.py`).
- **Pre-commit regimen** active: ruff + orphan-check + co-commit invariant. The co-commit invariant requires any `.py` change under `scripts/` or `skills/` to be accompanied by test changes — implementation and tests MUST ship in the same commit.

### Project Structure Notes

- Registry-split rationale (Winston + Amelia synthesis): capabilities are behavior contracts (sanctum), deterministic scripts are implementation (scripts/). Scripts import schemas from the sanctum via `yaml.safe_load(project_root() / "skills/bmad-agent-marcus/capabilities/schemas/pr_*.yaml")`. No hardcoded schemas in scripts.
- **No new scaffold version** needed. 26-6 adds capabilities *on top of* the migrated Marcus sanctum; it does not touch `scripts/bmb_agent_migration/init_sanctum.py` (that's 26-5 preservation territory).
- **No collision with Story 26-5** (scaffold preservation, backlog). The PR-* capabilities are Marcus-only — not inherited by the scaffold templates the 14 downstream migrations use. Adding capabilities to Marcus does not conflict with eventual scaffold-preservation `--force` semantics.

### References

- **Run charter:** [run-charters/pretrial-prep-charter-20260417.md](run-charters/pretrial-prep-charter-20260417.md) §1 (scope), §12 (scope-confirmation party consensus)
- **Epic 26 artifact:** [epic-26-bmb-sanctum-migration.md](epic-26-bmb-sanctum-migration.md) § "Companion stories"
- **2026-04-17 trial halt runbook:** [trial-run-c1m1-tejal-20260417.md](trial-run-c1m1-tejal-20260417.md) — the Prompt 1 halt that PR-RC directly fixes
- **Run-constants validator:** [scripts/utilities/run_constants.py](../../scripts/utilities/run_constants.py) — lines 96–99 for `_require_non_empty_str` required-field enforcement; lines 243+ for `parse_run_constants`
- **Session readiness script:** [scripts/utilities/app_session_readiness.py](../../scripts/utilities/app_session_readiness.py) — the runner PR-PF wraps
- **Prompt pack to surgery:** [docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](../../docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md) — lines 18–70 for Run Constants + Initialization Instructions sections
- **Existing contract test pattern:** [tests/contracts/test_pack_doc_matches_schema.py](../../tests/contracts/test_pack_doc_matches_schema.py) — thin L1-W lockstep test shipped in `a944189`; PR-RC summarize-test should co-evolve with it
- **Marcus SKILL.md:** [skills/bmad-agent-marcus/SKILL.md](../../skills/bmad-agent-marcus/SKILL.md) — capability-code table to amend
- **Dev-guide testing doc:** [docs/dev-guide/testing.md](../../docs/dev-guide/testing.md) — regimen (co-commit invariant, orphan detection, cadence, trial_critical marker usage)
- **Landing-point posture:** memory `feedback_landing_point_posture.md` — verbose shape discipline
- **Production-run speed target:** memory `project_production_run_speed_target.md` — trial tests OK, real runs test-free
- **Regression-proof tests:** memory `feedback_regression_proof_tests.md` — never leave tests failing on master

### Non-goals (explicit, per John's green-light)

- **No PR-HC / PR-RS full implementation.** Stubs with pinned contracts and xfail tests only. Full impl lives in follow-up story 26-10.
- **No new contract fields** beyond the 6-field invocation + 7-field return envelope in AC-C.1/C.2. Extensibility via registry entries, not contract expansion.
- **No Irene-side changes.** 26-6 is Marcus-scoped.
- **No trial execution** in this story. AC-B.2's "trial-restart proxy" is a dry-run against the captured fixture, not a live trial.
- **No scaffold v0.3.** 26-4 scaffold v0.2 is the current ceiling.
- **No `MC-*` capability-code rename.** PR-* is grandfathered. Naming convention for future families (MC-EX-*, MC-MON-*) is a separate follow-up story, filed after 26-6 closes.
- **No `pytest --cov` gating.** Coverage measurement deferred per John's "measure post-trial first" position.

## Dev Agent Record

### Agent Model Used

_(filled by dev-story at implementation time)_

### Debug Log References

### Completion Notes List

### File List

### Review Record

_(filled after bmad-code-review adversarial pass)_

**Layered review results:**
- Blind Hunter findings: _(tbd)_
- Edge Case Hunter findings: _(tbd)_
- Acceptance Auditor findings: _(tbd)_
- MUST-FIX remediated: _(tbd)_
- SHOULD-FIX remediated / deferred: _(tbd)_

**BMAD closure criteria (per `feedback_bmad_workflow_discipline.md`):**
- [ ] All AC-B.*, AC-T.*, AC-D.*, AC-C.* checkboxes green
- [ ] Full pytest suite green (no regressions)
- [ ] `pytest -m trial_critical` green
- [ ] Pre-commit hooks pass (ruff + orphan + co-commit)
- [ ] Party-mode implementation review round captured (consensus: approve)
- [ ] bmad-code-review adversarial pass: MUST-FIX remediated
- [ ] Marcus SKILL.md + `marcus-capabilities.md` cross-references resolvable
- [ ] `sprint-status.yaml` flipped to `done` with `# BMAD done 2026-04-XX: <summary>` comment
- [ ] This story's closure summary appended to Epic 26 roster
