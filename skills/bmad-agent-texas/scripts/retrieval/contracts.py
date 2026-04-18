"""Retrieval foundation Pydantic contracts — Shape 3-Disciplined (Story 27-0).

These types are the wire-format boundary between editorial authors (Tracy,
operator directives) and mechanical executors (Texas dispatcher + per-provider
`RetrievalAdapter` subclasses). They are schema-pinned by
`tests/contracts/test_acceptance_criteria_schema_stable.py` — changes without
an entry in `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` fail
the test.

Three guardrails enforced at the contract level:
  - `provider_hints` REQUIRED v1 (no provider discovery)
  - mechanical-only acceptance criteria evaluable in Texas (semantic is Tracy's post-fetch pass)
  - `convergence_signal` is STRUCTURAL, not semantic
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RetrievalKind = Literal["query", "direct_ref", "render"]
ProviderShape = Literal["retrieval", "locator"]
ProviderStatus = Literal["ready", "stub", "ratified", "backlog"]
SourceOrigin = Literal["operator-named", "tracy-suggested"]


class ProviderHint(BaseModel):
    """One element of `RetrievalIntent.provider_hints`.

    Pinned shape per AC-C.10 (green-light Round 1, 2026-04-17). `params` is
    provider-opaque — the dispatcher does not inspect it; each adapter
    interprets its own `params` via `formulate_query`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: str = Field(min_length=1)
    params: dict[str, Any] = Field(default_factory=dict)


class AcceptanceCriteria(BaseModel):
    """Three-tier acceptance criteria — AC-B.2.

    `mechanical`: Texas evaluates deterministically (date ranges, min results,
    license allowlists, duration caps, etc.).
    `provider_scored`: Texas evaluates via provider-native signals (authority
    tier, supporting-citation counts, peer-review flags).
    `semantic_deferred`: Texas does NOT evaluate — surfaces unchanged to
    Tracy's post-fetch semantic pass.

    Unknown keys under `mechanical` / `provider_scored` are NOT silently
    dropped; the dispatcher logs them in `refinement_log` with
    `reason: "not evaluable by this provider"` (AC-B.2 strengthened).
    """

    model_config = ConfigDict(extra="forbid")

    mechanical: dict[str, Any] = Field(default_factory=dict)
    provider_scored: dict[str, Any] = Field(default_factory=dict)
    semantic_deferred: str | None = None


class RetrievalIntent(BaseModel):
    """Editorial-to-mechanical boundary — AC-B.1.

    Tracy (or an operator directive auto-transformed via AC-B.7) authors this.
    Texas dispatcher routes it to adapters named in `provider_hints`.
    """

    model_config = ConfigDict(extra="forbid")

    intent: str = Field(min_length=1)
    provider_hints: list[ProviderHint] = Field(min_length=1)
    kind: RetrievalKind = "query"
    acceptance_criteria: AcceptanceCriteria = Field(default_factory=AcceptanceCriteria)
    iteration_budget: int = Field(default=3, ge=1, le=20)
    convergence_required: bool = True
    cross_validate: bool = False

    @field_validator("provider_hints")
    @classmethod
    def _require_nonempty_hints(cls, value: list[ProviderHint]) -> list[ProviderHint]:
        if not value:
            raise ValueError("provider_hints is required v1 — no provider discovery")
        return value


class ConvergenceSignal(BaseModel):
    """Cross-validation structural annotation — AC-C.11 dumbness clause.

    Structural only: row-count agreement, ID-overlap, identity-key match.
    Explicitly NOT semantic — no "these providers agree about the claim."
    """

    model_config = ConfigDict(extra="forbid")

    providers_agreeing: list[str] = Field(default_factory=list)
    providers_disagreeing: list[str] = Field(default_factory=list)
    single_source_only: list[str] = Field(default_factory=list)


class TexasRow(BaseModel):
    """Canonical normalized output shape — AC-C.2.

    Every adapter's `normalize(raw_result) -> TexasRow` emits this shape.
    Downstream consumers (Vera, Quinn-R, Irene, report writers) consume
    `TexasRow` exclusively; `provider_metadata` is the per-provider opaque
    escape hatch for adapter-specific fields.
    """

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    title: str = ""
    body: str = ""
    authors: list[str] = Field(default_factory=list)
    date: str | None = None
    provider: str = Field(min_length=1)
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
    source_origin: SourceOrigin = "operator-named"
    tracy_row_ref: str | None = None
    convergence_signal: ConvergenceSignal | None = None
    authority_tier: str | None = None
    completeness_ratio: float | None = Field(default=None, ge=0.0, le=1.0)
    structural_fidelity: float | None = Field(default=None, ge=0.0, le=1.0)


class ProviderInfo(BaseModel):
    """Provider directory entry — AC-B.8 (operator amendment 2026-04-18).

    One entry per thing Texas can fetch. Retrieval-shape entries auto-register
    from `RetrievalAdapter` subclasses via their `PROVIDER_INFO` classvar.
    Locator-shape entries (file-format handlers) are declared statically in
    `provider_directory.py`. Backlog-status entries are forward-looking
    placeholders (e.g., `openai-chatgpt`) reserved so the directory is a true
    roster of intended capability, not just shipped capability.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1)
    shape: ProviderShape
    status: ProviderStatus
    capabilities: list[str] = Field(default_factory=list)
    auth_env_vars: list[str] = Field(default_factory=list)
    spec_ref: str | None = None
    notes: str = ""


class RefinementLogEntry(BaseModel):
    """One row of the dispatcher's `refinement_log`.

    Surfaces WHY a query was refined (or failed) to the caller. Unknown AC
    keys, budget exhaustion, non-improvement aborts, and adapter-returned
    `refine -> None` each emit an entry.
    """

    model_config = ConfigDict(extra="forbid")

    iteration: int = Field(ge=0)
    reason: str
    provider: str
    criterion_key: str | None = None
    quality_delta: float | None = None


class ProviderResult(BaseModel):
    """Output of a single adapter's `run_until_converged()` — Model A iteration.

    The dispatcher assembles these per-provider results; for `cross_validate:
    true`, the cross-validation merger then produces a merged result with
    `ConvergenceSignal` annotations.
    """

    model_config = ConfigDict(extra="forbid")

    provider: str
    rows: list[TexasRow] = Field(default_factory=list)
    acceptance_met: bool = False
    iterations_used: int = Field(ge=0)
    refinement_log: list[RefinementLogEntry] = Field(default_factory=list)


__all__ = [
    "AcceptanceCriteria",
    "ConvergenceSignal",
    "ProviderHint",
    "ProviderInfo",
    "ProviderResult",
    "ProviderShape",
    "ProviderStatus",
    "RefinementLogEntry",
    "RetrievalIntent",
    "RetrievalKind",
    "SourceOrigin",
    "TexasRow",
]


SCHEMA_VERSION = "1.1"
"""Extraction-report schema version anchored to these contracts (AC-C.3)."""
