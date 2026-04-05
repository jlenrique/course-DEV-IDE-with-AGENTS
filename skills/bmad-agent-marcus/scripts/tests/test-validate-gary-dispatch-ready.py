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


# ---------------------------------------------------------------------------
# Content-bearing validation for literal-text slides
# Root cause: gary-slide-content.json populated with Irene planning directives
# instead of actual extracted source text for literal-text slides.
# ---------------------------------------------------------------------------


def _write_fidelity_slides(bundle_dir: Path, entries: list[dict]) -> None:
    """Write a minimal gary-fidelity-slides.json to the bundle dir."""
    (bundle_dir / "gary-fidelity-slides.json").write_text(
        json.dumps({"slides": entries}), encoding="utf-8"
    )


def _write_slide_content(bundle_dir: Path, slides: list[dict]) -> str:
    """Write gary-slide-content.json and return the relative filename."""
    (bundle_dir / "gary-slide-content.json").write_text(
        json.dumps({"slides": slides}), encoding="utf-8"
    )
    return "gary-slide-content.json"


def test_fails_when_literal_text_content_is_planning_directive(tmp_path: Path) -> None:
    """A literal-text slide whose content field contains a planning-directive
    pattern must cause validate_gary_dispatch_ready to return status='fail'.
    Anti-pattern detected: 'instructional content aligned to'."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)

    slides_content_path = _write_slide_content(
        bundle_dir,
        [
            {
                "slide_number": 1,
                "content": "Card 1: instructional content aligned to CLO2. Atmosphere + framing.",
                "source_ref": "extracted.md#anchor-1",
            },
            {
                "slide_number": 2,
                "content": "Card 2: instructional content aligned to CLO1. Retain terms.",
                "source_ref": "extracted.md#anchor-2",
            },
        ],
    )
    _write_fidelity_slides(
        bundle_dir,
        [
            {"slide_number": 1, "fidelity": "creative"},
            {"slide_number": 2, "fidelity": "literal-text"},
        ],
    )
    payload["dispatch_metadata"] = {"slides_content_json_path": slides_content_path}

    result = validate_gary_dispatch_ready(
        payload, payload_path=bundle_dir / "gary-dispatch-result.json"
    )

    assert result["status"] == "fail"
    assert any("planning directive" in msg.lower() for msg in result["errors"])


def test_passes_when_literal_text_content_is_real_source_text(tmp_path: Path) -> None:
    """A literal-text slide with substantive source-derived content must pass."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)

    slides_content_path = _write_slide_content(
        bundle_dir,
        [
            {
                "slide_number": 1,
                "content": "The Modern Clinician's Dilemma: physicians face administrative burnout.",
                "source_ref": "extracted.md#anchor-1",
            },
            {
                "slide_number": 2,
                "content": (
                    "By the end of this module, the learner will be able to:\n"
                    "1. Define the innovation mindset and correlate core clinical competencies.\n"
                    "2. Analyze macro-economic trends including administrative burnout.\n"
                    "3. Differentiate between a superficial idea and a vetted opportunity."
                ),
                "source_ref": "extracted.md#anchor-2",
            },
        ],
    )
    _write_fidelity_slides(
        bundle_dir,
        [
            {"slide_number": 1, "fidelity": "creative"},
            {"slide_number": 2, "fidelity": "literal-text"},
        ],
    )
    payload["dispatch_metadata"] = {"slides_content_json_path": slides_content_path}

    result = validate_gary_dispatch_ready(
        payload, payload_path=bundle_dir / "gary-dispatch-result.json"
    )

    assert result["status"] == "pass"
    assert result["errors"] == []


