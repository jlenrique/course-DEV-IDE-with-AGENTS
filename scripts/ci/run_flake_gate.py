"""PDG-3 flake-detection gate.

Runs ``pytest -k "<selector>" -p no:cacheprovider`` N times in sequence and
fails if any run diverges from the others (different exit code, different
pass/fail/error counts, or different collected-node count).

Binding per Story 27-2.5 Pre-Development Gate PDG-3 and extended to PR-R per
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
# Subprocess timeout (seconds) — upper bound on any single pytest run in the
# gate. Prevents a deadlocked test from hanging the gate indefinitely. The
# flake-gate slice is expected to complete in seconds; anything approaching
# this bound is itself a signal worth investigating.
_RUN_TIMEOUT_SECONDS = 600
# Pytest terminal-summary sentinel: authoritative summary line ends with
# `in <duration>` where duration is one of:
#   - "0.03s"                         (sub-minute, fractional seconds)
#   - "65.00s (0:01:05)"              (long form with HH:MM:SS suffix)
#   - "1m5s" / "1h2m3s"               (compact multi-unit when no seconds
#                                      decimal; pytest emits this for
#                                      sessions exceeding format_session_duration thresholds)
# Used to anchor the regex to the real summary, not stray `"5 passed"`
# strings elsewhere in stdout (tracebacks, log messages, assertion text).
_SUMMARY_TAIL_RE = re.compile(
    r"\bin (?:\d+h)?(?:\d+m)?[\d.]+s(?:\s*\([\d:]+\))?\s*$"
)
# Individual-count patterns (each optional). Parsed independently so we
# don't require a fixed ordering or require `passed` to be present.
_COUNT_PATTERNS: dict[str, re.Pattern[str]] = {
    "passed": re.compile(r"(\d+) passed\b"),
    "failed": re.compile(r"(\d+) failed\b"),
    "errors": re.compile(r"(\d+) errors?\b"),
    "skipped": re.compile(r"(\d+) skipped\b"),
    "xfailed": re.compile(r"(\d+) xfailed\b"),
    "xpassed": re.compile(r"(\d+) xpassed\b"),
    "deselected": re.compile(r"(\d+) deselected\b"),
}


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
    parser_recognized_summary: bool = True
    # Distinct from exit_code because POSIX reports signal-killed processes
    # as negative numbers (e.g. SIGHUP = -1), which would collide with an
    # exit_code sentinel for "timed out." Thread timeout as its own flag so
    # signal-killed and timed-out runs are never mistaken for one another
    # in signature comparison.
    timed_out: bool = False

    def signature(
        self,
    ) -> tuple[int, int, int, int, int, int, int, int, bool, bool]:
        # parser_recognized_summary is part of signature so "zero-tuple
        # because we couldn't parse any summary" is NOT confused with a
        # genuine "0 passed" outcome. timed_out is part of signature so
        # a timeout is not confused with a signal-killed (same exit_code)
        # or with a non-terminating parse failure.
        return (
            self.exit_code,
            self.passed,
            self.failed,
            self.errors,
            self.skipped,
            self.xfailed,
            self.xpassed,
            self.deselected,
            self.parser_recognized_summary,
            self.timed_out,
        )


def _parse_summary(stdout: str) -> tuple[dict[str, int], bool]:
    """Parse pytest's terminal summary, anchoring on the ``in <n>s`` tail.

    Returns (counts_dict, recognized). ``recognized`` is True iff we matched
    an authoritative summary line. Used by callers to distinguish a genuine
    all-zero result from an unparseable output.
    """
    for line in reversed(stdout.splitlines()):
        if not _SUMMARY_TAIL_RE.search(line):
            continue
        counts: dict[str, int] = {}
        for key, pattern in _COUNT_PATTERNS.items():
            match = pattern.search(line)
            counts[key] = int(match.group(1)) if match else 0
        # Only recognize a summary line that carries at least one real
        # outcome count — otherwise we match any random `"foo in 1.5s"`
        # line (e.g., verbose duration plugin output).
        if any(counts.values()) or re.search(r"no tests ran", line):
            return counts, True
    return {k: 0 for k in _COUNT_PATTERNS}, False


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
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=_RUN_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        return RunOutcome(
            exit_code=0,  # intentionally 0; timed_out carries the signal
            passed=0,
            failed=0,
            errors=0,
            skipped=0,
            xfailed=0,
            xpassed=0,
            deselected=0,
            raw_tail=(
                f"[timeout after {_RUN_TIMEOUT_SECONDS}s]\n"
                + "\n".join(partial.splitlines()[-3:] if partial else [])
            ),
            parser_recognized_summary=False,
            timed_out=True,
        )

    counts, recognized = _parse_summary(proc.stdout)
    tail_lines = proc.stdout.splitlines()[-3:] if proc.stdout else []
    return RunOutcome(
        exit_code=proc.returncode,
        passed=counts["passed"],
        failed=counts["failed"],
        errors=counts["errors"],
        skipped=counts["skipped"],
        xfailed=counts["xfailed"],
        xpassed=counts["xpassed"],
        deselected=counts["deselected"],
        raw_tail="\n".join(tail_lines),
        parser_recognized_summary=recognized,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "PDG-3 flake-detection gate: run a pytest slice N times and "
            "fail if outcomes diverge or any run is not green."
        )
    )
    parser.add_argument("--selector", default=DEFAULT_SELECTOR)
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    args = parser.parse_args()

    if args.runs < 2:
        parser.error("--runs must be >= 2 (flake detection requires comparing runs)")

    print(f"PDG-3 flake gate: {args.runs}x `pytest -k \"{args.selector}\"`")
    outcomes: list[RunOutcome] = []
    for idx in range(1, args.runs + 1):
        print(f"  run {idx}/{args.runs}...", end=" ", flush=True)
        outcome = _run_once(args.selector)
        outcomes.append(outcome)
        summary_note = (
            "" if outcome.parser_recognized_summary else " [NO PARSEABLE SUMMARY]"
        )
        print(
            f"exit={outcome.exit_code} "
            f"passed={outcome.passed} failed={outcome.failed} "
            f"errors={outcome.errors} skipped={outcome.skipped} "
            f"xfailed={outcome.xfailed} deselected={outcome.deselected}"
            f"{summary_note}"
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

    # Fail closed when we couldn't parse a summary on any run — a crash
    # (segfault, import error) or a timeout yields zero outcome counts
    # that must never be confused with "3 consecutive green runs."
    if sig.timed_out:
        print(
            f"\nGATE FAILED — pytest timed out on all {args.runs} runs "
            f"(timeout={_RUN_TIMEOUT_SECONDS}s). Likely deadlock or "
            f"hang in the test slice."
        )
        if sig.raw_tail:
            print(f"tail: {sig.raw_tail}")
        return 1

    if not sig.parser_recognized_summary:
        print(
            f"\nGATE FAILED — could not parse pytest terminal summary across "
            f"{args.runs} runs (likely crash, import error, or unexpected "
            f"pytest output format). signature={sig.signature()}"
        )
        if sig.raw_tail:
            print(f"tail: {sig.raw_tail}")
        return 1

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
