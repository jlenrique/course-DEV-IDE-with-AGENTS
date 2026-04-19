"""Contract: manifest sections and templates remain in one-to-one coverage."""

from __future__ import annotations

from pathlib import Path

from scripts.generators.v42.manifest import load_generator_manifest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "state/config/pipeline-manifest.yaml"
SECTIONS = ROOT / "scripts/generators/v42/templates/sections"


def test_all_manifest_sections_have_templates() -> None:
    gm = load_generator_manifest(MANIFEST)
    expected = {Path(step.template_name).name for step in gm.steps}
    actual = {p.name for p in SECTIONS.glob("*.md.j2")}
    assert expected == actual
