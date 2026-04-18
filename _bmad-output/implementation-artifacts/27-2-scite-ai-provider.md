# Story 27.2: scite.ai Provider (RetrievalAdapter subclass + deferred-27-0 cascade)

**Status:** ready-for-dev (green-light round 1 closed 2026-04-18 — 13 MUST-FIX applied; see §Green-Light Patches Applied)
**Created:** 2026-04-17 (ratified-stub post-Round-3 party consensus); pre-reshape 382-line expansion 2026-04-17 22:45 (archived); **re-expanded against Shape 3-Disciplined 27-0 contract 2026-04-18** via `bmad-create-story`; **green-light round 1 patches applied 2026-04-18** via four-panelist party-mode (Winston / Amelia / Murat / Paige).
**Epic:** 27 — Texas Intake Surface Expansion
**Sprint key:** `27-2-scite-ai-provider`
**Branch:** `dev/epic-27-texas-intake`
**Points:** 5 (holds under PDG resolutions: path-B / path-B / path-A — see §Pre-Development Gate)
**Depends on:** [27-0 Retrieval Foundation](./27-0-retrieval-foundation.md) (DONE 2026-04-18 — `RetrievalAdapter` ABC + dispatcher + `MCPClient` + contracts + `provider_directory`).
**Blocks:** **Epic 28 — Tracy the Detective** (28-1 pilot depends on scite adapter). Soft-enables [27-2.5 Consensus adapter](./epic-27-texas-intake-expansion.md) — 27-2.5 is the second retrieval-shape adapter and the first real `cross_validate: true` exercise (scite + Consensus).
**Supersedes:** Pre-reshape 382-line expansion (2026-04-17 22:45) — archived at [archive/27-2-scite-pre-reshape-2026-04-17.md](./archive/27-2-scite-pre-reshape-2026-04-17.md). A compressed scite-domain-knowledge extract is preserved inline at [§Historical Domain Knowledge](#historical-domain-knowledge-pre-reshape-extract) at the bottom of this file.

## Reshape notice (2026-04-18)

The story below is the **active dev target.** The pre-reshape 382-line expansion (preserved under §Historical Reference) predates 27-0 closure and mis-shapes scite as a standalone `SciteClient` + `wrangle_scite_paper()` function under `scripts/providers/`. That shape is obsolete. Under Shape 3-Disciplined (Round-3 consensus), scite lands as a `RetrievalAdapter` subclass in `skills/bmad-agent-texas/scripts/retrieval/scite_provider.py`, auto-registers via `PROVIDER_INFO`, and uses 27-0's `MCPClient` for transport. Historical content is preserved for domain-knowledge reference only (endpoint shapes, smart-citation metadata fields, paywall semantics) — **do not follow it for implementation.**

## TL;DR

- **What:** Author `SciteProvider(RetrievalAdapter)` at `skills/bmad-agent-texas/scripts/retrieval/scite_provider.py` — the first real consumer of 27-0's ABC. Uses existing `MCPClient` (Option Y hand-rolled JSON-RPC) against the scite.ai MCP. Auto-registers via `PROVIDER_INFO` ClassVar, superseding the `scite: ratified` placeholder in `provider_directory.py` so `list_providers()` flips `scite` to `status="ready"`.
- **Cascade from 27-0 (absorbed into this story's scope):**
  1. **AC-B.6 literal dispatcher wiring** — `run_wrangler.py` routes retrieval-shape directives (`intent` + `provider_hints`) through `dispatcher.dispatch()`; locator-shape directives preserve existing `_fetch_source` path per anti-pattern #3. **Dual-emit is an UPSTREAM ROUTING concern, NOT a locator-shape refactor** (Winston green-light carve-out — §Anti-pattern Guardrails).
  2. **Dual-emit `schema_version` writer with discriminant contract** — writer takes an explicit `code_path` discriminant enum; mismatched field sets raise, not silently drop (Winston MUST-FIX #1 — AC-C.11). Emits `"1.1"` for retrieval-shape path, `"1.0"` for legacy path.
  3. **AC-T.6 regression tests** — log-stream parity via **golden file + regex scrubber** (pinned mechanism per Amelia/Murat MUST-FIX — see AC-T.6); malformed-DOCX exception-class parity for legacy DOCX directive.
  4. **Parametrized `test_extraction_report_schema_compliance`** over `["1.0", "1.1"]` — AC-T.7.
  5. **Module-prefix exception contract test** — every `SciteProvider`-raised exception's `type(exc).__module__.startswith("retrieval.")` — no `requests.*` / `urllib3.*` leakage (Winston MUST-FIX #2 — AC-T.10).
  6. **`docs/dev-guide.md` "How to add a retrieval provider" Recipe-4 + sharded file** — Paige+Amelia co-authored; Extension Guide gets stub Recipe-4 pointing at sharded `docs/dev-guide/how-to-add-a-retrieval-provider.md` (Paige MUST-FIX #2 — AC-C.9).
- **Why:** Tracy (Epic 28) dispatches against scite for its differentiating value over generic search — smart citation context (supporting / contradicting / mentioning classifications with snippets). scite is the pilot retrieval-shape provider; 27-2.5 duplicates the pattern for Consensus; cross-validation then becomes first-class.
- **Size:** 5 pts (holds under PDG path-B/B/A). Custom-strategy expansion caps at ≤2 under 5 pts; 3+ → re-estimate to 6 pts (Amelia MUST-FIX #4).
- **Key decisions ratified at green-light round 1:** uses 27-0's `MCPClient` public surface; HTTP Basic auth (`SCITE_USER_NAME` + `SCITE_PASSWORD`); identity_key = DOI (fallback `scite_paper_id` → `source_id`); synthetic JSON fixtures via `responses` library; no live_api / no xfail / no trial_critical under PDG path-B resolution; task order **T1 skeleton → T8 wiring → T2-T7 guts** (Amelia MUST-FIX #3 — skeleton-first wiring validation); test-count floor **≥22 collecting pinned** (Murat MUST-FIX #3 — not a range); follow-on `27-2-live-cassette-refresh` story ticket committed at green-light (Murat MUST-FIX #4).

## Pre-Development Gate (RESOLVED — green-light round 1, 2026-04-18)

All three sub-gates resolved by unanimous panelist consensus (Winston / Amelia / Murat / Paige). Full resolution record in §Green-Light Patches Applied.

| Gate | Resolution | Rationale |
|------|------------|-----------|
| **PDG-1: Auth credentials** | **Path B — synthetic-fixture-only.** | No dependency on `.env` credential acquisition; `responses` library + hand-crafted JSON fixtures give full coverage of `execute` / `normalize` / `refine`. Live verification deferred to follow-on `27-2-live-cassette-refresh` story (ticket committed at green-light per Murat MUST-FIX #4). Risk-weighted: live creds give ~10% fixture-fidelity improvement vs ~40% CI-bleed risk (Murat). |
| **PDG-2: MCP tool catalog** | **Path B — inferred from scite.ai/api-docs + public MCP docs.** | Consequence of PDG-1=B. Fixture source documented as "inferred from scite.ai/api-docs v2026-04-18" in `tests/fixtures/retrieval/scite/README.md`. First live run becomes the moment-of-truth; diff → follow-on hardening (Winston). |
| **PDG-3: Refinement strategies** | **Path A — `drop_filters_in_order` only.** | With scite-specific order list (`supporting_citations_min → authority_tier_min → date_range → cited_by_count_min`), monotonic looseness is covered (Winston). Custom strategies are speculative until real-run data; ship path A, promote via `27-2-refinement-hardening` follow-on if first live dispatch shows exhaustion clustering on the drop-in-order tail. YAGNI. Scope ceiling: ≤2 custom strategies hold 5 pts; 3+ → 6 pts (Amelia MUST-FIX #4). |

**Follow-on story tickets committed at green-light** (Murat MUST-FIX #4):

- `27-2-live-cassette-refresh` — opens when/if operator acquires `SCITE_USER_NAME` + `SCITE_PASSWORD`; records live cassettes into `tests/fixtures/retrieval/scite-live/`; schema-canary test diffs against synthetic fixtures.
- `27-2-refinement-hardening` — opens only if first live run shows `drop_filters_in_order` inadequate; adds scite-specific custom strategies to `refinement_registry.py`.

**Dev-story cleared to start.** PDG resolution is terminal; no further gates remain.

## Anti-pattern Guardrails (Winston MUST-FIX #3 carve-out)

The AC-B.6 dispatcher-wiring cascade interacts with 27-0's anti-pattern #3 ("Do NOT retrofit 27-1 DOCX or any locator-shape provider to use `RetrievalIntent` directly"). The carve-out Winston negotiated at green-light, stated plainly for Amelia at dev time:

- ✅ **Permitted** (this is NOT a locator-shape refactor):
  - Upstream directive-row shape detection in `run_wrangler.py` (new `_classify_directive_shape()` helper).
  - Routing retrieval-shape directives through `dispatcher.dispatch()`.
  - Dual-emit `schema_version` at the writer (gated on code path, not on a flag).
  - Additive `"1.0"` `schema_version` field on legacy output rows (consumers that don't read it are unaffected; 27-1 byte-identical was about row *content*, not the absence of a version tag — AC-T.6 proves this).

- ❌ **Prohibited** (this IS a locator-shape refactor — do not do):
  - Opening `source_wrangler_operations.py` to make DOCX / PDF / HTML consume `RetrievalIntent`.
  - Wrapping locator-shape directives in a degenerate `RetrievalIntent` upstream of `_fetch_source`.
  - Touching `_fetch_source`'s provider-dispatch internals (existing branches stay exactly as they are).
  - Rerouting locator-shape directives through `dispatcher.dispatch()` via a degenerate-case transform (AC-B.7 of 27-0 is aspirational; do NOT implement it here).

**The mental model**: dual-emit is an *upstream routing concern at the wrangler's dispatch cap*. Locator-shape code below `_fetch_source` is not opened. This carve-out MUST appear in the dev-guide Recipe-4 as a warning to future retrieval-provider authors who will be tempted to collapse the two paths.

## Story

As the **Texas wrangler**,
I want **a `SciteProvider` `RetrievalAdapter` subclass that translates natural-language intents into scite MCP queries, executes them via the 27-0 `MCPClient`, applies mechanical + provider-scored filters, and normalizes results to canonical `TexasRow` with scite's smart-citation metadata carried in `provider_metadata.scite`**,
So that **Tracy's editorial dispatch (Epic 28) — emitted as `RetrievalIntent` with `provider_hints: [{provider: "scite", ...}]` — routes through the dispatcher and produces DOI-keyed rows ready for cross-validation with Consensus (27-2.5), and the dispatcher is for the first time literally wired into `run_wrangler.py` (AC-B.7 cascade from 27-0)**.

## Background — Why This Story Exists

Round-3 party consensus (2026-04-17) ratified Shape 3-Disciplined retrieval architecture (Dr. Quinn's knowledge-locality partitioning). 27-0 closed BMAD-clean 2026-04-18 with the ABC + dispatcher + MCPClient + contracts + provider_directory foundation, but **shipped with `FakeProvider` only** — no real provider in 27-0 by explicit anti-pattern #4 guard ("Do NOT bundle scite or any real provider into 27-0"). 27-2 is now the first real stress test of the contract.

Four DISMISSED-with-rationale findings from 27-0's layered code-review cascade into 27-2 scope because they cannot be cleanly verified without a real retrieval-shape integration. Per 27-0 Review Record (DISMISSED rationale): *"AC-B.7 literal wiring + cascade ... Full wiring + downstream cascade tests land naturally with 27-2 (first real retrieval-shape integration)."*

scite.ai's differentiating value over generic search is **smart citation context** — it classifies citations as *supporting / contradicting / mentioning* with context snippets. This is the exact signal Tracy's authority-plus-recency-plus-relevance scoring leverages. Operator directive (2026-04-17): *"Scite is ALREADY available and authenticated as an MCP in Cursor. ... Once we get scite.ai working, we'll duplicate that with Consensus so we can extend Texas's toolset and use one service's findings to confirm or supplement another's."*

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — `SciteProvider(RetrievalAdapter)` subclass ships.** New module `skills/bmad-agent-texas/scripts/retrieval/scite_provider.py`. Class `SciteProvider` subclasses `RetrievalAdapter`; declares `PROVIDER_INFO: ClassVar[ProviderInfo]` with `id="scite"`, `shape="retrieval"`, `status="ready"`, `auth_env_vars=["SCITE_USER_NAME", "SCITE_PASSWORD"]`, `spec_ref` pointing at this file, `capabilities` list extending the placeholder's (adds `"smart-citation-classification"`). On module import, `__init_subclass__` auto-registers via `provider_directory.register_adapter`, superseding the `scite: ratified` placeholder; `list_providers()` now shows `scite: ready`.

2. **AC-B.2 — Seven abstract methods implemented.** Per 27-0 ABC contract:
   - `formulate_query(intent: RetrievalIntent) -> dict` — deterministic translation of `intent.intent` + `provider_hints[scite].params` into a scite query dict (`{mode: "search"|"paper"|"citation_contexts", query: str | doi: str, filters: {...}}`). Byte-identical across invocations with same input (AC-T.2 determinism self-test).
   - `execute(query: dict) -> list[dict]` — dispatches to `MCPClient.call_tool("scite", tool_name, args)` per query mode. Raises `MCPAuthError` / `MCPRateLimitError` / `MCPFetchError` / `MCPProtocolError` unchanged (dispatcher wraps these in `ProviderResult` with `acceptance_met: False`). No retry logic inside adapter — Marcus re-dispatches on fatal errors per AC-C.11 dumbness clause.
   - `apply_mechanical(results, criteria) -> filtered` — honored keys: `date_range` ([start, end] YYYY-MM-DD; row.date within), `min_results` (passthrough; dispatcher post-evaluates count), `exclude_ids` (DOI or scite paper-id), `license_allow` (if scite surfaces license flag).
   - `apply_provider_scored(results, criteria) -> filtered` — honored keys: `authority_tier_min` (lookup table: `peer-reviewed=3 / preprint=2 / web=1`), `supporting_citations_min` (scite's `supporting_count` field), `cited_by_count_min` (scite's total citation count).
   - `normalize(results) -> list[TexasRow]` — scite paper → canonical `TexasRow`. `title`, `body` (abstract + full_text_if_available), `authors`, `date` from paper metadata. `provider_metadata.scite` sub-object holds scite-specific fields: `doi`, `supporting_count`, `contradicting_count`, `mentioning_count`, `citation_context_snippets[]` (≤3 per classification; each with `classification`, `citing_doi`, `snippet`), `scite_report_url`, `scite_paper_id`, `venue` (nullable), `authority_tier` (derived). Authority tier also exposed at top-level `TexasRow.authority_tier`.
   - `refine(previous_query, previous_results, criteria) -> dict | None` — monotonically-loosening. Default path uses `refinement_registry.drop_filters_in_order` with scite-specific order: `supporting_citations_min` → `authority_tier_min` → `date_range` → `cited_by_count_min`. If PDG-3 resolves path B, additional scite-specific strategies land in `refinement_registry.py`. Returns `None` when all filter keys exhausted.
   - `identity_key(row: TexasRow) -> str` — DOI from `row.provider_metadata["doi"]` (primary); fallback `row.provider_metadata["scite_paper_id"]` if DOI missing (preprint case); fallback `row.source_id` as last resort. Raises `NotImplementedError` ONLY if none available — used for `cross_validate: true` preflight check in dispatcher.

3. **AC-B.3 — `declare_honored_criteria` returns explicit key set.** Not the default empty set — returns `frozenset({"date_range", "min_results", "exclude_ids", "authority_tier_min", "supporting_citations_min", "cited_by_count_min", "license_allow"})`. Unknown keys in `intent.acceptance_criteria.mechanical` / `.provider_scored` will log to `refinement_log` (AC-B.2 strengthened in 27-0) but won't block dispatch.

4. **AC-B.4 — Paywall graceful degradation.** When scite's paper-metadata response indicates `full_text_available: false` (or equivalent), `normalize` produces a row with body = abstract only; `provider_metadata.scite.known_losses = ["full_text_paywalled"]`. The existing `completeness_ratio` downstream logic (Vera / Quinn-R) handles tier downgrade automatically — no special-case code in the adapter.

5. **AC-B.5 — Controlled failure on scite-specific errors.** MCPClient exceptions flow through unchanged: auth failure (401/403) → `MCPAuthError` → dispatcher records `ProviderResult` with `acceptance_met: False` + `refinement_log` entry `reason="auth_failed"`. Rate-limit (429) → `MCPRateLimitError` → same, `reason="rate_limited"`. Generic fetch/timeout → `MCPFetchError` → `reason="fetch_failed"`. Malformed JSON-RPC response → `MCPProtocolError` → `reason="protocol_error"`. **No traceback leaks to stdout** (handled by MCPClient). Missing auth env vars → `MCPAuthError` at first `call_tool` invocation (lazy resolution per MCPClient design).

6. **AC-B.6 — `run_wrangler.py` dispatcher wiring (AC-B.7-cascade from 27-0, with discriminant contract).** Directive load branches on shape via a new helper:

   ```python
   def _classify_directive_shape(src: dict) -> Literal["retrieval", "locator", "malformed"]:
       has_intent = "intent" in src and "provider_hints" in src
       has_locator = "provider" in src and "locator" in src
       if has_intent and not has_locator: return "retrieval"
       if has_locator and not has_intent: return "locator"
       return "malformed"
   ```

   - Directive row classified as **"retrieval"** → construct `RetrievalIntent`, call `dispatcher.dispatch(intent)`, receive `ProviderResult` (single) or `list[ProviderResult]` (cross-validate), write each `TexasRow` as a source entry with `schema_version: "1.1"`, populate `retrieval_intent` / `provider_hints` / `cross_validate` / `convergence_signal` / `source_origin` / `tracy_row_ref` fields per schema v1.1 additive.
   - Directive row classified as **"locator"** → existing `_fetch_source` dispatch unchanged (per anti-pattern #3 no-refactor-of-locator-shape); output written with `schema_version: "1.0"` (dual-emit per deferred cascade).
   - Directive row classified as **"malformed"** → exit 30 with clear error naming the ambiguous/missing keys. Suggested error prose: `"Directive row ambiguous: exactly one of {intent+provider_hints} or {provider+locator} must be present; got: {<observed_keys>}"`.
   - **Both paths converge on `write_extraction_report`, but the writer takes an explicit `code_path` discriminant** (see AC-C.11). Dual-emit is gated on code path, NOT a flag.

7. **AC-B.7 — `docs/dev-guide.md` "How to add a provider" section added.** New section authored by Paige + Amelia co-review (deferred from 27-0 per green-light doc patch). Content: (a) subclass `RetrievalAdapter`; (b) declare `PROVIDER_INFO` ClassVar; (c) implement 7 abstract methods; (d) add test by parametrizing `tests/contracts/test_retrieval_adapter_base.py`; (e) register auth env vars in `PROVIDER_INFO.auth_env_vars`; (f) update `retrieval-contract.md` if provider introduces new provider_metadata fields. Worked example: SciteProvider as living reference.

### Test (AC-T.*)

1. **AC-T.1 — `SciteProvider` unit tests with atomicity splits (Murat MUST-FIX #2)** (`tests/test_retrieval_scite_provider.py`, NEW). 11 atomic tests — one assertion-cluster per test. Uses `responses.RequestsMock()` **per-test context manager** (module-level leaks across tests; anti-pattern #8 guard). Scite MCP responses are JSON fixtures under `tests/fixtures/retrieval/scite/`.

   **`formulate_query` atoms (3):**
   - `test_scite_formulate_query_deterministic` — same `RetrievalIntent` → byte-identical query dict across 100 invocations.
   - `test_scite_formulate_query_search_mode` — topical intent + `{mode: "search"}` hint → search-shaped query dict.
   - `test_scite_formulate_query_doi_mode` — direct-DOI intent + `{mode: "paper"}` hint → paper-metadata-shaped query dict.

   **`execute` atoms (3 — split from original `test_scite_execute_happy_path`):**
   - `test_scite_execute_calls_correct_tool_name` — assert MCPClient.call_tool invoked with exactly `("scite", "<expected_tool>", ...)`.
   - `test_scite_execute_passes_args_verbatim` — assert the args dict matches the formulated query verbatim (no key re-mapping in `execute`).
   - `test_scite_execute_returns_parsed_list` — assert return value is a list of dicts with expected scite fields (title, doi, supporting_count, etc.).

   **`execute` error paths (1):**
   - `test_scite_execute_auth_error_propagates` — `responses` stub returns 401; MCPClient raises `MCPAuthError`; adapter re-raises unchanged (no transport-type leakage — AC-T.10 covers the parent contract).

   **`normalize` atoms (3 — split from original `test_scite_normalize_populates_provider_metadata`):**
   - `test_scite_normalize_extracts_doi_to_identity` — synthetic paper → `TexasRow.provider_metadata["doi"]` populated; `SciteProvider.identity_key(row)` returns that DOI.
   - `test_scite_normalize_truncates_citation_contexts_to_3_per_classification` — fixture has 10 supporting + 10 contradicting + 10 mentioning contexts; normalized output has exactly 3 per classification.
   - `test_scite_normalize_derives_authority_tier_via_lookup_table` — fixture venue "Nature Medicine" → `row.authority_tier == "peer-reviewed"` per `SCITE_AUTHORITY_TIERS` lookup.

   **`normalize` paywall degradation (1):**
   - `test_scite_normalize_paywall_degrades_to_abstract` — fixture has `full_text_available: false` → body = abstract only; `provider_metadata.scite.known_losses: ["full_text_paywalled"]`.

   **Total AC-T.1 atoms: 11.** Each test asserts ONE thing; ONE `responses.RequestsMock()` context per test (no module-level fixture leakage).

2. **AC-T.2 — Parametrize `test_retrieval_adapter_base.py` over SciteProvider + scaffold refactor (Amelia MUST-FIX #1 / Murat strengthening #7).** Per 27-0's explicit-inheritance-target mandate: 27-2 parametrizes the ABC-contract tests over both `FakeProvider` AND `SciteProvider`. BUT the current `tests/contracts/test_retrieval_adapter_base.py:23-45` hard-codes FakeProvider in both `intent` + `adapter` fixtures — it is NOT yet parametrized. 27-2 does the scaffold refactor as part of AC-T.2.

   **Required scaffold refactor (+30 LOC, not +20)**:

   ```python
   # tests/contracts/test_retrieval_adapter_base.py

   ADAPTER_FACTORIES = [
       ("fake", _make_fake_adapter),       # returns (adapter_instance, intent_for_adapter)
       ("scite", _make_scite_adapter),     # returns (adapter_instance, intent_for_adapter)
   ]

   @pytest.fixture(params=ADAPTER_FACTORIES, ids=lambda p: p[0])
   def adapter_and_intent(request):
       _id, factory = request.param
       return factory()

   # Existing tests refactored to consume `adapter_and_intent` instead of hardcoded FakeProvider.
   ```

   Each factory encapsulates its adapter's specific fixture data (FakeProvider's `rows_by_query`, SciteProvider's `responses`-library-mocked HTTP stubs).

   **Tests that run parametrized (inherited; NO reimplementation):**
   - `test_adapter_base_formulate_query_deterministic[fake]` + `[scite]`
   - `test_adapter_base_apply_mechanical_deterministic[fake]` + `[scite]`
   - `test_adapter_base_refine_monotonic_looseness[fake]` + `[scite]`
   - `test_adapter_base_declare_honored_criteria_introspection[fake]` + `[scite]`
   - `test_adapter_base_identity_key_returns_scalar[fake]` + `[scite]`
   - Any additional base tests the 27-0 module exposes — all inherit via the factory fixture.

   **Anti-pattern guard**: if the dev agent is tempted to copy test bodies into `test_retrieval_scite_provider.py`, stop — parametrize through the fixture factory instead.

   **Scope delta**: `test_retrieval_adapter_base.py` +30 LOC for refactor; new parametrized test IDs show both `[fake]` and `[scite]` in pytest output.

3. **AC-T.3 — Refinement strategy test.** `test_scite_refine_monotonic_looseness` (in `test_retrieval_scite_provider.py`): starts with full acceptance criteria (all 6 honored keys set), iterates `refine()` N times, asserts (a) each returned query has fewer restrictive keys than the previous, (b) after 6 iterations `refine()` returns `None`, (c) log entries emitted at every step. If PDG-3 resolves path B (custom strategies), tests also cover scite-specific loosening (e.g., `test_scite_refine_authority_tier_relaxation`).

4. **AC-T.4 — Dispatcher integration smoke.** `test_retrieval_scite_dispatch_single_provider` (in `tests/test_retrieval_dispatcher.py`, ADD): FakeProvider-style sequence fixture for scite — uses `responses` library at the MCPClient HTTP layer rather than in-memory query-to-result map. Asserts `dispatcher.dispatch(scite_intent)` returns `ProviderResult` with populated `rows`, `acceptance_met`, `iterations_used`, `refinement_log`. **Cross-validation test with Consensus is 27-2.5 scope**, not here.

5. **AC-T.5 — `run_wrangler.py` dispatcher-wiring regression (AC-B.7 cascade).** `tests/test_run_wrangler_retrieval_shape.py` (NEW):
   - `test_retrieval_shape_directive_routes_through_dispatcher` — intent-shape directive → `schema_version: "1.1"` emitted; all 6 retrieval-shape schema fields present (retrieval_intent, provider_hints, cross_validate, convergence_signal, source_origin, tracy_row_ref).
   - `test_locator_shape_directive_preserves_legacy_path` — legacy provider+locator directive → `schema_version: "1.0"` emitted; no retrieval-shape fields present.
   - `test_malformed_shape_directive_exits_30` — directive with both `intent` and `provider`+`locator` → exit 30 with "ambiguous shape" error.

6. **AC-T.6 — Legacy DOCX log-stream + exception parity with PINNED golden-file mechanism (Amelia MUST-FIX #2 / Murat MUST-FIX #1).** `tests/test_run_wrangler_legacy_docx_parity.py` (NEW). Mechanism explicitly pinned — no regex-guessing at code-review time.

   **Golden-file baseline capture** (one-time, pre-cascade):
   - `tests/fixtures/regression/legacy_docx_baseline/log_stream.txt` — run `run_wrangler` on the 27-1 DOCX fixture before the AC-B.6 wiring patch lands; capture log stream to this golden file.
   - `tests/fixtures/regression/legacy_docx_baseline/exception_class.json` — run against a malformed DOCX fixture; capture `{exception_class: str, error_kind: str, error_detail_prefix: str}` to this golden.
   - Golden files committed to git; regenerated only via a documented procedure (new dev-guide Recipe-4 subsection).

   **Log-stream scrubber** (`_normalize_log_stream` helper in the test module):
   - Masks ISO-8601 timestamps: `r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?"` → `"<TIMESTAMP>"`.
   - Masks wall-clock durations: `r"\d+\.\d+ ?(ms|s|seconds)"` → `"<DURATION>"`.
   - Masks PIDs: `r"\bpid[= ]\d+"` → `"pid=<PID>"`.
   - Masks absolute Windows/POSIX path prefixes: `r"[A-Z]:\\\\[^\s]+|/[a-z_/-]+/"` → `"<PATH_PREFIX>/"`.
   - Scrubber self-test: `test_log_stream_scrubber_normalizes_known_shapes` with hand-crafted input/output pairs proves the scrubber itself has coverage before it's used as test infrastructure.

   **The two regression tests**:
   - `test_docx_directive_log_stream_structural_parity` — invokes `run_wrangler` on 27-1 DOCX fixture post-cascade; runs output through `_normalize_log_stream`; asserts `scrubbed_actual == golden_text` via plain string equality (no diff libs, no fuzzy compare, no syrupy).
   - `test_docx_malformed_exception_class_parity` — invokes `run_wrangler` on corrupt DOCX fixture post-cascade; asserts `type(exc).__name__ == golden_exception_class` AND `error_kind == golden_error_kind` AND `error_detail.startswith(golden_error_detail_prefix)`.

   **Scrubber hygiene test (companion)**:
   - `test_log_stream_scrubber_normalizes_known_shapes` — 3-5 input/expected pairs covering each regex pattern. Prevents scrubber drift without coverage.

   **Rationale for golden-file approach over snapshot libraries** (e.g., syrupy): no new deps; diff-friendly; Paige's dev-guide can describe the regeneration procedure in plain markdown without tooling. Winston: "structural parity with timestamp normalization" is the correct strictness level — bit-exact would couple tests to Python version + log-handler formatting.

   **AC-T.6 test count: 3 atoms** (log-stream parity + malformed exception parity + scrubber self-test).

7. **AC-T.7 — Parametrized schema-compliance test** (deferred-cascade). `tests/contracts/test_extraction_report_schema_compliance.py` (NEW or extension): `@pytest.mark.parametrize("version", ["1.0", "1.1"])` validates a canonical `extraction-report.yaml` output for each version against the pinned schema in `extraction-report-schema.md`. v1.0 row uses legacy shape; v1.1 row has retrieval-shape additive fields populated.

8. **AC-T.8 — `SciteProvider` auto-registration contract test.** Inherited from 27-0 `test_provider_directory_autoregister.py` — no new test needed; importing `scite_provider` is enough for existing test to notice the new entry. Validation: `list_providers(shape="retrieval", status="ready")` returns SciteProvider's PROVIDER_INFO; the `scite: ratified` placeholder is superseded.

9. **AC-T.9 — Regression suite-level gate with FLOOR PINNED ≥22 (Murat MUST-FIX #3).** Baseline from 27-0 closeout: **1106 passed / 2 skipped / 0 failed / 2 xfailed**. After 27-2, floor pinned at **≥22 collecting additions** — post-atomicity-splits count:

   | Cluster | Tests | AC |
   |---------|-------|-----|
   | SciteProvider units (atomicity-split) | 11 | AC-T.1 |
   | ABC-contract parametrized `[scite]` | ≥5 | AC-T.2 |
   | Refinement | ≥2 | AC-T.3 |
   | Dispatcher-scite integration | 1 | AC-T.4 |
   | run_wrangler shape-routing | 3 | AC-T.5 |
   | Legacy DOCX parity + scrubber self-test | 3 | AC-T.6 |
   | Schema-compliance parametrized over `["1.0","1.1"]` | 2 | AC-T.7 |
   | Module-prefix exception contract | 1 | AC-T.10 |
   | Writer discriminant mismatched-call guards | 2 | AC-C.11 test |
   | No-stateful-mock anti-pattern guard | 1 | AC-T.11 |
   | **Minimum floor** | **≥31** | — |

   Expected after 27-2: **≥1137 passed** / 2 skipped / 0 failed / 2 xfailed. No new `@pytest.mark.skip`, `xfail`, `live_api`, `trial_critical`. Ranges drift; floors regress-gate — this is a floor, not a range.

10. **AC-T.10 — Module-prefix exception contract test (Winston MUST-FIX #2).** New test in `tests/test_retrieval_scite_provider.py`:

    ```python
    def test_scite_provider_exceptions_never_leak_transport_types():
        """AC-T.10 — no requests.* / urllib3.* exception classes reach callers."""
        provider = SciteProvider()
        # Enumerate every raise path via 401/403/429/500/timeout/malformed-JSON stubs
        for status, _ in [(401, "auth"), (429, "rate"), (500, "fetch"), ...]:
            with responses.RequestsMock() as rsps:
                rsps.add(responses.POST, SCITE_MCP_URL, json={...}, status=status)
                try:
                    provider.execute(provider.formulate_query(intent))
                except Exception as exc:
                    assert type(exc).__module__.startswith("retrieval."), (
                        f"SciteProvider leaked {type(exc).__module__}.{type(exc).__name__} "
                        f"— must be retrieval.* (Option-X escape hatch)"
                    )
                    assert "requests" not in type(exc).__module__
                    assert "urllib3" not in type(exc).__module__
    ```

    **Rationale**: the Option-X migration escape hatch (when `mcp` PyPI hits 1.0) depends on `mcp_client.py` never letting `requests` types leak out. A future contributor adding richer error context could accidentally re-raise `requests.Response`-shaped data in an exception message; this test is the smoke alarm.

11. **AC-T.11 — No-stateful-mock anti-pattern guard (Murat strengthening #8).** New test in `tests/test_retrieval_scite_provider.py`:

    ```python
    def test_scite_provider_test_module_has_no_stateful_mocks():
        """AC-T.11 — anti-pattern #2 guard (Murat's Model A → deterministic fixtures)."""
        module_source = Path(__file__).read_text()
        for forbidden in ["MagicMock", "AsyncMock", "from unittest.mock import Mock"]:
            assert forbidden not in module_source, (
                f"SciteProvider tests must not use {forbidden} — "
                f"use `responses.RequestsMock()` + deterministic fixtures instead."
            )
    ```

    Prevents regression of Murat's Model A deterministic-fixture discipline. Also guards against copy-paste from other test modules that may use `Mock` legitimately in different contexts.

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Adapter lives in `retrieval/` package, NOT `scripts/providers/`.** New file at `skills/bmad-agent-texas/scripts/retrieval/scite_provider.py`. The pre-reshape spec's `scripts/providers/scite_client.py` path is superseded; scite is a `RetrievalAdapter` subclass alongside `fake_provider.py`, not a standalone HTTP client module.

2. **AC-C.2 — Uses 27-0 `MCPClient` public surface exclusively.** SciteProvider calls `MCPClient.call_tool("scite", tool, args)` and `MCPClient.list_tools("scite")`. Does NOT construct its own `requests.Session`, does NOT import `requests.Response` or any `requests` exception types, does NOT receive or return `requests` objects at any method boundary. The Option-X migration escape hatch must remain open (per 27-0 AC-C.9).

3. **AC-C.3 — `PROVIDER_INFO` supersedes placeholder.** When SciteProvider is imported, `__init_subclass__` auto-registers. The `_RETRIEVAL_SHAPE_PLACEHOLDERS` tuple in `provider_directory.py` retains the `scite: ratified` entry; `list_providers()` merge-order (registered adapters first) causes the live entry to supersede. Do NOT delete the placeholder — it remains as a fallback for the case where `scite_provider` fails to import.

4. **AC-C.4 — Schema v1.1 additive fields + schema-doc layering split (Paige MUST-FIX #3).** Two distinct contract obligations:

   **(a) Field population on retrieval-shape path**: `run_wrangler.py` writer populates `retrieval_intent`, `provider_hints`, `cross_validate`, `convergence_signal`, `source_origin`, `tracy_row_ref` per source entry ONLY when the directive row used the retrieval-shape path. Legacy directives emit v1.0 shape with none of these fields (backwards-compatible — consumers reading v1.1 see `null` / `[]` / `false` defaults).

   **(b) Documentation layering (Paige MUST-FIX #3 — single source of truth with pointers)**:
   - **Primary home**: `extraction-report-schema.md` gains a new H2 section `## Provider Metadata Sub-objects` (inserted after the `provider_metadata` field is first referenced) containing the FULL `provider_metadata.scite` field schema — all AC-B.2 fields with types, nullability, value ranges, and worked examples. This is the authoritative schema.
   - **Pointer-only home**: `retrieval-contract.md` "For Tracy" section gets a 10-15 line pointer subsection — "scite adapter returns these signals; see [extraction-report-schema.md#provider-metadata-sub-objects](./extraction-report-schema.md#provider-metadata-sub-objects) for the full schema." NO duplicate schema table.
   - **Rationale**: future field drift in two places = divergence risk. Single-source-of-truth via extraction-report-schema.md; retrieval-contract.md stays audience-facing pointer.

   **AC-C.4 scope delta**: +30 lines to `extraction-report-schema.md` (primary schema), +15 lines to `retrieval-contract.md` "For Tracy" (pointer + signal summary) — superseded by AC-C.4' below which also absorbs Paige MUST-FIX #1.

4'. **AC-C.4' — "Authoring retrieval-shape directives directly" operator-facing subsection (Paige MUST-FIX #1).** `retrieval-contract.md` "For operators" section currently ends with the legacy-directive transform explanation ("nothing changes about the directive shapes you already use"). That statement becomes misleading the instant 27-2 ships, because operators CAN now author retrieval-shape directives directly. Add a new subsection (~25 lines) immediately after the legacy-transform block:

   ```markdown
   ### Authoring retrieval-shape directives directly (advanced)

   Most operators never write these; Tracy (Epic 28) emits them. But retrieval-shape
   directives are authorable by hand for testing or specialized workflows. The shape:

   ```yaml
   sources:
     - intent: "peer-reviewed studies on sleep hygiene since 2020"
       provider_hints:
         - {provider: "scite", params: {mode: "search"}}
       acceptance_criteria:
         mechanical: {date_range: ["2020-01-01", "2026-12-31"], min_results: 5}
         provider_scored: {authority_tier_min: "peer-reviewed"}
       iteration_budget: 3
       convergence_required: true
       cross_validate: false
   ```

   Field reference: see §For Tracy above. Cross-validation (multi-provider fan-out)
   requires multiple provider_hints entries and cross_validate: true.
   ```

   **Rationale**: without this, AC-B.6 ships an operator-facing feature without a doc surface (Paige green-light blocker). Scope delta: +25 lines to `retrieval-contract.md` "For operators."

   **Combined scope for retrieval-contract.md**: +40 lines total (AC-C.4' subsection + AC-C.4(b) pointer subsection).

5. **AC-C.5 — Dispatcher public surface unchanged.** No new arg to `dispatcher.dispatch()`; SciteProvider factory-resolves via `provider_directory.get_registered_adapter_class("scite")`. Tests that inject adapters via `AdapterFactory(overrides={...})` pattern remain valid.

6. **AC-C.6 — Legacy directive regression must be byte-identical.** AC-T.6 proves legacy DOCX directive output is unchanged after dispatcher-wiring lands. If byte-identical cannot hold due to log-line formatting changes, a one-line deviation is permitted IFF it is intentional (document in test + Review Record). Silent drift fails the story.

7. **AC-C.7 — No LLM-in-the-loop for query formulation or refinement.** scite-specific strategies are lookup-table code, not inference (per 27-0 AC-C.6). If a "semantic expansion" need surfaces, defer to a follow-on story with its own eval framework.

8. **AC-C.8 — `identity_key` never returns empty string or None.** Raises `NotImplementedError` when none of DOI / scite_paper_id / source_id is available — the dispatcher's cross-validation preflight catches this at dispatch-time (per 27-0 anti-pattern #10).

9. **AC-C.9 — Dev-guide content ownership + Extension Guide placement (Paige MUST-FIX #2).** Paige drives structure, prose, and audience cues; Amelia countersigns technical accuracy on code snippets + ABC method signatures. Three surfaces, ALL required:

   **(a) Sharded how-to file**: `docs/dev-guide/how-to-add-a-retrieval-provider.md` (~180 lines) — primary content lives here. SciteProvider as worked example. Sections:
     - "Understanding your provider's API surface" (PDG-2 resolution pattern for future provider authors)
     - "Subclassing RetrievalAdapter" (the 7 abstract methods, with SciteProvider snippets)
     - "Declaring PROVIDER_INFO for directory auto-registration"
     - "Parametrizing test_retrieval_adapter_base.py" (explicit inheritance target, no reimplementation)
     - "Refinement strategy: when `drop_filters_in_order` is enough, when to add custom"
     - "Anti-patterns" (lookup tables over inference, refinement monotonicity, no locator-shape refactor — the AC-B.6 carve-out from §Anti-pattern Guardrails).

   **(b) Recipe-4 stub under §Extension Guide of main `docs/dev-guide.md`**: `docs/dev-guide.md`'s "Extension Guide: Adding New Capabilities" section already carries three sibling Recipes (API Client / Skill / Agent). Add a fourth — Recipe 4: Adding a Retrieval Provider (Texas) — as a 4-8 line stub with a 2-sentence scope summary pointing at the sharded file. Fresh developers scan the Extension Guide recipes, not Texas-specific subsections (Paige).

   **(c) Table-of-Contents entry in main `docs/dev-guide.md`** (line 20 area) pointing at the new Recipe-4 anchor.

   **Do NOT** rely on a single one-liner link under a Texas-specific subsection — that fails the "fresh developer lands in wrong file" heuristic. Scope delta: `docs/dev-guide.md` +8 lines (ToC + Recipe-4 stub), sharded file +180 lines.

10. **AC-C.10 — No new top-level CLI flag.** SciteProvider is invoked via the existing directive-load → dispatcher path. No `--scite` / `--use-scite` flag. The `--list-providers` CLI from 27-0 will show scite as `status="ready"` automatically.

11. **AC-C.11 — Writer-discriminant contract (Winston MUST-FIX #1).** `run_wrangler.py::write_extraction_report(sources, *, code_path: Literal["retrieval", "locator"])` takes an explicit `code_path` discriminant argument. The writer:
    - On `code_path="retrieval"`: emits `schema_version: "1.1"` and populates the 6 v1.1 additive fields per `TexasRow`. If any row lacks the v1.1 shape (e.g., caller accidentally passed a legacy SourceOutcome), raise `ValueError("write_extraction_report received non-retrieval row on retrieval code path: {row!r}")`. No silent default-filling.
    - On `code_path="locator"`: emits `schema_version: "1.0"` and DOES NOT populate any v1.1 field. If any row carries v1.1-only fields populated (e.g., `retrieval_intent` non-null), raise `ValueError("write_extraction_report received retrieval-shape row on locator code path: {row!r}")`. Dual-emit becomes dual-drift without this guard.
    - Contract test: `test_write_extraction_report_rejects_mismatched_code_path` in `tests/test_run_wrangler_retrieval_shape.py` — two explicit cases, each asserts `ValueError` with correct message prefix.

    **Rationale**: without the discriminant, a future contributor could pass the wrong path and silently produce a malformed v1.1 row (missing retrieval_intent) or a leaky v1.0 row (with retrieval_intent populated but schema_version="1.0"). The raise-on-mismatch pattern is the contract teeth.

## File Impact

| File | Change | Lines (est.) |
|------|--------|-------|
| [`skills/bmad-agent-texas/scripts/retrieval/scite_provider.py`](../../skills/bmad-agent-texas/scripts/retrieval/scite_provider.py) | **New** — `SciteProvider(RetrievalAdapter)` + `PROVIDER_INFO` + authority-tier lookup data + `_build_query_search` / `_build_query_paper` helpers | +220 |
| [`skills/bmad-agent-texas/scripts/retrieval/refinement_registry.py`](../../skills/bmad-agent-texas/scripts/retrieval/refinement_registry.py) | **Touch** — iff PDG-3 path B: register scite-specific strategies (`authority_tier_relaxation`, `date_range_broaden`, `supporting_citation_floor_drop`) | +60 (conditional) |
| [`skills/bmad-agent-texas/scripts/run_wrangler.py`](../../skills/bmad-agent-texas/scripts/run_wrangler.py) | **Touch** — directive-load shape branching (intent vs locator); dispatcher integration for retrieval-shape path; dual-emit schema_version; malformed-shape exit-30 | +100 |
| [`skills/bmad-agent-texas/references/retrieval-contract.md`](../../skills/bmad-agent-texas/references/retrieval-contract.md) | **Touch** — scite-specific section under "For Tracy" + "For operators" (provider_metadata.scite field documentation) | +50 |
| [`skills/bmad-agent-texas/references/extraction-report-schema.md`](../../skills/bmad-agent-texas/references/extraction-report-schema.md) | **Touch** — `provider_metadata.scite` sub-object schema with all AC-B.2 fields documented | +30 |
| [`skills/bmad-agent-texas/scripts/retrieval/provider_directory.py`](../../skills/bmad-agent-texas/scripts/retrieval/provider_directory.py) | **Touch** — no code change required (supersession is via `__init_subclass__`); comment update noting scite is now live | +5 |
| [`docs/dev-guide/how-to-add-a-retrieval-provider.md`](../../docs/dev-guide/how-to-add-a-retrieval-provider.md) | **New** — Paige+Amelia co-authored; worked example = SciteProvider | +180 |
| [`docs/dev-guide.md`](../../docs/dev-guide.md) | **Touch** — one-liner link to new sharded how-to-add-a-provider doc under Texas retrieval section | +3 |
| [`tests/test_retrieval_scite_provider.py`](../../tests/test_retrieval_scite_provider.py) | **New** — AC-T.1 (11 atomic unit tests post-split) + AC-T.3 (2 refine tests) + AC-T.10 (1 module-prefix contract) + AC-T.11 (1 no-stateful-mock guard) | +380 |
| [`tests/contracts/test_retrieval_adapter_base.py`](../../tests/contracts/test_retrieval_adapter_base.py) | **Touch** — extend parametrization to include SciteProvider (AC-T.2) | +20 |
| [`tests/test_retrieval_dispatcher.py`](../../tests/test_retrieval_dispatcher.py) | **Touch** — 1 scite-via-MCPClient dispatch integration test (AC-T.4) | +40 |
| [`tests/test_run_wrangler_retrieval_shape.py`](../../tests/test_run_wrangler_retrieval_shape.py) | **New** — 3 dispatcher-wiring tests (AC-T.5) | +150 |
| [`tests/test_run_wrangler_legacy_docx_parity.py`](../../tests/test_run_wrangler_legacy_docx_parity.py) | **New** — 2 log-stream + exception parity tests (AC-T.6) | +120 |
| [`tests/contracts/test_extraction_report_schema_compliance.py`](../../tests/contracts/test_extraction_report_schema_compliance.py) | **New** — parametrized schema-compliance (AC-T.7) | +80 |
| [`tests/fixtures/retrieval/scite/`](../../tests/fixtures/retrieval/scite/) | **New** — 7 JSON fixtures (search_happy, paper_metadata_happy, paper_metadata_paywalled, citation_context_happy, empty_search, auth_failure_401, rate_limit_429) | ~7 files, +250 lines JSON |

**No changes to:** `retrieval/base.py` (ABC stable from 27-0), `retrieval/contracts.py` (schema v1.1 frozen), `retrieval/dispatcher.py` (public surface stable), `retrieval/mcp_client.py` (Option Y surface stable), `retrieval/fake_provider.py` (reference adapter stays), `retrieval/normalize.py` (canonical helpers stable), `tests/contracts/test_acceptance_criteria_schema_stable.py` (schema-pin passes unchanged — no schema mutation), `tests/test_retrieval_mcp_client.py` (MCP client tests stable), `transform-registry.md` (locator-shape doc; scite is retrieval-shape and lives in `retrieval-contract.md` + `provider_directory`), `.env.example` (still blocked by repo policy; discovery via `--list-providers`), `pyproject.toml` / `requirements.txt` (`responses` already added in 27-0).

## Tasks / Subtasks

**Task order (Amelia MUST-FIX #3 — skeleton-first wiring validation):** T1 skeleton → **T8 wiring** → T2-T7 guts. Rationale: wiring-first catches dual-emit + shape-detector + discriminant bugs before scite specifics pile on; SciteProvider skeleton (empty `execute` returning `[]`) is enough to prove the wiring routes correctly.

- [x] **T-Pre — Pre-Development Gate resolved at green-light round 1 (2026-04-18).** PDG-1 = path B (synthetic-only); PDG-2 = path B (inferred catalog); PDG-3 = path A (`drop_filters_in_order` only). Full resolution recorded in §Pre-Development Gate and §Green-Light Patches Applied. Follow-on tickets `27-2-live-cassette-refresh` + `27-2-refinement-hardening` committed.
- [ ] **T1 — SciteProvider skeleton + PROVIDER_INFO** (AC-B.1, AC-C.1, AC-C.3)
  - [ ] Create `scite_provider.py`; subclass `RetrievalAdapter`.
  - [ ] Declare `PROVIDER_INFO: ClassVar[ProviderInfo]` with `id="scite"`, `status="ready"`, auth env vars, capabilities, spec_ref.
  - [ ] Stub-implement all 7 abstract methods with trivial bodies (e.g., `execute` returns `[]`, `normalize` returns `[]`, `formulate_query` returns `{}`, `identity_key` raises `NotImplementedError` for now). This is ENOUGH to prove dispatcher factory-resolution + supersession; real bodies land T2-T7.
  - [ ] Smoke test: import module, verify `list_providers(shape="retrieval")` now shows `scite: ready` (superseded placeholder). Also export `SCITE_MCP_URL` constant for AC-T.10 use.
- [ ] **T8 — run_wrangler.py dispatcher-wiring cascade (WIRING-FIRST per Amelia MF-3)** (AC-B.6, AC-C.4(a), AC-C.11)
  - [ ] Add `_classify_directive_shape(src: dict) -> Literal["retrieval", "locator", "malformed"]` helper (per AC-B.6 signature).
  - [ ] Retrieval-shape branch: construct `RetrievalIntent` + call `dispatcher.dispatch()`; route results to `write_extraction_report(sources, code_path="retrieval")`.
  - [ ] Legacy-shape branch: existing `_fetch_source` path unchanged; route results to `write_extraction_report(sources, code_path="locator")`.
  - [ ] `write_extraction_report` refactor: accept `code_path` discriminant; raise `ValueError` on mismatched field sets per AC-C.11.
  - [ ] Writer dual-emit: `schema_version = "1.1"` on retrieval-shape path, `"1.0"` on legacy path (determined by `code_path` argument, NOT a flag).
  - [ ] Retrieval-shape schema fields (retrieval_intent, provider_hints, cross_validate, convergence_signal, source_origin, tracy_row_ref) populated on retrieval-shape output rows.
  - [ ] Malformed-shape exit 30 with clear error per suggested prose in AC-B.6.
  - [ ] **Dev checkpoint**: at this point, T1's stub SciteProvider is enough to prove the retrieval-shape path routes correctly (output will show empty rows but `schema_version: "1.1"` + populated `retrieval_intent`). If dual-emit or discriminant bug surfaces, it surfaces HERE before T2-T7 scite specifics pile on.
- [ ] **T2 — Authority-tier lookup table + identity_key** (AC-B.2, AC-C.8)
  - [ ] Module-level constant `SCITE_AUTHORITY_TIERS: dict[str, str]` mapping scite venue-type → canonical tier (`peer-reviewed` / `preprint` / `web`).
  - [ ] `identity_key` implementation with 3-tier fallback (DOI → scite_paper_id → source_id → `NotImplementedError`).
- [ ] **T3 — formulate_query + query-mode helpers** (AC-B.2, AC-T.1)
  - [ ] `formulate_query` inspects `intent.kind` + `provider_hints[scite].params["mode"]` to pick search / paper / citation-contexts shape.
  - [ ] Helper `_build_query_search(intent, params)` → dict with keys per scite MCP tool signature (inferred from scite.ai/api-docs per PDG-2 path B; `tests/fixtures/retrieval/scite/README.md` documents the source-of-truth).
  - [ ] Helper `_build_query_paper(intent, params)` → dict for DOI-direct paper fetch.
  - [ ] Determinism guard: no dict iteration order reliance, no `random`, no `datetime.now()`.
- [ ] **T4 — execute via MCPClient** (AC-B.2, AC-B.5, AC-C.2)
  - [ ] Lazy MCPClient instantiation inside `execute` (not at `__init__`) with `MCPServerConfig(url=<scite_mcp_url>, auth_env=["SCITE_USER_NAME", "SCITE_PASSWORD"], auth_style="basic")`.
  - [ ] Dispatch `call_tool` per query mode.
  - [ ] Let MCPClient exceptions propagate unchanged (dispatcher wraps). Verify via AC-T.10 module-prefix contract test.
- [ ] **T5 — apply_mechanical + apply_provider_scored + declare_honored_criteria** (AC-B.2, AC-B.3)
  - [ ] Mechanical filters: `date_range`, `exclude_ids`, `license_allow`, `min_results` (passthrough).
  - [ ] Provider-scored filters: `authority_tier_min`, `supporting_citations_min`, `cited_by_count_min`.
  - [ ] `declare_honored_criteria` returns explicit frozenset (NOT the default empty set).
- [ ] **T6 — normalize → TexasRow with provider_metadata.scite** (AC-B.2, AC-B.4)
  - [ ] Scite paper → `TexasRow` with all AC-B.2 fields populated under `provider_metadata.scite`.
  - [ ] Paywall degradation: `full_text_available: false` → body = abstract only; `known_losses` sentinel.
  - [ ] Authority tier derivation: scite venue-type → lookup table → `row.authority_tier`.
  - [ ] Citation context: top-3 per classification (supporting / contradicting / mentioning).
- [ ] **T7 — refine + refinement registry** (AC-B.2, PDG-3 path A)
  - [ ] Call `refinement_registry.get_strategy("drop_filters_in_order")` with scite-specific order list: `["supporting_citations_min", "authority_tier_min", "date_range", "cited_by_count_min"]`.
  - [ ] Return `None` when all filter keys exhausted (iteration bound).
  - [ ] Custom strategies DEFERRED to `27-2-refinement-hardening` follow-on per PDG-3 resolution.
- [ ] **T9 — Synthetic fixtures + SciteProvider unit tests** (AC-T.1)
  - [ ] Author JSON fixtures under `tests/fixtures/retrieval/scite/` matching scite MCP tool shapes (per PDG-2 resolution).
  - [ ] Implement 11 atomic unit tests (atomicity-split per AC-T.1) in `test_retrieval_scite_provider.py` using `responses.RequestsMock()` **per-test** context manager preloaded with fixtures. Also: AC-T.10 module-prefix exception contract test (1) + AC-T.11 no-stateful-mock anti-pattern guard (1).
- [ ] **T10 — Parametrize ABC-contract tests over SciteProvider** (AC-T.2)
  - [ ] Extend `tests/contracts/test_retrieval_adapter_base.py` parametrization to include SciteProvider alongside FakeProvider.
  - [ ] NO test-body reimplementation; parametrize via `@pytest.mark.parametrize("adapter_class", [FakeProvider, SciteProvider])`.
- [ ] **T11 — Refinement tests** (AC-T.3)
  - [ ] Monotonic-looseness test: N iterations produce strictly-looser queries.
  - [ ] Exhaustion test: after all filters dropped, `refine` returns `None`.
  - [ ] PDG-3 path B: scite-specific strategy tests.
- [ ] **T12 — Dispatcher integration smoke** (AC-T.4)
  - [ ] Add 1 test to `tests/test_retrieval_dispatcher.py` exercising `dispatch(scite_intent)` with `responses`-mocked MCP.
- [ ] **T13 — run_wrangler dispatcher-wiring tests** (AC-T.5)
  - [ ] Create `test_run_wrangler_retrieval_shape.py` with 3 tests (retrieval-shape routing, legacy preservation, malformed exit-30).
- [ ] **T14 — Legacy DOCX byte-identical regression** (AC-T.6, AC-T.7-cascade)
  - [ ] Create `test_run_wrangler_legacy_docx_parity.py` with log-stream parity + malformed-DOCX exception-class parity tests.
- [ ] **T15 — Parametrized schema-compliance test** (AC-T.7, deferred-cascade)
  - [ ] Create `tests/contracts/test_extraction_report_schema_compliance.py` with `@pytest.mark.parametrize("version", ["1.0", "1.1"])`.
- [ ] **T16 — `docs/dev-guide.md` how-to-add-a-provider section** (AC-B.7, AC-C.9)
  - [ ] Paige drafts; Amelia countersigns technical accuracy.
  - [ ] SciteProvider as worked example.
  - [ ] New sharded file `docs/dev-guide/how-to-add-a-retrieval-provider.md`; main `docs/dev-guide.md` gets one-liner link.
- [ ] **T17 — retrieval-contract.md + extraction-report-schema.md updates** (AC-B.2, AC-C.4)
  - [ ] Add scite-specific subsection to `retrieval-contract.md` "For Tracy" + "For operators" sections.
  - [ ] Document `provider_metadata.scite` sub-object fields in `extraction-report-schema.md`.
- [ ] **T18 — Regression + pre-commit + lockstep verification**
  - [ ] Full pytest green — expected **1106 + N collecting** (refine at green-light).
  - [ ] Pre-commit hooks green (ruff + orphan + co-commit).
  - [ ] `pytest -m trial_critical` unchanged (scite not trial-critical).
  - [ ] `test_provider_directory_autoregister.py` automatically covers SciteProvider — verify green.
- [ ] **T19 — Party-mode implementation review + bmad-code-review + closure**
  - [ ] Party-mode implementation review (Winston + Amelia + Murat + Paige).
  - [ ] `bmad-code-review` layered pass (Blind Hunter + Edge Case Hunter + Acceptance Auditor); MUST-FIX remediated; SHOULD-FIX triaged.
  - [ ] Flip sprint-status 27-2 → `done` with closure comment.
  - [ ] Epic 27 roster update (epic file + bmm-workflow-status.yaml).
  - [ ] Epic 28 roster update — 28-1 hard-dependency on 27-2 now satisfied.
  - [ ] 27-2.5 Consensus unblock confirmation (soft-block on 27-2 for cross-val demo).

## Dev Notes

### Architecture guardrails (from 27-0 foundation + deferred cascade)

- **scite is a `RetrievalAdapter` subclass, NOT a standalone `SciteClient`.** The pre-reshape file's `scripts/providers/scite_client.py` path is obsolete. scite lives in the `retrieval/` package alongside `fake_provider.py`. `MCPClient` supplies HTTP; SciteProvider supplies the provider-DSL translation.
- **`MCPClient` public surface MUST remain library-agnostic.** No `requests.Response` types in SciteProvider signatures. No library-specific exceptions re-exported. The Option-X migration escape hatch (when `mcp` PyPI hits 1.0) is a single-file swap IF this discipline holds. Regressing this regresses 27-0's AC-C.9.
- **Locator-shape providers stay on legacy path.** Anti-pattern #3 from 27-0 prohibits refactoring DOCX / PDF / Notion / Box / Playwright to use `RetrievalIntent` directly. The dispatcher-wiring cascade (AC-B.6) routes retrieval-shape directives through the dispatcher; locator-shape directives preserve existing `_fetch_source` path. Dual-emit `schema_version` is the observable boundary between paths.
- **Deterministic query formulation only.** scite-specific query building is code + data (venue-type tables, filter-key ordering), not inference. LLM-driven query expansion is explicitly non-goal.
- **Refinement is monotonically-loosening.** Each `refine()` call drops a filter or widens a range — never tightens. The iteration counter lives in the query itself (FakeProvider pattern) or in an internal cursor; either works as long as `refine()` is pure.
- **Cross-validation is 27-2.5's job, not 27-2's.** SciteProvider provides `identity_key` (DOI-primary) to unblock cross-validation; 27-2.5 Consensus will be the first real `cross_validate: true` exercise with scite + Consensus fan-out.
- **scite's smart-citation classification is scite-opinion, not ground truth.** The `supporting_count` / `contradicting_count` / `mentioning_count` fields are populated as reported by scite. Downstream (Tracy's semantic pass, Vera's fidelity check) may re-evaluate or override. `provider_metadata.scite` is an opaque sub-object for this reason — per-provider fields do not pollute the top-level `TexasRow` schema.

### Source tree (new + touched)

```
skills/bmad-agent-texas/
├── scripts/
│   ├── retrieval/
│   │   ├── scite_provider.py                    [NEW] +220  SciteProvider(RetrievalAdapter) + helpers
│   │   ├── refinement_registry.py               [TOUCH] +60 (conditional on PDG-3 path B)
│   │   └── provider_directory.py                [TOUCH] +5   comment update (supersession via __init_subclass__)
│   └── run_wrangler.py                          [TOUCH] +100 directive-shape branching + dispatcher-wiring + dual-emit
└── references/
    ├── retrieval-contract.md                    [TOUCH] +50  scite-specific sections
    └── extraction-report-schema.md              [TOUCH] +30  provider_metadata.scite sub-object schema

docs/
├── dev-guide.md                                 [TOUCH] +3   link to new sharded file
└── dev-guide/
    └── how-to-add-a-retrieval-provider.md       [NEW] +180  Paige+Amelia co-authored

tests/
├── test_retrieval_scite_provider.py             [NEW] +380  AC-T.1 (11 atomic unit) + AC-T.3 (2 refine) + AC-T.10 (1 module-prefix) + AC-T.11 (1 no-mock guard)
├── test_retrieval_dispatcher.py                 [TOUCH] +40 AC-T.4 scite dispatch integration
├── test_run_wrangler_retrieval_shape.py         [NEW] +150  AC-T.5 (3 dispatcher-wiring tests)
├── test_run_wrangler_legacy_docx_parity.py      [NEW] +120  AC-T.6 (log-stream + exception parity)
├── contracts/
│   ├── test_retrieval_adapter_base.py           [TOUCH] +20 AC-T.2 parametrization over SciteProvider
│   └── test_extraction_report_schema_compliance.py  [NEW] +80  AC-T.7 parametrized v1.0/v1.1
└── fixtures/retrieval/scite/                    [NEW] 7 JSON files, +250 lines
    ├── search_happy.json
    ├── paper_metadata_happy.json
    ├── paper_metadata_paywalled.json
    ├── citation_context_happy.json
    ├── empty_search.json
    ├── auth_failure_401.json
    └── rate_limit_429.json
```

### Previous-story intelligence (from 27-0 closeout, 2026-04-18)

27-0 established patterns 27-2 MUST inherit:

- **Adapter subclass pattern** — `FakeProvider` in `retrieval/fake_provider.py` is the living reference. Subclass `RetrievalAdapter`; declare `PROVIDER_INFO` ClassVar; implement 7 abstract methods; `__init_subclass__` auto-registers. SciteProvider follows the identical shape.
- **Deterministic query formulation** — `FakeProvider.formulate_query` returns `f"initial:{intent.intent}"`. SciteProvider builds a dict with scite MCP tool args; same determinism requirement (AC-T.2 self-test at 100 invocations).
- **Refinement as pure function of previous query** — `FakeProvider.refine` encodes iteration counter in the query string. SciteProvider uses `refinement_registry.drop_filters_in_order` which takes `(current_mechanical, original, iteration)` — same pattern.
- **`MCPClient` per-server config + lazy auth** — 27-0's `MCPClient` resolves env vars at first `call_tool`, not at `__init__`. SciteProvider does NOT bypass this — do not eagerly call `os.environ.get("SCITE_USER_NAME")` at module load.
- **`responses` library for HTTP mocking** — 27-0 added `responses>=0.25,<1` to dev deps. Unit tests register URL patterns + response JSON at setup; fail loudly on unexpected calls (good — that means the client is hitting the wrong endpoint).
- **Fixture hygiene** — JSON fixtures under `tests/fixtures/retrieval/<provider>/` as plain text, diff-friendly, not binary. scite's follow exactly. 27-0's fakes at `tests/fixtures/retrieval/fake-responses/` show the shape.
- **Test-helper re-use** — `tests/_helpers/mcp_fixtures.py` provides `jsonrpc_response(result=...)` / `jsonrpc_error(code=..., message=...)` envelope builders. scite tests wrap responses via these — do not re-invent JSON-RPC envelopes.
- **Deterministic sequence fixtures for dispatcher iteration tests** — 27-0's `test_retrieval_dispatcher.py` pre-scripts provider responses as lists, NOT stateful mocks. scite's dispatcher-integration test follows the same doctrine (with `responses` doing the HTTP-layer mocking).
- **Module-qualified exception classification** — if SciteProvider raises an exception, `type(exc).__module__.startswith("retrieval.scite_provider")` is the pattern for downstream classifiers (mirrors 27-1's `docx.` prefix check).
- **Co-commit test + impl** — tests land in the same commit slice as source. Pre-commit hook enforces.
- **Ruff + orphan + co-commit pre-commit hooks green before review** — no exceptions.
- **No `trial_critical` marker** — scite dispatch isn't a pre-Prompt-1 trial gate.
- **Review-record structure** — match 27-1 / 27-0 template: MUST-FIX remediated with `[x] [Review][Patch]`; SHOULD-FIX remediated or deferred with `[x] [Review][Defer]`; NITs logged to `_bmad-output/maps/deferred-work.md`; Blind Hunter / Edge Case Hunter / Acceptance Auditor layer breakdown.

### Testing standards

- **Unit / contract / integration split:**
  - Unit: `tests/test_retrieval_scite_provider.py` (SciteProvider methods + determinism).
  - Contract: parametrization of `tests/contracts/test_retrieval_adapter_base.py` + new `tests/contracts/test_extraction_report_schema_compliance.py`.
  - Integration: `tests/test_retrieval_dispatcher.py` extension + new `test_run_wrangler_retrieval_shape.py` + new `test_run_wrangler_legacy_docx_parity.py`.
- **HTTP mocking via `responses` library** — no real network; no live_api; no cassettes-recording-against-real-MCP.
- **Deterministic sequence fixtures for dispatcher tests** — no stateful mocks.
- **No `live_api`, no `trial_critical`, no `xfail`, no `skip`** added to default suite.
- **Fixture hygiene** — plain-text JSON; diff-friendly; not binary.
- **Per `feedback_regression_proof_tests.md`**: no xfail, no skip, classify every failure (update/restore/delete), measure coverage. If the dispatcher-wiring cascade breaks existing 27-1 DOCX tests, classify each failure explicitly in §Review Record — don't mass-update.

### References

- **27-0 foundation spec**: [27-0-retrieval-foundation.md](./27-0-retrieval-foundation.md) — contract source of truth; §Anti-patterns has the 10-item disciplinary list; §Green-Light Patches Applied has the AC-C.9 / AC-C.10 / AC-C.11 library-agnostic / provider_hints / dumbness clauses.
- **Retrieval contract (audience-segmented)**: [retrieval-contract.md](../../skills/bmad-agent-texas/references/retrieval-contract.md) — "For dev-agents" section has the subclass template.
- **Schema changelog**: [SCHEMA_CHANGELOG.md](./SCHEMA_CHANGELOG.md) — v1.1 additive fields with migration notes.
- **Base ABC**: [retrieval/base.py](../../skills/bmad-agent-texas/scripts/retrieval/base.py) — the 7 abstract methods SciteProvider implements.
- **Contracts**: [retrieval/contracts.py](../../skills/bmad-agent-texas/scripts/retrieval/contracts.py) — Pydantic models (RetrievalIntent, TexasRow, ProviderInfo, etc.).
- **MCP client**: [retrieval/mcp_client.py](../../skills/bmad-agent-texas/scripts/retrieval/mcp_client.py) — Option Y JSON-RPC; library-agnostic public surface.
- **FakeProvider (reference impl)**: [retrieval/fake_provider.py](../../skills/bmad-agent-texas/scripts/retrieval/fake_provider.py) — pattern template for SciteProvider.
- **Provider directory**: [retrieval/provider_directory.py](../../skills/bmad-agent-texas/scripts/retrieval/provider_directory.py) — scite placeholder at line 156-164.
- **Refinement registry**: [retrieval/refinement_registry.py](../../skills/bmad-agent-texas/scripts/retrieval/refinement_registry.py) — `drop_filters_in_order` default strategy.
- **Dispatcher**: [retrieval/dispatcher.py](../../skills/bmad-agent-texas/scripts/retrieval/dispatcher.py) — single-provider + cross-validation paths; scite integrates as factory-resolved adapter.
- **27-0 ABC contract tests (parametrization target)**: [tests/contracts/test_retrieval_adapter_base.py](../../tests/contracts/test_retrieval_adapter_base.py) — explicit inheritance target per 27-0 AC-T.2 mandate.
- **Previous DOCX story (pattern source)**: [27-1-docx-provider-wiring.md](./27-1-docx-provider-wiring.md) — dispatch-extension, module-loader, co-commit discipline patterns.
- **27-0 deferred-cascade context**: [27-0-retrieval-foundation.md](./27-0-retrieval-foundation.md)§Review Record — rationale for DISMISSED findings absorbed into 27-2 scope.
- **NITs deferred from 27-0**: [_bmad-output/maps/deferred-work.md](../maps/deferred-work.md) — ~22 items; 27-2 may batch-absorb a subset when touching related code (e.g., MCPConfigError taxonomy when wiring scite auth if auth shape surfaces a new error class).
- **Epic 27 roster**: [epic-27-texas-intake-expansion.md](./epic-27-texas-intake-expansion.md) — shape classification + AC-S spine.
- **Tracy's consuming spec (downstream)**: [28-1-tracy-pilot-scite-ai.md](./28-1-tracy-pilot-scite-ai.md) — reshape pending 27-2 + 27-0 closure; Tracy emits `RetrievalIntent` contract which routes through 27-2's adapter.
- **scite.ai public API docs**: `scite.ai/api-docs` (operator-accessible; LLM agent cannot navigate directly — operator captures during PDG-2 resolution).

### Non-goals

- **Tracy's agent-side editorial code** — fit-score algorithm, authority-tier editorial classification, editorial_note generation (Epic 28 scope).
- **Live-API cassette recording against real scite MCP** — follow-on "27-2-live-cassette-refresh" story triggered if PDG-2 path B is chosen and live verification becomes possible post-auth-acquisition.
- **Cross-validation with Consensus** — 27-2.5 scope (scite + Consensus fan-out is 27-2.5's `cross_validate: true` test).
- **scite MCP webhook / notification support** — not needed for pull-style fetching.
- **Multi-tenant API-token handling** — single operator, single credential pair.
- **Generic scholarly-search provider abstraction** — 27-2 is scite-specific. Future PubMed / Semantic Scholar / OpenAlex are each their own story per the one-provider-per-story pattern.
- **Adaptive rate-limit backoff** — basic 429-surfacing via `MCPRateLimitError` is in scope; adaptive backoff is future hardening.
- **Semantic evaluation in Texas** — `acceptance_criteria.semantic_deferred` surfaces unchanged to Tracy's post-fetch pass (27-0 AC-C.8).
- **Locator-shape provider refactoring** — anti-pattern #3 from 27-0 prohibits; deferred cascade respects this.
- **LLM-in-the-loop query expansion or refinement** — deferred to future story with own eval framework (27-0 AC-C.6).

## Test Plan

| Test | AC | Level | Mocked? | Blocking at merge? |
|------|----|-------|---------|---------------------|
| AC-T.1 × 11 SciteProvider unit atoms (atomicity-split) | B.1, B.2, B.4, B.5 | Unit | `responses` (per-test) | Yes |
| AC-T.2 × ≥5 parametrized ABC-contract tests + scaffold refactor | B.1-B.3 | Contract | N/A | Yes |
| AC-T.3 × ≥2 refinement tests | B.2 (refine) | Unit | N/A | Yes |
| AC-T.4 × 1 dispatcher-scite integration test | B.6, C.5 | Integration | `responses` | Yes |
| AC-T.5 × 3 run_wrangler dispatcher-wiring tests | B.6 | Integration | fixture | Yes |
| AC-T.6 × 3 legacy DOCX parity (log-stream + exception-class + scrubber self-test) | C.6, cascade | Regression | golden file | **Yes — regression proof** |
| AC-T.7 × 2 parametrized schema-compliance v1.0/v1.1 | C.4, cascade | Contract | N/A | Yes |
| AC-T.8 SciteProvider auto-registration (inherited from 27-0) | C.3 | Contract | N/A | Yes (existing test) |
| AC-T.9 suite-level regression floor ≥31 collecting | — | Suite | N/A | Yes (non-collecting) |
| AC-T.10 × 1 module-prefix exception contract | C.2 | Contract | `responses` | Yes |
| AC-T.11 × 1 no-stateful-mock anti-pattern guard | — | Meta | N/A | Yes |
| AC-C.11-guard × 2 writer-discriminant mismatched-call tests | C.11 | Contract | N/A | Yes |

**Target baseline floor: ≥31 collecting additions** (Murat MUST-FIX #3 pinned floor; atomicity splits put us well above the rough +20-25 estimate). Baseline from 27-0 closeout: 1106 passed / 2 skipped / 0 failed / 2 xfailed. Expected after 27-2: **≥1137 passed** / 2 skipped / 0 failed / 2 xfailed. No new `@pytest.mark.skip`, `xfail`, `live_api`, `trial_critical`.

## Risks

| Risk | Mitigation |
|------|------------|
| **scite MCP tool catalog differs from scite.ai/api-docs REST shape** (fixture fidelity risk) | PDG-2 resolution at green-light: live `list_tools("scite")` ping IF PDG-1 path A; otherwise fixtures authored against scite.ai/api-docs + public MCP docs, with schema-canary follow-on story deferred. First live run is the moment-of-truth; diff between synthetic and live → follow-on hardening. |
| **Dispatcher-wiring cascade (AC-B.6) breaks 27-1 DOCX byte-identical output** | AC-T.6 is the explicit regression proof — log-stream parity + malformed-DOCX exception parity. If these tests fail on the first run, the wiring patch ships incorrectly; iterate on the writer shape until byte-identical holds. |
| **PDG-3 path B expands scope mid-implementation** | Green-light spot-check (Amelia + Kira/Murat) before dev begins. If `drop_filters_in_order` provably inadequate, 2 options: (1) land scite-specific strategies in this story (+~60 LOC, keep 5 pts) OR (2) defer to a 27-2-refinement-hardening follow-on and ship scite with basic loosening. Party picks at green-light. |
| **`responses` library's request-matching is too loose / too strict** (false-positive or false-negative test failures) | Use `responses.matchers.header_matcher` for auth header + URL + query-param matching. Fixture JSON is the single source of truth; one fixture-per-endpoint keeps diffing clean. |
| **SciteProvider auto-registration collides with placeholder** | `register_adapter` raises on ID conflict. Placeholder merge-order (live adapters first) already handles supersession; AC-T.8 existing test verifies. If collision surfaces, trace through `__init_subclass__` firing order. |
| **Paywalled full-text forcing abstract-only degradation** (row quality degrades but not flagged) | AC-B.4 makes `known_losses: ["full_text_paywalled"]` a first-class sentinel; Vera's fidelity check reads this and adjusts `completeness_ratio` via existing downstream logic. |
| **scite's citation classification disagrees with ground truth** | Out of scope — `provider_metadata.scite` is opaque, scite-opinion. Tracy's semantic pass + Vera's fidelity pass can override downstream. This is an architectural constraint, not a 27-2 risk. |
| **Identity-key fallback chain (DOI → paper_id → source_id) produces collisions across scite + Consensus in 27-2.5** | Anti-pattern #10 from 27-0: cross-validation preflight requires both adapters to return comparable identity keys. If Consensus uses a different identity scheme, cross-validation tests will fail at 27-2.5 — handled there. For 27-2 single-provider scope, DOI-primary is sufficient. |
| **`.env` missing SCITE credentials at green-light** | PDG-1 default path B (synthetic-fixtures-only) keeps dev unblocked. Live verification deferred to follow-on story IF operator chooses to acquire credentials mid-Epic-27. Default: proceed without live. |

## Dev Agent Record

### Agent Model Used

_(filled by dev-story at implementation time)_

### Debug Log References

_(filled by dev-story)_

### Completion Notes List

_(filled by dev-story)_

### File List

_(filled by dev-story; expected list matches §File Impact above)_

### Review Record

_(filled by bmad-code-review; template = 27-0 Review Record structure: party-mode implementation review → layered bmad-code-review with Blind Hunter + Edge Case Hunter + Acceptance Auditor breakdown)_

## Green-Light Patches Applied (party-mode round 1, 2026-04-18)

Four-panelist roundtable: Winston (Architect) / Amelia (Dev) / Murat (Test) / Paige (Tech Writer). Unanimous verdict: YELLOW → GREEN after 13 MUST-FIX applied. All MUST-FIX and selected SHOULD-FIX baked into the spec above.

### PDG resolutions (unanimous)

- **PDG-1 (auth credentials): Path B — synthetic-fixture-only.** Rationale: live creds give ~10% fixture-fidelity improvement vs ~40% CI-bleed risk (Murat risk calc). Committed follow-on ticket: `27-2-live-cassette-refresh`.
- **PDG-2 (MCP tool catalog): Path B — inferred from scite.ai/api-docs + public MCP docs.** Consequence of PDG-1=B. Fixture-source provenance captured in `tests/fixtures/retrieval/scite/README.md`.
- **PDG-3 (refinement strategies): Path A — `drop_filters_in_order` only.** Scite-specific key-order list enforces monotonic looseness. Committed follow-on ticket: `27-2-refinement-hardening` (opens only if first live dispatch shows exhaustion clustering).

### MUST-FIX applied (13 items)

**Winston (Architect):**
- **W-1 (AC-C.11)**: writer-discriminant contract — `write_extraction_report(sources, *, code_path: Literal["retrieval", "locator"])` raises on mismatched field sets. Prevents dual-emit → dual-drift.
- **W-2 (AC-T.10)**: module-prefix exception contract test — every SciteProvider-raised exception's `type(exc).__module__.startswith("retrieval.")`; no `requests.*` / `urllib3.*` leakage. Option-X escape-hatch smoke alarm.
- **W-3 (§Anti-pattern Guardrails)**: explicit spec-level carve-out — "dual-emit is UPSTREAM ROUTING, NOT a locator-shape refactor." Permitted vs prohibited actions enumerated for Amelia at dev time. Prevents future contributors from collapsing the two paths.

**Amelia (Dev):**
- **A-1 (AC-T.2)**: `test_retrieval_adapter_base.py` parametrization scaffold refactor written into the spec (+30 LOC, not +20). Factory-per-adapter-class pattern enables `[fake]` + `[scite]` IDs without reimplementing tests.
- **A-2 (AC-T.6)**: golden-file mechanism explicitly pinned — `tests/fixtures/regression/legacy_docx_baseline/` + `_normalize_log_stream` regex scrubber + scrubber self-test. No diff libs; plain string equality.
- **A-3 (§Tasks)**: task order swapped — T1 skeleton → **T8 wiring** → T2-T7 guts. Skeleton-first catches wiring bugs before scite specifics pile on.
- **A-4 (PDG-3 ceiling)**: scope cap ≤2 custom refinement strategies at 5 pts; 3+ → re-estimate to 6 pts. Documented in Pre-Development Gate row.

**Murat (Test):**
- **M-1 (AC-T.6)**: overlaps with A-2 — log-stream parity mechanism pinned via golden-file + regex scrubber. Added 3 atoms (log parity + exception parity + scrubber self-test).
- **M-2 (AC-T.1)**: atomicity splits — 7 tests → 11 atomic tests. One assertion-cluster per test. Split `test_scite_execute_happy_path` into 3 atoms; split `test_scite_normalize_populates_provider_metadata` into 3 atoms.
- **M-3 (AC-T.9)**: test-count floor pinned ≥31 collecting (post-atomicity-splits) — not a range. Floors regress-gate; ranges drift. Expected ≥1137 passed.
- **M-4 (follow-on tickets committed)**: `27-2-live-cassette-refresh` + `27-2-refinement-hardening` tickets recorded in §Pre-Development Gate at green-light time, not "deferred if."

**Paige (Tech Writer):**
- **P-1 (AC-C.4')**: new `retrieval-contract.md` "For operators" subsection — "Authoring retrieval-shape directives directly (advanced)" with worked YAML example. Closes missing-doc-obligation blocker on AC-B.6.
- **P-2 (AC-C.9)**: dev-guide placement enforcement — Recipe-4 stub under §Extension Guide of main `docs/dev-guide.md` + ToC entry + sharded how-to file. All three, not just one.
- **P-3 (AC-C.4(b))**: schema documentation layering — primary schema in `extraction-report-schema.md` under new `## Provider Metadata Sub-objects` H2; `retrieval-contract.md` gets pointer-only. Single source of truth, no duplicate tables.

### SHOULD-FIX applied

- **W-SF-1**: `retrieval/__init__.py` eagerly imports `scite_provider` (belt-and-suspenders on `__init_subclass__` registration — removes import-order dependency). Added to T1 task.
- **P-SF-1**: Historical 382-line block archived to [archive/27-2-scite-pre-reshape-2026-04-17.md](./archive/27-2-scite-pre-reshape-2026-04-17.md); active spec keeps only a ~30-line domain-knowledge extract below. Clarity for next-week readers.
- **A-SF-1**: T16 explicitly creates `docs/dev-guide/` subdirectory (new shard location).
- **A-SF-2**: AC-T.7 file-creation language tightened — "NEW" (not "NEW or extension") — `tests/contracts/test_extraction_report_schema_compliance.py` does not exist today.
- **A-SF-3**: Shape-detector helper `_classify_directive_shape` signature pinned in AC-B.6.
- **P-SF-2**: Marcus `external-specialist-registry.md` gets one-sentence CLI pointer added ("Provider availability is authoritative via `run_wrangler.py --list-providers`"). Surfaces the CLI for Marcus.

### SHOULD-FIX deferred (tracked in deferred-work.md or follow-on scope)

- **M-SF-2**: CI 3x-run flake-detection gate still not wired. Moderate risk for 27-2 (network-mocked paths; `responses` strict matcher reduces); MUST-WIRE at 27-2.5 (cross-validation combinatorial flake surface). Logged.
- **W-SF-2**: `test_list_providers_before_scite_import` regression documenting observed pre-import state. Nice-to-have; deferred.
- **P-SF-3**: AC-C.7 + AC-C.10 three-beat prose expansion for dev-guide Recipe-4 (authoring-time discipline, not AC text). Paige owns at T16.

### Vote record

- 🏗️ Winston: **YELLOW → GREEN** (after W-1, W-2, W-3 applied).
- 💻 Amelia: **YELLOW → GREEN** (after A-1, A-2, A-3, A-4 applied).
- 🧪 Murat: **YELLOW → GREEN** (after M-1, M-2, M-3, M-4 applied).
- 📚 Paige: **YELLOW → GREEN** (after P-1, P-2, P-3 applied).

**Unanimous conditional-GREEN → patches applied → hard GREEN.** Dev-story cleared to start.

## BMAD Closure Criteria

- [ ] Pre-Development Gate resolved (PDG-1/2/3 paths recorded in §Green-Light Patches Applied).
- [ ] All AC-B.1 through AC-B.7 behavioral assertions green in test output.
- [ ] All AC-T.1 through AC-T.8 collecting tests pass; AC-T.9 suite-level regression gate green.
- [ ] All AC-C.1 through AC-C.10 contract-pinning checks satisfied.
- [ ] Full `pytest` green (expected 1126-1131 passed / 2 skipped / 0 failed / 2 xfailed; refine at green-light).
- [ ] Pre-commit hooks pass (ruff + orphan + co-commit) on all changed files.
- [ ] 27-1 DOCX byte-identical regression holds (AC-T.6 green).
- [ ] `list_providers(shape="retrieval", status="ready")` returns SciteProvider's PROVIDER_INFO (AC-T.8 existing test covers).
- [ ] `docs/dev-guide/how-to-add-a-retrieval-provider.md` published with SciteProvider as worked example.
- [ ] `retrieval-contract.md` + `extraction-report-schema.md` updated with scite provider_metadata documentation.
- [ ] `bmad-party-mode` implementation review consensus: approve.
- [ ] `bmad-code-review` layered pass (Blind Hunter + Edge Case Hunter + Acceptance Auditor); MUST-FIX remediated; SHOULD-FIX triaged.
- [ ] `sprint-status.yaml::development_status::27-2-scite-ai-provider` flipped to `done` with closure comment.
- [ ] Epic 27 roster entry updated (epic file + `bmm-workflow-status.yaml`).
- [ ] Epic 28 entry updated — 28-1 hard-dependency on 27-2 now satisfied; Tracy pilot unblocked for spec re-expansion.
- [ ] 27-2.5 Consensus unblock confirmation (soft-block on 27-2 for cross-validation demo).

## Questions for Green-Light Round — RESOLVED (2026-04-18)

All questions answered at green-light round 1. Full resolutions in §Green-Light Patches Applied above.

1. ✅ **PDG-1**: Path B (synthetic-only). No credential dependency on dev-story start.
2. ✅ **PDG-2**: Path B (inferred catalog). Fixture provenance in `tests/fixtures/retrieval/scite/README.md`.
3. ✅ **PDG-3**: Path A (`drop_filters_in_order` only). Custom strategies → `27-2-refinement-hardening` follow-on.
4. ✅ **AC-B.6 shape detection**: `_classify_directive_shape()` helper; directive-row shape detection, NOT a CLI flag.
5. ✅ **Dev-guide sharding**: all three surfaces — sharded file + Recipe-4 stub + ToC entry (Paige MUST-FIX #2).
6. ✅ **AC-T.6 log-stream-parity**: structural parity via golden-file + regex scrubber (Amelia MF-2 / Murat MF-1).
7. ✅ **Points estimate**: 5 pts holds under PDG path-B/B/A. ≤2 custom strategies for 5 pts; 3+ → 6 pts (won't happen under path A).
8. ✅ **NIT absorption**: no — keep scope clean, leave NITs in `deferred-work.md` (unanimous).
9. ✅ **Tracy-approved-resources integration**: confirmed — no `--tracy-approved-resources` flag or interim schema in 27-2 scope. Tracy emits `RetrievalIntent` directly in Epic 28.

---

# Historical Domain Knowledge (pre-reshape extract)

> **Full pre-reshape spec archived at** [archive/27-2-scite-pre-reshape-2026-04-17.md](./archive/27-2-scite-pre-reshape-2026-04-17.md) **(382 lines).** Only the scite-domain-knowledge extract that informed the reshape is preserved inline below per Paige's green-light compression ask. The archived file is the source-of-truth for the pre-reshape AC-B / AC-T / AC-C detail + original ratification party input.

### Scite MCP — canonical domain knowledge (inferred from scite.ai/api-docs + public MCP docs)

- **MCP server endpoint**: `https://mcp.scite.ai` (repo-level `.cursor/mcp.json` + `.mcp.json` entries landed with 27-0).
- **Auth shape**: HTTP Basic — `SCITE_USER_NAME` + `SCITE_PASSWORD` → base64-encoded `Authorization: Basic <token>` header. Matches `MCPClient.auth_style="basic"` default. Env vars document discovery via `run_wrangler.py --list-providers`.
- **Three endpoint families** (exposed as MCP tools; exact tool names confirmed at PDG-2 path B fixture authoring time):
  - **search** — topical query → paper-summary list. Inputs: query string, optional date-range / venue / authority-tier filters. Outputs: list of `{doi, title, year, venue, authors, supporting_count, contradicting_count, mentioning_count}`.
  - **paper metadata** — DOI lookup → full paper record. Inputs: DOI. Outputs: title, authors, year, venue, abstract, full_text (if available), `full_text_available` boolean, `scite_report_url`, `scite_paper_id`.
  - **citation contexts** — DOI → smart-citation classifications. Outputs: list of `{classification: "supporting" | "contradicting" | "mentioning", citing_doi, snippet}`. Top-3 per classification retained in `provider_metadata.scite.citation_context_snippets`.
- **`provider_metadata.scite` sub-object schema** (exhaustive field list — documented authoritatively in `extraction-report-schema.md` per AC-C.4(b) layering):
  - `doi: str | null`, `scite_paper_id: str`, `title: str`, `authors: list[str]`, `year: int | null`, `venue: str | null`, `authority_tier: "peer-reviewed" | "preprint" | "web" | null` (derived from venue via `SCITE_AUTHORITY_TIERS` lookup), `supporting_count: int`, `contradicting_count: int`, `mentioning_count: int`, `citation_context_snippets: list[{classification, citing_doi, snippet}]` (≤3 per classification), `scite_report_url: str`, `known_losses: list[str]` (sentinels like `"full_text_paywalled"`).
- **Paywall graceful degradation semantics**: `full_text_available: false` → `body = abstract`; `provider_metadata.scite.known_losses: ["full_text_paywalled"]`. Vera's downstream `completeness_ratio` logic handles tier downgrade automatically.
- **Authority-tier lookup table** (shipped as `SCITE_AUTHORITY_TIERS` module-level constant in `scite_provider.py`, NOT as inference): scite venue-string → canonical tier. Journals with impact-factor and peer review → `peer-reviewed`; arXiv / bioRxiv / medRxiv / SSRN → `preprint`; everything else → `web`. **Data, not inference** — preserves AC-C.7 "no LLM in the loop" guardrail.
- **Error-taxonomy delegation**: reshape inherits MCPClient's `MCPAuthError` / `MCPRateLimitError` / `MCPFetchError` / `MCPProtocolError` unchanged (pre-reshape's `scite_auth_failed` / `scite_rate_limited` / `scite_not_found` / `scite_fetch_failed` adapter-layer taxonomy retired).
- **Reshape relocations** (what moved OUT of 27-2 scope in the reshape):
  - Atomic-write refactor → Epic 28 spine AC-S2 (Winston ratification 2026-04-17).
  - `--tracy-approved-resources` CLI flag → eliminated; Tracy emits `RetrievalIntent` directly in Epic 28.
  - `tracy-approved-resources-interim.schema.yaml` → not needed (RetrievalIntent IS the contract).
  - `scite_paper` SourceRecord kind → retired; canonical `TexasRow.provider == "scite"` with scite-specific fields under opaque `provider_metadata.scite` sub-object.
