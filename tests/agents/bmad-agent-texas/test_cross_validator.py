"""Tests for Texas agent cross_validator.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# Load module from skill path
_MOD_PATH = Path(__file__).resolve().parents[3] / "skills" / "bmad-agent-texas" / "scripts" / "cross_validator.py"
_spec = importlib.util.spec_from_file_location("cross_validator", _MOD_PATH)
cv = importlib.util.module_from_spec(_spec)
sys.modules["cross_validator"] = cv
_spec.loader.exec_module(cv)

cross_validate = cv.cross_validate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

REFERENCE_MD = """
# Course 1, Module 1: Foundations of the Innovation Mindset

## Part 1: The Call - Setting the Stage

By the end of this module, the learner will be able to:
1. **Define** the "innovation mindset"
2. **Analyze** the macro-economic and structural trends

### Slide 1: Welcome & The Modern Clinician's Dilemma

- **Visual Format:** Welcome Video
- **Narration:** "Welcome. I am Dr. Tejal Naik."

### Slide 2: The Innovator's Hero's Journey

**Narration:** "This certificate is designed to unlock a skill set."

### Slide 3: The Lineage of Physician Innovators

Dr. Thomas Fogarty, Dr. Peter Pronovost, Dr. Patricia Bath

### Slide 4: Expectations & Mental Frameworks

Growth mindset, Psychological safety, First principles

### Part 1 Summary Slide

- The Gap: Traditional training creates clinical experts
- The Mission: Move from employee to innovation leader
"""

META = {
    "ref_id": "src-002",
    "description": "Part 1 MD reference",
    "coverage_scope": "part_1_only",
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSectionMatching:
    """Verify heading/section matching between extraction and reference."""

    def test_full_match_when_content_contains_all_sections(self) -> None:
        extraction = REFERENCE_MD  # same content
        result = cross_validate(extraction, REFERENCE_MD, META)
        assert result.sections_matched > 0
        assert result.sections_matched == result.sections_in_reference

    def test_no_match_from_unrelated_content(self) -> None:
        extraction = "This is completely unrelated content about cooking recipes."
        result = cross_validate(extraction, REFERENCE_MD, META)
        assert result.sections_matched == 0
        assert len(result.missing_sections) == result.sections_in_reference

    def test_partial_match(self) -> None:
        extraction = (
            "# Introduction\n\n"
            "Welcome. I am Dr. Tejal Naik. Innovation mindset.\n"
            "The Innovator's Hero's Journey is about unlocking skills.\n"
            "Growth mindset and psychological safety are key.\n"
        )
        result = cross_validate(extraction, REFERENCE_MD, META)
        assert 0 < result.sections_matched < result.sections_in_reference


class TestKeyTermCoverage:
    """Verify key term extraction and coverage measurement."""

    def test_high_coverage_from_matching_content(self) -> None:
        result = cross_validate(REFERENCE_MD, REFERENCE_MD, META)
        assert result.key_terms_coverage >= 0.80  # some terms span lines in extraction

    def test_low_coverage_from_stub(self) -> None:
        result = cross_validate("Course 1 Module 1", REFERENCE_MD, META)
        assert result.key_terms_coverage < 0.20

    def test_moderate_coverage_from_partial_content(self) -> None:
        extraction = (
            "Dr. Tejal Naik discusses innovation mindset and Design Thinking. "
            "Growth mindset by Carol Dweck. Psychological safety by Amy Edmondson. "
            "Dr. Thomas Fogarty and Dr. Peter Pronovost are physician innovators. "
            "The Hero's Journey framework structures the certificate."
        )
        result = cross_validate(extraction, REFERENCE_MD, META)
        assert 0.2 < result.key_terms_coverage < 0.9


class TestPassFailDecision:
    """Verify the pass/fail threshold."""

    def test_passes_with_good_coverage(self) -> None:
        result = cross_validate(REFERENCE_MD, REFERENCE_MD, META)
        assert result.passed is True

    def test_fails_with_stub(self) -> None:
        result = cross_validate("stub content", REFERENCE_MD, META)
        assert result.passed is False


class TestVerdict:
    """Verify human-readable verdict generation."""

    def test_strong_match_verdict(self) -> None:
        result = cross_validate(REFERENCE_MD, REFERENCE_MD, META)
        assert "strong" in result.verdict.lower() or result.key_terms_coverage >= 0.80

    def test_poor_match_verdict(self) -> None:
        result = cross_validate("nothing relevant", REFERENCE_MD, META)
        assert "poor" in result.verdict.lower() or "missing" in result.verdict.lower()


class TestWordCountRatio:
    """Verify word count ratio calculation."""

    def test_ratio_close_to_one_for_same_content(self) -> None:
        result = cross_validate(REFERENCE_MD, REFERENCE_MD, META)
        assert 0.9 < result.word_count_ratio < 1.1

    def test_ratio_high_for_longer_extraction(self) -> None:
        extraction = REFERENCE_MD + "\n\nExtra content " * 500
        result = cross_validate(extraction, REFERENCE_MD, META)
        assert result.word_count_ratio > 2.0


class TestEscapedMarkdown:
    """Verify handling of escaped markdown in reference files."""

    def test_escaped_headings_extracted(self) -> None:
        escaped_ref = (
            "\\# **Course Title**\n\n"
            "\\## **Part 1**\n\n"
            "\\### **Slide 1: Welcome**\n\n"
            "Content about innovation mindset.\n"
        )
        extraction = (
            "# Course Title\n\n"
            "## Part 1\n\n"
            "### Slide 1: Welcome\n\n"
            "Content about innovation mindset.\n"
        )
        meta = {"ref_id": "test", "description": "escaped ref", "coverage_scope": "full"}
        result = cross_validate(extraction, escaped_ref, meta)
        assert result.sections_in_reference >= 2
        assert result.sections_matched >= 1


class TestSerialization:
    """Verify to_dict output structure."""

    def test_to_dict_structure(self) -> None:
        result = cross_validate(REFERENCE_MD, REFERENCE_MD, META)
        d = result.to_dict()
        assert "asset_ref_id" in d
        assert "sections_matched" in d
        assert "key_terms_coverage" in d
        assert "verdict" in d
        assert "passed" in d
        assert "missing_sections" in d


class TestRealC1M1Data:
    """Integration test against actual C1M1 course content."""

    @pytest.fixture
    def c1m1_md(self) -> str:
        path = Path(__file__).resolve().parents[3] / "course-content" / "courses" / "tejal-APC-C1" / "C1M1Part01.md"
        if not path.exists() or path.stat().st_size < 100:
            pytest.skip("C1M1Part01.md not available or too small")
        return path.read_text(encoding="utf-8")

    def test_real_md_self_validates(self, c1m1_md: str) -> None:
        """The MD file cross-validated against itself should pass."""
        meta = {"ref_id": "src-002", "description": "C1M1 Part 1", "coverage_scope": "part_1_only"}
        result = cross_validate(c1m1_md, c1m1_md, meta)
        assert result.passed is True
        assert result.key_terms_coverage >= 0.90
