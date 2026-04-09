from __future__ import annotations

import json
from importlib import util
from pathlib import Path

import pytest
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "build-pass2-inspection-pack.py"


def _load_script_module():
    spec = util.spec_from_file_location(
        "build_pass2_inspection_pack_module",
        SCRIPT_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


module = _load_script_module()
build_pass2_inspection_pack = module.build_pass2_inspection_pack


def _make_png(path: Path, color: tuple[int, int, int]) -> None:
    image = Image.new("RGB", (640, 360), color=color)
    image.save(path)


def _make_bundle(tmp_path: Path, *, with_motion: bool = False) -> Path:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    slide_01 = bundle / "slide-01.png"
    slide_02 = bundle / "slide-02.png"
    _make_png(slide_01, (200, 30, 30))
    _make_png(slide_02, (30, 30, 200))

    authorized = {
        "authorized_slides": [
            {
                "slide_id": "slide-01",
                "card_number": 1,
                "file_path": str(slide_01),
                "source_ref": "src-01",
            },
            {
                "slide_id": "slide-02",
                "card_number": 2,
                "file_path": str(slide_02),
                "source_ref": "src-02",
            },
        ]
    }
    (bundle / "authorized-storyboard.json").write_text(
        json.dumps(authorized),
        encoding="utf-8",
    )

    if with_motion:
        motion_dir = bundle / "motion"
        motion_dir.mkdir()
        motion_asset = motion_dir / "slide-01-motion.mp4"
        motion_asset.write_bytes(b"video")
        motion_plan = {
            "motion_enabled": True,
            "slides": [
                {
                    "slide_id": "slide-01",
                    "motion_type": "video",
                    "motion_status": "approved",
                    "motion_asset_path": str(motion_asset),
                },
                {
                    "slide_id": "slide-02",
                    "motion_type": "static",
                    "motion_status": None,
                    "motion_asset_path": None,
                },
            ],
        }
        (bundle / "motion_plan.yaml").write_text(
            yaml.safe_dump(motion_plan, sort_keys=False),
            encoding="utf-8",
        )

    return bundle


def test_builds_winner_slide_contact_sheet(tmp_path: Path) -> None:
    bundle = _make_bundle(tmp_path)

    result = build_pass2_inspection_pack(bundle)

    assert result["status"] == "built"
    assert Path(result["winner_slide_contact_sheet"]).is_file()
    assert Path(result["receipt_path"]).is_file()
    assert result["winner_slide_count"] == 2


def test_builds_motion_keyframe_contact_sheet_for_approved_motion(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    bundle = _make_bundle(tmp_path, with_motion=True)

    def _fake_extract(video_path: Path, output_dir: Path, max_frames: int = 6):
        frame_paths = []
        for idx in range(3):
            frame_path = output_dir / f"frame_{idx + 1:04d}.png"
            _make_png(frame_path, (50 * (idx + 1), 60, 70))
            frame_paths.append(
                {
                    "frame_index": idx,
                    "frame_path": str(frame_path),
                    "timestamp_ms": None,
                }
            )
        return frame_paths

    monkeypatch.setattr(module, "_extract_keyframes", _fake_extract)

    result = build_pass2_inspection_pack(bundle, max_motion_frames=3)

    assert len(result["motion_inspection"]) == 1
    motion = result["motion_inspection"][0]
    assert motion["slide_id"] == "slide-01"
    assert len(motion["frame_paths"]) == 3
    assert Path(motion["contact_sheet_path"]).is_file()
