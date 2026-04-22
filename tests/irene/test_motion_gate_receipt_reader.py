"""T5 tests for Motion Gate receipt reader.

Reader module satisfies Amelia's separation-of-concerns rider: Motion Gate
receipt parsing lives in its own module, NOT inlined in the lint validator
(§7.1 AC-B.3 upstream-reference check). The lint consumes the reader's
published interface; if Motion Gate receipt format evolves, only this module
updates.

Contract tested here:
- read_motion_durations(receipt_path) → dict[slide_id, duration_seconds]
  (only non_static_slides with approved gate_decision)
- load_receipt(receipt_path) → raw JSON (for lint's audit trail use)
- MotionGateReceiptError raised on: missing file, malformed JSON, missing
  required keys, unapproved gate_decision, negative/zero duration, duplicate
  slide_id in non_static_slides
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from skills.bmad_agent_content_creator.scripts.motion_gate_receipt_reader import (
    MotionGateReceiptError,
    load_receipt,
    read_motion_durations,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_RECEIPT = (
    _REPO_ROOT
    / "tests"
    / "fixtures"
    / "7-1-irene-pass-2-authoring-template"
    / "motion_gate_receipts"
    / "trial_c1m1_motion_gate_receipt.json"
)


def test_read_motion_durations_returns_slide_id_to_duration_mapping():
    durations = read_motion_durations(FIXTURE_RECEIPT)
    assert durations == {"apc-c1m1-tejal-20260419b-motion-card-01": 5.041}


def test_load_receipt_returns_raw_json_payload():
    receipt = load_receipt(FIXTURE_RECEIPT)
    assert receipt["run_id"] == "C1-M1-PRES-20260419B"
    assert receipt["gate_decision"] == "approved"
    assert receipt["coverage"]["video"] == 1


def test_read_motion_durations_missing_file_raises(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    with pytest.raises(MotionGateReceiptError, match="not found"):
        read_motion_durations(missing)


def test_read_motion_durations_malformed_json_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(MotionGateReceiptError, match="malformed"):
        read_motion_durations(bad)


def test_read_motion_durations_missing_gate_decision_raises(tmp_path):
    incomplete = tmp_path / "incomplete.json"
    incomplete.write_text(
        json.dumps({"run_id": "X", "non_static_slides": []}), encoding="utf-8"
    )
    with pytest.raises(MotionGateReceiptError, match="gate_decision"):
        read_motion_durations(incomplete)


def test_read_motion_durations_unapproved_gate_raises(tmp_path):
    unapproved = tmp_path / "unapproved.json"
    unapproved.write_text(
        json.dumps(
            {
                "run_id": "X",
                "gate_decision": "blocked",
                "non_static_slides": [],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(MotionGateReceiptError, match="approved"):
        read_motion_durations(unapproved)


def test_read_motion_durations_missing_non_static_slides_raises(tmp_path):
    missing_slides = tmp_path / "missing.json"
    missing_slides.write_text(
        json.dumps({"run_id": "X", "gate_decision": "approved"}), encoding="utf-8"
    )
    with pytest.raises(MotionGateReceiptError, match="non_static_slides"):
        read_motion_durations(missing_slides)


def test_read_motion_durations_duplicate_slide_id_raises(tmp_path):
    dup = tmp_path / "dup.json"
    dup.write_text(
        json.dumps(
            {
                "run_id": "X",
                "gate_decision": "approved",
                "non_static_slides": [
                    {"slide_id": "s1", "duration_seconds": 3.0},
                    {"slide_id": "s1", "duration_seconds": 4.0},
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(MotionGateReceiptError, match="duplicate"):
        read_motion_durations(dup)


def test_read_motion_durations_non_positive_duration_raises(tmp_path):
    bad_duration = tmp_path / "bad_dur.json"
    bad_duration.write_text(
        json.dumps(
            {
                "run_id": "X",
                "gate_decision": "approved",
                "non_static_slides": [{"slide_id": "s1", "duration_seconds": 0}],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(MotionGateReceiptError, match="duration"):
        read_motion_durations(bad_duration)


def test_read_motion_durations_missing_slide_id_in_entry_raises(tmp_path):
    missing_field = tmp_path / "missing_field.json"
    missing_field.write_text(
        json.dumps(
            {
                "run_id": "X",
                "gate_decision": "approved",
                "non_static_slides": [{"duration_seconds": 3.0}],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(MotionGateReceiptError, match="slide_id"):
        read_motion_durations(missing_field)


def test_read_motion_durations_accepts_empty_non_static_slides(tmp_path):
    static_only = tmp_path / "static_only.json"
    static_only.write_text(
        json.dumps(
            {
                "run_id": "X",
                "gate_decision": "approved",
                "non_static_slides": [],
            }
        ),
        encoding="utf-8",
    )
    assert read_motion_durations(static_only) == {}
