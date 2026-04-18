"""AC-T.3 — ScopeDecision state-machine + two-level actor matrix + Q-5 bypass guard.

Parametrized over legal + illegal transitions (Winston / R2 rider S-4).
Plus the dedicated Q-5 test asserting ``state == "locked"`` AND ``ratified_by
!= "maya"`` is rejected at every entry point (R2 rider Q-5 / AC-C.8).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from marcus.lesson_plan.schema import ScopeDecision


def _proposed(internal: str = "marcus") -> ScopeDecision:
    return ScopeDecision(
        state="proposed",
        scope="in-scope",
        proposed_by="system",
        _internal_proposed_by=internal,
    )


def _ratified(internal: str = "marcus") -> ScopeDecision:
    return ScopeDecision(
        state="ratified",
        scope="in-scope",
        proposed_by="operator",
        _internal_proposed_by=internal,
        ratified_by="maya",
    )


# ---------------------------------------------------------------------------
# Legal transitions
# ---------------------------------------------------------------------------


def test_proposed_to_proposed_repropose_different_scope() -> None:
    sd = _proposed()
    sd2 = ScopeDecision.transition_to(sd, state="proposed", scope="delegated")
    assert sd2.state == "proposed"
    assert sd2.scope == "delegated"


def test_proposed_to_ratified_with_maya() -> None:
    sd = _proposed()
    sd2 = ScopeDecision.transition_to(sd, state="ratified", ratified_by="maya")
    assert sd2.state == "ratified"
    assert sd2.ratified_by == "maya"


def test_ratified_to_locked_via_plan_lock() -> None:
    sd = _ratified()
    locked = ScopeDecision.transition_to(sd, state="locked")
    assert locked.state == "locked"
    assert locked.ratified_by == "maya"
    assert locked.locked_at is not None


def test_internal_actor_preserved_through_legal_transitions() -> None:
    sd = _proposed(internal="marcus-intake")
    sd2 = ScopeDecision.transition_to(sd, state="ratified", ratified_by="maya")
    assert sd2.internal_proposed_by == "marcus-intake"


# ---------------------------------------------------------------------------
# Illegal transitions (each asserts explicit error message)
# ---------------------------------------------------------------------------


def test_proposed_to_ratified_without_maya_rejected() -> None:
    sd = _proposed()
    with pytest.raises(ValueError) as exc:
        ScopeDecision.transition_to(sd, state="ratified", ratified_by=None)
    assert "ratified_by='maya'" in str(exc.value)


def test_ratified_to_proposed_rejected_no_revert() -> None:
    sd = _ratified()
    with pytest.raises(ValueError) as exc:
        ScopeDecision.transition_to(sd, state="proposed")
    assert "ratified -> proposed" in str(exc.value)


@pytest.mark.parametrize("target_state", ["proposed", "ratified", "locked"])
def test_locked_to_anything_rejected_terminal(target_state: str) -> None:
    """Fresh ``locked`` instance per case (SF-7): avoids state carry-over."""
    locked = ScopeDecision.transition_to(_ratified(), state="locked")
    with pytest.raises(ValueError) as exc:
        ScopeDecision.transition_to(locked, state=target_state)  # type: ignore[arg-type]
    assert "locked" in str(exc.value)


def test_proposed_to_locked_direct_rejected() -> None:
    sd = _proposed()
    with pytest.raises(ValueError) as exc:
        ScopeDecision.transition_to(sd, state="locked", ratified_by="maya")
    assert "proposed -> locked" in str(exc.value)


# ---------------------------------------------------------------------------
# Q-5 bypass guard (R2 rider Q-5 / AC-C.8)
# ---------------------------------------------------------------------------


def test_scope_decision_locked_with_maya_is_valid() -> None:
    sd = ScopeDecision(
        state="locked",
        scope="in-scope",
        proposed_by="operator",
        _internal_proposed_by="maya",
        ratified_by="maya",
        locked_at=datetime.now(tz=UTC),
    )
    assert sd.state == "locked"
    assert sd.ratified_by == "maya"


def test_scope_decision_locked_without_maya_rejected() -> None:
    """Q-5 guard: ``state="locked"`` + ``ratified_by=None`` direct construction."""
    with pytest.raises(ValidationError) as exc:
        ScopeDecision(
            state="locked",
            scope="in-scope",
            proposed_by="operator",
            _internal_proposed_by="maya",
            ratified_by=None,
        )
    assert "ratified_by='maya'" in str(exc.value)


def test_scope_decision_locked_with_non_maya_string_rejected_at_type_layer() -> None:
    """Type layer rejects any non-``"maya"`` / non-``None`` string via Literal."""
    with pytest.raises(ValidationError) as exc:
        ScopeDecision(
            state="locked",
            scope="in-scope",
            proposed_by="operator",
            _internal_proposed_by="maya",
            ratified_by="marcus",  # type: ignore[arg-type]
        )
    # The Literal["maya"] | None constraint surfaces as a validation error.
    message = str(exc.value)
    assert "ratified_by" in message or "maya" in message


def test_scope_decision_direct_mutation_locked_without_maya_rejected() -> None:
    """``validate_assignment=True`` re-runs the Q-5 guard on field mutation."""
    sd = _ratified()  # state=ratified, ratified_by=maya
    # Now try to bypass via direct mutation of ratified_by while already locked.
    locked = ScopeDecision.transition_to(sd, state="locked")
    with pytest.raises(ValidationError) as exc:
        locked.ratified_by = None
    assert "ratified_by='maya'" in str(exc.value)


def test_scope_decision_direct_state_mutation_locked_without_maya_rejected() -> None:
    """Direct ``state="locked"`` mutation without Maya is rejected on re-validate."""
    sd = _proposed()  # ratified_by is None here
    with pytest.raises(ValidationError) as exc:
        sd.state = "locked"
    assert "ratified_by='maya'" in str(exc.value)
