from __future__ import annotations

import json
from pathlib import Path

from pathlib import Path

import pytest

from scripts.utilities.marcus_prompt_harness import (
    CLUSTER_GATE_STEP_HEADING,
    MOTION_STEP_HEADINGS,
    STANDARD_STEP_HEADINGS,
    _step_headings,
    build_consistency_findings,
    build_step_reports,
    infer_context,
    render_quinn_report,
)
from scripts.utilities.run_constants import RunConstantsError

_ROOT = Path(__file__).resolve().parents[1]


def test_cluster_gate_heading_constant_is_correct() -> None:
    assert CLUSTER_GATE_STEP_HEADING == "5B) Cluster Plan G1.5 Gate + Operator Review"


def test_standard_step_headings_does_not_include_5b_by_default() -> None:
    # 5B is a conditional gate excluded from positional index tuples by design.
    # It is documented via CLUSTER_GATE_STEP_HEADING and the prompt packs.
    assert CLUSTER_GATE_STEP_HEADING not in STANDARD_STEP_HEADINGS


def test_motion_step_headings_does_not_include_5b_by_default() -> None:
    assert CLUSTER_GATE_STEP_HEADING not in MOTION_STEP_HEADINGS


def test_cluster_step_headings_includes_5b_for_cluster_runs(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _write(
        bundle_dir / "run-constants.yaml",
        "\n".join(
            [
                "schema_version: 1",
                'frozen_at_utc: "2026-04-05T00:00:00Z"',
                "run_id: C1-M1-PRES-20260405",
                "lesson_slug: apc-c1m1-tejal",
                f"bundle_path: {bundle_dir.as_posix()}",
                "primary_source_file: C:/example/source.pdf",
                "optional_context_assets: none",
                "theme_selection: hil-2026-apc-nejal-A",
                "theme_paramset_key: hil-2026-apc-nejal-A",
                "execution_mode: tracked/default",
                "quality_preset: production",
                "double_dispatch: false",
                "motion_enabled: false",
                "cluster_density: sparse",
            ]
        ),
    )

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    headings = _step_headings(context)

    assert CLUSTER_GATE_STEP_HEADING in headings
    # Should be after 5
    index_5 = next(i for i, h in enumerate(headings) if h.startswith("5) "))
    index_5b = next(i for i, h in enumerate(headings) if h == CLUSTER_GATE_STEP_HEADING)
    assert index_5b == index_5 + 1


def test_non_cluster_step_headings_excludes_5b(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _write(
        bundle_dir / "run-constants.yaml",
        "\n".join(
            [
                "schema_version: 1",
                'frozen_at_utc: "2026-04-05T00:00:00Z"',
                "run_id: C1-M1-PRES-20260405",
                "lesson_slug: apc-c1m1-tejal",
                f"bundle_path: {bundle_dir.as_posix()}",
                "primary_source_file: C:/example/source.pdf",
                "optional_context_assets: none",
                "theme_selection: hil-2026-apc-nejal-A",
                "theme_paramset_key: hil-2026-apc-nejal-A",
                "execution_mode: tracked/default",
                "quality_preset: production",
                "double_dispatch: false",
                "motion_enabled: false",
                "cluster_density: none",
            ]
        ),
    )

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    headings = _step_headings(context)

    assert CLUSTER_GATE_STEP_HEADING not in headings


def test_prompt_pack_v41_contains_cluster_gate_step() -> None:
    pack = (_ROOT / "docs" / "workflow" / "production-prompt-pack-v4.1-narrated-deck-video-export.md").read_text(encoding="utf-8")
    assert "5B) Cluster Plan G1.5 Gate + Operator Review" in pack


def test_prompt_pack_v42_contains_cluster_gate_step() -> None:
    pack = (_ROOT / "docs" / "workflow" / "production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md").read_text(encoding="utf-8")
    assert "5B) Cluster Plan G1.5 Gate + Operator Review" in pack


def test_prompt_pack_v42_contains_plain_language_profile_selection_step() -> None:
    pack = (_ROOT / "docs" / "workflow" / "production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md").read_text(encoding="utf-8")
    assert "Should the visuals lead, or should the text lead for this lesson?" in pack
    assert "experience_profile: visual-led" in pack
    assert "experience_profile: text-led" in pack


def test_conversation_management_maps_plain_language_profile_selection() -> None:
    guidance = (_ROOT / "skills" / "bmad-agent-marcus" / "references" / "conversation-mgmt.md").read_text(encoding="utf-8")
    assert "Should the visuals lead, or should the text lead for this lesson?" in guidance
    assert "`visual-led`" in guidance
    assert "`text-led`" in guidance
    assert "Do not expose the internal term `experience_profile` to the operator." in guidance


def test_cd_skill_declares_marcus_only_intake_contract() -> None:
    skill = (_ROOT / "skills" / "bmad-agent-cd" / "SKILL.md").read_text(encoding="utf-8")
    assert "## Intake Contract" in skill
    assert "Marcus's envelope" in skill
    assert "returns structured output only to Marcus" in skill


def test_c1_m1_storyboard_html_remains_view_only_for_profile_selection() -> None:
    html = (
        _ROOT
        / "course-content"
        / "staging"
        / "tracked"
        / "source-bundles"
        / "apc-c1m1-tejal-20260406-motion"
        / "storyboard"
        / "index.html"
    ).read_text(encoding="utf-8").lower()
    assert "experience_profile" not in html
    assert "visual-led" not in html
    assert "text-led" not in html
    assert "visuals lead" not in html
    assert "text lead" not in html


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _minimal_run_constants(bundle_dir: Path) -> None:
    _write(
        bundle_dir / "run-constants.yaml",
        "\n".join(
            [
                "schema_version: 1",
                'frozen_at_utc: "2026-04-05T00:00:00Z"',
                "run_id: C1-M1-PRES-20260405",
                "lesson_slug: apc-c1m1-tejal",
                f"bundle_path: {bundle_dir.as_posix()}",
                "primary_source_file: C:/example/source.pdf",
                "optional_context_assets: none",
                "theme_selection: hil-2026-apc-nejal-A",
                "theme_paramset_key: hil-2026-apc-nejal-A",
                "execution_mode: tracked/default",
                "quality_preset: production",
                "double_dispatch: false",
                "motion_enabled: false",
            ]
        ),
    )


def _profile_run_constants(bundle_dir: Path, *, experience_profile: str) -> None:
    _write(
        bundle_dir / "run-constants.yaml",
        "\n".join(
            [
                "schema_version: 1",
                'frozen_at_utc: "2026-04-14T00:00:00Z"',
                "run_id: C1-M1-PRES-20260414",
                "lesson_slug: apc-c1m1-tejal",
                f"bundle_path: {bundle_dir.as_posix()}",
                "primary_source_file: C:/example/source.pdf",
                "optional_context_assets: none",
                "theme_selection: hil-2026-apc-nejal-A",
                "theme_paramset_key: hil-2026-apc-nejal-A",
                "execution_mode: tracked/default",
                "quality_preset: production",
                "double_dispatch: false",
                "motion_enabled: false",
                f"experience_profile: {experience_profile}",
            ]
        ),
    )


def test_infer_context_prefers_run_constants(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _minimal_run_constants(bundle_dir)

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)

    assert context.run_id == "C1-M1-PRES-20260405"
    assert context.lesson_slug == "apc-c1m1-tejal"
    assert context.field_sources["run_id"] == "run-constants.yaml"
    assert context.double_dispatch is False
    assert context.motion_enabled is False


def test_infer_context_captures_experience_profile_from_run_constants(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _profile_run_constants(bundle_dir, experience_profile="visual-led")

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)

    assert context.experience_profile == "visual-led"
    assert context.field_sources["experience_profile"] == "run-constants.yaml"


def test_infer_context_derives_cluster_density_from_experience_profile(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _profile_run_constants(bundle_dir, experience_profile="text-led")

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)

    assert context.experience_profile == "text-led"
    assert context.cluster_density == "rich"
    assert context.field_sources["cluster_density"] == "run-constants.yaml"


def test_profile_derived_cluster_density_includes_5b_step(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _profile_run_constants(bundle_dir, experience_profile="visual-led")

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    headings = _step_headings(context)

    assert context.cluster_density == "default"
    assert CLUSTER_GATE_STEP_HEADING in headings


def test_infer_context_raises_for_invalid_profile_density_contract(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _write(
        bundle_dir / "run-constants.yaml",
        "\n".join(
            [
                "schema_version: 1",
                'frozen_at_utc: "2026-04-14T00:00:00Z"',
                "run_id: C1-M1-PRES-20260414",
                "lesson_slug: apc-c1m1-tejal",
                f"bundle_path: {bundle_dir.as_posix()}",
                "primary_source_file: C:/example/source.pdf",
                "optional_context_assets: none",
                "theme_selection: hil-2026-apc-nejal-A",
                "theme_paramset_key: hil-2026-apc-nejal-A",
                "execution_mode: tracked/default",
                "quality_preset: production",
                "double_dispatch: false",
                "motion_enabled: false",
                "experience_profile: text-led",
                "cluster_density: default",
            ]
        ),
    )

    with pytest.raises(RunConstantsError, match="cluster_density must match the resolved experience_profile values"):
        infer_context(root=tmp_path, bundle_dir=bundle_dir)


def test_build_step_reports_marks_prompt_2_inferred_without_direct_map(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _minimal_run_constants(bundle_dir)
    _write(bundle_dir / "ingestion-evidence.md", "# evidence")
    _write(bundle_dir / "metadata.json", json.dumps({"source": "ok"}))

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    reports = build_step_reports(context)
    prompt2 = next(item for item in reports if item.step == "2")

    assert prompt2.status == "INFERRED"
    assert "ingestion-evidence.md present" in prompt2.evidence


def test_build_consistency_findings_detects_run_id_drift(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _minimal_run_constants(bundle_dir)
    _write(
        bundle_dir / "preflight-results.json",
        json.dumps({"run_id": "C1-M1-PRES-20260406", "gate": {"overall_status": "pass"}}),
    )

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    findings = build_consistency_findings(context)

    assert findings == [
        "preflight-results.json run_id=C1-M1-PRES-20260406 does not match canonical run_id=C1-M1-PRES-20260405"
    ]


def test_render_quinn_report_includes_step_summary(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _minimal_run_constants(bundle_dir)
    _write(
        bundle_dir / "preflight-results.json",
        json.dumps({"run_id": "C1-M1-PRES-20260405", "gate": {"overall_status": "pass"}}),
    )

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    step_reports = build_step_reports(context)
    report = render_quinn_report(
        context=context,
        step_reports=step_reports,
        consistency_findings=[],
    )

    assert "# Quinn Watcher Report" in report
    assert "Overall watcher status:" in report
    assert "| `1` | `PASS` |" in report
    assert "| `8` | `MISSING` |" in report


def test_infer_context_detects_motion_from_run_constants(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _write(
        bundle_dir / "run-constants.yaml",
        "\n".join(
            [
                "schema_version: 1",
                'frozen_at_utc: "2026-04-05T00:00:00Z"',
                "run_id: C1-M1-PRES-20260405",
                "lesson_slug: apc-c1m1-tejal",
                f"bundle_path: {bundle_dir.as_posix()}",
                "primary_source_file: C:/example/source.pdf",
                "optional_context_assets: none",
                "theme_selection: hil-2026-apc-nejal-A",
                "theme_paramset_key: hil-2026-apc-nejal-A",
                "execution_mode: tracked/default",
                "quality_preset: production",
                "double_dispatch: true",
                "motion_enabled: true",
                "motion_budget:",
                "  max_credits: 12",
                "  model_preference: std",
            ]
        ),
    )

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)

    assert context.double_dispatch is True
    assert context.motion_enabled is True
    assert context.field_sources["motion_enabled"] == "run-constants.yaml"


def test_build_step_reports_adds_motion_steps_for_motion_runs(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _write(
        bundle_dir / "run-constants.yaml",
        "\n".join(
            [
                "schema_version: 1",
                'frozen_at_utc: "2026-04-05T00:00:00Z"',
                "run_id: C1-M1-PRES-20260405",
                "lesson_slug: apc-c1m1-tejal",
                f"bundle_path: {bundle_dir.as_posix()}",
                "primary_source_file: C:/example/source.pdf",
                "optional_context_assets: none",
                "theme_selection: hil-2026-apc-nejal-A",
                "theme_paramset_key: hil-2026-apc-nejal-A",
                "execution_mode: tracked/default",
                "quality_preset: production",
                "double_dispatch: true",
                "motion_enabled: true",
                "motion_budget:",
                "  max_credits: 12",
                "  model_preference: std",
            ]
        ),
    )
    _write(bundle_dir / "authorized-storyboard.json", json.dumps({"slide_ids": ["slide-01"]}))
    _write(bundle_dir / "variant-selection.json", json.dumps({"run_id": "C1-M1-PRES-20260405"}))
    _write(bundle_dir / "motion-designations.json", json.dumps({"run_id": "C1-M1-PRES-20260405"}))
    _write(
        bundle_dir / "motion_plan.yaml",
        "\n".join(
            [
                "run_id: C1-M1-PRES-20260405",
                "motion_enabled: true",
                "slides:",
                "  - slide_id: slide-01",
                "    motion_type: video",
                "    motion_status: approved",
                "    motion_asset_path: C:/example/slide-01.mp4",
            ]
        ),
    )
    _write(bundle_dir / "motion-gate-receipt.json", json.dumps({"run_id": "C1-M1-PRES-20260405", "decision": "go"}))
    _write(
        bundle_dir / "pass2-envelope.json",
        json.dumps(
            {
                "run_id": "C1-M1-PRES-20260405",
                "motion_perception_artifacts": {"slide-01": {"artifact_path": "C:/example/slide-01.mp4"}},
            }
        ),
    )
    _write(bundle_dir / "narration-script.md", "# narration")
    _write(bundle_dir / "segment-manifest.yaml", "segments: []")
    _write(bundle_dir / "perception-artifacts.json", json.dumps([]))

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    reports = build_step_reports(context)
    steps = {item.step: item for item in reports}

    assert "7C" in steps
    assert "7D" in steps
    assert "7E" in steps
    assert "7F" in steps
    assert steps["7D"].status == "PASS"
    assert steps["7F"].status == "PASS"
    assert steps["8"].heading == "8) Irene Pass 2 - Motion-Aware Narration + Segment Manifest"


def test_build_step_reports_accepts_list_shaped_motion_perception_artifacts(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _write(
        bundle_dir / "run-constants.yaml",
        "\n".join(
            [
                "schema_version: 1",
                'frozen_at_utc: "2026-04-05T00:00:00Z"',
                "run_id: C1-M1-PRES-20260405",
                "lesson_slug: apc-c1m1-tejal",
                f"bundle_path: {bundle_dir.as_posix()}",
                "primary_source_file: C:/example/source.pdf",
                "optional_context_assets: none",
                "theme_selection: hil-2026-apc-nejal-A",
                "theme_paramset_key: hil-2026-apc-nejal-A",
                "execution_mode: tracked/default",
                "quality_preset: production",
                "double_dispatch: true",
                "motion_enabled: true",
                "motion_budget:",
                "  max_credits: 12",
                "  model_preference: std",
            ]
        ),
    )
    _write(bundle_dir / "authorized-storyboard.json", json.dumps({"slide_ids": ["slide-01"]}))
    _write(bundle_dir / "variant-selection.json", json.dumps({"run_id": "C1-M1-PRES-20260405"}))
    _write(bundle_dir / "motion-designations.json", json.dumps({"run_id": "C1-M1-PRES-20260405"}))
    _write(
        bundle_dir / "motion_plan.yaml",
        "\n".join(
            [
                "run_id: C1-M1-PRES-20260405",
                "motion_enabled: true",
                "slides:",
                "  - slide_id: slide-01",
                "    motion_type: video",
                "    motion_status: approved",
                "    motion_asset_path: C:/example/slide-01.mp4",
            ]
        ),
    )
    _write(bundle_dir / "motion-gate-receipt.json", json.dumps({"run_id": "C1-M1-PRES-20260405", "decision": "go"}))
    _write(
        bundle_dir / "pass2-envelope.json",
        json.dumps(
            {
                "run_id": "C1-M1-PRES-20260405",
                "motion_perception_artifacts": [
                    {"slide_id": "slide-01", "artifact_path": "C:/example/slide-01.mp4"}
                ],
            }
        ),
    )
    _write(bundle_dir / "narration-script.md", "# narration")
    _write(bundle_dir / "segment-manifest.yaml", "segments: []")
    _write(bundle_dir / "perception-artifacts.json", json.dumps([]))

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    reports = build_step_reports(context)
    step8 = next(item for item in reports if item.step == "8")

    assert step8.status == "PASS"
