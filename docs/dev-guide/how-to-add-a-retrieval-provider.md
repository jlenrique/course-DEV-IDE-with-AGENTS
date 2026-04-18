# How to add a retrieval provider (Texas)

**Audience:** Developers wiring a new scholarly / video / image / MCP-mediated
retrieval source into Texas — e.g., Consensus, PubMed, Semantic Scholar,
YouTube, a new image provider. Story 27-2 (SciteProvider) is the living worked
example.

**When this guide applies:** You are adding a *retrieval-shape* provider — one
that takes an editorial intent and returns rows Texas then merges / normalizes.
If you are adding a *locator-shape* handler (file format — PDF, DOCX, HTML,
Notion, Box), see [transform-registry.md](../../skills/bmad-agent-texas/references/transform-registry.md) instead. **Do not** retrofit a locator-shape
provider to use `RetrievalIntent` — that is anti-pattern #3 from Story 27-0.

## 1. Understanding your provider's API surface

Before writing code, resolve three gates (these are the "Pre-Development
Gates" that Story 27-2 formalized; every retrieval-provider story should
resolve them at the green-light round):

| Gate | Question | Resolution options |
|------|----------|--------------------|
| **PDG-1 auth** | How do tests get credentials? | (a) live creds from `.env`, cassette-recorded once; (b) **synthetic JSON fixtures only** (preferred v1 — no CI credential bleed) |
| **PDG-2 tool catalog** | Does the MCP tool catalog exist at test-authoring time? | (a) live `list_tools()` ping IF creds are available; (b) **inferred from public API docs**, first live run is the moment-of-truth |
| **PDG-3 refinement** | Is `drop_filters_in_order` sufficient, or do we need custom strategies? | (a) **`drop_filters_in_order` only** — YAGNI; promote via follow-on story if real data warrants; (b) custom strategies baked in at this story's cost |

**Data-not-inference rule (AC-C.7):** any mapping that looks tempting to
compute via LLM (authority-tier lookup, venue classification, license
normalization) **must** be a lookup table. LLM-in-the-loop retrieval is
explicitly non-goal for v1; future LLM adapters require their own eval
framework.

## 2. Subclassing `RetrievalAdapter`

Create `skills/bmad-agent-texas/scripts/retrieval/<provider>_provider.py`.
Subclass `RetrievalAdapter` from `retrieval.base`:

```python
from typing import Any, ClassVar

from .base import RetrievalAdapter
from .contracts import AcceptanceCriteria, ProviderInfo, RetrievalIntent, TexasRow


class MyProvider(RetrievalAdapter):
    PROVIDER_INFO: ClassVar[ProviderInfo] = ProviderInfo(
        id="myprovider",
        shape="retrieval",
        status="ready",
        capabilities=["whatever-the-provider-uniquely-does"],
        auth_env_vars=["MYPROVIDER_API_KEY"],
        spec_ref="_bmad-output/implementation-artifacts/<story-id>.md",
        notes="One-line operator-facing summary.",
    )
    HONORED_CRITERIA: ClassVar[frozenset[str]] = frozenset({
        "date_range", "min_results", "exclude_ids",
    })
    # 7 abstract methods below.
```

Notes:
- `id` is the string operators use in `provider_hints: [{provider: "<id>"}]`.
- `status="ready"` once the adapter ships; `"stub"` before that. Backlog
  placeholders in `provider_directory.py` are superseded by live
  registrations with the same id.
- `__init_subclass__` auto-registers the class in the provider directory on
  import — no explicit registration call needed. The placeholder (if any)
  remains as a fallback so `list_providers()` never silently loses a row.

## 3. The seven abstract methods

