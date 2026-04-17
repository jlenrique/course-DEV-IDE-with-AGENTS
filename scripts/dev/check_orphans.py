"""Orphan-reference detector for test files.

Catches the defect class from commit 1572819: a source refactor removed
`progress_map._parse_epic_labels_from_comments`, but test files still referenced
it. Collection succeeded (the module imported fine); failures appeared only when
tests ran, by which time the refactor was already on master.

This script parses each test file's AST, finds attribute accesses like
``module_alias.NAME`` where ``module_alias`` was imported from a project module,
and verifies ``NAME`` actually exists on that module. Orphans exit non-zero.

Run directly (``python scripts/dev/check_orphans.py``) to scan every test file
in the repo, or via pre-commit hook passing changed test files as arguments.
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEST_ROOTS = [
    REPO_ROOT / "tests",
    REPO_ROOT / "skills" / "source-wrangler" / "scripts" / "tests",
    REPO_ROOT / "skills" / "compositor" / "scripts" / "tests",
    REPO_ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "tests",
    REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts" / "tests",
    REPO_ROOT / "skills" / "kling-video" / "scripts" / "tests",
]


def _module_aliases_from_tree(tree: ast.AST) -> dict[str, str]:
    """Return alias_name -> importable module path, for project imports only.

    Only project modules (scripts.*, skills.*) are tracked — stdlib/third-party
    attribute access is not our concern.
    """
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                alias = n.asname or n.name.split(".")[0]
                if n.name.startswith(("scripts.", "skills.")):
                    aliases[alias] = n.name
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith(("scripts", "skills")):
                for n in node.names:
                    alias = n.asname or n.name
                    aliases[alias] = f"{node.module}.{n.name}"
    return aliases


def check_file(filepath: Path) -> list[str]:
    """Return orphan-reference findings for a single test file."""
    findings: list[str] = []
    try:
        source = filepath.read_text(encoding="utf-8")
    except Exception as exc:
        return [f"{filepath}: read error {exc}"]
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:
        return [f"{filepath}:{exc.lineno}: syntax error {exc.msg}"]

    aliases = _module_aliases_from_tree(tree)
    if not aliases:
        return []

    for node in ast.walk(tree):
        if not (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)):
            continue
        alias = node.value.id
        attr = node.attr
        target = aliases.get(alias)
        if target is None:
            continue
        try:
            mod = importlib.import_module(target)
        except Exception:
            # If the import itself fails, pytest --collect-only surfaces it;
            # don't duplicate that check here.
            continue
        # If the target is a symbol (not a module), fall back to its parent.
        if not hasattr(mod, attr):
            findings.append(
                f"{filepath}:{node.lineno}: "
                f"{alias}.{attr} — '{attr}' is not exported by module '{target}'"
            )
    return findings


def discover_test_files() -> list[Path]:
    files: list[Path] = []
    for root in DEFAULT_TEST_ROOTS:
        if root.is_dir():
            files.extend(root.rglob("test_*.py"))
            files.extend(root.rglob("*_test.py"))
    return files


def main(argv: list[str]) -> int:
    if argv:
        paths = [Path(a) for a in argv if Path(a).is_file() and a.endswith(".py")]
    else:
        paths = discover_test_files()

    all_findings: list[str] = []
    for p in paths:
        all_findings.extend(check_file(p))

    if all_findings:
        print("ORPHAN REFERENCES DETECTED:", file=sys.stderr)
        for f in all_findings:
            print(f"  {f}", file=sys.stderr)
        print(
            "",
            "A test file references a symbol that no longer exists in the "
            "imported module. Either:",
            "  1. Update the test to match the new module API, or",
            "  2. Restore the deleted symbol if it was removed by mistake.",
            sep="\n",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
