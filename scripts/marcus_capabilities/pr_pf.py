"""PR-PF — Preflight (full implementation).

Wraps ``scripts.utilities.app_session_readiness --with-preflight`` to give
Marcus a structured readiness report before firing Prompt 1 on a tracked
production run. Verbose-posture: summarize-mode reports what WOULD happen;
execute-mode actually runs the readiness subprocess.

See ``skills/bmad-agent-marcus/capabilities/pr-pf.md`` for doctrine.

Invocation:
    python -m scripts.marcus_capabilities.pr_pf --mode summarize --run-id ABC
    python -m scripts.marcus_capabilities.pr_pf --mode execute --bundle-path <path>
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from scripts.marcus_capabilities._shared import (
    CapabilityError,
    Invocation,
    LandingPoint,
    ReturnEnvelope,
    run_cli,
)

CAPABILITY_CODE = "PR-PF"

# Subprocess entrypoint. Injectable for testing (patch at import site).
_READINESS_ENTRYPOINT = "scripts.utilities.app_session_readiness"

# Upper bound on how long the readiness subprocess may run before we abort
# and surface PREFLIGHT_TIMEOUT into the envelope. 120s is generous for a
# preflight check (typically ~1-3s) while preventing an indefinite hang of
# Marcus's turn when the runner stalls on I/O.
_SUBPROCESS_TIMEOUT_SEC = 120


def summarize(invocation: Invocation) -> ReturnEnvelope:
    """Report the plan without touching disk or running subprocesses."""
    args = invocation.args
    with_preflight = bool(args.get("with_preflight", True))
    json_only = bool(args.get("json_only", True))
    ctx = invocation.context
    bundle_path = ctx.bundle_path if ctx else None

    plan_lines = [
        f"Would invoke: python -m {_READINESS_ENTRYPOINT}",
        f"  --with-preflight={with_preflight}",
        f"  --json-only={json_only}",
    ]
    if bundle_path:
        plan_lines.append(f"  --bundle-dir={bundle_path}")

    return ReturnEnvelope(
        status="ok",
        capability_code=CAPABILITY_CODE,
        run_id=ctx.run_id if ctx else None,
        result={
            "mode": "summarize",
            "plan": plan_lines,
            "with_preflight": with_preflight,
            "json_only": json_only,
            "bundle_path": bundle_path,
        },
        landing_point=LandingPoint(bundle_path=bundle_path),
        errors=[],
        telemetry={"mode": "summarize"},
    )


def _build_cmd(args: dict[str, Any], bundle_path: str | None) -> list[str]:
    cmd = [sys.executable, "-m", _READINESS_ENTRYPOINT]
    if args.get("with_preflight", True):
        cmd.append("--with-preflight")
    if args.get("json_only", True):
        cmd.append("--json-only")
    if bundle_path:
        cmd.extend(["--bundle-dir", bundle_path])
    return cmd


def _run_subprocess(cmd: list[str]) -> tuple[int, str, str]:
    """Invoke the readiness runner. Split out for mockability in tests.

    Bounded by ``_SUBPROCESS_TIMEOUT_SEC`` so a stalled runner cannot hang
    Marcus's turn indefinitely. ``subprocess.TimeoutExpired`` bubbles up to
    ``execute`` for envelope surfacing.
    """
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=_SUBPROCESS_TIMEOUT_SEC,
    )
    return completed.returncode, completed.stdout, completed.stderr


def execute(invocation: Invocation) -> ReturnEnvelope:
    """Actually run the preflight subprocess and assemble the envelope.

    All exception paths land in the envelope. No Python traceback crosses
    the Marcus boundary (AC-C.3) — parity with the PR-RC wrap added in
    commit 5548a3a.
    """
    ctx = invocation.context
    bundle_path = ctx.bundle_path if ctx else None
    cmd = _build_cmd(invocation.args, bundle_path)

    try:
        returncode, stdout, stderr = _run_subprocess(cmd)
    except FileNotFoundError as exc:
        return ReturnEnvelope(
            status="error",
            capability_code=CAPABILITY_CODE,
            run_id=ctx.run_id if ctx else None,
            errors=[
                CapabilityError(
                    code="PREFLIGHT_EXEC_UNAVAILABLE",
                    message=f"Could not invoke readiness runner: {exc}",
                    remediation=(
                        "Confirm Python venv is active and the scripts package "
                        "is importable."
                    ),
                )
            ],
            telemetry={"cmd": cmd},
        )
    except subprocess.TimeoutExpired:
        return ReturnEnvelope(
            status="error",
            capability_code=CAPABILITY_CODE,
            run_id=ctx.run_id if ctx else None,
            errors=[
                CapabilityError(
                    code="PREFLIGHT_TIMEOUT",
                    message=(
                        f"Readiness runner exceeded {_SUBPROCESS_TIMEOUT_SEC}s "
                        f"timeout. cmd={cmd}"
                    ),
                    remediation=(
                        "Investigate the readiness runner for stalled I/O or "
                        "hung sub-processes. Re-invoke PR-PF after remediation."
                    ),
                )
            ],
            telemetry={"cmd": cmd, "timeout_sec": _SUBPROCESS_TIMEOUT_SEC},
        )
    except Exception as exc:  # noqa: BLE001 — envelope contract requires catching all
        # AC-C.3: scripts exit 0 on capability-level failure; Python exceptions
        # MUST NOT cross the Marcus boundary. PermissionError, OSError, and
        # unforeseen failure modes all get wrapped.
        return ReturnEnvelope(
            status="error",
            capability_code=CAPABILITY_CODE,
            run_id=ctx.run_id if ctx else None,
            errors=[
                CapabilityError(
                    code="PR_PF_UNEXPECTED_FAILURE",
                    message=f"{type(exc).__name__}: {exc}",
                    remediation=(
                        "Investigate the readiness subprocess environment. "
                        "If the issue persists, surface to operator for "
                        "manual diagnosis."
                    ),
                )
            ],
            telemetry={"cmd": cmd},
        )

    parsed: dict[str, Any] | None = None
    parse_failed = False
    if stdout:
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            parsed = None
            parse_failed = True

    errors: list[CapabilityError] = []
    if returncode != 0:
        status = "error"
        errors.append(
            CapabilityError(
                code="PREFLIGHT_FAILED",
                message=(
                    f"Readiness runner exited {returncode}. "
                    f"stderr: {stderr.strip()[:500]}"
                ),
                remediation=(
                    "Inspect the preflight JSON payload for failing checks; "
                    "remediate and re-invoke PR-PF."
                ),
            )
        )
    elif parse_failed:
        # Exit 0 + unparseable stdout = can't confirm PASS. Reporting
        # preflight_passed=True without a parsed verdict would silently
        # mask a downstream contract violation.
        status = "partial"
        errors.append(
            CapabilityError(
                code="PREFLIGHT_STDOUT_UNPARSEABLE",
                message=(
                    "Readiness runner exited 0 but stdout is not valid JSON — "
                    "cannot confirm PASS verdict."
                ),
                remediation=(
                    "Check the runner emits pure JSON on stdout (no trailing "
                    "log lines). Re-invoke PR-PF after remediation."
                ),
            )
        )
    else:
        status = "ok"

    preflight_passed = returncode == 0 and not parse_failed

    return ReturnEnvelope(
        status=status,
        capability_code=CAPABILITY_CODE,
        run_id=ctx.run_id if ctx else None,
        result={
            "mode": "execute",
            "returncode": returncode,
            "readiness": parsed if parsed is not None else {"raw_stdout": stdout},
            "preflight_passed": preflight_passed,
        },
        landing_point=LandingPoint(bundle_path=bundle_path),
        errors=errors,
        telemetry={"cmd": cmd, "returncode": returncode},
    )


def main(argv: list[str] | None = None) -> int:
    return run_cli(CAPABILITY_CODE, summarize, execute, argv)


if __name__ == "__main__":
    sys.exit(main())
