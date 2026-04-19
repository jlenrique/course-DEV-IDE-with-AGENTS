#!/usr/bin/env python
"""Validate Lesson Planner story specs against repo governance rules."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "docs" / "dev-guide" / "lesson-planner-story-governance.json"
SPRINT_STATUS_PATH = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"

STATUS_RE = re.compile(r"^\*\*Status:\*\*\s*`?([a-z-]+)`?(?:\s.*)?$", re.MULTILINE)
SPRINT_KEY_RE = re.compile(r"^\*\*Sprint key:\*\*\s*`?([0-9]+-[0-9]+-[^`\n]+)`?\s*$", re.MULTILINE)
K_RE = re.compile(r"\bK\s*=\s*(\d+)\b")
RANGE_RE = re.compile(r"(\d+)\s*[–-]\s*(\d+)")


def load_policy() -> dict[str, Any]:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_story_key(story_text: str, story_path: Path) -> str:
    match = SPRINT_KEY_RE.search(story_text)
    if match:
        return match.group(1).strip()
    return story_path.stem


def extract_story_prefix(story_key: str) -> str:
    parts = story_key.split("-")
    if len(parts) < 2:
        raise ValueError(f"Cannot derive story prefix from story key {story_key!r}")
    return "-".join(parts[:2])


def extract_status(story_text: str) -> str | None:
    match = STATUS_RE.search(story_text)
    return match.group(1).strip() if match else None


def extract_gate_mode(story_text: str) -> str | None:
    lowered = story_text.lower()
    if "dual-gate" in lowered:
        return "dual-gate"
    if "single-gate" in lowered:
        return "single-gate"
    return None


def extract_first_k(story_text: str) -> int | None:
    match = K_RE.search(story_text)
    return int(match.group(1)) if match else None


def extract_named_range(story_text: str, label: str) -> tuple[int, int] | None:
    for line in story_text.splitlines():
        if label.lower() not in line.lower():
            continue
        match = RANGE_RE.search(line)
        if match:
            return (int(match.group(1)), int(match.group(2)))
    return None


def extract_target_range(story_text: str) -> tuple[int, int] | None:
    for candidate in (
        "target collecting-test range",
        "target collecting tests",
        "target test range",
        "target range",
        "target ",
    ):
        found = extract_named_range(story_text, candidate)
        if found:
            return found
    return None


def extract_estimated_landing(story_text: str) -> tuple[int, int] | None:
    for candidate in (
        "realistic landing",
        "landing estimate",
        "estimated collecting tests",
    ):
        found = extract_named_range(story_text, candidate)
        if found:
            return found
    return None


def has_t1_readiness_block(story_text: str) -> bool:
    lowered = story_text.lower()
    return "## t1 readiness" in lowered or "### t1 readiness" in lowered


def section_contains_required_fields(story_text: str) -> bool:
    lowered = story_text.lower()
    required_tokens = (
        "gate mode",
        "k floor",
        "target",
        "required readings",
        "scaffold",
    )
    return all(token in lowered for token in required_tokens)


def has_required_readings(story_text: str) -> bool:
    required_paths = (
        "docs/dev-guide/story-cycle-efficiency.md",
        "docs/dev-guide/dev-agent-anti-patterns.md",
        "docs/dev-guide/pydantic-v2-schema-checklist.md",
    )
    return all(path in story_text for path in required_paths)


def has_scaffold_reference(story_text: str) -> bool:
    return (
        "docs/dev-guide/scaffolds/schema-story/" in story_text
        or "scripts/utilities/instantiate_schema_story_scaffold.py" in story_text
    )


def extract_sprint_status(story_key: str) -> str | None:
    if not SPRINT_STATUS_PATH.exists():
        return None
    status_pattern = re.compile(
        rf"^\s{{2}}{re.escape(story_key)}:\s*([a-z-]+)\b(?:\s*#.*)?$",
        re.MULTILINE,
    )
    match = status_pattern.search(load_text(SPRINT_STATUS_PATH))
    return match.group(1).strip() if match else None


def get_historical_deviation(
    rule: dict[str, Any],
    story_status: str | None,
    sprint_status: str | None,
) -> dict[str, Any] | None:
    deviation = rule.get("accepted_historical_deviation")
    if not deviation:
        return None

    allowed_story_status = deviation.get("only_when_story_status", "done")
    if story_status != allowed_story_status:
        return None

    allowed_sprint_status = deviation.get("only_when_sprint_status")
    if allowed_sprint_status and sprint_status != allowed_sprint_status:
        return None

    return deviation


def accepted_historical_value(
    deviation: dict[str, Any] | None,
    key: str,
) -> Any:
    if not deviation:
        return None
    return deviation.get("accepted_values", {}).get(key)


def validate_story(path: Path) -> list[str]:
    story_text = load_text(path)
    story_key = extract_story_key(story_text, path)
    story_prefix = extract_story_prefix(story_key)
    policy = load_policy()
    rule = policy["stories"].get(story_prefix)
    if not rule:
        return [f"{story_key}: no Lesson Planner governance policy found for {story_prefix}"]

    story_status = extract_status(story_text)
    sprint_status = extract_sprint_status(story_key)
    historical_deviation = get_historical_deviation(rule, story_status, sprint_status)

    errors: list[str] = []
    gate_mode = extract_gate_mode(story_text)
    if gate_mode != rule["expected_gate_mode"]:
        accepted_gate_mode = accepted_historical_value(historical_deviation, "gate_mode")
        if accepted_gate_mode != gate_mode:
            errors.append(
                f"{story_key}: gate mode drifted to {gate_mode or 'missing'}; "
                f"expected {rule['expected_gate_mode']}"
            )

    if story_status and sprint_status and story_status != sprint_status:
        errors.append(
            f"{story_key}: story status {story_status!r} is out of sync with "
            f"sprint-status.yaml {sprint_status!r}"
        )

    if rule.get("require_t1_readiness"):
        if not has_t1_readiness_block(story_text):
            if not historical_deviation or not historical_deviation.get(
                "allow_missing_t1_readiness"
            ):
                errors.append(f"{story_key}: missing explicit 'T1 readiness' block")
        elif not section_contains_required_fields(story_text):
            errors.append(f"{story_key}: T1 readiness block is missing one or more required fields")

    if not has_required_readings(story_text):
        errors.append(
            f"{story_key}: required Lesson Planner readings are not all cited "
            "in the story spec"
        )

    if rule.get("require_scaffold") and not has_scaffold_reference(story_text):
        errors.append(f"{story_key}: schema-story scaffold reference is missing")

    k_floor = extract_first_k(story_text)
    expected_k_floor = rule.get("expected_k_floor")
    if expected_k_floor is not None and k_floor != expected_k_floor:
        accepted_k_floor = accepted_historical_value(historical_deviation, "k_floor")
        if accepted_k_floor != k_floor:
            errors.append(
                f"{story_key}: K floor is {k_floor or 'missing'}; "
                f"expected {expected_k_floor}"
            )

    target_range = extract_target_range(story_text)
    expected_target = rule.get("expected_target_range")
    if expected_target is not None:
        expected_tuple = tuple(expected_target)
        if target_range != expected_tuple:
            accepted_target_range = accepted_historical_value(historical_deviation, "target_range")
            accepted_target_tuple = (
                tuple(accepted_target_range) if accepted_target_range is not None else None
            )
            if accepted_target_tuple != target_range:
                errors.append(
                    f"{story_key}: target range is {target_range or 'missing'}; "
                    f"expected {expected_tuple}"
                )
    elif k_floor is not None and target_range is not None:
        min_allowed = math.ceil(k_floor * 1.2)
        max_allowed = math.floor(k_floor * 1.5)
        if target_range[0] < min_allowed or target_range[1] > max_allowed:
            errors.append(
                f"{story_key}: target range {target_range} sits outside the "
                "allowed 1.2x-1.5x K window "
                f"({min_allowed}-{max_allowed})"
            )

    estimated_landing = extract_estimated_landing(story_text)
    if k_floor is not None and estimated_landing is not None:
        max_allowed = math.floor(k_floor * 1.5)
        if estimated_landing[1] > max_allowed and (
            not historical_deviation
            or not historical_deviation.get("allow_estimated_landing_cap_violation")
        ):
            errors.append(
                f"{story_key}: estimated landing {estimated_landing} exceeds "
                "the allowed 1.5x K cap "
                f"({max_allowed})"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "story_file",
        type=Path,
        help="Path to the Lesson Planner story markdown file",
    )
    args = parser.parse_args()

    errors = validate_story(args.story_file.resolve())
    if errors:
        print("Lesson Planner governance validation FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Lesson Planner governance validation PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
