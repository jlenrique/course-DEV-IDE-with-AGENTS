"""Tests for validate-literal-visual-pre-dispatch.py (§06B enforcement gate).

Boundary contract (per story AC-5):
- THIS gate: checks image_url presence BEFORE Gary is invoked.
- Post-dispatch gate (``validate-gary-dispatch-ready.py``): checks
  ``literal_visual_publish`` receipt AFTER Gary runs.
They are NOT redundant — both must exist.

Test matrix (K-floor 10, target 11-13):
- T1: diagram_cards absent → skip
- T2: diagram_cards empty list → skip
- T3: required card, image_url valid HTTPS → PASS
- T4: required card, image_url null, preintegration_png_path present on disk (tracked) → PASS
- T5: required card, image_url null, preintegration_png_path declared but file missing → FAIL
- T6: required card, image_url null, no preintegration_png_path → FAIL
- T7: required=false card, image_url null → PASS (non-blocking)
- T8: packet absent when required card exists → FAIL
- T9: packet present when required card exists → contributes to PASS
- T10: ad-hoc mode + required card + local preintegration_png_path → FAIL
- T11: full tracked PASS — all required resolved + packet present
- T12: integration — reads live-shaped gary-outbound-envelope.yaml directly
"""

from __future__ import annotations

import sys
from importlib import util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = (
    ROOT
    / "skills"
    / "bmad-agent-marcus"
    / "scripts"
    / "validate-literal-visual-pre-dispatch.py"
)


def _load_module():
    sys.path.insert(0, str(ROOT))
    spec = util.spec_from_file_location("validate_literal_visual_pre_dispatch", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
validate_literal_visual_pre_dispatch = mod.validate_literal_visual_pre_dispatch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_envelope(
    bundle: Path,
    diagram_cards: list | None = None,
    run_mode: str = "tracked/default",
) -> None:
    envelope = {
        "schema_version": "1.0",
        "run_id": "TEST-001",
        "run_mode": run_mode,
    }
    if diagram_cards is not None:
        envelope["diagram_cards"] = diagram_cards
    (bundle / "gary-outbound-envelope.yaml").write_text(
        yaml.safe_dump(envelope), encoding="utf-8"
    )


def _write_packet(bundle: Path) -> None:
    (bundle / "literal-visual-operator-packet.md").write_text(
        "# Literal-Visual Operator Packet\nOperator confirmed: assets staged.", encoding="utf-8"
    )


def _required_card(image_url: str | None = None, preintegration_path: str | None = None) -> dict:
    return {
        "card_number": 12,
        "slide_id": "S12",
        "required": True,
        "image_url": image_url,
        "preintegration_png_path": preintegration_path,
    }


# ---------------------------------------------------------------------------
# T1 + T2: Skip when no diagram cards
# ---------------------------------------------------------------------------

def test_t1_diagram_cards_absent_skips(tmp_path: Path) -> None:
    """T1: diagram_cards key absent from envelope → gate skips, no errors."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_envelope(bundle, diagram_cards=None)
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert errors == []


def test_t2_diagram_cards_empty_skips(tmp_path: Path) -> None:
    """T2: diagram_cards is empty list → gate skips, no errors."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_envelope(bundle, diagram_cards=[])
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert errors == []


# ---------------------------------------------------------------------------
# T3: Valid HTTPS image_url passes
# ---------------------------------------------------------------------------

def test_t3_valid_https_image_url_passes(tmp_path: Path) -> None:
    """T3: required card with valid HTTPS image_url → PASS."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_packet(bundle)
    _write_envelope(bundle, diagram_cards=[
        _required_card(image_url="https://jlenrique.github.io/assets/card-12.jpg")
    ])
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert errors == []


# ---------------------------------------------------------------------------
# T4: Local preintegration_png_path present on disk (tracked) → PASS
# ---------------------------------------------------------------------------

def test_t4_local_preintegration_path_on_disk_passes(tmp_path: Path) -> None:
    """T4: required card, null image_url, preintegration path on disk → PASS (tracked)."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_packet(bundle)
    # Create the local PNG file
    png = bundle / "roadmap.jpg"
    png.write_bytes(b"fake-image-data")
    _write_envelope(bundle, diagram_cards=[
        _required_card(image_url=None, preintegration_path="roadmap.jpg")
    ])
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert errors == []


# ---------------------------------------------------------------------------
# T5: preintegration_png_path declared but file missing → FAIL
# ---------------------------------------------------------------------------

def test_t5_preintegration_path_declared_but_missing_fails(tmp_path: Path) -> None:
    """T5: required card, null image_url, declared preintegration path missing on disk → FAIL."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_packet(bundle)
    _write_envelope(bundle, diagram_cards=[
        _required_card(image_url=None, preintegration_path="missing-roadmap.jpg")
    ])
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert len(errors) == 1
    assert "not found" in errors[0]
    assert "S12" in errors[0]


# ---------------------------------------------------------------------------
# T6: image_url null, no preintegration path → FAIL
# ---------------------------------------------------------------------------

def test_t6_null_image_url_no_path_fails(tmp_path: Path) -> None:
    """T6: required card, image_url null, no preintegration_png_path → FAIL."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_packet(bundle)
    _write_envelope(bundle, diagram_cards=[
        _required_card(image_url=None, preintegration_path=None)
    ])
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert len(errors) == 1
    assert "image_url is null" in errors[0]
    assert "12" in errors[0]


# ---------------------------------------------------------------------------
# T7: required=false card with null image_url → PASS (non-blocking)
# ---------------------------------------------------------------------------

def test_t7_non_required_card_null_url_passes(tmp_path: Path) -> None:
    """T7: required=false card with null image_url → not a blocker."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_envelope(bundle, diagram_cards=[{
        "card_number": 5,
        "slide_id": "S05",
        "required": False,
        "image_url": None,
        "preintegration_png_path": None,
    }])
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert errors == []


# ---------------------------------------------------------------------------
# T8 + T9: Operator packet presence
# ---------------------------------------------------------------------------

def test_t8_packet_absent_when_required_card_exists_fails(tmp_path: Path) -> None:
    """T8: literal-visual-operator-packet.md absent when required card exists → FAIL."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_envelope(bundle, diagram_cards=[
        _required_card(image_url="https://example.com/img.jpg")
    ])
    # packet NOT written
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert any("literal-visual-operator-packet.md is absent" in e for e in errors)


