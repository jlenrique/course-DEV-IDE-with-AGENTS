"""AC-T.4 — Cross-validation merger tests.

Six atomic tests after Murat's split (was 4, now 6):
  1. both-agree
  2. disagreement (3-provider case)
  3. single-source
  4. identity-keyed merge
  5. single-source-only flag
  6. non-DOI identity extractor

Cross-validation is a DISTINCT code path from single-provider even at N=1
(anti-pattern #8). Structural only (AC-C.11) — no semantic interpretation.
"""

from __future__ import annotations

import json

import pytest
import responses
from retrieval import (
    AcceptanceCriteria,
    AdapterFactory,
    DispatchError,
    ProviderHint,
    RetrievalIntent,
    dispatch,
)
from retrieval.consensus_provider import CONSENSUS_MCP_URL
from retrieval.fake_provider import FakeProvider, make_fake_provider_class, make_row
from retrieval.scite_provider import SCITE_MCP_URL

from tests._helpers.mcp_fixtures import jsonrpc_response


def _build_two_provider_fixtures():
    scite_cls = make_fake_provider_class("scite_fake")
    consensus_cls = make_fake_provider_class("consensus_fake")
    scite = scite_cls()
    scite._rows_by_query = {  # noqa: SLF001 — test fixture
        "initial:x": [
            make_row("doi:a", provider="scite_fake"),
            make_row("doi:b", provider="scite_fake"),
        ]
    }
    consensus = consensus_cls()
    consensus._rows_by_query = {  # noqa: SLF001
        "initial:x": [
            make_row("doi:a", provider="consensus_fake"),
            make_row("doi:c", provider="consensus_fake"),
        ]
    }
    factory = AdapterFactory({"scite_fake": scite, "consensus_fake": consensus})
    return scite, consensus, factory


def _cv_intent() -> RetrievalIntent:
    return RetrievalIntent(
        intent="x",
        provider_hints=[
            ProviderHint(provider="scite_fake"),
            ProviderHint(provider="consensus_fake"),
        ],
        cross_validate=True,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )


def _all_annotations(results):
    """Return dict of source_id -> ConvergenceSignal across all provider results."""
    out = {}
    for r in results:
        for row in r.rows:
            if row.convergence_signal is not None:
                out[row.source_id] = row.convergence_signal
    return out


def test_convergence_signal__both_agree() -> None:
    """doi:a appears in both → providers_agreeing contains both."""
    _, _, factory = _build_two_provider_fixtures()
    results = dispatch(_cv_intent(), factory=factory)
    ann = _all_annotations(results)
    assert "doi:a" in ann
    agree = set(ann["doi:a"].providers_agreeing)
    assert agree == {"scite_fake", "consensus_fake"}


def test_convergence_signal__disagreement() -> None:
    """In a 3-provider fan-out, a row present in 2 of 3 gets disagreeing=[missing]."""
    a_cls = make_fake_provider_class("a_p")
    b_cls = make_fake_provider_class("b_p")
    c_cls = make_fake_provider_class("c_p")
    a = a_cls()
    a._rows_by_query = {"initial:x": [make_row("doi:shared", provider="a_p")]}
    b = b_cls()
    b._rows_by_query = {"initial:x": [make_row("doi:shared", provider="b_p")]}
    c = c_cls()
    c._rows_by_query = {"initial:x": [make_row("doi:c_only", provider="c_p")]}
    factory = AdapterFactory({"a_p": a, "b_p": b, "c_p": c})
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[
            ProviderHint(provider="a_p"),
            ProviderHint(provider="b_p"),
            ProviderHint(provider="c_p"),
        ],
        cross_validate=True,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    results = dispatch(intent, factory=factory)
    ann = _all_annotations(results)
    shared = ann["doi:shared"]
    assert set(shared.providers_agreeing) == {"a_p", "b_p"}
    assert shared.providers_disagreeing == ["c_p"]


def test_convergence_signal__single_source() -> None:
    """A row seen in only one provider out of two → single_source_only=[that].

    SHOULD-FIX H-5 (code-review 2026-04-18): `providers_disagreeing` also
    populated with the peers that were checked-but-missed, so downstream
    consumers filtering on single-source can still see WHICH peers were
    available for corroboration.
    """
    _, _, factory = _build_two_provider_fixtures()
    results = dispatch(_cv_intent(), factory=factory)
    ann = _all_annotations(results)
    assert ann["doi:b"].single_source_only == ["scite_fake"]
    assert ann["doi:b"].providers_disagreeing == ["consensus_fake"]
    assert ann["doi:c"].single_source_only == ["consensus_fake"]
    assert ann["doi:c"].providers_disagreeing == ["scite_fake"]


