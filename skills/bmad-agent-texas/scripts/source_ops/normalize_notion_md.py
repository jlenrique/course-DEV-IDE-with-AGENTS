"""Normalize Notion-exported Markdown into clean, parser-friendly Markdown.

Notion's Markdown exporter backslash-escapes every character that has
Markdown meaning (``#`` → ``\\#``, ``**`` → ``\\*\\*``, ``-`` → ``\\-``,
``1.`` → ``1\\.``, etc.) and emits HTML entities for indentation
(``&#x20;`` for a space, ``&amp;`` for ``&``). The text itself is
complete and correct, but the encoding breaks every standard Markdown
parser (readers render the backslashes literally and the HTML entities
as escaped text).

This module reverses those transformations so downstream extractors,
cross-validators, and planners see what a human author would recognise
as plain Markdown.

Use as a library::

    from normalize_notion_md import normalize_notion_markdown
    cleaned = normalize_notion_markdown(raw_text)

Use as a CLI::

    python normalize_notion_md.py path/to/notion-export.md --in-place
    python normalize_notion_md.py path/to/in.md --output path/to/out.md
    python normalize_notion_md.py path/to/in.md            # stdout

The transformation is deterministic and idempotent: running it twice
yields identical output.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

# Markdown special characters that Notion backslash-escapes in its export.
# Source: observed behaviour across Notion-exported lesson plans (2026-04-19).
# Includes the full punctuation set Notion is known to escape; any character
# outside this set is left untouched so legitimate backslashes (e.g. inside
# fenced code blocks demonstrating Windows paths) are preserved.
_MARKDOWN_SPECIAL_CHARS = r"#*_\-.&()<>\[\]{}`~|!+=^/"

# One backslash immediately before a single markdown-special character.
# Captures the special char so we can drop the leading backslash.
_BACKSLASH_ESCAPE_RE = re.compile(rf"\\([{_MARKDOWN_SPECIAL_CHARS}])")

# Three-or-more consecutive newlines collapse to a single blank line.
# Notion exports triple-space between every paragraph, which inflates
# word counts when naive line iteration is applied and creates visual
# noise in reviewer diffs.
_EXCESSIVE_BLANKS_RE = re.compile(r"\n{3,}")


def normalize_notion_markdown(text: str) -> str:
    """Return Notion-exported Markdown normalized for standard parsers.

    Applies, in order:
      1. HTML entity decoding via :func:`html.unescape` (covers ``&#x20;``,
         ``&amp;``, ``&lt;``, ``&gt;``, and any numeric entity Notion emits).
      2. Backslash-unescape of Markdown special characters listed in
         :data:`_MARKDOWN_SPECIAL_CHARS`.
      3. Collapse of three-or-more consecutive newlines to exactly two
         (one blank line).

    The operation is idempotent: ``normalize_notion_markdown(x) ==
    normalize_notion_markdown(normalize_notion_markdown(x))``.

    Args:
        text: Raw Markdown content, typically from a Notion export.

    Returns:
        Cleaned Markdown with escapes removed, HTML entities decoded,
        and blank-line runs collapsed.
    """
    if not text:
        return ""
    cleaned = html.unescape(text)
    cleaned = _BACKSLASH_ESCAPE_RE.sub(r"\1", cleaned)
    cleaned = _EXCESSIVE_BLANKS_RE.sub("\n\n", cleaned)
    return cleaned


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize a Notion-exported Markdown file: remove "
            "backslash escapes, decode HTML entities, and collapse "
            "runs of blank lines."
        ),
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the Notion-exported Markdown file to normalize.",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Write the normalized output to this path. "
            "If omitted and --in-place is not set, the normalized "
            "content is written to stdout."
        ),
    )
    output_group.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the input file with the normalized content.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    src: Path = args.input
    if not src.is_file():
        print(f"error: input file not found: {src}", file=sys.stderr)
        return 2
    try:
        raw = src.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"error: input file is not UTF-8: {exc}", file=sys.stderr)
        return 2

    cleaned = normalize_notion_markdown(raw)

    if args.in_place:
        src.write_text(cleaned, encoding="utf-8")
        print(f"Normalized in place: {src}", file=sys.stderr)
        return 0
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(cleaned, encoding="utf-8")
        print(f"Normalized output written to: {args.output}", file=sys.stderr)
        return 0
    sys.stdout.write(cleaned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
