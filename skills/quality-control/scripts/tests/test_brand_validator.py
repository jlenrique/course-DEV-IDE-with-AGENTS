"""Tests for brand_validator.py."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "brand_validator",
    Path(__file__).resolve().parent.parent / "brand_validator.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestCheckColorCompliance:
    def test_palette_color_passes(self):
        content = "Use color #1e3a5f for headers."
        findings = mod.check_color_compliance(content, mod.DEFAULT_BRAND_MARKERS["colors"])
        assert len(findings) == 0

    def test_non_palette_color_flagged(self):
        content = "Use color #ff0000 for highlights."
        findings = mod.check_color_compliance(content, mod.DEFAULT_BRAND_MARKERS["colors"])
        assert len(findings) == 1
        assert findings[0]["severity"] == "medium"
        assert "#ff0000" in findings[0]["description"]

    def test_multiple_violations(self):
        content = "Colors: #ff0000 and #00ff00 used."
        findings = mod.check_color_compliance(content, mod.DEFAULT_BRAND_MARKERS["colors"])
        assert len(findings) == 2


class TestCheckFontCompliance:
    def test_brand_font_passes(self):
        content = "Font: Montserrat"
        findings = mod.check_font_compliance(content, mod.DEFAULT_BRAND_MARKERS["fonts"])
        assert len(findings) == 0

    def test_non_brand_font_flagged(self):
        content = "Font: Comic Sans for body text."
        findings = mod.check_font_compliance(content, mod.DEFAULT_BRAND_MARKERS["fonts"])
        assert len(findings) == 1
        assert "Comic Sans" in findings[0]["description"]


class TestRunBrandValidation:
    def test_clean_content_passes(self):
        content = "Using #1e3a5f for headers with clean design."
        result = mod.run_brand_validation(content)
        assert result["status"] == "pass"
        assert result["compliance_score"] == 1.0

    def test_violations_reduce_score(self):
        content = "Color #ff0000 and #00ff00 used. Font: Arial everywhere."
        result = mod.run_brand_validation(content)
        assert result["compliance_score"] < 1.0
        assert result["summary"]["total"] > 0

    def test_no_style_bible_uses_defaults(self):
        content = "Simple content with no brand references."
        result = mod.run_brand_validation(content, style_bible_path=Path("/nonexistent"))
        assert result["checker"] == "brand_validation"
        assert "colors" in result["brand_markers_used"]