def test_intra_provider_identity_key_duplicate_logs_not_drops() -> None:
    """MUST-FIX CR-3 (code-review 2026-04-18): intra-provider duplicate
    identity_key is NOT silently dropped — the merger records a
    refinement-log entry on the owning provider's result so callers can
    detect adapter-side pagination bugs.
    """
    # A provider that returns two rows with the same DOI (happens with scite
    # on multi-context-window returns).
    DupFake = make_fake_provider_class("dup_fake")  # noqa: N806 — class object, not a variable
    dup = DupFake(
        rows={
            "initial:x": [
                make_row("doi:same", title="first"),
                make_row("doi:same", title="dup"),
            ]
        }
    )
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="dup_fake")],
        cross_validate=True,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    results = dispatch(intent, factory=AdapterFactory({"dup_fake": dup}))
    assert len(results) == 1
    reasons = {e.reason for e in results[0].refinement_log}
    assert "intra_provider_identity_key_duplicate" in reasons


def test_cross_validation_merges_by_identity_key() -> None:
    """Identity-keyed merge: a shared row appears once per result with identical annotation."""
    _, _, factory = _build_two_provider_fixtures()
    results = dispatch(_cv_intent(), factory=factory)
    # Each provider's result retains its own rows, but 'doi:a' annotation matches across providers.
    all_ann_for_a = [
        row.convergence_signal
        for r in results
        for row in r.rows
        if row.source_id == "doi:a"
    ]
    assert len(all_ann_for_a) == 2  # scite + consensus
    assert all_ann_for_a[0] == all_ann_for_a[1]


def test_cross_validation_identity_key_missing_raises() -> None:
    """anti-pattern #10 guard: adapter without identity_key cannot cross-validate."""
    from retrieval.contracts import ProviderInfo

    class _BadAdapter(FakeProvider):
        PROVIDER_INFO = ProviderInfo(
            id="_bad_id_missing", shape="retrieval", status="stub"
        )

        def identity_key(self, row):
            raise NotImplementedError("cannot identify")

    bad = _BadAdapter(
        rows_by_query={"initial:x": [make_row("doi:1")]},
        provider_name="_bad_id_missing",
    )
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="_bad_id_missing")],
        cross_validate=True,
    )
    try:
        dispatch(intent, factory=AdapterFactory({"_bad_id_missing": bad}))
    except DispatchError as exc:
        assert "identity_key" in str(exc)
        return
    raise AssertionError("DispatchError was not raised")


def test_cross_validation_non_doi_identity_extractor() -> None:
    """Identity key can be any canonical string (not just DOI) — e.g., video-id."""
    from retrieval.contracts import ProviderInfo

    class _YoutubeFake(FakeProvider):
        PROVIDER_INFO = ProviderInfo(
            id="_yt_test", shape="retrieval", status="stub"
        )

        def identity_key(self, row):
            return row.provider_metadata.get("video_id") or row.source_id

    yt = _YoutubeFake(
        rows_by_query={
            "initial:x": [
                make_row("yt:1", provider="_yt_test", video_id="abc123"),
                make_row("yt:2", provider="_yt_test", video_id="xyz789"),
            ]
        },
        provider_name="_yt_test",
    )
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="_yt_test")],
        cross_validate=True,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    results = dispatch(intent, factory=AdapterFactory({"_yt_test": yt}))
    # N=1 cross-val path: every row gets single_source_only=[_yt_test]
    ann = _all_annotations(results)
    assert "yt:1" in ann
    assert ann["yt:1"].single_source_only == ["_yt_test"]