| Method | Responsibility | Determinism requirement |
|--------|----------------|-------------------------|
| `formulate_query(intent)` | Translate `intent.intent` + hint `params` into your provider's query DSL | **Byte-deterministic** — same input → same output across 100+ invocations |
| `execute(query)` | Fetch results via `MCPClient.call_tool(...)` or your own client | May raise; dispatcher wraps errors in `ProviderResult(acceptance_met=False)` |
| `apply_mechanical(raw, criteria)` | Deterministic-predicate filters (date range, exclude IDs, license) | Pure function |
| `apply_provider_scored(raw, criteria)` | Provider-native-signal filters (authority tier, citation-count) | Pure function |
| `normalize(raw)` | Convert to canonical `TexasRow` list; provider-specifics under `provider_metadata.<id>` | Pure function |
| `refine(previous_query, previous_results, criteria)` | Return a **monotonically-looser** query or `None` when exhausted | Pure function of inputs |
| `identity_key(row)` | Canonical cross-validation identity (DOI, video ID, URL); `NotImplementedError` if unavailable | Pure function |

**Use `refinement_registry.drop_filters_in_order`** for `refine` unless you
have real-data evidence that custom strategies are needed. That function
takes an `order: list[str]` — supply your provider-specific
most-restrictive-first filter key list.

**`MCPClient` usage** (HTTP-MCP providers):

```python
from .mcp_client import MCPClient, MCPServerConfig

def _client(self) -> MCPClient:
    if self._mcp_client is None:
        self._mcp_client = MCPClient({
            self.PROVIDER_INFO.id: MCPServerConfig(
                url="https://mcp.example.ai/mcp",
                auth_env=["MYPROVIDER_USER", "MYPROVIDER_PASSWORD"],
                auth_style="basic",  # or "bearer"
            )
        })
    return self._mcp_client
```

Keep the client lazy — env var resolution happens at first `execute`, not
`__init__`. This keeps tests that construct the provider without creds
from raising at construction time.

## 4. Library-agnostic error surface (AC-C.2)

**The public surface of `MCPClient` hides `requests`.** Your adapter MUST NOT:

- import `requests.Response` or any `requests.*` exception types;
- receive or return `requests` objects at method boundaries;
- re-raise `requests.RequestException` subclasses.

Instead, propagate the MCP error taxonomy:

- `MCPAuthError` — 401 / 403 / missing env vars
- `MCPRateLimitError` — 429
- `MCPFetchError` — 5xx / timeout / connection / unparseable
- `MCPProtocolError` — JSON-RPC envelope carried an `error`

The dispatcher maps each to a `ProviderResult` with `acceptance_met=False`
and a `refinement_log` entry. **Regression test this:** copy
`test_scite_provider_exceptions_never_leak_transport_types` from
`tests/test_retrieval_scite_provider.py` for your adapter (AC-T.10 pattern).

Why the discipline matters: when the `mcp` PyPI package hits 1.0, we plan
to swap `MCPClient`'s internals to the official library. That swap is a
**single-file change** iff this module-prefix invariant holds across every
adapter.

## 5. Parametrizing the ABC-contract tests

**Do not copy** `tests/contracts/test_retrieval_adapter_base.py` into your
provider's test file. Instead, extend its `ADAPTER_FACTORIES` list with a
factory that returns your adapter's `AdapterHarness`:

```python
def _make_myprovider_harness() -> AdapterHarness:
    adapter = MyProvider()
    intent = RetrievalIntent(
        intent="canonical test intent",
        provider_hints=[ProviderHint(provider="myprovider")],
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    # Raw sample: the shape your execute() returns — use this in
    # apply_mechanical / normalize / quality_delta parametrized tests.
    raw_sample = [{"id": "id-1", ...}, {"id": "id-2", ...}]
    # A row whose identity_key is deterministically known for the parametrized check.
    known_row = TexasRow(
        source_id="fallback",
        provider="myprovider",
        provider_metadata={"myprovider": {"id": "known-id"}},
    )
    return AdapterHarness(
        adapter=adapter,
        intent=intent,
        raw_sample=raw_sample,
        known_identity_row=known_row,
        known_identity_value="known-id",
        expected_honored_keys={"date_range", "min_results"},
    )


ADAPTER_FACTORIES.append(("myprovider", _make_myprovider_harness))
```

Every parametrized base test (`test_adapter_formulate_query_deterministic`,
`test_adapter_identity_key_returns_known_string`, etc.) now runs for your
adapter automatically.

## 6. Provider-unit tests (atomic splits)

