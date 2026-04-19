"""Tests for run_hud.py — Heads-Up Display generator."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from scripts.utilities import run_hud as hud

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def bundle(tmp_path: Path) -> Path:
    """Create a minimal bundle directory with run-constants and gates."""
    b = tmp_path / "bundles" / "test-bundle-20260416"
    b.mkdir(parents=True)

    rc = {
        "RUN_ID": "TEST-RUN-001",
        "EXPERIENCE_PROFILE": "visual-led",
        "PRIMARY_SOURCE_FILE": "test-source.pdf",
        "LESSON_SLUG": "test-lesson",
    }
    (b / "run-constants.yaml").write_text(
        yaml.dump(rc, default_flow_style=False), encoding="utf-8"
    )

    (b / "extracted.md").write_text("# Test extraction\nContent here.", encoding="utf-8")

    gates = b / "gates"
    gates.mkdir()

    gate_01 = {
        "schema_version": "1.0",
        "step_id": "01",
        "step_name": "Activation + Preflight",
        "run_id": "TEST-RUN-001",
        "timestamp": "2026-04-16T14:00:00Z",
        "result": "pass",
        "operator": "Marcus",
        "duration_seconds": 12,
        "summary": "Preflight OK",
        "metrics": {"mcp_gamma": "connected"},
    }
    (gates / "gate-01-result.yaml").write_text(
        yaml.dump(gate_01, default_flow_style=False), encoding="utf-8"
    )

    gate_04 = {
        "schema_version": "1.0",
        "step_id": "04",
        "step_name": "Ingestion Quality Gate",
        "run_id": "TEST-RUN-001",
        "timestamp": "2026-04-16T14:10:00Z",
        "result": "fail",
        "operator": "Marcus",
        "duration_seconds": 30,
        "summary": "Extraction too thin",
        "blockers": ["word count 120 < floor 3000"],
        "metrics": {"word_count": 120, "word_floor": 3000},
        "evidence": "Stub extraction detected.",
    }
    (gates / "gate-04-result.yaml").write_text(
        yaml.dump(gate_04, default_flow_style=False), encoding="utf-8"
    )

    return b


@pytest.fixture
def empty_bundle(tmp_path: Path) -> Path:
    """Create a bundle with no gates and no run-constants."""
    b = tmp_path / "bundles" / "empty-bundle"
    b.mkdir(parents=True)
    return b


# ---------------------------------------------------------------------------
# Data collection tests
# ---------------------------------------------------------------------------


class TestLoadRunConstants:
    def test_loads_valid_constants(self, bundle: Path) -> None:
        rc = hud._load_run_constants(bundle)
        assert rc["RUN_ID"] == "TEST-RUN-001"
        assert rc["EXPERIENCE_PROFILE"] == "visual-led"

    def test_missing_file_returns_empty(self, empty_bundle: Path) -> None:
        rc = hud._load_run_constants(empty_bundle)
        assert rc == {}

    def test_nonexistent_dir_returns_empty(self, tmp_path: Path) -> None:
        rc = hud._load_run_constants(tmp_path / "nope")
        assert rc == {}


class TestLoadGateResults:
    def test_loads_gate_files(self, bundle: Path) -> None:
        gates = hud._load_gate_results(bundle)
        assert len(gates) == 2
        assert gates[0]["step_id"] == "01"
        assert gates[1]["step_id"] == "04"

    def test_empty_bundle_returns_empty(self, empty_bundle: Path) -> None:
        gates = hud._load_gate_results(empty_bundle)
        assert gates == []

    def test_invalid_yaml_skipped(self, bundle: Path) -> None:
        (bundle / "gates" / "gate-99-result.yaml").write_text(
            "{{bad yaml", encoding="utf-8"
        )
        gates = hud._load_gate_results(bundle)
        assert len(gates) == 2  # only the 2 valid ones


class TestScanBundleArtifacts:
    def test_lists_files_with_sizes(self, bundle: Path) -> None:
        artifacts = hud._scan_bundle_artifacts(bundle)
        paths = [a["path"] for a in artifacts]
        assert any("run-constants.yaml" in p for p in paths)
        assert any("extracted.md" in p for p in paths)

    def test_missing_dir_returns_empty(self, tmp_path: Path) -> None:
        artifacts = hud._scan_bundle_artifacts(tmp_path / "nope")
        assert artifacts == []


class TestFindLatestBundle:
    def test_finds_newest_by_mtime(self, tmp_path: Path) -> None:
        bundles = tmp_path / "bundles"
        bundles.mkdir()
        old = bundles / "old-bundle"
        old.mkdir()
        new = bundles / "new-bundle"
        new.mkdir()
        # Touch new to ensure it's newer
        (new / "marker.txt").write_text("x", encoding="utf-8")
        result = hud._find_latest_bundle(bundles)
        assert result == new

    def test_missing_dir_returns_none(self, tmp_path: Path) -> None:
        assert hud._find_latest_bundle(tmp_path / "nope") is None

    def test_empty_dir_returns_none(self, tmp_path: Path) -> None:
        d = tmp_path / "empty"
        d.mkdir()
        assert hud._find_latest_bundle(d) is None


class TestBuildPipelineState:
    def test_merges_gate_results(self) -> None:
        gates = [
            {"step_id": "01", "result": "pass", "summary": "OK"},
            {"step_id": "07B", "result": "conditional-pass",
             "summary": "Variant A slightly preferred",
             "conditions": ["Variant B scored within 5% of A"]},
            {"step_id": "04", "result": "fail", "summary": "Bad"},
        ]
        pipeline = hud._build_pipeline_state(gates)
        step_01 = next(s for s in pipeline if s["id"] == "01")
        step_04 = next(s for s in pipeline if s["id"] == "04")
        step_05 = next(s for s in pipeline if s["id"] == "05")
        step_07b = next(s for s in pipeline if s["id"] == "07B")
        assert step_01["result"] == "pass"
        assert step_04["result"] == "fail"
        assert step_05["result"] == "not-started"
        assert step_07b["result"] == "conditional-pass"
        assert step_07b["conditions"] == ["Variant B scored within 5% of A"]

    def test_empty_gates(self) -> None:
        pipeline = hud._build_pipeline_state([])
        assert all(s["result"] == "not-started" for s in pipeline)
        assert len(pipeline) == len(hud.PIPELINE_STEPS)


class TestCollectHudData:
    def test_collects_from_bundle(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        assert data["run_constants"]["RUN_ID"] == "TEST-RUN-001"
        assert data["pipeline_summary"]["passed"] == 1
        assert data["pipeline_summary"]["failed"] == 1
        # Gate 04 is the 5th step (01, 02, 02A, 03, 04)
        assert data["pipeline_summary"]["current_step"] == 5
        assert len(data["artifacts"]) > 0

    def test_collects_with_no_bundle(self, tmp_path: Path) -> None:
        data = hud.collect_hud_data(
            bundle_dir=None, bundles_dir=tmp_path / "empty"
        )
        assert data["run_constants"] == {}
        assert data["pipeline_summary"]["current_step"] == 0

    def test_dev_report_included(self, bundle: Path, tmp_path: Path) -> None:
        sprint = tmp_path / "sprint.yaml"
        sprint.write_text(
            "last_updated: 2026-04-16\n"
            "development_status:\n"
            "  epic-1: done\n"
            "  1-1-test: done\n",
            encoding="utf-8",
        )
        handoff = tmp_path / "handoff.md"
        handoff.write_text(
            "# H\n\n## What Is Next\nX\n\n## Unresolved Issues\nY\n",
            encoding="utf-8",
        )
        nxt = tmp_path / "next.md"
        nxt.write_text(
            "# N\n\n## Immediate Next Action\nA\n\n"
            "## Key Risks / Unresolved Issues\nR\n",
            encoding="utf-8",
        )

        from scripts.utilities import progress_map as pm
        with patch.object(pm, "SPRINT_STATUS", sprint), \
             patch.object(pm, "SESSION_HANDOFF", handoff), \
             patch.object(pm, "NEXT_SESSION", nxt):
            data = hud.collect_hud_data(bundle_dir=bundle)

        assert data["dev_report"] is not None
        assert "summary" in data["dev_report"]

    def test_dev_report_degrades_on_exception(self, bundle: Path) -> None:
        """build_progress_report raising non-SystemExit must not crash HUD."""
        with patch(
            "scripts.utilities.run_hud.build_progress_report",
            side_effect=FileNotFoundError("boom"),
        ):
            data = hud.collect_hud_data(bundle_dir=bundle)
        assert data["dev_report"] is None


# ---------------------------------------------------------------------------
# Rendering tests
# ---------------------------------------------------------------------------


class TestRenderHtml:
    def test_produces_valid_html(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "<!DOCTYPE html>" in html
        assert "TEST-RUN-001" in html
        assert "visual-led" in html

    def test_shows_pipeline_steps(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "Activation + Preflight" in html
        assert "Ingestion Quality Gate" in html
        assert "status-pass" in html
        assert "status-fail" in html

    def test_shows_gate_details(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "Preflight OK" in html
        assert "Extraction too thin" in html
        assert "word count 120" in html

    def test_shows_metrics(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "word_count" in html
        assert "3000" in html

    def test_includes_refresh_script(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "sessionStorage" in html
        assert "hud_scroll" in html
        assert "refreshBar" in html

    def test_includes_tab_switching(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "switchTab" in html
        assert "tab-production" in html
        assert "tab-dev" in html

    def test_empty_run_renders_cleanly(self, tmp_path: Path) -> None:
        data = hud.collect_hud_data(
            bundle_dir=None, bundles_dir=tmp_path / "empty"
        )
        html = hud.render_html(data)
        assert "<!DOCTYPE html>" in html
        assert "No active run" in html

    def test_escapes_html_special_chars(self, tmp_path: Path) -> None:
        b = tmp_path / "xss-bundle"
        b.mkdir()
        rc = {"RUN_ID": "<script>alert(1)</script>", "XSS": "a&b"}
        (b / "run-constants.yaml").write_text(
            yaml.dump(rc, default_flow_style=False), encoding="utf-8"
        )
        data = hud.collect_hud_data(bundle_dir=b)
        html = hud.render_html(data)
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html
        assert "a&amp;b" in html


class TestRenderDevPanel:
    def test_renders_with_report(self) -> None:
        report = {
            "summary": {
                "completion_pct": 76.1,
                "done_stories": 108,
                "total_stories": 142,
                "done_epics": 19,
                "active_epics": 4,
                "backlog_epics": 4,
            },
            "completed_epics": [{"id": "1", "label": "Test", "stories": 5}],
            "backlog_epics": [{"id": "15", "label": "Future", "stories": 7}],
            "you_are_here": {
                "active_epics": [{
                    "epic_id": "20c",
                    "label": "Cluster Intel",
                    "counts": {"done": 11, "in_progress": 1, "ready": 0,
                               "deferred": 3, "backlog": 0, "review": 0, "unknown": 0},
                    "in_progress": ["20c-1"],
                    "ready_for_dev": [],
                    "deferred": ["20c-4"],
                    "in_review": [],
                }],
            },
            "source_health": {"verdict": "CLEAN", "findings": []},
            "risks": "",
        }
        html = hud._render_dev_panel(report)
        assert "76.1%" in html
        assert "108/142" in html
        assert "20c" in html
        assert "Cluster Intel" in html

    def test_renders_without_report(self) -> None:
        html = hud._render_dev_panel(None)
        assert "unavailable" in html


# ---------------------------------------------------------------------------
# HUD v2: System Health, freshness, layout tests
# ---------------------------------------------------------------------------


class TestRenderHealthPanel:
    def test_renders_preflight_pass(self) -> None:
        pipeline = [{"id": "01", "result": "pass", "name": "Preflight",
                      "is_gate": True, "summary": "All clear",
                      "metrics": {"mcp_gamma": "connected", "bundle_validated": "true"},
                      "timestamp": "2026-04-16T14:00:00Z",
                      "conditions": [], "blockers": [], "evidence": "",
                      "duration": 12, "inputs": [], "outputs": []}]
        html = hud._render_health_panel(pipeline, None)
        assert "Preflight" in html
        assert "All clear" in html
        assert "connected" in html
        assert "READY" in html

    def test_renders_preflight_not_run(self) -> None:
        pipeline = [{"id": "01", "result": "not-started", "name": "Preflight",
                      "is_gate": True, "summary": "", "metrics": {},
                      "timestamp": "", "conditions": [], "blockers": [],
                      "evidence": "", "duration": 0, "inputs": [], "outputs": []}]
        html = hud._render_health_panel(pipeline, None)
        assert "Not yet run" in html

    def test_renders_source_health(self) -> None:
        pipeline = [{"id": "01", "result": "not-started", "name": "P",
                      "is_gate": True, "summary": "", "metrics": {},
                      "timestamp": "", "conditions": [], "blockers": [],
                      "evidence": "", "duration": 0, "inputs": [], "outputs": []}]
        dev_report = {
            "source_health": {
                "verdict": "DEGRADED",
                "error_count": 0,
                "warning_count": 1,
                "findings": [
                    {"level": "warn", "check": "staleness", "message": "Old data"}
                ],
            }
        }
        html = hud._render_health_panel(pipeline, dev_report)
        assert "DEGRADED" in html
        assert "Old data" in html


class TestHudV2Layout:
    def test_three_tabs_present(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "tab-health" in html
        assert "tab-production" in html
        assert "tab-dev" in html
        assert "System Health" in html

    def test_right_panel_present(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "run-context" in html
        assert "Run Context" in html
        assert "hud-body" in html

    def test_freshness_meter_present(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "freshness-meter" in html
        assert "countdown" in html

    def test_source_freshness_tracked(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        assert "source_freshness" in data
        assert "run-constants" in data["source_freshness"]
        assert "gate-sidecars" in data["source_freshness"]

    def test_script_at_end_of_body(self, bundle: Path) -> None:
        """Script must be at end of body so DOM exists for tab restore."""
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        script_pos = html.rfind("<script>")
        body_end = html.rfind("</body>")
        assert script_pos < body_end
        # Script should be AFTER the tab content
        tab_dev_pos = html.rfind("tab-dev")
        assert script_pos > tab_dev_pos

    def test_dom_content_loaded_in_js(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "DOMContentLoaded" in html


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestMainCli:
    def test_writes_output_file(self, bundle: Path, tmp_path: Path) -> None:
        output = tmp_path / "test-hud.html"
        hud.main(["--bundle-dir", str(bundle), "-o", str(output)])
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "TEST-RUN-001" in content

    def test_default_output_path(self, bundle: Path, tmp_path: Path) -> None:
        default = tmp_path / "hud.html"
        with patch.object(hud, "HUD_OUTPUT", default):
            hud.main(["--bundle-dir", str(bundle)])
        assert default.exists()


# ---------------------------------------------------------------------------
# Active-run bundle resolution tests
# ---------------------------------------------------------------------------


def _build_coordination_db(path: Path, rows: list[dict[str, str]]) -> None:
    """Create a minimal coordination.db with a production_runs table.

    Schema mirrors the production DB's production_runs columns used by
    ``_query_active_run_id``: run_id, status, updated_at (others are
    optional for the query). Tests supply whichever rows they need.
    """
    import sqlite3

    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE production_runs ("
            "run_id TEXT PRIMARY KEY, "
            "status TEXT NOT NULL, "
            "updated_at TEXT NOT NULL)"
        )
        for row in rows:
            conn.execute(
                "INSERT INTO production_runs (run_id, status, updated_at) "
                "VALUES (?, ?, ?)",
                (row["run_id"], row["status"], row["updated_at"]),
            )
        conn.commit()


class TestQueryActiveRunId:
    def test_returns_most_recent_planning_run(self, tmp_path: Path) -> None:
        db = tmp_path / "coordination.db"
        _build_coordination_db(db, [
            {"run_id": "OLD-RUN", "status": "planning", "updated_at": "2026-04-10T00:00:00"},
            {"run_id": "NEW-RUN", "status": "planning", "updated_at": "2026-04-19T00:00:00"},
        ])
        assert hud._query_active_run_id(db) == "NEW-RUN"

    def test_returns_active_over_planning_when_newer(self, tmp_path: Path) -> None:
        db = tmp_path / "coordination.db"
        _build_coordination_db(db, [
            {"run_id": "PLAN-RUN", "status": "planning", "updated_at": "2026-04-10T00:00:00"},
            {"run_id": "ACTIVE-RUN", "status": "active", "updated_at": "2026-04-19T00:00:00"},
        ])
        assert hud._query_active_run_id(db) == "ACTIVE-RUN"

    def test_skips_cancelled_and_completed(self, tmp_path: Path) -> None:
        db = tmp_path / "coordination.db"
        _build_coordination_db(db, [
            {"run_id": "CANCELLED", "status": "cancelled", "updated_at": "2026-04-19T00:00:00"},
            {"run_id": "COMPLETED", "status": "completed", "updated_at": "2026-04-19T00:00:00"},
            {"run_id": "PLAN-RUN", "status": "planning", "updated_at": "2026-04-10T00:00:00"},
        ])
        assert hud._query_active_run_id(db) == "PLAN-RUN"

    def test_missing_db_returns_none(self, tmp_path: Path) -> None:
        assert hud._query_active_run_id(tmp_path / "nope.db") is None

    def test_no_matching_rows_returns_none(self, tmp_path: Path) -> None:
        db = tmp_path / "coordination.db"
        _build_coordination_db(db, [
            {"run_id": "CANCELLED", "status": "cancelled", "updated_at": "2026-04-19T00:00:00"},
        ])
        assert hud._query_active_run_id(db) is None

    def test_malformed_db_returns_none(self, tmp_path: Path) -> None:
        bad = tmp_path / "coordination.db"
        bad.write_bytes(b"not a sqlite database")
        assert hud._query_active_run_id(bad) is None

    def test_missing_table_returns_none(self, tmp_path: Path) -> None:
        import sqlite3
        db = tmp_path / "coordination.db"
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE unrelated (id INTEGER)")
            conn.commit()
        assert hud._query_active_run_id(db) is None


class TestBundleRunId:
    def test_reads_lowercase_run_id(self, tmp_path: Path) -> None:
        b = tmp_path / "bundle"
        b.mkdir()
        (b / "run-constants.yaml").write_text(
            yaml.dump({"run_id": "LOWER-CASE"}), encoding="utf-8"
        )
        assert hud._bundle_run_id(b) == "LOWER-CASE"

    def test_reads_uppercase_run_id_legacy(self, tmp_path: Path) -> None:
        b = tmp_path / "bundle"
        b.mkdir()
        (b / "run-constants.yaml").write_text(
            yaml.dump({"RUN_ID": "UPPER-CASE"}), encoding="utf-8"
        )
        assert hud._bundle_run_id(b) == "UPPER-CASE"

    def test_missing_file_returns_none(self, tmp_path: Path) -> None:
        b = tmp_path / "bundle"
        b.mkdir()
        assert hud._bundle_run_id(b) is None

    def test_malformed_yaml_returns_none(self, tmp_path: Path) -> None:
        b = tmp_path / "bundle"
        b.mkdir()
        (b / "run-constants.yaml").write_text("{{not yaml", encoding="utf-8")
        assert hud._bundle_run_id(b) is None

    def test_empty_run_id_returns_none(self, tmp_path: Path) -> None:
        b = tmp_path / "bundle"
        b.mkdir()
        (b / "run-constants.yaml").write_text(
            yaml.dump({"run_id": ""}), encoding="utf-8"
        )
        assert hud._bundle_run_id(b) is None


class TestFindBundleForRunId:
    def test_matches_correct_bundle(self, tmp_path: Path) -> None:
        bundles = tmp_path / "bundles"
        bundles.mkdir()
        first = bundles / "first-bundle"
        first.mkdir()
        (first / "run-constants.yaml").write_text(
            yaml.dump({"run_id": "RUN-A"}), encoding="utf-8"
        )
        second = bundles / "second-bundle"
        second.mkdir()
        (second / "run-constants.yaml").write_text(
            yaml.dump({"run_id": "RUN-B"}), encoding="utf-8"
        )
        assert hud._find_bundle_for_run_id(bundles, "RUN-B") == second

    def test_no_match_returns_none(self, tmp_path: Path) -> None:
        bundles = tmp_path / "bundles"
        bundles.mkdir()
        b = bundles / "only-bundle"
        b.mkdir()
        (b / "run-constants.yaml").write_text(
            yaml.dump({"run_id": "RUN-X"}), encoding="utf-8"
        )
        assert hud._find_bundle_for_run_id(bundles, "NO-SUCH") is None

    def test_missing_dir_returns_none(self, tmp_path: Path) -> None:
        assert hud._find_bundle_for_run_id(tmp_path / "nope", "any") is None

    def test_skips_bundles_without_run_constants(self, tmp_path: Path) -> None:
        bundles = tmp_path / "bundles"
        bundles.mkdir()
        bare = bundles / "bare-bundle"
        bare.mkdir()
        target = bundles / "target"
        target.mkdir()
        (target / "run-constants.yaml").write_text(
            yaml.dump({"run_id": "TARGET"}), encoding="utf-8"
        )
        assert hud._find_bundle_for_run_id(bundles, "TARGET") == target


class TestResolveActiveBundle:
    def test_db_match_wins_over_mtime(self, tmp_path: Path) -> None:
        bundles = tmp_path / "bundles"
        bundles.mkdir()
        # Older bundle with matching run_id
        older = bundles / "older"
        older.mkdir()
        (older / "run-constants.yaml").write_text(
            yaml.dump({"run_id": "ACTIVE-RUN"}), encoding="utf-8"
        )
        # Newer bundle that would win on mtime alone
        newer = bundles / "newer"
        newer.mkdir()
        (newer / "run-constants.yaml").write_text(
            yaml.dump({"run_id": "OTHER-RUN"}), encoding="utf-8"
        )
        (newer / "marker.txt").write_text("recent", encoding="utf-8")

        db = tmp_path / "coordination.db"
        _build_coordination_db(db, [
            {"run_id": "ACTIVE-RUN", "status": "active", "updated_at": "2026-04-19T00:00:00"},
        ])
        result = hud._resolve_active_bundle(bundles, db_path=db)
        assert result == older

    def test_falls_back_to_mtime_when_no_db_match(self, tmp_path: Path) -> None:
        bundles = tmp_path / "bundles"
        bundles.mkdir()
        older = bundles / "older"
        older.mkdir()
        newer = bundles / "newer"
        newer.mkdir()
        (newer / "marker.txt").write_text("x", encoding="utf-8")

        db = tmp_path / "coordination.db"
        _build_coordination_db(db, [
            {"run_id": "ORPHAN-RUN", "status": "active", "updated_at": "2026-04-19T00:00:00"},
        ])
        result = hud._resolve_active_bundle(bundles, db_path=db)
        assert result == newer

    def test_falls_back_to_mtime_when_no_db(self, tmp_path: Path) -> None:
        bundles = tmp_path / "bundles"
        bundles.mkdir()
        only = bundles / "only"
        only.mkdir()
        result = hud._resolve_active_bundle(bundles, db_path=tmp_path / "missing.db")
        assert result == only


# ---------------------------------------------------------------------------
# Watch-mode tests
# ---------------------------------------------------------------------------


class TestCollectWatchPaths:
    def test_includes_existing_core_files(self, tmp_path: Path) -> None:
        (tmp_path / "state" / "config").mkdir(parents=True)
        (tmp_path / "state" / "runtime").mkdir(parents=True)
        (tmp_path / "_bmad-output" / "implementation-artifacts").mkdir(parents=True)

        manifest = tmp_path / "state" / "config" / "pipeline-manifest.yaml"
        manifest.write_text("{}", encoding="utf-8")
        sprint = tmp_path / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
        sprint.write_text("{}", encoding="utf-8")
        mode_state = tmp_path / "state" / "runtime" / "mode_state.json"
        mode_state.write_text("{}", encoding="utf-8")

        paths = hud._collect_watch_paths(None, root=tmp_path)
        resolved = {p.resolve() for p in paths}
        assert manifest.resolve() in resolved
        assert sprint.resolve() in resolved
        assert mode_state.resolve() in resolved

    def test_skips_missing_core_files(self, tmp_path: Path) -> None:
        paths = hud._collect_watch_paths(None, root=tmp_path)
        assert paths == []

    def test_includes_bundle_files_recursively(self, tmp_path: Path) -> None:
        bundle = tmp_path / "bundle"
        (bundle / "gates").mkdir(parents=True)
        (bundle / "extracted.md").write_text("x", encoding="utf-8")
        (bundle / "gates" / "gate-01-result.yaml").write_text("x", encoding="utf-8")

        paths = hud._collect_watch_paths(bundle, root=tmp_path)
        resolved = {p.resolve() for p in paths}
        assert (bundle / "extracted.md").resolve() in resolved
        assert (bundle / "gates" / "gate-01-result.yaml").resolve() in resolved


class TestSnapshotAndDetect:
    def test_snapshot_records_mtimes(self, tmp_path: Path) -> None:
        a = tmp_path / "a.txt"
        a.write_text("x", encoding="utf-8")
        snap = hud._snapshot_mtimes([a])
        assert str(a.resolve()) in snap

    def test_detect_no_changes(self, tmp_path: Path) -> None:
        a = tmp_path / "a.txt"
        a.write_text("x", encoding="utf-8")
        snap = hud._snapshot_mtimes([a])
        assert hud._detect_changes(snap, dict(snap)) is False

    def test_detect_added_file(self, tmp_path: Path) -> None:
        a = tmp_path / "a.txt"
        a.write_text("x", encoding="utf-8")
        snap_before = hud._snapshot_mtimes([a])
        b = tmp_path / "b.txt"
        b.write_text("y", encoding="utf-8")
        snap_after = hud._snapshot_mtimes([a, b])
        assert hud._detect_changes(snap_before, snap_after) is True

    def test_detect_removed_file(self, tmp_path: Path) -> None:
        a = tmp_path / "a.txt"
        a.write_text("x", encoding="utf-8")
        b = tmp_path / "b.txt"
        b.write_text("y", encoding="utf-8")
        snap_before = hud._snapshot_mtimes([a, b])
        snap_after = hud._snapshot_mtimes([a])
        assert hud._detect_changes(snap_before, snap_after) is True

    def test_detect_modified_file(self, tmp_path: Path) -> None:
        a = tmp_path / "a.txt"
        a.write_text("x", encoding="utf-8")
        snap_before = hud._snapshot_mtimes([a])
        future = snap_before[str(a.resolve())] + 1.0
        snap_after = {str(a.resolve()): future}
        assert hud._detect_changes(snap_before, snap_after) is True


class TestRunWatchLoop:
    def test_generates_once_on_startup(self, bundle: Path, tmp_path: Path) -> None:
        output = tmp_path / "hud.html"
        prints: list[str] = []
        exit_code = hud.run_watch_loop(
            bundle_dir=bundle,
            output_path=output,
            root=tmp_path,
            bundles_dir=tmp_path / "no-bundles",
            db_path=tmp_path / "no-db.sqlite",
            poll_interval=0.01,
            max_iterations=1,
            sleep_fn=lambda _: None,
            print_fn=prints.append,
        )
        assert exit_code == 0
        assert output.exists()
        html = output.read_text(encoding="utf-8")
        # Banner should render the live mode marker.
        assert "Live" in html
        assert "Watching" in html
        assert any("HUD generated" in line for line in prints)

    def test_regenerates_when_watched_file_changes(
        self, bundle: Path, tmp_path: Path
    ) -> None:
        output = tmp_path / "hud.html"
        # Seed a sentinel file inside the bundle so the watcher notices a change
        sentinel = bundle / "sentinel.txt"
        sentinel.write_text("initial", encoding="utf-8")

        # The loop polls on each sleep_fn call; flip the sentinel's mtime
        # forward on the first poll so the watcher regenerates.
        call_count = {"n": 0}

        def _fake_sleep(_seconds: float) -> None:
            call_count["n"] += 1
            if call_count["n"] == 1:
                # Force a detectable mtime delta (fs granularity on Windows
                # can be as coarse as 2s; explicit os.utime is robust).
                import os
                new_mtime = sentinel.stat().st_mtime + 5.0
                os.utime(sentinel, (new_mtime, new_mtime))

        prints: list[str] = []
        hud.run_watch_loop(
            bundle_dir=bundle,
            output_path=output,
            root=tmp_path,
            bundles_dir=tmp_path / "no-bundles",
            db_path=tmp_path / "no-db.sqlite",
            poll_interval=0.01,
            max_iterations=2,
            sleep_fn=_fake_sleep,
            print_fn=prints.append,
        )
        # First iteration observes the mtime change and regenerates; second
        # iteration sees no further delta and does not.
        regen_lines = [line for line in prints if "regenerated" in line]
        assert len(regen_lines) == 1

    def test_no_regeneration_when_nothing_changes(
        self, bundle: Path, tmp_path: Path
    ) -> None:
        output = tmp_path / "hud.html"
        prints: list[str] = []
        hud.run_watch_loop(
            bundle_dir=bundle,
            output_path=output,
            root=tmp_path,
            bundles_dir=tmp_path / "no-bundles",
            db_path=tmp_path / "no-db.sqlite",
            poll_interval=0.01,
            max_iterations=3,
            sleep_fn=lambda _: None,
            print_fn=prints.append,
        )
        regen_lines = [line for line in prints if "regenerated" in line]
        assert regen_lines == []


# ---------------------------------------------------------------------------
# Snapshot banner tests
# ---------------------------------------------------------------------------


class TestSnapshotBanner:
    def test_static_banner_shows_static_label_and_guidance(
        self, bundle: Path
    ) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data, watching=False)
        assert "Static snapshot" in html
        assert "run_hud" in html
        assert "--watch" in html
        assert "snapshot-banner" in html
        assert "banner-static" in html

    def test_watch_banner_shows_live_label_and_interval(
        self, bundle: Path
    ) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data, watching=True, watch_interval_seconds=5)
        assert "Live" in html
        assert "Watching" in html
        assert "5s" in html
        assert "banner-live" in html

    def test_banner_includes_generated_timestamp(self, bundle: Path) -> None:
        data = hud.collect_hud_data(bundle_dir=bundle)
        html = hud.render_html(data)
        assert "Generated:" in html
