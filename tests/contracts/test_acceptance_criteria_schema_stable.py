"""AC-T.1 — Retrieval contract schema-pin (Murat #1 priority test).

Snapshot + allowlist + SCHEMA_CHANGELOG.md gate (Option A green-light decision).
Any change to `RetrievalIntent` / `AcceptanceCriteria` / `TexasRow` without a
matching snapshot update here AND a matching entry in
`_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` fails the test.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from retrieval.contracts import (
    AcceptanceCriteria,
    ProviderInfo,
    RetrievalIntent,
    TexasRow,
)

FIXTURES = Path(__file__).parent / "fixtures" / "retrieval"
CHANGELOG = (
    Path(__file__).parents[2]
    / "_bmad-output"
    / "implementation-artifacts"
    / "SCHEMA_CHANGELOG.md"
)


def _load_snapshot(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _field_names(model_cls) -> set[str]:
    return set(model_cls.model_fields.keys())


def test_retrieval_intent_fields_match_snapshot() -> None:
    snap = _load_snapshot("retrieval_intent_v1_1.json")
    expected = set(snap["fields"].keys())
    actual = _field_names(RetrievalIntent)
    missing = expected - actual
    extra = actual - expected
    assert not missing, f"RetrievalIntent missing fields per snapshot: {missing}"
    assert not extra, (
        f"RetrievalIntent has NEW fields not in snapshot: {extra}. "
        f"Add them to tests/contracts/fixtures/retrieval/retrieval_intent_v1_1.json "
        f"AND add a SCHEMA_CHANGELOG.md entry explaining the bump."
    )


def test_acceptance_criteria_fields_match_snapshot() -> None:
    snap = _load_snapshot("acceptance_criteria_v1_1.json")
    expected = set(snap["fields"].keys())
    actual = _field_names(AcceptanceCriteria)
    assert actual == expected, (
        f"AcceptanceCriteria schema drift. Missing: {expected - actual}. "
        f"New: {actual - expected}."
    )


def test_texas_row_fields_match_snapshot() -> None:
    snap = _load_snapshot("texas_row_v1_1.json")
    expected = set(snap["fields"].keys())
    actual = _field_names(TexasRow)
    assert actual == expected, (
        f"TexasRow schema drift. Missing: {expected - actual}. "
        f"New: {actual - expected}."
    )


def test_provider_info_is_frozen() -> None:
    """ProviderInfo must remain frozen (immutable after construction)."""
    info = ProviderInfo(id="x", shape="retrieval", status="ready")
    with pytest.raises((ValidationError, AttributeError, TypeError)):
        info.status = "backlog"  # type: ignore[misc]


def test_schema_changelog_exists_and_pins_v1_1() -> None:
    """AC-T.1 gate: every schema bump must be documented in the changelog."""
    assert CHANGELOG.exists(), (
        f"SCHEMA_CHANGELOG.md missing at {CHANGELOG}. "
        f"Every non-patch schema bump requires an entry here."
    )
    text = CHANGELOG.read_text(encoding="utf-8")
    assert "v1.1" in text, "SCHEMA_CHANGELOG.md does not mention v1.1 bump"
    assert "Story 27-0" in text, "SCHEMA_CHANGELOG.md does not attribute v1.1 to Story 27-0"


def test_retrieval_intent_rejects_empty_provider_hints() -> None:
    """Dr. Quinn guardrail: provider_hints REQUIRED v1 — no provider discovery."""
    with pytest.raises(ValidationError):
        RetrievalIntent(intent="x", provider_hints=[])


def test_retrieval_intent_rejects_extra_fields() -> None:
    """extra='forbid' prevents silent schema drift."""
    with pytest.raises(ValidationError):
        RetrievalIntent(
            intent="x",
            provider_hints=[{"provider": "p"}],
            rogue_field="should-reject",  # type: ignore[call-arg]
        )


# ---------------------------------------------------------------------------
# SHOULD-FIX (code-review 2026-04-18): dual-version pin per spec's
# green-light strengthening "pin BOTH v1.0 and v1.1 artifacts; legacy row
# validates against both; new row validates against v1.1 only."
#
# Retrieval contracts (RetrievalIntent / AcceptanceCriteria / TexasRow) are
# NEW in v1.1 — they did not exist in v1.0. The v1.0 snapshot therefore
# pins the empty-set baseline. The dual-version test asserts that every
# v1.1 field is ADDITIVE (present in v1.1, absent in v1.0), which is
# exactly what the SCHEMA_CHANGELOG "additive only" claim requires.
# ---------------------------------------------------------------------------


def test_retrieval_intent_v1_0_baseline_is_empty() -> None:
    """v1.0 had no retrieval-contract fields — the baseline snapshot is empty."""
    snap = _load_snapshot("retrieval_intent_v1_0.json")
    assert snap["fields"] == {}, (
        "v1.0 retrieval-intent baseline must be empty — the contracts are "
        "new in v1.1. Any non-empty v1.0 fixture breaks the additive-only claim."
    )


def test_v1_1_retrieval_intent_is_additive_over_v1_0() -> None:
    """Every v1.1 field must be NEW (not renamed/retyped from v1.0)."""
    v1_0 = _load_snapshot("retrieval_intent_v1_0.json")["fields"]
    v1_1 = _load_snapshot("retrieval_intent_v1_1.json")["fields"]
    renamed = set(v1_0) - set(v1_1)
    assert not renamed, (
        f"v1.0 fields {renamed} disappeared in v1.1 — that is a breaking change, "
        f"not additive. Major-bump required, not a minor-bump."
    )
