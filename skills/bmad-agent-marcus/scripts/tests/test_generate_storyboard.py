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
    assert manifest["storyboard_version"] == 3
    assert manifest["storyboard_view"] == "slides_only"
    assert manifest["related_assets"] == []
    assert len(manifest["rows"]) == 3
    for s in manifest["slides"]:
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
    assert "Pending (pre-Pass 2)" in html
    assert "narration (pass 2)" in html.lower()


def test_segment_manifest_attaches_narration(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    (slides / "s1.png").write_bytes(b"x")
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
    assert narration_map["m1-c1"] == "First slide voiceover line."
    assert narration_map["m1-c3"] == "Third slide only."

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
    assert by_id["m1-c2"]["narration_status"] == "pending"
    assert by_id["m1-c2"]["narration_text"] == ""
    assert by_id["m1-c3"]["narration_status"] == "present"

    html = mod.render_index_html(manifest)
    assert "First slide voiceover line." in html
    assert "Third slide only." in html
    summary = mod.format_summary(manifest)
    assert "Narration: 2/3 slide(s) have script text attached." in summary


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
    (slides / "s1.png").write_bytes(b"x")
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
    assert "(related)" in html
    assert "Lesson teaser" in html
    summary = mod.format_summary(manifest)
    assert "Related assets: 1 row(s) appended after slides." in summary


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


def test_cli_generate_with_segment_manifest(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    slides = bundle / "slides"
    slides.mkdir(parents=True)
    (slides / "s1.png").write_bytes(b"x")
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
    (slides / "s1.png").write_bytes(b"x")
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


def test_cli_generate_accepts_run_id(tmp_path: Path) -> None:
    """--run-id is accepted without error and correlated in Channel-C logs."""
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
    (bundle / "slides" / "s1.png").write_bytes(b"x")

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
    (bundle / "slides" / "s1.png").write_bytes(b"x")
    (bundle / "slides" / "s2.png").write_bytes(b"x")

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
    assert "Variant Selection (A/B side-by-side)" in rendered
    assert "Full-Deck Preview (selected variants)" in rendered


def test_write_authorized_with_selection_metadata(tmp_path: Path) -> None:
    mod = _load_generate_module()
    bundle = tmp_path / "bundle"
    (bundle / "slides").mkdir(parents=True)
    (bundle / "slides" / "s1.png").write_bytes(b"x")
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
    assert data["selection_metadata"][0]["selected_variant"] == "A"
    assert data["selection_metadata"][0]["rejected_variant"] == "B"
