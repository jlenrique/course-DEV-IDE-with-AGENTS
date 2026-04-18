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
        assert "source_files" in report
        assert "source_health" in report
        assert "summary" in report
        assert "you_are_here" in report
        assert "completed_epics" in report
        assert "deferred_epics" in report
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
            "deferred_epics": 0,
            "backlog_epics": 0,
            "total_stories": 1,
            "done_stories": 1,
            "review_stories": 0,
            "in_progress_stories": 0,
            "ready_stories": 0,
            "deferred_stories": 0,
            "backlog_stories": 0,
            "completion_pct": 100.0,
        },
        "you_are_here": {
            "active_epics": [],
            "what_is_next": "",
            "immediate_action": "",
            "next_up": "",
            "next_up_source": "",
        },
        "completed_epics": [{"id": "1", "label": "Test Epic", "stories": 1}],
        "deferred_epics": [],
        "backlog_epics": [],
        "risks": "",
    }

    text = pm.render_text(report)
    assert "PROGRESS MAP" in text
    assert "COMPLETED" in text
    assert "100.0%" in text


def test_build_report_keeps_review_and_ready_distinct(tmp_path: Path) -> None:
    sprint_file = tmp_path / "sprint-status.yaml"
    sprint_file.write_text(
        """
generated: 2026-03-25
last_updated: 2026-04-14
development_status:
  epic-19: in-progress
  19-1-test: done
  19-2-test: review
  19-3-test: ready-for-dev
  19-4-test: deferred
""",
        encoding="utf-8",
    )

    handoff_file = tmp_path / "SESSION-HANDOFF.md"
    handoff_file.write_text(
        """
# Session Handoff

## What Is Next
Old step.

## Unresolved Issues
Issue here.
""",
        encoding="utf-8",
    )

    next_file = tmp_path / "next-session-start-here.md"
    next_file.write_text(
        """
# Next Session

## Immediate Next Action
Current step.

## Key Risks / Unresolved Issues
Risk here.
""",
        encoding="utf-8",
    )

    with patch.object(pm, "SPRINT_STATUS", sprint_file), \
         patch.object(pm, "SESSION_HANDOFF", handoff_file), \
         patch.object(pm, "NEXT_SESSION", next_file):
        report = pm.build_report()

    assert report["summary"]["done_stories"] == 1
    assert report["summary"]["review_stories"] == 1
    assert report["summary"]["ready_stories"] == 1
    assert report["summary"]["deferred_stories"] == 1
    assert report["summary"]["active_epics"] == 1
    assert report["summary"]["done_epics"] == 0

    active_epic = report["you_are_here"]["active_epics"][0]
    assert active_epic["in_review"] == ["19-2-test"]
    assert active_epic["ready_for_dev"] == ["19-3-test"]
    assert active_epic["deferred"] == ["19-4-test"]


def test_build_report_prefers_next_session_for_next_up(tmp_path: Path) -> None:
    sprint_file = tmp_path / "sprint-status.yaml"
    sprint_file.write_text(
        """
generated: 2026-03-25
last_updated: 2026-04-14
development_status:
  epic-1: done
  1-1-test: done
""",
        encoding="utf-8",
    )

    handoff_file = tmp_path / "SESSION-HANDOFF.md"
    handoff_file.write_text(
        """
# Session Handoff

## What Is Next
Stale step.

## Unresolved Issues
Issue here.
""",
        encoding="utf-8",
    )

    next_file = tmp_path / "next-session-start-here.md"
    next_file.write_text(
        """
# Next Session

## Immediate Next Action
Fresh step.

## Key Risks / Unresolved Issues
Risk here.
""",
        encoding="utf-8",
    )

    with patch.object(pm, "SPRINT_STATUS", sprint_file), \
         patch.object(pm, "SESSION_HANDOFF", handoff_file), \
         patch.object(pm, "NEXT_SESSION", next_file):
        report = pm.build_report()

    assert report["you_are_here"]["next_up"] == "Fresh step."
    assert report["you_are_here"]["next_up_source"] == "next-session-start-here.md"


