"""Validate exemplar catalog YAML files are parseable."""

from __future__ import annotations

from pathlib import Path

import yaml


def test_exemplar_catalogs_are_valid_yaml() -> None:
    root = Path(__file__).resolve().parents[1] / "resources" / "exemplars"
    catalogs = sorted(root.glob("*/_catalog.yaml"))

    assert catalogs, "Expected at least one exemplar catalog file"

    for catalog in catalogs:
        parsed = yaml.safe_load(catalog.read_text(encoding="utf-8"))
        assert isinstance(parsed, dict), f"Catalog must parse to a mapping: {catalog}"
        assert "tool" in parsed, f"Catalog missing tool key: {catalog}"
        assert "exemplars" in parsed, f"Catalog missing exemplars key: {catalog}"
