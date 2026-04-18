# Story 27.2: scite.ai Provider

**Status:** ready-for-dev (pending green-light resolution of Pre-Development Gate)
**Created:** 2026-04-17 (ratified-stub); expanded to full BMAD story 2026-04-17 22:45
**Epic:** 27 — Texas Intake Surface Expansion
**Sprint key:** `27-2-scite-ai-provider`
**Branch:** `dev/epic-27-texas-intake`
**Points:** 5
**Depends on:** [27-1](./27-1-docx-provider-wiring.md) (DONE — lockstep check pattern + dispatch-extension template established).
**Blocks:** **Epic 28 — Tracy the Detective.** [28-1 Tracy pilot](./28-1-tracy-pilot-scite-ai.md) cannot run end-to-end without Texas being able to fetch from scite.ai on Tracy's approved-resources directive.

## TL;DR

- **What:** New scite.ai provider for Texas (`provider: scite`) fetching scholarly-paper metadata + abstract/full-text + scite's smart-citation-context signal. Plus `--tracy-approved-resources` CLI flag for second-pass dispatch. Plus atomic-write refactor applied to all Texas artifacts.
- **Why:** Tracy (Epic 28) dispatches via Marcus against this provider to surface evidence with supporting/contradicting/mentioning signal — scite's unique value-add over generic search.
- **Size:** 5 pts. Cross-cutting: new client module + run_wrangler extensions + schema extensions + lockstep-test update.
- **Pre-Dev Gate:** `SCITE_API_TOKEN` is NOT set in `.env`. See §Pre-Development Gate below for path-selection decision (synthetic-cassettes vs xfail vs parallelize).

## Story

As the **Texas wrangler**,
I want **a `scite.ai` provider that fetches scholarly-paper metadata + full-text where available + scite's smart-citation-context signal**,
So that **Tracy's dispatch-via-Marcus second-pass can flow through Texas normally**, producing `extraction-report.yaml` rows tagged `source_origin: tracy-suggested` with scite-specific `provider_metadata` payloads for downstream consumption by Irene Pass 2.

## Background — Why This Story Exists

The operator committed (2026-04-17 session) to making scite.ai the pilot provider for Tracy's editorial-judgment layer (Epic 28). Scite.ai's differentiating value over generic search is its **smart citation context** — for each paper it indexes, scite classifies citations as *supporting / contradicting / mentioning* with context snippets. This is the exact signal Tracy's authority-plus-recency-plus-relevance scoring leverages.

Texas is the technician. Per the dispatch-vs-artifact ratification (Winston, 2026-04-17), Tracy never calls Texas at runtime — instead Tracy writes `tracy-approved-resources.yaml`, operator approves via Marcus, Marcus dispatches Texas with a second-pass directive (`--tracy-approved-resources <path>`), Texas reads Tracy's artifact and fetches. This story builds the `scite.ai` provider Texas needs for that second-pass fetch + the atomic-write artifact hygiene Epic 28's hard pre-Pass-2 gate depends on.

Scite.ai exposes a REST API at `https://api.scite.ai` (documented at `scite.ai/api-docs`). Auth is via API token (env var `SCITE_API_TOKEN`). Three endpoint families touched: **search**, **paper metadata**, **citation-context**.

## Pre-Development Gate (operator-facing — must resolve at green-light)

**Condition:** `SCITE_API_TOKEN` is not present in local `.env`. The story cannot record live cassettes against the real API without it. Four paths exist:

| Path | Approach | Cost | Honors |
|------|----------|------|--------|
| **A — Synthetic cassettes + follow-on live verification** | Hand-craft JSON fixtures matching scite.ai's public API docs. Tests pass deterministically against synthetic data. When token arrives, a follow-on story replays against live API to verify synthetic shapes match production. | +1 follow-on story (small; "27-2-live-cassette-refresh"). | `feedback_regression_proof_tests.md` "no xfail" rule; Epic 28 critical-path timing. |
| **B — xfail-until-token (handoff default)** | Ship client code + unit tests with mocked HTTP. Cassette-backed tests marked `@pytest.mark.xfail(reason="requires SCITE_API_TOKEN")`. Close story "conditional-done"; remediate once token arrives. | Zero follow-on cost. | Handoff's explicit "No API token → xfail" language. |
| **C — Parallelize to 27-3/5/6/7** | Pause 27-2 entirely until operator acquires token. Open parallel work on non-Epic-28-blocking stories (27-3 image, 27-5 Notion MCP, 27-6 Box, 27-7 Playwright MCP). Resume 27-2 when token arrives. | Delays Epic 28 critical path by whatever time token acquisition takes. | No conflict with any rule. |
| **D — Pause run entirely** | Stop here; operator acquires token, then resumes 27-2 as the next story. | Highest idle cost but simplest. | Strictest interpretation of "prereq not met." |

**Path A is the proposed default** — the green-light round can override.

**AC-Pre — Pre-Dev Gate resolution recorded.** Dev-story does NOT start until the selected path is explicitly recorded in the story file's §Green-Light Patches Applied section with party consensus.

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — Provider registration + dispatch.** `run_wrangler.py` recognizes `provider: scite` in the directive. Directive-load validation accepts a `scite` row with exactly one of `query` (string) or `doi` (string) plus an optional `filters` object (`year_min: int`, `venue: string`, `authority_tier_hint: string`). Malformed scite rows (both or neither of query/doi; missing both; unknown filter keys) fail directive-load with exit 30 and a clear error naming the invalid field.

