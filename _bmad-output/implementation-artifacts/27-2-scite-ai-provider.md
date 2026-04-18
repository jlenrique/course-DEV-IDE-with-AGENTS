# Story 27-2: scite.ai Provider

**Epic:** 27 — Texas Intake Surface Expansion
**Status:** ratified-stub
**Sprint key:** `27-2-scite-ai-provider`
**Added:** 2026-04-17
**Points:** 5
**Depends on:** 27-1 ships first (lockstep check pattern must exist before adding a new format)
**Blocks:** **Epic 28 — Tracy the Detective.** 28-1 (Tracy pilot) cannot run end-to-end without Texas being able to fetch from scite.ai on Tracy's approved-resources directive.

## Story

As the Texas wrangler,
I want a `scite.ai` provider that fetches scholarly-paper metadata + full-text where available + scite's smart-citation-context signal,
So that Tracy's dispatch-via-Marcus second-pass can flow through Texas normally, producing `extraction-report.yaml` rows tagged `source_origin: tracy-suggested` with scite-specific `provider_metadata` payloads for downstream consumption by Irene Pass 2.

## Background — Why This Story Exists

The operator committed (2026-04-17 session) to making scite.ai the pilot provider for Tracy's editorial-judgment layer (Epic 28). Scite.ai's differentiating value over generic search is its **smart citation context** — for each paper it indexes, scite classifies citations as *supporting / contradicting / mentioning* with context snippets. This is the exact signal Tracy's authority-plus-recency-plus-relevance scoring leverages.

Texas is the technician. Per the dispatch-vs-artifact ratification (Winston, 2026-04-17), Tracy never calls Texas at runtime — instead Tracy writes `tracy-approved-resources.yaml`, operator approves via Marcus, Marcus dispatches Texas with a second-pass directive, Texas reads Tracy's artifact and fetches. This story builds the `scite.ai` provider Texas needs for that second-pass fetch.

Scite.ai exposes a REST API. Auth is via API token (env var `SCITE_API_TOKEN`). Three endpoint families touched by this story: **search**, **paper metadata**, **citation-context**.

## Acceptance Criteria

**AC-1: Provider registration + dispatch**
- `skills/bmad-agent-texas/scripts/run_wrangler.py` gains `provider: scite` in the provider dispatch.
- Directive schema accepts `provider: scite` with required `query` or `doi` field + optional `filters` sub-object (year_min, venue, authority_tier_hint).
- Unsupported combinations (neither `query` nor `doi`) rejected at directive-load with exit 30.

**AC-2: API client**
- New module `skills/bmad-agent-texas/scripts/providers/scite_client.py` wraps scite.ai REST endpoints.
- Client reads `SCITE_API_TOKEN` from env; missing token raises clear `SciteAuthError` at construction.
- Three methods: `search(query, filters)`, `get_paper(doi)`, `get_citation_context(doi)`.
- All calls use a bounded timeout (default 30s, configurable). All network exceptions caught at the boundary and synthesized into FAILED `SourceOutcome` per AC-S4 of the epic spine.

**AC-3: `transform-registry.md` row for scite**
- Registry advertises: `scite` format, fetches scholarly paper metadata + abstract + citation context, known-losses: full-text may be paywalled (metadata-only fallback), `provider_metadata.scite` sub-object is populated per the schema in `extraction-report-schema.md`.
- Auth requirement documented: `SCITE_API_TOKEN` env var.
- Passes the lockstep check from 27-1 (AC-S6).

**AC-4: Extraction output shape**
- Each scite row in `extraction-report.yaml` carries:
  - Standard Texas fields: `source_id`, `provider`, `role`, `tier`, `completeness_ratio`, `word_count`, `line_count`, `heading_count`, `structural_fidelity`, `evidence[]`, `known_losses[]`
  - `source_origin: tracy-suggested` (if directive arrives from a Tracy-approved-resources file; `operator-named` otherwise)
  - `tracy_row_ref: <path-to-tracy-approved-yaml>#<row_id>` when `source_origin: tracy-suggested`
  - `provider_metadata.scite` sub-object with: `doi`, `title`, `authors`, `year`, `venue`, `supporting_count`, `contradicting_count`, `mentioning_count`, `citation_context_snippets[]`, `scite_report_url`
