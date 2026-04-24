"""Tests for the Image intake provider (Story 27-3).

The image bridge lives at `skills/sensory-bridges/scripts/image_to_agent.py`
(hyphenated directory prevents plain `from ... import`). Tests substitute a
``FakeImageAnalyzer`` for the production ``VisionLLMAnalyzer`` stub via
dependency injection so unit coverage does not require a vision API key or
a live vision backend — this mirrors the Box provider's ``FakeBoxFetcher``
pattern from Story 27-6.

Coverage (K>=14, target 15-18 per Amelia green-light rider):

  Happy paths (4):
    1. JPEG happy path — pre-computed perception flows through to the
       wrangle_* contract triple.
    2. PNG happy path.
    3. WebP happy path.
    4. Mixed-case suffix (`.JPG`) normalized and accepted.

  Negative paths (5 — Murat rider):
    5. Unsupported suffix (`.bmp`) raises ImageFetchError with remediation.
    6. OCR-empty + no elements + no layout → ImageOCRFailureError.
    7. Default VisionLLMAnalyzer → ImageVisionAPIError with remediation.
    8. Corrupt-header bytes → ImageDecodeError.
    9. Missing file → ImageFetchError with remediation.

  Structural / integration (3):
    10. Provenance shape — sha256 prefix + bridge_version + suffix + size in note.
    11. `extraction_validator._WORDS_PER_PAGE["image"] == 60` lookup correct.
    12. Directive-schema validator accepts visual-primary / visual-supplementary.

  Registry + portability (2):
    13. AST guard — image_to_agent.py has no marcus.orchestrator/dispatch imports.
    14. Transform-registry lockstep — "image (intake via sensory-bridges)"
        is in LOCKSTEP_EXEMPTIONS with a rationale.

  Stretch (15-18 — Amelia target):
    15. Body shape-pin — canonical section headings in expected order.
    16. run_wrangler._fetch_source('image', ...) dispatches end-to-end
        through _wrangle_image_via_bridge.
    17. assess_image_fidelity boundary transitions (high / medium / low / none).
    18. SCHEMA_CHANGELOG has the Sprint 2 Image Intake entry.
"""

from __future__ import annotations

import ast
import importlib.util
import struct
import sys
import zlib
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loading via importlib.util (hyphenated skill directories)
# ---------------------------------------------------------------------------

_ROOT = Path(__file__).resolve().parent.parent
_BRIDGE_PATH = (
    _ROOT / "skills" / "sensory-bridges" / "scripts" / "image_to_agent.py"
)
_spec = importlib.util.spec_from_file_location(
    "texas_image_bridge_tests", _BRIDGE_PATH
)
assert _spec is not None and _spec.loader is not None
bridge = importlib.util.module_from_spec(_spec)
sys.modules["texas_image_bridge_tests"] = bridge
_spec.loader.exec_module(bridge)


_RUNNER_PATH = _ROOT / "skills" / "bmad-agent-texas" / "scripts" / "run_wrangler.py"
_runner_spec = importlib.util.spec_from_file_location(
    "texas_run_wrangler_image_tests", _RUNNER_PATH
)
assert _runner_spec is not None and _runner_spec.loader is not None
runner = importlib.util.module_from_spec(_runner_spec)
sys.modules["texas_run_wrangler_image_tests"] = runner
_runner_spec.loader.exec_module(runner)


_VALIDATOR_PATH = (
    _ROOT / "skills" / "bmad-agent-texas" / "scripts" / "extraction_validator.py"
)
_validator_spec = importlib.util.spec_from_file_location(
    "texas_extraction_validator_image_tests", _VALIDATOR_PATH
)
assert _validator_spec is not None and _validator_spec.loader is not None
ev = importlib.util.module_from_spec(_validator_spec)
sys.modules["texas_extraction_validator_image_tests"] = ev
_validator_spec.loader.exec_module(ev)


# ---------------------------------------------------------------------------
# Byte fixtures — real header-valid images without requiring Pillow
# ---------------------------------------------------------------------------