2. **AC-B.2 — Three-call scite fetch contract.** For each scite row, the provider:
   - If `doi` is present: calls `GET /papers/{doi}` for metadata, then `GET /papers/{doi}/citation-contexts` for smart-citation signal. No search.
   - If `query` is present: calls `GET /search` with query + filters. Takes the top result, then proceeds as if it were a doi directive.
   - Returns a `(title, body, SourceRecord)` tuple where body is paper abstract + full-text-if-available, and SourceRecord carries `kind: "scite_paper"` and a note string summarizing smart-citation counts (e.g., `"scite doi=10.1234/abc supporting=12 contradicting=2 mentioning=8"`).

3. **AC-B.3 — Controlled failure on API errors.** All scite network / auth / rate-limit errors surface as FAILED `SourceOutcome` via the existing `_wrangle_source` exception path. New `error_kind` values in `_classify_fetch_error`: `scite_auth_failed` (HTTP 401/403), `scite_rate_limited` (429), `scite_not_found` (404 for doi lookup), `scite_fetch_failed` (generic catch-all for network/timeout/5xx). `known_losses` sentinels via the `_ERROR_KIND_TO_KNOWN_LOSSES` table (same pattern 27-1 introduced): `scite_auth_token_missing_or_invalid`, `scite_rate_limit_hit`, `scite_paper_not_found`, `scite_fetch_generic`.

