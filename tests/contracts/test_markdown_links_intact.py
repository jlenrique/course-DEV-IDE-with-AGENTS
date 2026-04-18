"""Markdown link-check on the three files touched by story 26-6 (AC-D.5).

Lightweight in-process checker — resolves every relative markdown link in
the target files and asserts the target exists on disk. External URLs are
skipped (we only validate internal consistency).

Defect class guarded: doc surgery (strip + redirect + new reference doc)
leaves a broken relative link behind. At low doc volume this is easy to
spot; at scale it is easy to miss until the operator clicks.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.utilities.file_helpers import project_root

pytestmark = pytest.mark.trial_critical

# AC-D.5: the three files touched by 26-6 doc surgery.
TARGETS = [
    project_root()
    / "docs"
    / "workflow"
    / "production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md",
    project_root() / "docs" / "workflow" / "archive" / "prompt-pack-preprompt-2026-04.md",
    project_root() / "docs" / "dev-guide" / "marcus-capabilities.md",
]

# Matches `[text](path)` — greedy text, non-greedy path.
_LINK_RE = re.compile(r"\[([^\]]+?)\]\(([^)]+?)\)")


def _is_external(link: str) -> bool:
    """Treat http(s), mailto, and protocol-relative links as out-of-scope."""
    return (
        link.startswith("http://")
        or link.startswith("https://")
        or link.startswith("mailto:")
        or link.startswith("//")
    )


def _strip_anchor(link: str) -> str:
    """Drop trailing `#fragment` for filesystem existence checks."""
    return link.split("#", 1)[0]


def _iter_relative_links(text: str) -> list[str]:
    links: list[str] = []
    for match in _LINK_RE.finditer(text):
        link = match.group(2).strip()
        if not link or _is_external(link):
            continue
        # Reference-style `[label][id]` patterns would not match the URL group.
        links.append(link)
    return links


@pytest.mark.parametrize("target", TARGETS, ids=lambda p: p.name)
def test_markdown_links_resolve(target: Path) -> None:
    """Every relative markdown link in the target file must resolve to a
    file that exists on disk."""
    assert target.is_file(), f"Target doc missing: {target}"
    text = target.read_text(encoding="utf-8")
    broken: list[tuple[str, str]] = []
    for raw_link in _iter_relative_links(text):
        resolved = _strip_anchor(raw_link)
        if not resolved:
            # Anchor-only (`#foo`) — in-page reference; skip existence check.
            continue
        candidate = (target.parent / resolved).resolve()
        if not candidate.exists():
            broken.append((raw_link, str(candidate)))
    assert not broken, (
        f"Broken relative links in {target.name}:\n"
        + "\n".join(f"  {raw} -> {resolved}" for raw, resolved in broken)
    )
