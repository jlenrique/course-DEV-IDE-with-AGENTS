"""Pipeline manifest loader and typed access helpers."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from types import MappingProxyType

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from scripts.utilities.file_helpers import project_root

DEFAULT_MANIFEST_PATH = project_root() / "state" / "config" / "pipeline-manifest.yaml"
KNOWN_SCHEMA_VERSIONS = frozenset({"1.0"})


class ManifestInternalInconsistencyError(ValueError):
    """Raised when manifest links violate internal consistency rules."""


class LearningEventsConfig(BaseModel):
    """Top-level learning-event config."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_ref: str | None = None


class StepLearningEvents(BaseModel):
    """Per-step event emission topology."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    emits: bool = False
    event_types: tuple[str, ...] = ()
    schema_ref: str | None = None

    @model_validator(mode="after")
    def _validate_emit_shape(self) -> StepLearningEvents:
        if self.emits and not self.event_types:
            raise ValueError("learning_events.emits=true requires non-empty event_types")
        if not self.emits and self.event_types:
            raise ValueError("learning_events.emits=false requires empty event_types")
        return self


class StepEntry(BaseModel):
    """Single pipeline step declaration."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    id: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    gate: bool
    gate_code: str | None = None
    sub_phase_of: str | None = None
    insertion_after: str | None = None
    hud_tracked: bool = True
    pack_section_anchor: str = Field(..., min_length=1)
    pack_version: str | None = None
    rationale: str | None = None
    learning_events: StepLearningEvents = Field(default_factory=StepLearningEvents)

    @model_validator(mode="after")
    def _validate_gate_code(self) -> StepEntry:
        if self.gate and not self.gate_code:
            raise ValueError(f"step {self.id}: gate=true requires gate_code")
        if not self.gate and self.gate_code:
            raise ValueError(f"step {self.id}: gate=false must not set gate_code")
        return self


class PipelineManifest(BaseModel):
    """Canonical pipeline declaration for lockstep projections."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_version: str
    pack_version: str
    generator_ref: str
    learning_events: LearningEventsConfig = Field(default_factory=LearningEventsConfig)
    block_mode_trigger_paths: tuple[str, ...] = ()
    steps: tuple[StepEntry, ...]

    @model_validator(mode="after")
    def _validate_block_mode_trigger_paths(self) -> PipelineManifest:
        for pattern in self.block_mode_trigger_paths:
            if not isinstance(pattern, str) or not pattern.strip():
                raise ValueError("block_mode_trigger_paths entries must be non-empty strings")
            # Validate fnmatch compatibility by compiling the translated regex.
            fnmatch.translate(pattern)
        return self


def _enforce_internal_invariants(manifest: PipelineManifest) -> None:
    if manifest.schema_version not in KNOWN_SCHEMA_VERSIONS:
        raise ManifestInternalInconsistencyError(
            f"Unsupported schema_version: {manifest.schema_version}"
        )

    step_ids = {step.id for step in manifest.steps}
    if len(step_ids) != len(manifest.steps):
        raise ManifestInternalInconsistencyError("Duplicate step IDs found in manifest")

    gate_codes: set[str] = set()
    for step in manifest.steps:
        if step.sub_phase_of and step.sub_phase_of not in step_ids:
            raise ManifestInternalInconsistencyError(
                f"Step {step.id} references missing sub_phase_of target {step.sub_phase_of}"
            )
        if step.insertion_after and step.insertion_after not in step_ids:
            raise ManifestInternalInconsistencyError(
                f"Step {step.id} references missing insertion_after target {step.insertion_after}"
            )
        if step.gate and step.gate_code:
            if step.gate_code in gate_codes:
                raise ManifestInternalInconsistencyError(
                    f"Duplicate gate_code detected: {step.gate_code}"
                )
            gate_codes.add(step.gate_code)


def load_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> PipelineManifest:
    """Load and validate the pipeline manifest."""
    if not path.exists():
        raise FileNotFoundError(f"Pipeline manifest not found at {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ManifestInternalInconsistencyError("Pipeline manifest root must be a mapping")
    manifest = PipelineManifest.model_validate(raw)
    _enforce_internal_invariants(manifest)
    return manifest


def step_map(manifest: PipelineManifest) -> MappingProxyType[str, StepEntry]:
    """Return immutable id->step mapping."""
    return MappingProxyType({step.id: step for step in manifest.steps})


def hud_steps(manifest: PipelineManifest) -> list[dict[str, str]]:
    """Build HUD-compatible step dictionaries."""
    return [
        {"id": step.id, "name": step.label, "gate": "yes" if step.gate else "no"}
        for step in manifest.steps
        if step.hud_tracked
    ]

