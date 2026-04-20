"""Validate the Prompt 2 source-directory scan gate artifact.

Fail-closed guard for Marcus's scan-first source-authority-map workflow:
the numbered scan table with operator-assigned roles must exist before the
final source authority map is drafted.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

ALLOWED_ROLES = frozenset({"primary", "validation", "supplementary", "skip"})
_ROW_RE = re.compile(
    r"^\|\s*(?P<row>\d+)\s*\|\s*(?P<file>.+?)\s*\|\s*(?P<proposed>.+?)\s*\|"
    r"\s*(?P<assigned>.+?)\s*\|\s*(?P<note>.+?)\s*\|$"
)
_STATUS_RE = re.compile(
    r"^\s*operator_assignment_status:\s*(?P<status>.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_DIRECTORY_RE = re.compile(
    r"^\s*scanned_directory:\s*(?P<path>.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def validate_source_directory_scan_gate(scan_path: Path) -> dict[str, Any]:
    """Validate that the scan artifact is approved and contains numbered rows."""
    if not scan_path.is_file():
        return {
            "valid": False,
            "reason": f"File not found: {scan_path}",
            "issues": [f"source-directory-scan.md not found at {scan_path}"],
        }

    try:
        content = scan_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "valid": False,
            "reason": f"Read error: {exc}",
            "issues": [f"Cannot read {scan_path}: {exc}"],
        }

    issues: list[str] = []

    status_matches = _STATUS_RE.findall(content)
    if not status_matches:
        issues.append("Missing operator_assignment_status marker")
    else:
        status = status_matches[-1].strip().lower()
        if status != "approved":
            issues.append(
                "operator_assignment_status must be approved before source-authority-map drafting"
            )

    directory_matches = _DIRECTORY_RE.findall(content)
    if not directory_matches:
        issues.append("Missing scanned_directory marker")
        scanned_directory = None
    else:
        scanned_directory = directory_matches[-1].strip()

    row_matches: list[re.Match[str]] = []
    numbered_rows: list[int] = []
    for line in content.splitlines():
        match = _ROW_RE.match(line)
        if match is None:
            continue
        row_matches.append(match)
        row_number = int(match.group("row"))
        numbered_rows.append(row_number)

        for field_name in ("file", "note"):
            if not match.group(field_name).strip():
                issues.append(f"Row {row_number}: {field_name} must be non-empty")

        for field_name in ("proposed", "assigned"):
            value = match.group(field_name).strip().lower()
            if value not in ALLOWED_ROLES:
                issues.append(
                    f"Row {row_number}: {field_name}_role must be one of {sorted(ALLOWED_ROLES)}"
                )

    if not numbered_rows:
        issues.append("No numbered scan rows found")
    else:
        expected = list(range(1, len(numbered_rows) + 1))
        if numbered_rows != expected:
            issues.append(
                f"Scan row numbers must be contiguous starting at 1; got {numbered_rows}"
            )

    if row_matches and not any(
        match.group("assigned").strip().lower() == "primary"
        for match in row_matches
    ):
        issues.append("At least one operator-assigned primary row is required")

    if scanned_directory:
        scanned_path = Path(scanned_directory)
        if scanned_path.is_dir():
            actual_files = {
                item.name
                for item in scanned_path.iterdir()
                if item.is_file()
            }
            listed_files = {
                Path(match.group("file").strip()).name
                for match in row_matches
            }
            if listed_files != actual_files:
                issues.append(
                    "Scan rows must cover every file in scanned_directory exactly once"
                )

    return {
        "valid": len(issues) == 0,
        "reason": "Valid" if not issues else f"{len(issues)} issues found",
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate source-directory-scan.md before Prompt 2 map drafting."
    )
    parser.add_argument(
        "--scan-path",
        type=Path,
        required=True,
        help="Path to source-directory-scan.md",
    )
    args = parser.parse_args(argv)

    result = validate_source_directory_scan_gate(args.scan_path)
    if result["valid"]:
        print("VALID: source-directory-scan.md passes gate validation")
        return 0

    print(f"INVALID: {result['reason']}")
    for issue in result["issues"]:
        print(f"  - {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
