"""Tests for cumulative fidelity drift checking."""

from pathlib import Path

import pytest

from scripts.fidelity_drift_check import (
    check_theme_representation,
    compute_global_drift,
    extract_source_themes,
)


@pytest.fixture
def source_bundle(tmp_path: Path) -> Path:
    content = """\
# Course Content

## Digital Transformation

The healthcare industry is undergoing digital transformation...

## Workforce Evolution

Workforce patterns are shifting toward...

## Regulatory Compliance

Healthcare regulation requires...

## Patient Safety Metrics

Patient safety is measured by...
"""
    doc = tmp_path / "extracted.md"
    doc.write_text(content, encoding="utf-8")
    return doc


class TestExtractSourceThemes:
    def test_extracts_four_themes(self, source_bundle: Path) -> None:
        themes = extract_source_themes(str(source_bundle))
        assert len(themes) == 4
        assert themes[0]["heading"] == "Digital Transformation"
        assert themes[3]["heading"] == "Patient Safety Metrics"

    def test_missing_file(self, tmp_path: Path) -> None:
        themes = extract_source_themes(str(tmp_path / "nonexistent.md"))
        assert themes == []


class TestCheckThemeRepresentation:
    def test_theme_present(self) -> None:
        assert check_theme_representation(
            "Digital Transformation",
            "The digital transformation of healthcare continues to accelerate."
        )

    def test_theme_absent(self) -> None:
        assert not check_theme_representation(
            "Regulatory Compliance",
            "The digital transformation of healthcare continues."
        )

    def test_partial_match(self) -> None:
        result = check_theme_representation(
            "Patient Safety Metrics",
            "Patient outcomes and safety protocols were discussed."
        )
        assert result  # "patient" and "safety" match (2/3 significant words)


class TestComputeGlobalDrift:
    def test_no_drift(self, source_bundle: Path) -> None:
        artifact = (
            "Digital transformation in healthcare. "
            "Workforce evolution patterns. "
            "Regulatory compliance requirements. "
            "Patient safety metrics dashboard."
        )
        result = compute_global_drift(str(source_bundle), artifact, "G3")
        assert result["verdict"] == "pass"
        assert result["drift"] == 0.0
        assert result["themes_represented"] == 4

    def test_one_missing_theme(self, source_bundle: Path) -> None:
        artifact = (
            "Digital transformation in healthcare. "
            "Workforce evolution patterns. "
            "Patient safety metrics dashboard."
        )
        result = compute_global_drift(str(source_bundle), artifact, "G3", "production")
        assert result["themes_represented"] == 3
        assert result["total_source_themes"] == 4
        assert result["drift"] == 0.25
        assert result["verdict"] == "failure"  # 25% > 20% production failure threshold

    def test_adhoc_more_tolerant(self, source_bundle: Path) -> None:
        artifact = (
            "Digital transformation in healthcare. "
            "Workforce evolution patterns. "
            "Patient safety metrics dashboard."
        )
        result = compute_global_drift(str(source_bundle), artifact, "G3", "ad-hoc")
        assert result["drift"] == 0.25
        assert result["verdict"] == "warning"  # 25% > 20% warning but < 40% failure

    def test_missing_file(self, tmp_path: Path) -> None:
        result = compute_global_drift(str(tmp_path / "nope.md"), "text", "G3")
        assert result["verdict"] == "pass"
        assert result["total_source_themes"] == 0


class TestIntegrationDriftWithResolver:
    """Integration test exercising compute_global_drift → resolve_source_ref chain."""

    def test_full_chain_with_source_ref_resolution(self, tmp_path: Path) -> None:
        """End-to-end: source bundle → drift check → resolver called on missing themes."""
        source = tmp_path / "extracted.md"
        source.write_text(
            "# Course\n\n"
            "## Pharmacology Basics\n\nDrug interactions and dosing.\n\n"
            "## Clinical Assessment\n\nPatient evaluation protocols.\n\n"
            "## Regulatory Framework\n\nCompliance requirements.\n",
            encoding="utf-8",
        )

        artifact_covering_all = (
            "This slide covers pharmacology basics including drug interactions. "
            "Clinical assessment protocols are reviewed. "
            "The regulatory framework and compliance requirements are addressed."
        )
        result_pass = compute_global_drift(str(source), artifact_covering_all, "G3", "production")
        assert result_pass["verdict"] == "pass"
        assert result_pass["drift"] == 0.0
        assert result_pass["themes_represented"] == 3

        artifact_missing_one = (
            "This slide covers pharmacology basics. "
            "Clinical assessment is reviewed."
        )
        result_warn = compute_global_drift(str(source), artifact_missing_one, "G3", "production")
        assert result_warn["themes_represented"] == 2
        assert result_warn["total_source_themes"] == 3
        assert len(result_warn["missing_themes"]) == 1
        assert result_warn["missing_themes"][0]["theme"] == "Regulatory Framework"
        assert "extracted.md#Regulatory Framework" in result_warn["missing_themes"][0]["source_ref"]

        from scripts.resolve_source_ref import resolve_source_ref
        ref = result_warn["missing_themes"][0]["source_ref"]
        content, confidence = resolve_source_ref(ref, str(tmp_path))
        assert confidence == "exact"
        assert "Compliance requirements" in content
