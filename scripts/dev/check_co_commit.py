"""Co-commit invariant: staged source changes must include staged test changes.

A commit that modifies production code under ``skills/`` or ``scripts/`` must
also stage at least one file under a test directory. The invariant formalizes
the operator preference 'regression-proof tests' (see
``memory/feedback_regression_proof_tests.md``): behavior changes ship with
their guard tests in the same commit, or not at all.

Scope: only ``.py`` files are considered "production code" for this check —
pure doc/yaml/assets changes in ``skills/`` do not trigger the requirement.

Run via pre-commit hook. Exits non-zero with a message when the invariant is
violated; exits zero when satisfied or when no source code is staged.
"""

from __future__ import annotations

import subprocess
import sys

SOURCE_ROOTS = ("skills/", "scripts/")
TEST_MARKERS = ("tests/", "/tests/")


def staged_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        # Git error — don't block commit; report and pass.
        print(f"check_co_commit: git diff failed: {result.stderr}", file=sys.stderr)
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    files = staged_files()
    if not files:
        return 0

    source_code_changed = [
        f for f in files
        if f.endswith(".py")
        and any(f.startswith(root) for root in SOURCE_ROOTS)
        and not any(marker in f for marker in TEST_MARKERS)
    ]
    if not source_code_changed:
        return 0

    test_touched = any(
        any(marker in f for marker in TEST_MARKERS) for f in files
    )
    if test_touched:
        return 0

    print("CO-COMMIT INVARIANT VIOLATED:", file=sys.stderr)
    print("  Production source files were staged without any test file changes:", file=sys.stderr)
    for f in source_code_changed:
        print(f"    {f}", file=sys.stderr)
    print(
        "",
        "Every behavior-changing commit must travel with its test update in the",
        "same commit. Options:",
        "  1. Update or add tests that guard the new behavior, OR",
        "  2. Update tests that previously guarded the old behavior.",
        "",
        "If the change genuinely requires no test update (rare: pure rename with",
        "no behavior change, internal refactor with full existing coverage), stage",
        "a no-op test touch and explain in the commit message.",
        sep="\n",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
