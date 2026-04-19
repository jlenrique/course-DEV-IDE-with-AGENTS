"""Contract pin for 33-2 lockstep-check exit codes."""

from __future__ import annotations

from pathlib import Path

from scripts.utilities.check_pipeline_manifest_lockstep import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_PACK_PATH,
    run_check,
)


def test_exit_codes_are_strictly_0_1_2(tmp_path: Path) -> None:
    clean_exit, _ = run_check(DEFAULT_MANIFEST_PATH, DEFAULT_PACK_PATH, "v4.2")
    assert clean_exit in {0, 1}

    structural_exit, _ = run_check(tmp_path / "missing.yaml", DEFAULT_PACK_PATH, "v4.2")
    assert structural_exit == 2