- Extracted text (written to `extracted.md`) is the paper abstract + available full-text body; falls back to abstract-only when full-text is paywalled, with `known_losses: ["full_text_paywalled"]` recorded.

**AC-5: Tracy approved-resources ingestion**
- `run_wrangler.py` grows a new CLI flag `--tracy-approved-resources <path>` for second-pass invocation.
- When present, the runner reads the YAML, iterates rows, dispatches each approved row as a scite (or future-provider) fetch.
- Each resulting `SourceOutcome` carries `source_origin: tracy-suggested` + `tracy_row_ref` automatically.
- When `--tracy-approved-resources` absent, behavior is unchanged from current (operator-named sources only).

**AC-6: Atomic artifact write (Winston hygiene edge case)**
- The runner's output artifacts (`extraction-report.yaml`, `manifest.json`, etc.) are written atomically: temp file + rename. No half-written files visible to downstream consumers.
- Applies epic-wide once landed, not just scite — but this is the story that introduces the pattern because Tracy's Epic 28 depends on it for partial-write protection.

**AC-7: Test coverage (AC-S5 from spine)**
- `tests/test_scite_provider.py` — unit tests for the client (mocked HTTP).
- `tests/cassettes/texas/scite/` — cassette library:
  - `search_happy.yaml` — canonical multi-result response
  - `paper_metadata_happy.yaml` — full metadata + abstract
  - `citation_context_happy.yaml` — 3 citation contexts mixed supporting / contradicting / mentioning
  - `search_empty.yaml` — zero-result response
  - `auth_failure.yaml` — 401 response shape
- `tests/test_run_wrangler.py::test_scite_integration_scenario` — integration test against cassettes, verifies AC-4 output shape.
- `tests/test_run_wrangler.py::test_tracy_approved_resources_ingestion` — integration test verifying AC-5 (simulates Tracy-produced approved-resources file as input).
- Schema-canary test: a cassette-backed test that validates the live-recorded response shape against the client's pydantic/jsonschema model. Warns loudly (not fails) on schema drift in a quarterly cassette refresh.

**AC-8: Lockstep check passes**
- Transform-registry lockstep check (from 27-1 AC-6) now includes scite — registry advertisement matches implementation.

**AC-9: Regression — no new failures, no new skips**
- Full pytest green.
- No `skip` / `xfail` added to default suite.

## File Impact

| File | Change | Lines (est.) |
|------|--------|--------------|
| `skills/bmad-agent-texas/scripts/providers/scite_client.py` | New — API client | +150 |
| `skills/bmad-agent-texas/scripts/run_wrangler.py` | Add scite dispatch branch + `--tracy-approved-resources` flag + atomic-write refactor | +80 |
| `skills/bmad-agent-texas/references/transform-registry.md` | Add scite row | +10 |
| `skills/bmad-agent-texas/references/extraction-report-schema.md` | Extend with `provider_metadata.scite` schema, `source_origin` field, `tracy_row_ref` field | +30 |
| `tests/test_scite_provider.py` | New — unit tests | +180 |
| `tests/cassettes/texas/scite/*.yaml` | New — cassette library (5 files) | binary-ish |
| `tests/test_run_wrangler.py` | Add scite + tracy-approved scenarios | +60 |
| `requirements.txt` or `pyproject.toml` | Add scite client deps (likely just `httpx` or `requests`; probably already present) | 0-1 |
| `.env.example` | Document `SCITE_API_TOKEN` | +1 |

## Tasks / Subtasks

