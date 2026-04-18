# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> **Current objective:** Commit the uncommitted 27-0 closure work, then open Story 27-2 (scite.ai adapter) via `bmad-create-story`. 27-2 is the first real consumer of the `RetrievalAdapter` ABC from 27-0 and absorbs the AC-B.7 dispatcher-wiring cascade explicitly deferred from 27-0.

## Immediate Next Action (pick-up point)

1. **Run BMAD Session Protocol Session START.**
2. **Commit 27-0.** The prior session BMAD-closed Story 27-0 but did not commit — 15 modified + 24 untracked files sit in the working tree. Stage and commit before any new dev work (single-commit at operator discretion; see Startup Commands below).
3. **Then pivot into `bmad-create-story 27-2-scite-ai-provider`.** Spec at [_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md](_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md) has the Round-3-superseded 382-line pre-reshape content preserved behind a supersession banner; re-expand with the 27-0 contract in hand.

Session START expectations:
- Cora `§1a` gate: **tripwire NOT fired** (prior session's Step 0a ran clean; report at `reports/dev-coherence/2026-04-18-0059/harmonization-summary.md`). Default scope `since-handoff` for any opening `/harmonize`.
- Story 27-0 is **done** in sprint-status; Story 27-2 is **ratified-stub (unblocked)**; Story 27-2.5 is **ratified-stub (unblocked, soft-blocked on 27-2)**. All other Epic 27 stubs unchanged.

## Hot-Start Summary

Prior session (2026-04-18 early hours) closed 27-0 full-stack:

1. **Shape 3-Disciplined retrieval foundation shipped** — 8 new modules under `skills/bmad-agent-texas/scripts/retrieval/` (contracts, base ABC with auto-registry, dispatcher with cross-val merger, hand-rolled JSON-RPC MCP client per Option Y, normalize, refinement_registry, FakeProvider reference adapter, provider_directory operator-amendment). Schema v1.1 additive bump. Audience-segmented retrieval-contract.md. `--list-providers` CLI. MCP configs. CLAUDE.md pointer. Marcus external-specialist-registry breadcrumb.

2. **Operator amendment — Provider Directory (AC-B.8 / B.9 / T.9-11)** — post-green-light fold added runtime `list_providers()` surface with 16 entries (11 locator ready/ratified + 5 retrieval incl. `openai_chatgpt: backlog` forward placeholder per operator directive). Answers "what can Texas fetch?" authoritatively via `python skills/bmad-agent-texas/scripts/run_wrangler.py --list-providers`.

3. **Both BMAD gates GREEN.** Party-mode implementation review (3 GREEN + 1 YELLOW→GREEN after Paige must-fix applied). bmad-code-review layered (5 MUST-FIX + 9 SHOULD-FIX applied; 4 DISMISSED with rationale including AC-B.7 literal dispatcher-wiring deferred to 27-2 per anti-pattern #3 shape-separation; ~22 NITs logged to deferred-work.md).

4. **Tests +70 collecting (target +34). Full suite 1106/2/0.** Ruff clean on 27-0 code.

5. **Forward-design memory** — three distinct missing parameter knobs captured for future epic: enrichment degree (aspirational depth beyond SME), gap-filling (derivative-artifact content demands), evidence-bolster (corroboration via cross-validation).

## Sequenced Implementation Plan for This Session

### Step 1 — Harmonization check (default since-handoff scope)

Cora `§1a` gate. No tripwire. Expect clean.

### Step 2 — Confirm branch + commit 27-0

Branch already on `dev/epic-27-texas-intake`. The 27-0 work is uncommitted. Single-commit option:

```bash
git status --short   # verify 39 session-owned files (15 modified + 24 untracked)
git add -A           # session commit is the canonical pattern; operator may prefer file-by-file staging
git commit -m "$(cat <<'EOF'
feat(27-0): Shape 3-Disciplined retrieval foundation + Provider Directory (operator amendment)

Retrieval package at skills/bmad-agent-texas/scripts/retrieval/:
  contracts, base (ABC + auto-registry), dispatcher (single + cross-val merger),
  mcp_client (Option Y JSON-RPC), fake_provider, normalize, refinement_registry,
  provider_directory (AC-B.8/B.9 operator amendment).

Schema v1.1 additive bump (SCHEMA_CHANGELOG.md gate + extraction-report-schema.md).
Audience-segmented retrieval-contract.md. --list-providers CLI. scite+Consensus
MCP URL entries. CLAUDE.md + Marcus external-specialist-registry breadcrumb.

Tests +70 collecting (target +34). Full suite 1106/2/0. Ruff clean on 27-0 code.
Gates: party-mode 3 GREEN + 1 YELLOW→GREEN; bmad-code-review layered
5 MUST-FIX + 9 SHOULD-FIX applied, 4 DISMISSED with rationale (AC-B.7 literal
dispatcher wiring cascade-deferred to 27-2 per anti-pattern #3).

Unblocks 27-2 scite adapter + 27-2.5 Consensus adapter.
EOF
)"
git push origin dev/epic-27-texas-intake
git log --oneline -6
```

### Step 3 — Execute `bmad-create-story 27-2-scite-ai-provider`

Authoring reference: 27-0 spec at [_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md](_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md) is the contract source of truth. 27-2 implements the first real `RetrievalAdapter` subclass against that contract. Expand the existing stub at [_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md](_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md) (pre-reshape 382-line content preserved behind supersession banner for reference, but new story body writes against 27-0 ABC).

**Scope for 27-2 (per bmm-workflow-status.yaml)**:
- Core: implement `formulate_query` / `execute` / `apply_mechanical` / `apply_provider_scored` / `normalize` / `refine` / `identity_key` / `declare_honored_criteria` for scite.ai via the hand-rolled MCP client.
- **Deferred-from-27-0 cascade** absorbed into 27-2 scope:
  - **AC-B.7 degenerate-case dispatcher wiring** — route legacy operator-locator directives through the new dispatcher via the transform per spec. Preserves anti-pattern #3 (no locator-shape provider refactor) by delegating to existing `_fetch_source` under the hood.
  - **`docs/dev-guide.md` "how to add a provider" section** — Paige + Amelia co-authored.
  - **AC-T.7 log-stream structural parity + malformed-DOCX exception-class parity regression tests** (Winston MUST-FIX #4 from 27-0 green-light).
  - **Dual-emit writer** — `run_wrangler.py` emits `schema_version: "1.1"` when dispatcher path invoked; `"1.0"` when legacy-path only.
  - **Parametrized `test_extraction_report_schema_compliance`** over `["1.0", "1.1"]`.

**Pre-dev checks** (to resolve at create-story time):
- Scite.ai MCP endpoint availability and auth-shape confirmation (handoff assumed HTTP Basic; verify against live once credentials are loaded).
- Refinement strategies needed beyond `drop_filters_in_order` — authority-tier relaxation, date-range broadening, supporting-citation floor drop.
- FakeProvider integration test pattern for cross-verifying before live scite fixtures available.

**Target suite delta for 27-2**: TBD at green-light; rough estimate +15-20 collecting tests (ABC-inheritance parametrization + scite-specific formulate/refine + dispatcher-wiring regression + parametrized schema compliance + dual-emit test).

### Step 4 — After 27-2 closes (gate sequence)

- `bmad-party-mode` implementation review.
- `bmad-code-review` layered (Blind Hunter + Edge Case Hunter + Acceptance Auditor).
- Flip 27-2 to done in sprint-status + bmm-workflow-status + epic-27 roster.

### Step 5 — Unblock 27-2.5

Once 27-2 closes, open Story 27-2.5 (Consensus adapter) via `bmad-create-story` — second retrieval-shape adapter + first real `cross_validate: true` exercise (scite + Consensus fan-out → `convergence_signal` annotation).

## Branch Metadata

- **Repository baseline branch after closeout:** `dev/epic-27-texas-intake` (pending commit; no master merge planned until Epic 27 hits a natural close-point, e.g., after 27-2.5 or when operator calls it).
- **Next working branch:** `dev/epic-27-texas-intake` (continue on same branch for 27-2 dev-story).
- **Pushed-to-origin:** **No** — 27-0 closure commit is uncommitted at wrapup per operator preference. Next session first action is to commit + push.
- **Merge strategy:** `--no-ff` per Epic 27/28 pattern, applied at epic-close (not per-story).

## Startup Commands

```bash
# 1. Verify branch
git branch --show-current   # expect: dev/epic-27-texas-intake
git status --short           # expect: 39 files session-owned from 27-0 closure

# 2. Run Session START protocol (Cora §1a gate — no tripwire expected)

# 3. Commit 27-0 closure work (see Step 2 above for full commit template)

# 4. Begin bmad-create-story 27-2-scite-ai-provider
#    Spec ref: _bmad-output/implementation-artifacts/27-0-retrieval-foundation.md
#    Existing stub (pre-reshape, behind supersession banner):
#      _bmad-output/implementation-artifacts/27-2-scite-ai-provider.md

# 5. Run HUD sanity check (optional)
.venv\Scripts\python -m scripts.utilities.run_hud --open

# 6. Inspect Texas capability surface
.venv\Scripts\python skills/bmad-agent-texas/scripts/run_wrangler.py --list-providers
```

## Hot-Start Files

- [SESSION-HANDOFF.md](SESSION-HANDOFF.md) — backward-looking record of the 2026-04-18 session (27-0 close + directory operator amendment + forward-design memory).
- [_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md](_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md) — **reference for 27-2 author** (Status: done; full Review Record + Dev Agent Record populated).
- [skills/bmad-agent-texas/references/retrieval-contract.md](skills/bmad-agent-texas/references/retrieval-contract.md) — audience-segmented contract doc; "For dev-agents" section has the subclass template for 27-2.
- [_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md](_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md) — v1.1 bump rationale; 27-2 dual-emit writer lands against this.
- [_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md](_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md) — ratified-stub spec awaiting re-expansion via `bmad-create-story`.
- [_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md](_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md) — Epic 27 roster post-27-0 closure; 27-2 row absorbs deferred cascade.
- [_bmad-output/maps/deferred-work.md](_bmad-output/maps/deferred-work.md) — ~22 code-review NITs batched for future cleanup.
- [reports/dev-coherence/2026-04-18-0059/harmonization-summary.md](reports/dev-coherence/2026-04-18-0059/harmonization-summary.md) — this session's wrapup L1 sweep audit trail.

## Key Risks / Unresolved Issues

1. **AC-B.7 deferred to 27-2 scope** — when 27-2 party-mode green-lights, re-verify the deferral rationale holds. If the first real retrieval-shape integration reveals the "degenerate-case transform" can't cleanly route legacy operator-locator directives through the new dispatcher without violating anti-pattern #3, the sub-items may need promotion to a dedicated 27-0.1 hotfix. Current bet: delegation pattern (dispatcher handles retrieval-shape; delegates to existing `_fetch_source` for locator-shape via the degenerate transform) works without locator-shape refactor. Documented in [reports/dev-coherence/2026-04-18-0059/harmonization-summary.md](reports/dev-coherence/2026-04-18-0059/harmonization-summary.md) and [_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md](_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md)§Review Record.

2. **Nothing committed to git yet from 27-0 session.** 39 files (15 modified + 24 untracked) sit in the working tree. Next session's FIRST action must be stage + commit + push before opening 27-2 work. If another agent/browser context touched the tree between sessions, reconcile per Session START §2b dirty-worktree scope fence.

3. **Scite.ai MCP endpoint live-verification** — 27-2 pre-dev checks should confirm scite's actual auth flow (we assumed HTTP Basic per scite's standard API pattern, but the MCP-wrapped endpoint may use OAuth / token-exchange). If the auth-shape differs materially, `mcp_client.py` scope grows and 27-2 estimate re-evaluates. Library-agnostic public surface (AC-C.9) mitigates mid-dev surprise.

4. **Repo-wide ruff debt: 1565 findings** (up from prior handoff's 377). All pre-existing warehouse clutter outside 27-0 scope; 27-0 code itself is clean. Clear incrementally as stories touch affected files (per 27-1 cleanup pattern). Not a blocker for 27-2.

5. **~22 NIT-class code-review findings from 27-0** logged to [_bmad-output/maps/deferred-work.md](_bmad-output/maps/deferred-work.md) (polymorphic dispatch return-type, MCPFetchError/MCPConfigError taxonomy, HTTP redirect default `allow_redirects=False`, identity_key mid-merge exception handling, etc.). 27-2 may choose to batch-absorb a subset as it touches related code (e.g., MCPConfigError taxonomy when wiring scite auth).

6. **Pre-commit 3x flake-detection gate** (Murat green-light ask from 27-0) — still not wired at CI level. 27-0 deterministic-sequence-fixture discipline means 60 new tests showed zero flake across 10+ runs, but formal CI guardrail remains future work. Not blocking for 27-2 but should land before Epic 27 closes.

7. **Three missing operator parameter knobs** (enrichment / gap-filling / evidence-bolster) — captured in user memory as forward-design discipline. Not blocking 27-2, but when Epic 27 closes and Tracy / Irene integration opens, this memory surfaces.

## Key Gotchas Discovered This Session

- **Operator amendment post-green-light is OK when strictly additive.** The Provider Directory fold (AC-B.8 / B.9 / T.9-11) added a runtime enumeration surface WITHOUT changing the existing contract. Pattern verified: check architectural coherence (read-surface only, never feeds dispatch), then fold; no need to re-run full green-light.

- **`.env.example` is blocked by two pre-existing repo-policy tests.** Attempted to add one per spec; tests `test_local_env_template_is_not_committed` and `test_no_env_example_in_repo` flagged it. Removed and relocated env-var documentation to `retrieval-contract.md` + `provider_directory.py` `auth_env_vars` field. Pattern for future providers: document env vars in the directory entry; `--list-providers` surfaces them.

- **Deferral-with-rationale is legitimate for DISMISSED code-review findings.** AC-B.7 literal dispatcher wiring was the Acceptance Auditor's most material finding. Classification as DISMISSED (not MUST-FIX) required explicit rationale: anti-pattern #3 prohibits locator-shape refactor; full wiring lands naturally with 27-2; documented in sprint-status AND bmm-workflow-status AND spec Review Record so the deferral isn't lost. Pattern: when a single finding cascades to multiple related findings, batch-dismiss them under one rationale rather than individually-dismiss each.

- **`while/else` with `budget=1` has a logic gotcha**. Python's `while/else` runs the else-clause when the condition becomes False without a `break`. With `iteration_budget=1` and unmet acceptance, the condition `iterations_used(1) < budget(1)` is False on entry — loop body never executes, else still fires. CR-1 code-review finding. Fix: detect the degenerate case before the loop and emit a distinct log reason.

- **Ruff auto-fix can introduce line-length violations**. `SIM114` "combine if branches" on a long line produces an E501 over the 100-char limit. Pattern: after auto-fix, re-run ruff; if new errors appear, hand-fix to produce a shorter form.

## Run HUD

```bash
.venv\Scripts\python -m scripts.utilities.run_hud --open
```

Three tabs: System Health / Production Run / Dev Cycle. After this session's closeout commit lands, HUD will show Epic 27 with 9 stories (27-0 now done, 27-2 ratified-stub/unblocked, 27-2.5 ratified-stub/unblocked). Epic 27 completion: 2/9 stories done (27-1 + 27-0), ~7 pts landed; 24 pts remaining across 7 unblocked stories.

## Ambient Worktree State at Handoff

**39 files uncommitted** — all session-owned from 27-0 closure work:

- **15 modified**: `.cursor/mcp.json`, `.mcp.json`, `CLAUDE.md`, 4 planning/sprint artifacts, `pyproject.toml`, `requirements.txt`, Marcus registry, schema doc, `retrieval/__init__.py`, `run_wrangler.py`, `tests/conftest.py`, `tests/contracts/test_transform_registry_lockstep.py`.
- **24 untracked**: `SCHEMA_CHANGELOG.md`, `retrieval-contract.md`, 8 new retrieval modules, `tests/_helpers/`, `tests/contracts/fixtures/`, 7 new tests under `tests/contracts/`, `tests/fixtures/retrieval/`, 3 new tests under `tests/`, `reports/dev-coherence/2026-04-18-0059/`, this file + `SESSION-HANDOFF.md`.

No pre-existing unrelated changes detected. No collaborative in-scope changes from other agents.

## Protocol Status

Follows the canonical BMAD session protocol pair ([bmad-session-protocol-session-START.md](bmad-session-protocol-session-START.md) / [bmad-session-protocol-session-WRAPUP.md](bmad-session-protocol-session-WRAPUP.md)). Charter §5 discipline honored: session closed at operator-requested stop-point after 5-step BMAD closure completed (party-mode + code-review + sprint-status flip + bmm-workflow + roster update), not at impasse.

Per-operator directive from session: nothing touches git; operator owns the commit decision in the next session's Step 2.
