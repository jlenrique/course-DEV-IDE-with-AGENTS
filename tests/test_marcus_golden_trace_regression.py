"""Golden-Trace byte-identical regression (AC-T.1, AC-B.5).

Re-runs the tracked-bundle-synthesis capture mode against the canonical
committed source bundle and compares normalized output byte-for-byte
against the committed fixture under ``tests/fixtures/golden_trace/marcus_pre_30-1/``.

At 30-1 close (no pipeline code movement): this test passes trivially
— the capture script produces the same output as when the fixture was
captured. At 30-2a close (code lifted into marcus/intake/): the test
actively guards byte-identity and any un-normalized diff fails the story.

R1 amendment 12 (Murat RED binding PDG) enforcement.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT: Path = Path(__file__).parent.parent.resolve()
_BUNDLE_DIR: Path = (
    _REPO_ROOT
    / "course-content"
    / "staging"
    / "tracked"
    / "source-bundles"
    / "apc-c1m1-tejal-20260409-motion"
)
_SOURCE_PATH: Path = (
    _REPO_ROOT
    / "course-content"
    / "courses"
    / "tejal-APC-C1"
    / "APC C1-M1 Tejal 2026-03-29.pdf"
)
_FIXTURE_DIR: Path = _REPO_ROOT / "tests" / "fixtures" / "golden_trace" / "marcus_pre_30-1"
_ENVELOPE_FILENAMES: tuple[str, ...] = (
    "step-01-ingestion-envelope.json",
    "step-02-source-quality-envelope.json",
    "step-03-audience-profile-envelope.json",
    "step-04-ingestion-quality-gate-envelope.json",
    "step-04-05-pre-packet-handoff-envelope.json",
)

_SKIP_REASON = (
    "Golden-trace source bundle or canonical PDF missing — capture script "
    "unable to synthesize envelopes. Expected in full trial-corpus checkouts."
)


@pytest.mark.skipif(
    not (_BUNDLE_DIR.is_dir() and _SOURCE_PATH.is_file()),
    reason=_SKIP_REASON,
)
def test_golden_trace_byte_identical_against_committed_fixture(tmp_path: Path) -> None:
    """AC-T.1 — normalized envelopes match committed fixture byte-for-byte.

    At 30-1 close this passes trivially (no pipeline code moves). Becomes
    load-bearing at 30-2a lift when the envelopes' origin changes.
    """
    assert _FIXTURE_DIR.is_dir(), (
        f"Committed fixture dir missing: {_FIXTURE_DIR}. "
        "Golden-Trace baseline must be committed before 30-1 opens."
    )

    output_dir = tmp_path / "capture"
    output_dir.mkdir()

    cmd = [
        sys.executable,
        "-m",
        "scripts.utilities.capture_marcus_golden_trace",
        "--source",
        str(_SOURCE_PATH),
        "--bundle-dir",
        str(_BUNDLE_DIR),
        "--output",
        str(output_dir),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(_REPO_ROOT), check=False
    )
    assert result.returncode == 0, (
        f"capture_marcus_golden_trace failed: stderr=\n{result.stderr}"
    )

    for filename in _ENVELOPE_FILENAMES:
        actual_path = output_dir / filename
        expected_path = _FIXTURE_DIR / filename
        assert actual_path.is_file(), (
            f"Captured envelope missing: {actual_path}"
        )
        actual = actual_path.read_text(encoding="utf-8")
        expected = expected_path.read_text(encoding="utf-8")
        # Normalize line endings only — fixture committed with LF; captures on
        # Windows may pick up CRLF on disk despite utf-8 write. Content equality
        # is what the AC asserts.
        actual_lf = actual.replace("\r\n", "\n")
        expected_lf = expected.replace("\r\n", "\n")
        assert actual_lf == expected_lf, (
            f"Byte-identity regression on {filename}.\n"
            f"First divergent character at index: "
            f"{_first_diff_index(actual_lf, expected_lf)}"
        )


def _first_diff_index(a: str, b: str) -> int:
    for i, (ca, cb) in enumerate(zip(a, b, strict=False)):
        if ca != cb:
            return i
    return min(len(a), len(b))


def test_fixture_files_are_all_present() -> None:
    """AC-T.1 — baseline fixture bundle is committed and complete."""
    assert _FIXTURE_DIR.is_dir()
    for filename in _ENVELOPE_FILENAMES:
        assert (_FIXTURE_DIR / filename).is_file(), (
            f"Golden-trace fixture missing: {filename}"
        )
    manifest = _FIXTURE_DIR / "golden-trace-manifest.yaml"
    assert manifest.is_file(), "golden-trace-manifest.yaml missing from fixture bundle"


def test_fixture_envelopes_are_valid_json_with_normalized_tokens() -> None:
    """AC-B.5 — committed fixtures parse as JSON and contain normalized tokens.

    Not a byte-identity pin — a shape-pin: each committed envelope is
    well-formed JSON and uses the locked normalization tokens rather than
    raw timestamps / UUIDs / SHA-256 / absolute paths.
    """
    timestamp_token_re = re.compile(r"\{\{TIMESTAMP\}\}")
    uuid_token_re = re.compile(r"\{\{UUID4\}\}")
    for filename in _ENVELOPE_FILENAMES:
        path = _FIXTURE_DIR / filename
        content = path.read_text(encoding="utf-8")
        # Parses as JSON.
        payload = json.loads(content)
        assert isinstance(payload, dict), f"{filename} is not a top-level object"
        # At least one normalization token is present — confirms normalization
        # was applied symmetrically at capture time.
        # (Not all envelopes contain timestamps; they all contain at least
        # one normalized token of some kind per the capture manifest.)
        has_any_normalization = (
            timestamp_token_re.search(content) is not None
            or uuid_token_re.search(content) is not None
        )
        assert has_any_normalization, (
            f"{filename} contains no normalization token; capture may have "
            "been skipped or normalization rules regressed."
        )