def _minimal_png_bytes(width: int = 4, height: int = 3) -> bytes:
    """Build a minimal header-valid PNG with valid IHDR + a tiny IDAT + IEND."""
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    ihdr = b"IHDR" + ihdr_data
    ihdr_chunk = struct.pack(">I", len(ihdr_data)) + ihdr + struct.pack(
        ">I", zlib.crc32(ihdr)
    )
    # Grayscale 4x3 pixels: each row = filter byte 0 + <width> pixel bytes
    raw = b"".join(b"\x00" + b"\x80" * width for _ in range(height))
    compressed = zlib.compress(raw)
    idat = b"IDAT" + compressed
    idat_chunk = struct.pack(">I", len(compressed)) + idat + struct.pack(
        ">I", zlib.crc32(idat)
    )
    iend = b"IEND"
    iend_chunk = struct.pack(">I", 0) + iend + struct.pack(">I", zlib.crc32(iend))
    return sig + ihdr_chunk + idat_chunk + iend_chunk


def _minimal_jpeg_bytes() -> bytes:
    """Build a JPEG with SOI + SOF0 (so dimensions can be parsed) + EOI."""
    soi = b"\xff\xd8"
    # SOF0: marker 0xFFC0, length=17, precision=8, height=16, width=24, components=3
    sof0 = b"\xff\xc0" + struct.pack(">HBHHB", 17, 8, 16, 24, 3)
    sof0 += b"\x01\x11\x00\x02\x11\x01\x03\x11\x01"
    eoi = b"\xff\xd9"
    return soi + sof0 + eoi


def _minimal_webp_bytes() -> bytes:
    """Build a minimal WebP VP8L container with a readable VP8L header."""
    riff_header = b"RIFF"
    webp_sig = b"WEBP"
    vp8l_chunk_id = b"VP8L"
    # VP8L payload: 1-byte signature (0x2F) + 4 bytes encoding width-1/height-1
    # For width=8, height=4 → width_minus_one=7, height_minus_one=3.
    # Bit-packing per VP8L spec (14 bits each):
    #   b[0] = (width_m1 & 0xFF)        = 0x07
    #   b[1] = ((width_m1 >> 8) & 0x3F) | ((height_m1 & 0x03) << 6) = 0x00 | (3 << 6) = 0xC0
    #   b[2] = (height_m1 >> 2) & 0xFF  = 0x00
    #   b[3] = 0 (alpha_is_used=0, version_number=0)
    vp8l_payload = b"\x2F" + b"\x07\xC0\x00\x00"
    vp8l_chunk = vp8l_chunk_id + struct.pack("<I", len(vp8l_payload)) + vp8l_payload
    riff_body = webp_sig + vp8l_chunk
    riff_size = len(riff_body)
    return riff_header + struct.pack("<I", riff_size) + riff_body


# ---------------------------------------------------------------------------
# FakeImageAnalyzer — DI substitute
# ---------------------------------------------------------------------------


class FakeImageAnalyzer(bridge.ImageAnalyzer):
    """In-memory analyzer that returns a pre-scripted ImagePerception."""

    def __init__(self, perception: bridge.ImagePerception) -> None:
        self.perception = perception
        self.calls: list[Path] = []

    def analyze(self, path: Path) -> bridge.ImagePerception:
        self.calls.append(Path(path))
        return self.perception


def _rich_perception() -> bridge.ImagePerception:
    return bridge.ImagePerception(
        caption=(
            "A three-column roadmap comparing the strategies for the first, "
            "second, and third quarters of a course revision project."
        ),
        extracted_text=(
            "Q1 DISCOVERY\nScope study + exemplar review\n"
            "Q2 DESIGN\nContent creation + review cycles\n"
            "Q3 DELIVERY\nPilot cohort + iteration\nMetrics dashboard"
        ),
        visual_elements=[
            {"type": "column", "description": "Q1 milestones"},
            {"type": "column", "description": "Q2 milestones"},
            {"type": "column", "description": "Q3 milestones"},
            {"type": "arrow", "description": "sequence arrow across columns"},
        ],
        layout_description=(
            "Three equally spaced columns reading left to right, with a "
            "horizontal arrow beneath spanning all three."
        ),
        slide_title="Course revision roadmap",
        text_blocks=[
            "Q1 DISCOVERY",
            "Scope study + exemplar review",
            "Q2 DESIGN",
            "Content creation + review cycles",
            "Q3 DELIVERY",
            "Pilot cohort + iteration",
            "Metrics dashboard",
        ],
        confidence="HIGH",
        confidence_rationale="OCR-clean roadmap with labeled columns.",
    )


