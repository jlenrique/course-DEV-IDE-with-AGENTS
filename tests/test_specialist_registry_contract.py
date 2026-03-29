from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-not-found]

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "skills" / "bmad-agent-marcus" / "references" / "specialist-registry.yaml"

REQUIRED_SPECIALISTS = {
    "content-creator",
    "gamma-specialist",
    "kling-specialist",
    "elevenlabs-specialist",
    "vyond-specialist",
    "midjourney-specialist",
    "articulate-specialist",
    "compositor",
    "fidelity-assessor",
    "quality-reviewer",
    "canva-specialist",
    "canvas-specialist",
    "qualtrics-specialist",
    "coursearc-specialist",
}


def _load_registry() -> dict:
    payload = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_specialist_registry_exists_and_has_specialists_map() -> None:
    assert REGISTRY_PATH.exists()
    payload = _load_registry()
    assert payload.get("version") == 1
    assert isinstance(payload.get("specialists"), dict)


def test_specialist_registry_contains_required_specialists() -> None:
    specialists = _load_registry()["specialists"]
    missing = REQUIRED_SPECIALISTS - set(specialists.keys())
    assert not missing, f"Missing specialist registry entries: {sorted(missing)}"


def test_specialist_registry_paths_are_skills_and_exist() -> None:
    specialists = _load_registry()["specialists"]
    for specialist, entry in specialists.items():
        path = entry.get("path")
        assert isinstance(path, str) and path, specialist
        assert path.startswith("skills/"), f"{specialist}: non-skills path {path}"
        assert path.endswith("/SKILL.md"), f"{specialist}: path must target SKILL.md"
        assert not path.startswith("agents/"), f"{specialist}: legacy agents path {path}"
        assert (ROOT / path).exists(), f"{specialist}: missing target {path}"


def test_delegation_docs_reference_registry_not_stub_fallbacks() -> None:
    conversation_mgmt = (
        ROOT / "skills" / "bmad-agent-marcus" / "references" / "conversation-mgmt.md"
    ).read_text(encoding="utf-8")
    delegation_protocol = (
        ROOT / "skills" / "production-coordination" / "references" / "delegation-protocol.md"
    ).read_text(encoding="utf-8")

    for content in (conversation_mgmt, delegation_protocol):
        assert "specialist-registry.yaml" in content
        assert "agents/{name}.md" not in content


def test_root_agent_stub_files_are_removed() -> None:
    legacy_stubs = [
        "agents/articulate-specialist.md",
        "agents/canva-specialist.md",
        "agents/canvas-specialist.md",
        "agents/coursearc-specialist.md",
        "agents/midjourney-specialist.md",
        "agents/qualtrics-specialist.md",
        "agents/vyond-specialist.md",
    ]
    for rel_path in legacy_stubs:
        assert not (ROOT / rel_path).exists(), f"Legacy stub still present: {rel_path}"
