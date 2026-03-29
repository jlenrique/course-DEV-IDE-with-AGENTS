"""Compatibility package for pytest module import paths.

Some test collections under skills/*/scripts/tests can be resolved by pytest
as modules under `scripts.tests.*` when mixed with other test roots.
This package allows those imports to resolve cleanly.
"""