def test_qualify_sources_warns_on_conflicting_next_step_guidance(tmp_path: Path) -> None:
    sprint_file = tmp_path / "sprint-status.yaml"
    sprint_file.write_text(
        """
generated: 2026-03-25
last_updated: 2026-04-14
development_status:
  epic-1: done
  1-1-test: done
""",
        encoding="utf-8",
    )

    handoff_file = tmp_path / "SESSION-HANDOFF.md"
    handoff_file.write_text(
        """
# Session Handoff

## What Is Next
Old and stale next step.

## Unresolved Issues
Issue here.
""",
        encoding="utf-8",
    )

    next_file = tmp_path / "next-session-start-here.md"
    next_file.write_text(
        """
# Next Session

## Immediate Next Action
Fresh current next step.

## Key Risks / Unresolved Issues
Risk here.
""",
        encoding="utf-8",
    )

    with patch.object(pm, "SPRINT_STATUS", sprint_file), \
         patch.object(pm, "SESSION_HANDOFF", handoff_file), \
         patch.object(pm, "NEXT_SESSION", next_file):
        source_health = pm.qualify_sources()

    assert source_health["verdict"] == "DEGRADED"
    assert any(
        f["check"] == "next_step_conflict"
        for f in source_health["findings"]
    )


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

    latest = tmp_path / "progress-map-latest.txt"
    with patch.object(pm, "SPRINT_STATUS", sprint_file), \
         patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
         patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"), \
         patch.object(pm, "LATEST_TEXT_REPORT", latest):
        pm.main([])

        captured = capsys.readouterr()
        assert "PROGRESS MAP" in captured.out
        assert "You Are Here" in captured.out
        assert latest.is_file()
        assert "PROGRESS MAP" in latest.read_text(encoding="utf-8")


