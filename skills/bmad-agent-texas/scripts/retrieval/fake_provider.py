"""`FakeProvider` — reference adapter for contract + dispatcher tests (Story 27-0).

Pre-scripted, deterministic, zero-network. Exists for AC-T.2 (ABC inheritance
tests), AC-T.3 (dispatcher iteration tests via deterministic sequence
fixtures), and AC-T.4 (cross-validation merger tests).

Design principle — deterministic sequence fixtures, NOT stateful mocks
(anti-pattern #2, Murat's flakiness guard): each test pre-scripts a
`query_to_result` map from query-strings to row lists. `formulate_query` is
a pure function of the intent; `refine` is a pure function of the previous
query + iteration count (embedded in the query string). No internal cursors,
no clock dependence, no randomness.

Public tests import `FakeProvider` via
  from retrieval.fake_provider import FakeProvider, make_row

The constructor is `provider_id`-parameterized so a single test can stand up
two or more distinct `FakeProvider` instances (e.g., "scite-like" +
"consensus-like") for cross-validation merger coverage.
"""

from typing import Any, ClassVar

from .base import RetrievalAdapter
from .contracts import (
    AcceptanceCriteria,
    ProviderInfo,
    RetrievalIntent,
    TexasRow,
)


def make_row(
    source_id: str,
    *,
    provider: str = "fake",
    title: str = "",
    body: str = "",
    authority_tier: str | None = None,
    **extra: Any,
) -> TexasRow:
    """Build a `TexasRow` with sensible defaults for fixture construction."""
    return TexasRow(
        source_id=source_id,
        provider=provider,
        title=title or source_id,
        body=body,
        authority_tier=authority_tier,
        provider_metadata=extra,
    )


class FakeProvider(RetrievalAdapter):
    """Reference retrieval adapter for 27-0 foundation tests.

    Subclasses of `FakeProvider` auto-register under distinct provider IDs
    so multiple fakes can coexist in cross-validation tests. For ad-hoc
    tests use `make_fake_provider_class(provider_id, rows_by_query)` below
    to spin a fresh subclass without polluting the main registry.
    """

    PROVIDER_INFO: ClassVar[ProviderInfo] = ProviderInfo(
        id="fake",
        shape="retrieval",
        status="stub",
        capabilities=["contract-test-fixture", "deterministic-sequence"],
        auth_env_vars=[],
        spec_ref="_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md",
        notes="Reference adapter for 27-0 tests. Never ships to production; no network.",
    )

    HONORED_CRITERIA: ClassVar[frozenset[str]] = frozenset(
        {"min_results", "date_range", "authority_tier_min"}
    )

    def __init__(
        self,
        rows_by_query: dict[str, list[TexasRow]] | None = None,
        *,
        provider_name: str | None = None,
    ) -> None:
        self._rows_by_query: dict[str, list[TexasRow]] = rows_by_query or {}
        self._provider_name = provider_name or self.PROVIDER_INFO.id

    def formulate_query(self, intent: RetrievalIntent) -> str:
        """Deterministic initial query: `initial:<intent>`.

        Byte-identical across invocations with the same intent (AC-T.2 self-test).
        """
        return f"initial:{intent.intent}"

    def execute(self, query: str) -> list[TexasRow]:
        """Look up pre-scripted rows for the query; empty list if unknown."""
        return list(self._rows_by_query.get(query, []))

    def apply_mechanical(
        self, results: list[TexasRow], criteria: dict[str, Any]
    ) -> list[TexasRow]:
        """Deterministic predicate filter.

        Supported keys:
          - `min_results`: passthrough (dispatcher evaluates count post-filter)
          - `date_range`: [start, end] YYYY-MM-DD strings; row.date within
          - `exclude_ids`: list of source_ids to drop
        """
        out = list(results)
        date_range = criteria.get("date_range")
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start, end = date_range
            out = [
                r for r in out
                if r.date is None or (start <= r.date <= end)
            ]
        exclude = criteria.get("exclude_ids") or []
        if exclude:
            out = [r for r in out if r.source_id not in set(exclude)]
        return out

    def apply_provider_scored(
        self, results: list[TexasRow], criteria: dict[str, Any]
    ) -> list[TexasRow]:
        """Provider-scored filter: authority_tier minimum."""
        out = list(results)
        tier_min = criteria.get("authority_tier_min")
        if tier_min is not None:
            tier_rank = {"peer-reviewed": 3, "preprint": 2, "web": 1, None: 0}
            min_rank = tier_rank.get(tier_min, 0)
            out = [
                r for r in out
                if tier_rank.get(r.authority_tier, 0) >= min_rank
            ]
        return out

    def normalize(self, results: list[TexasRow]) -> list[TexasRow]:
        """Pass-through — FakeProvider already returns canonical rows."""
        return [
            r.model_copy(update={"provider": self._provider_name})
            for r in results
        ]

    def refine(
        self,
        previous_query: str,
        previous_results: list[TexasRow],
        criteria: AcceptanceCriteria,
    ) -> str | None:
        """Monotonically-loosening refinement: `refined(N):<intent>`.

        The iteration counter lives in the query string itself — this keeps
        refinement a pure function of the previous query, with no internal
        cursor state. Returns None after iteration 5 to bound test runs.
        """
        if previous_query.startswith("initial:"):
            intent_body = previous_query[len("initial:"):]
            return f"refined(1):{intent_body}"
        if previous_query.startswith("refined("):
            close_idx = previous_query.index(")")
            n = int(previous_query[len("refined("):close_idx])
            if n >= 5:
                return None
            intent_body = previous_query[close_idx + 2:]
            return f"refined({n + 1}):{intent_body}"
        return None

    def identity_key(self, row: TexasRow) -> str:
        """Identity is `source_id` for FakeProvider (doubles as DOI-like key)."""
        return row.source_id

    def declare_honored_criteria(self) -> set[str]:
        return set(self.HONORED_CRITERIA)


def make_fake_provider_class(
    provider_id: str,
    rows_by_query: dict[str, list[TexasRow]] | None = None,
    *,
    honored: set[str] | None = None,
) -> type[FakeProvider]:
    """Build a uniquely-named `FakeProvider` subclass for tests.

    Auto-registers under `provider_id`. Call `reset_adapter_registry()` in
    test teardown if a fresh slate is needed. The returned class is a real
    subclass (not an instance) so each caller instantiates it with whatever
    fixture data the test requires.
    """
    info = ProviderInfo(
        id=provider_id,
        shape="retrieval",
        status="stub",
        capabilities=["contract-test-fixture"],
        auth_env_vars=[],
        spec_ref=None,
        notes=f"Ad-hoc FakeProvider subclass '{provider_id}' for test use only.",
    )
    honored_frozen = frozenset(honored or FakeProvider.HONORED_CRITERIA)

    class _AdHocFakeProvider(FakeProvider):
        PROVIDER_INFO: ClassVar[ProviderInfo] = info
        HONORED_CRITERIA: ClassVar[frozenset[str]] = honored_frozen

        def __init__(
            self,
            rows: dict[str, list[TexasRow]] | None = None,
        ) -> None:
            super().__init__(
                rows_by_query=rows if rows is not None else rows_by_query,
                provider_name=provider_id,
            )

    _AdHocFakeProvider.__name__ = f"FakeProvider_{provider_id}"
    _AdHocFakeProvider.__qualname__ = _AdHocFakeProvider.__name__
    return _AdHocFakeProvider


__all__ = [
    "FakeProvider",
    "make_fake_provider_class",
    "make_row",
]
