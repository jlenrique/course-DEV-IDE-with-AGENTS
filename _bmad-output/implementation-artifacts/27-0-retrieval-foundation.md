# Story 27-0: Retrieval Foundation — Shape 3-Disciplined Contract + Multi-Provider Dispatch

**Status:** in-progress
**Created:** 2026-04-17 (ratified-stub post-Round-3 party consensus); expanded to full BMAD story 2026-04-17 via `bmad-create-story`; green-light UNANIMOUS Option Y + consensus patches applied 2026-04-17; `bmad-dev-story` started 2026-04-17
**Epic:** 27 — Texas Intake Surface Expansion
**Sprint key:** `27-0-retrieval-foundation`
**Branch:** `dev/epic-27-texas-intake`
**Points:** 5 (Amelia estimate, John-compatible at 3 narrow scope; Winston implicit at 8 scite-inclusive — **5 pts scoped as foundation + FakeProvider reference only; scite adapter is 27-2, not bundled**)
**Depends on:** none (foundation — nothing upstream). Closes 27-1 DOCX provider wiring is the spec-pattern reference (locator-shape counterpart).
**Blocks:** **27-2 (scite adapter)**, **27-2.5 (Consensus adapter)**, **27-3 (image sources)**, **27-4 (YouTube)**, **28-1 (Tracy reshape)**.

## TL;DR

