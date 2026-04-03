"""Test configuration for gamma-api-mastery scripts."""

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
_SCRIPTS_DIR = str(Path(__file__).resolve().parents[1])

if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-live-e2e",
        action="store_true",
        default=False,
        help="Run tests marked as live_api_e2e (disabled by default).",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "live_api_e2e: marks slower/flakier live end-to-end API tests",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    run_live_e2e = config.getoption("--run-live-e2e")
    skip_live_e2e = pytest.mark.skip(reason="needs --run-live-e2e option to run")
    for item in items:
        if "live_api_e2e" in item.keywords and not run_live_e2e:
            item.add_marker(skip_live_e2e)
