"""Validation tests for Story 1.4: Pre-Flight Check Skill.

Verifies skill structure, MCP config parsing, heartbeat output parsing,
readiness report classification, and resolution guidance.

Marked ``trial_critical`` — on the pre-Prompt-1 trial path. Must pass before
firing any trial production run. See ``docs/dev-guide/testing.md``.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from scripts.utilities.file_helpers import project_root

pytestmark = pytest.mark.trial_critical

ROOT = project_root()


# ---------------------------------------------------------------------------
# AC #1: Skill directory structure
# ---------------------------------------------------------------------------


class TestSkillStructure:
    def test_skill_md_exists(self):
        assert (ROOT / "skills/pre-flight-check/SKILL.md").exists()

    def test_references_dir_exists(self):
        assert (ROOT / "skills/pre-flight-check/references").is_dir()

    def test_scripts_dir_exists(self):
        assert (ROOT / "skills/pre-flight-check/scripts").is_dir()

    def test_diagnostic_procedures_exists(self):
        assert (ROOT / "skills/pre-flight-check/references/diagnostic-procedures.md").exists()

    def test_check_strategy_matrix_exists(self):
        assert (ROOT / "skills/pre-flight-check/references/check-strategy-matrix.md").exists()

    def test_tool_doc_scanning_exists(self):
        assert (ROOT / "skills/pre-flight-check/references/tool-doc-scanning.md").exists()

    def test_preflight_runner_exists(self):
        assert (ROOT / "skills/pre-flight-check/scripts/preflight_runner.py").exists()

    def test_doc_scanner_exists(self):
        assert (ROOT / "skills/pre-flight-check/scripts/doc_scanner.py").exists()


# ---------------------------------------------------------------------------
# AC #2: MCP config parsing
# ---------------------------------------------------------------------------


class TestMCPConfigParsing:
    def test_parse_project_mcp_json(self):
        from skills.pre_flight_check.scripts.preflight_runner import check_mcp_configs

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            mcp = {"mcpServers": {"gamma": {"command": "node", "args": ["test"]}}}
            (tmp_path / ".mcp.json").write_text(json.dumps(mcp), encoding="utf-8")

            result = check_mcp_configs(tmp_path)
            assert "gamma" in result

    def test_parse_cursor_mcp_json(self):
        from skills.pre_flight_check.scripts.preflight_runner import check_mcp_configs

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cursor_dir = tmp_path / ".cursor"
            cursor_dir.mkdir()
            mcp = {"mcpServers": {"canvas-lms": {"command": "node", "args": []}}}
            (cursor_dir / "mcp.json").write_text(json.dumps(mcp), encoding="utf-8")

            result = check_mcp_configs(tmp_path)
            assert "canvas-lms" in result

    def test_merge_both_configs(self):
        from skills.pre_flight_check.scripts.preflight_runner import check_mcp_configs

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / ".mcp.json").write_text(
                json.dumps({"mcpServers": {"gamma": {"command": "node"}}}),
                encoding="utf-8",
            )
            cursor_dir = tmp_path / ".cursor"
            cursor_dir.mkdir()
            (cursor_dir / "mcp.json").write_text(
                json.dumps({"mcpServers": {"canvas-lms": {"command": "node"}}}),
                encoding="utf-8",
            )

            result = check_mcp_configs(tmp_path)
            assert "gamma" in result
            assert "canvas-lms" in result

    def test_missing_config_returns_empty(self):
        from skills.pre_flight_check.scripts.preflight_runner import check_mcp_configs

        with tempfile.TemporaryDirectory() as tmp:
            result = check_mcp_configs(Path(tmp))
            assert result == {}

    def test_real_mcp_configs(self):
        from skills.pre_flight_check.scripts.preflight_runner import check_mcp_configs

        result = check_mcp_configs(ROOT)
        assert "gamma" in result
        assert "canvas-lms" in result


# ---------------------------------------------------------------------------
# AC #3 + #4: Heartbeat output parsing
# ---------------------------------------------------------------------------


class TestHeartbeatParsing:
    SAMPLE_OUTPUT = """
=== TIER 1: Full Programmatic Access (API + MCP) ===
  PASS: Gamma API — Connected (themes endpoint responded)
  PASS: ElevenLabs API — Connected (45 voices available)
  PASS: Canvas LMS API — Connected (user: Test User)
  FAIL: Qualtrics API — HTTP 401
  SKIP: Canva API — OAuth-based (MCP handles auth via browser). Test by using Canva MCP in Cursor.

