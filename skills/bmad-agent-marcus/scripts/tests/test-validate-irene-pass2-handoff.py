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
            {"slide_id": "s-1", "sensory_bridge": "Bridge text"},
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
            {"slide_id": "s-1", "sensory_bridge": "Bridge one"},
            {"slide_id": "s-2", "sensory_bridge": "Bridge two"},
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
            {"slide_id": "s-1"},
            {"slide_id": "s-2"},
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
            {"slide_id": "s-1"},
            {"slide_id": "s-2"},
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
                "perception_artifacts": [{"slide_id": "s-1"}],
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
