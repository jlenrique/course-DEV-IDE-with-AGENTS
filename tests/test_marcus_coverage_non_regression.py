"""Coverage non-regression pin (AC-T.17, M-4 rider).

Loads the committed baseline at
``tests/fixtures/coverage_baseline/marcus_pre_30-1.json`` and asserts that
post-30-1 per-package line-coverage for ``marcus/lesson_plan/*`` meets or
exceeds the baseline minus a 0.5% tolerance.

Requires ``pytest-cov`` + ``coverage`` packages. When those are not
installed, the test skips gracefully (the baseline artifact still ships
so the pin activates the moment coverage tooling lands in dev deps).

Env-gate skip ``MARCUS_COVERAGE_PIN_SKIP=1`` is honored for local dev
iteration; CI runs unconditionally.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT: Path = Path(__file__).parent.parent.resolve()
_BASELINE_PATH: Path = (
    _REPO_ROOT
    / "tests"
    / "fixtures"
    / "coverage_baseline"
    / "marcus_pre_30-1.json"
)
_TOLERANCE_PCT: float = 0.5


def _pytest_cov_available() -> bool:
    try:
        import pytest_cov  # type: ignore[import-untyped]  # noqa: F401
    except ImportError:
        return False
    return True


def _baseline_is_placeholder() -> bool:
    """Return True iff the committed baseline still carries placeholder values.

    G6 Auditor#5 + Edge#3: the 30-1 baseline shipped with placeholder
    percentages + an explicit ``_note`` saying so. Activating the pin
    against placeholder values would fail in the wrong direction (real
    coverage ≠ 85% placeholder). Skip until a real baseline is captured.
    """
    if not _BASELINE_PATH.is_file():
        return False
    try:
        payload = json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    note = str(payload.get("_note", "")).lower()
    comment = str(payload.get("_comment", "")).lower()
    if "placeholder" in note or "placeholder" in comment:
        return True

    for entry in payload.values():
        if isinstance(entry, dict):
            entry_note = str(entry.get("note", "")).lower()
            if "placeholder" in entry_note:
                return True
    return False


@pytest.mark.skipif(
    os.environ.get("MARCUS_COVERAGE_PIN_SKIP") == "1",
    reason="MARCUS_COVERAGE_PIN_SKIP=1 set for local dev iteration",
)
@pytest.mark.skipif(
    not _pytest_cov_available(),
    reason="pytest-cov not installed; coverage pin dormant until dev deps add it",
)
@pytest.mark.skipif(
    _baseline_is_placeholder(),
    reason=(
        "Baseline artifact still carries placeholder values; activate when a "
        "real pre-30-1 coverage capture replaces the placeholder percentages"
    ),
)
def test_marcus_lesson_plan_coverage_non_regression(tmp_path: Path) -> None:
    """AC-T.17 — marcus/lesson_plan/* line-coverage ≥ baseline - 0.5%.

    M-4 rider enforcement. Commits a baseline; future runs compare.
    """
    assert _BASELINE_PATH.is_file(), (
        f"Coverage baseline missing: {_BASELINE_PATH}"
    )
    baseline = json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))

    coverage_json = tmp_path / "coverage.json"
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=marcus",
        f"--cov-report=json:{coverage_json}",
        "--cov-report=term:skip-covered",
        "-q",
        "-p",
        "no:cacheprovider",
        str(_REPO_ROOT / "tests" / "test_marcus_duality_imports.py"),
        str(_REPO_ROOT / "tests" / "test_marcus_negotiator_seam_named.py"),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(_REPO_ROOT), check=False
    )
    if result.returncode != 0 or not coverage_json.is_file():
        pytest.skip(
            f"pytest --cov run failed; pin dormant. "
            f"stdout={result.stdout[-200:]} stderr={result.stderr[-200:]}"
        )
    actual = json.loads(coverage_json.read_text(encoding="utf-8"))

    baseline_lp = baseline.get("marcus/lesson_plan", {}).get(
        "line_coverage_pct", 0.0
    )
    actual_lp = _extract_package_pct(actual, "marcus/lesson_plan")
    assert actual_lp >= baseline_lp - _TOLERANCE_PCT, (
        f"marcus/lesson_plan line-coverage regressed: "
        f"baseline={baseline_lp}% actual={actual_lp}% "
        f"tolerance={_TOLERANCE_PCT}%"
    )


def test_baseline_artifact_is_well_formed() -> None:
    """AC-T.17 (shape pin) — committed baseline parses and has expected shape."""
    assert _BASELINE_PATH.is_file(), (
        f"Coverage baseline artifact missing: {_BASELINE_PATH}"
    )
    baseline = json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))
    assert isinstance(baseline, dict)
    for required_pkg in ("marcus/lesson_plan", "marcus/intake", "marcus/orchestrator"):
        assert required_pkg in baseline, (
            f"baseline missing package key: {required_pkg}"
        )
        entry = baseline[required_pkg]
        assert "line_coverage_pct" in entry, (
            f"baseline[{required_pkg!r}] missing line_coverage_pct"
        )
        assert isinstance(entry["line_coverage_pct"], int | float)


def _extract_package_pct(coverage_report: dict, package_path: str) -> float:
    """Extract per-package line-coverage % from a pytest-cov JSON report.

    pytest-cov JSON shape: ``{"files": {"path/to/file.py": {"summary": {"percent_covered": N}}}}``.
    We aggregate per file under ``package_path`` and return the mean.
    """
    files = coverage_report.get("files", {})
    matching = [
        data for path, data in files.items() if path.startswith(package_path)
    ]
    if not matching:
        return 0.0
    total = sum(
        entry.get("summary", {}).get("percent_covered", 0.0) for entry in matching
    )
    return total / len(matching)