# ---------------------------------------------------------------------------
# 1-4. Happy paths
# ---------------------------------------------------------------------------


def test_jpeg_happy_path_produces_wrangle_contract(tmp_path: Path) -> None:
    path = tmp_path / "roadmap.jpg"
    path.write_bytes(_minimal_jpeg_bytes())
    analyzer = FakeImageAnalyzer(_rich_perception())

    title, body, rec = bridge.wrangle_local_image(path, analyzer=analyzer)

    assert title == "roadmap"
    assert rec.kind == "image_source"
    assert rec.ref.startswith("image://")
    assert "## Caption" in body
    assert "Q1 DISCOVERY" in body
    assert len(analyzer.calls) == 1


def test_png_happy_path(tmp_path: Path) -> None:
    path = tmp_path / "funnel.png"
    path.write_bytes(_minimal_png_bytes(width=4, height=3))
    analyzer = FakeImageAnalyzer(_rich_perception())

    title, body, rec = bridge.wrangle_local_image(path, analyzer=analyzer)

    assert title == "funnel"
    assert rec.kind == "image_source"
    assert "## Visual elements" in body


def test_webp_happy_path(tmp_path: Path) -> None:
    path = tmp_path / "diagram.webp"
    path.write_bytes(_minimal_webp_bytes())
    analyzer = FakeImageAnalyzer(_rich_perception())

    title, _body, rec = bridge.wrangle_local_image(path, analyzer=analyzer)

    assert title == "diagram"
    assert rec.kind == "image_source"


def test_uppercase_suffix_normalized(tmp_path: Path) -> None:
    path = tmp_path / "CHART.JPG"
    path.write_bytes(_minimal_jpeg_bytes())
    analyzer = FakeImageAnalyzer(_rich_perception())

    title, _body, rec = bridge.wrangle_local_image(path, analyzer=analyzer)

    assert title == "CHART"
    assert rec.kind == "image_source"


# ---------------------------------------------------------------------------
# 5-9. Negative paths
# ---------------------------------------------------------------------------


def test_unsupported_suffix_raises_fetch_error_with_remediation(
    tmp_path: Path,
) -> None:
    path = tmp_path / "snapshot.bmp"
    path.write_bytes(b"\x00" * 32)
    analyzer = FakeImageAnalyzer(_rich_perception())

    with pytest.raises(bridge.ImageFetchError) as exc_info:
        bridge.wrangle_local_image(path, analyzer=analyzer)

    msg = str(exc_info.value)
    assert ".bmp" in msg
    assert "Supported suffixes" in msg
    assert ".jpg" in msg and ".png" in msg


def test_empty_perception_raises_ocr_failure(tmp_path: Path) -> None:
    path = tmp_path / "blank.png"
    path.write_bytes(_minimal_png_bytes())
    empty = bridge.ImagePerception(
        caption="",
        extracted_text="",
        visual_elements=[],
        layout_description="",
        confidence="LOW",
        confidence_rationale="no signal",
    )
    analyzer = FakeImageAnalyzer(empty)

    with pytest.raises(bridge.ImageOCRFailureError) as exc_info:
        bridge.wrangle_local_image(path, analyzer=analyzer)

    assert "no perceivable signal" in str(exc_info.value)
    # Remediation text carries operator-actionable options
    assert "Options:" in str(exc_info.value)
    assert "visual-supplementary" in str(exc_info.value)


def test_default_analyzer_raises_vision_unavailable(tmp_path: Path) -> None:
    path = tmp_path / "slide.png"
    path.write_bytes(_minimal_png_bytes())

    with pytest.raises(bridge.ImageVisionAPIError) as exc_info:
        bridge.wrangle_local_image(path)  # no analyzer -> VisionLLMAnalyzer

    msg = str(exc_info.value)
    assert "vision" in msg.lower()
    assert "Story 27-3b" in msg or "follow-on" in msg


