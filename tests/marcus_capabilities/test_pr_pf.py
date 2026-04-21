"""PR-PF (Preflight) capability tests (AC-T.3 from story 26-6).

Subprocess test is the highest flakiness risk area per Murat's green-light
guardrails. We MOCK the subprocess runner — do NOT shell out to the real
``app_session_readiness`` in CI. Test the wrapper contract, not the
downstream script.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from scripts.marcus_capabilities import pr_pf
from scripts.marcus_capabilities._shared import Invocation, InvocationContext

# test_pr_pf.py is NOT marked trial_critical — the subprocess boundary has
# inherent flakiness potential (per Murat). The wrapping contract (shared
# envelope shape) IS covered trial_critically in test_landing_point_contract.py.


def _invoke(mode: str, **args) -> Invocation:
    return Invocation(
        capability_code="PR-PF",
        mode=mode,
        args=args,
        context=InvocationContext(
            run_id="PF-TEST-1",
            bundle_path="some/bundle",
            invoked_by="marcus",
        ),
    )


def test_summarize_reports_plan_without_touching_disk() -> None:
    envelope = pr_pf.summarize(_invoke("summarize"))
    assert envelope.status == "ok"
    assert envelope.capability_code == "PR-PF"
    assert "plan" in envelope.result
    plan_text = "\n".join(envelope.result["plan"])
    assert "app_session_readiness" in plan_text
    assert "--with-preflight" in plan_text
    assert "some/bundle" in plan_text
    assert "session-preflight-receipt.json" in plan_text


def test_execute_passes_on_zero_exit() -> None:
    """AC-T.3: subprocess returns 0 + JSON; envelope status must be 'ok'."""
    fake_stdout = json.dumps({"verdict": "PASS", "checks": []})
    with patch.object(pr_pf, "_run_subprocess", return_value=(0, fake_stdout, "")):
        envelope = pr_pf.execute(_invoke("execute"))
    assert envelope.status == "ok"
    assert envelope.result["preflight_passed"] is True
    assert envelope.result["readiness"]["verdict"] == "PASS"
    assert envelope.errors == []


def test_execute_propagates_nonzero_exit() -> None:
    """AC-T.3 core: non-zero exit maps to status=error + PREFLIGHT_FAILED in errors[]."""
    with patch.object(
        pr_pf, "_run_subprocess", return_value=(2, "{}", "something broke\n")
    ):
        envelope = pr_pf.execute(_invoke("execute"))
    assert envelope.status == "error"
    assert envelope.result["preflight_passed"] is False
    assert len(envelope.errors) == 1
    assert envelope.errors[0].code == "PREFLIGHT_FAILED"
    assert "something broke" in envelope.errors[0].message


def test_execute_handles_non_json_stdout() -> None:
    """Code-review MUST-FIX: exit=0 + unparseable stdout must NOT silently
    report preflight_passed=True. Return status=partial with a
    STDOUT_UNPARSEABLE warning so Marcus can challenge the verdict."""
    with patch.object(pr_pf, "_run_subprocess", return_value=(0, "not json", "")):
        envelope = pr_pf.execute(_invoke("execute"))
    assert envelope.status == "partial"
    assert envelope.result["readiness"] == {"raw_stdout": "not json"}
    assert envelope.result["preflight_passed"] is False
    assert len(envelope.errors) == 1
    assert envelope.errors[0].code == "PREFLIGHT_STDOUT_UNPARSEABLE"


def test_execute_handles_missing_runner() -> None:
    """If the readiness runner can't even be invoked, envelope carries the reason."""
    with patch.object(pr_pf, "_run_subprocess", side_effect=FileNotFoundError("python?")):
        envelope = pr_pf.execute(_invoke("execute"))
    assert envelope.status == "error"
    assert envelope.errors[0].code == "PREFLIGHT_EXEC_UNAVAILABLE"


def test_execute_handles_subprocess_timeout() -> None:
    """Code-review MUST-FIX: a hung readiness runner must surface as
    PREFLIGHT_TIMEOUT in the envelope — never hang Marcus's turn."""
    timeout_exc = subprocess.TimeoutExpired(cmd=["python"], timeout=120)
    with patch.object(pr_pf, "_run_subprocess", side_effect=timeout_exc):
        envelope = pr_pf.execute(_invoke("execute"))
    assert envelope.status == "error"
    assert envelope.errors[0].code == "PREFLIGHT_TIMEOUT"
    assert envelope.telemetry["timeout_sec"] == pr_pf._SUBPROCESS_TIMEOUT_SEC


def test_execute_wraps_unexpected_exceptions() -> None:
    """Code-review MUST-FIX: parity with PR-RC — non-FileNotFoundError
    exceptions (PermissionError, OSError, library bugs) must land in the
    envelope as PR_PF_UNEXPECTED_FAILURE, not leak as tracebacks."""
    with patch.object(
        pr_pf, "_run_subprocess", side_effect=PermissionError("denied")
    ):
        envelope = pr_pf.execute(_invoke("execute"))
    assert envelope.status == "error"
    assert envelope.errors[0].code == "PR_PF_UNEXPECTED_FAILURE"
    assert "PermissionError" in envelope.errors[0].message
    assert "denied" in envelope.errors[0].message


def test_build_cmd_respects_args() -> None:
    """Command construction reflects args + bundle_path."""
    cmd = pr_pf._build_cmd({"with_preflight": False, "json_only": True}, "B")
    assert "--with-preflight" not in cmd
    assert "--json-only" in cmd
    assert cmd[-2:] == ["--bundle-dir", "B"]


def test_execute_writes_default_session_receipt_when_bundle_exists(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    fake_stdout = json.dumps(
        {
            "overall_status": "pass",
            "checks": [],
            "root": str(tmp_path),
            "timestamp": "now",
        }
    )
    invocation = Invocation(
        capability_code="PR-PF",
        mode="execute",
        args={},
        context=InvocationContext(
            run_id="PF-TEST-2",
            bundle_path=str(bundle_dir),
            invoked_by="marcus",
        ),
    )

    with patch.object(pr_pf, "_run_subprocess", return_value=(0, fake_stdout, "")):
        envelope = pr_pf.execute(invocation)

    receipt_path = bundle_dir / "session-preflight-receipt.json"
    assert envelope.status == "ok"
    assert envelope.result["session_receipt_path"] == str(receipt_path)
    assert json.loads(receipt_path.read_text(encoding="utf-8"))["overall_status"] == "pass"
