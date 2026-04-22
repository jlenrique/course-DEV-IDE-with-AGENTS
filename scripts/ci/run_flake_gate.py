"""PDG-3 flake-detection gate.

Runs ``pytest -k "<selector>" -p no:cacheprovider`` N times in sequence and
fails if any run diverges from the others (different exit code, different
pass/fail/error counts, or different collected-node count).

Binding per Story 27-2.5 §Pre-Development Gate PDG-3 and extended to PR-R per
Murat's Sprint #1 roster rider #6.

Usage:
    python scripts/ci/run_flake_gate.py [--selector SEL] [--runs N]

Defaults:
    --selector "cross_validate or retrieval_dispatcher"
    --runs 3
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass

DEFAULT_SELECTOR = "cross_validate or retrieval_dispatcher"
DEFAULT_RUNS = 3

_SUMMARY_RE = re.compile(
    r"(?P<passed>\d+) passed"
    r"(?:, (?P<failed>\d+) failed)?"
    r"(?:, (?P<errors>\d+) error[s]?)?"
    r"(?:, (?P<skipped>\d+) skipped)?"
    r"(?:, (?P<xfailed>\d+) xfailed)?"
    r"(?:, (?P<xpassed>\d+) xpassed)?"
    r"(?:, (?P<deselected>\d+) deselected)?"
)


@dataclass(frozen=True)
class RunOutcome:
    exit_code: int
    passed: int
    failed: int
    errors: int
    skipped: int
    xfailed: int
    xpassed: int
    deselected: int
    raw_tail: str

    def signature(self) -> tuple[int, int, int, int, int, int, int, int]:
        return (
            self.exit_code,
            self.passed,
            self.failed,
            self.errors,
            self.skipped,
            self.xfailed,
            self.xpassed,
            self.deselected,
        )


def _parse_summary(stdout: str) -> tuple[int, int, int, int, int, int, int]:
    for line in reversed(stdout.splitlines()):
        m = _SUMMARY_RE.search(line)
        if not m:
            continue
        return (
            int(m.group("passed") or 0),
            int(m.group("failed") or 0),
            int(m.group("errors") or 0),
            int(m.group("skipped") or 0),
            int(m.group("xfailed") or 0),
            int(m.group("xpassed") or 0),
            int(m.group("deselected") or 0),
        )
    return (0, 0, 0, 0, 0, 0, 0)


def _run_once(selector: str) -> RunOutcome:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-k",
        selector,
        "-p",
        "no:cacheprovider",
        "--tb=line",
        "-q",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    passed, failed, errors, skipped, xfailed, xpassed, deselected = _parse_summary(
        proc.stdout
    )
    tail_lines = proc.stdout.splitlines()[-3:] if proc.stdout else []
    return RunOutcome(
        exit_code=proc.returncode,
        passed=passed,
        failed=failed,
        errors=errors,
        skipped=skipped,
        xfailed=xfailed,
        xpassed=xpassed,
        deselected=deselected,
        raw_tail="\n".join(tail_lines),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selector", default=DEFAULT_SELECTOR)
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    args = parser.parse_args()

    print(f"PDG-3 flake gate: {args.runs}x `pytest -k \"{args.selector}\"`")
    outcomes: list[RunOutcome] = []
    for idx in range(1, args.runs + 1):
        print(f"  run {idx}/{args.runs}...", end=" ", flush=True)
        outcome = _run_once(args.selector)
        outcomes.append(outcome)
        print(
            f"exit={outcome.exit_code} "
            f"passed={outcome.passed} failed={outcome.failed} "
            f"errors={outcome.errors} skipped={outcome.skipped} "
            f"xfailed={outcome.xfailed} deselected={outcome.deselected}"
        )

    signatures = {o.signature() for o in outcomes}
    if len(signatures) > 1:
        print("\nFLAKE DETECTED — outcomes diverged across runs:")
        for idx, outcome in enumerate(outcomes, 1):
            print(f"  run {idx} signature: {outcome.signature()}")
            if outcome.raw_tail:
                print(f"    tail: {outcome.raw_tail}")
        return 1

    sig = outcomes[0]
    if sig.exit_code != 0 or sig.failed > 0 or sig.errors > 0:
        print(
            f"\nGATE FAILED — all {args.runs} runs agree but outcome is "
            f"not green: {sig.signature()}"
        )
        if sig.raw_tail:
            print(f"tail: {sig.raw_tail}")
        return 1

    print(f"\nPDG-3 GREEN — {args.runs}x runs converged on {sig.passed} passed, 0 flake detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