=== TIER 2: API Only (No MCP) ===
  SKIP: Botpress API — BOTPRESS_API_KEY not set in .env
  PASS: Wondercraft API — Connected (responded with HTTP 200)
  SKIP: Vyond API — Manual workflow for this repo

HEARTBEAT RESULTS: 3 connected, 1 failed, 3 skipped
"""

    def test_parse_pass_lines(self):
        from skills.pre_flight_check.scripts.preflight_runner import parse_heartbeat_output

        results = parse_heartbeat_output(self.SAMPLE_OUTPUT)
        passed = [r for r in results if r["status"] == "PASS"]
        assert len(passed) == 4

    def test_parse_fail_lines(self):
        from skills.pre_flight_check.scripts.preflight_runner import parse_heartbeat_output

        results = parse_heartbeat_output(self.SAMPLE_OUTPUT)
        failed = [r for r in results if r["status"] == "FAIL"]
        assert len(failed) == 1
        assert "401" in failed[0]["detail"]

    def test_parse_skip_lines(self):
        from skills.pre_flight_check.scripts.preflight_runner import parse_heartbeat_output

        results = parse_heartbeat_output(self.SAMPLE_OUTPUT)
        skipped = [r for r in results if r["status"] == "SKIP"]
        assert len(skipped) == 3

    def test_parse_tool_names(self):
        from skills.pre_flight_check.scripts.preflight_runner import parse_heartbeat_output

        results = parse_heartbeat_output(self.SAMPLE_OUTPUT)
        names = {r["name"] for r in results}
        assert "Gamma API" in names
        assert "ElevenLabs API" in names
        assert "Canvas LMS API" in names


# ---------------------------------------------------------------------------
# AC #6: Readiness report classification
# ---------------------------------------------------------------------------


class TestReportClassification:
    def test_mcp_ready_classification(self):
        from skills.pre_flight_check.scripts.preflight_runner import (
            PreflightReport,
            ToolResult,
            ToolStatus,
        )

        report = PreflightReport()
        report.add(ToolResult("Gamma", ToolStatus.MCP_READY, "MCP configured"))
        assert len(report.by_status(ToolStatus.MCP_READY)) == 1

    def test_api_ready_classification(self):
        from skills.pre_flight_check.scripts.preflight_runner import (
            PreflightReport,
            ToolResult,
            ToolStatus,
        )

        report = PreflightReport()
        report.add(ToolResult("ElevenLabs", ToolStatus.API_READY, "45 voices"))
        assert len(report.by_status(ToolStatus.API_READY)) == 1

    def test_has_failures_flag(self):
        from skills.pre_flight_check.scripts.preflight_runner import (
            PreflightReport,
            ToolResult,
            ToolStatus,
        )

        report = PreflightReport()
        report.add(ToolResult("Good", ToolStatus.API_READY, "ok"))
        assert not report.has_failures

        report.add(ToolResult("Bad", ToolStatus.FAILED, "error"))
        assert report.has_failures

    def test_format_report_structure(self):
        from skills.pre_flight_check.scripts.preflight_runner import (
            PreflightReport,
            ToolResult,
            ToolStatus,
        )

        report = PreflightReport()
        report.add(ToolResult("Gamma", ToolStatus.MCP_READY, "ok"))
        report.add(ToolResult("ElevenLabs", ToolStatus.API_READY, "ok"))
        report.add(ToolResult("Vyond", ToolStatus.MANUAL_ONLY, "manual"))
        report.add(ToolResult("Bad", ToolStatus.FAILED, "HTTP 401", "Check key"))

        output = report.format_report()
        assert "PRE-FLIGHT CHECK RESULTS" in output
        assert "MCP-READY" in output
        assert "API-READY" in output
        assert "MANUAL-ONLY" in output
        assert "RESOLUTION NEEDED" in output
        assert "SUMMARY" in output

    def test_report_all_statuses(self):
        from skills.pre_flight_check.scripts.preflight_runner import ToolStatus

        statuses = list(ToolStatus)
        assert len(statuses) == 6


class TestNonBlockingToolFailures:
    def test_botpress_failure_classified_as_blocked_non_blocking(self):
        from skills.pre_flight_check.scripts.preflight_runner import run_preflight

        root = ROOT

        from skills.pre_flight_check.scripts import preflight_runner as mod

        original_run_node_script = mod.run_node_script
        original_check_notion_api = mod.check_notion_api
        original_check_box_drive = mod.check_box_drive
        original_load_env = mod.load_env

        def fake_run_node_script(script_path, cwd):
            name = Path(script_path).name
            if name == "heartbeat_check.mjs":
                return (
                    0,
                    "FAIL: Botpress API -- HTTP 400\n"
                    "PASS: Gamma API -- Connected (themes endpoint responded)\n",
                    "",
                )
            return 0, "", ""

        try:
            mod.run_node_script = fake_run_node_script
            mod.load_env = lambda _path: {}
            mod.check_notion_api = lambda _env: mod.ToolResult(
                "Notion", mod.ToolStatus.SKIPPED, "NOTION_API_KEY not set in .env"
            )
            mod.check_box_drive = lambda _env: mod.ToolResult(
                "Box Drive", mod.ToolStatus.SKIPPED, "BOX_DRIVE_PATH not set in .env"
            )

            report = run_preflight(root)

            botpress_results = [
                r for r in report.results if r.name.lower().startswith("botpress")
            ]
            assert len(botpress_results) == 1
            assert botpress_results[0].status == mod.ToolStatus.BLOCKED
            assert "non-blocking" in botpress_results[0].detail.lower()
            assert not report.has_failures
        finally:
            mod.run_node_script = original_run_node_script
            mod.check_notion_api = original_check_notion_api
            mod.check_box_drive = original_check_box_drive
            mod.load_env = original_load_env


# ---------------------------------------------------------------------------
# AC #7: Resolution guidance
# ---------------------------------------------------------------------------


class TestResolutionGuidance:
    def test_missing_key_resolution(self):
        from skills.pre_flight_check.scripts.preflight_runner import get_resolution

        r = get_resolution("GAMMA_API_KEY not set in .env")
        assert ".env" in r.lower() or "key" in r.lower()

    def test_auth_failure_resolution(self):
        from skills.pre_flight_check.scripts.preflight_runner import get_resolution

        r = get_resolution("HTTP 401 Unauthorized")
        assert "invalid" in r.lower() or "expired" in r.lower()

    def test_rate_limit_resolution(self):
        from skills.pre_flight_check.scripts.preflight_runner import get_resolution

        r = get_resolution("HTTP 429 Too Many Requests")
        assert "wait" in r.lower() or "retry" in r.lower()

    def test_connection_error_resolution(self):
        from skills.pre_flight_check.scripts.preflight_runner import get_resolution

        r = get_resolution("Connection error: could not reach host")
        assert "internet" in r.lower() or "connectivity" in r.lower()

    def test_oauth_resolution(self):
        from skills.pre_flight_check.scripts.preflight_runner import get_resolution

        r = get_resolution("OAuth-based authentication required")
        assert "browser" in r.lower() or "mcp" in r.lower()

    def test_manual_workflow_resolution(self):
        from skills.pre_flight_check.scripts.preflight_runner import get_resolution

        r = get_resolution("Manual workflow for this repo")
        assert "agent" in r.lower() or "ui" in r.lower() or "specs" in r.lower()

    def test_default_resolution(self):
        from skills.pre_flight_check.scripts.preflight_runner import get_resolution

        r = get_resolution("Some unknown error type")
        assert len(r) > 0


# ---------------------------------------------------------------------------
# AC #5: Doc scanner
# ---------------------------------------------------------------------------


class TestDocScanner:
    def test_get_scan_instructions(self):
        from skills.pre_flight_check.scripts.doc_scanner import get_scan_instructions

        instructions = get_scan_instructions()
        assert len(instructions) > 0
        for inst in instructions:
            assert "tool" in inst
            assert "search_queries" in inst
            assert "instruction" in inst

    def test_scan_targets_include_key_tools(self):
        from skills.pre_flight_check.scripts.doc_scanner import get_scan_instructions

        tools = {inst["tool"] for inst in get_scan_instructions()}
        assert "Gamma" in tools
        assert "ElevenLabs" in tools
        assert "Canvas LMS" in tools

    def test_format_scan_prompt(self):
        from skills.pre_flight_check.scripts.doc_scanner import format_scan_prompt

        prompt = format_scan_prompt()
        assert "Gamma" in prompt
        assert "ElevenLabs" in prompt
        assert "ref_search_documentation" not in prompt  # instructions, not commands
        assert "Doc URL" in prompt


# ---------------------------------------------------------------------------
# AC #8: Reference documentation exists
# ---------------------------------------------------------------------------


class TestReferenceDocumentation:
    def test_diagnostic_procedures_has_content(self):
        content = (
            ROOT / "skills/pre-flight-check/references/diagnostic-procedures.md"
        ).read_text(encoding="utf-8")
        assert "401" in content
        assert "Connection" in content

    def test_check_strategy_matrix_has_tools(self):
        content = (
            ROOT / "skills/pre-flight-check/references/check-strategy-matrix.md"
        ).read_text(encoding="utf-8")
        assert "Gamma" in content
        assert "Canvas" in content
        assert "MCP" in content

    def test_tool_doc_scanning_has_targets(self):
        content = (
            ROOT / "skills/pre-flight-check/references/tool-doc-scanning.md"
        ).read_text(encoding="utf-8")
        assert "Ref MCP" in content
        assert "Gamma" in content


# ---------------------------------------------------------------------------
# Story 12.5: Double-dispatch compatibility check
# ---------------------------------------------------------------------------


class TestDoubleDispatchCompatibility:
    def test_check_passes_when_gamma_key_present(self):
        from skills.pre_flight_check.scripts.preflight_runner import (
            ToolStatus,
            check_double_dispatch_compatibility,
        )

        result = check_double_dispatch_compatibility({"GAMMA_API_KEY": "test-key-123"})
        assert result.status == ToolStatus.API_READY
        assert "present" in result.detail.lower()

    def test_check_fails_when_gamma_key_missing(self):
        import os
        from unittest.mock import patch

        from skills.pre_flight_check.scripts.preflight_runner import (
            ToolStatus,
            check_double_dispatch_compatibility,
        )

        with patch.dict(os.environ, {}, clear=True):
            result = check_double_dispatch_compatibility({})
        assert result.status == ToolStatus.FAILED
        assert "GAMMA_API_KEY" in result.detail

    def test_preflight_skips_check_when_flag_inactive(self):
        from skills.pre_flight_check.scripts.preflight_runner import run_preflight

        report = run_preflight(ROOT, double_dispatch=False)
        dd_results = [r for r in report.results if "Double-Dispatch" in r.name]
        assert len(dd_results) == 0

    def test_preflight_includes_check_when_flag_active(self):
        from skills.pre_flight_check.scripts.preflight_runner import run_preflight

        report = run_preflight(ROOT, double_dispatch=True)
        dd_results = [r for r in report.results if "Double-Dispatch" in r.name]
        assert len(dd_results) == 1


class TestMotionPipelineCompatibility:
    def test_check_passes_when_kling_keys_present(self):
        from skills.pre_flight_check.scripts.preflight_runner import (
            ToolStatus,
            check_kling_compatibility,
        )

        result = check_kling_compatibility(
            {"KLING_ACCESS_KEY": "ak-test", "KLING_SECRET_KEY": "sk-test"}
        )
        assert result.status == ToolStatus.API_READY
        assert "motion-enabled" in result.detail.lower()

    def test_check_fails_when_kling_keys_missing(self):
        import os
        from unittest.mock import patch

        from skills.pre_flight_check.scripts.preflight_runner import (
            ToolStatus,
            check_kling_compatibility,
        )

        with patch.dict(os.environ, {}, clear=True):
            result = check_kling_compatibility({})
        assert result.status == ToolStatus.FAILED
        assert "KLING_ACCESS_KEY" in result.detail

    def test_preflight_skips_motion_check_when_motion_disabled(self):
        from skills.pre_flight_check.scripts.preflight_runner import run_preflight

        report = run_preflight(ROOT, motion_enabled=False)
        motion_results = [r for r in report.results if "Motion Pipeline" in r.name]
        assert len(motion_results) == 0

    def test_preflight_includes_motion_check_when_motion_enabled(self):
        from skills.pre_flight_check.scripts.preflight_runner import run_preflight

        report = run_preflight(ROOT, motion_enabled=True)
        motion_results = [r for r in report.results if "Motion Pipeline" in r.name]
        assert len(motion_results) == 1
