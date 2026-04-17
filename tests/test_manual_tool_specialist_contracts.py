"""Contract checks for Story 5.1 manual-tool specialists."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "skills" / "bmad-agent-marcus" / "references" / "specialist-registry.yaml"
)


SPECIALISTS = {
    "vyond": {
        "identifier": "vyond-specialist",
        "skill": ROOT / "skills" / "bmad-agent-vyond" / "SKILL.md",
        "sidecar": ROOT / "_bmad" / "memory" / "vyx-sidecar",
        "interaction_guide": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-vyond"
        / "interaction-test-guide.md",
        "review_signoff": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-vyond"
        / "review-sign-off.md",
        "guidance_sample": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-vyond"
        / "sample-guidance-response.yaml",
        "blocked_sample": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-vyond"
        / "sample-blocked-response.yaml",
    },
    "midjourney": {
        "identifier": "midjourney-specialist",
        "skill": ROOT / "skills" / "bmad-agent-midjourney" / "SKILL.md",
        "sidecar": ROOT / "_bmad" / "memory" / "mira-sidecar",
        "interaction_guide": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-midjourney"
        / "interaction-test-guide.md",
        "review_signoff": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-midjourney"
        / "review-sign-off.md",
        "guidance_sample": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-midjourney"
        / "sample-guidance-response.yaml",
        "blocked_sample": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-midjourney"
        / "sample-blocked-response.yaml",
    },
    "articulate": {
        "identifier": "articulate-specialist",
        "skill": ROOT / "skills" / "bmad-agent-articulate" / "SKILL.md",
        "sidecar": ROOT / "_bmad" / "memory" / "aria-sidecar",
        "interaction_guide": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-articulate"
        / "interaction-test-guide.md",
        "review_signoff": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-articulate"
        / "review-sign-off.md",
        "guidance_sample": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-articulate"
        / "sample-guidance-response.yaml",
        "blocked_sample": ROOT
        / "tests"
        / "agents"
        / "bmad-agent-articulate"
        / "sample-blocked-response.yaml",
    },
}

EXPECTED_RETURN_FIELDS = {
    "vyond": [
        "status",
        "recommended_workflow",
        "step_by_step_instructions",
        "storyboard_payload",
        "human_review_required",
        "warnings",
        "blockers",
    ],
    "midjourney": [
        "status",
        "recommended_workflow",
        "prompt_packages",
        "iteration_log",
        "step_by_step_instructions",
        "human_review_required",
        "warnings",
        "blockers",
    ],
    "articulate": [
        "status",
        "recommended_workflow",
        "step_by_step_instructions",
        "review_checklists",
        "human_review_required",
        "warnings",
        "blockers",
    ],
}

WCAG_REQUIRED_CRITERIA = {
    "2.1.1",
    "2.1.2",
    "2.4.3",
    "2.4.7",
    "1.4.3",
    "1.4.10",
    "1.3.1",
    "1.3.2",
    "1.1.1",
    "3.3.2",
}


def test_manual_tool_skills_exist_and_declared() -> None:
    for specialist, paths in SPECIALISTS.items():
        content = paths["skill"].read_text(encoding="utf-8")
        assert "manual-tool" in content.lower(), specialist
        assert "no api" in content.lower() or "no api client" in content.lower(), specialist
        assert "human_review_required" in content, specialist
        for field in EXPECTED_RETURN_FIELDS[specialist]:
            assert field in content, f"{specialist}: missing {field} in skill return contract"


def test_manual_tool_specialists_are_registered() -> None:
    expected_routes = {
        "vyond-specialist": "skills/bmad-agent-vyond/SKILL.md",
        "midjourney-specialist": "skills/bmad-agent-midjourney/SKILL.md",
        "articulate-specialist": "skills/bmad-agent-articulate/SKILL.md",
    }

    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    specialists = registry.get("specialists", {})

    for _, paths in SPECIALISTS.items():
        specialist_id = paths["identifier"]
        assert specialist_id in specialists
        assert specialists[specialist_id].get("path") == expected_routes[specialist_id]


def test_sidecars_and_interaction_guides_exist() -> None:
    for specialist, paths in SPECIALISTS.items():
        sidecar = paths["sidecar"]
        for name in ["index.md", "patterns.md", "chronology.md", "access-boundaries.md"]:
            assert (sidecar / name).exists(), f"{specialist}: missing {name}"

        assert paths["interaction_guide"].exists(), f"{specialist}: missing guide"
        assert paths["review_signoff"].exists(), f"{specialist}: missing review signoff"
        assert paths["guidance_sample"].exists(), f"{specialist}: missing guidance sample"
        assert paths["blocked_sample"].exists(), f"{specialist}: missing blocked sample"


def test_sample_payloads_cover_guidance_and_blocked_behavior() -> None:
    for specialist, paths in SPECIALISTS.items():
        guidance_payload = yaml.safe_load(paths["guidance_sample"].read_text(encoding="utf-8"))
        blocked_payload = yaml.safe_load(paths["blocked_sample"].read_text(encoding="utf-8"))

        for required_field in EXPECTED_RETURN_FIELDS[specialist]:
            assert required_field in guidance_payload, (
                f"{specialist}: guidance missing {required_field}"
            )
            assert required_field in blocked_payload, (
                f"{specialist}: blocked missing {required_field}"
            )

        assert guidance_payload["status"] == "guidance-ready", specialist
        assert blocked_payload["status"] == "blocked", specialist
        assert guidance_payload["human_review_required"] is True, specialist
        assert blocked_payload["human_review_required"] is True, specialist

        assert isinstance(guidance_payload["step_by_step_instructions"], list), specialist
        assert len(guidance_payload["step_by_step_instructions"]) >= 3, specialist
        assert isinstance(blocked_payload["step_by_step_instructions"], list), specialist
        assert len(blocked_payload["step_by_step_instructions"]) >= 3, specialist

        assert len(guidance_payload["recommended_workflow"].strip()) >= 20, specialist
        assert len(blocked_payload["recommended_workflow"].strip()) >= 20, specialist
        assert isinstance(guidance_payload["warnings"], list) and guidance_payload[
            "warnings"
        ], specialist
        assert isinstance(blocked_payload["warnings"], list) and blocked_payload[
            "warnings"
        ], specialist
        assert guidance_payload["blockers"] == [], specialist

        assert isinstance(blocked_payload["blockers"], list), specialist
        assert len(blocked_payload["blockers"]) >= 1, specialist
        assert blocked_payload.get("route_to") == "marcus", specialist
        assert all(len(item.strip()) >= 10 for item in blocked_payload["blockers"]), specialist

        if specialist == "midjourney":
            iteration_log = guidance_payload["iteration_log"]
            assert isinstance(iteration_log, list) and len(iteration_log) >= 2
            for row in iteration_log:
                assert row.get("run_id")
                assert row.get("seed") is not None
                assert row.get("parameter_delta")
                assert row.get("rationale")
                assert row.get("model_version") in {"v6", "v7"}
            for pkg in guidance_payload["prompt_packages"]:
                assert pkg.get("model_version") in {"v6", "v7"}
                assert "--seed" in pkg.get("parameters", "")
                assert "--no" in pkg.get("parameters", "")

        if specialist == "vyond":
            scenes = guidance_payload["storyboard_payload"]["scenes"]
            assert isinstance(scenes, list) and len(scenes) >= 2
            for scene in scenes:
                assert scene.get("scene_id")
                assert scene.get("duration_seconds", 0) > 0
                assert scene.get("objective_signal")

        if specialist == "articulate":
            review_checklists = guidance_payload["review_checklists"]
            assert review_checklists.get("scorm")
            wcag_entries = review_checklists.get("wcag")
            assert isinstance(wcag_entries, list) and len(wcag_entries) >= len(
                WCAG_REQUIRED_CRITERIA
            )
            covered = {entry.get("criterion") for entry in wcag_entries}
            assert WCAG_REQUIRED_CRITERIA.issubset(covered)
            for entry in wcag_entries:
                assert entry.get("result") in {"pass", "fail"}
                assert entry.get("evidence_path")


def test_interaction_guides_include_behavioral_and_review_gates() -> None:
    for specialist, paths in SPECIALISTS.items():
        guide = paths["interaction_guide"].read_text(encoding="utf-8")
        assert "Scenario" in guide, specialist
        assert "Expect:" in guide, specialist
        assert "Human review gate" in guide, specialist
        assert guide.count("## Scenario") >= 5, specialist


def test_review_signoff_artifacts_include_required_fields() -> None:
    required_markers = [
        "Story:",
        "Reviewer:",
        "Reviewer Role:",
        "Date:",
        "Approval Timestamp:",
        "Outcome:",
        "Evidence Links:",
        "Checks:",
    ]

    for specialist, paths in SPECIALISTS.items():
        signoff = paths["review_signoff"].read_text(encoding="utf-8")
        for marker in required_markers:
            assert marker in signoff, f"{specialist}: missing {marker} in review signoff"
        assert "approved" in signoff.lower(), f"{specialist}: signoff outcome must be approved"
        assert "Party-mode panel" not in signoff
        assert "reviewer: " in signoff.lower()


def test_articulate_wcag_and_scorm_references_are_present() -> None:
    skill_content = (ROOT / "skills" / "bmad-agent-articulate" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    scorm_content = (
        ROOT
        / "skills"
        / "bmad-agent-articulate"
        / "references"
        / "scorm-export-review-checklist.md"
    ).read_text(encoding="utf-8")
    wcag_file = (
        ROOT
        / "skills"
        / "bmad-agent-articulate"
        / "references"
        / "wcag-2-1-aa-interactive-checklist.md"
    )
    wcag_content = wcag_file.read_text(encoding="utf-8")

    assert "wcag-2-1-aa-interactive-checklist.md" in skill_content
    assert wcag_file.exists()
    assert "gradebook" in scorm_content.lower()
    assert "Verification Matrix" in wcag_content
    for criterion in WCAG_REQUIRED_CRITERIA:
        assert criterion in wcag_content, f"missing WCAG criterion {criterion}"


def test_midjourney_parameter_depth_and_iteration_schema() -> None:
    param_catalog = (
        ROOT
        / "skills"
        / "bmad-agent-midjourney"
        / "references"
        / "parameter-catalog-v6-v7.md"
    ).read_text(encoding="utf-8")
    sidecar_patterns = (
        ROOT
        / "_bmad"
        / "memory"
        / "mira-sidecar"
        / "patterns.md"
    ).read_text(encoding="utf-8")
    sidecar_chronology = (
        ROOT
        / "_bmad"
        / "memory"
        / "mira-sidecar"
        / "chronology.md"
    ).read_text(encoding="utf-8")

    assert "Iteration Protocol" in param_catalog
    assert "run_id" in param_catalog
    assert "v6" in param_catalog and "v7" in param_catalog
    assert "guardrails" in param_catalog.lower()
    assert "seed" in sidecar_patterns
    assert "iteration_log" in sidecar_chronology
    structured_entries = [
        line
        for line in sidecar_chronology.splitlines()
        if line.startswith("- run_id:")
    ]
    assert len(structured_entries) >= 3
    for line in structured_entries:
        assert "model:" in line
        assert "seed:" in line
        assert "parameter_delta:" in line
        assert "rationale:" in line
        assert "outcome:" in line


def test_marcus_registry_lists_story_5_1_specialists() -> None:
    marcus = (ROOT / "skills" / "bmad-agent-marcus" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "vyond-specialist" in marcus
    assert "midjourney-specialist" in marcus
    assert "articulate-specialist" in marcus
