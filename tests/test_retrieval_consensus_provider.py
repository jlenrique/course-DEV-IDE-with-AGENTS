"""ConsensusProvider unit tests (Story 27-2.5).

Atomic tests for query formulation, MCP execution, normalization/identity,
refinement monotonicity, and adapter exception-boundary guards.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import pytest
import responses
from retrieval import (
    AcceptanceCriteria,
    MCPAuthError,
    ProviderHint,
    RetrievalIntent,
)
from retrieval.consensus_provider import (
    CONSENSUS_MCP_URL,
    CONSENSUS_REFINEMENT_KEY_ORDER,
    ConsensusProvider,
)

from tests._helpers.mcp_fixtures import jsonrpc_response

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "retrieval" / "consensus"


def _load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _consensus_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONSENSUS_API_KEY", "consensus-token")
    monkeypatch.delenv("CONSENSUS_USER_NAME", raising=False)
    monkeypatch.delenv("CONSENSUS_PASSWORD", raising=False)


def _intent_search(
    *, params: dict[str, Any] | None = None, **criteria: Any
) -> RetrievalIntent:
    return RetrievalIntent(
        intent="sleep hygiene adults",
        provider_hints=[ProviderHint(provider="consensus", params=params or {})],
        acceptance_criteria=AcceptanceCriteria(
            mechanical=criteria.get("mechanical", {}),
            provider_scored=criteria.get("provider_scored", {}),
        ),
    )


def _intent_doi(doi: str) -> RetrievalIntent:
    return RetrievalIntent(
        intent=doi,
        provider_hints=[
            ProviderHint(provider="consensus", params={"mode": "paper", "doi": doi})
        ],
        kind="direct_ref",
    )


def test_consensus_formulate_query_deterministic() -> None:
    provider = ConsensusProvider()
    intent = _intent_search(
        mechanical={"min_results": 5, "date_range": ["2020-01-01", "2026-12-31"]},
        provider_scored={"consensus_score_min": 0.7},
    )
    serialized = {
        json.dumps(provider.formulate_query(intent), sort_keys=True)
        for _ in range(100)
    }
    assert len(serialized) == 1


def test_consensus_formulate_query_search_mode() -> None:
    provider = ConsensusProvider()
    intent = _intent_search(
        mechanical={"min_results": 4},
        provider_scored={"study_design_allow": ["meta-analysis"]},
    )
    query = provider.formulate_query(intent)
    assert query["mode"] == "search"
    assert query["query"] == "sleep hygiene adults"
    assert query["max_results"] == 4
    assert query["filters"]["study_design_allow"] == ["meta-analysis"]


def test_consensus_formulate_query_doi_mode() -> None:
    provider = ConsensusProvider()
    intent = _intent_doi("10.1000/consensus-paper")
    query = provider.formulate_query(intent)
    assert query == {"mode": "paper", "doi": "10.1000/consensus-paper"}


def test_consensus_execute_calls_correct_tool_name() -> None:
    provider = ConsensusProvider()
    query = provider.formulate_query(_intent_search(mechanical={"min_results": 1}))
    with responses.RequestsMock() as rsps:
        rsps.post(
            CONSENSUS_MCP_URL,
            json=jsonrpc_response(result=_load_fixture("search_happy.json")),
        )
        provider.execute(query)
        body = json.loads(rsps.calls[0].request.body)
        assert body["method"] == "tools/call"
        assert body["params"]["name"] == "search"


def test_consensus_execute_passes_bearer_header() -> None:
    provider = ConsensusProvider()
    query = provider.formulate_query(_intent_search(mechanical={"min_results": 1}))
    with responses.RequestsMock() as rsps:
        rsps.post(
            CONSENSUS_MCP_URL,
            json=jsonrpc_response(result=_load_fixture("search_happy.json")),
        )
        provider.execute(query)
        header = rsps.calls[0].request.headers.get("Authorization")
        assert header == "Bearer consensus-token"


def test_consensus_execute_passes_basic_header_when_api_key_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CONSENSUS_API_KEY", raising=False)
    monkeypatch.setenv("CONSENSUS_USER_NAME", "consensus-user")
    monkeypatch.setenv("CONSENSUS_PASSWORD", "consensus-pass")

    provider = ConsensusProvider()
    query = provider.formulate_query(_intent_search(mechanical={"min_results": 1}))
    with responses.RequestsMock() as rsps:
        rsps.post(
            CONSENSUS_MCP_URL,
            json=jsonrpc_response(result=_load_fixture("search_happy.json")),
        )
        provider.execute(query)
        header = rsps.calls[0].request.headers.get("Authorization")

    assert header is not None and header.startswith("Basic ")
    token = header.split(" ", 1)[1]
    decoded = base64.b64decode(token.encode("utf-8")).decode("utf-8")
    assert decoded == "consensus-user:consensus-pass"


def test_consensus_execute_returns_parsed_list() -> None:
    provider = ConsensusProvider()
    query = provider.formulate_query(_intent_search(mechanical={"min_results": 1}))
    with responses.RequestsMock() as rsps:
        rsps.post(
            CONSENSUS_MCP_URL,
            json=jsonrpc_response(result=_load_fixture("search_happy.json")),
        )
        results = provider.execute(query)
    assert isinstance(results, list)
    assert len(results) == 3
    assert "doi" in results[0]


def test_consensus_execute_paper_mode_calls_correct_tool_name() -> None:
    provider = ConsensusProvider()
    query = provider.formulate_query(_intent_doi("10.1000/consensus-paper"))
    with responses.RequestsMock() as rsps:
        rsps.post(
            CONSENSUS_MCP_URL,
            json=jsonrpc_response(result=_load_fixture("paper_metadata_happy.json")),
        )
        results = provider.execute(query)
        body = json.loads(rsps.calls[0].request.body)

    assert body["method"] == "tools/call"
    assert body["params"]["name"] == "paper_metadata"
    assert body["params"]["arguments"] == {"doi": "10.1000/consensus-paper"}
    assert len(results) == 1
    assert results[0]["doi"] == "10.1000/consensus-paper"


def test_consensus_formulate_query_paper_mode_rejects_empty_doi() -> None:
    provider = ConsensusProvider()
    with pytest.raises(ValueError, match="non-empty DOI"):
        provider.formulate_query(_intent_doi("   "))


def test_consensus_execute_auth_error_propagates() -> None:
    provider = ConsensusProvider()
    query = provider.formulate_query(_intent_search(mechanical={"min_results": 1}))
    with responses.RequestsMock() as rsps:
        rsps.post(CONSENSUS_MCP_URL, status=401, body="unauthorized")
        with pytest.raises(MCPAuthError):
            provider.execute(query)


def test_consensus_normalize_extracts_doi_to_identity() -> None:
    provider = ConsensusProvider()
    fixture = _load_fixture("search_happy.json")
    rows = provider.normalize(fixture["papers"])
    first = rows[0]
    assert first.provider_metadata["consensus"]["doi"] == "10.1000/consensus-a"
    assert provider.identity_key(first) == "10.1000/consensus-a"


def test_consensus_normalize_populates_consensus_score() -> None:
    provider = ConsensusProvider()
    fixture = _load_fixture("search_happy.json")
    rows = provider.normalize(fixture["papers"])
    assert rows[0].provider_metadata["consensus"]["consensus_score"] == 0.88


def test_consensus_normalize_surfaces_study_design_tag() -> None:
    provider = ConsensusProvider()
    fixture = _load_fixture("search_with_study_design.json")
    rows = provider.normalize(fixture["papers"])
    assert rows[0].provider_metadata["consensus"]["study_design_tag"] == "meta-analysis"


def test_consensus_normalize_handles_missing_optional_fields() -> None:
    provider = ConsensusProvider()
    fixture = _load_fixture("search_missing_optional_fields.json")
    rows = provider.normalize(fixture["papers"])
    metadata = rows[0].provider_metadata["consensus"]
    assert metadata["sample_size"] is None
    assert metadata["evidence_strength"] is None
    assert "study_design_unknown" in metadata["known_losses"]


def test_consensus_normalize_assigns_unique_unknown_source_ids() -> None:
    provider = ConsensusProvider()
    rows = provider.normalize(
        [
            {"title": "Unknown A", "abstract": "a"},
            {"title": "Unknown B", "abstract": "b"},
        ]
    )
    assert rows[0].source_id != rows[1].source_id


def test_consensus_normalize_skips_non_dict_rows() -> None:
    provider = ConsensusProvider()
    rows = provider.normalize([
        {"doi": "10.1000/ok", "title": "Valid", "abstract": "x"},
        None,
        "bad-row",
        7,
    ])
    assert len(rows) == 1
    assert rows[0].source_id == "10.1000/ok"


@pytest.mark.parametrize("excluded_id", ["10.1000/consensus-a", "cp-a"])
def test_consensus_apply_mechanical_exclude_ids_matches_any_identity(
    excluded_id: str,
) -> None:
    provider = ConsensusProvider()
    fixture = _load_fixture("search_happy.json")
    filtered = provider.apply_mechanical(
        fixture["papers"],
        {"exclude_ids": [excluded_id]},
    )

    assert len(filtered) == 2
    assert all(row.get("doi") != "10.1000/consensus-a" for row in filtered)
    assert all(row.get("consensus_paper_id") != "cp-a" for row in filtered)


def test_consensus_apply_mechanical_exclude_ids_normalizes_doi_token() -> None:
    provider = ConsensusProvider()
    fixture = _load_fixture("search_happy.json")
    filtered = provider.apply_mechanical(
        fixture["papers"],
        {"exclude_ids": [" 10.1000/CONSENSUS-A "]},
    )
    assert len(filtered) == 2
    assert all(row.get("doi") != "10.1000/consensus-a" for row in filtered)


def test_consensus_apply_mechanical_exclude_ids_matches_case_variant_fallback_id() -> None:
    provider = ConsensusProvider()
    fixture = _load_fixture("search_happy.json")
    filtered = provider.apply_mechanical(
        fixture["papers"],
        {"exclude_ids": ["CP-A"]},
    )
    assert len(filtered) == 2
    assert all(row.get("consensus_paper_id") != "cp-a" for row in filtered)


def test_consensus_apply_mechanical_ignores_non_dict_rows() -> None:
    provider = ConsensusProvider()
    filtered = provider.apply_mechanical(
        [
            {"doi": "10.1000/ok", "consensus_paper_id": "cp-ok"},
            None,
            "bad-row",
        ],
        {"exclude_ids": []},
    )
    assert filtered == [{"doi": "10.1000/ok", "consensus_paper_id": "cp-ok"}]


def test_consensus_identity_key_falls_back_to_consensus_paper_id_when_doi_missing() -> None:
    from retrieval import TexasRow

    provider = ConsensusProvider()
    row = TexasRow(
        source_id="fallback-src",
        provider="consensus",
        provider_metadata={"consensus": {"doi": "", "consensus_paper_id": "cp-preprint-1"}},
    )
    assert provider.identity_key(row) == "cp-preprint-1"


def test_consensus_identity_key_normalizes_doi_case_and_whitespace() -> None:
    from retrieval import TexasRow

    provider = ConsensusProvider()
    row = TexasRow(
        source_id="fallback-src",
        provider="consensus",
        provider_metadata={"consensus": {"doi": " 10.1000/ABC-XYZ "}},
    )
    assert provider.identity_key(row) == "10.1000/abc-xyz"


def test_consensus_identity_key_uses_fallback_when_doi_is_whitespace_only() -> None:
    from retrieval import TexasRow

    provider = ConsensusProvider()
    row = TexasRow(
        source_id="fallback-src",
        provider="consensus",
        provider_metadata={"consensus": {"doi": "   ", "consensus_paper_id": "cp-1"}},
    )
    assert provider.identity_key(row) == "cp-1"


def test_consensus_identity_key_raises_when_all_three_tiers_empty() -> None:
    from retrieval import TexasRow

    provider = ConsensusProvider()
    row = TexasRow.model_construct(
        source_id="",
        provider="consensus",
        provider_metadata={"consensus": {}},
    )
    with pytest.raises(NotImplementedError, match="no DOI"):
        provider.identity_key(row)


def test_consensus_refine_monotonic_looseness() -> None:
    provider = ConsensusProvider()
    criteria = AcceptanceCriteria(
        mechanical={"date_range": ["2020-01-01", "2026-12-31"]},
        provider_scored={
            "sample_size_min": 200,
            "consensus_score_min": 0.7,
            "study_design_allow": ["meta-analysis"],
        },
    )
    current = {
        "mode": "search",
        "query": "x",
        "filters": {
            "sample_size_min": 200,
            "consensus_score_min": 0.7,
            "study_design_allow": ["meta-analysis"],
            "date_range": ["2020-01-01", "2026-12-31"],
        },
    }
    for expected_drop in CONSENSUS_REFINEMENT_KEY_ORDER:
        before = set(current["filters"])
        nxt = provider.refine(current, [], criteria)
        assert nxt is not None
        dropped = before - set(nxt["filters"])
        assert dropped == {expected_drop}
        current = nxt
    assert provider.refine(current, [], criteria) is None


def test_consensus_provider_exceptions_never_leak_transport_types() -> None:
    provider = ConsensusProvider()
    query = provider.formulate_query(_intent_search(mechanical={"min_results": 1}))
    for status in (401, 429, 500, 400):
        with responses.RequestsMock() as rsps:
            rsps.post(CONSENSUS_MCP_URL, status=status, body="err")
            raised: BaseException | None = None
            try:
                provider.execute(query)
            except Exception as exc:  # noqa: BLE001
                raised = exc
            assert raised is not None
            module = type(raised).__module__
            assert module.startswith("retrieval.")
            assert "requests" not in module
            assert "urllib3" not in module


def test_consensus_apply_provider_scored_handles_malformed_numeric_fields() -> None:
    provider = ConsensusProvider()
    rows = [
        {
            "consensus_score": "unknown",
            "sample_size": "n/a",
            "study_design_tag": "meta-analysis",
        }
    ]
    filtered = provider.apply_provider_scored(
        rows,
        {
            "consensus_score_min": 0.5,
            "sample_size_min": 100,
            "study_design_allow": ["meta-analysis"],
        },
    )
    assert filtered == []


def test_consensus_apply_provider_scored_coerces_numeric_string_criteria() -> None:
    provider = ConsensusProvider()
    rows = [
        {
            "consensus_score": 0.8,
            "sample_size": 120,
            "study_design_tag": "meta-analysis",
        }
    ]
    filtered = provider.apply_provider_scored(
        rows,
        {
            "consensus_score_min": "0.7",
            "sample_size_min": "100",
            "study_design_allow": ["meta-analysis"],
        },
    )
    assert len(filtered) == 1


def test_consensus_provider_test_module_has_no_stateful_mocks() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = (
        "Magic" + "Mock",
        "Async" + "Mock",
        "unittest" + ".mock",
    )
    for token in forbidden:
        assert token not in source
