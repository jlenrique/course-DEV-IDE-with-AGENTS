# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> **Current objective:** Execute `bmad-dev-story 27-0-retrieval-foundation` — implement the Shape 3-Disciplined retrieval foundation package (contracts, ABC, dispatcher, hand-rolled MCP client, FakeProvider, 30 tests, schema v1.1). 27-0 is the dependency-gate for 27-2 (scite), 27-2.5 (Consensus), 27-3 (image), 27-4 (YouTube), and 28-1 (Tracy pilot).

## Immediate Next Action (pick-up point)

**Run BMAD Session Protocol Session START**, then pivot directly into `bmad-dev-story 27-0-retrieval-foundation`.

Session START expectations:
- Cora `§1a` gate: **tripwire NOT fired** (last session's Step 0a ran clean; report at `reports/dev-coherence/2026-04-17-2318/`). Default scope `since-handoff` for any opening `/harmonize`.
- Story 27-0 is **ready-for-dev** in sprint-status (not in-progress — the one line of placeholder `retrieval/__init__.py` stub does not count as dev-started). Expect a clean foundation-story dev-story from an empty slate.

## Hot-Start Summary

Prior session (2026-04-17 evening) landed three major things:
1. **Story 27-1 DOCX provider wiring closed BMAD-clean** — python-docx 1.2.0 wired; Tejal cross-validation 100% key-term coverage / 69 of 69 sections; full suite 1036/2/0; gates party green-light + implementation review (3 SHOULD-FIX patches) + bmad-code-review layered (0 MUST-FIX, 8 patches, 4 deferred, 6 dismissed). Unblocks halted APC C1-M1 Tejal trial.
2. **Three-round partitioning debate** converged on **Shape 3-Disciplined** retrieval architecture (Dr. Quinn knowledge-locality partitioning). Tracy authors intent+AC+provider_hints (editorial); Texas owns query formulation + fetch + iteration + normalization (mechanical). Cross-validation is v1 first-class (scite + Consensus convergence signal).
3. **27-0 Retrieval Foundation opened + green-lit** — full BMAD spec with 7 AC-B + 8 AC-T + 11 AC-C. **Option Y (hand-rolled JSON-RPC-over-HTTP) unanimously chosen** over `mcp` PyPI pre-1.0.

## Sequenced Implementation Plan for This Session

### Step 1 — Harmonization check (default since-handoff scope)

Cora `§1a` gate. No tripwire. Expect clean.

### Step 2 — Confirm branch + pull

```bash
git checkout dev/epic-27-texas-intake
git pull origin dev/epic-27-texas-intake
git log --oneline -6
```

Branch already cut + committed to origin at last session's close.

### Step 3 — Execute `bmad-dev-story 27-0-retrieval-foundation`

Spec: [_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md](_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md) — ~400 lines of ratified contract + green-light patches applied.

**Pre-dev checks** (Amelia's R1-R3 from green-light; resolve these before writing production code):
- **R1 scite MCP auth**: assume HTTP Basic (username/password → base64 `Authorization` header). Library-agnostic MCP client public surface (`call_tool`, `list_tools`) protects against auth-shape surprise at 27-2. If auth differs materially, re-estimate.
- **R2 refinement registry shape**: start flat registry with `drop_filters_in_order` as the default strategy. 27-2's scite adapter can extend with provider-specific strategies if needed; do NOT over-engineer for hypothetical 27-3/4 needs.
- **R3 FakeProvider fixtures**: enumerate `tests/fixtures/retrieval/fake-responses/*.json` during T4. Minimum 2 canned responses (happy-path + empty-result).

**Task order** (follows spec's §Tasks / Subtasks):
1. T2 `contracts.py` — Pydantic `RetrievalIntent`, `AcceptanceCriteria`, `TexasRow`, enums.
2. T3 `base.py` — `RetrievalAdapter` ABC (8 methods: formulate_query / execute / apply_mechanical / apply_provider_scored / normalize / refine / quality_delta / declare_honored_criteria).
3. T4 `fake_provider.py` — reference adapter for contract tests.
4. T5+T6 `dispatcher.py` — single-provider path (Model A iteration, budget-bounded, abort-on-non-improvement) + multi-provider cross-validation fan-out path (identity-keyed merge + `convergence_signal` annotation). **Anti-pattern guard**: keep single-provider + multi-provider as distinct code paths per Winston's green-light note (N=1 is not folded into the merger — Murat + Winston agreed). Cross-val is **structural only**, not semantic.
5. T7 `mcp_client.py` — hand-rolled JSON-RPC-over-HTTP using existing `requests`. Library-agnostic public surface: `call_tool(server, tool, args) -> dict`, `list_tools(server) -> list`. No `requests.Response` leaking to callers. ~80-120 lines.
6. T8 `normalize.py` + `refinement_registry.py` — canonical TexasRow helpers + deterministic refine strategies.
7. T9 Schema v1.1 additive bump in `extraction-report-schema.md` + `SCHEMA_CHANGELOG.md` gate artifact + "Why minor bump" paragraph (Paige mandate).
8. T10 `run_wrangler.py` dispatcher integration + legacy-directive auto-transform per AC-B.7 (operator-direct = degenerate case of Shape 3 call).
9. T11 Repo-level `.cursor/mcp.json` + `.mcp.json` scite + Consensus URL entries + `run_mcp_from_env.cjs` URL-based server support.
10. T12 Schema-pin contract test (Murat Option A: snapshot + allowlist + CHANGELOG gate).
11. T13 ABC inheritance contract tests (parametrized over FakeProvider; named `test_retrieval_adapter_base.py` as explicit inheritance target for 27-2 / 27-2.5 per Murat green-light).
12. T14 Dispatcher iteration tests (deterministic sequence fixtures — NO stateful mocks; 5 iteration tests + budget-boundary + FakeProvider determinism self-test).
13. T15 Cross-validation merger tests (6 tests after AC-T.4 split into both-agree / disagreement / single-source + identity-key + single-source-only + non-DOI identity extractor).
14. T16 Fungibility parametrized contract test (against canonical fixture; canonical-shape self-test).
15. T17 MCP client tests (`tests/_helpers/mcp_fixtures.py` JSON-RPC helper + 6 error-mapping tests via `responses`).
16. T18 Legacy 27-1 DOCX byte-identical regression (AC-T.7): output byte-parity + log-line parity + error-path fixture parity. DOCX only; PDF deferred to 27-3+ per Murat scope call.
17. T19 Schema version field presence contract + parametrize `test_extraction_report_schema_compliance` for v1.0/v1.1.
18. T20 Lockstep test extension: `RETRIEVAL_SHAPE_PROVIDERS` + `LOCATOR_SHAPE_PROVIDERS` classification dicts + meta-principle docstring ("The distinction lives in the input-origin axis, not the extractor axis").
19. T21 `retrieval-contract.md` — audience-segmented (For Tracy / For operators / For dev-agents / Appendix) unified doc. **Paige drives structure, Amelia countersigns technical accuracy.**
20. T22 CLAUDE.md pointer + `.env.example` (SCITE_USER_NAME / SCITE_PASSWORD + Consensus equivalents) + `test_retrieval_contract_doc_exists.py`.
21. T23 Regression + 3x flake-detection CI gate + ruff + pre-commit.
22. T24 Flip 27-0 to review; hand off to party-mode implementation review.

**Target suite delta: +30 collecting tests** (1036 → 1066). No xfail, no skip, no new live_api, no new trial_critical.

**Anti-pattern guardrails** (from green-light; each is a dev-agent mistake trap):
- No LLM-in-loop for query formulation / refinement (v1 deterministic Python only).
- No stateful mocks for iteration tests (deterministic sequence fixtures only).
- No refactoring 27-1 DOCX or any locator-shape provider — legacy directive shape preserved via AC-B.7 degenerate-case transform.
- No real providers in 27-0 (FakeProvider only; scite is 27-2, Consensus is 27-2.5).
- `provider_hints` REQUIRED v1 — no provider discovery.
- No semantic-criteria evaluation in Texas — Tracy owns `semantic_deferred` post-fetch pass.
- Log unknown AC keys (not silent-drop).
- Cross-validation is a DISTINCT code path from single-provider (not N=1 degenerate of multi).
- MCP library = Option Y locked; dispatcher non-retrying + non-fallback in v1 (Marcus owns cross-provider re-dispatch).
- `identity_key(row) -> str` required from each adapter; cross-val with an adapter that can't identify rows → clear error at dispatch.

### Step 4 — After 27-0 closes (gate sequence)

- `bmad-party-mode` implementation review (Winston + Amelia + Murat — Paige joins if doc scope non-trivial).
- `bmad-code-review` layered (Blind Hunter + Edge Case Hunter + Acceptance Auditor).
- Flip 27-0 to done in sprint-status + bmm-workflow-status + epic-27 roster.

### Step 5 — Unblock downstream

Once 27-0 closes, these stories unblock:
- **27-2 scite.ai adapter** (blocked): re-expand via `bmad-create-story` post-27-0 — reshape from direct scite provider to scite ADAPTER against 27-0's `RetrievalAdapter` ABC.
- **27-2.5 Consensus adapter** (ratified-stub): expand via `bmad-create-story` — second retrieval-shape adapter; first real `cross_validate: true` exercise.
- **28-1 Tracy pilot** (blocked): re-expand via `bmad-create-story` post-27-2 — reshape Tracy's output from scite-specific queries to provider-agnostic intent+AC+provider_hints per 27-0 contract. Scope drops 9 → ~7 pts.

## Branch Metadata

- **Repository baseline branch after closeout:** `dev/epic-27-texas-intake` (post-session-commit; this session chose NOT to merge-to-master because 27-0 foundation is in-progress — merge-to-master happens after 27-0 closes).
- **Next working branch:** `dev/epic-27-texas-intake` (continue on same branch for 27-0 foundation dev-story).
- **Pushed-to-origin:** Yes (session commit pushed to `origin/dev/epic-27-texas-intake`).
- **Merge strategy:** `--no-ff` per Epic 27/28 pattern (applies at 27-0 close, not at this session close).

## Startup Commands

```bash
# 1. Verify branch + pull
git checkout dev/epic-27-texas-intake
git pull origin dev/epic-27-texas-intake
git log --oneline -6

# 2. Run Session START protocol (Cora §1a gate — no tripwire expected)

# 3. Begin bmad-dev-story 27-0-retrieval-foundation
# Pre-dev checks R1-R3 resolved inline; proceed with T2 contracts.py as first code artifact.

# 4. Run HUD sanity check (optional)
.venv\Scripts\python -m scripts.utilities.run_hud --open
```

## Hot-Start Files

- [SESSION-HANDOFF.md](SESSION-HANDOFF.md) — backward-looking record of the 2026-04-17 evening session (27-1 close + three-round partitioning + 27-0 foundation-story-opened-and-green-lit).
- [_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md](_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md) — 400-line full BMAD spec for the next dev-story.
- [_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md](_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md) — Epic 27 roster post-Round-3 reshape (27-0 inserted, 27-2.5 Consensus added).
- [_bmad-output/maps/deferred-work.md](_bmad-output/maps/deferred-work.md) — includes Notion MCP dual-config research (user hosted vs project stdio) for Story 27-5.
- [reports/dev-coherence/2026-04-17-2318/harmonization-summary.md](reports/dev-coherence/2026-04-17-2318/harmonization-summary.md) — this session's wrapup L1 sweep audit trail.

## Key Risks / Unresolved Issues

1. **27-0 is substantial** (~5 pts, ~2000 lines across 20+ files, 30 tests). This will be a full focused session. Don't try to bundle any other story work in parallel.

2. **MCP client auth shape** — R1 above. Assumed HTTP Basic with username/password from `.env`. If scite MCP actually uses a different auth flow (OAuth token exchange, etc.), `mcp_client.py` scope grows; re-estimate at green-light. Library-agnostic public surface mitigates mid-dev surprise.

3. **Scite.ai MCP endpoint availability** — operator confirmed scite + Consensus both already authenticated in Cursor user-scope `mcp.json`. For Texas headless access, Story 27-0 T11 adds repo-level entries. If scite MCP endpoint is rate-limited at connection-level, T17 MCP client tests may need careful fixture design to avoid accidentally hitting live API.

4. **Repo-wide ruff debt (377 errors, 77 auto-fixable)** — pre-existing warehouse clutter; not a blocker. Strategy: clear incrementally as stories touch affected files (per 27-1 cleanup pattern).

5. **Deferred from 27-1 code review** (non-blocking follow-ups; documented in deferred-work.md):
   - Sibling Office-ZIP suffixes (.docm, .dotx, .dotm) fall-through class → future "Texas intake robustness" story.
   - DOCX body-order silently drops `<w:sdt>` / `<w:altChunk>` content → same follow-on.
   - `extract_docx_text` docstring exception completeness.
   - Windows short-path integration-test flakiness theoretical.
   - Negative-control fixture for Tejal cross-validator — Murat follow-on.
   - `_EXTRACTOR_LABELS` dual-lookup collapse — Winston polish.

6. **28-1 Tracy pilot needs re-expansion** via `bmad-create-story` after 27-2 closes. Current spec has reshape banner at top; full body is pre-reshape. Don't start Tracy dev-story until re-expanded.

7. **Pre-commit 3x flake-detection gate** (Murat green-light ask) — needs CI config update when Tracy-era stories land. Not blocking for 27-0 but should be considered for CI hygiene.

## Key Gotchas Discovered This Session

- **Knowledge-locality > role-tradition partitioning** (Dr. Quinn). Query formulation is mechanical (Texas's lane); editorial judgment is intent + acceptance criteria (Tracy's lane). This unlocked Shape 3-Disciplined.
- **Cross-validation is a mechanical algorithm, not editorial** — Texas owns fan-out + dedup + convergence_signal annotation. Tracy interprets the signals editorially.
- **Cursor user-scope + project-scope MCP configs merge** — case-sensitive key difference means "Notion" (user) and "notion" (project) load as two separate Notion MCPs. Intentional; serves different consumers (IDE vs headless).
- **Iteration Model A vs B is test-architecture tradeoff** — 4-1 party for Model A (Texas-internal adapter loop), resolved Murat's dissent with **deterministic sequence fixtures** (NOT stateful mocks).
- **Library-agnostic public surface** is the escape hatch for pre-1.0 dependency decisions — Option X (`mcp` PyPI) migration later becomes a single-file swap.
- **Operator-direct = degenerate case of Shape 3 contract** (Dr. Quinn) — one contract, two UX surfaces. Locator-shape providers (27-1 DOCX, 27-5 Notion, 27-6 Box, 27-7 Playwright) keep existing directive shape at CLI; internally route through new dispatcher. No retrofit.

## Run HUD

```bash
.venv\Scripts\python -m scripts.utilities.run_hud --open
```

Three tabs: System Health / Production Run / Dev Cycle. After this session's closeout commit, HUD will show Epic 27 with 9 stories (27-0 added, 27-2.5 added, 27-2 blocked), and 28-1 Tracy with reshape banner flag.

## Ambient Worktree State at Handoff

**Clean after commit.** Session commit captures all 14 modified + 3 untracked files. No ambient changes left behind. No uncommitted work.

## Protocol Status

Follows the canonical BMAD session protocol pair ([bmad-session-protocol-session-START.md](bmad-session-protocol-session-START.md) / [bmad-session-protocol-session-WRAPUP.md](bmad-session-protocol-session-WRAPUP.md)). Charter §5 discipline honored: autonomous run paused at operator-directed stop-point (option a from three-way choice) rather than impasse or completion.
