"""Determinism tests for v4.2 generator."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import yaml

from scripts.generators.v42.render import render_pack

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests/generators/v42/fixtures"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_sha_round_trip_fixture_manifest(tmp_path: Path) -> None:
    out = tmp_path / "out.md"
    render_pack(FIXTURES / "manifest_fixture.yaml", out)
    expected = (
        (FIXTURES / "pack_sha_fixture.txt")
        .read_text(encoding="utf-8")
        .splitlines()[0]
        .split(":", 1)[1]
    )
    assert _sha(out) == expected


def test_5x_consecutive_byte_identity_fixture_manifest(tmp_path: Path) -> None:
    shas: list[str] = []
    for idx in range(5):
        out = tmp_path / f"run-{idx}.md"
        render_pack(FIXTURES / "manifest_fixture.yaml", out)
        shas.append(_sha(out))
    assert len(set(shas)) == 1


def test_generated_pack_parses_through_l1_check(tmp_path: Path) -> None:
    out = tmp_path / "generated.md"
    render_pack(FIXTURES / "manifest_fixture.yaml", out)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.utilities.check_pipeline_manifest_lockstep",
            "--manifest",
            str(FIXTURES / "manifest_fixture.yaml"),
            "--pack-path",
            str(out),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 2, result.stdout + result.stderr


def test_manifest_mutation_produces_localized_diff(tmp_path: Path) -> None:
    manifest = yaml.safe_load((FIXTURES / "manifest_fixture.yaml").read_text(encoding="utf-8"))
    base_out = tmp_path / "base.md"
    render_pack(FIXTURES / "manifest_fixture.yaml", base_out)
    manifest["steps"][0]["label"] = "Activation + Preflight UPDATED"
    mut_manifest = tmp_path / "mut.yaml"
    mut_manifest.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    mut_out = tmp_path / "mut.md"
    render_pack(mut_manifest, mut_out)
    assert _sha(base_out) != _sha(mut_out)
    assert "Activation + Preflight UPDATED" in mut_out.read_text(encoding="utf-8")
