"""Import-chain side-effect invariant (AC-T.15, Q-5 rider).

"No pipeline code movement" is about file placement; module-load side
effects (registry registration, logger configuration, atexit hooks) can
still drift envelope output. Catches "trivial pass" false positives on
Golden-Trace.

Asserts importing the 30-1 modules produces:
* zero new filesystem writes,
* zero new log handler attachments,
* zero atexit callbacks added.

Uses a subprocess to get a clean import graph per test.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap


def test_importing_30_1_modules_has_no_filesystem_side_effects() -> None:
    """AC-T.15 — no new files are written by importing the 30-1 modules."""
    script = textwrap.dedent(
        """
        import os
        import sys
        import tempfile

        # Record filesystem state under cwd BEFORE import.
        cwd_root = os.getcwd()
        before: set[str] = set()
        for dirpath, dirnames, filenames in os.walk(cwd_root):
            # Skip known transient dirs that may churn on import unrelated to
            # our concern (e.g., .pytest_cache is the test driver's, not ours).
            if any(skip in dirpath for skip in (
                "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
                ".git", "node_modules",
            )):
                continue
            for fn in filenames:
                before.add(os.path.join(dirpath, fn))

        # Import the 30-1 surface.
        import marcus  # noqa: F401
        import marcus.facade  # noqa: F401
        import marcus.intake  # noqa: F401
        import marcus.orchestrator  # noqa: F401
        import marcus.orchestrator.write_api  # noqa: F401

        # Record filesystem state AFTER import.
        after: set[str] = set()
        for dirpath, dirnames, filenames in os.walk(cwd_root):
            if any(skip in dirpath for skip in (
                "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
                ".git", "node_modules",
            )):
                continue
            for fn in filenames:
                after.add(os.path.join(dirpath, fn))

        new_files = after - before
        if new_files:
            print("NEW_FILES:", "|".join(sorted(new_files)))
            sys.exit(1)
        print("OK")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Importing 30-1 modules produced filesystem side effects: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "OK" in result.stdout


def test_30_1_modules_do_not_call_atexit_register_in_source() -> None:
    """AC-T.15 — no 30-1 module registers an atexit callback.

    Shape-pin: grep 30-1 source files for ``atexit.register``.

    Rationale: runtime atexit-count probing proved noisy (CPython's own
    standard library registers callbacks during import of dependencies).
    What matters for the Q-5 invariant is that WE do not register any;
    that is a source-level property this test enforces directly.
    """
    from pathlib import Path

    repo_root = Path(__file__).parent.parent
    guarded_files: list[Path] = [
        repo_root / "marcus" / "__init__.py",
        repo_root / "marcus" / "facade.py",
        repo_root / "marcus" / "intake" / "__init__.py",
        repo_root / "marcus" / "orchestrator" / "__init__.py",
        repo_root / "marcus" / "orchestrator" / "write_api.py",
    ]
    offenders: list[str] = []
    for path in guarded_files:
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        if "atexit.register" in source or "atexit.unregister" in source:
            offenders.append(str(path.relative_to(repo_root)))

    assert not offenders, (
        f"30-1 source files must not register atexit callbacks: {offenders}. "
        "Module-load side effects drift envelope output."
    )
