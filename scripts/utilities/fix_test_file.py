"""One-shot script: truncate the test file after the last valid test and rewrite the new section."""
from pathlib import Path

path = Path("skills/bmad-agent-marcus/scripts/tests/test-validate-gary-dispatch-ready.py")
content = path.read_text(encoding="utf-8")

# The last valid test function body ends with this exact string (the old ending)
CUTMARKER = "        assert any(\"validator_exception:\" in msg for msg in data.get(\"errors\", []))\n"

idx = content.rfind(CUTMARKER)
if idx == -1:
    raise RuntimeError("Could not find cut marker")

cut_at = idx + len(CUTMARKER)
head = content[:cut_at]

new_section = '''

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
    pattern must cause validate_gary_dispatch_ready to return status=\'fail\'.
    Anti-pattern detected: \'instructional content aligned to\'."""
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
                "content": "The Modern Clinician\'s Dilemma: physicians face administrative burnout.",
                "source_ref": "extracted.md#anchor-1",
            },
            {
                "slide_number": 2,
                "content": (
                    "By the end of this module, the learner will be able to:\\n"
                    "1. Define the innovation mindset and correlate core clinical competencies.\\n"
                    "2. Analyze macro-economic trends including administrative burnout.\\n"
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
    (Gamma\'s textMode=generate treats the content as a topic prompt; the slip
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
'''

path.write_text(head + new_section, encoding="utf-8")
print(f"Done. Total lines: {(head + new_section).count(chr(10))}")
