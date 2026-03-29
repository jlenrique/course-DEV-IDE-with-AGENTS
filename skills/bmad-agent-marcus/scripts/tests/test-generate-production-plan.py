# /// script
# requires-python = ">=3.10"
# ///
"""Tests for generate-production-plan.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "generate-production-plan.py"


def test_markdown_output() -> None:
    """Script produces markdown for a known content type."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "lecture-slides"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "# Production Plan: Lecture Slides" in result.stdout
    assert "gamma-specialist" in result.stdout
    assert "Style bible consulted" in result.stdout


def test_json_output() -> None:
    """Script produces valid JSON with --json flag."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "assessment", "--json"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["content_type"] == "assessment"
    assert data["label"] == "Assessment / Quiz"
    assert len(data["stages"]) > 0


def test_all_content_types() -> None:
    """All content types produce valid output."""
    content_types = [
        "lecture-slides", "case-study", "assessment", "discussion-prompt",
        "video-script", "animated-explainer", "bespoke-medical-illustration",
        "voiceover", "interactive-module", "coursearc-deployment",
    ]
    for ct in content_types:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), ct, "--json"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"Failed for {ct}: {result.stderr}"
        data = json.loads(result.stdout)
        assert data["content_type"] == ct
        assert len(data["stages"]) > 0, f"No stages for {ct}"


def test_module_and_lesson_args() -> None:
    """Module and lesson arguments are included in output."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "lecture-slides", "--module", "M2", "--lesson", "L3", "--json"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["module"] == "M2"
    assert data["lesson"] == "L3"


def test_markdown_includes_module() -> None:
    """Markdown output includes module when specified."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "case-study", "--module", "M1"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "**Module:** M1" in result.stdout


def test_human_checkpoint_present() -> None:
    """All content type workflows include at least one human checkpoint."""
    content_types = [
        "lecture-slides", "case-study", "assessment", "discussion-prompt",
        "video-script", "animated-explainer", "bespoke-medical-illustration",
        "voiceover", "interactive-module", "coursearc-deployment",
    ]
    for ct in content_types:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), ct],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "USER REVIEW" in result.stdout, f"No user checkpoint for {ct}"


def test_help_flag() -> None:
    """Script supports --help."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "content type" in result.stdout.lower()


if __name__ == "__main__":
    tests = [
        test_markdown_output, test_json_output, test_all_content_types,
        test_module_and_lesson_args, test_markdown_includes_module,
        test_human_checkpoint_present, test_help_flag,
    ]
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
        except AssertionError as e:
            print(f"  FAIL: {test.__name__}: {e}")
