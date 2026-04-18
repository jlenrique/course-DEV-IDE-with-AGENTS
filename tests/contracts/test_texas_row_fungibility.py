"""AC-T.5 — `TexasRow` cross-provider fungibility (against-canonical, not pairwise).

Providers conform TO the canonical shape — not vice versa. Linear in provider
count (Murat). Canonical fixture self-tests so the canonical itself can't drift
from the schema.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from retrieval.contracts import TexasRow
from retrieval.fake_provider import FakeProvider, make_fake_provider_class, make_row

CANONICAL_PATH = (
    Path(__file__).parent / "fixtures" / "retrieval" / "canonical_texas_row.json"
)


@pytest.fixture
def canonical() -> dict:
    return json.loads(CANONICAL_PATH.read_text(encoding="utf-8"))


def test_canonical_texas_row_is_schema_valid(canonical: dict) -> None:
    """AC-T.5 canonical-shape self-test (Murat add) — prevents canonical drifting from schema."""
    row = TexasRow(**canonical)
    assert row.source_id == canonical["source_id"]


def test_row_identity_preserved_across_providers(canonical: dict) -> None:
    """Identity round-trips unchanged regardless of emitting adapter."""
    adapter_a = FakeProvider(provider_name="adapter_a")
    adapter_b_cls = make_fake_provider_class("adapter_b")
    adapter_b = adapter_b_cls()
    row_raw = make_row(
        canonical["source_id"],
        title=canonical["title"],
        body=canonical["body"],
        authority_tier=canonical["authority_tier"],
    )
    out_a = adapter_a.normalize([row_raw])[0]
    out_b = adapter_b.normalize([row_raw])[0]
    assert out_a.source_id == out_b.source_id == canonical["source_id"]
    assert out_a.title == out_b.title == canonical["title"]


def test_row_ordering_deterministic_per_provider() -> None:
    """Adapter.normalize() preserves input ordering across calls."""
    adapter = FakeProvider()
    rows = [make_row(f"doi:{i}") for i in range(5)]
    out1 = [r.source_id for r in adapter.normalize(rows)]
    out2 = [r.source_id for r in adapter.normalize(rows)]
    assert out1 == out2
    assert out1 == [f"doi:{i}" for i in range(5)]
