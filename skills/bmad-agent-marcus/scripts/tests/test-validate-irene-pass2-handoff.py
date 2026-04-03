from __future__ import annotations

import json
import subprocess
import sys
from importlib import util
from pathlib import Path

import pytest

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
                }
            ],
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
