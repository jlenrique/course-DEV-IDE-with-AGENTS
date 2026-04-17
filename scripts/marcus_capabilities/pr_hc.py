"""PR-HC — Health Check (stub).

Currently registered with pinned contracts and a canonical NOT_YET_IMPLEMENTED
envelope. Full implementation scheduled for story 26-10.

Invocation:
    python -m scripts.marcus_capabilities.pr_hc --mode summarize
    python -m scripts.marcus_capabilities.pr_hc --mode execute
"""

from __future__ import annotations

import sys

from scripts.marcus_capabilities._shared import (
    Invocation,
    ReturnEnvelope,
    run_cli,
    stub_envelope,
)


def summarize(invocation: Invocation) -> ReturnEnvelope:
    """Stub summarize — operator-observable NOT_YET_IMPLEMENTED envelope (AC-B.3)."""
    return stub_envelope("PR-HC", invocation)


def execute(invocation: Invocation) -> ReturnEnvelope:
    """Stub execute — identical envelope to summarize."""
    return stub_envelope("PR-HC", invocation)


def main(argv: list[str] | None = None) -> int:
    return run_cli("PR-HC", summarize, execute, argv)


if __name__ == "__main__":
    sys.exit(main())
