from __future__ import annotations

import json
import subprocess
import sys
from importlib import util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "prepare-irene-pass2-handoff.py"


def _load_script_module():
    spec = util.spec_from_file_location(
        "prepare_irene_pass2_handoff_module",
        SCRIPT_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


module = _load_script_module()
prepare_irene_pass2_handoff = module.prepare_irene_pass2_handoff


def _make_bundle(
    tmp_path: Path,
    *,
    double_dispatch: bool = False,
    include_variant_selection: bool = True,
    motion_enabled: bool = False,
    nonstatic_status: str = "approved",
    complete_motion_coverage: bool = True,
    stale_outputs: bool = False,
    static_motion_leftover: bool = False,
) -> Path:
    bundle = tmp_path / "bundle"
    bundle.mkdir()

    slide_01 = bundle / "slide-01.png"
    slide_02 = bundle / "slide-02.png"
    slide_01.write_bytes(b"png")
    slide_02.write_bytes(b"png")

    dispatch_payload = {
        "run_id": "RUN-001",
        "lesson_slug": "lesson-alpha",
        "generation_mode": "double-dispatch" if double_dispatch else "single-dispatch",
        "gary_slide_output": [
            {
                "slide_id": "slide-01",
                "card_number": 1,
                "file_path": str(slide_01),
                "source_ref": "extracted.md#slide-01",
                "visual_description": "Opening slide",
                "fidelity": "creative",
            },
            {
                "slide_id": "slide-02",
                "card_number": 2,
                "file_path": str(slide_02),
                "source_ref": "extracted.md#slide-02",
                "visual_description": "Second slide",
                "fidelity": "literal-text",
            },
        ],
        "literal_visual_publish": {"status": "provenance-only"},
    }
    (bundle / "gary-dispatch-result.json").write_text(
        json.dumps(dispatch_payload),
        encoding="utf-8",
    )

    authorized_storyboard = {
        "run_id": "RUN-001",
        "lesson_slug": "lesson-alpha",
        "slide_ids": ["slide-01", "slide-02"],
        "authorized_slides": [
            {
                "slide_id": "slide-01",
                "card_number": 1,
                "file_path": str(slide_01),
                "source_ref": "extracted.md#slide-01",
                "visual_description": "Opening slide",
                "fidelity": "creative",
            },
            {
                "slide_id": "slide-02",
                "card_number": 2,
                "file_path": str(slide_02),
                "source_ref": "extracted.md#slide-02",
                "visual_description": "Second slide",
                "fidelity": "literal-text",
            },
        ],
    }
    (bundle / "authorized-storyboard.json").write_text(
        json.dumps(authorized_storyboard),
        encoding="utf-8",
    )

    (bundle / "irene-pass1.md").write_text(
        "\n".join(
            [
                "# Irene Pass 1",
                "",
                "## Runtime budget",
                "",
                "| Slide | Target (s) | Cumulative (min) |",
                "|-------|-----------|-----------------|",
                "| 1 | 45 | 0:45 |",
                "| 2 | 35 | 1:20 |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (bundle / "operator-directives.md").write_text("# Operator Directives\n", encoding="utf-8")
    (bundle / "run-constants.yaml").write_text(
        yaml.safe_dump(
            {
                "locked_slide_count": 2,
                "target_total_runtime_minutes": 2,
                "slide_runtime_average_seconds": 40,
                "slide_runtime_variability_scale": 0.5,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    if double_dispatch and include_variant_selection:
        (bundle / "variant-selection.json").write_text(
            json.dumps({"1": "A", "2": "B"}),
            encoding="utf-8",
        )

    if motion_enabled:
        motion_dir = bundle / "motion"
        motion_dir.mkdir()
        approved_asset = motion_dir / "slide-01-motion.mp4"
        approved_asset.write_bytes(b"mp4")
        slides = [
            {
                "slide_id": "slide-01",
                "motion_type": "video",
                "motion_status": nonstatic_status,
                "motion_asset_path": str(approved_asset),
            },
        ]
        if complete_motion_coverage:
            slides.append(
                {
                    "slide_id": "slide-02",
                    "motion_type": "static",
                    "motion_status": None,
                    "motion_asset_path": None,
                }
            )
        motion_plan = {"motion_enabled": True, "slides": slides}
        (bundle / "motion_plan.yaml").write_text(
            yaml.safe_dump(motion_plan, sort_keys=False),
            encoding="utf-8",
        )

        if static_motion_leftover:
            (motion_dir / "slide-02-motion.mp4").write_bytes(b"old-mp4")
            (motion_dir / "slide-02-motion.json").write_text("{}", encoding="utf-8")

    if stale_outputs:
        (bundle / "pass2-envelope.json").write_text("{}", encoding="utf-8")
        (bundle / "narration-script.md").write_text("# stale\n", encoding="utf-8")
        (bundle / "segment-manifest.yaml").write_text("segments: []\n", encoding="utf-8")
        (bundle / "perception-artifacts.json").write_text("[]", encoding="utf-8")

    return bundle


def test_prepares_envelope_with_exact_motion_gate_asset_path(tmp_path: Path) -> None:
    bundle = _make_bundle(tmp_path, motion_enabled=True)

    result = prepare_irene_pass2_handoff(bundle)

    assert result["status"] == "prepared"
    envelope = json.loads((bundle / "pass2-envelope.json").read_text(encoding="utf-8"))
    assert envelope["motion_enabled"] is True
    assert envelope["approved_motion_assets"]["slide-01"].endswith("slide-01-motion.mp4")
    assert envelope["motion_perception_artifacts"] == []
    assert envelope["runtime_plan"]["locked_slide_count"] == 2
    assert envelope["runtime_plan"]["per_slide_targets"][0]["target_runtime_seconds"] == 45.0
    assert envelope["voice_direction_defaults"]["speed"] == 1.0


def test_fails_when_motion_enabled_plan_has_incomplete_authorized_coverage(tmp_path: Path) -> None:
    bundle = _make_bundle(
        tmp_path,
        motion_enabled=True,
        complete_motion_coverage=False,
    )

    result = prepare_irene_pass2_handoff(bundle)

    assert result["status"] == "fail"
    assert any("missing authorized slide coverage" in error for error in result["errors"])


def test_fails_when_nonstatic_motion_row_not_approved(tmp_path: Path) -> None:
    bundle = _make_bundle(
        tmp_path,
        motion_enabled=True,
        nonstatic_status="generated",
    )

    result = prepare_irene_pass2_handoff(bundle)

    assert result["status"] == "fail"
    assert any("must be approved" in error for error in result["errors"])


def test_archives_stale_pass2_outputs_before_writing_fresh_envelope(tmp_path: Path) -> None:
    bundle = _make_bundle(tmp_path, stale_outputs=True)

    result = prepare_irene_pass2_handoff(bundle)

    assert result["status"] == "prepared"
    assert result["archive_dir"] is not None
    archived = result["archived_stale_outputs"]
    assert {Path(entry["source"]).name for entry in archived} >= {
        "pass2-envelope.json",
        "narration-script.md",
        "segment-manifest.yaml",
        "perception-artifacts.json",
    }
    archive_dir = Path(result["archive_dir"])
    assert (archive_dir / "narration-script.md").is_file()
    envelope = json.loads((bundle / "pass2-envelope.json").read_text(encoding="utf-8"))
    assert envelope["handoff_status"] == "prepared-pending-irene-pass2"


def test_reports_non_authoritative_motion_leftovers_for_static_reset_slides(tmp_path: Path) -> None:
    bundle = _make_bundle(
        tmp_path,
        motion_enabled=True,
        static_motion_leftover=True,
    )

    result = prepare_irene_pass2_handoff(bundle)

    assert result["status"] == "prepared"
    leftovers = result["non_authoritative_motion_leftovers"]
    assert any("slide-02-motion.mp4" in entry for entry in leftovers)
    assert any("slide-02-motion.json" in entry for entry in leftovers)


def test_requires_variant_selection_for_double_dispatch(tmp_path: Path) -> None:
    bundle = _make_bundle(
        tmp_path,
        double_dispatch=True,
        include_variant_selection=False,
    )

    result = prepare_irene_pass2_handoff(bundle)

    assert result["status"] == "fail"
    assert any("variant-selection.json is required" in error for error in result["errors"])


def test_envelope_includes_variant_selection_only_when_required(tmp_path: Path) -> None:
    bundle = _make_bundle(
        tmp_path,
        double_dispatch=True,
        include_variant_selection=True,
    )

    result = prepare_irene_pass2_handoff(bundle)

    assert result["status"] == "prepared"
    envelope = json.loads((bundle / "pass2-envelope.json").read_text(encoding="utf-8"))
    assert envelope["variant_selection_path"].endswith("variant-selection.json")


def test_cli_emits_prepared_receipt_and_exit_zero(tmp_path: Path) -> None:
    bundle = _make_bundle(tmp_path, motion_enabled=True)

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--bundle", str(bundle)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["status"] == "prepared"
    assert (bundle / "pass2-prep-receipt.json").is_file()


def test_cli_returns_exit_one_on_invalid_motion_plan(tmp_path: Path) -> None:
    bundle = _make_bundle(
        tmp_path,
        motion_enabled=True,
        nonstatic_status="generated",
    )

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--bundle", str(bundle)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert data["status"] == "fail"


def test_prepares_envelope_when_authorized_storyboard_uses_repo_relative_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "repo-root"
    bundle = repo_root / "course-content" / "staging" / "tracked" / "source-bundles" / "bundle"
    bundle.mkdir(parents=True)

    slide_01 = bundle / "slide-01.png"
    slide_02 = bundle / "slide-02.png"
    slide_01.write_bytes(b"png")
    slide_02.write_bytes(b"png")

    monkeypatch.setattr(module, "REPO_ROOT", repo_root)

    relative_slide_01 = slide_01.relative_to(repo_root)
    relative_slide_02 = slide_02.relative_to(repo_root)

    dispatch_payload = {
        "run_id": "RUN-001",
        "lesson_slug": "lesson-alpha",
        "generation_mode": "single-dispatch",
        "gary_slide_output": [
            {
                "slide_id": "slide-01",
                "card_number": 1,
                "file_path": str(relative_slide_01),
                "source_ref": "extracted.md#slide-01",
                "visual_description": "Opening slide",
                "fidelity": "creative",
            },
            {
                "slide_id": "slide-02",
                "card_number": 2,
                "file_path": str(relative_slide_02),
                "source_ref": "extracted.md#slide-02",
                "visual_description": "Second slide",
                "fidelity": "literal-text",
            },
        ],
    }
    (bundle / "gary-dispatch-result.json").write_text(json.dumps(dispatch_payload), encoding="utf-8")

    authorized_storyboard = {
        "run_id": "RUN-001",
        "lesson_slug": "lesson-alpha",
        "slide_ids": ["slide-01", "slide-02"],
        "authorized_slides": [
            {
                "slide_id": "slide-01",
                "card_number": 1,
                "file_path": str(relative_slide_01),
                "source_ref": "extracted.md#slide-01",
                "visual_description": "Opening slide",
                "fidelity": "creative",
            },
            {
                "slide_id": "slide-02",
                "card_number": 2,
                "file_path": str(relative_slide_02),
                "source_ref": "extracted.md#slide-02",
                "visual_description": "Second slide",
                "fidelity": "literal-text",
            },
        ],
    }
    (bundle / "authorized-storyboard.json").write_text(
        json.dumps(authorized_storyboard),
        encoding="utf-8",
    )
    (bundle / "irene-pass1.md").write_text("# Irene Pass 1\n", encoding="utf-8")
    (bundle / "operator-directives.md").write_text("# Operator Directives\n", encoding="utf-8")

    result = prepare_irene_pass2_handoff(bundle)

    assert result["status"] == "prepared"
    envelope = json.loads((bundle / "pass2-envelope.json").read_text(encoding="utf-8"))
    assert envelope["gary_slide_output"][0]["file_path"] == str(slide_01.resolve())


def test_cli_returns_exception_payload_when_bundle_missing(tmp_path: Path) -> None:
    missing_bundle = tmp_path / "missing"

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--bundle", str(missing_bundle)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 2
    data = json.loads(proc.stdout)
    assert data["status"] == "fail"
    assert any("prepare_exception:" in error for error in data["errors"])