Create `tests/test_retrieval_<provider>_provider.py` with **one
assertion-cluster per test** (Murat MUST-FIX pattern from Story 27-2 green-light):

- Split `test_execute_happy_path` into `_calls_correct_tool_name`,
  `_passes_args_verbatim`, `_returns_parsed_list` — each a separate test.
- Split `test_normalize_populates_provider_metadata` by field-group — one
  atom per semantic cluster (identity-key extraction, classification
  truncation, authority-tier derivation, paywall degradation).
- Use `responses.RequestsMock()` **per test** (context manager), not a
  module-level fixture. Module-level leaks are anti-pattern #8.
- Fixtures are plain-text JSON under
  `tests/fixtures/retrieval/<provider>/`; document provenance in
  `README.md` alongside them.

Count floor: ≥11 atomic units for an HTTP-MCP provider like scite;
non-HTTP providers may run leaner (image providers, deterministic API
clients). Set a **test-count floor**, not a range — floors regress-gate;
ranges drift.

## 7. Refinement strategy

Most providers can ship with `drop_filters_in_order` and a
provider-specific key-order list. Test monotonic looseness + exhaustion
(AC-T.3 pattern):

```python
def test_myprovider_refine_monotonic_looseness():
    # Start with all honored filters set; iterate refine(); assert each
    # returned query has a strict subset of the previous filters.

def test_myprovider_refine_exhausts_and_returns_none():
    # After len(REFINEMENT_KEY_ORDER) iterations, refine() returns None.
```

Promote to custom strategies only when real-run data shows exhaustion
clustering on the drop-in-order tail — this is what the "follow-on
refinement-hardening" tickets in green-light round 1 exist for.

## 8. Writing the dev-story + green-light round

Author your story under `_bmad-output/implementation-artifacts/<id>.md`
following Story 27-2's template:

- **Pre-Development Gate** table resolving PDG-1/2/3.
- **Acceptance Criteria** in three sections: Behavioral (AC-B), Test
  (AC-T), Contract Pinning (AC-C).
