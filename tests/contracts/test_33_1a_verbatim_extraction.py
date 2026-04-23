"""Contract: extracted section prose stays verbatim to v4.2 source."""

from __future__ import annotations

from pathlib import Path

from scripts.generators.v42.env import make_env
from scripts.generators.v42.manifest import load_generator_manifest
from scripts.utilities.workflow_policy import load_workflow_policy

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "state/config/pipeline-manifest.yaml"
SOURCE = ROOT / (
    "docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md"
)


def test_existing_sections_match_source_pack_byte_identical() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    gm = load_generator_manifest(MANIFEST)
    workflow_policy = load_workflow_policy()
    env = make_env()
    audience_macros = env.get_template("macros/audience_tag.j2").module
    for step in gm.steps:
        if step.id == "04.55":
            continue
        rendered = env.get_template(step.template_name).render(
            step=step,
            audience=audience_macros.audience,
            workflow_policy=workflow_policy,
            **workflow_policy,
        ).strip()
        assert rendered in source, f"Template prose drift for {step.id}"
