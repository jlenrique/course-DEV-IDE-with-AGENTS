"""AC-C.1 — Voice Register invariant for 30-2b source files.

Source-grep guard: no Marcus-duality routing tokens in raise-message
string literals across 30-2b's new/modified surfaces. The 30-1 facade
Voice Register (see ``marcus/facade.py`` module docstring) requires
Maya-facing error strings stay generic; hyphenated internal-routing
tokens belong on attribute-scoped fields (e.g.,
``UnauthorizedFacadeCallerError.offending_writer``), not on
``args[0]`` / ``str(err)``.

Scope: the 30-2b authored files that could surface Maya-facing strings:
* ``marcus/intake/pre_packet.py``
* ``marcus/orchestrator/dispatch.py``

Approach: AST walk each file, inspect every :class:`ast.Raise` node's
exception-constructor argument list. If an argument is a string literal
containing a forbidden token without a ``# noqa: VOICE-REGISTER``
comment on the same or previous line, that's a violation.

Not a 30-1 rescope: the 30-1 ``UnauthorizedFacadeCallerError`` message
is already Maya-safe, and 30-2b does not introduce a new exception
type. This test prevents regression if 30-2b grows a new raise-site
that inlines a routing token.
"""

from __future__ import annotations

import ast
from pathlib import Path

_GUARDED_FILES: tuple[str, ...] = (
    "marcus/intake/pre_packet.py",
    "marcus/orchestrator/dispatch.py",
    # 30-3a additions:
    "marcus/orchestrator/loop.py",
    "marcus/orchestrator/stub_dials.py",
    "marcus/facade.py",
)
_FORBIDDEN_TOKENS: tuple[str, ...] = ("marcus-intake", "marcus-orchestrator")


def _iter_string_literals(node: ast.AST) -> list[tuple[str, int]]:
    """Return (literal_value, line_number) for every string literal in ``node``."""
    literals: list[tuple[str, int]] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            literals.append((child.value, getattr(child, "lineno", 0)))
    return literals


def _source_line(source_lines: list[str], lineno: int) -> str:
    # ast line numbers are 1-based.
    if 1 <= lineno <= len(source_lines):
        return source_lines[lineno - 1]
    return ""


def test_no_duality_tokens_in_raise_messages() -> None:
    """AC-C.1 — raise-site string literals do not leak duality routing tokens."""
    repo_root = Path(__file__).parent.parent.parent
    offenders: list[str] = []
    for rel in _GUARDED_FILES:
        path = repo_root / rel
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        source_lines = source.splitlines()
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Raise):
                continue
            exc = node.exc
            if exc is None:
                continue
            for literal, lineno in _iter_string_literals(exc):
                for token in _FORBIDDEN_TOKENS:
                    if token not in literal:
                        continue
                    line = _source_line(source_lines, lineno)
                    if "# noqa: VOICE-REGISTER" in line:
                        continue
                    offenders.append(
                        f"{rel}:{lineno} raises with literal containing "
                        f"forbidden token {token!r}"
                    )

    assert not offenders, (
        "30-2b source files MUST NOT inline Marcus-duality routing tokens "
        "in raise-message string literals (Voice Register, 30-1 facade "
        f"discipline). Offenders: {offenders}. Use attribute-scoped fields "
        "on the exception class instead."
    )