4. **AC-B.4 — Rich `provider_metadata.scite` payload on success.** Each scite row in `extraction-report.yaml` carries a `provider_metadata.scite` sub-object with exactly these keys: `doi`, `title`, `authors` (list), `year`, `venue`, `supporting_count`, `contradicting_count`, `mentioning_count`, `citation_context_snippets` (list of 3 most-relevant per classification, each with `classification`, `citing_doi`, `snippet`), `scite_report_url` (link to scite's report page for the paper). Missing optional fields (e.g., no venue for a preprint) render as `null`, not absent.

5. **AC-B.5 — Paywall graceful degradation.** When scite's paper-metadata response indicates full-text is paywalled / not available, the extractor falls back to abstract-only extraction. Body contains the abstract; `known_losses: ["full_text_paywalled"]` is recorded. Tier assignment downgrades appropriately (validator handles via existing `completeness_ratio` logic; no special-case code needed).

6. **AC-B.6 — Tracy approved-resources CLI ingestion.** `run_wrangler.py` grows a new flag `--tracy-approved-resources <path>`. When provided:
   - Runner reads the YAML file (schema per `skills/bmad-agent-tracy/schemas/suggested-resources.schema.yaml` once that ships in 28-1; for 27-2 scope, an interim schema in `skills/bmad-agent-texas/references/tracy-approved-resources-interim.schema.yaml` governs).
   - For each approved row, constructs an equivalent directive entry and dispatches via the existing `_wrangle_source` pipeline.
   - Each resulting `SourceOutcome` automatically carries `source_origin: "tracy-suggested"` (vs default `"operator-named"`) + `tracy_row_ref: "<relative-path-to-approved-yaml>#<row_id>"`.
   - Malformed approved-resources file → exit 30 with clear error naming the validation failure.
   - Flag absent → behavior unchanged from pre-27-2 (operator-named sources only).

7. **AC-B.7 — Atomic artifact write (AC-S2 from Epic 28 spine).** All six Texas artifacts (`extracted.md`, `metadata.json`, `extraction-report.yaml`, `ingestion-evidence.md`, `manifest.json`, `result.yaml`) are written atomically via temp-file + rename. No half-written file ever appears at the canonical path. Uses `os.replace()` (POSIX-and-Windows-atomic). Temp files use a suffix that cannot clash with concurrent runs on the same bundle (e.g., `.tmp.<pid>.<monotonic-ns>`).

### Test (AC-T.*)

1. **AC-T.1 — `SciteClient` unit tests with mocked HTTP.** New file `skills/bmad-agent-texas/scripts/tests/test_scite_client.py`. Tests use `responses` library (new dev dep) to mock scite API at the HTTP layer:
   - `test_search_happy_path` — search query returns multi-result canonical response; client returns parsed list.
   - `test_paper_metadata_happy_path` — doi lookup returns full metadata; client returns typed dataclass.
   - `test_citation_context_happy_path` — citation-contexts endpoint returns 3 mixed classifications; client returns sorted list.
   - `test_auth_failure_raises_scite_auth_error` — 401 response → `SciteAuthError` (new typed exception).
   - `test_rate_limit_raises_scite_rate_limit_error` — 429 response → `SciteRateLimitError`.
   - `test_timeout_raises_scite_fetch_error` — timeout → `SciteFetchError`.
   - `test_missing_token_raises_scite_auth_error_at_construction` — `SciteClient()` with env var absent → immediate `SciteAuthError`.

2. **AC-T.2 — Synthetic-cassette integration tests** (path A resolution of Pre-Dev Gate). `skills/bmad-agent-texas/scripts/tests/fixtures/scite-synthetic/` holds hand-crafted JSON responses matching scite.ai's published API docs (scite.ai/api-docs). Tests load these via a `SciteClient` fixture configured to hit a local `responses` registry pre-loaded with the fixtures. Tests:
   - `test_scite_integration_doi_lookup` — full end-to-end through `_wrangle_source` → `extraction-report.yaml` with `provider_metadata.scite` populated correctly.
   - `test_scite_integration_query_search` — query-based dispatch → search → paper-metadata chain.
   - `test_scite_integration_paywalled_falls_back_to_abstract` — fixture simulates paywall flag → `known_losses: ["full_text_paywalled"]`.

3. **AC-T.3 — Tracy approved-resources ingestion integration test.** `test_tracy_approved_resources_ingestion` in `test_run_wrangler.py`:
   - Builds a synthetic `tracy-approved-resources.yaml` at `tmp_path` with 2 scite rows (intent_class `narration_citation` + `counter_example`).
   - Invokes `run_wrangler --tracy-approved-resources <path> --bundle-dir <bundle>` (no `--directive` — approved-resources IS the directive for second-pass).
   - Asserts 2 sources in `extraction-report.yaml`, each with `source_origin: "tracy-suggested"`, `tracy_row_ref` non-empty, `provider_metadata.scite` sub-object populated.
   - Uses synthetic scite cassettes (path A). Fails with a clear message if malformed-approved-resources-file is passed instead.

4. **AC-T.4 — Atomic-write integration test.** `test_atomic_artifact_write` in `test_run_wrangler.py`:
   - Happy-path run produces all 6 artifacts at canonical paths.
   - Asserts NO `.tmp.` or partially-named files remain in bundle dir post-run.
   - Simulated-crash test: monkeypatches `os.replace` to raise `OSError` on the `extraction-report.yaml` final rename, asserts either (a) the full canonical `extraction-report.yaml` never appeared (atomic semantics held) OR (b) the temp file is cleaned up on exit. No half-written canonical artifact ever present.

5. **AC-T.5 — Directive validation tests.** `test_scite_directive_validation` unit test family in `test_run_wrangler.py`:
   - `test_scite_directive_requires_query_or_doi` — neither → exit 30.
   - `test_scite_directive_rejects_both_query_and_doi` — both → exit 30.
   - `test_scite_directive_rejects_unknown_filter_keys` — unknown `filters.foo` → exit 30.

6. **AC-T.6 — Lockstep contract test extended.** `tests/contracts/test_transform_registry_lockstep.py` `REGISTRY_METHOD_TO_EXTRACTOR` gains a scite entry. The new `## scite` section in `transform-registry.md` (AC-C.4) is the discovery target. Test extended to cover 4 in-scope formats now (DOCX + PDF + Notion + scite).

7. **AC-T.7 — Schema-canary test (follow-on — NOT this story).** When the token arrives and a follow-on live-cassette-refresh story runs, a schema-canary test compares a live-recorded cassette against the synthetic fixtures' schema. Drift → WARN (not fail). Cassette-refresh script at `scripts/utilities/refresh_scite_cassettes.py` is stubbed in this story but not executed.

8. **AC-T.8 — Regression suite-level gate (non-collecting AC).** Full pytest green. Baseline from 27-1 closeout: **1036 passed / 2 skipped / 0 failed**. Expected after 27-2: **+N collecting tests** (breakdown below). No `@pytest.mark.skip` or `xfail` added to default suite (path A requirement). No new `@pytest.mark.live_api` (path A requirement — cassette-refresh story would add a `@pytest.mark.live_api` later).

**Test-count delta projection (path A):**
- AC-T.1: 7 unit tests
- AC-T.2: 3 synthetic-cassette integration tests
- AC-T.3: 1 integration test (Tracy ingestion)
- AC-T.4: 2 integration tests (happy atomic-write + simulated crash)
- AC-T.5: 3 directive-validation tests
- AC-T.6: no new test file; existing contract test gains 1 scite entry to iterate
- **Total projected: +16 collecting tests** (1052 passed expected).

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Client lives in `scripts/providers/`.** New file `skills/bmad-agent-texas/scripts/providers/scite_client.py`. Classes: `SciteClient`, `ScitePaper` (dataclass), `CitationContext` (dataclass). Exceptions: `SciteError` (base), `SciteAuthError`, `SciteRateLimitError`, `SciteFetchError`, `SciteNotFoundError`. New directory `skills/bmad-agent-texas/scripts/providers/` (no prior providers live there).

2. **AC-C.2 — `source_wrangler_operations.py` exposes `wrangle_scite_paper()`.** New function `wrangle_scite_paper(doi_or_query_row: dict, *, client: SciteClient | None = None) -> tuple[str, str, SourceRecord]`. Signature mirrors `wrangle_local_docx` (27-1 pattern) but takes a directive-row dict rather than a path. Lazy-default `client` parameter enables test injection; default `SciteClient()` reads env.

3. **AC-C.3 — `run_wrangler._fetch_source()` extended with scite branch.** New `elif provider == "scite":` branch. Branch shape mirrors existing `notion` / `playwright_html` branches. Dispatch regex added to the lockstep test's `REGISTRY_METHOD_TO_EXTRACTOR` under key `"scite search + paper + citation-context api"`.

4. **AC-C.4 — Transform-registry row for scite.** New `## scite` section in [`transform-registry.md`](../../skills/bmad-agent-texas/references/transform-registry.md). Single-row table with Priority 1 method `scite search + paper + citation-context api`, When-to-use `"scholarly-paper intake via DOI or topical query; Tracy-dispatched second-pass evidence fetch"`, Known-limitations `"full-text paywall may degrade to abstract-only; scite's citation-classification accuracy is scite-provider-opinion, not ground truth; rate-limit quota unknown at pilot — monitor"`. Plus implementation cross-reference footnote pointing at `scite_client.py` + `wrangle_scite_paper` + the `_fetch_source` dispatch branch. Human-facing only — test encodes mapping as constants.

5. **AC-C.5 — Schema extension: `provider_metadata.scite` + `source_origin` + `tracy_row_ref`.** [`extraction-report-schema.md`](../../skills/bmad-agent-texas/references/extraction-report-schema.md) extended:
   - Source entry gains optional `provider_metadata` object (typed per-provider; today: `scite` only).
   - Source entry gains optional `source_origin` string (enum: `operator-named` | `tracy-suggested`; default `operator-named` when field absent).
   - Source entry gains optional `tracy_row_ref` string (present iff `source_origin == "tracy-suggested"`).
   - Schema version bump to `1.1` (minor, additive — all fields optional with backwards-compatible defaults). Bump rationale documented in schema doc.

6. **AC-C.6 — Interim Tracy-approved-resources schema.** New file `skills/bmad-agent-texas/references/tracy-approved-resources-interim.schema.yaml`. Defines the shape Texas expects from Marcus's approved-resources-file dispatch, pending the authoritative Tracy-side schema in 28-1. Fields: `row_id`, `provider` (scite | future), `doi` or `query`, `filters` (optional), `intent_class`, `authority_tier` (optional), `fit_score` (optional), `editorial_note` (optional). Interim schema is explicitly superseded by Tracy's 28-1 schema when that lands; 28-1 pre-merge check includes validating Texas still reads the shape.

7. **AC-C.7 — Dependency pin.** `responses>=0.25,<1` added to `pyproject.toml` `[project.optional-dependencies] dev` (HTTP mocking for tests). No new runtime deps for scite — `requests` is already present (confirmed in repo). Token-availability is an operator concern; env-var reading uses existing `python-dotenv` stack.

8. **AC-C.8 — Inherit 27-1 patterns (verification-only).**
   - CLI UTF-8 guard on `run_wrangler.py` unchanged — scite dispatch inherits.
   - `_EXTRACTOR_LABELS_BY_KIND` gains `"scite_paper": "scite_api"`.
   - Controlled-failure FAILED-outcome contract from 27-1's AC-B.3 extended to scite via new `scite_*` error_kind values.

## File Impact

| File | Change | Lines (est.) |
|------|--------|-------|
| [`skills/bmad-agent-texas/scripts/providers/scite_client.py`](../../skills/bmad-agent-texas/scripts/providers/scite_client.py) | **New** — API client + dataclasses + exceptions | +180 |
| [`skills/bmad-agent-texas/scripts/providers/__init__.py`](../../skills/bmad-agent-texas/scripts/providers/__init__.py) | **New** — package marker | +1 |
| [`skills/bmad-agent-texas/scripts/source_wrangler_operations.py`](../../skills/bmad-agent-texas/scripts/source_wrangler_operations.py) | Add `wrangle_scite_paper()` + `scite_paper` `SourceRecord` kind | +90 |
| [`skills/bmad-agent-texas/scripts/run_wrangler.py`](../../skills/bmad-agent-texas/scripts/run_wrangler.py) | Add scite dispatch + `--tracy-approved-resources` CLI + atomic-write refactor + scite error_kinds + `source_origin` / `tracy_row_ref` / `provider_metadata` field population | +120 |
| [`skills/bmad-agent-texas/references/transform-registry.md`](../../skills/bmad-agent-texas/references/transform-registry.md) | Add `## scite` section with cross-reference footnote | +12 |
| [`skills/bmad-agent-texas/references/extraction-report-schema.md`](../../skills/bmad-agent-texas/references/extraction-report-schema.md) | Schema v1.1: add `provider_metadata`, `source_origin`, `tracy_row_ref` | +50 |
| [`skills/bmad-agent-texas/references/tracy-approved-resources-interim.schema.yaml`](../../skills/bmad-agent-texas/references/tracy-approved-resources-interim.schema.yaml) | **New** — interim schema pending 28-1 | +60 |
| [`skills/bmad-agent-texas/scripts/tests/test_scite_client.py`](../../skills/bmad-agent-texas/scripts/tests/test_scite_client.py) | **New** — 7 unit tests (AC-T.1) | +220 |
| [`skills/bmad-agent-texas/scripts/tests/test_texas_source_wrangler_operations.py`](../../skills/bmad-agent-texas/scripts/tests/test_texas_source_wrangler_operations.py) | Add `wrangle_scite_paper` unit tests (happy + paywall) | +60 |
| [`skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py`](../../skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py) | Add scite-integration (3) + tracy-approved-resources + atomic-write (2) + directive-validation (3) tests | +200 |
| [`skills/bmad-agent-texas/scripts/tests/fixtures/scite-synthetic/`](../../skills/bmad-agent-texas/scripts/tests/fixtures/scite-synthetic/) | **New** — hand-crafted JSON fixtures (search_happy, paper_metadata_happy, paper_metadata_paywalled, citation_context_happy, empty_search, auth_failure_401, rate_limit_429) | ~7 files, +250 lines JSON |
| [`tests/contracts/test_transform_registry_lockstep.py`](../../tests/contracts/test_transform_registry_lockstep.py) | Add scite entry to `REGISTRY_METHOD_TO_EXTRACTOR` | +5 |
| [`pyproject.toml`](../../pyproject.toml) | Add `responses>=0.25,<1` to dev deps | +1 |
| [`.env.example`](../../.env.example) | Document `SCITE_API_TOKEN` | +3 |
| [`scripts/utilities/refresh_scite_cassettes.py`](../../scripts/utilities/refresh_scite_cassettes.py) | **New (stub)** — executable only when token present; records live cassettes into `scite-live/` for future-refresh-story diff | +80 |

**No changes to:** other providers, fidelity contracts, fidelity-gate-map, lane-matrix.

## Tasks / Subtasks

- [ ] **T-Pre — Resolve Pre-Development Gate at green-light round.** Record selected path (A/B/C/D) in §Green-Light Patches Applied. Dev-story does NOT begin until this is written.
- [ ] **T1 — Dependency + env scaffolding** (AC-C.7)
  - [ ] Add `responses>=0.25,<1` to `pyproject.toml` dev deps; install.
  - [ ] Add `SCITE_API_TOKEN=` placeholder to `.env.example` with link to scite.ai/api-docs.
  - [ ] Create `skills/bmad-agent-texas/scripts/providers/__init__.py` (package marker).
- [ ] **T2 — SciteClient implementation** (AC-C.1)
  - [ ] Implement `scite_client.py`: `SciteClient` class with `__init__(token: str | None = None, base_url: str = "https://api.scite.ai", timeout: int = 30)`; three methods (`search`, `get_paper`, `get_citation_contexts`); typed exceptions; `ScitePaper` + `CitationContext` dataclasses matching AC-B.4 field names exactly.
  - [ ] Token resolution order: constructor arg → `SCITE_API_TOKEN` env var → `SciteAuthError` at `__init__`. Lazy env read (not at module load).
  - [ ] HTTP layer uses existing `requests` dep; all calls pass through a single `_get()` helper that maps status codes to typed exceptions (401/403 → SciteAuthError; 404 → SciteNotFoundError; 429 → SciteRateLimitError; 5xx + timeouts + connection errors → SciteFetchError).
- [ ] **T3 — Synthetic fixtures + unit tests** (AC-T.1, AC-T.2 path A)
  - [ ] Author JSON fixtures under `scripts/tests/fixtures/scite-synthetic/` matching scite.ai/api-docs shapes. One fixture file per response-type (search_happy.json, paper_metadata_happy.json, paper_metadata_paywalled.json, citation_context_happy.json, empty_search.json, auth_failure_401.json, rate_limit_429.json).
  - [ ] Write 7 unit tests in `test_scite_client.py` using `responses.RequestsMock()` context manager loaded with the fixtures.
- [ ] **T4 — wrangle_scite_paper + source_wrangler unit tests** (AC-C.2, AC-B.2, AC-B.4, AC-B.5)
  - [ ] Add `wrangle_scite_paper()` to `source_wrangler_operations.py` following the `wrangle_local_docx` pattern (title from paper title, body = abstract + full_text_if_available, SourceRecord kind="scite_paper", note = smart-cite counts).
  - [ ] Add `scite_paper` entry to `_EXTRACTOR_LABELS_BY_KIND` in `run_wrangler.py` → `"scite_api"`.
  - [ ] Add 2 happy-path + paywall unit tests to `test_texas_source_wrangler_operations.py`.
- [ ] **T5 — `_fetch_source` scite dispatch + directive validation** (AC-B.1, AC-C.3, AC-T.5)
  - [ ] Add `elif provider == "scite":` branch. Construct `SciteClient()` lazily; pass directive row to `wrangle_scite_paper`.
  - [ ] Extend `_load_directive` validation: reject malformed scite rows (both/neither of query/doi; unknown filter keys) with exit 30.
  - [ ] Add 3 directive-validation tests (AC-T.5).
- [ ] **T6 — Error classification + known_losses sentinels** (AC-B.3)
  - [ ] Extend `_classify_fetch_error` with 4 scite-prefixed isinstance checks (lazy-import the SciteError class via `type(exc).__name__` check + `type(exc).__module__` startswith qualification — same pattern 27-1 introduced).
  - [ ] Extend `_ERROR_KIND_TO_KNOWN_LOSSES` with 4 scite sentinels.
- [ ] **T7 — `provider_metadata.scite` + schema v1.1 extension** (AC-B.4, AC-C.5)
  - [ ] Update `extraction-report-schema.md` to schema v1.1 with `provider_metadata`, `source_origin`, `tracy_row_ref` fields documented.
  - [ ] Update `_source_outcome_to_report_entry` in `run_wrangler.py` to emit these fields when present.
  - [ ] Plumb `rec.provider_metadata` (new SourceRecord field) from `wrangle_scite_paper` through `_wrangle_source` to the report entry.
- [ ] **T8 — `--tracy-approved-resources` CLI + interim schema** (AC-B.6, AC-C.6)
  - [ ] Author `tracy-approved-resources-interim.schema.yaml` under Texas references.
  - [ ] Add `--tracy-approved-resources <path>` argparse flag to `run_wrangler.main`.
  - [ ] Add `_load_approved_resources(path)` helper that validates against interim schema and returns a directive-equivalent list of source rows.
  - [ ] Wire source_origin + tracy_row_ref onto each SourceOutcome derived from approved-resources rows.
  - [ ] Add 1 integration test (AC-T.3) + 1 malformed-file test (exit 30).
- [ ] **T9 — Atomic artifact write refactor** (AC-B.7, AC-T.4)
  - [ ] Refactor every `write_text()` / `json.dumps` write path for the 6 canonical artifacts into an `_atomic_write(path, content)` helper using `os.replace()` on a `<path>.tmp.<pid>.<monotonic-ns>` intermediate.
  - [ ] Cleanup on exit: install atexit handler (or use try/finally in `run()`) to remove stray `.tmp.*` files.
  - [ ] Add 2 integration tests (AC-T.4): happy-path no-temp-leakage + monkeypatch simulated-crash.
- [ ] **T10 — Transform-registry + lockstep test** (AC-C.4, AC-T.6)
  - [ ] Add `## scite` section to `transform-registry.md`.
  - [ ] Add scite entry to `REGISTRY_METHOD_TO_EXTRACTOR` in the lockstep contract test.
  - [ ] Verify lockstep test passes (registry ↔ code in lockstep for DOCX + PDF + Notion + scite).
- [ ] **T11 — Cassette-refresh stub** (AC-T.7)
  - [ ] Create `scripts/utilities/refresh_scite_cassettes.py` — reads token from env, hits live API with canonical query set, writes cassettes into `scite-live/` directory. Script is executable-by-operator; NOT run in CI. Docstring + --help text explain the follow-on workflow.
- [ ] **T12 — Regression + pre-commit + lockstep verification**
  - [ ] Full pytest green — expected **1052 passed / 2 skipped / 0 failed** (1036 baseline + 16 new).
  - [ ] Pre-commit hooks green (ruff + orphan + co-commit).
  - [ ] `pytest -m trial_critical` unchanged (scite is not trial-critical).
  - [ ] Lockstep test green (4 in-scope formats + 3 exempt).
- [ ] **T13 — Party-mode implementation review + bmad-code-review + closure**
  - [ ] Party-mode implementation review (Winston + Amelia + Murat + Paige).
  - [ ] `bmad-code-review` layered pass. MUST-FIX remediated; SHOULD-FIX triaged.
  - [ ] Flip sprint-status 27-2 → done with closure comment.
  - [ ] Epic 27 roster update (epic file + bmm-workflow-status.yaml).
  - [ ] Epic 28 roster update — 28-1 `ready-for-dev` dependency on 27-2 is now satisfied.

## Dev Notes

### Architecture guardrails (from ratification + Epic 27 spine + Epic 28 spine)

- **Texas stays pure technician.** No editorial judgment on scite results. Faithful fetch + structured extraction only. (Winston Round-1 Epic 27.)
- **Tracy never calls Texas at runtime.** All dispatch goes through Marcus; artifact handoff via filesystem. (AC-S1 Epic 28 spine — Winston ratification 2026-04-17.)
- **Structured return, not blob dump.** `provider_metadata.scite` sub-object + typed SourceRecord with per-provider kind. (AC-S3 Epic 27 spine.)
- **Controlled-failure contract extended.** 4 new scite-specific `error_kind` values; each maps to a distinct `known_losses` sentinel so operator routing can distinguish auth-failure (need new token) from rate-limit (wait + retry) from not-found (typo or paper withdrawn).
- **Atomic-write is an Epic 28 prerequisite.** Not a polish — partial-write protection is load-bearing because Tracy's output drives a hard downstream gate (Epic 28 AC-S3). A half-written manifest that "appears complete" would bypass the gate silently.
- **Synthetic cassettes > live cassettes for a pilot provider.** Synthetic fixtures captured against scite.ai published API docs are the ground-truth contract for this story. Live cassettes record actual response shapes — a diff between synthetic and live reveals API-doc drift. Schema-canary test (follow-on) is the operator's leading indicator.

### Source tree (new + touched)

```
skills/bmad-agent-texas/
├── scripts/
│   ├── providers/
│   │   ├── __init__.py                   [NEW] +1 line
│   │   └── scite_client.py               [NEW] +180 lines
│   ├── source_wrangler_operations.py     [TOUCH] +wrangle_scite_paper() ~line 410
│   ├── run_wrangler.py                   [TOUCH] +scite dispatch + --tracy-approved-resources + atomic-write
│   └── tests/
│       ├── fixtures/scite-synthetic/     [NEW] 7 JSON fixture files
│       ├── test_scite_client.py          [NEW] +220 lines (7 tests)
│       ├── test_texas_source_wrangler_operations.py  [TOUCH] +2 tests
│       └── test_run_wrangler.py          [TOUCH] +9 tests (scite + tracy + atomic + validation)
└── references/
    ├── transform-registry.md             [TOUCH] +## scite section
    ├── extraction-report-schema.md       [TOUCH] schema v1.1
    └── tracy-approved-resources-interim.schema.yaml  [NEW] +60 lines

tests/contracts/
└── test_transform_registry_lockstep.py   [TOUCH] +scite entry

scripts/utilities/
└── refresh_scite_cassettes.py            [NEW] +80 lines (stub script)

pyproject.toml                            [TOUCH] +responses dev dep
.env.example                              [TOUCH] +SCITE_API_TOKEN placeholder
```

### Previous story intelligence (from 27-1 DOCX wiring closeout)

27-1 established patterns this story MUST inherit:

- **Dispatch branch extension** (not rewrite) — new `elif provider == "scite":` follows the existing `notion` / `playwright_html` shape.
- **`_EXTRACTOR_LABELS_BY_KIND`** is keyed by `SourceRecord.kind`, not provider. Add `"scite_paper": "scite_api"`.
- **Module-qualified exception classification** — `type(exc).__module__.startswith("scite_client")` pattern (mirrors 27-1's `docx.` prefix check for PackageNotFoundError).
- **`_ERROR_KIND_TO_KNOWN_LOSSES` table pattern** — add 4 scite error_kinds with sentinel known_losses strings.
- **Lockstep test `REGISTRY_METHOD_TO_EXTRACTOR` + `LOCKSTEP_EXEMPTIONS`** — add scite entry; the fragility signpost docstring (added in 27-1 code-review remediation) already warns about dispatch-regex refactors.
- **In-test fixture generation for tests** — hand-crafted JSON fixtures under `tests/fixtures/` (not committed binaries; same pattern 27-1's in-test DOCX generation followed).
- **Co-commit test + impl** — tests land in the same commit slice as source.
- **Ruff + pre-commit + pytest green before review** — no exceptions.
- **No `trial_critical` marker** — scite dispatch isn't a pre-Prompt-1 trial gate.

### Testing standards

- **Unit / integration split** — unit tests in `test_scite_client.py` + `test_texas_source_wrangler_operations.py` exercise the client + extractor directly; integration tests in `test_run_wrangler.py` exercise the full CLI path with synthetic cassettes.
- **HTTP mocking via `responses`** — avoid real network in ALL tests. `responses` registers expected URL patterns + response JSON/headers/status at test setup; fails loudly on unexpected calls (good — that means the client is hitting the wrong endpoint).
- **No `live_api`, no `trial_critical`, no `xfail`, no `skip`** — path A requirement.
- **Fixture hygiene** — JSON fixtures under `tests/fixtures/scite-synthetic/` are plain text, diff-friendly, not binary. Check in to git.
- **Regression coverage** — +16 collecting tests expected. Verify via `pytest --collect-only | wc -l`.

### References

- Epic spine: [_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md](epic-27-texas-intake-expansion.md) — AC-S cross-cutting spine (AC-S1 through AC-S8).
- Epic 28 spine (downstream contract): [_bmad-output/implementation-artifacts/epic-28/_shared/ac-spine.md](epic-28/_shared/ac-spine.md) — AC-S1 (dispatch-vs-artifact) + AC-S2 (atomicity) + AC-S5 (vocabulary SSOT).
- Tracy vocabulary SSOT: [skills/bmad-agent-tracy/references/vocabulary.yaml](../../skills/bmad-agent-tracy/references/vocabulary.yaml) — `intent_class`, `authority_tier`, `fit_score` values Texas's interim-schema validator checks for.
- Closed 27-1 story (pattern source): [27-1-docx-provider-wiring.md](./27-1-docx-provider-wiring.md) — dispatch-extension + lockstep + error-classification patterns.
- scite.ai public API docs: `scite.ai/api-docs` (operator-accessible; agent cannot navigate — use for synthetic-fixture authoring reference).
- Transform registry: [skills/bmad-agent-texas/references/transform-registry.md](../../skills/bmad-agent-texas/references/transform-registry.md) (new `## scite` section lands here).
- Extraction report schema: [skills/bmad-agent-texas/references/extraction-report-schema.md](../../skills/bmad-agent-texas/references/extraction-report-schema.md) (schema v1.1 bump).

### Non-goals

- **Tracy's agent-side code** — fit-score algorithm, authority-tier classification, editorial_note generation. All in 28-1 scope.
- **Live-API cassette recording** — follow-on "27-2-live-cassette-refresh" story triggered by token arrival.
- **Schema-canary test execution** — test framework stubbed, cassette-refresh script stubbed, both executable only after token arrives.
- **scite.ai webhook / notification support** — not needed for pull-style fetching.
- **Multi-tenant API-token handling** — single operator, single token.
- **Generic scholarly-search provider abstraction** — 27-2 is scite-specific. Future Pubmed / Semantic Scholar / OpenAlex providers will each get their own story per the one-provider-per-story pattern.
- **Run-time quota / rate-limit adaptive backoff** — basic 429-surfacing via `SciteRateLimitError` is in scope; adaptive backoff is not. Operator handles rate-limit retry manually; automated backoff is a future hardening story.

## Test Plan

| Test | Level | Mocked? | Blocking at merge? |
|------|-------|---------|---------------------|
| AC-T.1 × 7 scite client unit tests | Unit | responses-mock | Yes |
| AC-T.2 × 3 synthetic-cassette integration tests | Integration | synthetic JSON | Yes |
| AC-T.3 tracy-approved-resources ingestion | Integration | synthetic JSON | Yes |
| AC-T.4 × 2 atomic-write tests | Integration | monkeypatch | Yes |
| AC-T.5 × 3 directive-validation tests | Unit | N/A | Yes |
| AC-T.6 lockstep contract (scite entry added) | Contract | N/A | Yes |
| AC-T.7 schema-canary (follow-on story) | Live | No | **Not this story — deferred** |
| AC-T.8 suite-level regression | Suite | N/A | Yes |

Target baseline delta: **+16 collecting tests** (path A; 1052 passed expected). AC-T.8 is a non-collecting suite-level gate. No new skips, no new xfail, no new live_api, no new trial_critical.

## Risks

| Risk | Mitigation |
|------|------------|
| Synthetic-cassette shapes drift from real scite.ai response shapes (fixture fidelity risk) | Schema-canary follow-on story records live cassettes + diffs against synthetic. First live run is the moment-of-truth; if diff is non-trivial, operator raises follow-on hardening. |
| Atomic-write refactor (AC-B.7) breaks existing tests that race on intermediate file presence | Pre-merge audit: `grep -rn "\.tmp\|existence.*before" tests/` + run full pytest mid-refactor. Temp suffix includes PID + monotonic-ns to avoid cross-test clash. |
| `responses` library's request-matching is too loose / too strict → false-positive or false-negative test failures | Use `responses.matchers.header_matcher` for auth header + URL + query-param matching. Fixture JSON is the single source of truth; one fixture-per-endpoint keeps diffing clean. |
| Tracy-approved-resources interim schema drifts from 28-1's canonical schema when that lands | 28-1 pre-merge includes a contract test that validates Texas still reads the interim shape OR migrates cleanly. Captured as 28-1 AC. |
| scite.ai API rate-limit (unknown quota) hit during future live cassette recording | Operator-facing script includes per-request pacing + abort-on-429. Not a risk for synthetic-cassette story path. |
| Paywalled full-text forcing abstract-only degradation | AC-B.5 makes this a first-class known_losses sentinel; downstream validators handle via existing completeness_ratio logic. |

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

_(filled by bmad-code-review; template = 27-1 Review Record structure)_

## Party Input Captured (ratification, 2026-04-17)

- **John (PM, Round 3):** scite.ai elevated from grouped-provider story to standalone because Epic 28 blocks on it. Points: 3 (John) / 5 (Amelia) — Amelia's estimate adopted given the Tracy-ingestion AC-5 scope.
- **Amelia (Dev, Round 3):** file-path impact, test surface, atomic-write hygiene detail.
- **Murat (Test, Round 2 + 3):** cassette strategy (5 cassettes), schema-canary, quarantined live tests, xfail-strict during implementation.
- **Paige (Docs, Round 3):** `provider_metadata.scite` sub-object pattern (wins over row-level scite fields for extensibility to future providers).
- **Winston (dispatch-vs-artifact ratification, Round 3+):** atomic-write artifact discipline is a Winston hygiene edge case baked into AC-B.7.

## Green-Light Patches Applied (party-mode round 1, pending)

_Green-light round to record:_
- **Path selection for Pre-Development Gate (A / B / C / D).** Dev-story blocks until this is set.
- Any other scope patches per panel consensus.

## BMAD Closure Criteria

- [ ] Pre-Development Gate resolved (path recorded in §Green-Light Patches Applied).
- [ ] All AC-B.1 through AC-B.7 behavioral assertions green in test output.
- [ ] All AC-T.1 through AC-T.6 collecting tests pass; AC-T.8 suite-level regression gate green.
- [ ] All AC-C.1 through AC-C.8 contract-pinning checks satisfied.
- [ ] Full `pytest` green (expected 1052 passed / 2 skipped / 0 failed under path A).
- [ ] Pre-commit hooks pass (ruff + orphan + co-commit) on all changed files.
- [ ] `bmad-party-mode` implementation review consensus: approve.
- [ ] `bmad-code-review` layered pass (Blind Hunter + Edge Case Hunter + Acceptance Auditor); MUST-FIX remediated; SHOULD-FIX triaged.
- [ ] `sprint-status.yaml::development_status::27-2-scite-ai-provider` flipped to `done` with closure comment.
- [ ] Epic 27 roster entry updated (epic file + bmm-workflow-status.yaml).
- [ ] Epic 28 entry updated — 28-1 hard-dependency on 27-2 now satisfied.
