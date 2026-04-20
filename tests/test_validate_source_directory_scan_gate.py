from __future__ import annotations

from pathlib import Path

from scripts.utilities.validate_source_directory_scan_gate import (
    validate_source_directory_scan_gate,
)


def _write_scan(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_validate_source_directory_scan_gate_accepts_approved_contiguous_rows(
    tmp_path: Path,
) -> None:
    scan_path = tmp_path / "source-directory-scan.md"
    _write_scan(
        scan_path,
        "\n".join(
            [
                "operator_assignment_status: approved",
                "scanned_directory: C:/example/source",
                "| row | file | proposed | assigned | note |",
                "| 1 | lesson.pdf | primary | primary | canonical source |",
                "| 2 | appendix.md | supplementary | skip | excluded by operator |",
            ]
        ),
    )

    result = validate_source_directory_scan_gate(scan_path)

    assert result["valid"] is True
    assert result["issues"] == []


def test_validate_source_directory_scan_gate_rejects_missing_approval(tmp_path: Path) -> None:
    scan_path = tmp_path / "source-directory-scan.md"
    _write_scan(
        scan_path,
        "\n".join(
            [
                "operator_assignment_status: pending",
                "scanned_directory: C:/example/source",
                "| row | file | proposed | assigned | note |",
                "| 1 | lesson.pdf | primary | primary | canonical source |",
            ]
        ),
    )

    result = validate_source_directory_scan_gate(scan_path)

    assert result["valid"] is False
    assert "operator_assignment_status must be approved" in result["issues"][0]


def test_validate_source_directory_scan_gate_rejects_non_contiguous_rows(tmp_path: Path) -> None:
    scan_path = tmp_path / "source-directory-scan.md"
    _write_scan(
        scan_path,
        "\n".join(
            [
                "operator_assignment_status: approved",
                "scanned_directory: C:/example/source",
                "| row | file | proposed | assigned | note |",
                "| 1 | lesson.pdf | primary | primary | canonical source |",
                "| 3 | appendix.md | supplementary | skip | excluded by operator |",
            ]
        ),
    )

    result = validate_source_directory_scan_gate(scan_path)

    assert result["valid"] is False
    assert "Scan row numbers must be contiguous starting at 1" in result["issues"][0]


def test_validate_source_directory_scan_gate_uses_latest_assignment_status(tmp_path: Path) -> None:
    scan_path = tmp_path / "source-directory-scan.md"
    _write_scan(
        scan_path,
        "\n".join(
            [
                "operator_assignment_status: approved",
                "scanned_directory: C:/example/source",
                "| row | file | proposed | assigned | note |",
                "| 1 | lesson.pdf | primary | primary | canonical source |",
                "operator_assignment_status: pending",
            ]
        ),
    )

    result = validate_source_directory_scan_gate(scan_path)

    assert result["valid"] is False
    assert "operator_assignment_status must be approved" in result["issues"][0]


def test_validate_source_directory_scan_gate_requires_primary_assignment(tmp_path: Path) -> None:
    scan_path = tmp_path / "source-directory-scan.md"
    _write_scan(
        scan_path,
        "\n".join(
            [
                "operator_assignment_status: approved",
                "scanned_directory: C:/example/source",
                "| row | file | proposed | assigned | note |",
                "| 1 | appendix.md | supplementary | skip | excluded by operator |",
            ]
        ),
    )

    result = validate_source_directory_scan_gate(scan_path)

    assert result["valid"] is False
    assert "At least one operator-assigned primary row is required" in result["issues"][0]


def test_validate_source_directory_scan_gate_requires_complete_directory_coverage(
    tmp_path: Path,
) -> None:
    scanned_dir = tmp_path / "source"
    scanned_dir.mkdir()
    (scanned_dir / "lesson.pdf").write_text("a", encoding="utf-8")
    (scanned_dir / "appendix.md").write_text("b", encoding="utf-8")
    scan_path = tmp_path / "source-directory-scan.md"
    _write_scan(
        scan_path,
        "\n".join(
            [
                "operator_assignment_status: approved",
                f"scanned_directory: {scanned_dir.as_posix()}",
                "| row | file | proposed | assigned | note |",
                "| 1 | lesson.pdf | primary | primary | canonical source |",
            ]
        ),
    )

    result = validate_source_directory_scan_gate(scan_path)

    assert result["valid"] is False
    assert (
        "Scan rows must cover every file in scanned_directory exactly once" in result["issues"][0]
    )
