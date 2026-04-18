"""Stub-capability tests (AC-B.3, AC-T.4, AC-T.6 from story 26-6).

PR-HC and PR-RS are registered-but-unimplemented. They must:
- Return the canonical NOT_YET_IMPLEMENTED envelope (operator-observable)
- Carry the capability code and follow-up story pointer in the error entry
- Exist as xfail behavioral placeholders for when story 26-10 promotes them

Marked ``trial_critical`` — the routing spine MUST distinguish stub from
unknown capability.
"""

from __future__ import annotations

import pytest

from scripts.marcus_capabilities import pr_hc, pr_rs
from scripts.marcus_capabilities._shared import Invocation, InvocationContext

pytestmark = pytest.mark.trial_critical

STUB_MODULES = [
    ("PR-HC", pr_hc),
    ("PR-RS", pr_rs),
]


def _invoke(code: str) -> Invocation:
    return Invocation(
        capability_code=code,
        mode="execute",
        args={},
        context=InvocationContext(run_id="T-123", invoked_by="marcus"),
    )


@pytest.mark.parametrize("code, module", STUB_MODULES)
def test_stub_summarize_returns_not_yet_implemented(code, module) -> None:
    envelope = module.summarize(_invoke(code))
    assert envelope.status == "error"
    assert envelope.capability_code == code
    assert len(envelope.errors) == 1
    err = envelope.errors[0]
    assert err.code == "NOT_YET_IMPLEMENTED"
    assert "26-10" in err.message  # points at the follow-up story


@pytest.mark.parametrize("code, module", STUB_MODULES)
def test_stub_execute_returns_not_yet_implemented(code, module) -> None:
    envelope = module.execute(_invoke(code))
    assert envelope.status == "error"
    assert envelope.capability_code == code
    assert envelope.errors[0].code == "NOT_YET_IMPLEMENTED"


@pytest.mark.parametrize("code, module", STUB_MODULES)
def test_stub_echoes_run_id(code, module) -> None:
    """Even stubs must echo context.run_id — envelope contract still applies."""
    envelope = module.execute(_invoke(code))
    assert envelope.run_id == "T-123"


@pytest.mark.parametrize("code, module", STUB_MODULES)
def test_stub_has_telemetry(code, module) -> None:
    envelope = module.summarize(_invoke(code))
    assert isinstance(envelope.telemetry, dict)
    assert envelope.telemetry.get("stub") is True


# ---------------------------------------------------------------------------
# AC-T.6: xfail behavioral placeholders — fail when story 26-10 promotes stubs
# ---------------------------------------------------------------------------


@pytest.mark.xfail(reason="PR-HC full implementation deferred to story 26-10", strict=True)
def test_pr_hc_health_report_is_populated() -> None:
    """Placeholder: once PR-HC is promoted, status should be 'ok' with a health report."""
    envelope = pr_hc.execute(_invoke("PR-HC"))
    assert envelope.status == "ok"
    assert "health_report" in envelope.result


@pytest.mark.xfail(reason="PR-RS full implementation deferred to story 26-10", strict=True)
def test_pr_rs_run_inventory_is_populated() -> None:
    """Placeholder: once PR-RS is promoted, status should be 'ok' with run inventory."""
    envelope = pr_rs.execute(_invoke("PR-RS"))
    assert envelope.status == "ok"
    assert "runs" in envelope.result
