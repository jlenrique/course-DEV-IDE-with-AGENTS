# Deferred Work

- ~~2026-04-02: Build function to save downloaded literal visuals from Gamma into the existing Git site destination. Status: implemented on `dev/storyboarding-feature` with preintegration publish helper, mode-aware fail-closed behavior, URL substitution wiring, and regression/live integration test coverage.~~ **Closed 2026-04-02.**

## Stashed for Story 27-5 (Notion provider) — 2026-04-17

Cursor loads TWO Notion MCP servers in parallel (non-conflicting keys):

**User-scope** `C:\Users\juanl\.cursor\mcp.json` → `"Notion"` → hosted HTTP MCP at `https://mcp.notion.com/mcp`
- Tools: `notion-*` curated surface (~12-14 tools: `notion-search`, `notion-fetch`, `notion-create-pages`, etc.)
- Auth: Notion's hosted flow (typically OAuth / session)
- Designed for agent-UX (Tracy, IDE sessions)

**Project-scope** `.cursor/mcp.json` + `.mcp.json` → `"notion"` → local stdio via `scripts/run_mcp_from_env.cjs notion` → `npx -y @notionhq/notion-mcp-server`
- Tools: `API-*` wrappers (~22 tools: `API-post-search`, `API-retrieve-a-page`, etc.)
- Auth: integration token (`NOTION_API_KEY` in `.env`, mapped to `NOTION_TOKEN`)
- Designed for API-key automation (headless Python, CI)

**For Story 27-5 (Texas Notion adapter, locator-shape)**: use **project-scope stdio version**. Rationale:
1. Token-auth matches `run_mcp_from_env.cjs` pattern already established for canvas-lms, gamma, and this notion entry.
2. Texas runs headless in CI — OAuth-style user-session auth doesn't fit.
3. Granular `API-*` tools map cleanly onto locator-shape dispatch (operator provides Notion page-id → Texas fetches via `API-retrieve-a-page` / `API-get-block-children`).
4. Deterministic for testing — stdio subprocess can be mocked; hosted HTTP requires live auth flow.

**For Tracy's IDE-agent exploratory research (Epic 28)**: user-scope hosted version is better. Curated `notion-*` tools are designed for agent reasoning; OAuth session matches Cursor's session auth; fewer tools = less prompt bloat.

**Recommendation**: keep both — they serve different consumers. When 27-5 reshapes post-27-0, spec notes that Texas's Notion adapter uses project-scope stdio; Tracy may use either in IDE sessions at her discretion.

## Deferred from: code review of story-27-1 (2026-04-17)

- Sibling Office-ZIP suffixes `.docm` / `.dotx` / `.dotm` still fall through to `read_text_file()` in Texas's `local_file` dispatch, re-introducing the binary-garbage defect 27-1 fixes for slightly rarer suffixes. Real-world-shape robustness was explicitly deferred to a follow-on Epic 27 story per Murat's implementation-review note (candidate name: "Texas intake robustness" — password-protected, macros, Google Docs / Pages exports, corrupted-ZIP-valid).
- DOCX body-order iteration silently drops `<w:sdt>` (content controls / structured document tags) and `<w:altChunk>` (embedded sub-document) elements. Form-control DOCX files produce empty extraction with no `known_loss` sentinel. Same follow-on story as the sibling-suffix gap.
- `extract_docx_text` docstring only documents `PackageNotFoundError`, but python-docx can raise `BadZipFile`, `KeyError` (missing style reference), or `AttributeError` under unusual inputs. Either expand the classifier's case table or broaden the docstring's Raises clause. Low-priority doc accuracy.
- Integration test `provenance[0]["ref"] == str(docx_path)` could theoretically flake on Windows short-path resolution (`JUANLE~1` format). Not observed in practice; switch to `Path(...).samefile(...)` comparison if observed.
- Negative-control fixture for Tejal cross-validator — a DOCX/PDF pair from unrelated source docs that should cross-validate as DIFFERENT. Without it, the 100% key-term coverage result cannot be distinguished from "heuristic is loose." Murat implementation-review follow-on.
- Collapse `_EXTRACTOR_LABELS` + `_EXTRACTOR_LABELS_BY_KIND` to a single kind-keyed source of truth with provider-derived default kind. Winston implementation-review architectural polish pass (~20 min).

## Deferred from: implementation review of story-27-2 (2026-04-18)

- **Winston nit — authority-tier lookup promotion.** `SCITE_AUTHORITY_TIERS` in `skills/bmad-agent-texas/scripts/retrieval/scite_provider.py` is provider-local today (correctly so — data, not inference, AC-C.7). Promote to `skills/bmad-agent-texas/scripts/retrieval/authority_tiers.py` as a shared module when a second retrieval-shape provider (Consensus 27-2.5, YouTube 27-4) needs tier-lookup semantics. Do not let the second consumer copy-paste. Trigger: first cross-provider demand. Effort: ~30 min (extract + one-adapter migration + test).
- **Amelia nit — adapter-factory registration drift guard.** `tests/contracts/test_retrieval_adapter_base.py::ADAPTER_FACTORIES` currently requires human memory — a new adapter that ships without being appended to the list silently skips the parametrized contract tests. Add a meta-test that enumerates `RetrievalAdapter.__subclasses__()` and asserts every subclass with a live `PROVIDER_INFO.status == "ready"` appears in `ADAPTER_FACTORIES`. Catches 27-3 / 27-4 / 27-2.5 onboarding misses. Effort: ~15 min.
- **Amelia nit — spec-gap tells for future provider authors.** Two 27-2 implementation debug-log entries worth surfacing in `docs/dev-guide/how-to-add-a-retrieval-provider.md` §11 Anti-patterns so 27-3/27-4 authors don't re-discover them: (a) **self-reference trap in literal-token guards** — a test that greps its own source for forbidden literals will match its own docstring; runtime string concatenation (`"Magic" + "Mock"`) is the mitigation; (b) **regex-ordering pitfalls in log-scrubbers** — `(ms|s|seconds)` matches `s` of "seconds" greedily; put longer alternations first (`(seconds|ms|s)\b`) with explicit word boundary. Both are one-paragraph additions to the §11 anti-pattern list. Effort: ~10 min.
- **Paige nit (applied in 27-2)** — see `retrieval-contract.md` §"Authoring retrieval-shape directives directly (advanced)" for the added operator "when would I reach for this" framing sentence. Kept here as the acknowledgement trail.

