from __future__ import annotations

import json
import subprocess
import sys
from importlib import util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "validate-gary-dispatch-ready.py"


def _load_script_module():
    spec = util.spec_from_file_location(
        "validate_gary_dispatch_ready_module",
        SCRIPT_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


module = _load_script_module()
validate_gary_dispatch_ready = module.validate_gary_dispatch_ready


def _valid_payload(base_dir: Path | None = None) -> dict[str, object]:
    slide_01 = "course-content/staging/card-01.png"
    slide_02 = "course-content/staging/card-02.png"
    if base_dir is not None:
        card_01 = base_dir / "card-01.png"
        card_02 = base_dir / "card-02.png"
        card_01.write_bytes(b"png")
        card_02.write_bytes(b"png")
        slide_01 = str(card_01)
        slide_02 = str(card_02)

    return {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": slide_01,
                "source_ref": "slide-brief.md#Slide 1",
            },
            {
                "slide_id": "s-2",
                "card_number": 2,
                "file_path": slide_02,
                "source_ref": "slide-brief.md#Slide 2",
            },
        ],
        "quality_assessment": {},
        "parameter_decisions": {},
        "recommendations": [],
        "flags": {},
        "theme_resolution": {
            "requested_theme_key": "hil-2026-apc-nejal-A",
            "resolved_theme_key": "theme_abc",
            "resolved_parameter_set": "hil-2026-apc-nejal-A",
            "mapping_source": "state/config/gamma-style-presets.yaml",
            "mapping_version": "1",
            "user_confirmation": True,
        },
        "dispatch_metadata": {"slides_content_json_path": "gary-slide-content.json"},
    }


def test_passes_when_payload_is_dispatch_ready() -> None:
    result = validate_gary_dispatch_ready(_valid_payload())

    assert result["status"] == "pass"
    assert result["errors"] == []
    assert result["checks"]["slide_count"] == 2
    assert result["checks"]["contiguous_from_one"] is True


def test_fails_when_file_path_missing() -> None:
    payload = _valid_payload()
    payload["gary_slide_output"][1]["file_path"] = ""  # type: ignore[index]

    result = validate_gary_dispatch_ready(payload)

    assert result["status"] == "fail"
    assert any("file_path must be a non-empty string" in msg for msg in result["errors"])


def test_fails_when_source_ref_missing() -> None:
    payload = _valid_payload()
    payload["gary_slide_output"][0]["source_ref"] = ""  # type: ignore[index]

    result = validate_gary_dispatch_ready(payload)

    assert result["status"] == "fail"
    assert any("source_ref must be a non-empty string" in msg for msg in result["errors"])


def test_fails_when_card_sequence_not_contiguous_from_one() -> None:
    payload = _valid_payload()
    payload["gary_slide_output"][0]["card_number"] = 2  # type: ignore[index]
    payload["gary_slide_output"][1]["card_number"] = 3  # type: ignore[index]

    result = validate_gary_dispatch_ready(payload)

    assert result["status"] == "fail"
    assert any("contiguous and start at 1" in msg for msg in result["errors"])


def test_fails_when_file_path_is_remote_url() -> None:
    payload = _valid_payload()
    payload["gary_slide_output"][0]["file_path"] = "https://example.org/slide-01.png"  # type: ignore[index]

    result = validate_gary_dispatch_ready(payload)

    assert result["status"] == "fail"
    assert any("must reference local downloaded PNGs" in msg for msg in result["errors"])


def test_fails_when_file_path_not_png() -> None:
    payload = _valid_payload()
    payload["gary_slide_output"][1]["file_path"] = "course-content/staging/card-02.pdf"  # type: ignore[index]

    result = validate_gary_dispatch_ready(payload)

    assert result["status"] == "fail"
    assert any("must end with .png" in msg for msg in result["errors"])


def test_fails_on_empty_slide_output() -> None:
    payload = _valid_payload()
    payload["gary_slide_output"] = []

    result = validate_gary_dispatch_ready(payload)

    assert result["status"] == "fail"
    assert any("must contain at least one slide" in msg for msg in result["errors"])


