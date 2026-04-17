# Testing — How We Test Here

Single source of truth for the testing regimen on course-DEV-IDE-with-AGENTS.
Audience: operator + any agent building or reviewing code. Policy without an
anchoring doc drifts; this is that anchor.

Regimen authored via party-mode consensus 2026-04-17 (Murat + Winston + Amelia +
John + Paige). Revisit after the first successful trial production run.

## Three tiers of verification

The APP distinguishes three things that are often conflated:

| Tier | What it verifies | When it runs | Examples |
|------|------------------|--------------|----------|
| **Dev-cycle tests** | Code correctness during iteration | Pre-commit (fast subset), PR (full suite) | Unit, contract, behavioral tests under `tests/` + per-skill `scripts/tests/` |
| **Trial-gate tests** | Pre-Prompt-1 trial readiness | Before firing any trial production run | `pytest -m trial_critical` — validators, preflight, pack-schema lockstep |
| **Real-run validators** | In-pipeline production gates | During actual production runs | `emit-preflight-receipt.py`, `validate_fidelity_contracts.py`, gate sidecars. **These are NOT tests** — they're pipeline-embedded gates. |

The 15-minute "real production run" target (see `memory/project_production_run_speed_target.md`)
applies to Tier 3 only. Tier 1 + Tier 2 can and should take as long as they
need — they're how we earn confidence to fire the run.

## Test shapes that co-ship with code

Every behavior-changing commit includes the guard tests. Shape depends on what
changed:

| Shape | When to use | Example |
|-------|-------------|---------|
| **Unit** | Any function with logic worth pinning | `tests/test_progress_map.py::test_extract_section_*` |
| **Contract** | Agent-to-agent interface, schema, or capability code | `tests/contracts/test_pack_doc_matches_schema.py` |
| **Behavioral** | New Marcus landing point, HIL interaction shape | Tests that simulate `ask → default → recommend → proceed?` |
| **Lockstep** | Doc schema vs code schema pairing | Contract test that reads both and asserts alignment |
| **Regression** | Any past-bug fix. Never deleted without explicit justification. | Test named for the incident (e.g., "real-heading shape" guard added after `1572819`) |

Integration + E2E tests run **periodically** (nightly / pre-trial / release) —
they don't co-ship with every commit because they're slower and typically
cover stable seams.

## Co-commit invariant (enforced mechanically)

Commits that modify `.py` files under `skills/` or `scripts/` must also touch
at least one test file. Enforced by [scripts/dev/check_co_commit.py](../../scripts/dev/check_co_commit.py)
wired into `.pre-commit-config.yaml`.

Rationale: yesterday's `1572819` refactor landed on master with 34 orphaned
tests. Social review at team size 1-operator + agents does not scale; mechanical
gates do. The invariant formalizes the operator preference documented in
`memory/feedback_regression_proof_tests.md`.

## Orphan-reference detection

Source refactors that remove a public symbol often leave test files pointing
at the deleted name. The 2026-04-17 `1572819` incident is the canonical case:
`progress_map._parse_epic_labels_from_comments` was removed; 34 test methods
still called it; pytest went red on master.

[scripts/dev/check_orphans.py](../../scripts/dev/check_orphans.py) parses each
test file's AST, finds attribute accesses like `module_alias.NAME`, and
verifies `NAME` still exists on the imported module. Runs in the pre-commit
hook and catches the full defect class (not just import-time errors that
`pytest --collect-only` catches).

## Cadence

| Moment | Runs | Target time |
|--------|------|-------------|
| **Pre-commit** | ruff + orphan check + co-commit invariant | <5s |
| **Per-PR (or pre-push for solo)** | Full `pytest` | ~30s |
| **Pre-trial-run** | `pytest -m trial_critical` | <10s |
| **Nightly (future)** | Full suite + docs-vs-code lockstep sweep | open-ended |
| **Release (future)** | + chaos/perf on Marcus graph | open-ended |

"Pre-PR / pre-push" is solo-operator shorthand: this repo has one human committer,
so pre-push is the last mechanical chance before remote. The hook config lives
in [.pre-commit-config.yaml](../../.pre-commit-config.yaml).

