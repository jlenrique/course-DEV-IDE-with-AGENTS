"""Tests for Gary dispatch → static storyboard bundle."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image

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


def _all_present_payload() -> dict:
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
                "file_path": "slides/s2.png",
            },
        ]
    }


def _write_test_png(path: Path, *, size: tuple[int, int] = (12, 6)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(10, 90, 160)).save(path, format="PNG")


def test_build_manifest_order_and_asset_status(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png", size=(12, 6))
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
    assert manifest["storyboard_version"] == 3
    assert manifest["storyboard_view"] == "slides_only"
    assert manifest["related_assets"] == []
    assert len(manifest["rows"]) == 3
    assert manifest["checkpoint_label"] == "Storyboard A"
    assert manifest["review_meta"]["total_slides"] == 3
    assert manifest["review_meta"]["missing_assets"] == 1
    assert manifest["review_meta"]["remote_assets"] == 1
    assert manifest["review_meta"]["first_slide_id"] == "m1-c1"
    assert manifest["review_meta"]["last_slide_id"] == "m1-c3"
    assert manifest["slides"][0]["orientation"] == "landscape"
    assert manifest["slides"][0]["dimensions"] == {"width": 12, "height": 6}
    assert manifest["slides"][0]["aspect_ratio"] == "12:6"
    by_id = {s["slide_id"]: s for s in manifest["slides"]}
    assert by_id["m1-c1"]["issue_flags"] == []
    assert by_id["m1-c2"]["issue_flags"] == ["missing_asset"]
    assert by_id["m1-c3"]["issue_flags"] == []
    for s in manifest["slides"]:
        assert s["row_id"].startswith("slide-")
        assert s["preview_kind"] in {"image", "missing", "link", "other"}
        assert "orientation" in s
        assert "script_notes" in s
        assert "issue_flags" in s
        assert s["narration_status"] == "pending"
        assert s["narration_text"] == ""


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


def test_format_summary_handles_no_valid_slide_ids() -> None:
    mod = _load_generate_module()
    manifest = {"slides": ["not-a-dict", 1, None]}
    text = mod.format_summary(manifest)
    assert "zero valid slide_id entries" in text


def test_html_contains_missing_marker(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    (bundle / "slides").mkdir(parents=True)
    _write_test_png(bundle / "slides" / "s1.png")
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
    assert "Storyboard A Review" in html
    assert 'data-role="slide-card"' in html
    assert 'data-role="preview-link"' in html
    assert 'data-role="search"' in html
    assert 'data-role="issues-only"' in html
    assert "Preview unavailable" in html
    assert "m1-c1" in html
    assert "Pending (pre-Pass 2)" in html
    assert "Script notes" in html
    assert "Orientation data" in html
    assert 'class="expand-cue"' in html
    assert 'summary::after { content: "[+]";' in html
    assert '[open] summary::after { content: "[-]";' in html
    assert 'data-role="jump-next-issue">Next issue<' in html
    assert 'data-role="issues-only"' in html


def test_html_disables_issue_controls_when_no_actionable_issues(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
    _write_test_png(slides / "s2.png")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_all_present_payload()), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        _all_present_payload(),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )

    assert all(slide["issue_flags"] == [] for slide in manifest["slides"])
    html = mod.render_index_html(manifest)
    assert 'data-role="jump-next-issue" disabled aria-disabled="true">No issues<' in html
    assert 'data-role="issues-only" disabled aria-disabled="true"' in html


def test_html_enables_issue_controls_when_actionable_issue_exists(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_sample_payload()), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        _sample_payload(),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )

    by_id = {slide["slide_id"]: slide for slide in manifest["slides"]}
    assert by_id["m1-c2"]["issue_flags"] == ["missing_asset"]
    html = mod.render_index_html(manifest)
    assert 'data-role="jump-next-issue">Next issue<' in html
    assert 'data-role="jump-next-issue" disabled' not in html
    assert 'data-role="issues-only" disabled' not in html
    assert 'data-slide-id="m1-c2"' in html
    assert 'data-issues="missing_asset"' in html


def test_segment_manifest_attaches_narration(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_sample_payload()), encoding="utf-8")
    manifest_yaml = bundle / "manifest.yaml"
    manifest_yaml.write_text(
        """