def test_corrupt_header_raises_decode_error(tmp_path: Path) -> None:
    path = tmp_path / "truncated.png"
    # Wrong suffix for these bytes: claim PNG but write JPEG header
    path.write_bytes(_minimal_jpeg_bytes())
    analyzer = FakeImageAnalyzer(_rich_perception())

    with pytest.raises(bridge.ImageDecodeError):
        bridge.wrangle_local_image(path, analyzer=analyzer)


def test_missing_file_raises_fetch_error(tmp_path: Path) -> None:
    path = tmp_path / "nonexistent.png"
    analyzer = FakeImageAnalyzer(_rich_perception())

    with pytest.raises(bridge.ImageFetchError) as exc_info:
        bridge.wrangle_local_image(path, analyzer=analyzer)

    assert "not found" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# 10-12. Structural / integration
# ---------------------------------------------------------------------------


def test_provenance_note_carries_sha_and_bridge_version(tmp_path: Path) -> None:
    path = tmp_path / "img.png"
    path.write_bytes(_minimal_png_bytes())
    analyzer = FakeImageAnalyzer(_rich_perception())

    _, _, rec = bridge.wrangle_local_image(path, analyzer=analyzer)

    assert "sha256=" in rec.note
    assert bridge.BRIDGE_VERSION in rec.note
    assert "suffix=.png" in rec.note
    assert "size=" in rec.note
    assert "fidelity=" in rec.note
    assert "perceived_words=" in rec.note
    assert "confidence=HIGH" in rec.note
    # sha256-prefix in ref
    sha_from_ref = rec.ref.removeprefix("image://")
    assert sha_from_ref and all(c in "0123456789abcdef" for c in sha_from_ref)
    assert f"sha256={sha_from_ref}" in rec.note


def test_words_per_page_image_floor_is_sixty() -> None:
    assert ev._WORDS_PER_PAGE["image"] == 60


def test_directive_validator_accepts_visual_roles(tmp_path: Path) -> None:
    """Ensure run_wrangler's directive validator accepts visual-primary /
    visual-supplementary and that visual-primary counts as a primary-class
    role for the at-least-one-primary requirement."""
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        "run_id: img-visual-roles-test\n"
        "sources:\n"
        "  - ref_id: img-1\n"
        "    role: visual-primary\n"
        "    provider: image\n"
        "    locator: /tmp/roadmap.png\n"
        "  - ref_id: img-2\n"
        "    role: visual-supplementary\n"
        "    provider: image\n"
        "    locator: /tmp/appendix.png\n",
        encoding="utf-8",
    )
    data = runner._load_directive(directive)
    assert data["_directive_shape"] == "locator"
    roles = [s["role"] for s in data["sources"]]
    assert "visual-primary" in roles
    assert "visual-supplementary" in roles

    # Invalid role rejected
    bad_directive = tmp_path / "bad.yaml"
    bad_directive.write_text(
        "run_id: bad\n"
        "sources:\n"
        "  - ref_id: bad-1\n"
        "    role: not-a-role\n"
        "    provider: image\n"
        "    locator: /tmp/x.png\n",
        encoding="utf-8",
    )
    with pytest.raises(runner.DirectiveError) as exc_info:
        runner._load_directive(bad_directive)
    assert "visual-primary" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 13-14. Registry + portability
# ---------------------------------------------------------------------------


def test_image_bridge_has_no_marcus_orchestrator_imports() -> None:
    """Sprint 2 LangGraph-portability guard — image bridge must not import
    marcus.orchestrator.* / marcus.dispatch.*.
    """
    tree = ast.parse(_BRIDGE_PATH.read_text(encoding="utf-8"))
    forbidden = ("marcus.orchestrator", "marcus.dispatch")
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name.startswith(p) for p in forbidden):
                    offenders.append(alias.name)
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(mod.startswith(p) for p in forbidden):
                offenders.append(mod)
    assert not offenders, (
        f"image_to_agent.py imports forbidden orchestrator/dispatch modules: "
        f"{offenders}. Image intake must remain a leaf IO adapter per Sprint 2 "
        f"LangGraph-portability rulings."
    )


