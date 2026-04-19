"""Contract: extracted section prose stays verbatim to v4.2 source."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.generators.v42.manifest import load_generator_manifest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "state/config/pipeline-manifest.yaml"
SECTIONS = ROOT / "scripts/generators/v42/templates/sections"
SOURCE = ROOT / (
    "docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md"
)


def _strip_jinja(value: str) -> str:
    value = re.sub(r"\{\{.*?\}\}", "", value, flags=re.S)
    value = re.sub(r"\{\%.*?\%\}", "", value, flags=re.S)
    return value.strip()


def test_existing_sections_match_source_pack_byte_identical() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    gm = load_generator_manifest(MANIFEST)
    for step in gm.steps:
        if step.id == "04.55":
            continue
        text = (SECTIONS / Path(step.template_name).name).read_text(encoding="utf-8")
        cleaned = _strip_jinja(text)
        assert cleaned in source, f"Template prose drift for {step.id}"