- **What:** The `skills/bmad-agent-texas/scripts/retrieval/` foundation package — contracts (`RetrievalIntent` / `AcceptanceCriteria` / `TexasRow`), `RetrievalAdapter` ABC, dispatcher (single-provider + multi-provider cross-validation), hand-rolled Python MCP client utility (**Option Y — JSON-RPC-over-`requests`, no new dependency; library-agnostic surface for future Option-X migration**), canonical normalization, repo-level scite + Consensus MCP registration, schema v1.1 bump. **NO real provider ships in 27-0 — NOT scite, NOT Consensus, NOT YouTube, NOT image sources.** Those land in 27-2, 27-2.5, 27-4, 27-3 respectively. A `FakeProvider` reference adapter proves the contract in this story only.
- **Why:** Three-round party consensus converged on **Shape 3-Disciplined** (Dr. Quinn's knowledge-locality partitioning). Editorial work (intent + acceptance criteria) with Tracy; provider-DSL work with per-provider adapters; dispatch + iteration with thin Texas shell. Foundation authored **before any provider ships** to prevent "first-provider shapes the contract poorly" failure mode (Murat + Amelia mandate).
- **Key decisions ratified**: Iteration **Model A** (adapter-internal loop with deterministic sequence fixtures, NOT stateful mocks — resolving Murat's test-flakiness concern). Three Dr. Quinn guardrails — `provider_hints` **required** v1 / mechanical-only AC v1 / convergence signal for abort-on-non-improvement. Deterministic Python query formulation only (**no LLM-in-the-loop v1**).
- **Cross-validation is first-class v1** — `cross_validate: true` dispatches every `provider_hints` entry in parallel, merges by identity key (DOI / video-id / canonical-url), annotates rows with `convergence_signal: {providers_agreeing, providers_disagreeing, single_source_only}`. Operator-directed use-case: scite + Consensus convergence for Tracy's research workflow.
- **Operator-locator paths unchanged at CLI** (27-1 DOCX / 27-5 Notion / 27-6 Box / 27-7 Playwright keep existing directive shape); internally route through the new dispatcher as degenerate-case transforms — one contract, two UX surfaces.
- **Done when:** foundation + FakeProvider + schema v1.1 shipped; schema-pin + base-class-contract + fungibility + dispatcher-iteration + cross-validation-merger + MCP-client + legacy-directive-regression tests all green; 27-1 DOCX regression proof byte-identical; `bmad-code-review` clean; 27-2 + 27-2.5 unblocked.

## Story

As the **Texas wrangler architect**,
I want **a retrieval-specialist contract + dispatcher + multi-provider cross-validation merger foundation**,
So that **every future search-shaped provider** (scite, Consensus, YouTube, images) **ships as a clean adapter against a tested contract**, and **Tracy's dispatch interface collapses to intent + acceptance-criteria + provider-hints** — eliminating provider-specific query knowledge from her prompt.

## Background — Why This Story Exists

Across three party-mode rounds (2026-04-17), the team converged on **Shape 3-Disciplined** as the correct partitioning for search-shaped source retrieval. Summary of the consensus:

- **Original Shape 1** (IDE-agent materializes results, Texas consumes YAML) put scite's query DSL in Tracy's prompt. Every new provider would bloat the prompt; every API change would force prompt churn. Wrong locus of change.
- **Original Shape 2** (Python scite client in Texas) kept lane discipline but was scite-specific and didn't generalize.
- **Shape 3-Disciplined** (Dr. Quinn's synthesis): partition by **knowledge-locality**, not role-tradition. Editorial knowledge (intent + acceptance criteria) with Tracy. Provider-DSL knowledge with per-provider adapters. Dispatch + iteration orchestration with thin Texas shell.

**The operator's decisive input** closed the debate: "Source material is the heart of any academic course content development. Worth getting this right (or at least robust) now." **And**: "Scite is ALREADY available and authenticated as an MCP in Cursor. Consensus (another research tool) is already available and authorized. Once we get scite.ai working, we'll duplicate that with Consensus so we can extend Texas's toolset and use one service's findings to confirm or supplement another's."

Cross-validation (one provider confirms/supplements another) is a v1 requirement — exactly the class of mechanical retrieval operation that belongs in Texas's lane per knowledge-locality analysis.

## Acceptance Criteria (post-Round-1 green-light patches)

### Behavioral (AC-B.*)

1. **AC-B.1 — `RetrievalIntent` contract.** Pydantic model living at `skills/bmad-agent-texas/scripts/retrieval/contracts.py`:
   ```yaml
   intent: str                              # natural-language description
   provider_hints: list[str]                # REQUIRED v1 — no discovery
   kind: "query" | "direct_ref" | "render"  # polymorphic discriminator
   acceptance_criteria: AcceptanceCriteria
   iteration_budget: int = 3
   convergence_required: bool = true
   cross_validate: bool = false             # when true: fan-out + merge
   ```

2. **AC-B.2 — `AcceptanceCriteria` contract (three-tier schema).**
   ```yaml
   mechanical: dict   # Texas evaluates deterministically (date_range, min_results, duration_cap, license_allow, etc.)
   provider_scored: dict   # Texas evaluates via provider-native signals (authority_tier_min, supporting_citations_min, etc.)
   semantic_deferred: str | None   # Texas does NOT evaluate — Tracy post-fetch pass
   ```
   Unknown keys MUST NOT be silently dropped — logged in `refinement_log` as "not evaluable by this provider."

3. **AC-B.3 — `RetrievalAdapter` ABC.** Abstract base at `retrieval/base.py` with required methods:
   - `formulate_query(intent: RetrievalIntent) -> ProviderQuery` (deterministic Python only — no LLM)
   - `execute(query: ProviderQuery) -> RawProviderResult` (handles auth, pagination, rate-limiting)
   - `apply_mechanical(results, criteria.mechanical) -> filtered` (deterministic predicates)
   - `apply_provider_scored(results, criteria.provider_scored) -> filtered` (provider-native signals)
   - `normalize(result) -> TexasRow` (common output shape)
   - `refine(previous_query, previous_results, criteria) -> new_query | None` (returns None when refinement can't help)
   - `quality_delta(prev_results, curr_results) -> float` (for convergence-required abort-on-non-improvement)
   - `declare_honored_criteria() -> set[str]` (introspection — which criteria keys this adapter can evaluate)

4. **AC-B.4 — Dispatcher owns the iteration loop (Model A resolution).** `retrieval/dispatcher.py` implements:
   - Single-provider path: formulate → execute → apply mechanical + provider-scored → if `acceptance_met`: return; else if budget-remaining AND `quality_delta > 0`: refine → loop; else: return with `acceptance_met: false` + `refinement_log`.
   - Multi-provider path (`cross_validate: true`): fan out to every `provider_hints` entry, run each adapter independently up to `iteration_budget`, merge by identity key (DOI / video-id / canonical-url), annotate each merged row with `convergence_signal: {providers_agreeing: [...], providers_disagreeing: [...], single_source_only: [...]}`.
   - Abort-on-non-improvement: if `quality_delta <= 0` on any iteration, exit with current results + log entry.

5. **AC-B.5 — Python MCP client utility.** `retrieval/mcp_client.py` provides remote-HTTP-MCP access (for scite + Consensus + any future HTTP-MCP provider). Uses stable Python MCP library OR hand-rolled JSON-RPC-over-HTTP if library maturity blocks (TBD at green-light). Auth via env vars; credentials resolved lazily at first call. This utility is what future adapters import — foundation provides the infra, per-provider adapter picks the endpoint + auth model.

6. **AC-B.6 — Repo-level MCP registration.** `.cursor/mcp.json` and `.mcp.json` gain scite + Consensus entries (the user has them configured in Cursor-global; adding repo-local makes Claude Code + CI flows symmetric). Entries use URL-based remote-HTTP pattern (not stdio-subprocess pattern). `run_mcp_from_env.cjs` extended to handle URL-based servers if required.

7. **AC-B.7 — Operator-direct path becomes degenerate case.** Existing directive shape (provider + locator) is internally transformed into a Shape 3 call: `intent="fetch exact locator"`, `provider_hints=[<provider>]`, `kind="direct_ref"`, `acceptance_criteria={mechanical: [exists]}`, `iteration_budget=1`. One contract, two UX surfaces. Operator-locator paths (Notion/Box/Playwright) keep their current directive shape at the CLI level but route through the same dispatcher internally. **No retrofit of existing 27-1 DOCX or locator-shape providers required.**

### Test (AC-T.*)

1. **AC-T.1 — Schema-pin contract test.** `tests/contracts/test_acceptance_criteria_schema_stable.py` pins `RetrievalIntent` + `AcceptanceCriteria` + `TexasRow` from day one. Any change to these shapes without explicit migration → test fails. **Single most important test in the stack (Murat).**

2. **AC-T.2 — Base-class contract test module.** `tests/contracts/test_retrieval_adapter_base.py` parametrized over a `FakeProvider` reference adapter. Asserts the ABC contract: every subclass must honor `formulate_query` determinism, `apply_mechanical` deterministic predicate semantics, `refine` monotonic looseness, `quality_delta` monotonicity, `declare_honored_criteria` introspection correctness. Every future real adapter inherits these tests via parametrization.

3. **AC-T.3 — Dispatcher iteration-loop tests.** Murat's test-flakiness concern resolved via **deterministic sequence fixtures, not stateful mocks**. Each test case pre-scripts the sequence of query-result pairs the FakeProvider returns; the dispatcher's loop is tested as a pure function over the pre-scripted sequence. Covers: single-shot-meets-criteria; multi-iter-meets-criteria; budget-exhausted; non-improvement-abort; `refine` returning None → exit early.

4. **AC-T.4 — Cross-validation merger tests.** `tests/test_retrieval_cross_validation.py`: three-provider fan-out returning overlapping + non-overlapping DOIs. Asserts merged output has correct `convergence_signal` annotations per row; dedup-by-identity-key works; single-source-only flags set correctly; non-DOI identity keys (video-id, canonical-url) handled via adapter-declared identity-extractor.

5. **AC-T.5 — Fungibility contract test (against-canonical, not pairwise).** `tests/contracts/test_texas_row_fungibility.py` parametrized over `(provider_fixture, canonical_intent)` pairs. Asserts every provider's normalized `TexasRow` shape round-trips through Vera / Quinn-R / Irene consumption equivalently. Linear in provider count, not combinatorial (Murat).

6. **AC-T.6 — Python MCP client smoke tests.** Mocked-HTTP tests for `mcp_client.py` — auth header construction, JSON-RPC envelope parsing, error-class mapping (401 → `MCPAuthError`, 429 → `MCPRateLimitError`, 5xx → `MCPFetchError`). No live network.

7. **AC-T.7 — Operator-direct-path regression.** Existing 27-1 DOCX invocation path remains byte-identical in output (extraction-report.yaml + all 6 artifacts). Proof that Shape 3 refactor doesn't regress the legacy locator-shape flows.

8. **AC-T.8 — Regression suite-level gate (non-collecting AC).** Baseline from 27-1 closeout: 1036 passed / 2 skipped / 2 xfailed. Expected after 27-0: **+N collecting tests** (TBD at green-light; rough estimate +20-25). No xfail, no new skips, no new live_api, no new trial_critical.

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Foundation lives in `skills/bmad-agent-texas/scripts/retrieval/`.** New directory. Files: `__init__.py`, `contracts.py`, `base.py`, `dispatcher.py`, `mcp_client.py`, `normalize.py`, `refinement_registry.py`.

2. **AC-C.2 — Canonical `TexasRow` normalized shape.** Single common row format all adapters emit. Fields: `source_id` (provider-independent identity), `title`, `body`, `authors`, `date`, `provider`, `provider_metadata` (per-provider sub-object), `source_origin` (`operator-named` | `tracy-suggested`), `tracy_row_ref` (when applicable), `convergence_signal` (when cross-validated), `authority_tier` (when provider-scored), standard Texas quality fields (`completeness_ratio`, `structural_fidelity`, etc.).

3. **AC-C.3 — Extraction-report-schema bump to v1.1.** Additive fields: `retrieval_intent` (the originating intent), `provider_hints`, `cross_validate`, `convergence_signal` per source. Backwards-compatible (all new fields optional with v1.0 defaults). Schema changelog documents minor-bump rationale.

4. **AC-C.4 — Legacy directive shape coexists.** 27-1 DOCX directive format unchanged. `run_wrangler.py` accepts both old and new directive shapes; old shape is internally transformed to Shape 3 call as described in AC-B.7.

5. **AC-C.5 — Lockstep contract test extended.** `tests/contracts/test_transform_registry_lockstep.py` gains a `RETRIEVAL_SHAPE_PROVIDERS` dict enumerating providers that use Shape 3 (intent+AC) vs. `LOCATOR_SHAPE_PROVIDERS` dict for operator-locator providers. Current classification: scite/Consensus/YouTube/image = Shape 3; Notion/Box/Playwright/local_file/pdf/docx = locator-shape.

6. **AC-C.6 — No LLM-in-the-loop for query formulation or refinement** (v1 hard constraint). Deterministic Python only. Per-provider tier-classification lookup tables are **data**, not inference. LLM-driven query expansion deferred to a future story with its own eval-framework authorship.

7. **AC-C.7 — `provider_hints` is REQUIRED in v1** (Dr. Quinn guardrail). No provider-discovery / auto-selection. If Tracy needs multi-provider work, she specifies multiple hints.

8. **AC-C.8 — Semantic acceptance criteria are Tracy's post-fetch concern** (Dr. Quinn guardrail). Texas emits `semantic_deferred` field in results unchanged from Tracy's input — does not evaluate. Tracy runs her own post-fetch semantic pass on the normalized rows.

## File Impact (preliminary — refined at `bmad-create-story`)

| File | Change | Lines (est.) |
|------|--------|-------|
| `skills/bmad-agent-texas/scripts/retrieval/__init__.py` | **New** package marker | +1 |
| `skills/bmad-agent-texas/scripts/retrieval/contracts.py` | **New** — `RetrievalIntent`, `AcceptanceCriteria`, `TexasRow`, sentinel enums | +150 |
| `skills/bmad-agent-texas/scripts/retrieval/base.py` | **New** — `RetrievalAdapter` ABC + default implementations | +180 |
| `skills/bmad-agent-texas/scripts/retrieval/dispatcher.py` | **New** — single-provider + multi-provider dispatch + iteration loop + cross-validation merger | +220 |
| `skills/bmad-agent-texas/scripts/retrieval/mcp_client.py` | **New** — Python MCP client utility (HTTP JSON-RPC) | +120 |
| `skills/bmad-agent-texas/scripts/retrieval/normalize.py` | **New** — canonical `TexasRow` transformation helpers | +80 |
| `skills/bmad-agent-texas/scripts/retrieval/refinement_registry.py` | **New** — deterministic refinement strategies (drop-filters-in-order, broaden-date-range, etc.) | +90 |
| `skills/bmad-agent-texas/scripts/run_wrangler.py` | **Touch** — integrate dispatcher; legacy-directive auto-transform to Shape 3 call; preserve existing locator-shape paths | +60 |
| `skills/bmad-agent-texas/references/extraction-report-schema.md` | **Touch** — schema v1.1 (retrieval_intent, provider_hints, cross_validate, convergence_signal) | +70 |
| `skills/bmad-agent-texas/references/retrieval-contract.md` | **New** — operator-facing + Tracy-facing documentation of the contract | +200 |
| `tests/contracts/test_acceptance_criteria_schema_stable.py` | **New** — schema pin (Murat mandatory) | +80 |
| `tests/contracts/test_retrieval_adapter_base.py` | **New** — ABC contract tests with `FakeProvider` | +200 |
| `tests/contracts/test_texas_row_fungibility.py` | **New** — cross-provider row-shape equivalence | +150 |
| `tests/contracts/test_transform_registry_lockstep.py` | **Touch** — add `RETRIEVAL_SHAPE_PROVIDERS` classification | +15 |
| `tests/test_retrieval_dispatcher.py` | **New** — dispatcher iteration loop + cross-validation | +250 |
| `tests/test_retrieval_mcp_client.py` | **New** — mocked-HTTP MCP client tests | +120 |
| `skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py` | **Touch** — legacy-directive auto-transform test | +30 |
| `.cursor/mcp.json` + `.mcp.json` | **Touch** — scite + Consensus URL entries | +15 |
| `scripts/run_mcp_from_env.cjs` | **Touch** — handle URL-based servers (if needed) | +30 |
| `pyproject.toml` | **Touch** — add Python MCP client dep (TBD at green-light) | +1 |
| `.env.example` | **Touch** — `SCITE_USER_NAME` + `SCITE_PASSWORD` + Consensus equivalents | +5 |

## Tasks / Subtasks (preliminary — refined at `bmad-create-story`)

- [ ] T1 — Resolve `bmad-create-story` green-light on the stub shape (this file).
- [ ] T2 — Author `RetrievalIntent` + `AcceptanceCriteria` + `TexasRow` Pydantic models in `contracts.py`.
- [ ] T3 — Author `RetrievalAdapter` ABC in `base.py` with default implementations where sensible.
- [ ] T4 — Build `FakeProvider` reference adapter for base-class contract tests.
- [ ] T5 — Implement dispatcher single-provider path (formulate → execute → filter → loop).
- [ ] T6 — Implement dispatcher multi-provider path (fan-out + merge + `convergence_signal`).
- [ ] T7 — Implement `mcp_client.py` Python MCP client.
- [ ] T8 — Schema-pin contract test.
- [ ] T9 — ABC-inheritance contract test module.
- [ ] T10 — Dispatcher iteration-loop tests (deterministic sequence fixtures).
- [ ] T11 — Cross-validation merger tests.
- [ ] T12 — Fungibility contract test harness (against-canonical).
- [ ] T13 — Legacy-directive auto-transform + regression proof (27-1 DOCX byte-identical).
- [ ] T14 — Repo-level `.cursor/mcp.json` + `.mcp.json` scite/Consensus entries.
- [ ] T15 — Schema bump + documentation (`retrieval-contract.md`).
- [ ] T16 — Regression suite + pre-commit + lockstep-test extension.
- [ ] T17 — Party-mode implementation review.
- [ ] T18 — `bmad-code-review` layered pass.
- [ ] T19 — Close to done; 27-2 and 27-2.5 unblocked.

## Test Plan

| Test | AC | Level | Mocked? | Blocking at merge? |
|------|----|-------|---------|---------------------|
| `test_acceptance_criteria_schema_stable` | T.1 | Contract | N/A | **Yes — Murat's #1 priority** |
| `test_retrieval_intent_schema_stable` | T.1 | Contract | N/A | Yes |
| `test_texas_row_schema_stable` | T.1 | Contract | N/A | Yes |
| `test_adapter_base_formulate_query_deterministic` (parametrized over `FakeProvider`) | T.2 | Contract | N/A | Yes |
| `test_adapter_base_apply_mechanical_deterministic` | T.2 | Contract | N/A | Yes |
| `test_adapter_base_refine_monotonic_looseness` | T.2 | Contract | N/A | Yes |
| `test_adapter_base_quality_delta_monotonic` | T.2 | Contract | N/A | Yes |
| `test_adapter_base_declare_honored_criteria_introspection` | T.2 | Contract | N/A | Yes |
| `test_dispatcher_single_shot_meets_criteria` | T.3 | Unit | FakeProvider sequence fixture | Yes |
| `test_dispatcher_multi_iter_meets_criteria` | T.3 | Unit | FakeProvider sequence fixture | Yes |
| `test_dispatcher_budget_exhausted_returns_acceptance_false` | T.3 | Unit | FakeProvider sequence fixture | Yes |
| `test_dispatcher_non_improvement_aborts_on_convergence_required` | T.3 | Unit | FakeProvider sequence fixture | Yes |
| `test_dispatcher_refine_returning_none_exits_early` | T.3 | Unit | FakeProvider sequence fixture | Yes |
| `test_cross_validation_merges_by_identity_key` | T.4 | Unit | FakeProvider x2 | Yes |
| `test_cross_validation_annotates_convergence_signal_all_three` | T.4 | Unit | FakeProvider x2 | Yes |
| `test_cross_validation_flags_single_source_only` | T.4 | Unit | FakeProvider x2 | Yes |
| `test_cross_validation_non_doi_identity_extractor` | T.4 | Unit | FakeProvider custom extractor | Yes |
| `test_texas_row_fungibility_against_canonical` (parametrized over providers) | T.5 | Contract | fixture rows | Yes |
| `test_mcp_client_auth_header_construction` | T.6 | Unit | `responses` | Yes |
| `test_mcp_client_jsonrpc_envelope_parse` | T.6 | Unit | `responses` | Yes |
| `test_mcp_client_401_maps_to_mcp_auth_error` | T.6 | Unit | `responses` | Yes |
| `test_mcp_client_429_maps_to_mcp_rate_limit_error` | T.6 | Unit | `responses` | Yes |
| `test_mcp_client_5xx_maps_to_mcp_fetch_error` | T.6 | Unit | `responses` | Yes |
| `test_mcp_client_timeout_maps_to_mcp_fetch_error` | T.6 | Unit | `responses` | Yes |
| `test_legacy_docx_directive_byte_identical_output` | T.7 | Integration | None (27-1 fixture) | **Yes — regression proof** |

**Target baseline delta: +25 collecting tests** (AC-T.8 is non-collecting suite gate). Baseline from 27-1 closeout: 1036 passed / 2 skipped / 0 failed. Expected after 27-0: **1061 passed / 2 skipped / 0 failed**. No new `@pytest.mark.skip`, `xfail`, `live_api`, or `trial_critical` markers.

## Risks

| Risk | Mitigation |
|------|------------|
| **Python MCP client library maturity** — `mcp` PyPI package still 0.x with active breaking changes; HTTP streamable-transport API rewrote multiple times in 2024 | Decision deferred to green-light round. Fallback: hand-rolled JSON-RPC-over-HTTP in `mcp_client.py` (well-scoped, ~120 lines, uses `requests` which is mature). Party selects at green-light based on library state THAT DAY. |
| **First-consumer bias** — if 27-0 is authored in parallel with scite work, scite-idiosyncrasies shape the base class poorly | Foundation ships WITHOUT scite. `FakeProvider` is the only concrete adapter in 27-0. 27-2 scite is the first real stress test; if contract leaks, fix with one adapter of blast radius. |
| **Fungibility claim across providers fails at real-world test** — authority-tier semantics differ radically per provider | Per-provider lookup tables as DATA fixtures (not inference). Adapter declares `declare_honored_criteria()` — unknown keys logged in `refinement_log`, never silently dropped. |
| **Atomic-write semantics under multi-provider fan-out** — cross-validation writes 2+ provider results into merged output; partial-fail mid-write is a real concern | Inherited from 27-2's atomic-write work — staging-directory pattern (per Winston's Round-1 rewrite of AC-B.7). Staging dir atomic-swapped into place; partial fan-out leaves staging abandoned. |
| **Legacy-directive regression (27-1 DOCX)** — refactoring dispatcher as the new router could break byte-identical DOCX output | **AC-T.7 is the regression proof** — 27-1 DOCX fixture runs through new dispatcher via degenerate-case transform; output must be byte-identical. If it fails, ship is blocked. |
| **Test flakiness from iteration-loop sequencing** (Murat's Round 3 concern) | **Resolution: deterministic sequence fixtures, NOT stateful mocks.** Each test pre-scripts the FakeProvider's response sequence; dispatcher loop becomes a pure function over the pre-scripted sequence. No concurrency, no stdio, no async shutdown races. |
| **Schema bump breaks downstream consumers** (Marcus, Vera, Quinn-R reading extraction-report.yaml) | Schema v1.1 is **additive only** — all new fields optional with v1.0-compatible defaults. Changelog prose in `extraction-report-schema.md` justifies minor bump. Consumers are field-tolerant. |
| **`provider_hints` required in v1 breaks operator-direct CLI ergonomics** | AC-B.7 degenerate-case transform: operator-direct directive shape auto-constructs a single-element `provider_hints: [<provider>]` under the hood. CLI UX unchanged for operator; only Tracy must emit the list shape explicitly. |

## Dev Notes

### Architecture (per Round 3 party consensus — Shape 3-Disciplined)

- **Partition by knowledge-locality** (Dr. Quinn): editorial knowledge with Tracy; provider-DSL knowledge with per-provider adapters; dispatch + iteration orchestration with thin Texas shell.
- **Texas is a thin dispatcher + adapter shelf** — resolves the TRIZ contradiction (shallow AND deep) via separation-in-space.
- **Iteration at adapter-level is a loop, not cross-agent dispatch** — preserves "Marcus owns agent-to-agent dispatch" principle.
- **Operator-direct path is the degenerate case** — one contract, two UX surfaces, eliminates coexistence question.
- **Cross-validation is first-class v1** (per operator's Round 3 update): scite + Consensus dispatched in parallel, merged by identity, annotated with convergence signal.

### Round 3 Party Consensus Record

- **Shape 3-Disciplined**: 4 explicit votes (Winston flipped from Shape 1, Amelia from Shape 1, Murat from Shape 1, John from Shape 2); Dr. Quinn refined the framing to produce "Shape 3-Disciplined" with three explicit guardrails.
- **Iteration Model A** (Texas-internal loop): 4-1 (Winston/Amelia/John/Quinn vs Murat dissent on test-flakiness). Resolution: deterministic sequence fixtures, not stateful mocks.
- **Foundation-story-first**: 3 explicit (Amelia/Murat/John), Winston+Quinn implicit. Story 27-0 is the foundation.
- **Deterministic query formulation only** (Amelia+Murat): no LLM-in-the-loop in v1.
- **Required `provider_hints` + mechanical-only AC + convergence signal** (Dr. Quinn's three guardrails).
- **Narrowed scope** (John): Shape 3 for search-shaped providers only; operator-locator providers unchanged.

### Key architectural decisions (ratified)

1. **Iteration Model A** — adapter-internal loop, budget-bounded, abort-on-non-improvement, refinement_log mandatory.
2. **Escape hatch Model B** — when adapter returns `budget_exhausted` or `need_editorial_guidance`, Marcus re-dispatches with Tracy's edited intent.
3. **Cross-validation** — opt-in via `cross_validate: true`; identity-keyed merge; convergence_signal annotation.
4. **Legacy coexistence** — operator-locator providers (DOCX/PDF/Notion/Box/Playwright) unchanged at CLI; internally routed through dispatcher via degenerate-case transform.

### Anti-patterns (dev-agent WILL get these wrong without explicit warning)

- ❌ **Do NOT use LLM-in-the-loop for query formulation or refinement.** v1 is deterministic Python only. Per-provider query strategies are code + data (lookup tables), not inference. LLM-driven expansion is a future story with its own eval framework.
- ❌ **Do NOT write stateful sequence mocks for dispatcher iteration tests.** Use deterministic sequence fixtures — each test pre-scripts the FakeProvider's response sequence as a list; dispatcher loop becomes a pure function over the pre-scripted list. This resolves Murat's test-flakiness concern about Model A.
- ❌ **Do NOT refactor 27-1 DOCX (or any locator-shape provider) to use `RetrievalIntent` directly.** 27-1 is a **locator-shape provider** — its directive shape stays unchanged at the CLI level. The dispatcher handles the translation internally via AC-B.7's degenerate-case transform. AC-T.7 byte-identical-regression test is the proof.
- ❌ **Do NOT bundle scite or any real provider into 27-0.** Foundation ships with `FakeProvider` only. Scite lives in 27-2; Consensus in 27-2.5. This prevents "first-provider shapes the contract poorly" failure mode.
- ❌ **Do NOT make `provider_hints` optional or add provider discovery.** Dr. Quinn's guardrail — in v1, Tracy names the providers; no auto-selection. If an operator doesn't specify, AC-B.7's transform wraps the existing `provider` field into a single-element `provider_hints: [<provider>]` list.
- ❌ **Do NOT evaluate `semantic_deferred` in Texas.** Tracy's post-fetch semantic pass owns that. Texas surfaces the field unchanged in output rows.
- ❌ **Do NOT silently drop unknown acceptance-criteria keys.** Log them in `refinement_log` as "not evaluable by this provider." Future adapters must see criteria they couldn't apply so schema drift is visible.
- ❌ **Do NOT collapse cross-validation into single-provider path.** Multi-provider fan-out is a distinct code path in the dispatcher even when `provider_hints` has length 1 — the single-provider case is a degenerate case of the multi-provider algorithm, not a separate path.
- ❌ **Do NOT choose an MCP client library without explicit green-light approval.** Python MCP library maturity is under active churn. Party green-light selects the library OR approves hand-rolled JSON-RPC-over-HTTP fallback.
- ❌ **Do NOT let `cross_validate: true` fire without identity-extractor declared.** Each adapter must implement `identity_key(row) -> str` (DOI for scholarly, video-id for YouTube, canonical-url for image sources, etc.). If an adapter declares it cannot identify rows uniquely, cross-validation with it raises a clear error at dispatch time — not a silent merge failure.

### Source tree (new + touched)

```
skills/bmad-agent-texas/
├── scripts/
│   ├── retrieval/                              [NEW directory]
│   │   ├── __init__.py                         [NEW +1]
│   │   ├── contracts.py                        [NEW +150]  Pydantic: RetrievalIntent, AcceptanceCriteria, TexasRow, enums
│   │   ├── base.py                             [NEW +180]  RetrievalAdapter ABC + default impls
│   │   ├── dispatcher.py                       [NEW +220]  Single + multi-provider dispatch + iteration + cross-val merge
│   │   ├── mcp_client.py                       [NEW +120]  Python MCP client (HTTP JSON-RPC)
│   │   ├── normalize.py                        [NEW +80]   TexasRow canonical shape helpers
│   │   ├── refinement_registry.py              [NEW +90]   Deterministic refine strategies
│   │   └── fake_provider.py                    [NEW +100]  Reference adapter for foundation tests (FakeProvider)
│   ├── run_wrangler.py                         [TOUCH +60] Integrate dispatcher; legacy-directive auto-transform
│   └── tests/
│       └── test_run_wrangler.py                [TOUCH +30] Legacy-directive auto-transform test + 27-1 byte-identical
└── references/
    ├── extraction-report-schema.md             [TOUCH +70] Schema v1.1 (additive: retrieval_intent, provider_hints, cross_validate, convergence_signal)
    └── retrieval-contract.md                   [NEW +200]  Operator + Tracy-facing contract documentation

tests/contracts/
├── test_acceptance_criteria_schema_stable.py   [NEW +80]   Schema pin (Murat mandatory)
├── test_retrieval_adapter_base.py              [NEW +200]  ABC contract tests over FakeProvider
├── test_texas_row_fungibility.py               [NEW +150]  Cross-provider row-shape equivalence
└── test_transform_registry_lockstep.py         [TOUCH +15] RETRIEVAL_SHAPE_PROVIDERS / LOCATOR_SHAPE_PROVIDERS classification

tests/
├── test_retrieval_dispatcher.py                [NEW +250]  Dispatcher iteration + cross-validation
└── test_retrieval_mcp_client.py                [NEW +120]  Mocked-HTTP MCP client tests

.cursor/mcp.json                                [TOUCH +8]  scite + Consensus URL entries
.mcp.json                                       [TOUCH +8]  scite + Consensus URL entries
scripts/run_mcp_from_env.cjs                    [TOUCH +30] Handle URL-based servers (if needed)
pyproject.toml                                  [TOUCH +1]  Python MCP client dep (TBD at green-light)
.env.example                                    [TOUCH +5]  SCITE_USER_NAME + SCITE_PASSWORD + Consensus equivalents
```

**No changes to:** other providers (they retain existing shapes until their own stories), fidelity contracts, fidelity-gate-map, lane-matrix.

### Previous-story intelligence (from 27-1 DOCX closeout, 2026-04-17)

27-1 established patterns 27-0 MUST inherit:

- **Module loading via `load_module_from_path`** — Texas's hyphenated parent path blocks normal Python imports. All new `retrieval/*.py` modules must be loadable via this pattern; no direct-import assumption.
- **Dispatch-extension (not rewrite)** — the existing `_fetch_source` provider dispatch stays; new dispatcher is a layer **above** it. AC-B.7 degenerate-case transform routes legacy directives through the new dispatcher which delegates to `_fetch_source` for the actual work. 27-1 style: preserve existing code paths, add new routing around them.
- **`_EXTRACTOR_LABELS_BY_KIND` pattern** — new `retrieval/` types may need their own kind-keyed dispatch dicts (e.g., identity-extractor per provider-kind). Mirror the pattern.
- **Module-qualified exception classification** — if MCP client raises `MCPAuthError`, classifier checks `type(exc).__module__.startswith("...retrieval.mcp_client")` to avoid false-matches with foreign exceptions of the same name. Same pattern 27-1 used for `docx.PackageNotFoundError`.
- **CLI UTF-8 guard already in place** — `run_wrangler.py` fires `_cli_encoding.ensure_utf8_stdout()` at module-top. New dispatcher code inherits automatically; no duplication.
- **Co-commit test + impl** — new tests land in the same commit as the source. Pre-commit hook enforces.
- **Review-record structure** — match 27-1's Review Record template: MUST-FIX remediated with `[x] [Review][Patch]`; SHOULD-FIX remediated or deferred with `[x] [Review][Defer]`; NITs dismissed explicitly; Blind / Edge / Auditor layer breakdown.
- **Ruff + orphan + co-commit pre-commit hooks green** — no exceptions.

### Testing standards

- **Unit / contract / integration split**:
  - Unit: dispatcher logic, merger logic, MCP client HTTP mocking.
  - Contract: schema-pin (T.1), ABC-inheritance (T.2), fungibility (T.5). Live at `tests/contracts/`.
  - Integration: legacy-directive byte-identical regression (T.7).
- **HTTP mocking via `responses`** (already a dev-dep from 27-2 pre-green-light scope; promote it here now since 27-0 needs it).
- **Deterministic sequence fixtures for dispatcher tests** — the hard line. NO stateful mocks, NO async / stdio / concurrency plumbing in test paths.
- **No `live_api`, no `trial_critical`, no `xfail`, no `skip`** added to default suite.
- **Fixture hygiene** — all fixtures under `tests/fixtures/retrieval/` as plain-text JSON/YAML; diff-friendly; no binaries.
- **Regression coverage** — +25 collecting tests expected. Verify via `pytest --collect-only | wc -l`.
- **Per `feedback_regression_proof_tests.md`**: no xfail, no skip, classify every failure (update/restore/delete), measure coverage.

### References

- **Epic spine**: [epic-27-texas-intake-expansion.md](./epic-27-texas-intake-expansion.md) — cross-cutting AC-S spine still applies; 27-0 satisfies AC-S3 (structured return) + AC-S4 (failure-mode coverage) + AC-S6 (lockstep extended) + AC-S7 (CP1252 inheritance).
- **Closed 27-1 story (pattern source)**: [27-1-docx-provider-wiring.md](./27-1-docx-provider-wiring.md) — dispatch-extension, error-classification-by-module-prefix, `LOCKSTEP_EXEMPTIONS` dict pattern, in-test fixture generation, co-commit discipline.
- **Round 3 party consensus record** — embedded in this file under §Round 3 Party Consensus Record (consolidated).
- **Tracy vocabulary SSOT** (for `intent_class` values that may surface in `semantic_deferred` field): [skills/bmad-agent-tracy/references/vocabulary.yaml](../../skills/bmad-agent-tracy/references/vocabulary.yaml).
- **Epic 28 spine** (downstream contract consumer): [epic-28/_shared/ac-spine.md](./epic-28/_shared/ac-spine.md) — AC-S1 (dispatch-vs-artifact), AC-S2 (atomic-write), AC-S5 (vocabulary SSOT).
- **Downstream dependents**:
  - [27-2-scite-ai-provider.md](./27-2-scite-ai-provider.md) — will reshape as scite adapter against 27-0 contract.
  - `27-2.5-consensus-adapter` — to be opened post-27-0 as ratified-stub.
  - [28-1-tracy-pilot-scite-ai.md](./28-1-tracy-pilot-scite-ai.md) — Tracy's output contract reshapes to emit intent+AC+provider_hints.
- **Python MCP client references** (for green-light library decision):
  - `mcp` on PyPI (Anthropic reference implementation; 0.x status as of party-round date)
  - Alternative: hand-rolled JSON-RPC-over-HTTP using existing `requests` dep (~120 lines).

### Non-goals

- **No real providers in 27-0** — FakeProvider only. scite = 27-2, Consensus = 27-2.5, YouTube = 27-4, image = 27-3.
- **No LLM-in-the-loop query formulation or refinement** — v1 is deterministic. Deferred to a future story with its own eval framework.
- **No provider-discovery / auto-selection** — `provider_hints` required v1. Dr. Quinn guardrail.
- **No semantic acceptance evaluation** in Texas — `semantic_deferred` surfaces unchanged to Tracy's post-fetch pass.
- **No cross-provider automatic fallback** (try scite, fall back to Consensus) — that's Marcus re-dispatching with edited `provider_hints`, not a Texas feature. Preserves "Marcus owns agent-to-agent dispatch" principle.
- **No concurrency / async in dispatcher** — single-threaded fan-out for multi-provider cross-validation (sequential calls). Concurrency is a future optimization story; proving the contract is the priority.
- **No retrofit of 27-1 DOCX or locator-shape providers to use intent contract directly** — legacy directive shape coexists via AC-B.7 transform. AC-T.7 proves byte-identical output.
- **No authority-tier inference** — lookup tables as data only. Each adapter ships its own provider-to-tier lookup as a fixture.
- **No schema-canary / live-MCP testing** — that's a follow-on story per provider, not foundation scope.

## Dev Agent Record

_(filled by dev-story at implementation time)_

## Review Record

_(filled by bmad-code-review)_

## Party Input Captured (Round 3, 2026-04-17)

- **Winston (Architect):** "Shape 3 supersedes Shape 1. The evolve-later path costs more because it ships the wrong Tracy-prompt shape first." Flipped from Shape 1.
- **Amelia (Dev):** "Do not let 27-2 author the contract AND consume it. That's how spines rot." Foundation-story-first non-negotiable.
- **Murat (Test):** "First-provider shapes contract poorly if contract isn't authored independently." Model A accepted with deterministic sequence fixtures (not stateful mocks) resolving his Model-B preference.
- **John (PM):** "Shape 3 narrowed to search-shaped providers; operator-locator providers keep existing shape. No retrofit needed." Flipped from Shape 2.
- **Dr. Quinn (Problem-Solver):** "Partition by knowledge-locality, not role-tradition. Three guardrails: `provider_hints` required, mechanical-only AC in v1, convergence signal for iteration abort." Reframed the question from "where's the boundary" to "what knowledge does each act require."

## Operator's Decisive Input (2026-04-17)

> "Source material — whether wrangled at the HIL operator's request or at Irene's request via Tracy — is the heart of any academic course content development. It is worth really getting this right (or at least robust) now."

> "Scite is ALREADY available and authenticated as an MCP in Cursor. Consensus, another research tool, is already available and authorized in Cursor. Once we get scite.ai working, we'll duplicate that with Consensus so we can extend Texas's toolset and use one service's findings to confirm or supplement another's."

## Green-Light Patches Applied (party-mode round 1, 2026-04-17)

Four-agent independent green-light round (Winston + Amelia + Murat + Paige) produced these consensus patches BEFORE `bmad-dev-story` execution:

### Python MCP client library — UNANIMOUS Option Y

All 4 panelists voted **Option Y** (hand-rolled JSON-RPC-over-HTTP using existing `requests` dep). Option X (`mcp` PyPI pre-1.0) rejected. Risk calc: Option X breaking-change probability ~60-70% over a 6-month epic window vs. Option Y JSON-RPC 2.0 frozen since 2010 (<5% drift). Implementation constraint: **`mcp_client.py` exposes a narrow library-agnostic public surface** — `call_tool(server, tool, args) -> dict`, `list_tools(server) -> list`. NO `requests.Response` types leak to callers. Enables future Option X migration as a single-file swap when `mcp` PyPI hits 1.0 with compatibility guarantees. Recorded as **AC-Pre resolution**.

### Contract patches (apply to AC-B + AC-C)

- **AC-C.9 (new) — MCP client library-agnostic public surface.** `mcp_client.py` public API is `call_tool(server, tool, args) -> dict`, `list_tools(server) -> list`. No library-specific types in signatures. (Winston MUST-FIX #1)
- **AC-C.10 (new) — `provider_hints` minimum dict shape pinned.** Each entry is `{"provider": <str>, "params": <dict, provider-opaque>}` — required v1. FakeProvider and future Tracy/scite/Consensus adapters must all construct this shape. (Winston MUST-FIX #2 + Amelia partial)
- **AC-B.2 strengthened — Unknown-AC-key behavior: log-and-proceed.** Forward-compatible semantics: dispatcher logs unknown criteria keys at WARNING level as a structured `refinement_log` entry with `reason: "not evaluable by this provider"` + `criterion_key: <key>` fields. Dispatcher proceeds with known criteria; does NOT reject the intent. (Winston MUST-FIX #3 + Amelia AC-C.3 ambiguity fix)
- **AC-C.11 (new) — Dispatcher dumbness clauses.** (a) `convergence_signal` is explicitly **structural** (row-count-agreement, ID-overlap, identity-key-match) NOT semantic; (b) dispatcher is **non-retrying** and **non-fallback** in v1 — cross-provider retry/fallback is Marcus re-dispatching with Tracy's edited `provider_hints`, not a Texas-side feature. (Winston MUST-FIX #6 — architectural drift guard)
- **AC-B.4 strengthened — `provider_hints` required-v1 failure mode.** If directive arrives without `provider_hints` (and is not a legacy-directive auto-transform case), dispatcher raises `ValueError("provider_hints is required v1 — no provider discovery")` at dispatch-time, NOT at contract-test time only. (Amelia AC-B.4 ambiguity fix)

### Test patches (apply to AC-T)

- **AC-T.1 mechanism = Option A (Murat)**: snapshot + allowlist + `SCHEMA_CHANGELOG.md` gate. Pin `RetrievalIntent` + `AcceptanceCriteria` + `TexasRow` as JSON artifacts under `tests/contracts/fixtures/`. Test asserts (a) every field in snapshot present with correct type in current schema, (b) no field removed or retyped, (c) additive fields permitted but logged in `SCHEMA_CHANGELOG.md` which must be human-ack'd. Prevents drift, permits evolution.
- **AC-T.1 strengthened — dual-version test.** Pin BOTH v1.0 and v1.1 artifacts. Legacy row validates against both; new row validates against v1.1 only. Proves additive claim isn't just a version-string change. (Winston MUST-FIX #5)
- **AC-T.4 split — `convergence_signal` into 3 atomic tests** (Murat atomicity): `test_convergence_signal__both_agree`, `test_convergence_signal__disagreement`, `test_convergence_signal__single_source`. Was 4 tests total; now 6.
- **AC-T.7 strengthened — log-line parity + error-path regression** (Winston MUST-FIX #4): (a) assert log-stream structural parity when legacy DOCX directive is transformed through Shape 3 dispatcher vs. direct legacy path; (b) one error-path fixture (malformed DOCX) asserts same exception class + message. **DOCX-only; PDF regression deferred to 27-3+ per Murat scope call** (mechanism-proof via DOCX is sufficient; PDF is future-touched-only).
- **AC-T.2 split — ABC contract tests broken into ≥3 atomic tests** (Amelia atomicity): avoid bundling "contract shape" + "error propagation" + "provider_hints validation" into one test.
- **AC-T.5 split — fungibility into ≥2 atomic tests** (Amelia atomicity): `test_row_identity_preserved_across_providers` + `test_row_ordering_deterministic_per_provider`. Also: canonical shape is a **frozen dict/JSON fixture** under `tests/contracts/fixtures/canonical_texas_row.json`; providers conform TO the canonical, NOT vice versa. (Murat strengthening)
- **AC-T.6 — JSON-RPC response helper.** New `tests/_helpers/mcp_fixtures.py` (~20 lines) exposing `jsonrpc_response(result=...)` and `jsonrpc_error(code=..., message=...)` builders. `responses` library wraps those envelopes. (Murat)
- **AC-T.6 — timeout test mocked at `requests` layer.** Use `responses` library's timeout-simulation, NOT real short-timeout sleeps. Prevents CI-load-induced flakiness. (Murat)
- **AC-T.2 / T.3 strengthened — fixture-delta clear of threshold.** `quality_delta` fixture values clearly above/below the non-improvement threshold, not at the boundary. (Murat flakiness guard)
- **AC-T.3 add (new) — budget-boundary test.** `test_dispatcher_budget_boundary_single_iteration`: `budget=1`, meets-criteria-on-first-iteration case. Edge case between single-shot-meets and budget-exhausted. (Murat add)
- **AC-T.2 add (new) — FakeProvider determinism self-test.** `test_fake_provider_formulate_query_deterministic`: `FakeProvider.formulate_query(same_input)` returns byte-identical output across 100 invocations. Prevents downstream test flake from source-of-truth non-determinism. (Murat add)
- **AC-T.5 add (new) — canonical-shape self-test.** `test_canonical_texas_row_is_schema_valid`: the canonical-shape fixture itself passes the schema-pin. Prevents canonical drifting from schema. (Murat add)
- **AC-T (new) — schema version field contract.** `tests/contracts/test_schema_version_field_present.py` (+20): asserts `schema_version` field is never absent from `extraction-report.yaml` outputs. (Amelia)
- **Writer dual-emit** (Amelia): `run_wrangler.py` writer emits `schema_version: "1.1"` when dispatcher path used; `"1.0"` when legacy path used. Dual-emit gated by code path, not flag. `test_extraction_report_schema_compliance` parametrized `@pytest.mark.parametrize("version", ["1.0", "1.1"])`.
- **AC-T.2 — inheritance target named explicitly.** `tests/contracts/test_retrieval_adapter_base.py` IS the inheritance target for 27-2 / 27-2.5 provider-specific contract tests. Spec mandates future provider stories import and parametrize against this module rather than reimplementing. (Murat)
- **CI flake-detection gate** (Murat): 3x-run flake-detection on merge. Any non-deterministic test across runs = merge fail.

### Doc patches (apply to Dev Notes + doc deliverables)

- **`retrieval-contract.md` ownership shared** (Paige): Paige drives structure / prose / audience segmentation; Amelia countersigns technical accuracy on contract fields, `provider_metadata.<provider>` semantics, lockstep meta-principle.
- **Audience-segmented unified doc** (Paige): one `retrieval-contract.md` file with H2 sections `## For Tracy (intent authors)` / `## For operators (directive authors)` / `## For dev-agents (extending the base)` + appendix cross-refs. NOT three separate docs (SSOT fragmentation risk).
- **Schema v1.1 changelog inside `extraction-report-schema.md`** (Paige): top-level `## Changelog` section immediately below TL;DR and above schema body. Non-negotiable "Why minor bump" paragraph explaining semver-for-schemas rationale.
- **TL;DR negative scope** (Paige): MUST contain explicit "NOT scite, NOT Consensus" phrase — applied above.
- **Anti-pattern prose structure** (Paige): each of the 10 warnings follows "DON'T X, because Y, instead Z" three-beat; each pairs with the positive pattern name it violates. Paige + Amelia co-review during authoring.
- **CLAUDE.md pointer** (Paige + Amelia): one-line add to repo-root CLAUDE.md under a "Texas retrieval" section pointing at `retrieval-contract.md`. Surfaces for fresh Claude Code sessions.
- **Marcus orchestrator references** (Paige): one-liner in Marcus's references that Texas retrieval foundation landed (27-0); scite/Consensus providers pending 27-2/27-2.5. Prevents Marcus surface lying by omission.
- **`docs/dev-guide.md` touch** (Amelia + Paige): **deferred to 27-2** (scope-compress — first adapter author writes the "how to add a provider" section in-situ). 27-0 does NOT create this doc.
- **`test_retrieval_contract_doc_exists.py`** (Amelia): +20-line contract test asserting `retrieval-contract.md` exists, matches existing pattern for Texas reference docs.
- **Lockstep meta-principle** (Paige — extending 27-1 pattern): "A retrieval-shape exemption (RETRIEVAL_SHAPE_PROVIDERS) is a registry row whose extraction output originates from a remote provider call and is shaped by a `RetrievalIntent`; a locator-shape exemption (LOCATOR_SHAPE_PROVIDERS) is a registry row whose extraction output originates from a local filesystem locator and is shaped by a path/selector. The distinction lives in the input-origin axis, not the extractor axis." Landed in test module docstring.

### Pre-dev checks (must pass before `bmad-dev-story` starts)

- **Scite MCP auth shape confirmed** (Amelia R1): confirm HTTP Basic (username:password → base64 Authorization header) before dev begins. If auth flow differs (OAuth, token-exchange, etc.), `mcp_client.py` scope grows and the 5-pt estimate is invalidated — re-estimate.
- **Refinement registry scope** (Amelia R2): Kira/Murat spot-check that `refinement_registry.py` flat-registry shape is adequate for 27-2 scite refinement needs (drop-filters-in-order). If 27-2 needs priority-chains / fallback / complex strategy, 27-0 scope grows.
- **FakeProvider deterministic fixture enumeration** (Amelia R3): `tests/fixtures/retrieval/` directory with ≥2 canned response fixtures documented in the spec's Source Tree.

### Updated scope

- **Target collecting tests: +30** (was +25), baseline 1036 → **1066 passed** / 2 skipped / 0 failed.
- **5-pt estimate holds** IF dev-guide.md authoring deferred to 27-2 (scope-compress) AND MCP library decision locked (Option Y) AND pre-dev checks pass. Otherwise re-estimate at 6.

### Verdicts

Winston **GREEN** (post-MUST-FIX list) · Amelia **YELLOW → GREEN** (post-5-blocker resolution applied above) · Murat **GREEN** (post-3-strengthening + 3-new-test) · Paige **GREEN** (post-5-authoring-time-asks). **Green-light gate: PASSED by consensus.**

## BMAD Closure Criteria

- [ ] All AC-B.1 through AC-B.7 behavioral assertions green.
- [ ] All AC-T.1 through AC-T.7 tests pass; AC-T.8 suite-level regression gate green.
- [ ] All AC-C.1 through AC-C.8 contract-pinning checks satisfied.
- [ ] 27-1 DOCX regression proof: byte-identical output via legacy-directive auto-transform.
- [ ] Repo-level `.cursor/mcp.json` + `.mcp.json` scite + Consensus entries merged.
- [ ] Full pytest green; pre-commit clean.
- [ ] `bmad-party-mode` implementation review consensus: approve.
- [ ] `bmad-code-review` layered pass; MUST-FIX remediated; SHOULD-FIX triaged.
- [ ] `sprint-status.yaml` flipped to `done` with closure comment.
- [ ] Epic 27 roster updated; 27-2 and 27-2.5 unblocked.
- [ ] 28-1 Tracy spec amended to reflect new output contract (intent+AC+provider_hints, not scite-queries).
