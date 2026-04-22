"""T4 tests for the Pass 2 emission lint validator.

Wraps Story §7.1 structural schema (T2) + upstream Motion Gate receipt reader
(T5) into a single fail-closed validator Pass 2 pipelines invoke before
Storyboard B render. Pure function + thin CLI wrapper.

Contract tested here:
- lint_manifest(manifest, receipt_durations) -> list[LintFinding]
  Returns empty list when clean; one finding per violation otherwise.
- LintFinding carries kind ('§6.3' | '§6.4' | '§6.5-null' | '§6.5-mismatch' |
  'schema'), segment_id, and a human-readable detail string.
- run_cli([--manifest PATH, --motion-gate-receipt PATH]) -> int
  Exit 0 on clean; exit 1 on violations; exit 2 on infrastructure errors
  (missing files, malformed inputs).
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LINT_PATH = _REPO_ROOT / "scripts" / "validators" / "pass_2_emission_lint.py"
_spec = importlib.util.spec_from_file_location("pass_2_emission_lint", _LINT_PATH)
assert _spec is not None and _spec.loader is not None
lint = importlib.util.module_from_spec(_spec)
sys.modules["pass_2_emission_lint"] = lint
_spec.loader.exec_module(lint)

FIXTURE_ROOT = (
    _REPO_ROOT / "tests" / "fixtures" / "7-1-irene-pass-2-authoring-template"
)
PASS_2_DIR = FIXTURE_ROOT / "pass_2_emissions"
RECEIPT_DIR = FIXTURE_ROOT / "motion_gate_receipts"
RECEIPT = RECEIPT_DIR / "trial_c1m1_motion_gate_receipt.json"


def _load(name: str) -> dict:
    return yaml.safe_load((PASS_2_DIR / name).read_text(encoding="utf-8"))


def test_canonical_manifest_has_no_findings():
    manifest = _load("trial_c1m1_canonical.yaml")
    durations = {"apc-c1m1-tejal-20260419b-motion-card-01": 5.041}
    findings = lint.lint_manifest(manifest, durations)
    assert findings == [], f"Canonical must lint clean. Got: {findings}"


def test_malformed_6_3_reports_legacy_key_finding():
    manifest = _load("malformed_6_3_duplicate_motion_keys.yaml")
    findings = lint.lint_manifest(manifest, {})
    assert any(f.kind == "§6.3" for f in findings)
    card_01_findings = [f for f in findings if f.kind == "§6.3"]
    assert any(
        "motion-card-01" in f.segment_id for f in card_01_findings
    )


def test_malformed_6_4_reports_missing_visual_file_finding():
    manifest = _load("malformed_6_4_missing_visual_file.yaml")
    findings = lint.lint_manifest(manifest, {})
    assert any(f.kind == "§6.4" for f in findings)
    assert any("motion-card-02" in f.segment_id for f in findings if f.kind == "§6.4")


def test_malformed_6_5_null_duration_reports_null_finding():
    manifest = _load("malformed_6_5_null_motion_duration.yaml")
    durations = {"apc-c1m1-tejal-20260419b-motion-card-01": 5.041}
    findings = lint.lint_manifest(manifest, durations)
    assert any(f.kind == "§6.5-null" for f in findings)
    null_finding = next(f for f in findings if f.kind == "§6.5-null")
    assert "motion-card-01" in null_finding.segment_id


def test_lint_detects_receipt_value_mismatch_separately_from_null():
    """If manifest carries a concrete duration that disagrees with the
    receipt, lint reports §6.5-mismatch (distinct from §6.5-null)."""
    manifest = _load("trial_c1m1_canonical.yaml")
    # Manifest says 5.041; pretend receipt says 7.0 — disagreement.
    durations = {"apc-c1m1-tejal-20260419b-motion-card-01": 7.0}
    findings = lint.lint_manifest(manifest, durations)
    mismatch = [f for f in findings if f.kind == "§6.5-mismatch"]
    assert mismatch, "Duration disagreement must surface as §6.5-mismatch"
    assert "5.041" in mismatch[0].detail and "7.0" in mismatch[0].detail


def test_lint_detects_motion_slide_missing_from_receipt():
    """Motion segment in manifest without a matching receipt entry is a
    §6.5-null violation (upstream says 'no motion approved for this slide')."""
    manifest = _load("trial_c1m1_canonical.yaml")
    # Empty durations — receipt doesn't know about any motion slide.
    findings = lint.lint_manifest(manifest, {})
    assert any(f.kind == "§6.5-null" for f in findings)


def test_as_emitted_manifest_accumulates_all_three_finding_kinds():
    manifest = _load("trial_c1m1_as_emitted.yaml")
    durations = {"apc-c1m1-tejal-20260419b-motion-card-01": 5.041}
    findings = lint.lint_manifest(manifest, durations)
    kinds = {f.kind for f in findings}
    assert "§6.3" in kinds
    assert "§6.4" in kinds
    assert "§6.5-null" in kinds


def test_lint_is_deterministic_across_multiple_invocations():
    """AC-C.2 — Lint output is pure function of inputs; no network, no
    clock, no randomness."""
    manifest = _load("malformed_6_3_duplicate_motion_keys.yaml")
    a = lint.lint_manifest(manifest, {})
    b = lint.lint_manifest(manifest, {})
    c = lint.lint_manifest(manifest, {})
    assert [(f.kind, f.segment_id, f.detail) for f in a] == [
        (f.kind, f.segment_id, f.detail) for f in b
    ] == [(f.kind, f.segment_id, f.detail) for f in c]


def test_cli_exits_zero_on_clean_canonical_manifest(tmp_path):
    # Use the real canonical + real receipt
    canonical = PASS_2_DIR / "trial_c1m1_canonical.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            str(_LINT_PATH),
            "--manifest",
            str(canonical),
            "--motion-gate-receipt",
            str(RECEIPT),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"stdout={proc.stdout!r} stderr={proc.stderr!r}"


def test_cli_exits_one_on_malformed_manifest(tmp_path):
    malformed = PASS_2_DIR / "malformed_6_3_duplicate_motion_keys.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            str(_LINT_PATH),
            "--manifest",
            str(malformed),
            "--motion-gate-receipt",
            str(RECEIPT),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    # Every finding surfaces the segment id and kind in stdout for operator
    # triage.
    assert "§6.3" in proc.stdout or "motion_asset" in proc.stdout


def test_cli_exits_two_on_missing_manifest(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            str(_LINT_PATH),
            "--manifest",
            str(tmp_path / "does-not-exist.yaml"),
            "--motion-gate-receipt",
            str(RECEIPT),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2


def test_cli_exits_two_on_missing_receipt(tmp_path):
    canonical = PASS_2_DIR / "trial_c1m1_canonical.yaml"
    proc = subprocess.run(
        [
            sys.executable,
            str(_LINT_PATH),
            "--manifest",
            str(canonical),
            "--motion-gate-receipt",
            str(tmp_path / "missing-receipt.json"),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2


@pytest.mark.parametrize(
    "fixture,expected_kinds",
    [
        ("malformed_6_3_duplicate_motion_keys.yaml", {"§6.3"}),
        ("malformed_6_4_missing_visual_file.yaml", {"§6.4"}),
        ("malformed_6_5_null_motion_duration.yaml", {"§6.5-null"}),
    ],
)
def test_each_malformed_variant_isolates_its_target_failure_kind(
    fixture, expected_kinds
):
    """Each malformed fixture should surface AT LEAST the variant's kind.
    Other findings may surface if the fixture has a natural secondary shape,
    but the target kind must be present.
    """
    manifest = _load(fixture)
    durations = {"apc-c1m1-tejal-20260419b-motion-card-01": 5.041}
    findings = lint.lint_manifest(manifest, durations)
    kinds = {f.kind for f in findings}
    missing = expected_kinds - kinds
    assert not missing, (
        f"Expected kinds {expected_kinds} to surface, missing {missing}. Got {kinds}"
    )
