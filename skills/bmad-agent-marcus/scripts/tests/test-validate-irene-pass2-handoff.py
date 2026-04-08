from __future__ import annotations

import json
import subprocess
import sys
from importlib import util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "validate-irene-pass2-handoff.py"


def _load_script_module():
    spec = util.spec_from_file_location(
        "validate_irene_pass2_handoff_module",
        SCRIPT_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


module = _load_script_module()
validate_irene_pass2_handoff = module.validate_irene_pass2_handoff


def _write_complete_bundle_outputs(
    bundle_dir: Path,
    *,
    slide_ids: list[str],
    gary_slide_output: list[dict[str, object]],
    perception_artifacts: list[dict[str, object]],
    motion: bool = False,
    omit_slide_id: str | None = None,
    empty_narration_segment: str | None = None,
    empty_visual_cue_segment: str | None = None,
    cue_not_in_text_segment: str | None = None,
    wrong_motion_asset: bool = False,
    include_motion_confirmation: bool = True,
    motion_visual_file_uses_motion_asset: bool = False,
) -> dict[str, object]:
    (bundle_dir / "narration-script.md").write_text(
        "# Narration Script\n\nBundle-level validated output.\n",
        encoding="utf-8",
    )

    approved_motion_asset = bundle_dir / "motion-approved.mp4"
    approved_motion_asset.write_bytes(b"mp4")
    wrong_motion_path = bundle_dir / "motion-wrong.mp4"
    wrong_motion_path.write_bytes(b"mp4")

    segments: list[dict[str, object]] = []
    motion_perception_artifacts: list[dict[str, object]] = []
    gary_by_slide_id = {
        str(row.get("slide_id") or ""): row
        for row in gary_slide_output
        if isinstance(row, dict)
    }
    for index, slide_id in enumerate(slide_ids, start=1):
        if slide_id == omit_slide_id:
            continue

        seg_id = f"seg-{index:02d}"
        cue = f"notice cue {index}"
        narration_text = f"{cue} and explain the insight on slide {index}."
        if seg_id == empty_narration_segment:
            narration_text = ""
        if seg_id == cue_not_in_text_segment:
            narration_text = f"Different narration for slide {index}."
        if seg_id == empty_visual_cue_segment:
            cue = ""

        segment: dict[str, object] = {
            "id": seg_id,
            "gary_slide_id": slide_id,
            "gary_card_number": index,
            "narration_text": narration_text,
            "visual_file": str(gary_by_slide_id.get(slide_id, {}).get("file_path") or ""),
            "visual_references": [
                {
                    "element": f"Element {index}",
                    "location_on_slide": "left",
                    "narration_cue": cue,
                    "perception_source": slide_id,
                }
            ],
            "motion_type": "static",
            "motion_asset_path": None,
            "motion_status": None,
        }

        if motion and index == 1:
            segment["motion_type"] = "video"
            segment["motion_status"] = "approved"
            segment["motion_asset_path"] = str(
                wrong_motion_path if wrong_motion_asset else approved_motion_asset
            )
            if motion_visual_file_uses_motion_asset:
                segment["visual_file"] = str(
                    wrong_motion_path if wrong_motion_asset else approved_motion_asset
                )
            if include_motion_confirmation and not wrong_motion_asset:
                motion_perception_artifacts.append(
                    {
                        "segment_id": seg_id,
                        "slide_id": slide_id,
                        "source_motion_path": str(approved_motion_asset),
                    }
                )

        segments.append(segment)

    (bundle_dir / "segment-manifest.yaml").write_text(
        yaml.safe_dump({"segments": segments}, sort_keys=False),
        encoding="utf-8",
    )

    authorized_storyboard = {
        "slide_ids": slide_ids,
        "authorized_slides": [
            {
                "slide_id": row["slide_id"],
                "card_number": row["card_number"],
                "file_path": row["file_path"],
                "source_ref": row["source_ref"],
            }
            for row in gary_slide_output
        ],
    }
    (bundle_dir / "authorized-storyboard.json").write_text(
        json.dumps(authorized_storyboard),
        encoding="utf-8",
    )

    if motion:
        motion_plan = {
            "motion_enabled": True,
            "slides": [
                {
                    "slide_id": slide_ids[0],
                    "motion_type": "video",
                    "motion_asset_path": str(approved_motion_asset),
                    "motion_status": "approved",
                },
                {
                    "slide_id": slide_ids[1],
                    "motion_type": "static",
                    "motion_asset_path": None,
                    "motion_status": None,
                },
            ],
        }
        (bundle_dir / "motion_plan.yaml").write_text(
            yaml.safe_dump(motion_plan, sort_keys=False),
            encoding="utf-8",
        )

    payload: dict[str, object] = {
        "bundle_path": str(bundle_dir),
        "authorized_storyboard_path": str(bundle_dir / "authorized-storyboard.json"),
        "expected_outputs": [
            str(bundle_dir / "narration-script.md"),
            str(bundle_dir / "segment-manifest.yaml"),
            str(bundle_dir / "perception-artifacts.json"),
        ],
    }
    if motion:
        payload["motion_plan_path"] = str(bundle_dir / "motion_plan.yaml")
        if include_motion_confirmation:
            payload["motion_perception_artifacts"] = motion_perception_artifacts

    return payload


def test_fails_when_perception_artifacts_missing() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
        ]
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert "perception_artifacts" in result["missing_fields"]
    assert any("Missing required Pass 2 field" in msg for msg in result["errors"])


