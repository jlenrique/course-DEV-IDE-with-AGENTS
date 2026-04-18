"""AC-T.3 — Dispatcher iteration-loop tests with deterministic sequence fixtures.

Murat's test-flakiness concern is resolved HERE: each test pre-scripts the
FakeProvider's rows_by_query map. The dispatcher's loop becomes a pure
function over the pre-scripted sequence — no stateful mocks, no async, no
concurrency, no timing dependence.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from retrieval import (
    AcceptanceCriteria,
    AdapterFactory,
    ProviderHint,
    ProviderResult,
    RetrievalIntent,
    dispatch,
)
from retrieval.fake_provider import FakeProvider, make_row

FIXTURES = Path(__file__).parent / "fixtures" / "retrieval" / "fake-responses"


def _load_rows(name: str) -> dict[str, list]:
    raw = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return {
        q: [make_row(**row) for row in rows]
        for q, rows in raw["rows_by_query"].items()
    }


@pytest.fixture
def happy_path_adapter() -> FakeProvider:
    return FakeProvider(rows_by_query=_load_rows("happy_path.json"))


def test_dispatcher_single_shot_meets_criteria(happy_path_adapter: FakeProvider) -> None:
    intent = RetrievalIntent(
        intent="sleep hygiene studies",
        provider_hints=[ProviderHint(provider="fake")],
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 3}),
    )
    r = dispatch(intent, factory=AdapterFactory({"fake": happy_path_adapter}))
    assert isinstance(r, ProviderResult)
    assert r.acceptance_met is True
    assert r.iterations_used == 1
    assert len(r.rows) == 3


def test_dispatcher_multi_iter_meets_criteria(happy_path_adapter: FakeProvider) -> None:
    intent = RetrievalIntent(
        intent="sleep hygiene studies",
        provider_hints=[ProviderHint(provider="fake")],
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 5}),
    )
    r = dispatch(intent, factory=AdapterFactory({"fake": happy_path_adapter}))
    assert r.acceptance_met is True
    assert r.iterations_used == 2


def test_dispatcher_budget_exhausted_returns_acceptance_false(
    happy_path_adapter: FakeProvider,
) -> None:
    intent = RetrievalIntent(
        intent="sleep hygiene studies",
        provider_hints=[ProviderHint(provider="fake")],
        iteration_budget=2,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 100}),
    )
    r = dispatch(intent, factory=AdapterFactory({"fake": happy_path_adapter}))
    assert r.acceptance_met is False
    reasons = {e.reason for e in r.refinement_log}
    assert "budget_exhausted" in reasons


def test_dispatcher_non_improvement_aborts_on_convergence_required() -> None:
    adapter = FakeProvider(
        rows_by_query={
            "initial:x": [make_row("doi:1"), make_row("doi:2")],
            "refined(1):x": [make_row("doi:1")],  # shrinks → quality_delta < 0
        }
    )
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="fake")],
        iteration_budget=5,
        convergence_required=True,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 100}),
    )
    r = dispatch(intent, factory=AdapterFactory({"fake": adapter}))
    reasons = {e.reason for e in r.refinement_log}
    assert "non_improvement_abort" in reasons


def test_dispatcher_refine_returning_none_exits_early() -> None:
    from retrieval.contracts import ProviderInfo

    class _RefineNone(FakeProvider):
        PROVIDER_INFO = ProviderInfo(
            id="_refine_none", shape="retrieval", status="stub"
        )

        def refine(self, previous_query, previous_results, criteria):
            return None

    adapter = _RefineNone(
        rows_by_query={"initial:x": [make_row("doi:1")]},
        provider_name="_refine_none",
    )
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="_refine_none")],
        iteration_budget=5,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 100}),
    )
    r = dispatch(intent, factory=AdapterFactory({"_refine_none": adapter}))
    reasons = {e.reason for e in r.refinement_log}
    assert "refine_returned_none" in reasons


def test_dispatcher_budget_boundary_single_iteration() -> None:
    """AC-T.3 Murat add — edge between single-shot-meets and budget-exhausted."""
    adapter = FakeProvider(
        rows_by_query={"initial:x": [make_row("doi:1")]}
    )
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="fake")],
        iteration_budget=1,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    r = dispatch(intent, factory=AdapterFactory({"fake": adapter}))
    assert r.iterations_used == 1
    assert r.acceptance_met is True


def test_dispatcher_logs_unknown_criterion_key() -> None:
    """AC-B.2 strengthened — unknown keys do NOT silently drop."""
    adapter = FakeProvider(rows_by_query={"initial:x": [make_row("doi:1")]})
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="fake")],
        acceptance_criteria=AcceptanceCriteria(
            mechanical={"min_results": 1, "bogus_key": "value"}
        ),
    )
    r = dispatch(intent, factory=AdapterFactory({"fake": adapter}))
    logged_keys = {e.criterion_key for e in r.refinement_log if e.criterion_key}
    assert "bogus_key" in logged_keys


# -----------------------------------------------------------------------------
# Code-review MUST-FIX regression guards (2026-04-18)
# -----------------------------------------------------------------------------


def test_dispatcher_rejects_min_results_zero() -> None:
    """MUST-FIX CR-2: min_results=0 is the 'trivially met' footgun; must raise."""
    from retrieval.dispatcher import DispatchError

    adapter = FakeProvider(rows_by_query={"initial:x": []})
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="fake")],
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 0}),
    )
    with pytest.raises(DispatchError, match="must be >= 1"):
        dispatch(intent, factory=AdapterFactory({"fake": adapter}))


def test_dispatcher_rejects_min_results_non_integer() -> None:
    """MUST-FIX M-5: non-integer min_results should raise, NOT silently fall back."""
    from retrieval.dispatcher import DispatchError

    adapter = FakeProvider(rows_by_query={"initial:x": [make_row("doi:1")]})
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="fake")],
        acceptance_criteria=AcceptanceCriteria(
            mechanical={"min_results": "three"}
        ),
    )
    with pytest.raises(DispatchError, match="must be a positive integer"):
        dispatch(intent, factory=AdapterFactory({"fake": adapter}))


def test_dispatcher_budget_1_unmet_uses_distinct_log_reason() -> None:
    """MUST-FIX CR-1 / bh-m1: budget=1 unmet should NOT log 'budget_exhausted'.

    Before the fix, the while/else clause fired on budget=1 even though no
    refinement was attempted. After the fix, the degenerate case emits a
    distinct reason that names the real cause.
    """
    adapter = FakeProvider(rows_by_query={"initial:x": [make_row("doi:1")]})
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="fake")],
        iteration_budget=1,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 99}),
    )
    r = dispatch(intent, factory=AdapterFactory({"fake": adapter}))
    reasons = {e.reason for e in r.refinement_log}
    assert "single_shot_unmet_budget_too_small_to_refine" in reasons
    assert "budget_exhausted" not in reasons
    assert r.acceptance_met is False
    assert r.iterations_used == 1


def test_dispatcher_non_improvement_preserves_better_prior_result() -> None:
    """MUST-FIX bh-m2: abort-on-non-improvement commits to the BETTER
    (pre-regression) data set, not the worse follow-up."""
    adapter = FakeProvider(
        rows_by_query={
            "initial:x": [make_row("doi:1"), make_row("doi:2"), make_row("doi:3")],
            "refined(1):x": [make_row("doi:1")],  # shrinks → non-improvement
        }
    )
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="fake")],
        iteration_budget=5,
        convergence_required=True,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 99}),
    )
    r = dispatch(intent, factory=AdapterFactory({"fake": adapter}))
    # Must keep the 3-row pre-regression result, NOT the 1-row shrunken one.
    assert len(r.rows) == 3
    reasons = {e.reason for e in r.refinement_log}
    assert "non_improvement_abort" in reasons


# -----------------------------------------------------------------------------
# AC-T.4 — SciteProvider dispatcher integration smoke (Story 27-2)
# -----------------------------------------------------------------------------


def test_dispatcher_scite_single_provider_integration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC-T.4 — dispatch(scite_intent) with `responses`-mocked MCP produces a
    populated `ProviderResult`.

    Exercises the full single-provider dispatch path — formulate_query → execute
    (via MCPClient, mocked at the HTTP layer by `responses`) → apply_mechanical
    → apply_provider_scored → acceptance check → normalize → ProviderResult.
    """
    import responses as _responses
    from retrieval.scite_provider import SCITE_MCP_URL, SciteProvider

    from tests._helpers.mcp_fixtures import jsonrpc_response

    monkeypatch.setenv("SCITE_USER_NAME", "test-user")
    monkeypatch.setenv("SCITE_PASSWORD", "test-pass")

    fixture_path = Path(__file__).parent / "fixtures" / "retrieval" / "scite" / "search_happy.json"
    search_result = json.loads(fixture_path.read_text(encoding="utf-8"))

    adapter = SciteProvider()
    intent = RetrievalIntent(
        intent="sleep hygiene studies",
        provider_hints=[ProviderHint(provider="scite")],
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )

    with _responses.RequestsMock() as rsps:
        rsps.post(SCITE_MCP_URL, json=jsonrpc_response(result=search_result))
        r = dispatch(intent, factory=AdapterFactory({"scite": adapter}))

    assert isinstance(r, ProviderResult)
    assert r.provider == "scite"
    assert r.acceptance_met is True
    assert r.iterations_used == 1
    assert len(r.rows) == 3
    # Every row must have provider_metadata.scite populated (AC-C.4 opacity).
    for row in r.rows:
        assert "scite" in row.provider_metadata
        assert "doi" in row.provider_metadata["scite"]