- **Anti-pattern Guardrails** section citing the carve-outs from Story
  27-0 that apply to your shape (most commonly #3 no-locator-refactor and
  #10 identity-key-for-cross-validate).
- **Tasks / Subtasks** in skeleton-first order: stub → wiring → guts →
  tests → docs → closure. Skeleton-first catches dispatcher-wiring bugs
  before provider-specifics pile on.
- **File Impact** table with estimated line counts per file.
- Run **bmad-party-mode** for the green-light round; apply MUST-FIX; run
  it again for GREEN confirmation. Document the vote record + applied
  patches at the bottom of the spec.

## 9. Dispatcher-wiring (usually unchanged)

`run_wrangler.py` routes retrieval-shape directives through
`retrieval.dispatcher.dispatch()`. You almost never need to touch
`run_wrangler.py` — your adapter's `PROVIDER_INFO` registration is enough
for the dispatcher's factory to resolve you. The exception: if your
provider introduces a new **acceptance-criteria key** the dispatcher needs
to gate on, consider whether it belongs in `declare_honored_criteria`
first, or as a new mechanical predicate the dispatcher evaluates
(`min_results` is currently the only one).

## 10. Documentation — where things land

- **Your adapter's per-provider metadata fields** → document in
  `skills/bmad-agent-texas/references/extraction-report-schema.md` under
  the `## Provider Metadata Sub-objects` H2 (the single source of truth
  for `provider_metadata.<id>` shapes).
- **Operator-facing signal summary** → add a "For Tracy" / "For operators"
  subsection to
  `skills/bmad-agent-texas/references/retrieval-contract.md` — pointer-only,
  no duplicate schema tables.
- **Provider-specific story** → stays under `_bmad-output/`.
- **Recipe-4 stub** → in `docs/dev-guide.md` §Extension Guide already
  points here; no extra prose needed unless your provider introduces a
  genuinely new pattern (new auth scheme, new transport, new refinement
  algorithm).

## 11. Anti-patterns (learned-in-blood)

1. **Locator-shape refactor.** Do not retrofit DOCX / PDF / HTML / Notion
   / Box / Playwright to use `RetrievalIntent`. They stay on the legacy
   `_fetch_source` path. The dispatcher-wiring cascade in Story 27-2 is
   an **upstream routing concern** at the wrangler's dispatch cap — not a
   license to open `source_wrangler_operations.py`.
2. **Stateful mocks.** No `MagicMock.return_value = [1, 2]` sequences.
   Pre-script deterministic response dicts / fixtures (Model A). A
   `responses.RequestsMock()` per test + static JSON files is the
   pattern.
3. **Silent drop on unknown criteria.** Every acceptance-criteria key
   your adapter does NOT honor must appear in
   `declare_honored_criteria()`. The dispatcher compares against this set
   and logs a `refinement_log` entry for each unknown key.
4. **Non-monotonic refinement.** Refinement must NEVER tighten. Each
   `refine()` call drops a filter, widens a date range, or lowers a
   count-floor. Returning `None` is always safer than
   returning-something-narrower.
5. **Semantic scoring in Texas.** `acceptance_criteria.semantic_deferred`
   surfaces unchanged to Tracy. Texas does not evaluate sentence-level
   relevance — that is Tracy's post-fetch semantic pass.
6. **Library types on the public surface.** See §4. Any
   `requests.Response` on a method signature fails the Option-X migration
   discipline.

## 12. Regenerating the legacy-DOCX golden baseline

If the legacy locator-shape path's output shape legitimately changes
(e.g., a new field is added to `SourceOutcome`), the golden baseline
under `tests/fixtures/regression/legacy_docx_baseline/` needs to be
regenerated. **Regeneration is gated — by design, a default `pytest`
invocation cannot silently rebase the baseline** (Murat MH-1, Story 27-2
implementation review).

**Procedure:**

1. Delete the stale goldens:
   - `tests/fixtures/regression/legacy_docx_baseline/extraction_report_scrubbed.yaml`
   - `tests/fixtures/regression/legacy_docx_baseline/exception_class.json`
2. Re-run the parity tests **with the `REGENERATE_GOLDENS=1` env var**:

   ```bash
   REGENERATE_GOLDENS=1 pytest tests/test_run_wrangler_legacy_docx_parity.py
   ```

   Without the env var, a missing golden fails the test with an
   explicit error naming this procedure. Opt-in regeneration ensures
   every baseline rebase is an intentional, reviewable act.
3. **Inspect the new goldens** — `git diff` the fixture directory. If
   the change is larger than you expected, the scrubber may have missed
   a new run-specific token or the legacy path has drifted in a way
   that needs investigation.
4. **Commit the new goldens alongside the code change**, with a commit
   message that names:
   - the field addition / removal (or scrubber regex update) driving it,
   - who reviewed the new baseline (Murat or designated Test reviewer —
     this is a regression-gate change, not a mechanical refresh).

Silent regeneration via default `pytest` is impossible by design; the
test-suite regression proof only holds if a human reviewer countersigns
every baseline rebase.

## Living references

- **Worked example:** `skills/bmad-agent-texas/scripts/retrieval/scite_provider.py`
- **Base ABC:** `skills/bmad-agent-texas/scripts/retrieval/base.py`
- **Pydantic contracts:** `skills/bmad-agent-texas/scripts/retrieval/contracts.py`
- **MCP client:** `skills/bmad-agent-texas/scripts/retrieval/mcp_client.py`
- **Dispatcher:** `skills/bmad-agent-texas/scripts/retrieval/dispatcher.py`
- **Provider directory:** `skills/bmad-agent-texas/scripts/retrieval/provider_directory.py`
- **Refinement registry:** `skills/bmad-agent-texas/scripts/retrieval/refinement_registry.py`
- **ABC contract tests (parametrization target):** `tests/contracts/test_retrieval_adapter_base.py`
- **Retrieval contract doc (operator-facing):** `skills/bmad-agent-texas/references/retrieval-contract.md`
- **Extraction-report schema (provider_metadata schema home):** `skills/bmad-agent-texas/references/extraction-report-schema.md`
