"""Contract for pipeline-manifest top-level key uniqueness."""

from __future__ import annotations

from pathlib import Path

import yaml


def _collect_collisions(state_config: Path) -> dict[str, list[str]]:
    manifest_path = state_config / "pipeline-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    manifest_keys = set(manifest_data.keys())

    allowed_shared = {"schema_version"}
    collisions: dict[str, list[str]] = {}
    for candidate in state_config.glob("*.yaml"):
        if candidate.name == "pipeline-manifest.yaml":
            continue
        other_data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
        if not isinstance(other_data, dict):
            continue
        shared = manifest_keys.intersection(other_data.keys()) - allowed_shared
        if shared:
            collisions[candidate.name] = sorted(shared)
    return collisions


def test_pipeline_manifest_keys_do_not_shadow_other_state_configs() -> None:
    state_config = Path(__file__).resolve().parents[2] / "state" / "config"
    collisions = _collect_collisions(state_config)
    assert not collisions, f"pipeline-manifest top-level key collisions: {collisions}"


def test_disjoint_keys_detector_flags_synthesized_collision(tmp_path: Path) -> None:
    (tmp_path / "pipeline-manifest.yaml").write_text(
        "schema_version: '1.0'\npack_version: 'v4.2'\nsteps: []\n",
        encoding="utf-8",
    )
    (tmp_path / "other.yaml").write_text(
        "pack_version: 'shadow'\n",
        encoding="utf-8",
    )
    collisions = _collect_collisions(tmp_path)
    assert collisions == {"other.yaml": ["pack_version"]}

