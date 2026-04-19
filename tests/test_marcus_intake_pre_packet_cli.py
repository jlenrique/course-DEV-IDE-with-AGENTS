"""CLI-shim round-trip test for ``scripts/utilities/prepare-irene-packet.py`` (AC-T.5).

Invokes the CLI shim via subprocess against a synthetic bundle and
asserts the shim produces the same packet content + stdout format +
exit code as the pre-30-2a implementation.

The hyphenated filename (``prepare-irene-packet.py``) cannot be imported
as a Python module; subprocess invocation is the only way to exercise
the CLI end-to-end.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT: Path = Path(__file__).parent.parent.resolve()
_SHIM_PATH: Path = _REPO_ROOT / "scripts" / "utilities" / "prepare-irene-packet.py"


def _write_bundle(bundle_dir: Path) -> None:
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


def test_cli_shim_writes_expected_packet_and_exits_zero(tmp_path: Path) -> None:
    """AC-T.5 — CLI shim round-trip produces packet file + success stdout + exit 0."""
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir)
    output_path = tmp_path / "out" / "irene-packet.md"

    env_with_pythonpath = {
        **dict(__import__("os").environ),
        "PYTHONPATH": str(_REPO_ROOT),
    }
    result = subprocess.run(
        [
            sys.executable,
            str(_SHIM_PATH),
            "--bundle-dir",
            str(bundle_dir),
            "--run-id",
            "CLI-TEST-001",
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
        env=env_with_pythonpath,
        check=False,
    )

    assert result.returncode == 0, (
        f"shim exited non-zero: stderr={result.stderr!r} stdout={result.stdout!r}"
    )
    assert output_path.is_file()

    # Stdout format preserved byte-identical to pre-30-2a implementation.
    stdout_lines = result.stdout.splitlines()
    assert any(line.startswith("Irene packet written to ") for line in stdout_lines)
    assert "Sections: 15" in result.stdout
    assert "Has directives: True" in result.stdout
    assert "Has ingestion receipt: False" in result.stdout

    # Packet file header is identical.
    written = output_path.read_text(encoding="utf-8")
    assert written.startswith("# Irene Packet for CLI-TEST-001\n")
