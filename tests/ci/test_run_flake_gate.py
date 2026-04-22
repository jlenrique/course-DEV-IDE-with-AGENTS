"""Tests for PDG-3 flake-gate wrapper (scripts/ci/run_flake_gate.py).

Covers the pytest-summary parser — the only non-trivial logic in the wrapper
(subprocess invocation is a thin orchestration layer exercised by the 3x
local runs on commit and by the GitHub Actions workflow itself).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_WRAPPER_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "ci" / "run_flake_gate.py"
)
_spec = importlib.util.spec_from_file_location("run_flake_gate", _WRAPPER_PATH)
assert _spec is not None and _spec.loader is not None
run_flake_gate = importlib.util.module_from_spec(_spec)
sys.modules["run_flake_gate"] = run_flake_gate
_spec.loader.exec_module(run_flake_gate)


@pytest.mark.parametrize(
    "summary_line, expected",
    [
        (
            "12 passed, 2143 deselected in 1.55s",
            (12, 0, 0, 0, 0, 0, 2143),
        ),
        (
            "1478 passed, 6 skipped, 2 xfailed, 2 deselected in 30.22s",
            (1478, 0, 0, 6, 2, 0, 2),
        ),
        (
            "5 passed, 1 failed, 2 errors in 0.50s",
            (5, 1, 2, 0, 0, 0, 0),
        ),
        (
            "10 passed, 1 xpassed in 0.10s",
            (10, 0, 0, 0, 0, 1, 0),
        ),
    ],
)
def test_parse_summary_extracts_counts(summary_line, expected):
    stdout = f"some noise\n{summary_line}\n"
    assert run_flake_gate._parse_summary(stdout) == expected


def test_parse_summary_reads_last_summary_line_wins():
    # pytest-xdist / rerunfailures can print multiple summary lines; the
    # terminal one is authoritative. Parser reverse-scans, so most-recent wins.
    stdout = (
        "3 passed, 1 failed in 0.01s\n"
        "noise\n"
        "12 passed in 1.55s\n"
    )
    passed, failed, errors, *_ = run_flake_gate._parse_summary(stdout)
    assert (passed, failed, errors) == (12, 0, 0)


def test_parse_summary_returns_zero_tuple_when_no_match():
    assert run_flake_gate._parse_summary("no summary here\n") == (0, 0, 0, 0, 0, 0, 0)


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
    # Signature compares full run outcome; two runs with identical signatures
    # are considered flake-free.
    assert outcome.signature() == (0, 12, 0, 0, 0, 0, 0, 2143)


def test_run_outcome_signature_differs_on_exit_code():
    a = run_flake_gate.RunOutcome(0, 12, 0, 0, 0, 0, 0, 2143, "")
    b = run_flake_gate.RunOutcome(1, 12, 0, 0, 0, 0, 0, 2143, "")
    assert a.signature() != b.signature()


def test_run_outcome_signature_differs_on_failed_count():
    a = run_flake_gate.RunOutcome(0, 12, 0, 0, 0, 0, 0, 2143, "")
    b = run_flake_gate.RunOutcome(0, 11, 1, 0, 0, 0, 0, 2143, "")
    assert a.signature() != b.signature()