@pytest.fixture
def _live_provider_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Credentials used by real adapters under synthetic HTTP fixtures."""
    monkeypatch.setenv("SCITE_USER_NAME", "scite-user")
    monkeypatch.setenv("SCITE_PASSWORD", "scite-pass")
    monkeypatch.setenv("CONSENSUS_API_KEY", "consensus-token")


def _scite_search_payload(papers: list[dict[str, object]]) -> dict[str, object]:
    return {"papers": papers}


def _consensus_search_payload(papers: list[dict[str, object]]) -> dict[str, object]:
    return {"papers": papers}


def test_cross_validate_real_scite_consensus_fanout_and_merge(
    _live_provider_env: None,
) -> None:
    intent = RetrievalIntent(
        intent="sleep evidence",
        provider_hints=[
            ProviderHint(provider="scite", params={"mode": "search"}),
            ProviderHint(provider="consensus", params={"mode": "search"}),
        ],
        cross_validate=True,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )

    scite_papers = [
        {
            "doi": "10.shared/1",
            "scite_paper_id": "sp-1",
            "title": "Shared DOI from scite",
            "authors": ["A"],
            "year": 2024,
            "publication_date": "2024-01-01",
            "venue": "Nature",
            "abstract": "shared",
            "supporting_count": 12,
            "contradicting_count": 1,
            "mentioning_count": 5,
            "cited_by_count": 30,
            "scite_report_url": "https://scite.ai/reports/sp-1",
        },
        {
            "doi": "10.scite/2",
            "scite_paper_id": "sp-2",
            "title": "Scite-only DOI",
            "authors": ["B"],
            "year": 2023,
            "publication_date": "2023-06-01",
            "venue": "bioRxiv",
            "abstract": "scite only",
            "supporting_count": 4,
            "contradicting_count": 0,
            "mentioning_count": 2,
            "cited_by_count": 8,
            "scite_report_url": "https://scite.ai/reports/sp-2",
        },
    ]
    consensus_papers = [
        {
            "doi": "10.shared/1",
            "consensus_paper_id": "cp-1",
            "title": "Shared DOI from consensus",
            "authors": ["C"],
            "publication_date": "2024-02-01",
            "year": 2024,
            "venue": "Evidence Journal",
            "abstract": "shared",
            "consensus_score": 0.81,
            "study_design_tag": "meta-analysis",
            "sample_size": 220,
            "evidence_strength": "strong",
            "consensus_url": "https://consensus.app/papers/cp-1",
        },
        {
            "doi": "10.consensus/3",
            "consensus_paper_id": "cp-3",
            "title": "Consensus-only DOI",
            "authors": ["D"],
            "publication_date": "2022-05-01",
            "year": 2022,
            "venue": "Synthesis Review",
            "abstract": "consensus only",
            "consensus_score": 0.62,
            "study_design_tag": "cohort",
            "sample_size": 150,
            "evidence_strength": "moderate",
            "consensus_url": "https://consensus.app/papers/cp-3",
        },
    ]

    with responses.RequestsMock() as rsps:
        rsps.post(
            SCITE_MCP_URL,
            json=jsonrpc_response(result=_scite_search_payload(scite_papers)),
        )
        rsps.post(
            CONSENSUS_MCP_URL,
            json=jsonrpc_response(result=_consensus_search_payload(consensus_papers)),
        )
        results = dispatch(intent)

        assert len(rsps.calls) == 2
        call_bodies = [json.loads(call.request.body) for call in rsps.calls]
        tool_names = {body["params"]["name"] for body in call_bodies}
        assert tool_names == {"search"}

    assert isinstance(results, list)
    assert len(results) == 2
    assert {r.provider for r in results} == {"scite", "consensus"}

    ann = _all_annotations(results)
    assert set(ann["10.shared/1"].providers_agreeing) == {"scite", "consensus"}
    assert ann["10.shared/1"].single_source_only == []
    assert ann["10.scite/2"].single_source_only == ["scite"]
    assert ann["10.consensus/3"].single_source_only == ["consensus"]


def test_cross_validate_convergence_signal_structural_not_semantic(
    _live_provider_env: None,
) -> None:
    """Shared DOI means structural convergence even when semantics diverge."""
    intent = RetrievalIntent(
        intent="sleep evidence",
        provider_hints=[
            ProviderHint(provider="scite", params={"mode": "search"}),
            ProviderHint(provider="consensus", params={"mode": "search"}),
        ],
        cross_validate=True,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )

    scite_papers = [
        {
            "doi": "10.shared/sem",
            "scite_paper_id": "sp-sem",
            "title": "Shared DOI semantic split",
            "authors": ["A"],
            "year": 2024,
            "publication_date": "2024-03-01",
            "venue": "Nature",
            "abstract": "semantic split",
            "supporting_count": 50,
            "contradicting_count": 2,
            "mentioning_count": 5,
            "cited_by_count": 100,
            "scite_report_url": "https://scite.ai/reports/sp-sem",
        }
    ]
    consensus_papers = [
        {
            "doi": "10.shared/sem",
            "consensus_paper_id": "cp-sem",
            "title": "Shared DOI semantic split",
            "authors": ["B"],
            "publication_date": "2024-03-02",
            "year": 2024,
            "venue": "Evidence Journal",
            "abstract": "semantic split",
            "consensus_score": 0.30,
            "study_design_tag": "weak",
            "sample_size": 40,
            "evidence_strength": "weak",
            "consensus_url": "https://consensus.app/papers/cp-sem",
        }
    ]

    with responses.RequestsMock() as rsps:
        rsps.post(
            SCITE_MCP_URL,
            json=jsonrpc_response(result=_scite_search_payload(scite_papers)),
        )
        rsps.post(
            CONSENSUS_MCP_URL,
            json=jsonrpc_response(result=_consensus_search_payload(consensus_papers)),
        )
        results = dispatch(intent)

    ann = _all_annotations(results)
    signal = ann["10.shared/sem"]
    assert set(signal.providers_agreeing) == {"scite", "consensus"}
