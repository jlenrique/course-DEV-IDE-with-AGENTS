"""CLI-shim round-trip test for ``scripts/utilities/prepare-irene-packet.py``.

Invokes the CLI shim via subprocess against a synthetic bundle and
asserts the shim produces the same packet content + stdout format +
exit code as the pre-30-2a implementation (AC-T.5) and that the new
``--require-receipt`` default guard (2026-04-19 Step-04 silent-empty
fix) behaves correctly.

The hyphenated filename (``prepare-irene-packet.py``) cannot be imported
as a Python module; subprocess invocation is the only way to exercise
the CLI end-to-end.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT: Path = Path(__file__).parent.parent.resolve()
_SHIM_PATH: Path = _REPO_ROOT / "scripts" / "utilities" / "prepare-irene-packet.py"


def _valid_receipt_text() -> str:
    return (
        "# Ingestion Quality Gate Receipt\n"
        "\n"
        "- run_id: CLI-TEST-001\n"
        "- gate_decision: proceed\n"
    )


def _write_bundle(
    bundle_dir: Path,
    *,
    include_receipt: bool = False,
    receipt_text: str | None = None,
) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "extracted.md").write_text(
        "# Extracted\n\nBody.\n",
        encoding="utf-8",
    )
    (bundle_dir / "metadata.json").write_text(
        json.dumps(
            {
                "primary_source": "cli-test.pdf",
                "total_sections": 1,
                "overall_confidence": 0.5,
            }
        ),
        encoding="utf-8",
    )
    (bundle_dir / "operator-directives.md").write_text(
        "# Directives\n",
        encoding="utf-8",
    )
    if include_receipt:
        (bundle_dir / "ingestion-quality-gate-receipt.md").write_text(
            receipt_text if receipt_text is not None else _valid_receipt_text(),
            encoding="utf-8",
        )


def _run_shim(
    args: list[str],
) -> subprocess.CompletedProcess[str]:
    env_with_pythonpath = {
        **dict(os.environ),
        "PYTHONPATH": str(_REPO_ROOT),
    }
    return subprocess.run(
        [sys.executable, str(_SHIM_PATH), *args],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
        env=env_with_pythonpath,
        check=False,
    )


# ---------------------------------------------------------------------------
# AC-T.5 — legacy byte-identical round-trip (escape-hatch path)
# ---------------------------------------------------------------------------


def test_cli_shim_legacy_silent_pass_requires_opt_out_flag(tmp_path: Path) -> None:
    """AC-T.5 — With ``--no-require-receipt`` the shim still produces the
    same packet + stdout as the pre-30-2a implementation, preserving the
    escape hatch needed by golden-trace capture and rerun-carry-forward
    tooling."""
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir)
    output_path = tmp_path / "out" / "irene-packet.md"

    result = _run_shim([
        "--bundle-dir",
        str(bundle_dir),
        "--run-id",
        "CLI-TEST-001",
        "--output",
        str(output_path),
        "--no-require-receipt",
    ])

    assert result.returncode == 0, (
        f"shim exited non-zero: stderr={result.stderr!r} stdout={result.stdout!r}"
    )
    assert output_path.is_file()

    stdout_lines = result.stdout.splitlines()
    assert any(line.startswith("Irene packet written to ") for line in stdout_lines)
    assert "Sections: 15" in result.stdout
    assert "Has directives: True" in result.stdout
    assert "Has ingestion receipt: False" in result.stdout

    written = output_path.read_text(encoding="utf-8")
    assert written.startswith("# Irene Packet for CLI-TEST-001\n")


# ---------------------------------------------------------------------------
# 2026-04-19 Step-04 silent-empty receipt guard
# ---------------------------------------------------------------------------


def test_cli_shim_default_blocks_missing_receipt(tmp_path: Path) -> None:
    """Default (no flag) must refuse to generate the packet when the
    ingestion receipt is missing — this is the structural fix for the
    2026-04-19 trial's manual-intervention failure mode."""
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir, include_receipt=False)
    output_path = tmp_path / "out" / "irene-packet.md"

    result = _run_shim([
        "--bundle-dir",
        str(bundle_dir),
        "--run-id",
        "CLI-TEST-BLOCK",
        "--output",
        str(output_path),
    ])

    assert result.returncode == 1
    assert "ingestion-quality-gate-receipt.md is missing" in result.stderr.lower() or (
        "ingestion-quality-gate-receipt" in result.stderr.lower()
        and "missing" in result.stderr.lower()
    )
    assert "emit_ingestion_quality_receipt" in result.stderr
    assert not output_path.exists()


def test_cli_shim_default_blocks_placeholder_receipt(tmp_path: Path) -> None:
    """Default must block when the receipt is a template scaffold with
    unresolved ``[FILL IN: ...]`` markers — a partially-populated receipt
    is worse than a missing one because it masquerades as complete."""
    bundle_dir = tmp_path / "bundle"
    placeholder = (
        "# Ingestion Quality Gate Receipt\n"
        "- gate_decision: proceed\n"
        "- notes: [FILL IN: operator fills this in]\n"
    )
    _write_bundle(bundle_dir, include_receipt=True, receipt_text=placeholder)
    output_path = tmp_path / "out" / "irene-packet.md"

    result = _run_shim([
        "--bundle-dir",
        str(bundle_dir),
        "--run-id",
        "CLI-TEST-PLACEHOLDER",
        "--output",
        str(output_path),
    ])

    assert result.returncode == 1
    assert "[FILL IN:" in result.stderr
    assert not output_path.exists()


def test_cli_shim_default_passes_with_valid_receipt(tmp_path: Path) -> None:
    """Default must allow packet generation when the receipt is present,
    non-empty, has no placeholder markers, and declares a gate_decision."""
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir, include_receipt=True)
    output_path = tmp_path / "out" / "irene-packet.md"

    result = _run_shim([
        "--bundle-dir",
        str(bundle_dir),
        "--run-id",
        "CLI-TEST-PASS",
        "--output",
        str(output_path),
    ])

    assert result.returncode == 0, (
        f"shim exited non-zero: stderr={result.stderr!r} stdout={result.stdout!r}"
    )
    assert output_path.is_file()
    assert "Has ingestion receipt: True" in result.stdout


def test_cli_shim_default_blocks_empty_receipt(tmp_path: Path) -> None:
    """Default must block when the receipt exists but is whitespace-only
    — the operator-abandoned-halfway failure mode."""
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir, include_receipt=True, receipt_text="   \n\n")
    output_path = tmp_path / "out" / "irene-packet.md"

    result = _run_shim([
        "--bundle-dir",
        str(bundle_dir),
        "--run-id",
        "CLI-TEST-EMPTY",
        "--output",
        str(output_path),
    ])

    assert result.returncode == 1
    assert "empty" in result.stderr.lower()
    assert not output_path.exists()
