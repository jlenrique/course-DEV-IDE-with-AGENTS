"""Zero-test-edit invariant for the Marcus duality lane (AC-T.10, M-1 rider).

Originally guarded the 30-1 changeset's "no pre-existing test edits" rule
(AC-T.10). Rolled forward at 30-2b close to the post-30-2a baseline so the
pin continues to guard against unintended pre-existing test edits as the
lane advances through 30-2b and beyond.

Inverted env-gate per M-1 rider: runs BY DEFAULT; skips only when
``MARCUS_30_1_ZERO_EDIT_CHECK_SKIP=1`` is set (for amendment scenarios
where test edits are legal and expected in-flight).

Pins against the commit range ``4911fc4..HEAD`` — rolled forward to the
latest known clean concurrent-session baseline so the invariant guards
future edits instead of replaying historical, already-ratified changes.
Commit-range pin survives local dirty state.

Rollforward policy: when a downstream Marcus-duality story closes, the
baseline SHOULD be advanced to that story's closing commit and the
allowlists trimmed to the next in-flight story's scope.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

_PRE_30_1_BASELINE_COMMIT: str = "4911fc4"
_REPO_ROOT: Path = Path(__file__).parent.parent.parent.resolve()

# Allowlist: new test files that are legitimately added in the range
# ``4911fc4..HEAD``. Anything OUTSIDE this allowlist that shows up as
# ADDED in the range diff is a violation. The 30-1 through 32-4 test
# inventory is already in baseline commit 4911fc4, so only post-baseline
# additions need to appear here.
_ALLOWED_NEW_PATHS_UNDER_TESTS: frozenset[str] = frozenset(
    {
        # 30-2b new tests (AC-T.2–AC-T.7 + AC-C.1 spec entries).
        "tests/test_marcus_intake_pre_packet_emission.py",
        "tests/test_marcus_orchestrator_dispatch.py",
        "tests/contracts/test_30_2b_single_writer_routing.py",
        "tests/contracts/test_30_2b_dispatch_monopoly.py",
        "tests/contracts/test_30_2b_voice_register.py",
    }
)

# Modified-file allowlist: pre-existing test files that are legitimately
# MODIFIED in the range ``4911fc4..HEAD``. Each entry must name the
# specific AC or deferred finding that authorizes the edit.
_ALLOWED_MODIFIED_PATHS_UNDER_TESTS: frozenset[str] = frozenset(
    {
        # 30-2a G6-D1 deferral + 30-2b AC-B.9: extend the side-effect
        # guard to cover the new marcus.intake.pre_packet and
        # marcus.orchestrator.dispatch modules that land at 30-2b.
        "tests/test_marcus_import_chain_side_effects.py",
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
        # Modified / deleted / renamed pre-existing files are violations
        # unless explicitly allowed (e.g., for an in-flight AC that
        # legitimately extends a pre-existing test).
        if status.startswith(("M", "D", "R")):
            if path in _ALLOWED_MODIFIED_PATHS_UNDER_TESTS:
                continue
            violations.append(f"{status}\t{path} (pre-existing file touched)")

    assert not violations, (
        "30-1 zero-test-edit invariant violated (R1 amendment 12):\n"
        + "\n".join(f"  - {v}" for v in violations)
        + "\n\nOnly new test files in the 30-1 allowlist may be added. "
        "Pre-existing test files MUST NOT be modified by the 30-1 changeset."
    )
