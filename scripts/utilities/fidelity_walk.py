"""Backward-compatible wrapper for the canonical structural walk."""

from __future__ import annotations

from scripts.utilities.structural_walk import *  # noqa: F401,F403
from scripts.utilities.structural_walk import main as _structural_main


def main(argv: list[str] | None = None) -> int:
    print(
        "Legacy alias 'python -m scripts.utilities.fidelity_walk' invoked. "
        "Canonical command: python -m scripts.utilities.structural_walk --workflow standard"
    )
    return _structural_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