def test_t9_packet_present_contributes_to_pass(tmp_path: Path) -> None:
    """T9: packet present + valid image_url → no packet error."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_packet(bundle)
    _write_envelope(bundle, diagram_cards=[
        _required_card(image_url="https://example.com/img.jpg")
    ])
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert not any("operator-packet" in e for e in errors)


# ---------------------------------------------------------------------------
# T10: Ad-hoc mode + local preintegration path → FAIL
# ---------------------------------------------------------------------------

def test_t10_ad_hoc_mode_local_path_fails(tmp_path: Path) -> None:
    """T10: ad-hoc mode with local preintegration_png_path → FAIL (mirrors post-dispatch policy)."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_packet(bundle)
    png = bundle / "roadmap.jpg"
    png.write_bytes(b"fake-image-data")
    _write_envelope(bundle, diagram_cards=[
        _required_card(image_url=None, preintegration_path="roadmap.jpg")
    ], run_mode="ad-hoc")
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert len(errors) >= 1
    assert any("ad-hoc" in e for e in errors)


# ---------------------------------------------------------------------------
# T11: Full tracked PASS
# ---------------------------------------------------------------------------

def test_t11_full_tracked_pass(tmp_path: Path) -> None:
    """T11: all required cards resolved + packet present → exit 0."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_packet(bundle)
    png = bundle / "roadmap.jpg"
    png.write_bytes(b"fake-image-data")
    _write_envelope(bundle, diagram_cards=[
        _required_card(image_url=None, preintegration_path="roadmap.jpg"),
    ])
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert errors == []


# ---------------------------------------------------------------------------
# T12: Integration — reads live-shaped gary-outbound-envelope.yaml
# ---------------------------------------------------------------------------

def test_t4b_repo_relative_preintegration_path_passes(tmp_path: Path) -> None:
    """T4b: required card, image_url null, preintegration_png_path is repo-relative
    (e.g. 'course-content/courses/.../file.jpg') — file exists at project root, not bundle dir."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_packet(bundle)
    # Simulate a repo-relative path: file lives outside bundle_dir (at a fake project root)
    repo_dir = tmp_path / "repo"
    asset_dir = repo_dir / "course-content" / "courses" / "tejal-APC-C1"
    asset_dir.mkdir(parents=True)
    png = asset_dir / "APC Content Roadmap.jpg"
    png.write_bytes(b"fake-image-data")
    _write_envelope(bundle, diagram_cards=[
        _required_card(
            image_url=None,
            preintegration_path="course-content/courses/tejal-APC-C1/APC Content Roadmap.jpg"
        )
    ])
    # Patch _PROJECT_ROOT on the already-loaded module object
    original_root = mod._PROJECT_ROOT
    try:
        mod._PROJECT_ROOT = repo_dir
        errors = validate_literal_visual_pre_dispatch(bundle)
        assert errors == [], f"Expected no errors but got: {errors}"
    finally:
        mod._PROJECT_ROOT = original_root


def test_non_dict_envelope_returns_clean_error(tmp_path: Path) -> None:
    """Non-dict YAML (e.g. a list) returns a clean error instead of AttributeError."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "gary-outbound-envelope.yaml").write_text(
        "- item1\n- item2\n", encoding="utf-8"
    )
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert len(errors) == 1
    assert "mapping" in errors[0] or "dict" in errors[0] or "list" in errors[0]


def test_t12_integration_live_envelope_shape(tmp_path: Path) -> None:
    """T12: reads a live-shaped envelope YAML with diagram_cards block."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()

    # Write a live-shaped envelope matching the actual production format
    envelope_content = """
schema_version: "1.0"
run_id: C1-M1-PRES-TEST
run_mode: tracked/default
diagram_cards:
  - card_number: 12
    slide_id: S12
    required: true
    image_url: null
    preintegration_png_path: null
    placement_note: Full-frame
"""
    (bundle / "gary-outbound-envelope.yaml").write_text(envelope_content.strip(), encoding="utf-8")
    # No packet, no path → two errors expected
    errors = validate_literal_visual_pre_dispatch(bundle)
    assert len(errors) == 2  # null URL error + missing packet error
    assert any("S12" in e for e in errors)
    assert any("operator-packet" in e or "literal-visual-operator-packet" in e for e in errors)
