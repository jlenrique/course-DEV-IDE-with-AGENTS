"""Zero-test-edit invariant for the Marcus duality lane (AC-T.10, M-1 rider).

## Current state: DORMANT

Originally guarded Story 30-1's "no pre-existing test edits" rule during the
high-risk Marcus-duality refactor. Rolled forward at 30-2b close (commit
``4911fc4``) to keep protecting while 30-2x stories continued landing.

**All 30-x stories are closed** (30-1 → 2026-04-19; 30-2a, 30-2b → same lane
closed). Subsequent work (Epic 33, Sprint #1 stories including §7.1 Irene
Pass 2 template) legitimately adds test files across the repo; the pinned
``4911fc4`` baseline + frozen allowlists caused this guard to flag every
post-baseline test file addition as a "violation," even though no 30-x story
was in-flight to protect.

This guard is now **dormant** — it skips by default and only runs when an
operator explicitly arms it for a future Marcus-duality or similarly
scoped refactor.

## Re-arming for a future sensitive refactor

When a future story wants this same defensive discipline:

1. Set ``_PRE_30_1_BASELINE_COMMIT`` to the commit immediately *before* that
   story's first commit.
2. Populate ``_ALLOWED_NEW_PATHS_UNDER_TESTS`` with the test files the
   story is permitted to add.
3. Populate ``_ALLOWED_MODIFIED_PATHS_UNDER_TESTS`` with the test files the
   story is permitted to modify (each entry must name its AC / deferred
   finding).
4. Set ``MARCUS_DUALITY_GUARD_ACTIVE=1`` in the relevant CI job / local
   environment for the duration of that story's work.
5. Clear the env var + re-dormant the guard at story close.

## Back-compat env var

The original ``MARCUS_30_1_ZERO_EDIT_CHECK_SKIP=1`` still skips (kept for
any ambient scripts that set it). With the new dormant-by-default posture,
setting it is a no-op.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

_PRE_30_1_BASELINE_COMMIT: str = "4911fc4"
_REPO_ROOT: Path = Path(__file__).parent.parent.parent.resolve()

# Allowlist: new test files legitimately added in the range
# ``{_PRE_30_1_BASELINE_COMMIT}..HEAD`` when the guard is armed.
# Frozen at 30-2b scope — a future re-arm updates this in lockstep.
_ALLOWED_NEW_PATHS_UNDER_TESTS: frozenset[str] = frozenset(
    {
        "tests/test_marcus_intake_pre_packet_emission.py",
        "tests/test_marcus_orchestrator_dispatch.py",
        "tests/contracts/test_30_2b_single_writer_routing.py",
        "tests/contracts/test_30_2b_dispatch_monopoly.py",
        "tests/contracts/test_30_2b_voice_register.py",
    }
)

# Modified-file allowlist: pre-existing test files legitimately MODIFIED
# in the range when the guard is armed. Each entry names the AC / deferred
# finding that authorizes the edit.
_ALLOWED_MODIFIED_PATHS_UNDER_TESTS: frozenset[str] = frozenset(
    {
        "tests/test_marcus_import_chain_side_effects.py",
    }
)


def _guard_is_dormant() -> bool:
    """Guard runs only when explicitly armed via MARCUS_DUALITY_GUARD_ACTIVE=1.

    Back-compat: MARCUS_30_1_ZERO_EDIT_CHECK_SKIP=1 also forces skip.
    """
    if os.environ.get("MARCUS_30_1_ZERO_EDIT_CHECK_SKIP") == "1":
        return True
    return os.environ.get("MARCUS_DUALITY_GUARD_ACTIVE") != "1"


def test_no_preexisting_test_files_modified_in_30_1() -> None:
    """AC-T.10 — ``git diff {baseline}..HEAD -- tests/`` contains no
    pre-existing file edits outside the allowlists.

    Dormant by default (see module docstring for re-arm procedure).
    Commit-range pin (not working-tree diff) — survives local dirty state.

    Dormant check is re-evaluated at call time (not collection time) so
    env vars set via fixtures or dynamic CI activation take effect.
    """
    if _guard_is_dormant():
        pytest.skip(
            "30-1 zero-test-edit guard is dormant (all 30-x stories closed); "
            "set MARCUS_DUALITY_GUARD_ACTIVE=1 + update baseline/allowlists in "
            "this file to re-arm for a future Marcus-duality refactor"
        )
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
        if status.startswith("A"):
            if path not in _ALLOWED_NEW_PATHS_UNDER_TESTS:
                violations.append(f"{status}\t{path} (new file outside allowlist)")
            continue
        if status.startswith(("M", "D", "R")):
            if path in _ALLOWED_MODIFIED_PATHS_UNDER_TESTS:
                continue
            violations.append(f"{status}\t{path} (pre-existing file touched)")

    assert not violations, (
        "Marcus-duality zero-test-edit invariant violated:\n"
        + "\n".join(f"  - {v}" for v in violations)
        + "\n\nOnly new test files in the allowlist may be added. "
        "Pre-existing test files MUST NOT be modified by the armed changeset."
    )
