"""Manifest adapters for v4.2 generator rendering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.utilities.pipeline_manifest import PipelineManifest, StepEntry, load_manifest


@dataclass(frozen=True)
class GeneratorStep:
    """Generator-friendly step projection."""

    id: str
    label: str
    pack_section_anchor: str
    template_name: str
    hud_id: str
    module_path: str
    audience: str
    rationale: str | None
    sub_phase_of: str | None
    insertion_after: str | None


@dataclass(frozen=True)
class GeneratorManifest:
    """Generator input model."""

    schema_version: str
    pack_version: str
    generator_ref: str
    steps: tuple[GeneratorStep, ...]


def _slugify(label: str) -> str:
    import re

    lowered = label.lower().replace("&", " and ").replace("+", " ")
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return re.sub(r"-+", "-", lowered).strip("-")


def _template_name(step: StepEntry) -> str:
    sections_dir = Path(__file__).parent / "templates" / "sections"
    matches = sorted(sections_dir.glob(f"{step.id}-*.md.j2"))
    if not matches:
        return f"sections/{step.id}-{_slugify(step.label)}.md.j2"
    return f"sections/{matches[0].name}"


def _module_path(step: StepEntry) -> str:
    if step.id.startswith("11") or step.id == "12":
        return "skills/bmad-agent-audra"
    if step.id.startswith("07"):
        return "skills/bmad-agent-gary"
    if step.id.startswith("04"):
        return "marcus/orchestrator/loop.py"
    if step.id in {"14", "14.5", "15"}:
        return "skills/bmad-agent-desmond"
    return "scripts/utilities/run_hud.py"


def _audience(step: StepEntry) -> str:
    if step.gate:
        return "M→O"
    if step.sub_phase_of:
        return "M→self"
    return "O→M"


def load_generator_manifest(path: Path) -> GeneratorManifest:
    """Load the canonical manifest and shape steps for renderer loops."""
    manifest: PipelineManifest = load_manifest(path)
    ordered = manifest.steps
    generator_steps = tuple(
        GeneratorStep(
            id=step.id,
            label=step.label,
            pack_section_anchor=step.pack_section_anchor,
            template_name=_template_name(step),
            hud_id=step.id,
            module_path=_module_path(step),
            audience=_audience(step),
            rationale=getattr(step, "rationale", None),
            sub_phase_of=step.sub_phase_of,
            insertion_after=step.insertion_after,
        )
        for step in ordered
    )
    return GeneratorManifest(
        schema_version=manifest.schema_version,
        pack_version=manifest.pack_version,
        generator_ref=manifest.generator_ref,
        steps=generator_steps,
    )