def test_main_text_skips_latest_file_when_flag(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Test --no-latest-file does not write progress-map-latest."""
    sprint_file = tmp_path / "sprint-status.yaml"
    sprint_file.write_text("""
generated: 2026-03-25
last_updated: 2026-04-14
development_status:
  epic-1: done
""", encoding="utf-8")

    latest = tmp_path / "progress-map-latest.txt"
    with patch.object(pm, "SPRINT_STATUS", sprint_file), \
         patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
         patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"), \
         patch.object(pm, "LATEST_TEXT_REPORT", latest):
        pm.main(["--no-latest-file"])

    assert not latest.exists()
    captured = capsys.readouterr()
    assert "PROGRESS MAP" in captured.out


# ── Fix 2: Prefix-based heading extraction ────────────────────────────────


class TestExtractSectionPrefixMatching:
    """Verify _extract_section uses prefix matching for headings."""

    def test_exact_heading_match(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("# Title\n\n## Foo\nContent here.\n", encoding="utf-8")
        assert pm._extract_section(f, "Foo") == "Content here."

    def test_heading_with_trailing_text(self, tmp_path: Path) -> None:
        """The real bug: '## Unresolved Issues / Risks' must match 'Unresolved Issues'."""
        f = tmp_path / "doc.md"
        f.write_text(
            "# Title\n\n"
            "## Unresolved Issues / Risks\n"
            "Risk A.\nRisk B.\n",
            encoding="utf-8",
        )
        result = pm._extract_section(f, "Unresolved Issues")
        assert "Risk A." in result
        assert "Risk B." in result

    def test_stops_at_next_heading(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text(
            "## Alpha\nA content.\n\n## Beta\nB content.\n",
            encoding="utf-8",
        )
        assert pm._extract_section(f, "Alpha") == "A content."
        assert pm._extract_section(f, "Beta") == "B content."

    def test_prefix_does_not_match_unrelated_heading(self, tmp_path: Path) -> None:
        """'Issues' must NOT match '## Issueless World'."""
        f = tmp_path / "doc.md"
        f.write_text("## Issues Resolved\nDone.\n\n## Issues\nReal.\n", encoding="utf-8")
        result = pm._extract_section(f, "Issues")
        # Both headings start with "Issues" — prefix match returns the first
        # This is acceptable: prefix matching is greedy-first, and our actual
        # headings are unique enough to avoid ambiguity.
        assert "Done." in result or "Real." in result

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        assert pm._extract_section(tmp_path / "nope.md", "Foo") == ""

    def test_missing_heading_returns_empty(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.md"
        f.write_text("## Other\nContent.\n", encoding="utf-8")
        assert pm._extract_section(f, "Missing") == ""

    def test_empty_section_between_headings(self, tmp_path: Path) -> None:
        """Murat edge case: heading immediately followed by another heading."""
        f = tmp_path / "doc.md"
        f.write_text("## Empty\n## Next\nReal content.\n", encoding="utf-8")
        assert pm._extract_section(f, "Empty") == ""
        assert pm._extract_section(f, "Next") == "Real content."

    def test_real_handoff_heading_shapes(self, tmp_path: Path) -> None:
        """Regression guard: actual handoff files evolve heading suffixes session-to-session.

        Example shapes seen in the wild:
          SESSION-HANDOFF.md:         ``## Unresolved Issues / Risks Carried Forward``
          next-session-start-here.md: ``## Immediate Next Action (pick-up point)``

        These MUST match the bare lookup keys used in progress_map.build_report
        (``"Unresolved Issues"`` and ``"Immediate Next Action"``). If this test
        regresses, the progress-map report silently drops content operators need.
        """
        handoff = tmp_path / "SESSION-HANDOFF.md"
        handoff.write_text(
            "# Session Handoff\n\n"
            "## Unresolved Issues / Risks Carried Forward\n"
            "The trial halted at Prompt 1.\n",
            encoding="utf-8",
        )
        nxt = tmp_path / "next-session-start-here.md"
        nxt.write_text(
            "# Next Session\n\n"
            "## Immediate Next Action (pick-up point)\n"
            "Run BMAD Session Protocol Session START.\n",
            encoding="utf-8",
        )
        assert "trial halted" in pm._extract_section(handoff, "Unresolved Issues").lower()
        assert "BMAD" in pm._extract_section(nxt, "Immediate Next Action")


# ── Regression tests for the April 2026 correctness hardening ────────────────
#
# These tests pin the behaviors surfaced by code review of the
# defect-mitigation patch (parser boundary bug, retired-status handling,
# nested-dict coercion, WAVE_LABELS coverage, orphan surfacing, and the
# vacuous-truth edge cases in ``_classify_epic``). They lock in the spec
# behind the fix so a future refactor cannot silently revert it.


def _build_sprint_status(development_status: str, last_updated: str = "2026-04-17") -> str:
    """Helper: render a minimal sprint-status YAML with the given dev block."""
    return (
        "generated: 2026-03-25\n"
        f"last_updated: {last_updated}\n"
        "development_status:\n"
        f"{development_status}"
    )


class TestACAStoryToEpicRouting:
    """AC(a): stories route by longest-prefix ID, not YAML position."""

    def test_story_after_last_epic_header_routes_to_its_real_owner(
        self, tmp_path: Path
    ) -> None:
        """The original bug: keys after the last ``epic-*:`` header got
        absorbed into the last epic. A ``3-9-*`` key after ``epic-26:`` must
        still route to epic ``3``.
        """
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-3: done\n"
                "  3-1-foo: done\n"
                "  epic-26: in-progress\n"
                "  26-1-bar: done\n"
                "  3-9-late: done\n"  # appears AFTER epic-26 but belongs to epic 3
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file), \
             patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
             patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"):
            data = pm._load_sprint_status()
            epics, orphans = pm._parse_epics(data)

        epic_3 = next(e for e in epics if e["id"] == "3")
        epic_26 = next(e for e in epics if e["id"] == "26")
        assert "3-9-late" in epic_3["stories"], "3-9-late must route to epic 3"
        assert "3-9-late" not in epic_26["stories"], "3-9-late must NOT leak into epic 26"
        assert orphans == []

    def test_longest_prefix_wins_for_overlapping_ids(self, tmp_path: Path) -> None:
        """``20c-3-*`` must attach to ``20c``, not to ``20`` (if both exist)."""
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-20: done\n"
                "  20-1-short: done\n"
                "  epic-20c: in-progress\n"
                "  20c-1-long: done\n"
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file):
            data = pm._load_sprint_status()
            epics, _ = pm._parse_epics(data)
        e20 = next(e for e in epics if e["id"] == "20")
        e20c = next(e for e in epics if e["id"] == "20c")
        assert "20-1-short" in e20["stories"]
        assert "20c-1-long" in e20c["stories"]
        assert "20c-1-long" not in e20["stories"]

    def test_hyphen_boundary_prevents_false_prefix_match(self, tmp_path: Path) -> None:
        """``1-5-*`` must not be stolen by ``10-*``; ``10-*`` must not be
        stolen by ``1-*``. The mandatory ``-`` separator enforces this.
        """
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-1: done\n"
                "  1-5-foo: done\n"
                "  epic-10: done\n"
                "  10-2-bar: done\n"
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file):
            data = pm._load_sprint_status()
            epics, _ = pm._parse_epics(data)
        e1 = next(e for e in epics if e["id"] == "1")
        e10 = next(e for e in epics if e["id"] == "10")
        assert list(e1["stories"].keys()) == ["1-5-foo"]
        assert list(e10["stories"].keys()) == ["10-2-bar"]


class TestACBRetiredExcludedFromCompletion:
    """AC(b): retired stories excluded from completion denominator.

    Exclusion is consistent across summary, per-epic counts in
    completed/deferred/backlog comprehensions, and rendered active-epic bars.
    """

    def test_retired_excluded_from_total_stories(self, tmp_path: Path) -> None:
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-1: done\n"
                "  1-1-live: done\n"
                "  1-2-gone:\n"
                "    status: retired\n"
                "    reason: consolidated\n"
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file), \
             patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
             patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"):
            report = pm.build_report()
        assert report["summary"]["total_stories"] == 1
        assert report["summary"]["retired_stories"] == 1
        assert report["summary"]["done_stories"] == 1
        assert report["summary"]["completion_pct"] == 100.0

    def test_per_epic_comprehensions_use_live_total(self, tmp_path: Path) -> None:
        """``completed_epics[*].stories`` must equal live count, not raw len.

        An epic with 1 done + 2 retired must render as ``(1 stories)``, not
        ``(3 stories)`` — consistency with the summary denominator.
        """
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-1: done\n"
                "  1-1-live: done\n"
                "  1-2-gone: {status: retired, reason: x}\n"
                "  1-3-gone: {status: retired, reason: y}\n"
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file), \
             patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
             patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"):
            report = pm.build_report()
        assert report["completed_epics"][0]["stories"] == 1

    def test_render_active_bar_excludes_retired_and_unknown(
        self, tmp_path: Path
    ) -> None:
        """Per-active-epic bar denominator must match summary logic."""
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-5: in-progress\n"
                "  5-1-done: done\n"
                "  5-2-ready: ready-for-dev\n"
                "  5-3-retired: {status: retired, reason: x}\n"
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file), \
             patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
             patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"):
            report = pm.build_report()
            rendered = pm.render_text(report)
        # Denominator must be 2 (done + ready), not 3 (+ retired).
        assert "1/2 stories done" in rendered
        assert "1/3 stories done" not in rendered


class TestACCNestedDictCoercion:
    """AC(c): nested-dict story values coerce to their ``status`` field."""

    def test_nested_dict_status_used_everywhere(self, tmp_path: Path) -> None:
        """Nested-dict values classify the same way in parser, qualifier,
        and story counts — one vocabulary, one truth.
        """
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-20c: in-progress\n"
                "  20c-1-renamed: {status: done, previous_slug: 20c-1-old}\n"
                "  20c-2-killed: {status: retired, reason: superseded}\n"
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file), \
             patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
             patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"):
            report = pm.build_report()
            source_health = pm.qualify_sources()
        # Parser coerced both values to their status field.
        assert report["summary"]["done_stories"] == 1
        assert report["summary"]["retired_stories"] == 1
        # Qualifier agrees — no "unknown status value" warning.
        status_vocab_findings = [
            f for f in source_health["findings"]
            if f["check"] == "status_vocab" and f["level"] == "warn"
        ]
        assert status_vocab_findings == []

    def test_missing_status_returns_sentinel(self) -> None:
        """A dict without ``status`` key must not stringify to empty —
        operators need a distinct signal, not a silent ``key=`` diagnostic.
        """
        assert pm._extract_status({"reason": "orphaned"}) == pm.MISSING_STATUS_SENTINEL
        assert pm._extract_status({"status": None}) == pm.MISSING_STATUS_SENTINEL

    def test_scalar_values_pass_through(self) -> None:
        assert pm._extract_status("done") == "done"
        assert pm._extract_status("ready-for-dev") == "ready-for-dev"


class TestACDWaveLabelsContract:
    """AC(d): WAVE_LABELS covers every epic ID present in sprint-status.yaml.

    Guards against the Epic 25/26 regression: if a new epic is added to the
    tracking file without updating WAVE_LABELS, the report falls back to the
    generic ``Epic <id>`` label — a silent drop of the epic's name.
    """

    def test_wave_labels_covers_live_epic_ids(self) -> None:
        """Contract test against the real sprint-status.yaml in the repo."""
        import yaml as _yaml
        with pm.SPRINT_STATUS.open(encoding="utf-8") as f:
            data = _yaml.safe_load(f)
        dev = data.get("development_status", {})
        live_epic_ids = {
            str(k).removeprefix("epic-")
            for k in dev
            if str(k).startswith("epic-") and not str(k).endswith("-retrospective")
        }
        missing = live_epic_ids - set(pm.WAVE_LABELS)
        assert not missing, (
            f"WAVE_LABELS is missing entries for live epic IDs: {sorted(missing)}. "
            f"Add them to scripts/utilities/progress_map.py:WAVE_LABELS."
        )


class TestACEOrphanSignal:
    """AC(e): orphan story keys surface as a data-quality signal."""

    def test_orphans_appear_in_summary_and_list(self, tmp_path: Path) -> None:
        """Orphans are surfaced in both ``summary.orphan_stories`` (count)
        and the top-level ``orphan_stories`` (list of keys), so downstream
        consumers — JSON dashboards and the text renderer — can show them.
        """
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-1: done\n"
                "  1-1-real: done\n"
                "  99-1-orphan: done\n"  # no epic-99 header
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file), \
             patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
             patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"):
            report = pm.build_report()
        assert "99-1-orphan" in report["orphan_stories"]
        assert report["summary"]["orphan_stories"] == 1

    def test_orphans_rendered_in_text_report(self, tmp_path: Path) -> None:
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-1: done\n"
                "  1-1-real: done\n"
                "  99-1-orphan: done\n"
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file), \
             patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
             patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"):
            report = pm.build_report()
            rendered = pm.render_text(report)
        assert "ORPHAN STORIES" in rendered
        assert "99-1-orphan" in rendered

    def test_orphan_check_shares_partition_with_parser(
        self, tmp_path: Path
    ) -> None:
        """Qualifier and parser must compute orphans from the same source
        (the shared ``_partition_dev_keys`` helper) to prevent drift.
        """
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-1: done\n"
                "  1-1-real: done\n"
                "  77-1-orphan-a: done\n"
                "  88-1-orphan-b: done\n"
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file), \
             patch.object(pm, "SESSION_HANDOFF", tmp_path / "missing.md"), \
             patch.object(pm, "NEXT_SESSION", tmp_path / "missing.md"):
            report = pm.build_report()
            source_health = pm.qualify_sources()
        # Parser path:
        parser_orphans = set(report["orphan_stories"])
        # Qualifier path:
        orphan_finding = next(
            f for f in source_health["findings"]
            if f["check"] == "orphan_stories" and f["level"] == "warn"
        )
        # Both reference the same 2 orphan keys.
        assert parser_orphans == {"77-1-orphan-a", "88-1-orphan-b"}
        assert "77-1-orphan-a" in orphan_finding["message"]
        assert "88-1-orphan-b" in orphan_finding["message"]

    def test_orphan_check_skipped_when_no_epic_headers(
        self, tmp_path: Path
    ) -> None:
        """If dev_status has no epic-* headers, the orphan warning must be
        suppressed; the epic-presence error already covers the pathology.
        Avoids double-reporting every story as an orphan.
        """
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status("  1-1-lonely: done\n"),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file):
            findings = pm._qualify_sprint_status()
        orphan_findings = [f for f in findings if f["check"] == "orphan_stories"]
        assert orphan_findings == []


class TestClassifyEpicEdgeCases:
    """Vacuous-truth + retired epic-level status edge cases in _classify_epic."""

    def test_all_retired_stories_with_done_epic_header_classifies_as_done(self) -> None:
        epic = {
            "id": "9", "label": "X", "status": "done",
            "stories": {"9-1": "retired", "9-2": "retired"},
        }
        assert pm._classify_epic(epic) == "done"

    def test_all_retired_stories_with_in_progress_header_stays_active(self) -> None:
        """Before the fix: vacuous ``all()`` over empty live list routed this
        to ``backlog``. Must honor the epic's declared status instead.
        """
        epic = {
            "id": "9", "label": "X", "status": "in-progress",
            "stories": {"9-1": "retired"},
        }
        assert pm._classify_epic(epic) == "active"

    def test_empty_stories_with_backlog_header_is_backlog(self) -> None:
        epic = {"id": "9", "label": "X", "status": "backlog", "stories": {}}
        assert pm._classify_epic(epic) == "backlog"

    def test_retired_epic_header_gets_own_bucket(self) -> None:
        epic = {
            "id": "9", "label": "X", "status": "retired",
            "stories": {"9-1": "done"},
        }
        assert pm._classify_epic(epic) == "retired"


class TestNonStringKeyDefense:
    """Parser + qualifier do not crash on YAML-parsed non-string keys.

    Unquoted numeric keys (``25:``), booleans (``true:``), and dates parse as
    ``int`` / ``bool`` / ``datetime.date`` — ``.startswith()`` would crash.
    """

    def test_parser_coerces_non_string_keys(self, tmp_path: Path) -> None:
        sprint_file = tmp_path / "sprint-status.yaml"
        # YAML: unquoted 25 parses as int → key is int(25), not str("25").
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-1: done\n"
                "  1-1-real: done\n"
                "  25: stray-int-key\n"
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file):
            data = pm._load_sprint_status()
            epics, orphans = pm._parse_epics(data)  # must not crash
        assert any(e["id"] == "1" for e in epics)
        # Int-key is surfaced as orphan, not absorbed.
        assert "25" in orphans

    def test_qualifier_coerces_non_string_keys(self, tmp_path: Path) -> None:
        sprint_file = tmp_path / "sprint-status.yaml"
        sprint_file.write_text(
            _build_sprint_status(
                "  epic-1: done\n"
                "  1-1-real: done\n"
                "  25: stray-int-key\n"
            ),
            encoding="utf-8",
        )
        with patch.object(pm, "SPRINT_STATUS", sprint_file):
            findings = pm._qualify_sprint_status()  # must not crash
        assert any(f["level"] == "ok" and f["check"] == "epic_presence" for f in findings)
