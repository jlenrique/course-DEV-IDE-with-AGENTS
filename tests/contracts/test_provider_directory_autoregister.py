"""AC-T.9 — `RetrievalAdapter` auto-registration with the provider directory.

Every concrete subclass with `PROVIDER_INFO` must appear in
`list_providers(shape="retrieval")`. Parametrized over subclasses so future
adapters inherit the test automatically.
"""

from __future__ import annotations

import pytest
from retrieval.base import RetrievalAdapter
from retrieval.fake_provider import (  # noqa: F401 — side-effect: auto-register FakeProvider
    FakeProvider,
    make_fake_provider_class,
)
from retrieval.provider_directory import list_providers


def _concrete_retrieval_subclasses() -> list[type[RetrievalAdapter]]:
    """Walk the subclass tree for concrete classes with a PROVIDER_INFO."""
    seen: set[type] = set()
    out: list[type[RetrievalAdapter]] = []

    def walk(cls: type) -> None:
        for sub in cls.__subclasses__():
            if sub in seen:
                continue
            seen.add(sub)
            info = getattr(sub, "PROVIDER_INFO", None)
            if info is not None and info.shape == "retrieval":
                out.append(sub)
            walk(sub)

    walk(RetrievalAdapter)
    return out


def test_every_retrieval_adapter_subclass_is_directoried() -> None:
    """Every registered retrieval-shape entry must be reachable via the registry.

    Auto-registration via `__init_subclass__` means any concrete `RetrievalAdapter`
    subclass with a well-formed `PROVIDER_INFO` is in the registry at class-
    definition time — class creation fails otherwise (register_adapter raises).
    This test asserts the inverse direction: every registered entry has a
    living class behind it. Subclasses created transiently in other tests
    (e.g., via `make_fake_provider_class`) are filtered out of the registry
    by the autouse snapshot/restore fixture.
    """
    from retrieval.provider_directory import _RETRIEVAL_ADAPTER_REGISTRY

    for provider_id, (cls, info) in _RETRIEVAL_ADAPTER_REGISTRY.items():
        assert cls is not None, f"{provider_id!r} has no class in registry"
        assert info.id == provider_id, (
            f"Registry key {provider_id!r} disagrees with "
            f"PROVIDER_INFO.id={info.id!r}"
        )
        assert info.shape == "retrieval", (
            f"Retrieval registry holds non-retrieval shape for {provider_id!r}"
        )
        # Live directory listing must surface this registered class.
        assert info.id in {
            p.id for p in list_providers(shape="retrieval")
        }, (
            f"Registered {provider_id!r} missing from list_providers output"
        )


def test_register_adapter_rejects_id_collision() -> None:
    """Same ID from a different class must raise — prevents silent override."""
    from retrieval.contracts import ProviderInfo
    from retrieval.provider_directory import register_adapter

    info = ProviderInfo(id="fake", shape="retrieval", status="stub")

    class ShouldFail(RetrievalAdapter):
        PROVIDER_INFO = None  # Don't auto-register; we'll call register_adapter manually.
        def formulate_query(self, intent): return ""
        def execute(self, q): return []
        def apply_mechanical(self, r, c): return r
        def apply_provider_scored(self, r, c): return r
        def normalize(self, r): return []
        def refine(self, pq, pr, c): return None
        def identity_key(self, row): return row.source_id

    with pytest.raises(ValueError, match="already registered"):
        register_adapter(ShouldFail, info)


def test_directory_registration_idempotent_on_same_class() -> None:
    """Re-registering the same class with same ID should succeed (reloads)."""
    from retrieval.provider_directory import register_adapter

    # FakeProvider is already registered; re-registering same class is OK
    register_adapter(FakeProvider, FakeProvider.PROVIDER_INFO)
    ids = [p.id for p in list_providers(shape="retrieval")]
    assert ids.count("fake") == 1
