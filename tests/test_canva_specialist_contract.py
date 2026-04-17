"""Contract checks for Story 3.8 Canva specialist artifacts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "skills" / "bmad-agent-marcus" / "references" / "specialist-registry.yaml"
)


def test_canva_specialist_skill_exists_with_visual_designer_identity() -> None:
    skill_path = ROOT / "skills" / "bmad-agent-canva" / "SKILL.md"
    assert skill_path.exists()

    content = skill_path.read_text(encoding="utf-8")
    assert "Visual Designer" in content
    assert "manual-tool" in content
    assert "step-by-step" in content


def test_canva_specialist_poll_protocol_is_explicit() -> None:
    content = (ROOT / "skills" / "bmad-agent-canva" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "Poll Response Protocol" in content
    assert "What can you contribute to this production cycle?" in content
    assert "Feasible Canva contribution summary" in content
    assert "Explicit no-API constraints" in content
    assert "Recommended execution path" in content


def test_canva_response_payload_examples_include_decision_fields() -> None:
    specialist = (ROOT / "skills" / "bmad-agent-canva" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    design = (ROOT / "skills" / "canva-design" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "Example payload" in specialist
    assert "proceed_recommendation" in specialist
    assert "estimated_effort_minutes" in specialist
    assert "Example payload" in design
    assert "proceed_recommendation" in design


def test_canva_design_skill_is_knowledge_only() -> None:
    skill_path = ROOT / "skills" / "canva-design" / "SKILL.md"
    assert skill_path.exists()

    content = skill_path.read_text(encoding="utf-8")
    assert "Knowledge-only" in content or "knowledge-only" in content
    assert "No scripts directory" in content

    assert not (ROOT / "skills" / "canva-design" / "scripts").exists()


def test_canva_references_exist() -> None:
    refs_root = ROOT / "skills" / "canva-design" / "references"
    expected = [
        "capability-catalog.md",
        "template-catalog.md",
        "pptx-import-workflow.md",
    ]

    for name in expected:
        assert (refs_root / name).exists(), f"Missing reference: {name}"


def test_canva_sidecar_initialized_with_boundaries() -> None:
    sidecar = ROOT / "_bmad" / "memory" / "tamara-sidecar"
    expected = ["index.md", "patterns.md", "chronology.md", "access-boundaries.md"]

    for name in expected:
        assert (sidecar / name).exists(), f"Missing sidecar file: {name}"

    boundaries = (sidecar / "access-boundaries.md").read_text(encoding="utf-8")
    assert "## Read" in boundaries
    assert "## Write" in boundaries
    assert "## Deny" in boundaries


def test_marcus_lists_canva_specialist_as_active() -> None:
    # Epic 26 migration: the External Specialist Agents table moved from
    # Marcus's SKILL.md to references/external-specialist-registry.md.
    registry = (
        ROOT / "skills" / "bmad-agent-marcus" / "references"
        / "external-specialist-registry.md"
    ).read_text(encoding="utf-8")

    assert "canva-specialist" in registry
    assert "active (Story 3.8)" in registry


def test_canva_specialist_registry_mapping_exists() -> None:
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    specialists = registry.get("specialists", {})

    assert "canva-specialist" in specialists
    assert specialists["canva-specialist"]["path"] == "skills/bmad-agent-canva/SKILL.md"


def test_canva_config_precedence_rule_is_documented() -> None:
    specialist = (ROOT / "skills" / "bmad-agent-canva" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    design = (ROOT / "skills" / "canva-design" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "Configuration precedence" in specialist
    assert "Configuration precedence" in design
