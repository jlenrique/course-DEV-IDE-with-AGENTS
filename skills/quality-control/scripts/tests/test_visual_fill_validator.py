"""Tests for visual_fill_validator.py — edge-band and variance-based fill detection."""

import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw

spec = importlib.util.spec_from_file_location(
    "visual_fill_validator",
    Path(__file__).resolve().parent.parent / "visual_fill_validator.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


# ── Helpers ────────────────────────────────────────────────────

def _make_blank(tmp_path: Path, w: int = 2400, h: int = 1350) -> Path:
    """Create a pure white PNG."""
    p = tmp_path / "blank.png"
    Image.new("RGB", (w, h), (255, 255, 255)).save(p, "PNG")
    return p


def _make_dark_content(tmp_path: Path, w: int = 2400, h: int = 1350) -> Path:
    """Create a dark PNG with enough variance to count as real content."""
    p = tmp_path / "dark_content.png"
    img = Image.new("RGB", (w, h), (30, 60, 120))
    draw = ImageDraw.Draw(img)
    # Add enough variation to push stddev well above 25
    draw.rectangle([0, 0, w // 2, h // 2], fill=(180, 40, 40))
    draw.rectangle([w // 2, 0, w, h // 2], fill=(40, 160, 40))
    draw.rectangle([0, h // 2, w // 2, h], fill=(40, 40, 180))
    img.save(p, "PNG")
    return p


def _make_real_content(tmp_path: Path, w: int = 2400, h: int = 1350) -> Path:
    """Create a PNG with diverse colors simulating real slide content."""
    p = tmp_path / "real_content.png"
    img = Image.new("RGB", (w, h), (30, 60, 120))
    draw = ImageDraw.Draw(img)
    # Draw diverse colored rectangles to create high variance
    draw.rectangle([0, 0, w // 3, h // 3], fill=(200, 50, 50))
    draw.rectangle([w // 3, 0, 2 * w // 3, h // 3], fill=(50, 200, 50))
    draw.rectangle([2 * w // 3, 0, w, h // 3], fill=(50, 50, 200))
    draw.rectangle([0, h // 2, w, h], fill=(220, 180, 40))
    draw.rectangle([w // 4, h // 4, 3 * w // 4, 3 * h // 4], fill=(100, 150, 200))
    img.save(p, "PNG")
    return p


def _make_faded(tmp_path: Path, w: int = 2400, h: int = 1350) -> Path:
    """Create a PNG simulating a faded/background-treated slide.

    Very light colors, low variance (~stddev 5-20), like Gamma's faded output.
    Must be above blank (~0) but below content threshold (25).
    """
    p = tmp_path / "faded.png"
    img = Image.new("RGB", (w, h), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    # Moderate variation to land in the faded zone (stddev 5-25)
    draw.rectangle([0, 0, w // 2, h // 2], fill=(230, 232, 228))
    draw.rectangle([w // 2, 0, w, h // 2], fill=(240, 238, 242))
    draw.rectangle([0, h // 2, w // 2, h], fill=(235, 240, 235))
    draw.rectangle([w // 4, h // 4, 3 * w // 4, 3 * h // 4], fill=(220, 225, 220))
    img.save(p, "PNG")
    return p


def _make_light_edges_high_variance(tmp_path: Path, w: int = 2400, h: int = 1350) -> Path:
    """Create a PNG with light/white edges but strong content in the center.

    Simulates infographic images that have white borders but rich center content.
    The validator should pass this (stddev > 40 overrides edge check).
    """
    p = tmp_path / "light_edges.png"
    img = Image.new("RGB", (w, h), (252, 252, 252))  # near-white background
    draw = ImageDraw.Draw(img)
    # Rich content in center
    draw.rectangle([w // 6, h // 6, 5 * w // 6, 5 * h // 6], fill=(20, 80, 160))
    draw.rectangle([w // 4, h // 4, 3 * w // 4, 3 * h // 4], fill=(200, 40, 40))
    draw.rectangle([w // 3, h // 3, 2 * w // 3, 2 * h // 3], fill=(40, 180, 60))
    img.save(p, "PNG")
    return p


# ── TestEdgeFillRatio ──────────────────────────────────────────

class TestEdgeFillRatio:
    def test_all_white_returns_zero_fill(self, tmp_path: Path) -> None:
        img = Image.open(_make_blank(tmp_path))
        ratios = mod._edge_fill_ratio(img)
        for edge, ratio in ratios.items():
            assert ratio == 0.0, f"{edge} should be 0 for all-white image"

    def test_all_dark_returns_high_fill(self, tmp_path: Path) -> None:
        img = Image.open(_make_dark_content(tmp_path))
        ratios = mod._edge_fill_ratio(img)
        for edge, ratio in ratios.items():
            assert ratio >= 0.99, f"{edge} should be ~1.0 for solid dark image"

    def test_mixed_content_has_varying_ratios(self, tmp_path: Path) -> None:
        img = Image.open(_make_real_content(tmp_path))
        ratios = mod._edge_fill_ratio(img)
        # At least some edges should have content
        assert any(r > 0.5 for r in ratios.values())


# ── TestContentStddev ──────────────────────────────────────────

class TestContentStddev:
    def test_blank_white_near_zero(self, tmp_path: Path) -> None:
        img = Image.open(_make_blank(tmp_path))
        stddev = mod._content_stddev(img)
        assert stddev < 1.0, f"Blank image stddev should be ~0, got {stddev}"

    def test_solid_color_near_zero(self, tmp_path: Path) -> None:
        p = tmp_path / "solid.png"
        Image.new("RGB", (2400, 1350), (30, 60, 120)).save(p, "PNG")
        img = Image.open(p)
        stddev = mod._content_stddev(img)
        assert stddev < 1.0, f"Solid color stddev should be ~0, got {stddev}"

    def test_faded_image_low_variance(self, tmp_path: Path) -> None:
        img = Image.open(_make_faded(tmp_path))
        stddev = mod._content_stddev(img)
        assert 1.0 < stddev < 25.0, f"Faded image stddev should be ~5-15, got {stddev}"

    def test_real_content_high_variance(self, tmp_path: Path) -> None:
        img = Image.open(_make_real_content(tmp_path))
        stddev = mod._content_stddev(img)
        assert stddev > 25.0, f"Real content stddev should be >25, got {stddev}"


# ── TestValidateVisualFill ─────────────────────────────────────

class TestValidateVisualFill:
    def test_blank_slide_fails(self, tmp_path: Path) -> None:
        result = mod.validate_visual_fill(str(_make_blank(tmp_path)))
        assert result["passed"] is False
        assert any("blank" in f for f in result["failures"])
        assert result["content_stddev"] < 5.0

    def test_faded_slide_fails(self, tmp_path: Path) -> None:
        result = mod.validate_visual_fill(str(_make_faded(tmp_path)))
        assert result["passed"] is False
        assert any("faded" in f or "degraded" in f for f in result["failures"])

    def test_real_content_dark_slide_passes(self, tmp_path: Path) -> None:
        result = mod.validate_visual_fill(str(_make_dark_content(tmp_path)))
        assert result["passed"] is True

    def test_real_content_diverse_slide_passes(self, tmp_path: Path) -> None:
        result = mod.validate_visual_fill(str(_make_real_content(tmp_path)))
        assert result["passed"] is True
        assert result["content_stddev"] > 25.0

    def test_light_edges_high_variance_passes(self, tmp_path: Path) -> None:
        """Infographic with white edges but rich center should pass (stddev > 40)."""
        result = mod.validate_visual_fill(str(_make_light_edges_high_variance(tmp_path)))
        assert result["passed"] is True, (
            f"High-variance image with light edges should pass; "
            f"stddev={result.get('content_stddev')}, failures={result.get('failures')}"
        )

    def test_content_stddev_field_present(self, tmp_path: Path) -> None:
        result = mod.validate_visual_fill(str(_make_blank(tmp_path)))
        assert "content_stddev" in result
        assert isinstance(result["content_stddev"], float)

    def test_missing_file_returns_error(self, tmp_path: Path) -> None:
        result = mod.validate_visual_fill(str(tmp_path / "nonexistent.png"))
        assert result["passed"] is False
        assert "File not found" in result.get("error", "")

    def test_dimensions_in_result(self, tmp_path: Path) -> None:
        result = mod.validate_visual_fill(str(_make_blank(tmp_path)))
        assert result["dimensions"]["width"] == 2400
        assert result["dimensions"]["height"] == 1350


# ── TestValidateLiteralVisualSlides ────────────────────────────

class TestValidateLiteralVisualSlides:
    def test_no_literal_visual_slides_passes(self) -> None:
        result = mod.validate_literal_visual_slides([
            {"fidelity": "creative", "file_path": "x.png", "card_number": 1},
        ])
        assert result["passed"] is True
        assert result["checked"] == 0

    def test_filters_only_literal_visual(self, tmp_path: Path) -> None:
        good = _make_dark_content(tmp_path)
        slides = [
            {"fidelity": "creative", "file_path": "creative.png", "card_number": 1},
            {"fidelity": "literal-visual", "file_path": str(good), "card_number": 2},
        ]
        result = mod.validate_literal_visual_slides(slides)
        assert result["checked"] == 1
        assert result["passed"] is True

    def test_one_failure_fails_overall(self, tmp_path: Path) -> None:
        good = _make_dark_content(tmp_path)
        bad = _make_blank(tmp_path)
        # Rename to avoid collision
        bad_renamed = tmp_path / "blank2.png"
        bad.rename(bad_renamed)
        slides = [
            {"fidelity": "literal-visual", "file_path": str(good), "card_number": 1},
            {"fidelity": "literal-visual", "file_path": str(bad_renamed), "card_number": 2},
        ]
        result = mod.validate_literal_visual_slides(slides)
        assert result["checked"] == 2
        assert result["passed"] is False
