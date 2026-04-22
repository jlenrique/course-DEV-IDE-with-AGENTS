"""Tests for PDG-3 flake-gate wrapper (scripts/ci/run_flake_gate.py).

Covers the pytest-summary parser (the only non-trivial logic in the wrapper)
and the run-outcome signature comparison that the flake detector depends on.
Subprocess invocation is a thin orchestration layer exercised by the 3x
local runs on commit and by the GitHub Actions workflow itself.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_WRAPPER_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "ci" / "run_flake_gate.py"
)
# Use a unique module name so the spec'd module does not collide with any
# stale sys.modules entry from another test or a partial prior import.
_MODULE_NAME = "_test_run_flake_gate_helper"
_spec = importlib.util.spec_from_file_location(_MODULE_NAME, _WRAPPER_PATH)
assert _spec is not None and _spec.loader is not None
run_flake_gate = importlib.util.module_from_spec(_spec)
sys.modules[_MODULE_NAME] = run_flake_gate
_spec.loader.exec_module(run_flake_gate)


@pytest.mark.parametrize(
    "summary_line, expected",
    [
        (
            "12 passed, 2143 deselected in 1.55s",
            {
                "passed": 12,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "xfailed": 0,
                "xpassed": 0,
                "deselected": 2143,
            },
        ),
        (
            "1478 passed, 6 skipped, 2 xfailed, 2 deselected in 30.22s",
            {
                "passed": 1478,
                "failed": 0,
                "errors": 0,
                "skipped": 6,
                "xfailed": 2,
                "xpassed": 0,
                "deselected": 2,
            },
        ),
        (
            "5 passed, 1 failed, 2 errors in 0.50s",
            {
                "passed": 5,
                "failed": 1,
                "errors": 2,
                "skipped": 0,
                "xfailed": 0,
                "xpassed": 0,
                "deselected": 0,
            },
        ),
        (
            "10 passed, 1 xpassed in 0.10s",
            {
                "passed": 10,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "xfailed": 0,
                "xpassed": 1,
                "deselected": 0,
            },
        ),
        # Failure-only summary (no "passed" fragment) — pytest emits this
        # when all tests fail. Prior regex required passed first and
        # returned zero-tuple silently.
        (
            "5 failed in 0.10s",
            {
                "passed": 0,
                "failed": 5,
                "errors": 0,
                "skipped": 0,
                "xfailed": 0,
                "xpassed": 0,
                "deselected": 0,
            },
        ),
        # Error-only summary (singular plural boundary).
        (
            "1 error in 0.05s",
            {
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "skipped": 0,
                "xfailed": 0,
                "xpassed": 0,
                "deselected": 0,
            },
        ),
    ],
)
def test_parse_summary_extracts_counts(summary_line, expected):
    stdout = f"some noise\n{summary_line}\n"
    counts, recognized = run_flake_gate._parse_summary(stdout)
    assert recognized is True
    assert counts == expected


def test_parse_summary_reads_last_summary_line_wins():
    # pytest-xdist / rerunfailures can print multiple summary lines; the
    # terminal one is authoritative. Parser reverse-scans for the last
    # line matching the `in <n>s` tail sentinel.
    stdout = (
        "3 passed, 1 failed in 0.01s\n"
        "noise\n"
        "12 passed in 1.55s\n"
    )
    counts, recognized = run_flake_gate._parse_summary(stdout)
    assert recognized is True
    assert (counts["passed"], counts["failed"], counts["errors"]) == (12, 0, 0)


def test_parse_summary_returns_unrecognized_when_no_match():
    """Stdout without any pytest summary line — recognized=False signals
    the gate to fail-closed rather than silently treating as zero-green."""
    counts, recognized = run_flake_gate._parse_summary("no summary here\n")
    assert recognized is False
    assert counts == {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "deselected": 0,
    }


def test_parse_summary_ignores_noise_lines_that_mention_passed():
    """Assertion text or traceback lines can contain `"N passed"` strings;
    the `in <n>s` tail anchor keeps them from being mis-parsed as the
    authoritative summary."""
    stdout = (
        "AssertionError: expected 5 passed, got 3 failed\n"
        "some random line with passed in it\n"
        "12 passed in 1.55s\n"
    )
    counts, recognized = run_flake_gate._parse_summary(stdout)
    assert recognized is True
    assert counts["passed"] == 12
    assert counts["failed"] == 0


def test_parse_summary_recognizes_no_tests_ran():
    stdout = "no tests ran in 0.01s\n"
    counts, recognized = run_flake_gate._parse_summary(stdout)
    assert recognized is True
    assert counts["passed"] == 0


def test_run_outcome_signature_is_tuple_of_counts():
    outcome = run_flake_gate.RunOutcome(
        exit_code=0,
        passed=12,
        failed=0,
        errors=0,
        skipped=0,
        xfailed=0,
        xpassed=0,
        deselected=2143,
        raw_tail="12 passed, 2143 deselected in 1.55s",
    )
    # parser_recognized_summary defaults True; included in signature so
    # crashes (unrecognized=False) cannot be confused with genuine greens.
    assert outcome.signature() == (0, 12, 0, 0, 0, 0, 0, 2143, True)


def test_run_outcome_signature_differs_on_exit_code():
    a = run_flake_gate.RunOutcome(0, 12, 0, 0, 0, 0, 0, 2143, "")
    b = run_flake_gate.RunOutcome(1, 12, 0, 0, 0, 0, 0, 2143, "")
    assert a.signature() != b.signature()


def test_run_outcome_signature_differs_on_failed_count():
    a = run_flake_gate.RunOutcome(0, 12, 0, 0, 0, 0, 0, 2143, "")
    b = run_flake_gate.RunOutcome(0, 11, 1, 0, 0, 0, 0, 2143, "")
    assert a.signature() != b.signature()


def test_run_outcome_signature_distinguishes_crash_from_zero_green():
    """Two runs both exit 0 with no counts parsed: without the recognized
    flag, signatures would match and the gate would declare green. With
    the flag, crashes are distinguishable from zero-test greens."""
    crashed = run_flake_gate.RunOutcome(
        exit_code=0,
        passed=0,
        failed=0,
        errors=0,
        skipped=0,
        xfailed=0,
        xpassed=0,
        deselected=0,
        raw_tail="",
        parser_recognized_summary=False,
    )
    clean = run_flake_gate.RunOutcome(
        exit_code=0,
        passed=0,
        failed=0,
        errors=0,
        skipped=0,
        xfailed=0,
        xpassed=0,
        deselected=0,
        raw_tail="no tests ran in 0.01s",
        parser_recognized_summary=True,
    )
    assert crashed.signature() != clean.signature()


def test_cli_rejects_runs_below_two(capsys):
    """--runs 0 and --runs 1 are degenerate (no comparison possible).
    Parser should reject at the argparse layer so we don't silently
    short-circuit the gate."""
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(_WRAPPER_PATH), "--runs", "1"],
        capture_output=True,
        text=True,
    )
    # argparse.error() exits with code 2.
    assert proc.returncode == 2
    assert "runs must be >= 2" in (proc.stderr + proc.stdout)
