"""`RetrievalAdapter` abstract base class — AC-B.3 (Story 27-0).

Each real provider ships as a subclass (scite in 27-2, Consensus in 27-2.5,
image-sources in 27-3, YouTube in 27-4). The base defines the contract the
dispatcher orchestrates; concrete subclasses supply the provider-DSL-specific
behavior.

Subclasses auto-register into the provider directory via `__init_subclass__`
when they declare `PROVIDER_INFO` (AC-B.8 operator amendment). Subclasses
that omit `PROVIDER_INFO` are treated as abstract helpers (e.g., testing
shims) and do not register.

All query / refinement logic is DETERMINISTIC Python (AC-C.6). No LLM calls.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from .contracts import (
    AcceptanceCriteria,
    ProviderInfo,
    RetrievalIntent,
    TexasRow,
)

ProviderQuery = Any
"""Opaque per-provider query object. Each adapter defines its own shape
(string, structured dict, dataclass — adapter's choice). The dispatcher
does not inspect it; it flows formulate_query → execute → refine."""

RawProviderResult = Any
"""Opaque per-provider execute() return value. Each adapter defines its
own shape. `normalize(raw) -> list[TexasRow]` converts to canonical rows."""


class RetrievalAdapter(ABC):
    """Abstract base class for retrieval-shape provider adapters.

    Subclasses MUST declare:
      - `PROVIDER_INFO: ClassVar[ProviderInfo]` — directory entry (auto-registered)
      - Concrete implementations of the 7 abstract methods below
        (`formulate_query`, `execute`, `apply_mechanical`, `apply_provider_scored`,
        `normalize`, `refine`, `identity_key`).

    Subclasses MAY override the two methods with default implementations:
      - `quality_delta` (base provides a row-count-delta default)
      - `declare_honored_criteria` (base returns an empty set; subclass should
        enumerate keys it actually evaluates)
    """

    PROVIDER_INFO: ClassVar[ProviderInfo | None] = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Auto-register every concrete subclass that declares `PROVIDER_INFO`.

        Registration is deferred to `provider_directory.register_adapter()` so
        tests can reset the registry cleanly between runs. Subclasses without
        a `PROVIDER_INFO` class attribute are treated as abstract helpers (no
        registration, no warning).
        """
        super().__init_subclass__(**kwargs)
        info = getattr(cls, "PROVIDER_INFO", None)
        if info is None:
            return
        if not isinstance(info, ProviderInfo):
            raise TypeError(
                f"{cls.__name__}.PROVIDER_INFO must be a ProviderInfo instance; "
                f"got {type(info).__name__}"
            )
        if info.shape != "retrieval":
            raise ValueError(
                f"{cls.__name__}.PROVIDER_INFO.shape must be 'retrieval' "
                f"(locator-shape handlers are declared statically in "
                f"provider_directory.py, not as RetrievalAdapter subclasses); "
                f"got {info.shape!r}"
            )
        from . import provider_directory

        provider_directory.register_adapter(cls, info)

    @abstractmethod
    def formulate_query(self, intent: RetrievalIntent) -> ProviderQuery:
        """Translate editorial intent + provider_hints params into a provider DSL query.

        MUST be deterministic: same input → byte-identical output across
        invocations (AC-T.2 `test_fake_provider_formulate_query_deterministic`).
        NO LLM calls; NO network; NO clock / random-number dependence.
        """

    @abstractmethod
    def execute(self, query: ProviderQuery) -> RawProviderResult:
        """Fetch results for the query (auth, pagination, rate-limiting inside).

        The dispatcher wraps this in no retry / fallback logic (AC-C.11);
        the adapter is responsible for its own transient-failure behavior
        and may raise on fatal errors.
        """

    @abstractmethod
    def apply_mechanical(
        self, results: RawProviderResult, criteria: dict[str, Any]
    ) -> RawProviderResult:
        """Deterministic-predicate filter over mechanical acceptance criteria.

        Unknown keys MUST NOT be silently dropped; surface them via
        `declare_honored_criteria()` so the dispatcher can log them.
        """

    @abstractmethod
    def apply_provider_scored(
        self, results: RawProviderResult, criteria: dict[str, Any]
    ) -> RawProviderResult:
        """Provider-native-signal filter (authority tier, citation-count, etc.)."""

    @abstractmethod
    def normalize(self, results: RawProviderResult) -> list[TexasRow]:
        """Convert raw provider output into canonical TexasRow list."""

    @abstractmethod
    def refine(
        self,
        previous_query: ProviderQuery,
        previous_results: RawProviderResult,
        criteria: AcceptanceCriteria,
    ) -> ProviderQuery | None:
        """Produce a broadened query, or None if refinement cannot help.

        Refinement MUST be monotonically-loosening: each successive call
        broadens (drops filters, widens date ranges, etc.) — never narrows.
        Returning None exits the iteration loop cleanly.
        """

    @abstractmethod
    def identity_key(self, row: TexasRow) -> str:
        """Return the canonical cross-validation identity for a row.

        Scholarly: DOI. Video: YouTube video-id. Image: canonical URL.
        Adapters that cannot uniquely identify rows MUST raise
        `NotImplementedError` — the dispatcher surfaces this as a dispatch-time
        error when `cross_validate: true` is requested (AC anti-pattern #10).
        """

    def quality_delta(
        self,
        prev_results: RawProviderResult,
        curr_results: RawProviderResult,
    ) -> float:
        """Default: len(curr) - len(prev) normalized to {-1.0, 0.0, +1.0}.

        Subclasses SHOULD override with a richer signal (e.g., coverage
        against acceptance criteria). The value is compared against a
        non-improvement threshold (>0) in the dispatcher; fixtures keep
        deltas clearly above/below the threshold (Murat flakiness guard).
        """
        prev_len = _safe_len(prev_results)
        curr_len = _safe_len(curr_results)
        if curr_len > prev_len:
            return 1.0
        if curr_len < prev_len:
            return -1.0
        return 0.0

    def declare_honored_criteria(self) -> set[str]:
        """Return the set of acceptance-criteria keys this adapter evaluates.

        Base returns empty set; subclasses SHOULD enumerate the mechanical +
        provider-scored keys they actually handle so unknown keys can be
        logged (AC-B.2 strengthened, Winston MUST-FIX #3).
        """
        return set()


def _safe_len(obj: Any) -> int:
    try:
        return len(obj)
    except TypeError:
        return 0


__all__ = [
    "ProviderQuery",
    "RawProviderResult",
    "RetrievalAdapter",
]