def test_transform_registry_exempts_image_intake() -> None:
    contract_path = (
        _ROOT / "tests" / "contracts" / "test_transform_registry_lockstep.py"
    )
    text = contract_path.read_text(encoding="utf-8")
    assert '"image (intake via sensory-bridges)"' in text, (
        "LOCKSTEP_EXEMPTIONS must contain 'image (intake via sensory-bridges)' "
        "so the transform-registry lockstep test accepts the Image section"
    )


# ---------------------------------------------------------------------------
# 15-18. Stretch coverage
# ---------------------------------------------------------------------------


def test_body_has_canonical_section_order(tmp_path: Path) -> None:
    path = tmp_path / "map.png"
    path.write_bytes(_minimal_png_bytes())
    analyzer = FakeImageAnalyzer(_rich_perception())

    _, body, _ = bridge.wrangle_local_image(path, analyzer=analyzer)

    order = [
        body.index("## Caption"),
        body.index("## Detected text (OCR)"),
        body.index("## Visual elements"),
        body.index("## Layout"),
        body.index("## Tier classification"),
    ]
    assert order == sorted(order), (
        "Canonical body sections must appear in fixed order: "
        "Caption, Detected text (OCR), Visual elements, Layout, "
        "Tier classification."
    )
    # Tier-classification footer carries the AC-4 semantic labels (markdown bold)
    assert "**visual_structural_fidelity:**" in body
    assert "**visual_completeness:**" in body
    assert f"**bridge_version:** {bridge.BRIDGE_VERSION}" in body


def test_runner_dispatch_routes_image_provider_end_to_end(tmp_path: Path) -> None:
    """Runner's _fetch_source dispatches provider='image' into the bridge via
    the DI seam src['_image_analyzer']."""
    path = tmp_path / "panel.jpg"
    path.write_bytes(_minimal_jpeg_bytes())
    analyzer = FakeImageAnalyzer(_rich_perception())
    src = {
        "ref_id": "img-1",
        "role": "visual-primary",
        "provider": "image",
        "locator": str(path),
        "_image_analyzer": analyzer,
    }

    title, body, rec = runner._fetch_source(src)

    assert title == "panel"
    assert rec.kind == "image_source"
    assert rec.ref.startswith("image://")
    assert "## Detected text (OCR)" in body
    assert len(analyzer.calls) == 1


def test_assess_image_fidelity_boundaries() -> None:
    # HIGH: 2+ elements, 20+ OCR words, layout, confidence HIGH
    high = bridge.ImagePerception(
        caption="c",
        extracted_text=" ".join(["w"] * 25),
        visual_elements=[{"type": "a"}, {"type": "b"}],
        layout_description="left-right split",
        confidence="HIGH",
    )
    fidelity, words = bridge.assess_image_fidelity(high)
    assert fidelity == "high"
    assert words == 25 + 2 * 3

    # MEDIUM: 1 element + 10 OCR words
    medium = bridge.ImagePerception(
        caption="",
        extracted_text=" ".join(["w"] * 12),
        visual_elements=[{"type": "a"}],
        layout_description="",
        confidence="MEDIUM",
    )
    fidelity, _ = bridge.assess_image_fidelity(medium)
    assert fidelity == "medium"

    # LOW: sparse
    low = bridge.ImagePerception(
        caption="",
        extracted_text="hi",
        visual_elements=[],
        layout_description="",
        confidence="LOW",
    )
    fidelity, _ = bridge.assess_image_fidelity(low)
    assert fidelity == "low"

    # NONE
    none = bridge.ImagePerception(
        caption="",
        extracted_text="",
        visual_elements=[],
        layout_description="",
        confidence="LOW",
    )
    fidelity, words = bridge.assess_image_fidelity(none)
    assert fidelity == "none"
    assert words == 0


def test_schema_changelog_has_image_intake_entry() -> None:
    changelog_path = (
        _ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "SCHEMA_CHANGELOG.md"
    )
    text = changelog_path.read_text(encoding="utf-8")
    assert "Sprint #2 Image Intake v1.0" in text
    assert "Story 27-3 Image Provider" in text
    assert 'SUPPORTED_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".webp"})' in text
