"""Zero-test-edit invariant for 30-1 (AC-T.10, M-1 rider).

The 30-1 changeset does NOT modify any pre-existing file under
``tests/`` — only adds new test files + the coverage-baseline fixture.
Inverted env-gate per M-1 rider: runs BY DEFAULT; skips only when
``MARCUS_30_1_ZERO_EDIT_CHECK_SKIP=1`` is set (for amendment scenarios
post-30-2a where test edits become legal).

Pins against the commit range ``d7fd520..HEAD`` — the 29-1 + 32-2
closure commit is the pre-30-1 baseline. Commit-range pin survives local
dirty state.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

_PRE_30_1_BASELINE_COMMIT: str = "d7fd520"
_REPO_ROOT: Path = Path(__file__).parent.parent.parent.resolve()

# Allowlist: the new test files added by 30-1 + the coverage-baseline
# fixture. Anything OUTSIDE this allowlist that shows up as modified in
# the range diff is a violation.
_ALLOWED_NEW_PATHS_UNDER_TESTS: frozenset[str] = frozenset(
    {
        "tests/test_marcus_duality_imports.py",
        "tests/test_marcus_orchestrator_write_api.py",
        "tests/test_marcus_facade_leak_detector.py",
        "tests/test_marcus_negotiator_seam_named.py",
        "tests/test_marcus_facade_roundtrip.py",
        "tests/test_marcus_golden_trace_regression.py",
        "tests/test_marcus_import_chain_side_effects.py",
        "tests/test_marcus_coverage_non_regression.py",
        "tests/contracts/test_no_intake_orchestrator_leak_marcus_duality.py",
        "tests/contracts/test_marcus_single_writer_routing.py",
        "tests/contracts/test_marcus_facade_is_public_surface.py",
        "tests/contracts/test_30_1_zero_test_edits.py",
        "tests/fixtures/coverage_baseline/marcus_pre_30-1.json",
    }
)


@pytest.mark.skipif(
    os.environ.get("MARCUS_30_1_ZERO_EDIT_CHECK_SKIP") == "1",
    reason="MARCUS_30_1_ZERO_EDIT_CHECK_SKIP=1 set (amendment scenario)",
)
def test_no_preexisting_test_files_modified_in_30_1() -> None:
    """AC-T.10 — ``git diff d7fd520..HEAD -- tests/`` contains no pre-existing
    file edits outside the 30-1 allowlist.

    Commit-range pin (not working-tree diff) — survives local dirty state.
    """
    # Check baseline commit is reachable.
    reachable = subprocess.run(
        ["git", "-C", str(_REPO_ROOT), "cat-file", "-e", _PRE_30_1_BASELINE_COMMIT],
        capture_output=True,
        text=True,
        check=False,
    )
    if reachable.returncode != 0:
        pytest.skip(
            f"Baseline commit {_PRE_30_1_BASELINE_COMMIT} not reachable; "
            "zero-edit pin requires the pre-30-1 commit to be present."
        )

    # Get the list of files changed in the range, scoped to tests/.
    diff = subprocess.run(
        [
            "git",
            "-C",
            str(_REPO_ROOT),
            "diff",
            "--name-status",
            f"{_PRE_30_1_BASELINE_COMMIT}..HEAD",
            "--",
            "tests/",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if diff.returncode != 0:
        pytest.skip(
            f"git diff failed; zero-edit pin dormant. stderr={diff.stderr[-200:]}"
        )

    violations: list[str] = []
    for line in diff.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", maxsplit=1)
        if len(parts) != 2:
            continue
        status, path = parts[0], parts[1]
        # Added new files are legal (if in the allowlist).
        if status.startswith("A"):
            if path not in _ALLOWED_NEW_PATHS_UNDER_TESTS:
                violations.append(f"{status}\t{path} (new file outside allowlist)")
            continue
        # Modified / deleted / renamed pre-existing files are violations.
        if status.startswith(("M", "D", "R")):
            violations.append(f"{status}\t{path} (pre-existing file touched)")

    assert not violations, (
        "30-1 zero-test-edit invariant violated (R1 amendment 12):\n"
        + "\n".join(f"  - {v}" for v in violations)
        + "\n\nOnly new test files in the 30-1 allowlist may be added. "
        "Pre-existing test files MUST NOT be modified by the 30-1 changeset."
    )