def test_fails_when_perception_does_not_cover_all_gary_slide_ids() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
            {
                "slide_id": "s-2",
                "card_number": 2,
                "file_path": "course-content/staging/card-02.png",
                "source_ref": "slide-brief.md#Slide 2",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "sensory_bridge": "Bridge text",
                "source_image_path": "course-content/staging/card-01.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert result["consistency"]["missing_perception_for"] == ["s-2"]


def test_passes_when_required_inputs_present_and_aligned() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
            {
                "slide_id": "s-2",
                "card_number": 2,
                "file_path": "course-content/staging/card-02.png",
                "source_ref": "slide-brief.md#Slide 2",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "sensory_bridge": "Bridge one",
                "source_image_path": "course-content/staging/card-01.png",
            },
            {
                "slide_id": "s-2",
                "sensory_bridge": "Bridge two",
                "source_image_path": "course-content/staging/card-02.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload, expected_artifact_hint="/tmp/perception.json")

    assert result["status"] == "pass"
    assert result["missing_fields"] == []
    assert result["consistency"]["missing_perception_for"] == []
    assert result["order_check"]["strictly_ascending"] is True
    assert result["order_check"]["contiguous_from_one"] is True
    assert "expected location hint" in result["remediation_hint"]


def test_fails_for_non_contiguous_card_numbers() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 2,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
            {
                "slide_id": "s-2",
                "card_number": 3,
                "file_path": "course-content/staging/card-02.png",
                "source_ref": "slide-brief.md#Slide 2",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "course-content/staging/card-01.png",
            },
            {
                "slide_id": "s-2",
                "source_image_path": "course-content/staging/card-02.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert result["order_check"]["strictly_ascending"] is True
    assert result["order_check"]["contiguous_from_one"] is False
    assert any("contiguous and start at 1" in msg for msg in result["errors"])


def test_fails_when_file_path_or_source_ref_missing() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "",
                "source_ref": "slide-brief.md#Slide 1",
            },
            {
                "slide_id": "s-2",
                "card_number": 2,
                "file_path": "course-content/staging/card-02.png",
                "source_ref": "",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "course-content/staging/card-01.png",
            },
            {
                "slide_id": "s-2",
                "source_image_path": "course-content/staging/card-02.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert result["consistency"]["missing_file_path_for"] == ["s-1"]
    assert result["consistency"]["missing_source_ref_for"] == ["s-2"]


@pytest.mark.parametrize(
    ("payload", "expected_exit"),
    [
        (
            {
                "gary_slide_output": [
                    {
                        "slide_id": "s-1",
                        "card_number": 1,
                        "file_path": "course-content/staging/card-01.png",
                        "source_ref": "slide-brief.md#Slide 1",
                    }
                ],
            },
            1,
        ),
        (
            {
                "gary_slide_output": [
                    {
                        "slide_id": "s-1",
                        "card_number": 1,
                        "file_path": "course-content/staging/card-01.png",
                        "source_ref": "slide-brief.md#Slide 1",
                    }
                ],
                "perception_artifacts": [
                    {
                        "slide_id": "s-1",
                        "source_image_path": "course-content/staging/card-01.png",
                    }
                ],
            },
            0,
        ),
    ],
)
def test_cli_exit_code_and_json_output(
    tmp_path: Path,
    payload: dict[str, object],
    expected_exit: int,
) -> None:
    if expected_exit == 0:
        card_path = tmp_path / "card-01.png"
        card_path.write_bytes(b"png")
        payload = {
            **payload,
            "gary_slide_output": [
                {
                    **payload["gary_slide_output"][0],  # type: ignore[index]
                    "file_path": str(card_path),
                }
            ],
            "perception_artifacts": [
                {
                    **payload["perception_artifacts"][0],  # type: ignore[index]
                    "source_image_path": str(card_path),
                    "visual_elements": [{"description": "Element 1"}],
                }
            ],
        }
        payload = {
            **payload,
            **_write_complete_bundle_outputs(
                tmp_path,
                slide_ids=["s-1"],
                gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
                perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            ),
        }

    envelope_path = tmp_path / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--envelope", str(envelope_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == expected_exit
    data = json.loads(proc.stdout)
    assert "status" in data
    assert data["status"] in {"pass", "fail"}


def test_bundle_validation_fails_when_authorized_slide_missing_manifest_segment(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            omit_slide_id="s-2",
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["missing_manifest_for_slide_ids"] == ["s-2"]


def test_bundle_validation_fails_when_segment_narration_text_empty(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            empty_narration_segment="seg-02",
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["segments_missing_narration_text"] == ["seg-02"]


def test_bundle_validation_fails_when_visual_narration_cue_missing(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            empty_visual_cue_segment="seg-02",
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["segments_missing_visual_narration_cue"] == ["seg-02"]


def test_bundle_validation_fails_when_motion_segment_not_bound_to_approved_asset(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            motion=True,
            wrong_motion_asset=True,
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["motion_segments_with_unapproved_asset_binding"] == ["seg-01"]


def test_bundle_validation_passes_with_complete_motion_binding_and_confirmation(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            motion=True,
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "pass"
    assert result["pass2_outputs"]["motion_segments_missing_perception_confirmation"] == []


def test_bundle_validation_fails_when_motion_segment_visual_file_points_to_mp4(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            motion=True,
            motion_visual_file_uses_motion_asset=True,
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["motion_segments_with_noncanonical_visual_file"] == ["seg-01"]


def test_fails_when_perception_source_image_path_missing() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
        ],
        "perception_artifacts": [
            {"slide_id": "s-1", "sensory_bridge": "Bridge one"},
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert any("missing non-empty source_image_path" in msg for msg in result["errors"])


def test_fails_when_perception_source_path_does_not_match_gary_slide() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "course-content/staging/card-99.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert any("must match gary_slide_output.file_path" in msg for msg in result["errors"])


def test_fails_when_gary_file_path_is_remote() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "https://example.org/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "https://example.org/card-01.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert any("must reference local downloaded PNGs" in msg for msg in result["errors"])


def test_cli_fails_when_local_png_missing_on_disk(tmp_path: Path) -> None:
    envelope_path = tmp_path / "pass2-envelope.json"
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "missing/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "missing/card-01.png",
            },
        ],
    }
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--envelope", str(envelope_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert data["status"] == "fail"
    assert any("does not exist on disk" in msg for msg in data.get("errors", []))