## Deferred from: code review of story-27-2-scite-ai-provider (2026-04-18)

19 findings from the three-layer adversarial code-review pass (Blind Hunter + Edge Case Hunter + Acceptance Auditor). Real but non-blocking; reduce surface area of future stories' dev-time surprises.

- `SCITE_MCP_URL` captured at module import (`scite_provider.py:38` — `os.environ.get` at import time). Monkeypatched env post-import has no effect. Future: move URL resolution into `_client()` for full lazy-resolution parity with auth env vars.
- `_truncate_citation_contexts` silently drops unknown classifications (e.g., future scite category beyond supporting/contradicting/mentioning) — no `known_losses` sentinel. Add `unknown_classification` sentinel to surface schema drift from scite MCP.
- Year-only vs ISO-date lexicographic comparison in `_row_date` / date_range filter — `pub_date[:10]` slice on non-ISO input (e.g., bare "2023") produces a 4-char string that lexicographically sorts below any YYYY-MM-DD range and silently passes the filter. Tighten to isoparse + explicit comparison.
- Eager `from .scite_provider import SciteProvider` in `retrieval/__init__.py:72` creates hard import coupling — a scite import failure cascades to all retrieval imports including FakeProvider tests. Winston SF-1 shipped this intentionally for directory-registration determinism; revisit if a retrieval path must remain available with scite disabled (e.g., optional-provider build).
- Legacy-DOCX structural-parity test uses `yaml.safe_load` + dict-compare instead of "plain string equality" required by AC-T.6. This is an authorized deviation per AC-C.6 ("one-line deviation permitted IFF intentional"); document the deviation rationale explicitly in a future 27-* story's Review Record template so it stays authorized.
- `_load_runner` creates multiple module-copies of `run_wrangler.py` under distinct `sys.modules` names in each test file — cross-module `isinstance(o, SourceOutcome)` checks would silently fail if future tests passed dataclass instances across the boundary. Consolidate to a single `conftest.py`-scoped fixture.
- `exclude_ids` / `license_allow` identity surface inconsistent — `source_id` fallback uses `result.get("id")` but `exclude_ids` only checks `doi` + `scite_paper_id`. Add `id` to the exclude-check tuple.
- `int(result.get("supporting_count", 0) or 0)` coercion crashes on non-numeric provider payloads (`int("abc")` → ValueError). Wrap in try/except returning a sentinel or swap to `int(x) if isinstance(x, (int, float, str)) and str(x).lstrip('-').isdigit() else 0`.
- Empty/whitespace DOI slips through `intent.intent.strip()` (`scite_provider.py:283`) → MCP called with empty DOI string. Validate post-strip before query construction.
- `max_results` has no upper bound (scite API may reject `max_results=10_000_000`). Cap at a sane ceiling (e.g., 200) with a log entry when operator hint exceeds it.
- Unicode venue lookup doesn't match substring fallback for non-ASCII strings ("Nature Médicine"). Returns None (→ authority_tier=None), acceptable today but future-proof via NFKC normalization if non-English venues become common.
- `year` type inconsistency — `date = str(year) if year else None` accepts int/str; `_row_date`'s `isinstance(year, int)` guard rejects string "2023". Normalize to int at normalize-time or isoparse at compare-time.
- MCPRateLimitError (429) specific-semantic test not present — AC-T.10 module-prefix test covers the taxonomy generically. Add a 429→MCPRateLimitError assertion for symmetry with 401→MCPAuthError.
- Dispatcher `DispatchError` on constructor `TypeError` unexercised for scite (SciteProvider's `__init__` accepts optional kwargs so the path is reachable via `AdapterFactory.get()` if a future subclass tightens the constructor). Add a negative test if future adapters start requiring constructor args.
- `_acceptance_met` raises `DispatchError` mid-loop AFTER `formulate_query` + `execute` already ran — wasted network call if `min_results` is malformed. Pre-flight the dispatcher's acceptance-criteria validation before first execute.
- `execute` paper-mode `args = {"doi": query["doi"]}` KeyError if caller constructs query without `doi`. Caller-guaranteed today by `formulate_query`, but defensive `.get()` with None-check is low-cost.
- Fixture realism gaps (5 items): null venue, non-ISO `publication_date`, mixed-form authors in one paper, 0/5/2 citation-context distribution across classifications, missing `papers` key schema drift. Add one shared "edge-fixture" per release cycle as live-cassette data informs.
- Paywall graceful degradation with empty abstract → body="" and no `abstract_empty` sentinel alongside `full_text_paywalled`. Add the sentinel so Vera's `completeness_ratio` logic can distinguish "paywalled but abstract available" from "fully opaque."
- Test coverage gaps in `apply_provider_scored`: non-int `supporting_citations_min` / `cited_by_count_min` silently skip filtering (no refinement_log entry). Tighten to raise `DispatchError` or log `criterion_key=<key> reason="invalid_type"`.
- `_mode_from_intent` silently falls through to "search" default when `params["mode"]` is an invalid string — no warning. Add a `_log_unknown_criteria`-style warning path.