- [ ] T1: Register for scite.ai API access, store token in local `.env`, document pattern in `.env.example`.
- [ ] T2: Implement `scite_client.py` against the live API; record cassettes once working.
- [ ] T3: Extend `extraction-report-schema.md` with scite-aware fields (`provider_metadata.scite` sub-object, `source_origin` field, `tracy_row_ref` field).
- [ ] T4: Add scite dispatch branch in `run_wrangler.py` using the new client.
- [ ] T5: Refactor artifact write path to atomic (temp + rename) — applies to ALL artifacts, not just scite. This is the Epic 28-dependency hygiene item.
- [ ] T6: Add `--tracy-approved-resources` CLI flag + ingestion logic.
- [ ] T7: Record cassette library.
- [ ] T8: Write unit tests against mocked client + cassette-backed integration tests.
- [ ] T9: Update `transform-registry.md` with scite row + run lockstep check.
- [ ] T10: Schema-canary test + quarterly cassette refresh script.
- [ ] T11: Manual end-to-end: run Texas against a synthesized Tracy-approved-resources file, verify `extraction-report.yaml` has all new fields populated correctly.
- [ ] T12: Regression pass.

## Test Plan

| Test | Level | Cassette? | Blocking at merge? |
|------|-------|-----------|---------------------|
| `test_scite_provider::test_search_happy` | Unit (cassette) | Yes | Yes |
| `test_scite_provider::test_paper_metadata` | Unit (cassette) | Yes | Yes |
| `test_scite_provider::test_citation_context` | Unit (cassette) | Yes | Yes |
| `test_scite_provider::test_auth_failure_raises` | Unit (cassette) | Yes | Yes |
| `test_scite_provider::test_empty_search` | Unit (cassette) | Yes | Yes |
| `test_scite_provider::test_network_timeout_controlled_failure` | Unit (mocked) | No | Yes |
| `test_run_wrangler::test_scite_integration_scenario` | Integration | Yes | Yes |
| `test_run_wrangler::test_tracy_approved_resources_ingestion` | Integration | Yes | Yes |
| `test_run_wrangler::test_atomic_artifact_write` | Integration | No | Yes |
| `test_transform_registry_lockstep` (extended) | Contract | No | Yes |
| Schema-canary (cassette vs live) | Live | No | **Warn-only; not blocking** |

## Out of Scope

- Tracy's Epic 28 pilot story (28-1) — that's a separate story, separate epic.
- Generic "search this scholarly topic" from Texas — Texas does not initiate searches; Texas fetches explicit directives. Tracy handles query formulation.
- scite.ai notification / webhook integrations — not needed for pull-style fetching.
- Multi-tenant API-token handling — single operator, single token.

## Risks

| Risk | Mitigation |
|------|------------|
| scite.ai API schema drift between cassette record and production | Schema-canary test warns quarterly; cassette refresh script makes refresh cheap. |
| Scite API rate limit (unknown quota) hit during live testing | Cassette-backed by default; real-network calls quarantined to `tests/live/`. |
| Paywalled full-text forcing abstract-only degradation | Accepted as `known_losses` entry; Tracy's editorial_note will address when relevant. |
| Tracy approved-resources ingestion (AC-5) creates new failure surface where a malformed Tracy file crashes Texas | Strict YAML validation at load + pydantic schema for approved-resources shape; malformed file = exit 30 directive error. |
| Atomic-write refactor (AC-6) breaks existing write-path assumptions in other tests | Audit all file-write tests pre-merge; use temp-file suffix to avoid clash with concurrent runs. |

## Done When

- [ ] All 9 ACs green.
- [ ] Tracy-approved-resources sample file successfully drives Texas to produce a conforming second-pass `extraction-report.yaml`.
- [ ] Transform-registry lockstep check: scite row matches code.
- [ ] `bmad-code-review` run adversarially, MUST-FIX remediated.
- [ ] Story closure record in `sprint-status.yaml` with review summary.

## Party Input Captured

- **John (PM, Round 3):** scite.ai elevated from grouped-provider story to standalone because Epic 28 blocks on it. Points: 3 (John) / 5 (Amelia) — Amelia's estimate adopted given the Tracy-ingestion AC-5 scope.
- **Amelia (Dev, Round 3):** file-path impact, test surface, atomic-write hygiene detail.
- **Murat (Test, Round 2 + 3):** cassette strategy (5 cassettes), schema-canary, quarantined live tests, xfail-strict during implementation.
- **Paige (Docs, Round 3):** `provider_metadata.scite` sub-object pattern (wins over row-level scite fields for extensibility to future providers).
- **Winston (dispatch-vs-artifact ratification, Round 3+):** atomic-write artifact discipline is a Winston hygiene edge case baked into AC-6.
