"""Lightweight .venv health check for run-start preflight.

Checks:
- .venv directory exists
- pyvenv.cfg exists
- venv Python executable exists
- venv Python can run and import core modules

Usage:
    py -3.13 -m scripts.utilities.venv_health_check
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from scripts.utilities.file_helpers import project_root


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    resolution: str = ""


def _venv_python_path(root: Path) -> Path:
    if os.name == "nt":
        return root / ".venv" / "Scripts" / "python.exe"
    return root / ".venv" / "bin" / "python"


def _repair_commands() -> list[str]:
    if os.name == "nt":
        return [
            "py -3.13 -m venv .venv",
            ".venv\\Scripts\\python.exe -m pip install -r requirements.txt",
        ]
    return [
        "python3 -m venv .venv",
        ".venv/bin/python -m pip install -r requirements.txt",
    ]


def run_checks(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    venv_dir = root / ".venv"
    pyvenv_cfg = venv_dir / "pyvenv.cfg"
    venv_python = _venv_python_path(root)
    repair = " ; ".join(_repair_commands())

    if not venv_dir.exists():
        results.append(
            CheckResult(
                name="venv_dir",
                status="fail",
                detail="Missing .venv directory.",
                resolution=repair,
            )
        )
    else:
        results.append(
            CheckResult(
                name="venv_dir",
                status="pass",
                detail=".venv directory exists.",
            )
        )

    if not pyvenv_cfg.exists():
        results.append(
            CheckResult(
                name="pyvenv_cfg",
                status="fail",
                detail="Missing .venv/pyvenv.cfg.",
                resolution=repair,
            )
        )
    else:
        results.append(
            CheckResult(
                name="pyvenv_cfg",
                status="pass",
                detail="pyvenv.cfg is present.",
            )
        )

    if not venv_python.exists():
        results.append(
            CheckResult(
                name="venv_python",
                status="fail",
                detail=f"Missing venv interpreter at {venv_python}",
                resolution=repair,
            )
        )
        return results

    try:
        probe = subprocess.run(
            [
                str(venv_python),
                "-c",
                "import sys,requests,yaml,dotenv; print(sys.version.split()[0])",
            ],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - defensive
        results.append(
            CheckResult(
                name="venv_probe",
                status="fail",
                detail=f"Interpreter probe failed: {type(exc).__name__}: {exc}",
                resolution=repair,
            )
        )
        return results

    if probe.returncode != 0:
        detail = (probe.stderr or probe.stdout or "Unknown venv probe failure").strip()
        results.append(
            CheckResult(
                name="venv_probe",
                status="fail",
                detail=f"Interpreter probe failed: {detail}",
                resolution=repair,
            )
        )
    else:
        version = (probe.stdout or "").strip()
        results.append(
            CheckResult(
                name="venv_probe",
                status="pass",
                detail=f"Interpreter and core imports OK (Python {version}).",
            )
        )

    return results


def main() -> int:
    root = project_root()
    results = run_checks(root)
    failures = [r for r in results if r.status == "fail"]

    payload = {
        "root": str(root),
        "overall_status": "fail" if failures else "pass",
        "checks": [asdict(r) for r in results],
        "one_step_repair": _repair_commands(),
    }
    print(json.dumps(payload, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
