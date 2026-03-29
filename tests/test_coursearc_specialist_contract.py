"""Contract checks for Story 6.1 CourseArc specialist artifacts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_coursearc_skill_exists_with_manual_tool_contract() -> None:
    skill = ROOT / "skills" / "bmad-agent-coursearc" / "SKILL.md"
    assert skill.exists()

    content = skill.read_text(encoding="utf-8")
    assert "manual-tool" in content
    assert "LTI 1.3" in content
    assert "SCORM" in content
    assert "WCAG" in content
    assert "Return Contract" in content
    assert "Evidence Collection Loop" in content
    assert "Scenario Response Templates" in content
    assert "Sorting activity response template" in content
    assert "Flip card response template" in content
    assert "Virtual patient response template" in content


def test_coursearc_reference_guides_exist() -> None:
    refs = ROOT / "skills" / "bmad-agent-coursearc" / "references"
    expected = [
        "lti13-canvas-embedding-checklist.md",
        "lti-role-mapping-and-grading.md",
        "scorm-packaging-specs.md",
        "interactive-block-guidance.md",
        "wcag-interactive-verification.md",
        "evidence-collection-schema.md",
    ]

    for name in expected:
        assert (refs / name).exists(), f"Missing reference: {name}"


def test_coursearc_sidecar_has_boundaries() -> None:
    sidecar = ROOT / "_bmad" / "memory" / "coursearc-specialist-sidecar"
    boundaries = (sidecar / "access-boundaries.md").read_text(encoding="utf-8")

    assert "## Read" in boundaries
    assert "## Write" in boundaries
    assert "## Deny" in boundaries


def test_coursearc_agent_wrapper_exists_for_marcus_delegation() -> None:
    wrapper = ROOT / "agents" / "coursearc-specialist.md"
    assert wrapper.exists()

    content = wrapper.read_text(encoding="utf-8")
    assert "skills/bmad-agent-coursearc/SKILL.md" in content
    assert "status" in content
    assert "evidence_requirements" in content


def test_coursearc_references_include_evidence_expectations() -> None:
    lti = (
        ROOT
        / "skills"
        / "bmad-agent-coursearc"
        / "references"
        / "lti13-canvas-embedding-checklist.md"
    ).read_text(encoding="utf-8")
    scorm = (
        ROOT
        / "skills"
        / "bmad-agent-coursearc"
        / "references"
        / "scorm-packaging-specs.md"
    ).read_text(encoding="utf-8")
    wcag = (
        ROOT
        / "skills"
        / "bmad-agent-coursearc"
        / "references"
        / "wcag-interactive-verification.md"
    ).read_text(encoding="utf-8")

    interaction = (
        ROOT
        / "skills"
        / "bmad-agent-coursearc"
        / "references"
        / "interactive-block-guidance.md"
    ).read_text(encoding="utf-8")
    evidence_schema = (
        ROOT
        / "skills"
        / "bmad-agent-coursearc"
        / "references"
        / "evidence-collection-schema.md"
    ).read_text(encoding="utf-8")

    assert "evidence" in lti.lower()
    assert "Required verification evidence" in scorm
    assert "Completion rule" in wcag
    assert "2.1.1 Keyboard" in wcag
    assert "Reference documentation" in lti
    assert "SCORM technical reference" in scorm
    assert "## Sorting Activities" in interaction
    assert "## Flip Cards" in interaction
    assert "## Virtual Patient Drills" in interaction
    assert "Run ID rules" in evidence_schema
    assert "evidence-index.yaml Template" in evidence_schema


def test_marcus_lists_coursearc_as_active() -> None:
    marcus = (ROOT / "skills" / "bmad-agent-marcus" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "coursearc-specialist" in marcus
    assert "active (Story 6.1)" in marcus
