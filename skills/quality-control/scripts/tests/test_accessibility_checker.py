"""Tests for accessibility_checker.py."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "accessibility_checker",
    Path(__file__).resolve().parent.parent / "accessibility_checker.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestFleschKincaidGrade:
    def test_simple_text_low_grade(self):
        text = "The cat sat on the mat. The dog ran fast."
        grade = mod.flesch_kincaid_grade(text)
        assert grade < 6.0

    def test_complex_text_high_grade(self):
        text = (
            "The pharmacokinetic properties of anticoagulant medications "
            "necessitate careful consideration of hepatic metabolism and "
            "renal clearance parameters when determining appropriate "
            "therapeutic dosing regimens for geriatric patients with "
            "comorbid cardiovascular conditions."
        )
        grade = mod.flesch_kincaid_grade(text)
        assert grade > 12.0

    def test_empty_text_returns_zero(self):
        assert mod.flesch_kincaid_grade("") == 0.0


class TestCountSyllables:
    def test_one_syllable(self):
        assert mod._count_syllables("cat") == 1

    def test_two_syllables(self):
        assert mod._count_syllables("happy") == 2

    def test_three_syllables(self):
        assert mod._count_syllables("pharmacy") == 3


class TestHeadingHierarchy:
    def test_valid_hierarchy(self):
        text = "# Title\n## Section\n### Subsection\n"
        findings = mod.check_heading_hierarchy(text)
        assert len(findings) == 0

    def test_skip_detected(self):
        text = "# Title\n## Section\n#### Deep Skip\n"
        findings = mod.check_heading_hierarchy(text)
        assert len(findings) == 1
        assert findings[0]["severity"] == "critical"
        assert "H2 → H4" in findings[0]["description"]

    def test_multiple_skips(self):
        text = "# Title\n### Skip One\n##### Skip Two\n"
        findings = mod.check_heading_hierarchy(text)
        assert len(findings) == 2


class TestAltText:
    def test_valid_alt_text(self):
        text = "![A clinical diagram](image.png)\n"
        findings = mod.check_alt_text(text)
        assert len(findings) == 0

    def test_missing_alt_text(self):
        text = "![](image.png)\n"
        findings = mod.check_alt_text(text)
        assert len(findings) == 1
        assert findings[0]["severity"] == "critical"


class TestContentDensity:
    def test_short_block_passes(self):
        text = "Short content block with few words."
        findings = mod.check_content_density(text)
        assert len(findings) == 0

    def test_long_block_flagged(self):
        text = " ".join(["word"] * 250)
        findings = mod.check_content_density(text, max_words_per_block=200)
        assert len(findings) == 1
        assert findings[0]["severity"] == "medium"


class TestRunAccessibilityCheck:
    def test_clean_content_passes(self):
        text = "# Title\n## Section\nSimple clear content. Easy to read.\n"
        result = mod.run_accessibility_check(text)
        assert result["status"] == "pass"
        assert result["checker"] == "accessibility"

    def test_heading_skip_fails(self):
        text = "# Title\n#### Skip\nContent here.\n"
        result = mod.run_accessibility_check(text)
        assert result["status"] == "fail"
        assert result["summary"]["critical"] > 0

    def test_custom_target_grade(self):
        text = "Simple text. Easy words. Short sentences."
        result = mod.run_accessibility_check(text, target_grade=2.0)
        assert result["target_grade"] == 2.0
