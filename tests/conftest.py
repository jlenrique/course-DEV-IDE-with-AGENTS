"""Shared test configuration.

- Loads .env for live API tests
- Provides skip markers for missing API keys
- Registers skill script modules with dashed directory names
"""

import importlib.util
import os
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Load .env so API keys are available for live integration tests
# ---------------------------------------------------------------------------

_env_path = ROOT / ".env"
if _env_path.exists():
    for line in _env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        eq = line.find("=")
        if eq == -1:
            continue
        key, val = line[:eq].strip(), line[eq + 1 :].strip()
        if val and key not in os.environ:
            os.environ[key] = val

# ---------------------------------------------------------------------------
# Skip markers for optional API keys
# ---------------------------------------------------------------------------

requires_gamma = pytest.mark.skipif(
    not os.environ.get("GAMMA_API_KEY"), reason="GAMMA_API_KEY not set"
)
requires_elevenlabs = pytest.mark.skipif(
    not os.environ.get("ELEVENLABS_API_KEY"), reason="ELEVENLABS_API_KEY not set"
)
requires_canvas = pytest.mark.skipif(
    not (os.environ.get("CANVAS_ACCESS_TOKEN") and os.environ.get("CANVAS_API_URL")),
    reason="CANVAS_ACCESS_TOKEN or CANVAS_API_URL not set",
)
requires_qualtrics = pytest.mark.skipif(
    not (os.environ.get("QUALTRICS_API_TOKEN") and os.environ.get("QUALTRICS_BASE_URL")),
    reason="QUALTRICS_API_TOKEN or QUALTRICS_BASE_URL not set",
)
requires_panopto = pytest.mark.skipif(
    not (os.environ.get("PANOPTO_BASE_URL") and os.environ.get("PANOPTO_CLIENT_ID")),
    reason="PANOPTO_BASE_URL or PANOPTO_CLIENT_ID not set",
)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register CLI options for optional live API test execution."""
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Run tests marked as live_api (disabled by default).",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers used in this repository."""
    config.addinivalue_line(
        "markers",
        "live_api: marks tests that call live third-party APIs",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Exclude live API tests from default runs unless explicitly requested."""
    if config.getoption("--run-live"):
        return

    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []

    for item in items:
        if "live_api" in item.keywords:
            deselected.append(item)
        else:
            selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected

# ---------------------------------------------------------------------------
# Register skill scripts with dashed directory names for clean imports
# ---------------------------------------------------------------------------

_SKILL_SCRIPTS = [
    (
        "skills.pre_flight_check.scripts",
        ROOT / "skills" / "pre-flight-check" / "scripts",
    ),
]

for pkg_name, pkg_path in _SKILL_SCRIPTS:
    if pkg_name in sys.modules:
        continue
    parts = pkg_name.split(".")
    for i in range(1, len(parts) + 1):
        partial = ".".join(parts[:i])
        if partial not in sys.modules:
            mod = types.ModuleType(partial)
            mod.__path__ = []
            sys.modules[partial] = mod
    if pkg_path.is_dir():
        for py_file in sorted(pkg_path.glob("*.py")):
            if py_file.name == "__init__.py":
                continue
            mod_name = f"{pkg_name}.{py_file.stem}"
            if mod_name in sys.modules:
                continue
            spec = importlib.util.spec_from_file_location(mod_name, py_file)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)