lesson_id: C1-M1-L1
title: Test
segments:
  - id: seg-01
    gary_slide_id: m1-c1
    narration_text: "First slide voiceover line."
  - id: seg-02
    gary_slide_id: m1-c3
    narration_text: "Third slide only."
""",
        encoding="utf-8",
    )
    storyboard_dir = bundle / "storyboard"
    narration_map = mod.load_narration_by_slide_id(manifest_yaml)
    assert narration_map["m1-c1"]["narration_text"] == "First slide voiceover line."
    assert narration_map["m1-c1"]["match_count"] == 1
    assert narration_map["m1-c3"]["narration_text"] == "Third slide only."

    manifest = mod.build_manifest(
        _sample_payload(),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
        narration_by_slide_id=narration_map,
        segment_manifest_path=manifest_yaml,
    )
    assert manifest["storyboard_view"] == "slides_with_script"
    assert manifest["segment_manifest_source"] == manifest_yaml.resolve().as_posix()
    by_id = {s["slide_id"]: s for s in manifest["slides"]}
    assert by_id["m1-c1"]["narration_status"] == "present"
    assert "First slide" in by_id["m1-c1"]["narration_text"]
    assert by_id["m1-c2"]["narration_status"] == "no_match"
    assert by_id["m1-c2"]["narration_text"] == ""
    assert by_id["m1-c2"]["issue_flags"] == ["missing_asset", "no_match"]
    assert by_id["m1-c3"]["narration_status"] == "present"
    assert by_id["m1-c1"]["segment_match_count"] == 1

    html = mod.render_index_html(manifest)
    assert "First slide voiceover line." in html
    assert "Third slide only." in html
    assert "No match" in html
    summary = mod.format_summary(manifest)
    assert "Narration: 2/3 slide(s) have script text attached." in summary


def test_segment_manifest_multi_match_surfaces_review_state(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_all_present_payload()), encoding="utf-8")
    manifest_yaml = bundle / "manifest.yaml"
    manifest_yaml.write_text(
        """
segments:
  - id: seg-01
    gary_slide_id: m1-c1
    narration_ref: narration-script.md#seg-01
    narration_text: "First segment for slide one."
  - id: seg-01b
    gary_slide_id: m1-c1
    narration_ref: narration-script.md#seg-01b
    narration_text: "Second segment also matched slide one."
""",
        encoding="utf-8",
    )
    storyboard_dir = bundle / "storyboard"

    narration_map = mod.load_narration_by_slide_id(manifest_yaml)
    assert narration_map["m1-c1"]["match_count"] == 2
    assert narration_map["m1-c1"]["segment_ids"] == ["seg-01", "seg-01b"]

    manifest = mod.build_manifest(
        _all_present_payload(),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
        narration_by_slide_id=narration_map,
        segment_manifest_path=manifest_yaml,
    )
    by_id = {s["slide_id"]: s for s in manifest["slides"]}
    assert by_id["m1-c1"]["narration_status"] == "multi_match"
    assert by_id["m1-c1"]["segment_match_count"] == 2
    assert by_id["m1-c1"]["issue_flags"] == ["multi_match"]
    assert by_id["m1-c1"]["matched_narration_refs"] == [
        "narration-script.md#seg-01",
        "narration-script.md#seg-01b",
    ]
    assert manifest["review_meta"]["multi_match_narration"] == 1

    html = mod.render_index_html(manifest)
    assert "Multi-match" in html
    assert "Multiple segment-manifest matches attached (2)." in html
    assert "First segment for slide one." in html
    assert "Second segment also matched slide one." in html
    summary = mod.format_summary(manifest)
    assert "Narration review: 1 slide(s) have multiple segment matches" in summary


def test_segment_manifest_motion_metadata_is_visible_in_storyboard_b(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    motion = bundle / "motion"
    slides.mkdir(parents=True)
    motion.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
    (motion / "clip.mp4").write_bytes(b"mp4")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(
        json.dumps(
            {
                "gary_slide_output": [
                    {
                        "slide_id": "m1-c1",
                        "fidelity": "creative",
                        "card_number": 1,
                        "source_ref": "src-a",
                        "file_path": "slides/s1.png",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    manifest_yaml = bundle / "manifest.yaml"
    manifest_yaml.write_text(
        f"""
