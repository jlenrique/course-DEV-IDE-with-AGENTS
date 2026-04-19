"""Contract parity test: PR-PF preflight receipt ↔ Prompt 2 consumer schema
(AC-B.4 from story 26-6).

Defect class guarded: the preflight receipt PR-PF emits (pass-through of
``emit_preflight_receipt.py`` / ``run_readiness``) drifts in shape from what
Prompt 2 consumes downstream. Same defect class as the 2026-04-17 halt — a
schema-drift that doesn't surface until the trial fires.

This test pins the canonical receipt key set (``overall_status``, ``checks``,
``root``, ``timestamp``) as the cross-stage contract. If the runner's output
shape changes without the consumer being updated (or vice versa), this test
trips at co-commit time.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from scripts.marcus_capabilities import pr_pf
from scripts.marcus_capabilities._shared import Invocation, InvocationContext
from scripts.utilities.app_session_readiness import run_readiness

pytestmark = pytest.mark.trial_critical

# The field set Prompt 2 expects in the preflight receipt. Derived from
# scripts/utilities/emit_preflight_receipt.py, which is the canonical
# generator Marcus delegates to. If this set drifts, this test AND the
# downstream consumer must update in the same commit.
PROMPT_2_RECEIPT_FIELDS = frozenset({"overall_status", "checks", "root", "timestamp"})


def test_run_readiness_emits_canonical_receipt_shape() -> None:
    """The authoritative receipt generator emits the agreed field set."""
    report = run_readiness()
    missing = PROMPT_2_RECEIPT_FIELDS - set(report.keys())
    assert not missing, (
        f"run_readiness() dropped canonical receipt field(s): {sorted(missing)}. "
        f"This is the schema Prompt 2 consumes — update both sides in the same commit."
    )


def test_pr_pf_passes_through_canonical_receipt_fields() -> None:
    """PR-PF execute mode must preserve the canonical receipt fields in
    ``envelope.result.readiness`` — it's a thin wrapper, the shape the
    runner emits is the shape Prompt 2 receives."""
    fake_receipt = {
        "overall_status": "PASS",
        "checks": [{"name": "python_version", "status": "PASS"}],
        "root": "/repo",
        "timestamp": "2026-04-17T12:00:00Z",
    }
    invocation = Invocation(
        capability_code="PR-PF",
        mode="execute",
        args={},
        context=InvocationContext(run_id="PF-CONTRACT-1", invoked_by="marcus"),
    )
    with patch.object(
        pr_pf, "_run_subprocess", return_value=(0, json.dumps(fake_receipt), "")
    ):
        envelope = pr_pf.execute(invocation)
    assert envelope.status == "ok"
    passed_through = envelope.result["readiness"]
    missing = PROMPT_2_RECEIPT_FIELDS - set(passed_through.keys())
    assert not missing, (
        f"PR-PF dropped canonical receipt field(s) during pass-through: "
        f"{sorted(missing)}. Thin wrapper should preserve runner JSON verbatim."
    )
    assert passed_through["overall_status"] == "PASS"


def test_pr_pf_preflight_passed_requires_parsed_verdict() -> None:
    """Companion to AC-B.4 parity: preflight_passed=True must only fire
    when we have a parsed verdict, not on bare exit=0. Otherwise a runner
    emitting non-JSON could silently report PASS to Marcus."""
    invocation = Invocation(
        capability_code="PR-PF",
        mode="execute",
        args={},
        context=InvocationContext(run_id="PF-CONTRACT-2", invoked_by="marcus"),
    )
    # Exit 0 with non-JSON stdout: must NOT claim preflight_passed=True.
    with patch.object(pr_pf, "_run_subprocess", return_value=(0, "oops not json", "")):
        envelope = pr_pf.execute(invocation)
    assert envelope.result["preflight_passed"] is False