## The `trial_critical` marker

Apply `pytestmark = pytest.mark.trial_critical` (module-level) to any test on
the pre-Prompt-1 trial path. Current seed set:

- `tests/test_run_constants.py` — run-constants validator
- `tests/test_preflight_check.py` — preflight skill
- `tests/test_app_session_readiness.py` — readiness service
- `tests/contracts/test_pack_doc_matches_schema.py` — pack-doc ↔ validator lockstep

Before firing a trial production run, operator runs:

```bash
.venv/Scripts/python -m pytest -m trial_critical
```

All green → fire. Any red → halt, fix, re-run the marker set.

Expand the seed set as trial iterations reveal more critical-path tests. Do
not dump everything into the marker — the point is a fast pre-trial gate.

## Coverage measurement (deferred)

Per John's party-mode position: no defect trace to a missed line yet, so
adding coverage thresholds now is theoretical control. Decision: add coverage
instrumentation *after* the first successful trial run reveals which modules
regress most. When we add it:

- Tool: `pytest-cov` (boring, proven — Winston's principle)
- First threshold: whatever the baseline is on ratchet day. Never decrease.
- Per-module thresholds only on high-risk modules (agent routing, schema
  validators, prompt-pack loaders, Marcus sanctum boundary).

## Evolution-friendly patterns

- **Pin tests to contracts, not implementations.** A test that asserts
  `pm.build_report()["summary"]["done_stories"] == 5` survives refactors that
  rename internal helpers. A test that asserts `pm._helper_v2(x) == "foo"`
  rots on contact.
- **Factory fixtures over fixture trees.** One `make_bundle(**overrides)`
  helper beats 15 nested fixtures that inherit each other.
- **Parametrize over `skills/` glob for cross-agent invariants** (e.g., every
  BMB sanctum must have a `BOND.md`; every SKILL.md must declare capability
  codes). Adding a new agent adds a row to the parametrize matrix, not new
  test functions.
- **No snapshot tests that rot.** If the thing you're snapshotting changes
  frequently with intent, the snapshot test becomes noise. Use schema
  assertions instead.
- **Zero flakiness tolerance.** A flaky test is quarantined immediately and
  fixed within 48h or deleted. Tests that lie sometimes are worse than no
  tests.

## When tests break on master — the three-way classification

Per `memory/feedback_regression_proof_tests.md`, every failing test is
resolved by exactly one of:

1. **Update the test** — new behavior has its own regression surface worth guarding.
2. **Restore the behavior** — test was catching a real bug class that still matters.
3. **Delete the test** — behavior is genuinely gone AND no analogous bug class remains. Requires explicit justification in the commit message.

Never leave tests failing on master. Never silently delete a failing test.

## Cora/Audra coverage of test infrastructure

Cora's harmonization sweep (every scope) unions these paths into Audra's
change window so they stay in lockstep with each other and with canonical
repo SSOTs (sprint-status.yaml, prompt-pack pipeline definition):

- `scripts/utilities/run_hud.py`
- `scripts/utilities/progress_map.py`
- `tests/test_run_hud.py`
- `tests/test_progress_map.py`

See [skills/bmad-agent-cora/references/harmonization-protocol.md](../../skills/bmad-agent-cora/references/harmonization-protocol.md)
and Audra's L1-10 Run HUD Lockstep check.

## Companion docs

- [../../_bmad-output/test-artifacts/test-design-system.md](../../_bmad-output/test-artifacts/test-design-system.md) — the *what*: coverage matrix, ownership, quality gates
- [.pre-commit-config.yaml](../../.pre-commit-config.yaml) — hook wiring
- `memory/feedback_regression_proof_tests.md` — why the regimen is mechanical
- `memory/project_production_run_speed_target.md` — why the 15-min target doesn't mean skipping tests

## Setup (one-time per clone)

```bash
.venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/pre-commit install
```

Verify:

```bash
.venv/Scripts/pre-commit run --all-files
```

Should pass clean against the current tree.
