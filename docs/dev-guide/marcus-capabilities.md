# Marcus Capabilities

Single source of truth for Marcus's **production-readiness** capabilities —
the PR-* code family that replaced the prompt-pack pre-prompt operator
sections in Story 26-6. See also Marcus's built-in conversational capabilities
(CM, PR, HC, MM, SP, SM, SB) documented under
[`skills/bmad-agent-marcus/references/`](../../skills/bmad-agent-marcus/references/).

Every PR-* capability follows the **verbose landing-point posture** (see
operator-local auto-memory `memory/feedback_landing_point_posture.md`):

1. Marcus **asks** when options are present.
2. Marcus **displays** the default or current-run's prior value.
3. Marcus **recommends** (or flags a caution) alongside the ask.
4. Operator approves; Marcus invokes the deterministic script.

Auto-proceed / "set-landings-to-auto" is a future enhancement tracked in the
landing-point-posture memory. Until then: every PR-* landing point is a
verbose turn.

## Index

| Code | Capability | Status | Invocation |
|------|-----------|--------|------------|
| [PR-PF](#pr-pf--preflight) | Preflight — run readiness + preflight suite | **full** | operator asks "run preflight" or Marcus offers |
| [PR-RC](#pr-rc--run-constants) | Run-Constants author + validate | **full** | operator asks "author the run constants" or Marcus offers before Prompt 1 |
| [PR-HC](#pr-hc--health-check-stub) | Health Check | stub (Story 26-10) | registered; returns NOT_YET_IMPLEMENTED |
| [PR-RS](#pr-rs--run-selection-stub) | Run Selection (new vs continue) | stub (Story 26-10) | registered; returns NOT_YET_IMPLEMENTED |

Namespace note: **PR-\*** is a distinct 4-character prefix unrelated to the
single-letter **PR** (progress-reporting) built-in capability. The scaffold's
frontmatter scanner matches `code:` values exactly — no actual collision.

---

## PR-PF — Preflight

**Purpose.** Run the production preflight suite before Prompt 1 so the
operator has signal on whether the session, config, MCP servers, and bundle
are ready to fire a tracked run.

**Invocation.**

- Operator: "Marcus, run preflight" / "Verify readiness" / "Check preflight."
- Marcus offers at natural landing points: opening a new shift, returning
  from a break, after a prior gate flagged readiness concerns.

**Inputs.**

- Optional `args.with_preflight` (bool, default `true`) — if false, runs
  readiness-only.
- Optional `args.json_only` (bool, default `true`) — underlying runner uses
  JSON output.
- Optional `context.bundle_path` — enables `bundle_run_constants` validation
  against the frozen bundle.

**Return shape.**

```yaml
status: ok | error
capability_code: PR-PF
run_id: <echoed from context>
result:
  mode: execute
  returncode: 0
  readiness: {...}          # parsed JSON from app_session_readiness
  preflight_passed: true
landing_point:
  bundle_path: <path>
errors: []                  # populated on non-zero exit: code=PREFLIGHT_FAILED
telemetry:
  cmd: [python, -m, scripts.utilities.app_session_readiness, --with-preflight, --json-only]
  returncode: 0
  duration_ms: <int>
```

**When Marcus offers.** Natural triggers include the Session-Start handshake,
when the operator asks about readiness, when a bundle switch happens, and
before firing a trial production run.

---

## PR-RC — Run-Constants

**Purpose.** Author or validate a bundle's `run-constants.yaml` in the
**canonical lowercase-nested** form the validator at
[`scripts/utilities/run_constants.py`](../../scripts/utilities/run_constants.py)
expects. Direct fix for the 2026-04-17 trial halt at Prompt 1.

**Invocation.**

- Operator: "Marcus, author the run constants" / "Create run-constants.yaml
  for this bundle" / "Validate the existing run constants."
- Marcus offers before Prompt 1 on any new tracked bundle, or when a prior
  receipt showed schema failures.

**Inputs.**

- `args.values` (dict, required for `author`) — canonical field values.
  Marcus accepts UPPERCASE pack-display keys (`RUN_ID`,
  `MOTION_BUDGET_MAX_CREDITS`) and normalizes to lowercase-nested before
  writing.
- `args.target_path` (str, optional) — override write location.
- `args.mode_sub` (str) — `author` (default) or `validate`.
- `context.bundle_path` (required for `author` when `target_path` not given).

**Return shape (author).**

```yaml
status: ok
capability_code: PR-RC
run_id: <echoed>
result:
  mode: execute
  mode_sub: author
  written_path: <abs path>
  run_id_written: C1-M1-PRES-20260418
  bytes_written: <int>
landing_point:
  bundle_path: <path>
  manifest: {written_path: <path>}
  sha256: <hex>              # deterministic: same values → same sha
errors: []
telemetry:
  mode: execute
  mode_sub: author
  duration_ms: <int>
```

**Idempotency.** Re-authoring with the same `values` produces byte-equal
output (sha256 match). Safe to retry.

**When Marcus offers.** Before Prompt 1 on any new bundle; when the
validator rejects an existing file with a drift error; whenever the operator
says a profile or motion budget changed.

---

## PR-HC — Health Check (stub)

**Purpose (planned, Story 26-10).** Quick system-health ping distinct from
the fuller preflight suite — lightweight MCP reachability, API health,
workspace writability.

**Current behavior.** Registered stub. Any invocation (summarize or execute)
returns:

```yaml
status: error
capability_code: PR-HC
errors:
  - code: NOT_YET_IMPLEMENTED
    message: "Capability PR-HC is a registered stub; full implementation is
             scheduled for story 26-10."
    remediation: "Proceed without this capability for now, or request the
                  operator to prioritize story 26-10."
telemetry:
  stub: true
```

**When it ships (Story 26-10).** The stub will be promoted. See the xfail
placeholder test `test_pr_hc_health_report_is_populated` in
[`tests/marcus_capabilities/test_stubs.py`](../../tests/marcus_capabilities/test_stubs.py).

---

## PR-RS — Run Selection (stub)

**Purpose (planned, Story 26-10).** Determine whether a session is opening a
new run or continuing an existing one, and reconcile `state/runtime/` SQLite
state when orphan stages are found. Formalizes the ad-hoc DB-state cleanup
Marcus performed manually at the 2026-04-17 trial open.

**Current behavior.** Registered stub returning NOT_YET_IMPLEMENTED (same
envelope shape as PR-HC above).

**When it ships (Story 26-10).** Stub promotion will add: `args.action`
(`inspect` | `start_new` | `continue` | `cancel_orphans`), `args.run_id`
target, structured run-state inventory, proposed reconciliation plan.

---

## Contract reference (for developers)

- **Markdown capability files** (authoritative, scaffold-discovered):
  [`skills/bmad-agent-marcus/capabilities/pr-*.md`](../../skills/bmad-agent-marcus/capabilities/)
- **Schemas** (args + result shape):
  [`skills/bmad-agent-marcus/capabilities/schemas/pr_*.yaml`](../../skills/bmad-agent-marcus/capabilities/schemas/)
- **Registry** (supplementary programmatic index):
  [`skills/bmad-agent-marcus/capabilities/registry.yaml`](../../skills/bmad-agent-marcus/capabilities/registry.yaml)
- **Deterministic scripts**:
  [`scripts/marcus_capabilities/`](../../scripts/marcus_capabilities/)
- **Tests**:
  [`tests/marcus_capabilities/`](../../tests/marcus_capabilities/)
- **Invocation + return envelope contracts** (pinned — do not alter without
  a story that touches all 14+ agent migrations):
  [`scripts/marcus_capabilities/_shared.py`](../../scripts/marcus_capabilities/_shared.py)
- **Story of record**:
  [`_bmad-output/implementation-artifacts/26-6-marcus-production-readiness-capabilities.md`](../../_bmad-output/implementation-artifacts/26-6-marcus-production-readiness-capabilities.md)

## Related documentation

- [`docs/dev-guide/testing.md`](testing.md) — the regimen (regression-proof
  discipline, `trial_critical` marker, co-commit invariant, orphan detection)
- `memory/feedback_landing_point_posture.md` — verbose posture (operator-local auto-memory)
- `memory/project_production_run_speed_target.md` — 15-min target for real runs, not trials (operator-local auto-memory)
- [`docs/workflow/archive/prompt-pack-preprompt-2026-04.md`](../workflow/archive/prompt-pack-preprompt-2026-04.md) — historical verbatim of the stripped pack sections
