from __future__ import annotations

from pathlib import Path

import scripts.utilities.validate_lesson_planner_story_governance as governance_validator
from scripts.utilities.validate_lesson_planner_story_governance import validate_story


def write_story(tmp_path: Path, sprint_key: str, body: str) -> Path:
    story_path = tmp_path / f"{sprint_key}.md"
    story_path.write_text(body, encoding="utf-8")
    return story_path


def test_validator_accepts_expected_single_gate_story(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(governance_validator, "extract_sprint_status", lambda _: None)

    story = write_story(
        tmp_path,
        "31-3-registries",
        """# Story 31-3

**Status:** ready-for-dev
**Sprint key:** `31-3-registries`

## T1 Readiness

- gate mode: single-gate
- K floor: `K=8`
- target collecting-test range: `10-12`
- required readings:
  - docs/dev-guide/story-cycle-efficiency.md
  - docs/dev-guide/dev-agent-anti-patterns.md
  - docs/dev-guide/pydantic-v2-schema-checklist.md
- scaffold required: yes
- scaffold path: docs/dev-guide/scaffolds/schema-story/
""",
    )

    assert validate_story(story) == []


def test_validator_flags_gate_and_k_drift(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(governance_validator, "extract_sprint_status", lambda _: None)

    story = write_story(
        tmp_path,
        "31-3-registries",
        """# Story 31-3

**Status:** ready-for-dev
**Sprint key:** `31-3-registries`

This story runs dual-gate.

## T1 Readiness

- gate mode: dual-gate
- K floor: `K=15`
- target collecting-test range: `18-23`
- required readings:
  - docs/dev-guide/story-cycle-efficiency.md
  - docs/dev-guide/dev-agent-anti-patterns.md
  - docs/dev-guide/pydantic-v2-schema-checklist.md
- scaffold required: yes
- scaffold path: docs/dev-guide/scaffolds/schema-story/

Realistic landing: ~58-65 collecting tests.
""",
    )

    errors = validate_story(story)

    assert any("gate mode drifted" in error for error in errors)
    assert any("K floor is 15; expected 8" in error for error in errors)
    assert any("target range is (18, 23); expected (10, 12)" in error for error in errors)
    assert any("estimated landing (58, 65) exceeds" in error for error in errors)


def test_validator_accepts_documented_historical_deviation_for_done_story(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(governance_validator, "extract_sprint_status", lambda _: "done")

    story = write_story(
        tmp_path,
        "31-3-registries",
        """# Story 31-3

**Status:** done
**Sprint key:** `31-3-registries`

This story runs dual-gate.

- K floor: `K=15`
- target collecting-test range: `18-23`
- required readings:
  - docs/dev-guide/story-cycle-efficiency.md
  - docs/dev-guide/dev-agent-anti-patterns.md
  - docs/dev-guide/pydantic-v2-schema-checklist.md
- scaffold required: yes
- scaffold path: docs/dev-guide/scaffolds/schema-story/

Realistic landing: ~58-65 collecting tests.
""",
    )

    assert validate_story(story) == []


def test_validator_requires_t1_readiness_block(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(governance_validator, "extract_sprint_status", lambda _: None)

    story = write_story(
        tmp_path,
        "32-2-weather-band",
        """# Story 32-2

**Status:** ready-for-dev
**Sprint key:** `32-2-weather-band`

This cites docs/dev-guide/story-cycle-efficiency.md and
docs/dev-guide/dev-agent-anti-patterns.md and
docs/dev-guide/pydantic-v2-schema-checklist.md and
docs/dev-guide/scaffolds/schema-story/
""",
    )

    errors = validate_story(story)

    assert any("missing explicit 'T1 readiness' block" in error for error in errors)