def test_fails_when_multiple_literal_text_slides_have_directives(tmp_path: Path) -> None:
    """All literal-text slides with planning directives should each produce an error."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)

    slides_content_path = _write_slide_content(
        bundle_dir,
        [
            {
                "slide_number": 1,
                "content": "Slide 1: instructional content aligned to CLO1. Retain wording.",
                "source_ref": "extracted.md#anchor-1",
            },
            {
                "slide_number": 2,
                "content": "Slide 2: instructional content aligned to CLO3. Keep action verbs.",
                "source_ref": "extracted.md#anchor-2",
            },
        ],
    )
    _write_fidelity_slides(
        bundle_dir,
        [
            {"slide_number": 1, "fidelity": "literal-text"},
            {"slide_number": 2, "fidelity": "literal-text"},
        ],
    )
    payload["dispatch_metadata"] = {"slides_content_json_path": slides_content_path}

    result = validate_gary_dispatch_ready(
        payload, payload_path=bundle_dir / "gary-dispatch-result.json"
    )

    assert result["status"] == "fail"
    planning_directive_errors = [
        msg for msg in result["errors"] if "planning directive" in msg.lower()
    ]
    assert len(planning_directive_errors) == 2, (
        f"Expected 2 planning-directive errors (one per literal-text slide), "
        f"got {len(planning_directive_errors)}: {planning_directive_errors}"
    )


def test_creative_slides_with_directive_pattern_do_not_fail(tmp_path: Path) -> None:
    """Creative slides are not subject to the planning-directive content check
    (Gamma's textMode=generate treats the content as a topic prompt; the slip
    is only fatal under textMode=preserve)."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)

    slides_content_path = _write_slide_content(
        bundle_dir,
        [
            {
                "slide_number": 1,
                "content": "Card 1: instructional content aligned to CLO2. Creative synthesis.",
                "source_ref": "extracted.md#anchor-1",
            },
            {
                "slide_number": 2,
                "content": "Card 2: instructional content aligned to CLO1. Creative synthesis.",
                "source_ref": "extracted.md#anchor-2",
            },
        ],
    )
    _write_fidelity_slides(
        bundle_dir,
        [
            {"slide_number": 1, "fidelity": "creative"},
            {"slide_number": 2, "fidelity": "creative"},
        ],
    )
    payload["dispatch_metadata"] = {"slides_content_json_path": slides_content_path}

    result = validate_gary_dispatch_ready(
        payload, payload_path=bundle_dir / "gary-dispatch-result.json"
    )

    assert result["status"] == "pass"
    assert not any("planning directive" in msg.lower() for msg in result["errors"])


def test_skips_content_check_when_fidelity_slides_absent(tmp_path: Path) -> None:
    """When gary-fidelity-slides.json is absent (e.g., older runs), the content
    check is skipped gracefully — no false positives."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)

    slides_content_path = _write_slide_content(
        bundle_dir,
        [
            {
                "slide_number": 1,
                "content": "Slide 1: instructional content aligned to CLO1.",
                "source_ref": "extracted.md#anchor-1",
            },
        ],
    )
    # Deliberately do NOT write gary-fidelity-slides.json
    payload["dispatch_metadata"] = {"slides_content_json_path": slides_content_path}

    result = validate_gary_dispatch_ready(
        payload, payload_path=bundle_dir / "gary-dispatch-result.json"
    )

    assert result["status"] == "pass"
    assert not any("planning directive" in msg.lower() for msg in result["errors"])


def test_literal_text_check_reports_exact_offending_slide_numbers(tmp_path: Path) -> None:
    """Only literal-text slides with directive-like content should be reported,
    and the error should identify the exact slide numbers."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)

    slides_content_path = _write_slide_content(
        bundle_dir,
        [
            {
                "slide_number": 1,
                "content": "Slide 1: instructional content aligned to CLO1.",
                "source_ref": "extracted.md#anchor-1",
            },
            {
                "slide_number": 2,
                "content": "Slide 2: Real source-derived instructional text for learners.",
                "source_ref": "extracted.md#anchor-2",
            },
        ],
    )
    _write_fidelity_slides(
        bundle_dir,
        [
            {"slide_number": 1, "fidelity": "literal-text"},
            {"slide_number": 2, "fidelity": "literal-text"},
        ],
    )
    payload["dispatch_metadata"] = {"slides_content_json_path": slides_content_path}

    result = validate_gary_dispatch_ready(
        payload, payload_path=bundle_dir / "gary-dispatch-result.json"
    )

    assert result["status"] == "fail"
    planning_errors = [
        msg
        for msg in result["errors"]
        if "planning directive" in msg.lower()
    ]
    assert len(planning_errors) == 1
    assert "slide 1" in planning_errors[0].lower()
    assert "slide 2" not in planning_errors[0].lower()


