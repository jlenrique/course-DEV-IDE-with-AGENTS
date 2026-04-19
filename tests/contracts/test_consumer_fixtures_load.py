"""AC-T.6 — Consumer-fixture loader contract (Murat R1 amendment + M-AM-4).

Fixtures under ``tests/fixtures/consumers/fixture_*.py`` are NOT pytest-collected
(filenames don't start with ``test_``). This loader imports each fixture via
``importlib.util.spec_from_file_location``, invokes its ``demonstrate()``
callable, and asserts no error.

Blocks merge if any consumer fixture breaks its API surface.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

FIXTURES_DIR = (
    Path(__file__).resolve().parents[1] / "fixtures" / "consumers"
)

FIXTURE_FILES = [
    "fixture_30_3_marcus_consumer.py",
    "fixture_29_2_irene_consumer.py",
    "fixture_28_2_tracy_consumer.py",
]


def _import_fixture(filename: str):
    """Import a fixture file by path. Returns the loaded module object."""
    fixture_path = FIXTURES_DIR / filename
    assert fixture_path.exists(), f"Fixture missing: {fixture_path}"
    # Give each module a unique dotted name to avoid cache pollution.
    mod_name = f"tests.fixtures.consumers.{filename.removesuffix('.py')}"
    spec = importlib.util.spec_from_file_location(mod_name, fixture_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_fixture_file_exists(filename: str) -> None:
    assert (FIXTURES_DIR / filename).exists(), (
        f"Consumer fixture missing: {filename}. Check M-AM-4 rename."
    )


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_fixture_imports_and_exposes_demonstrate(filename: str) -> None:
    module = _import_fixture(filename)
    assert hasattr(module, "demonstrate"), (
        f"{filename} does not expose a 'demonstrate()' callable; the loader "
        f"requires this entry point."
    )
    assert callable(module.demonstrate)


@pytest.mark.parametrize("filename", FIXTURE_FILES)
def test_fixture_demonstrate_executes_without_error(filename: str) -> None:
    """Run each fixture's demonstrate() and assert no exception."""
    module = _import_fixture(filename)
    module.demonstrate()


def test_fixtures_directory_is_not_auto_collected_by_pytest() -> None:
    """Sanity: no file in tests/fixtures/consumers/ starts with 'test_'.

    M-AM-4 rename invariant: pytest collects only ``test_*.py``; these files
    intentionally use ``fixture_*.py`` so they are imported by this loader
    and NOT auto-collected as test modules (prevents naming-pattern foot-guns
    where a fixture has asserts but no pytest-recognizable tests).
    """
    for item in FIXTURES_DIR.iterdir():
        if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
            assert item.name.startswith("fixture_"), (
                f"Found non-fixture-prefixed Python file under "
                f"tests/fixtures/consumers/: {item.name}. Per M-AM-4 "
                f"rename rule, all consumer fixtures use 'fixture_' prefix."
            )
