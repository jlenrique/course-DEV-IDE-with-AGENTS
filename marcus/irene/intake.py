"""Irene retrieval-intake contract and deterministic narration helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

CONVERGENCE_NARRATION_PATTERNS: dict[str, str] = {
    "dual_scite_consensus": (
        "Corroborated by multiple independent sources, with support from "
        "peer-reviewed citation context and synthesis evidence."
    ),
    "single_scite": "According to scite.ai citation-context analysis.",
    "single_consensus": "Per Consensus research synthesis.",
    "fallback": "According to available retrieval evidence.",
}


class ConvergenceSignal(BaseModel):
    """Convergence metadata emitted by retrieval-shape extraction reports."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    providers_agreeing: list[str] = Field(default_factory=list)
    providers_disagreeing: list[str] = Field(default_factory=list)
    single_source_only: list[str] = Field(default_factory=list)


class RetrievalProvenance(BaseModel):
    """Additive pass-2 provenance payload attached to segment entries."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_id: str = Field(min_length=1)
    providers: list[str] = Field(min_length=1)
    convergence_signal: ConvergenceSignal | None = None


class IreneRetrievalIntake(BaseModel):
    """T1 intake record consumed by Irene when available."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str = Field(min_length=1)
    pass_2_cluster_id: str = Field(min_length=1)
    suggested_resources_ref: str = Field(min_length=1)
    extraction_report_ref: str | None = None
    intake_mode: Literal["corroborate", "embellish", "gap_fill", "mixed"] = (
        "corroborate"
    )
    evidence_bolster_active: bool = False

    @field_validator("suggested_resources_ref", "extraction_report_ref", mode="before")
    @classmethod
    def _validate_relative_refs(cls, value: Any) -> Any:
        if value is None:
            return value
        if not isinstance(value, str):
            raise TypeError("reference paths must be strings")
        normalized = value.replace("\\", "/")
        path = Path(normalized)
        first_part = path.parts[0] if path.parts else ""
        if (
            path.is_absolute()
            or path.drive
            or ":" in first_part
            or ".." in path.parts
        ):
            raise ValueError("reference paths must be workspace-relative")
        return normalized


class IreneRetrievalDecision(BaseModel):
    """Narration/posture decision derived from intake + retrieval artifacts."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    include_retrieval_segment: bool
    narration_attribution: str | None = None
    retrieval_provenance: tuple[RetrievalProvenance, ...] = ()
    known_losses: tuple[str, ...] = ()


def parse_irene_retrieval_intake(payload: Mapping[str, Any]) -> IreneRetrievalIntake:
    """Validate an intake payload from in-memory JSON/YAML data."""
    return IreneRetrievalIntake.model_validate(dict(payload))


def load_irene_retrieval_intake(path: Path) -> IreneRetrievalIntake:
    """Load and validate intake payload from disk."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        raise ValueError("intake file must contain an object")
    return parse_irene_retrieval_intake(data)


def resolve_convergence_narration(
    signal: ConvergenceSignal | None,
    *,
    evidence_bolster_active: bool,
) -> str:
    """Resolve the attribution phrase from convergence posture."""
    if not evidence_bolster_active:
        return CONVERGENCE_NARRATION_PATTERNS["single_scite"]

    if signal is None:
        return CONVERGENCE_NARRATION_PATTERNS["fallback"]

    agreeing = {provider.lower() for provider in signal.providers_agreeing}
    disagreeing = {provider.lower() for provider in signal.providers_disagreeing}
    single_source = {provider.lower() for provider in signal.single_source_only}
    if {"scite", "consensus"}.issubset(agreeing) and not single_source:
        return CONVERGENCE_NARRATION_PATTERNS["dual_scite_consensus"]
    if not disagreeing and ("scite" in single_source or agreeing == {"scite"}):
        return CONVERGENCE_NARRATION_PATTERNS["single_scite"]
    if not disagreeing and ("consensus" in single_source or agreeing == {"consensus"}):
        return CONVERGENCE_NARRATION_PATTERNS["single_consensus"]
    return CONVERGENCE_NARRATION_PATTERNS["fallback"]


def build_retrieval_provenance(
    extraction_report: Mapping[str, Any] | None,
) -> tuple[RetrievalProvenance, ...]:
    """Project extraction-report v1.1 entries into additive segment provenance."""
    if extraction_report is None:
        return ()
    raw_sources = extraction_report.get("sources", [])
    if not isinstance(raw_sources, list):
        return ()

    provenance: list[RetrievalProvenance] = []
    for source in raw_sources:
        if not isinstance(source, Mapping):
            continue
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            continue
        convergence = source.get("convergence_signal")
        signal_obj: ConvergenceSignal | None = None
        if isinstance(convergence, Mapping):
            try:
                signal_obj = ConvergenceSignal.model_validate(dict(convergence))
            except ValidationError:
                signal_obj = None
        providers = _extract_providers(source, signal_obj)
        if not providers:
            continue
        provenance.append(
            RetrievalProvenance(
                source_id=source_id.strip(),
                providers=providers,
                convergence_signal=signal_obj,
            )
        )
    return tuple(provenance)


def apply_corroborate_intake(
    intake: IreneRetrievalIntake,
    *,
    suggested_resources: Sequence[Mapping[str, Any]],
    extraction_report: Mapping[str, Any] | None,
) -> IreneRetrievalDecision:
    """Corroborate-only v1 seam from intake packet to narration attribution."""
    if not _has_corroborate_candidate(suggested_resources):
        return _empty_retrieval_decision(intake.pass_2_cluster_id)

    provenance = build_retrieval_provenance(extraction_report)
    if not provenance:
        return _empty_retrieval_decision(intake.pass_2_cluster_id)

    best_row = next(
        (
            row
            for row in provenance
            if row.convergence_signal is not None
            and row.convergence_signal.providers_agreeing
        ),
        provenance[0],
    )
    narration = resolve_convergence_narration(
        best_row.convergence_signal,
        evidence_bolster_active=intake.evidence_bolster_active,
    )

    return IreneRetrievalDecision(
        include_retrieval_segment=True,
        narration_attribution=narration,
        retrieval_provenance=provenance,
        known_losses=(),
    )


def _extract_providers(
    source: Mapping[str, Any],
    signal: ConvergenceSignal | None,
) -> list[str]:
    providers: list[str] = []

    def _push(raw: str) -> None:
        value = raw.strip().lower()
        if value and value not in providers:
            providers.append(value)

    if signal is not None:
        for value in signal.providers_agreeing:
            _push(value)
        for value in signal.single_source_only:
            _push(value)
    provider = source.get("provider")
    if isinstance(provider, str):
        _push(provider)
    return providers


def _has_corroborate_candidate(suggested_resources: Sequence[Mapping[str, Any]]) -> bool:
    for entry in suggested_resources:
        output = entry.get("output") if isinstance(entry, Mapping) else None
        posture = output.get("posture") if isinstance(output, Mapping) else None
        evidence_found = (
            output.get("evidence_found") if isinstance(output, Mapping) else None
        )
        if posture == "corroborate" and evidence_found is True:
            return True
    return False


def _empty_retrieval_decision(cluster_id: str) -> IreneRetrievalDecision:
    return IreneRetrievalDecision(
        include_retrieval_segment=False,
        narration_attribution=None,
        retrieval_provenance=(),
        known_losses=(f"retrieval_empty_for_cluster_{cluster_id}",),
    )