@pytest.mark.parametrize(
    ("payload", "expected_exit"),
    [
        (_valid_payload(), 0),
        ({"gary_slide_output": []}, 1),
    ],
)
def test_cli_exit_code_and_json_output(
    tmp_path: Path,
    payload: dict[str, object],
    expected_exit: int,
) -> None:
    dispatch_path = tmp_path / "gary-dispatch-result.json"
    if payload == _valid_payload():
        payload = _valid_payload(tmp_path)
    dispatch_path.write_text(json.dumps(payload), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--payload", str(dispatch_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == expected_exit
    data = json.loads(proc.stdout)
    assert "status" in data
    assert data["status"] in {"pass", "fail"}


def test_cli_accepts_yaml_payload(tmp_path: Path) -> None:
    card_01 = tmp_path / "card-01.png"
    card_02 = tmp_path / "card-02.png"
    card_01.write_bytes(b"png")
    card_02.write_bytes(b"png")
    dispatch_path = tmp_path / "gary-dispatch-result.yaml"
    dispatch_path.write_text(
        "\n".join(
            [
                "gary_slide_output:",
                "  - slide_id: s-1",
                "    card_number: 1",
                f"    file_path: '{card_01}'",
                "    source_ref: slide-brief.md#Slide 1",
                "  - slide_id: s-2",
                "    card_number: 2",
                f"    file_path: '{card_02}'",
                "    source_ref: slide-brief.md#Slide 2",
                "quality_assessment: {}",
                "parameter_decisions: {}",
                "recommendations: []",
                "flags: {}",
                "theme_resolution:",
                "  requested_theme_key: hil-2026-apc-nejal-A",
                "  resolved_theme_key: theme_abc",
                "  resolved_parameter_set: hil-2026-apc-nejal-A",
                "  mapping_source: state/config/gamma-style-presets.yaml",
                "  mapping_version: '1'",
                "  user_confirmation: true",
                "dispatch_metadata:",
                "  slides_content_json_path: gary-slide-content.json",
            ]
        ),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--payload", str(dispatch_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["status"] == "pass"


def test_fails_when_dispatch_metadata_absent() -> None:
    payload = _valid_payload()
    del payload["dispatch_metadata"]  # type: ignore[attr-defined]

    result = validate_gary_dispatch_ready(payload)

    assert result["status"] == "fail"
    assert any("dispatch_metadata must be present" in msg for msg in result["errors"])


def test_fails_when_slides_content_json_path_empty() -> None:
    payload = _valid_payload()
    payload["dispatch_metadata"] = {"slides_content_json_path": ""}  # type: ignore[index]

    result = validate_gary_dispatch_ready(payload)

    assert result["status"] == "fail"
    assert any("slides_content_json_path must be non-empty" in msg for msg in result["errors"])


def test_fails_when_source_crop_card_uses_generated_asset(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)
    (bundle_dir / "irene-pass1.md").write_text(
        "\n".join(
            [
                "## literal-visual spec cards",
                "",
                "### LV-01",
                "",
                "- slide_number: 2",
                "- source_asset: `metadata.json#media_references[2]`",
                "- image_treatment: source-crop",
                "- layout_constraint: full-width primary visual with no redrawn substitute",
            ]
        ),
        encoding="utf-8",
    )
    (bundle_dir / "gary-diagram-cards.json").write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "cards": [
                    {
                        "card_number": 2,
                        "image_url": "https://cdn.gamma.app/generated-images/example.png",
                        "placement_note": "Primary visual, full-width roadmap.",
                        "required": True,
                        "source_asset": "`metadata.json#media_references[2]`",
                        "derivation_type": "source-crop",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_gary_dispatch_ready(
        payload,
        payload_path=bundle_dir / "gary-dispatch-result.json",
    )

    assert result["status"] == "fail"
    assert any("generated-images asset" in msg for msg in result["errors"])


def test_passes_when_source_crop_card_uses_source_derived_asset(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)
    (bundle_dir / "irene-pass1.md").write_text(
        "\n".join(
            [
                "## literal-visual spec cards",
                "",
                "### LV-01",
                "",
                "- slide_number: 15",
                "- source_asset: `metadata.json#media_references[2]`",
                "- image_treatment: source-crop",
                "- layout_constraint: crop must keep C1 and C2 labels visible at the same time",
            ]
        ),
        encoding="utf-8",
    )
    (bundle_dir / "gary-diagram-cards.json").write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "cards": [
                    {
                        "card_number": 15,
                        "image_url": "https://cdn.gamma.app/design-anything/example.png",
                        "placement_note": "Bridge crop.",
                        "required": True,
                        "source_asset": "`metadata.json#media_references[2]`",
                        "derivation_type": "source-crop",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_gary_dispatch_ready(
        payload,
        payload_path=bundle_dir / "gary-dispatch-result.json",
    )

    assert result["status"] == "pass"


def test_cli_returns_exception_payload_on_malformed_json(tmp_path: Path) -> None:
        dispatch_path = tmp_path / "bad.json"
        dispatch_path.write_text("{not-json", encoding="utf-8")

        proc = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--payload", str(dispatch_path)],
                capture_output=True,
                text=True,
                check=False,
        )

        assert proc.returncode == 2
        data = json.loads(proc.stdout)
        assert data["status"] == "fail"
        assert any("validator_exception:" in msg for msg in data.get("errors", []))


def test_fails_when_local_slide_png_missing_on_disk(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload()

    result = validate_gary_dispatch_ready(
        payload,
        payload_path=bundle_dir / "gary-dispatch-result.json",
    )

    assert result["status"] == "fail"
    assert any("does not exist on disk" in msg for msg in result["errors"])


def test_fails_when_preintegration_cards_missing_publish_receipt(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)

    (bundle_dir / "irene-pass1.md").write_text(
        "\n".join(
            [
                "## literal-visual spec cards",
                "",
                "### LV-01",
                "",
                "- slide_number: 2",
                "- source_asset: `metadata.json#media_references[2]`",
                "- image_treatment: source-crop",
                "- layout_constraint: full-width primary visual with no redrawn substitute",
            ]
        ),
        encoding="utf-8",
    )
    (bundle_dir / "gary-diagram-cards.json").write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "cards": [
                    {
                        "card_number": 2,
                        "preintegration_png_path": "course-content/staging/rebranded-assets/slide-02.png",
                        "source_asset": "`metadata.json#media_references[2]`",
                        "derivation_type": "source-crop",
                        "required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_gary_dispatch_ready(
        payload,
        payload_path=bundle_dir / "gary-dispatch-result.json",
    )

    assert result["status"] == "fail"
    assert any("literal_visual_publish must be present" in msg for msg in result["errors"])


def test_passes_when_preintegration_cards_have_publish_receipt(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)
    payload["dispatch_metadata"] = {
        "slides_content_json_path": "gary-slide-content.json",
        "site_repo_url": "https://github.com/jlenrique/jlenrique.github.io",
        "invocation_mode": "tracked",
    }
    payload["literal_visual_publish"] = {
        "preintegration_ready": True,
        "substituted_cards": [2],
        "url_base": "https://example.github.io/assets/gamma/C1-M1",
    }

    (bundle_dir / "irene-pass1.md").write_text(
        "\n".join(
            [
                "## literal-visual spec cards",
                "",
                "### LV-01",
                "",
                "- slide_number: 2",
                "- source_asset: `metadata.json#media_references[2]`",
                "- image_treatment: source-crop",
                "- layout_constraint: full-width primary visual with no redrawn substitute",
            ]
        ),
        encoding="utf-8",
    )
    (bundle_dir / "gary-diagram-cards.json").write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "cards": [
                    {
                        "card_number": 2,
                        "preintegration_png_path": "course-content/staging/rebranded-assets/slide-02.png",
                        "image_url": "https://cdn.example.com/hosted-02.png",
                        "source_asset": "`metadata.json#media_references[2]`",
                        "derivation_type": "source-crop",
                        "required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_gary_dispatch_ready(
        payload,
        payload_path=bundle_dir / "gary-dispatch-result.json",
    )

    assert result["status"] == "pass"


def test_fails_when_preintegration_cards_missing_site_repo_url(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)
    payload["dispatch_metadata"] = {
        "slides_content_json_path": "gary-slide-content.json",
        "invocation_mode": "tracked",
    }
    payload["literal_visual_publish"] = {
        "preintegration_ready": True,
        "substituted_cards": [2],
        "url_base": "https://example.github.io/assets/gamma/C1-M1",
    }

    (bundle_dir / "irene-pass1.md").write_text(
        "\n".join(
            [
                "## literal-visual spec cards",
                "",
                "### LV-01",
                "",
                "- slide_number: 2",
                "- source_asset: `metadata.json#media_references[2]`",
                "- image_treatment: source-crop",
                "- layout_constraint: full-width primary visual with no redrawn substitute",
            ]
        ),
        encoding="utf-8",
    )
    (bundle_dir / "gary-diagram-cards.json").write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "cards": [
                    {
                        "card_number": 2,
                        "preintegration_png_path": "course-content/staging/rebranded-assets/slide-02.png",
                        "source_asset": "`metadata.json#media_references[2]`",
                        "derivation_type": "source-crop",
                        "required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_gary_dispatch_ready(
        payload,
        payload_path=bundle_dir / "gary-dispatch-result.json",
    )

    assert result["status"] == "fail"
    assert any("site_repo_url must be present" in msg for msg in result["errors"])


def test_fails_when_preintegration_cards_used_in_adhoc_mode(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)
    payload["dispatch_metadata"] = {
        "slides_content_json_path": "gary-slide-content.json",
        "site_repo_url": "https://github.com/jlenrique/jlenrique.github.io",
        "invocation_mode": "ad-hoc",
    }
    payload["literal_visual_publish"] = {
        "preintegration_ready": True,
        "substituted_cards": [2],
        "url_base": "https://example.github.io/assets/gamma/C1-M1",
    }

    (bundle_dir / "irene-pass1.md").write_text(
        "\n".join(
            [
                "## literal-visual spec cards",
                "",
                "### LV-01",
                "",
                "- slide_number: 2",
                "- source_asset: `metadata.json#media_references[2]`",
                "- image_treatment: source-crop",
                "- layout_constraint: full-width primary visual with no redrawn substitute",
            ]
        ),
        encoding="utf-8",
    )
    (bundle_dir / "gary-diagram-cards.json").write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "cards": [
                    {
                        "card_number": 2,
                        "preintegration_png_path": "course-content/staging/rebranded-assets/slide-02.png",
                        "source_asset": "`metadata.json#media_references[2]`",
                        "derivation_type": "source-crop",
                        "required": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_gary_dispatch_ready(
        payload,
        payload_path=bundle_dir / "gary-dispatch-result.json",
    )

    assert result["status"] == "fail"
    assert any("not allowed in ad-hoc mode" in msg for msg in result["errors"])
