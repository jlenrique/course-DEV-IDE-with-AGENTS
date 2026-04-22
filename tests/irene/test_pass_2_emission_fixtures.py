"""T1 fixture-load tests for Sprint #1 §7.1 Irene Pass 2 authoring template.

Asserts T1-harvested fixtures exist, parse, and carry the structural shapes
each variant is supposed to exhibit. Real validator/schema assertions land in
T2-T10; this file anchors the fixtures so T2+ can extend coverage without
re-locating them.

Fixtures covered:
- trial_c1m1_as_emitted.yaml (literal trial artifact; exhibits all three
  §6.3/§6.4/§6.5 failure modes in-situ)
- trial_c1m1_canonical.yaml (minimal 2-segment canonical with all three
  durable fixes applied; AC-T.3 regression canary target)
- malformed_6_3_duplicate_motion_keys.yaml
- malformed_6_4_missing_visual_file.yaml
- malformed_6_5_null_motion_duration.yaml
- motion_gate_receipts/trial_c1m1_motion_gate_receipt.json (cross-validation
  counterparty for AC-B.3 / AC-T.4 upstream-reference check)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

FIXTURE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "7-1-irene-pass-2-authoring-template"
)
PASS_2_DIR = FIXTURE_ROOT / "pass_2_emissions"
RECEIPT_DIR = FIXTURE_ROOT / "motion_gate_receipts"


def _load_yaml(name: str) -> dict:
    return yaml.safe_load((PASS_2_DIR / name).read_text(encoding="utf-8"))


def _segment_by_id(manifest: dict, segment_id: str) -> dict:
    for seg in manifest["segments"]:
        if seg["id"] == segment_id:
            return seg
    raise KeyError(segment_id)


@pytest.mark.parametrize(
    "fixture_name",
    [
        "trial_c1m1_as_emitted.yaml",
        "trial_c1m1_canonical.yaml",
        "malformed_6_3_duplicate_motion_keys.yaml",
        "malformed_6_4_missing_visual_file.yaml",
        "malformed_6_5_null_motion_duration.yaml",
    ],
)
def test_pass_2_fixture_is_valid_yaml_with_segments(fixture_name):
    manifest = _load_yaml(fixture_name)
    assert manifest["schema_version"] == "1.1"
    assert manifest["run_id"] == "C1-M1-PRES-20260419B"
    assert isinstance(manifest["segments"], list) and manifest["segments"]


def test_as_emitted_fixture_exhibits_6_3_duplicate_motion_keys():
    manifest = _load_yaml("trial_c1m1_as_emitted.yaml")
    card_01 = _segment_by_id(manifest, "apc-c1m1-tejal-20260419b-motion-card-01")
    assert "motion_asset" in card_01
    assert "motion_asset_path" in card_01


def test_as_emitted_fixture_exhibits_6_4_missing_visual_file():
    manifest = _load_yaml("trial_c1m1_as_emitted.yaml")
    non_card_01 = [
        s
        for s in manifest["segments"]
        if s["id"] != "apc-c1m1-tejal-20260419b-motion-card-01"
    ]
    assert all("visual_file" not in s for s in non_card_01), (
        "§6.4: cards 02-14 should be missing visual_file in as-emitted fixture"
    )


def test_as_emitted_fixture_exhibits_6_5_null_or_missing_motion_duration():
    manifest = _load_yaml("trial_c1m1_as_emitted.yaml")
    card_01 = _segment_by_id(manifest, "apc-c1m1-tejal-20260419b-motion-card-01")
    assert card_01.get("motion_duration_seconds") in (None,)


def test_canonical_fixture_has_all_three_fixes_applied():
    manifest = _load_yaml("trial_c1m1_canonical.yaml")
    card_01 = _segment_by_id(manifest, "apc-c1m1-tejal-20260419b-motion-card-01")
    card_02 = _segment_by_id(manifest, "apc-c1m1-tejal-20260419b-motion-card-02")

    assert "motion_asset" not in card_01, "§6.3 fix: legacy key must be absent"
    assert card_01["motion_asset_path"] == "motion/slide-01-motion.mp4"

    assert card_01["visual_file"], "§6.4 fix: card-01 visual_file populated"
    assert card_02["visual_file"], "§6.4 fix: card-02 visual_file populated"

    assert card_01["motion_duration_seconds"] == 5.041, (
        "§6.5 fix: carried forward from Motion Gate receipt"
    )


def test_malformed_6_3_reintroduces_duplicate_motion_keys_on_card_01():
    manifest = _load_yaml("malformed_6_3_duplicate_motion_keys.yaml")
    card_01 = _segment_by_id(manifest, "apc-c1m1-tejal-20260419b-motion-card-01")
    assert "motion_asset" in card_01
    assert "motion_asset_path" in card_01


def test_malformed_6_4_strips_visual_file_on_static_segment():
    manifest = _load_yaml("malformed_6_4_missing_visual_file.yaml")
    card_02 = _segment_by_id(manifest, "apc-c1m1-tejal-20260419b-motion-card-02")
    assert card_02["visual_mode"] == "static"
    assert "visual_file" not in card_02


def test_malformed_6_5_sets_motion_duration_null_despite_receipt_value():
    manifest = _load_yaml("malformed_6_5_null_motion_duration.yaml")
    card_01 = _segment_by_id(manifest, "apc-c1m1-tejal-20260419b-motion-card-01")
    assert card_01["motion_duration_seconds"] is None


def test_motion_gate_receipt_fixture_is_valid_json_with_duration():
    receipt_path = RECEIPT_DIR / "trial_c1m1_motion_gate_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["run_id"] == "C1-M1-PRES-20260419B"
    assert receipt["gate_decision"] == "approved"
    non_static = receipt["non_static_slides"]
    assert len(non_static) == 1
    assert non_static[0]["slide_id"] == "apc-c1m1-tejal-20260419b-motion-card-01"
    assert non_static[0]["duration_seconds"] == 5.041


def test_receipt_duration_matches_canonical_motion_duration_seconds():
    """Cross-artifact pin per Murat rider — guards AC-T.4 cross-reference.

    If Motion Gate receipt schema changes `duration_seconds` shape, OR the
    canonical fixture drifts away from the receipt, this fails loudly. The
    T5 Motion Gate receipt reader module will consume this same pair.
    """
    receipt_path = RECEIPT_DIR / "trial_c1m1_motion_gate_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt_duration = receipt["non_static_slides"][0]["duration_seconds"]

    canonical = _load_yaml("trial_c1m1_canonical.yaml")
    card_01 = _segment_by_id(canonical, "apc-c1m1-tejal-20260419b-motion-card-01")

    assert card_01["motion_duration_seconds"] == receipt_duration
