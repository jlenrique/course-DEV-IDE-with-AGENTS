"""Tests for Gary dispatch → static storyboard bundle."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_GENERATE_SCRIPT = _SCRIPTS_DIR / "generate-storyboard.py"
_AUTHORIZE_SCRIPT = _SCRIPTS_DIR / "write-authorized-storyboard.py"


def _load_generate_module():
    spec = importlib.util.spec_from_file_location("generate_storyboard_mod", _GENERATE_SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sample_payload() -> dict:
    return {
        "gary_slide_output": [
            {
                "slide_id": "m1-c1",
                "fidelity": "creative",
                "card_number": 1,
                "source_ref": "src-a",
                "file_path": "slides/s1.png",
            },
            {
                "slide_id": "m1-c2",
                "fidelity": "literal-text",
                "card_number": 2,
                "source_ref": "src-b",
                "file_path": "slides/missing.png",
            },
            {
                "slide_id": "m1-c3",
                "fidelity": "literal-visual",
                "card_number": 3,
                "source_ref": "src-c",
                "file_path": "https://example.com/img.png",
            },
        ]
    }


def test_build_manifest_order_and_asset_status(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    (slides / "s1.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_sample_payload()), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"

    manifest = mod.build_manifest(
        _sample_payload(),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )

    assert len(manifest["slides"]) == 3
    assert [s["slide_id"] for s in manifest["slides"]] == ["m1-c1", "m1-c2", "m1-c3"]
    assert manifest["slides"][0]["asset_status"] == "present"
    assert manifest["slides"][1]["asset_status"] == "missing"
    assert manifest["slides"][2]["asset_status"] == "remote"


def test_format_summary_counts_and_endpoints() -> None:
    mod = _load_generate_module()
    manifest = {
        "slides": [
            {"slide_id": "a", "fidelity": "creative", "asset_status": "present"},
            {"slide_id": "b", "fidelity": "literal-text", "asset_status": "present"},
            {"slide_id": "c", "fidelity": "creative", "asset_status": "missing"},
        ]
    }
    text = mod.format_summary(manifest)
    assert "3 slide(s)" in text
    assert "First slide_id: 'a'" in text
    assert "last slide_id: 'c'" in text
    assert "creative=2" in text
    assert "literal-text=1" in text
    assert "missing local assets" in text


def test_html_contains_missing_marker(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    (bundle / "slides").mkdir(parents=True)
    (bundle / "slides" / "s1.png").write_bytes(b"x")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_sample_payload()), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        _sample_payload(),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )
    html = mod.render_index_html(manifest)
    assert "MISSING" in html
    assert "m1-c1" in html


def test_cli_generate_strict_fails_on_missing(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    (slides / "s1.png").write_bytes(b"x")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_sample_payload()), encoding="utf-8")
    proc = subprocess.run(
        [
            sys.executable,
            str(_GENERATE_SCRIPT),
            "generate",
            "--payload",
            str(payload_path),
            "--out-dir",
            str(bundle),
            "--strict",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert (bundle / "storyboard" / "storyboard.json").is_file()


def test_write_authorized_refuses_overwrite(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    (bundle / "slides").mkdir(parents=True)
    (bundle / "slides" / "s1.png").write_bytes(b"x")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_sample_payload()), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        _sample_payload(),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )
    mod.write_bundle(manifest, storyboard_dir)
    manifest_path = storyboard_dir / "storyboard.json"
    out = bundle / "authorized-storyboard.json"

    r1 = subprocess.run(
        [
            sys.executable,
            str(_AUTHORIZE_SCRIPT),
            "--manifest",
            str(manifest_path),
            "--run-id",
            "RUN-TEST-1",
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r1.returncode == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["run_id"] == "RUN-TEST-1"
    assert data["slide_ids"] == ["m1-c1", "m1-c2", "m1-c3"]
    assert "authorized_at_utc" in data

    r2 = subprocess.run(
        [
            sys.executable,
            str(_AUTHORIZE_SCRIPT),
            "--manifest",
            str(manifest_path),
            "--run-id",
            "RUN-TEST-2",
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r2.returncode == 1
    assert "refusing to overwrite" in (r2.stderr or "").lower()


def test_cli_summarize_subcommand(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    (bundle / "slides").mkdir(parents=True)
    (bundle / "slides" / "s1.png").write_bytes(b"x")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_sample_payload()), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        _sample_payload(),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )
    mod.write_bundle(manifest, storyboard_dir)
    mp = storyboard_dir / "storyboard.json"
    proc = subprocess.run(
        [sys.executable, str(_GENERATE_SCRIPT), "summarize", "--manifest", str(mp)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "3 slide(s)" in proc.stdout
    assert "m1-c1" in proc.stdout
