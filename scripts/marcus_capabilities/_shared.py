"""Shared envelope + CLI wrapper for Marcus production-readiness capabilities.

Provides the pinned invocation/return envelope contracts (AC-C.1/C.2 from
Story 26-6) and the dual-mode (summarize | execute) CLI harness every PR-*
capability uses.

Contract summary:

* **Invocation envelope** (Marcus → capability script), 6 fields:
  ``capability_code, mode, args, context?, idempotency_key?``. ``context``
  itself may contain ``run_id, bundle_path, invoked_by``.
* **Return envelope** (capability → Marcus), 7 fields: ``status, capability_code,
  run_id?, result, landing_point?, errors, telemetry``. Scripts exit 0 on
  capability-level failure (errors populated in envelope); non-zero exit is
  reserved for envelope-contract violations (script bugs).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

InvocationMode = Literal["summarize", "execute"]
ReturnStatus = Literal["ok", "error", "partial"]


@dataclass(frozen=True)
class InvocationContext:
    """Optional context Marcus passes to a capability."""

    run_id: str | None = None
    bundle_path: str | None = None
    invoked_by: str = "marcus"


@dataclass(frozen=True)
class Invocation:
    """What Marcus sends to a capability (AC-C.1)."""

    capability_code: str
    mode: InvocationMode
    args: dict[str, Any] = field(default_factory=dict)
    context: InvocationContext | None = None
    idempotency_key: str | None = None


@dataclass
class LandingPoint:
    """Verbose-posture rendering payload Marcus shows the operator."""

    bundle_path: str | None = None
    manifest: dict[str, Any] = field(default_factory=dict)
    sha256: str | None = None


@dataclass
class CapabilityError:
    """Structured error surface (AC-C.3). Never raised — always returned."""

    code: str
    message: str
    remediation: str = ""


@dataclass
class ReturnEnvelope:
    """What every capability returns (AC-C.2).

    ``status == "ok"`` → ``result`` is populated, ``errors`` is empty.
    ``status == "error"`` → ``errors`` is non-empty; ``result`` may be partial.
    ``status == "partial"`` → both may be populated; rare.
    """

    status: ReturnStatus
    capability_code: str
    run_id: str | None = None
    result: dict[str, Any] = field(default_factory=dict)
    landing_point: LandingPoint | None = None
    errors: list[CapabilityError] = field(default_factory=list)
    telemetry: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """JSON-serializable dict with the canonical 7-field shape."""
        data = asdict(self)
        # Strip None-valued optional fields for cleaner stdout
        if data.get("run_id") is None:
            data.pop("run_id", None)
        if data.get("landing_point") is None:
            data.pop("landing_point", None)
        return data


# ---------------------------------------------------------------------------
# Canonical envelope field sets — tests cross-check against these.
# ---------------------------------------------------------------------------

INVOCATION_FIELDS = frozenset({"capability_code", "mode", "args", "context", "idempotency_key"})
RETURN_FIELDS = frozenset(
    {"status", "capability_code", "run_id", "result", "landing_point", "errors", "telemetry"}
)


# ---------------------------------------------------------------------------
# Stub helper — PR-HC and PR-RS use this until story 26-10 promotes them.
# ---------------------------------------------------------------------------


def stub_envelope(capability_code: str, invocation: Invocation) -> ReturnEnvelope:
    """Return the canonical NOT_YET_IMPLEMENTED envelope (AC-B.3).

    Stubs are operator-observable per party consensus: invisible stubs hide
    breakage. Follow-up impl lives in story 26-10.
    """
    return ReturnEnvelope(
        status="error",
        capability_code=capability_code,
        run_id=invocation.context.run_id if invocation.context else None,
        errors=[
            CapabilityError(
                code="NOT_YET_IMPLEMENTED",
                message=(
                    f"Capability {capability_code} is a registered stub; "
                    f"full implementation is scheduled for story 26-10."
                ),
                remediation=(
                    "Proceed without this capability for now, or request the "
                    "operator to prioritize story 26-10."
                ),
            )
        ],
        telemetry={"duration_ms": 0, "stub": True},
    )


# ---------------------------------------------------------------------------
# Dual-mode CLI harness — every PR-* script uses this.
# ---------------------------------------------------------------------------


def run_cli(
    capability_code: str,
    summarize_fn: Callable[[Invocation], ReturnEnvelope],
    execute_fn: Callable[[Invocation], ReturnEnvelope],
    argv: list[str] | None = None,
) -> int:
    """Parse CLI args, dispatch to summarize or execute, emit stdout JSON.

    Returns exit code (0 = contract satisfied even on capability-level error;
    1 = envelope-contract violation — script bug, not capability failure).
    """
    parser = argparse.ArgumentParser(
        prog=f"python -m scripts.marcus_capabilities.{capability_code.lower().replace('-', '_')}",
        description=f"Marcus capability {capability_code} (dual-mode: summarize | execute).",
    )
    parser.add_argument("--mode", choices=("summarize", "execute"), required=True)
    parser.add_argument("--args", default="{}", help="JSON-encoded capability args")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--bundle-path", default=None)
    parser.add_argument("--idempotency-key", default=None)
    parsed = parser.parse_args(argv)

    try:
        args_obj = json.loads(parsed.args)
        if not isinstance(args_obj, dict):
            raise ValueError("--args must decode to a JSON object")
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"envelope-contract violation: bad --args: {exc}", file=sys.stderr)
        return 1

    invocation = Invocation(
        capability_code=capability_code,
        mode=parsed.mode,
        args=args_obj,
        context=InvocationContext(
            run_id=parsed.run_id,
            bundle_path=parsed.bundle_path,
            invoked_by="marcus",
        ),
        idempotency_key=parsed.idempotency_key,
    )

    started = time.perf_counter()
    envelope = summarize_fn(invocation) if parsed.mode == "summarize" else execute_fn(invocation)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    envelope.telemetry.setdefault("duration_ms", elapsed_ms)

    # stdout = JSON envelope only; logs go to stderr.
    with contextlib.suppress(AttributeError):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(envelope.to_dict(), indent=2, default=str))
    return 0