segments:
  - id: seg-01
    gary_slide_id: m1-c1
    narration_ref: narration-script.md#seg-01
    narration_text: "Motion-aware line."
    visual_mode: video
    visual_file: {(slides / 's1.png').as_posix()}
    motion_type: video
    motion_asset_path: {((motion / 'clip.mp4').as_posix())}
    motion_status: approved
    motion_source: kling
    motion_duration_seconds: 5.041
    visual_references:
      - element: three callouts
        narration_cue: "Motion-aware line."
""",
        encoding="utf-8",
    )
    storyboard_dir = bundle / "storyboard"

    manifest = mod.build_manifest(
        json.loads(payload_path.read_text(encoding="utf-8")),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
        narration_by_slide_id=mod.load_narration_by_slide_id(manifest_yaml),
        segment_manifest_path=manifest_yaml,
    )
    slide = manifest["slides"][0]
    assert slide["motion_type"] == "video"
    assert slide["motion_status"] == "approved"
    assert slide["motion_asset_path"] == (motion / "clip.mp4").as_posix()
    assert slide["visual_mode"] == "video"
    assert slide["matched_visual_reference_count"] == 1
    assert slide["motion_preview_kind"] == "video"

    html = mod.render_index_html(manifest)
    assert "motion video" in html
    assert "Motion review: <strong>Motion: video | approved | 5.041s</strong>" in html
    assert '<video class="motion-preview" controls preload="metadata"' in html
    assert "<dt>Motion asset</dt><dd>" in html
    assert "<dt>Motion source</dt><dd>kling</dd>" in html


def test_load_related_assets_parses_and_validates(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    storyboard_dir = bundle / "storyboard"
    storyboard_dir.mkdir(parents=True)
    (bundle / "extras").mkdir(parents=True)
    (bundle / "extras" / "a1.mp3").write_bytes(b"x")

    related_json = bundle / "related.json"
    related_json.write_text(
        json.dumps(
            {
                "related_assets": [
                    {
                        "asset_type": "audio",
                        "label": "Intro narration",
                        "link": "extras/a1.mp3",
                        "stage": "generated",
                    },
                    {
                        "asset_type": "source",
                        "label": "Reference doc",
                        "link": "https://example.com/ref",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    rows = mod.load_related_assets(
        related_json,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )
    assert len(rows) == 2
    assert rows[0]["asset_status"] == "present"
    assert rows[0]["row_kind"] == "related_asset"
    assert rows[1]["asset_status"] == "remote"

    bad_json = bundle / "bad-related.json"
    bad_json.write_text(json.dumps([{"asset_type": "video", "link": "x.mp4"}]), encoding="utf-8")
    try:
        mod.load_related_assets(bad_json, storyboard_dir=storyboard_dir, asset_base=bundle)
        raise AssertionError("expected ValueError for missing label")
    except ValueError as exc:
        assert "label is required" in str(exc)


def test_manifest_and_html_include_related_assets(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_sample_payload()), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"

    related_assets = [
        {
            "row_kind": "related_asset",
            "asset_type": "video",
            "label": "Lesson teaser",
            "link": "https://example.com/video.mp4",
            "source_ref": "src-video",
            "asset_status": "remote",
            "html_asset_ref": "https://example.com/video.mp4",
        }
    ]
    manifest = mod.build_manifest(
        _sample_payload(),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
        related_assets=related_assets,
    )
    assert len(manifest["slides"]) == 3
    assert len(manifest["rows"]) == 4
    assert manifest["rows"][-1]["row_kind"] == "related_asset"
    assert manifest["rows"][-1]["sequence"] == 4
    assert manifest["related_assets"][0]["sequence"] == 4

    html = mod.render_index_html(manifest)
    assert "Related assets" in html
    assert "Lesson teaser" in html
    assert 'data-role="related-asset"' in html
    summary = mod.format_summary(manifest)
    assert "Related assets: 1 row(s) appended after slides." in summary


def test_cli_generate_strict_fails_on_missing(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
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
    _write_test_png(bundle / "slides" / "s1.png")
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


def test_cli_generate_with_segment_manifest(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_sample_payload()), encoding="utf-8")
    manifest_yaml = bundle / "manifest.yaml"
    manifest_yaml.write_text(
        "segments:\n"
        "  - gary_slide_id: m1-c1\n"
        "    narration_text: From CLI test.\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(_GENERATE_SCRIPT),
            "generate",
            "--payload",
            str(payload_path),
            "--out-dir",
            str(bundle),
            "--segment-manifest",
            str(manifest_yaml),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.returncode == 0
    data = json.loads((bundle / "storyboard" / "storyboard.json").read_text(encoding="utf-8"))
    assert data["storyboard_view"] == "slides_with_script"
    html = (bundle / "storyboard" / "index.html").read_text(encoding="utf-8")
    assert "From CLI test." in html


def test_cli_generate_with_related_assets(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_sample_payload()), encoding="utf-8")

    related_path = bundle / "related-assets.json"
    related_path.write_text(
        json.dumps(
            [
                {
                    "asset_type": "interactive",
                    "label": "Quiz prototype",
                    "link": "https://example.com/quiz",
                }
            ]
        ),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            str(_GENERATE_SCRIPT),
            "generate",
            "--payload",
            str(payload_path),
            "--out-dir",
            str(bundle),
            "--related-assets",
            str(related_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.returncode == 0
    data = json.loads((bundle / "storyboard" / "storyboard.json").read_text(encoding="utf-8"))
    assert len(data["related_assets"]) == 1
    assert data["related_assets"][0]["sequence"] == 4
    assert data["rows"][-1]["label"] == "Quiz prototype"
    html = (bundle / "storyboard" / "index.html").read_text(encoding="utf-8")
    assert "Quiz prototype" in html


def test_cli_summarize_subcommand(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    (bundle / "slides").mkdir(parents=True)
    _write_test_png(bundle / "slides" / "s1.png")
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


def test_cli_generate_accepts_run_id(tmp_path: Path) -> None:
    """--run-id is accepted without error and correlated in Channel-C logs."""
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
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
            "--run-id",
            "TEST-RUN-STORYBOARD-001",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert (bundle / "storyboard" / "storyboard.json").is_file()


def test_literal_visual_remote_url_preserved_in_storyboard(tmp_path: Path) -> None:
    """Regression: literal-visual slides with remote URLs (user-provided OR
    Git-site hosted) must survive storyboard generation unchanged as 'remote'
    status — not promoted to 'present' or demoted to 'missing'.

    This guards against regressions when the preintegration literal-visual
    Git-hosting feature replaces user-provided Gamma links with hosted URLs,
    ensuring the storyboard's asset resolution logic treats both URL shapes
    identically.
    """
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    (bundle / "slides").mkdir(parents=True)
    _write_test_png(bundle / "slides" / "s1.png")

    payload = {
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
                "fidelity": "literal-visual",
                "card_number": 2,
                "source_ref": "src-b",
                # User-provided Gamma link (pre-feature state)
                "file_path": "https://gamma.app/docs/some-deck",
            },
            {
                "slide_id": "m1-c3",
                "fidelity": "literal-visual",
                "card_number": 3,
                "source_ref": "src-c",
                # Git-site hosted URL (post-feature state)
                "file_path": "https://jlenrique.github.io/assets/gamma/C1-M1-PRES/slide_03.png",
            },
        ]
    }
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"

    manifest = mod.build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )

    by_id = {s["slide_id"]: s for s in manifest["slides"]}

    # Creative slide with local file should be present
    assert by_id["m1-c1"]["asset_status"] == "present"
    assert by_id["m1-c1"]["fidelity"] == "creative"

    # Both literal-visual slides with remote URLs must stay "remote"
    assert by_id["m1-c2"]["asset_status"] == "remote", (
        "literal-visual with user Gamma link must be remote, not missing"
    )
    assert by_id["m1-c2"]["fidelity"] == "literal-visual"
    assert by_id["m1-c3"]["asset_status"] == "remote", (
        "literal-visual with Git-site hosted URL must be remote, not missing"
    )
    assert by_id["m1-c3"]["fidelity"] == "literal-visual"

    # Fidelity counts in summary must include both literal-visual slides
    summary = mod.format_summary(manifest)
    assert "literal-visual=2" in summary

    # HTML should render preview links for both remote literal-visual slides
    rendered = mod.render_index_html(manifest)
    assert "gamma.app/docs/some-deck" in rendered
    assert "jlenrique.github.io/assets/gamma" in rendered


def test_double_dispatch_manifest_and_html_sections(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    (bundle / "slides").mkdir(parents=True)
    _write_test_png(bundle / "slides" / "s1.png")
    _write_test_png(bundle / "slides" / "s2.png")

    payload = {
        "gary_slide_output": [
            {
                "slide_id": "m1-c1",
                "fidelity": "creative",
                "card_number": 1,
                "source_ref": "src-a",
                "file_path": "slides/s1.png",
                "dispatch_variant": "A",
                "vera_score": 0.84,
                "quinn_score": 0.8,
                "selected": True,
            },
            {
                "slide_id": "m1-c1",
                "fidelity": "creative",
                "card_number": 1,
                "source_ref": "src-a",
                "file_path": "slides/s2.png",
                "dispatch_variant": "B",
                "vera_score": 0.79,
                "quinn_score": 0.76,
                "selected": False,
            },
        ]
    }
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )

    assert manifest["double_dispatch"]["enabled"] is True
    assert manifest["double_dispatch"]["selection_progress"]["selected"] == 1
    assert manifest["double_dispatch"]["selection_progress"]["total"] == 1
    assert len(manifest["selected_full_deck_preview"]) == 1

    rendered = mod.render_index_html(manifest)
    assert "Variant Selection" in rendered
    assert "Authorized Deck Preview" in rendered


def test_write_authorized_with_selection_metadata(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    (bundle / "slides").mkdir(parents=True)
    _write_test_png(bundle / "slides" / "s1.png")
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "m1-c1",
                "fidelity": "creative",
                "card_number": 1,
                "source_ref": "src-a",
                "file_path": "slides/s1.png",
                "dispatch_variant": "A",
                "selected": False,
            },
            {
                "slide_id": "m1-c1",
                "fidelity": "creative",
                "card_number": 1,
                "source_ref": "src-a",
                "file_path": "slides/s1.png",
                "dispatch_variant": "B",
                "selected": False,
            },
        ]
    }
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )
    mod.write_bundle(manifest, storyboard_dir)

    selections_path = bundle / "selections.json"
    selections_path.write_text(json.dumps({"1": "A"}), encoding="utf-8")

    out = bundle / "authorized-storyboard.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(_AUTHORIZE_SCRIPT),
            "--manifest",
            str(storyboard_dir / "storyboard.json"),
            "--run-id",
            "RUN-DD-001",
            "--selections",
            str(selections_path),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["slide_ids"] == ["m1-c1"]
    assert len(data["authorized_slides"]) == 1
    assert data["authorized_slides"][0]["dispatch_variant"] == "A"
    assert data["selection_metadata"][0]["selected_variant"] == "A"
    assert data["selection_metadata"][0]["rejected_variant"] == "B"


def test_html_escapes_reviewer_visible_fields(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")

    payload = {
        "gary_slide_output": [
            {
                "slide_id": "m1-c1",
                "title": '<script>alert("x")</script>',
                "fidelity": "creative",
                "card_number": 1,
                "source_ref": 'src-<b>bold</b>',
                "file_path": "slides/s1.png",
                "visual_description": 'notes with <tag> & "quotes"',
                "findings": ["alpha <beta>"],
            }
        ]
    }
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
    )

    html = mod.render_index_html(manifest)
    assert "<script>alert(" not in html
    assert "&lt;script&gt;alert" in html
    assert "src-&lt;b&gt;bold&lt;/b&gt;" in html
    assert "notes with &lt;tag&gt; &amp; &quot;quotes&quot;" in html
    assert "alpha &lt;beta&gt;" in html


def test_cli_generate_outputs_reviewer_friendly_storyboard_markup(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
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
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    html = (bundle / "storyboard" / "index.html").read_text(encoding="utf-8")
    assert "Static storyboard review surface for human approval." in html
    assert 'data-role="slide-card"' in html
    assert 'data-role="jump-next-issue"' in html
    assert '<dialog class="preview-dialog"' in html
    assert 'class="expand-cue"' in html


def test_export_snapshot_creates_deterministic_zip_with_sanitized_paths(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    local_png = slides / "s1.png"
    _write_test_png(local_png)

    payload = _sample_payload()
    payload["gary_slide_output"][0]["file_path"] = str(local_png.resolve())
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
        run_id="RUN-EXPORT-1",
    )
    mod.write_bundle(manifest, storyboard_dir)

    export_root = tmp_path / "exports"
    first = mod.export_storyboard_snapshot(storyboard_dir / "storyboard.json", export_root=export_root)
    first_zip_bytes = Path(first["zip_path"]).read_bytes()
    second = mod.export_storyboard_snapshot(storyboard_dir / "storyboard.json", export_root=export_root)
    second_zip_bytes = Path(second["zip_path"]).read_bytes()

    assert first_zip_bytes == second_zip_bytes
    with zipfile.ZipFile(second["zip_path"], "r") as zf:
        names = zf.namelist()
    assert names == ["index.html", "slides/s1.png", "storyboard.json"]
    assert all(":" not in name and "\\" not in name and not name.startswith("/") for name in names)

    exported_manifest = json.loads((Path(second["snapshot_dir"]) / "storyboard.json").read_text(encoding="utf-8"))
    assert exported_manifest["asset_base"] == "."
    assert exported_manifest["source_payload"] == "dispatch.json"
    assert exported_manifest["slides"][0]["file_path"] == "slides/s1.png"
    assert exported_manifest["slides"][0]["preview_href"] == "slides/s1.png"
    assert exported_manifest["slides"][1]["file_path"] == "slides/missing.png"
    assert "C:\\" not in json.dumps(exported_manifest)


def test_export_snapshot_includes_motion_preview_assets(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    motion = bundle / "motion"
    slides.mkdir(parents=True)
    motion.mkdir(parents=True)
    local_png = slides / "s1.png"
    local_mp4 = motion / "s1.mp4"
    _write_test_png(local_png)
    local_mp4.write_bytes(b"mp4")

    payload = {
        "gary_slide_output": [
            {
                "slide_id": "m1-c1",
                "fidelity": "creative",
                "card_number": 1,
                "source_ref": "src-a",
                "file_path": str(local_png.resolve()),
            }
        ]
    }
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    manifest_yaml = bundle / "manifest.yaml"
    manifest_yaml.write_text(
        f"""
