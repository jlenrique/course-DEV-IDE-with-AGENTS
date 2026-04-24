"""Tests for Story 18-5 Discovery — Podcasts & Audio Content.

The deliverable of Story 18-5 is a planning artifact
(`_bmad-output/planning-artifacts/discovery-podcasts-audio-content.md`).
These two tests enforce the single-gate K>=2 contract locked at sprint
green-light 2026-04-24:

  1. **Parity** — the discovery document covers all seven goals listed in
     the Story 18-5 spec under `## Goals`.
  2. **Link-validity** — every internal repository reference in the
     discovery document resolves to an existing file.

External links (http/https) are NOT verified here — link rot is a
deployment-layer concern, not a spec-compliance concern.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_DISCOVERY_DOC = (
    _ROOT
    / "_bmad-output"
    / "planning-artifacts"
    / "discovery-podcasts-audio-content.md"
)


REQUIRED_GOAL_HEADINGS = [
    "Goal 1 — Audio content type taxonomy",
    "Goal 2 — Script structure",
    "Goal 3 — Agent role matrix",
    "Goal 4 — Production requirements",
    "Goal 5 — Output formats",
    "Goal 6 — Descript integration",
    "Goal 7 — Workflow family definition",
]


def test_discovery_doc_exists() -> None:
    assert _DISCOVERY_DOC.is_file(), (
        f"Discovery document must exist at {_DISCOVERY_DOC}"
    )


def test_discovery_covers_all_seven_goals() -> None:
    """Parity check: every goal listed in Story 18-5's AC-1 must appear as
    a level-2 heading in the discovery document."""
    text = _DISCOVERY_DOC.read_text(encoding="utf-8")
    missing: list[str] = []
    for heading in REQUIRED_GOAL_HEADINGS:
        pattern = f"## {heading}"
        if pattern not in text:
            missing.append(heading)
    assert not missing, (
        f"Discovery document is missing required goal sections: {missing}. "
        f"AC-1 requires all seven goals from Story 18-5 be addressed."
    )


def test_discovery_covers_required_audio_content_types() -> None:
    """AC-2: taxonomy must include at least five content types."""
    text = _DISCOVERY_DOC.read_text(encoding="utf-8")
    required_types = [
        "Lecture podcast",
        "Interview / dialogue",
        "Case discussion audio",
        "Audio summary / recap",
        "Module bumper / intro",
    ]
    missing = [t for t in required_types if t not in text]
    assert not missing, (
        f"Discovery taxonomy must cover at least: {required_types}. "
        f"Missing: {missing}"
    )


def test_discovery_defines_three_script_structures() -> None:
    """AC-3: monologue, multi-voice dialogue, interview format."""
    text = _DISCOVERY_DOC.read_text(encoding="utf-8")
    assert "### Monologue" in text
    assert "### Dialogue (multi-voice)" in text
    assert "### Interview" in text


def test_discovery_internal_links_resolve() -> None:
    """Link-validity check: every internal markdown link (path starts with
    .. or /, excluding http/https) must resolve to an existing file or
    directory.

    External links are intentionally NOT verified (link rot is a
    deployment-layer concern).
    """
    text = _DISCOVERY_DOC.read_text(encoding="utf-8")
    # Match `[text](path)` but skip `[text](http...)` / `[text](#anchor)`.
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    unresolved: list[str] = []
    for match in link_pattern.finditer(text):
        target = match.group(1).strip()
        # Strip any anchor fragment
        path_part = target.split("#", 1)[0].strip()
        if not path_part:
            continue
        # Skip external links
        if path_part.startswith(("http://", "https://", "mailto:")):
            continue
        # Skip pure anchors
        if path_part.startswith("#"):
            continue
        # Resolve against the discovery doc's parent directory (repo-relative
        # link resolution).
        resolved = (_DISCOVERY_DOC.parent / path_part).resolve()
        if not resolved.exists():
            unresolved.append(
                f"{target!r} -> {resolved} (referenced in discovery doc)"
            )
    assert not unresolved, (
        "Discovery doc has internal references that do not resolve:\n  "
        + "\n  ".join(unresolved)
    )


# Sanity probe — not a new K-counted test, just guards against accidental
# deletion of the sprint-level green-light metadata in the doc.
def test_discovery_carries_sprint_level_metadata() -> None:
    text = _DISCOVERY_DOC.read_text(encoding="utf-8")
    assert "18-5 Discovery" in text
    assert "Authored:" in text
    assert "Sprint:** #2" in text
