"""AC-T.2 — `RetrievalAdapter` ABC contract tests.

Parametrized over `FakeProvider` as the reference adapter. Explicit inheritance
target for 27-2 / 27-2.5 / future retrieval adapters — they must import and
parametrize against this module (NOT reimplement the base contract).

Atomic test splits per Amelia green-light: contract-shape / error-propagation /
provider_hints-validation tests live separately.
"""

from __future__ import annotations

import pytest
from retrieval.contracts import (
    AcceptanceCriteria,
    ProviderHint,
    RetrievalIntent,
)
from retrieval.fake_provider import FakeProvider, make_row
from retrieval.provider_directory import reset_adapter_registry


@pytest.fixture
def intent() -> RetrievalIntent:
    return RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="fake")],
        acceptance_criteria=AcceptanceCriteria(
            mechanical={"min_results": 1}
        ),
    )


@pytest.fixture
def adapter() -> FakeProvider:
    return FakeProvider(
        rows_by_query={
            "initial:x": [make_row("doi:a"), make_row("doi:b")],
            "refined(1):x": [
                make_row("doi:a"),
                make_row("doi:b"),
                make_row("doi:c"),
            ],
        }
    )


def test_fake_provider_formulate_query_deterministic(
    adapter: FakeProvider, intent: RetrievalIntent
) -> None:
    """AC-T.2 FakeProvider determinism self-test (Murat add)."""
    queries = {adapter.formulate_query(intent) for _ in range(100)}
    assert len(queries) == 1, (
        "FakeProvider.formulate_query must be byte-deterministic across "
        "invocations with the same intent"
    )


def test_adapter_base_apply_mechanical_deterministic(adapter: FakeProvider) -> None:
    """Same input → same output across calls."""
    results = adapter.execute(adapter.formulate_query(
        RetrievalIntent(intent="x", provider_hints=[ProviderHint(provider="fake")])
    ))
    out1 = adapter.apply_mechanical(results, {"exclude_ids": ["doi:b"]})
    out2 = adapter.apply_mechanical(results, {"exclude_ids": ["doi:b"]})
    assert [r.source_id for r in out1] == [r.source_id for r in out2]
    assert "doi:b" not in {r.source_id for r in out1}


def test_adapter_base_refine_monotonic_looseness(
    adapter: FakeProvider, intent: RetrievalIntent
) -> None:
    """Each refinement call must broaden — never re-tighten."""
    q0 = adapter.formulate_query(intent)
    q1 = adapter.refine(q0, [], intent.acceptance_criteria)
    q2 = adapter.refine(q1, [], intent.acceptance_criteria)
    assert q1 is not None and q1 != q0
    assert q2 is not None and q2 != q1


def test_adapter_base_quality_delta_monotonic(adapter: FakeProvider) -> None:
    """Default delta: >0 on growth, 0 on flat, <0 on shrink."""
    prev = [make_row("a")]
    more = [make_row("a"), make_row("b")]
    less: list = []
    assert adapter.quality_delta(prev, more) > 0
    assert adapter.quality_delta(prev, prev) == 0
    assert adapter.quality_delta(prev, less) < 0


def test_adapter_base_declare_honored_criteria_introspection(
    adapter: FakeProvider,
) -> None:
    """Adapters must enumerate the criteria keys they evaluate."""
    honored = adapter.declare_honored_criteria()
    assert isinstance(honored, set)
    # FakeProvider honors these per its HONORED_CRITERIA ClassVar
    assert "min_results" in honored
    assert "date_range" in honored
    assert "authority_tier_min" in honored


def test_adapter_base_identity_key_required_for_cross_val(
    adapter: FakeProvider,
) -> None:
    """Every real adapter must implement identity_key (anti-pattern #10)."""
    row = make_row("doi:xyz")
    key = adapter.identity_key(row)
    assert isinstance(key, str) and key == "doi:xyz"


def test_adapter_base_normalize_returns_canonical_rows(
    adapter: FakeProvider,
) -> None:
    """normalize() emits TexasRow instances with provider field set."""
    raw = [make_row("doi:a"), make_row("doi:b")]
    out = adapter.normalize(raw)
    assert len(out) == 2
    assert all(r.provider == "fake" for r in out)


def test_adapter_auto_registers_in_directory() -> None:
    """AC-B.8: PROVIDER_INFO auto-registers via __init_subclass__."""
    from retrieval.provider_directory import list_providers

    # FakeProvider.PROVIDER_INFO is 'fake' — registered on import
    ids = {p.id for p in list_providers()}
    assert "fake" in ids
    reset_adapter_registry()
    # After reset, live registrations clear but static placeholders remain
    ids = {p.id for p in list_providers()}
    assert "fake" not in ids
    assert "openai_chatgpt" in ids, "backlog placeholders must survive reset"
