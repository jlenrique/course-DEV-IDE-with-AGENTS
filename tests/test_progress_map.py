"""Tests for progress_map.py CLI utility."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.utilities import progress_map as pm


def test_qualify_sprint_status_missing_file(tmp_path: Path) -> None:
    """Test qualify_sprint_status when file doesn't exist."""
    with patch.object(pm, "SPRINT_STATUS", tmp_path / "missing.yaml"):
        findings = pm._qualify_sprint_status()
        assert any(f["level"] == "error" and "not found" in f["message"] for f in findings)


def test_qualify_sprint_status_valid_file(tmp_path: Path) -> None:
    """Test qualify_sprint_status with valid sprint-status.yaml."""
    sprint_file = tmp_path / "sprint-status.yaml"
    sprint_file.write_text("""
generated: 2026-03-25
last_updated: 2026-04-14
development_status:
  epic-1: done
  1-1-test: done
""", encoding="utf-8")

    with patch.object(pm, "SPRINT_STATUS", sprint_file):
        findings = pm._qualify_sprint_status()
        assert any(f["level"] == "ok" and "File found" in f["message"] for f in findings)
        assert any(f["level"] == "ok" and "Valid YAML" in f["message"] for f in findings)


def test_qualify_markdown_missing_file(tmp_path: Path) -> None:
    """Test qualify_markdown when file doesn't exist."""
    missing_file = tmp_path / "missing.md"
    findings = pm._qualify_markdown(missing_file, ["Test Heading"])
    assert any(f["level"] == "warn" and "not found" in f["message"] for f in findings)


def test_qualify_markdown_valid_file(tmp_path: Path) -> None:
    """Test qualify_markdown with valid markdown."""
    md_file = tmp_path / "test.md"
    md_file.write_text("""
# Test Document

## Test Heading
This is content.
""", encoding="utf-8")

    findings = pm._qualify_markdown(md_file, ["Test Heading"])
    assert any(f["level"] == "ok" and "File found" in f["message"] for f in findings)
    assert any(f["level"] == "ok" and "expected heading" in f["message"] for f in findings)


def test_build_report_structure(tmp_path: Path) -> None:
    """Test build_report returns expected structure."""
    # Mock files
    sprint_file = tmp_path / "sprint-status.yaml"
    sprint_file.write_text("""
generated: 2026-03-25
last_updated: 2026-04-14
development_status:
  epic-1: done
  1-1-test: done
""", encoding="utf-8")

    handoff_file = tmp_path / "SESSION-HANDOFF.md"
    handoff_file.write_text("""
# Session Handoff

## What Is Next
Next steps here.

## Unresolved Issues
Issues here.
""", encoding="utf-8")

    next_file = tmp_path / "next-session-start-here.md"
    next_file.write_text("""
# Next Session

## Immediate Next Action
Action here.

## Key Risks / Unresolved Issues
Risks here.
""", encoding="utf-8")

    with patch.object(pm, "SPRINT_STATUS", sprint_file), \
         patch.object(pm, "SESSION_HANDOFF", handoff_file), \
         patch.object(pm, "NEXT_SESSION", next_file):
        report = pm.build_report()

        assert "generated" in report
        assert "sprint_status_updated" in report
        assert "source_health" in report
        assert "summary" in report
        assert "you_are_here" in report
        assert "completed_epics" in report
        assert "backlog_epics" in report
        assert "risks" in report


def test_render_text_includes_key_sections(tmp_path: Path) -> None:
    """Test render_text includes key sections."""
    # Mock minimal report
    report = {
        "generated": "2026-04-14T22:56:00Z",
        "sprint_status_updated": "2026-04-14",
        "source_health": {
            "verdict": "CLEAN",
            "error_count": 0,
            "warning_count": 0,
            "findings": []
        },
        "summary": {
            "total_epics": 1,
            "done_epics": 1,
            "active_epics": 0,
            "backlog_epics": 0,
            "total_stories": 1,
            "done_stories": 1,
            "active_stories": 0,
            "deferred_stories": 0,
            "backlog_stories": 0,
            "completion_pct": 100.0,
        },
        "you_are_here": {
            "active_epics": [],
            "what_is_next": "",
            "immediate_action": "",
        },
        "completed_epics": [{"id": "1", "label": "Test Epic", "stories": 1}],
        "backlog_epics": [],
        "risks": "",
    }

    text = pm.render_text(report)
    assert "PROGRESS MAP" in text
    assert "COMPLETED" in text
    assert "100.0%" in text


def test_main_json_output(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """Test main with --json flag."""
    # Mock files
    sprint_file = tmp_path / "sprint-status.yaml"
    sprint_file.write_text("""
generated: 2026-03-25
last_updated: 2026-04-14
development_status:
  epic-1: done
""", encoding="utf-8")

    with patch.object(pm, "SPRINT_STATUS", sprint_file), \
         patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
         patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"):
        pm.main(["--json"])

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "summary" in data
        assert "source_health" in data


def test_main_text_output(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """Test main with default text output."""
    # Mock files
    sprint_file = tmp_path / "sprint-status.yaml"
    sprint_file.write_text("""
generated: 2026-03-25
last_updated: 2026-04-14
development_status:
  epic-1: done
""", encoding="utf-8")

    with patch.object(pm, "SPRINT_STATUS", sprint_file), \
         patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
         patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"):
        pm.main([])

        captured = capsys.readouterr()
        assert "PROGRESS MAP" in captured.out
        assert "You Are Here" in captured.out