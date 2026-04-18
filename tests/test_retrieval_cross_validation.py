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

from retrieval import (
    AcceptanceCriteria,
    AdapterFactory,
    DispatchError,
    ProviderHint,
    RetrievalIntent,
    dispatch,
)
from retrieval.fake_provider import FakeProvider, make_fake_provider_class, make_row


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