segments:
  - id: seg-01
    gary_slide_id: m1-c1
    narration_ref: narration-script.md#seg-01
    narration_text: "Motion-aware line."
    visual_mode: video
    visual_file: {local_png.as_posix()}
    motion_type: video
    motion_asset_path: {local_mp4.as_posix()}
    motion_status: approved
    motion_source: kling
    motion_duration_seconds: 5.041
""",
        encoding="utf-8",
    )
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
        narration_by_slide_id=mod.load_narration_by_slide_id(manifest_yaml),
        segment_manifest_path=manifest_yaml,
        run_id="RUN-EXPORT-MOTION",
    )
    mod.write_bundle(manifest, storyboard_dir)

    export_root = tmp_path / "exports"
    result = mod.export_storyboard_snapshot(storyboard_dir / "storyboard.json", export_root=export_root)
    with zipfile.ZipFile(result["zip_path"], "r") as zf:
        names = zf.namelist()
    assert "motion/s1.mp4" in names

    exported_manifest = json.loads((Path(result["snapshot_dir"]) / "storyboard.json").read_text(encoding="utf-8"))
    slide = exported_manifest["slides"][0]
    assert slide["motion_preview_href"] == "motion/s1.mp4"
    html = (Path(result["snapshot_dir"]) / "index.html").read_text(encoding="utf-8")
    assert 'src="motion/s1.mp4"' in html


def test_exported_snapshot_html_local_links_resolve(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    _write_test_png(slides / "s1.png")
    payload_path = bundle / "dispatch.json"
    payload_path.write_text(json.dumps(_all_present_payload()), encoding="utf-8")
    storyboard_dir = bundle / "storyboard"
    manifest = mod.build_manifest(
        _all_present_payload(),
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=bundle,
        run_id="RUN-EXPORT-2",
    )
    mod.write_bundle(manifest, storyboard_dir)

    export_result = mod.export_storyboard_snapshot(storyboard_dir / "storyboard.json", export_root=tmp_path / "exports")
    snapshot_dir = Path(export_result["snapshot_dir"])
    html = (snapshot_dir / "index.html").read_text(encoding="utf-8")

    refs = set(re.findall(r'(?:src|href|data-preview-src)="([^"]+)"', html))
    local_refs = {
        ref for ref in refs
        if ref
        and not ref.startswith(("http://", "https://", "#", "mailto:"))
    }
    assert local_refs
    for ref in local_refs:
        assert (snapshot_dir / Path(ref)).is_file(), ref
    assert "C:\\" not in html
    assert "file://" not in html
    assert "..\\" not in html
    assert "../" not in html


def test_publish_snapshot_tree_is_non_destructive_and_idempotent(tmp_path: Path) -> None:
    mod = _load_generate_module()
    snapshot_dir = tmp_path / "snapshot"
    snapshot_dir.mkdir(parents=True)
    (snapshot_dir / "index.html").write_text("<html>ok</html>", encoding="utf-8")
    (snapshot_dir / "storyboard.json").write_text("{}", encoding="utf-8")
    (snapshot_dir / "gamma-export").mkdir()
    (snapshot_dir / "gamma-export" / "slide.png").write_bytes(b"png")

    repo_root = tmp_path / "pages-repo"
    (repo_root / "README.md").parent.mkdir(parents=True, exist_ok=True)
    (repo_root / "README.md").write_text("keep me", encoding="utf-8")

    first = mod.publish_snapshot_tree(
        snapshot_dir,
        repo_root=repo_root,
        target_subdir="assets/storyboards/RUN-EXPORT-3",
    )
    assert first["changed"] is True
    assert (repo_root / "README.md").read_text(encoding="utf-8") == "keep me"
    assert (repo_root / "assets" / "storyboards" / "RUN-EXPORT-3" / "index.html").is_file()

    second = mod.publish_snapshot_tree(
        snapshot_dir,
        repo_root=repo_root,
        target_subdir="assets/storyboards/RUN-EXPORT-3",
    )
    assert second["changed"] is False
    assert (repo_root / "README.md").read_text(encoding="utf-8") == "keep me"


def test_publish_snapshot_tree_rejects_different_existing_target(tmp_path: Path) -> None:
    mod = _load_generate_module()
    snapshot_dir = tmp_path / "snapshot"
    snapshot_dir.mkdir(parents=True)
    (snapshot_dir / "index.html").write_text("<html>new</html>", encoding="utf-8")
    (snapshot_dir / "storyboard.json").write_text("{}", encoding="utf-8")

    repo_root = tmp_path / "pages-repo"
    target_dir = repo_root / "assets" / "storyboards" / "RUN-EXPORT-4"
    target_dir.mkdir(parents=True)
    (target_dir / "index.html").write_text("<html>old</html>", encoding="utf-8")

    try:
        mod.publish_snapshot_tree(
            snapshot_dir,
            repo_root=repo_root,
            target_subdir="assets/storyboards/RUN-EXPORT-4",
        )
    except ValueError as exc:
        assert "already exists with different contents" in str(exc)
    else:
        raise AssertionError("expected publish_snapshot_tree to reject differing existing target")