def test_literal_text_check_is_case_insensitive_for_directive_pattern(tmp_path: Path) -> None:
    """Regression: directive pattern matching must remain case-insensitive."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)

    slides_content_path = _write_slide_content(
        bundle_dir,
        [
            {
                "slide_number": 1,
                "content": "SLIDE 1: INSTRUCTIONAL CONTENT ALIGNED TO CLO3. KEEP TERMS.",
                "source_ref": "extracted.md#anchor-1",
            },
        ],
    )
    _write_fidelity_slides(
        bundle_dir,
        [
            {"slide_number": 1, "fidelity": "literal-text"},
        ],
    )
    payload["dispatch_metadata"] = {"slides_content_json_path": slides_content_path}

    result = validate_gary_dispatch_ready(
        payload, payload_path=bundle_dir / "gary-dispatch-result.json"
    )

    assert result["status"] == "fail"
    assert any("planning directive" in msg.lower() for msg in result["errors"])


def test_fails_when_literal_visual_content_contains_non_url_text(tmp_path: Path) -> None:
    """Literal-visual payload must be image-only (URL-only or empty content)."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)

    slides_content_path = _write_slide_content(
        bundle_dir,
        [
            {
                "slide_number": 1,
                "content": "https://example.com/diagram.png\n\nThis explanatory text must move to narration.",
                "source_ref": "extracted.md#anchor-visual-1",
            },
            {
                "slide_number": 2,
                "content": "Real source-derived text for literal-text slide.",
                "source_ref": "extracted.md#anchor-text-2",
            },
        ],
    )
    _write_fidelity_slides(
        bundle_dir,
        [
            {"slide_number": 1, "fidelity": "literal-visual"},
            {"slide_number": 2, "fidelity": "literal-text"},
        ],
    )
    payload["dispatch_metadata"] = {"slides_content_json_path": slides_content_path}

    result = validate_gary_dispatch_ready(
        payload, payload_path=bundle_dir / "gary-dispatch-result.json"
    )

    assert result["status"] == "fail"
    assert any(
        "literal-visual" in msg.lower() and "image-only" in msg.lower()
        for msg in result["errors"]
    )


def test_passes_when_literal_visual_content_is_url_only(tmp_path: Path) -> None:
    """A literal-visual slide may carry only a URL (or empty content) in gary-slide-content."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    payload = _valid_payload(bundle_dir)

    slides_content_path = _write_slide_content(
        bundle_dir,
        [
            {
                "slide_number": 1,
                "content": "https://example.com/diagram.png",
                "source_ref": "extracted.md#anchor-visual-1",
            },
            {
                "slide_number": 2,
                "content": "By the end of this module, learners will define the innovation mindset.",
                "source_ref": "extracted.md#anchor-text-2",
            },
        ],
    )
    _write_fidelity_slides(
        bundle_dir,
        [
            {"slide_number": 1, "fidelity": "literal-visual"},
            {"slide_number": 2, "fidelity": "literal-text"},
        ],
    )
    payload["dispatch_metadata"] = {"slides_content_json_path": slides_content_path}

    result = validate_gary_dispatch_ready(
        payload, payload_path=bundle_dir / "gary-dispatch-result.json"
    )

    assert result["status"] == "pass"
    assert not any("literal-visual" in msg.lower() for msg in result["errors"])
