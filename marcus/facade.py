"""Single Maya-facing Marcus facade.

This module exposes the ONE surface Maya interacts with. The Marcus
duality split landed in Story 30-1 hides internal sub-package
boundaries behind this facade — Maya experiences one Marcus.

Maya-facing note
----------------

Maya sees ONE Marcus. The facade's return values and ``repr`` all render
"Marcus" — a consolidated single voice. Internal routing identifiers
never surface in Maya-visible strings; R1 amendment 17
(Marcus-as-one-voice) enforcement lives in the test file
``test_no_intake_orchestrator_leak_marcus_duality.py``.

Voice Register — binding on Facade Maya-facing surfaces
-------------------------------------------------------

Every Maya-facing string returned by a Facade method MUST honor:

1. **First person singular.** "I", never "Marcus will" or "the assistant".
2. **Present tense.** Not "I will" or "I was".
3. **No hedges.** No "I'll try to", "maybe I can", "I'm not sure but".
4. **No meta-references.** No "as your assistant", "as an AI".
5. **Ends with a question or an invitation to proceed.** Keeps the
   conversation in Maya's court (Marcus-as-SPOC posture).

The stub :meth:`Facade.greet` at 30-1 pins one example that honors all
five rules. Story 30-3a's real 4A conversation surface inherits these
rules; it does not relax them.

Maya-visibility boundary
------------------------

As of Story 30-1, the facade's return values and :meth:`Facade.__repr__`
are assumed to surface to Maya verbatim unless a later story introduces
a rendering layer. Any future layer inherits the same string discipline;
it does not relax it. A rendering layer MAY sanitize further but MUST
NOT reintroduce hyphenated sub-identity tokens.

Developer discipline note
-------------------------

* 30-1 (structural foundation, this commit): facade shell with lazy
  accessor, two identity constants, stub :meth:`Facade.greet`, and the
  Voice Register above.
* 30-3a (4A skeleton + lock): replaces :meth:`Facade.greet` with a real
  4A conversation surface honoring the Voice Register.
* 30-4+ stories: extend facade dispatch to route Intake artifacts
  through :mod:`marcus.orchestrator.write_api` for log emission.

Lazy-accessor construction (W-1 rider)
--------------------------------------

Do NOT instantiate a module-level ``facade = Facade()`` singleton.
Module-load singletons couple session state to import order and will
bite 30-3a when per-session conversation context lands. Use the lazy
accessor :func:`get_facade` instead; pytest fixtures can call
:func:`reset_facade` to isolate per-test state.
"""

from __future__ import annotations

from typing import Final, Literal

MARCUS_IDENTITY: Literal["marcus"] = "marcus"
"""Programming-token identity. Stable key for routing + logging.

Deliberately lowercase — a grep-time structural tripwire. If a developer
ever interpolates ``MARCUS_IDENTITY`` into a Maya-facing string, the
resulting "marcus" reads wrong in a screenshot and QA catches it
instantly. Maya-facing surfaces render from :data:`MARCUS_DISPLAY_NAME`
instead.
"""

MARCUS_DISPLAY_NAME: Final[str] = "Marcus"
"""Maya-facing render constant. All user-visible strings MUST use this."""


class Facade:
    """Maya's single Marcus-facing surface.

    At Story 30-1 the callable surface is deliberately minimal
    (:attr:`marcus_identity`, :meth:`__repr__`, :meth:`greet` stub).
    Story 30-3a's 4A conversation loop replaces :meth:`greet` with the
    real conversation surface.

    Instances are constructed via :func:`get_facade`; direct
    instantiation is supported but not the idiomatic path.
    """

    marcus_identity: Literal["marcus"] = MARCUS_IDENTITY

    def __repr__(self) -> str:
        return MARCUS_DISPLAY_NAME

    def greet(self) -> str:
        """Return Marcus's Voice-Register-compliant greeting.

        TODO(30-3a): replace with real 4A loop conversation surface
        honoring the Voice Register pinned in the module docstring.
        """
        return f"Hi — I'm {MARCUS_DISPLAY_NAME}. What are we planning today?"


_facade: Facade | None = None


def get_facade() -> Facade:
    """Return the lazily-constructed :class:`Facade` singleton.

    Lazy accessor (W-1 rider): avoids module-load instantiation so
    per-session state can land at 30-3a without import-order coupling.
    """
    global _facade
    if _facade is None:
        _facade = Facade()
    return _facade


def reset_facade() -> None:
    """Reset the cached :class:`Facade` singleton.

    Pytest-fixture hook: tests that mutate facade state call this in
    teardown to isolate per-test state. Production code MUST NOT call
    this function.
    """
    global _facade
    _facade = None


__all__: Final[tuple[str, ...]] = (
    "MARCUS_IDENTITY",
    "MARCUS_DISPLAY_NAME",
    "Facade",
    "get_facade",
)
# Note: `reset_facade` is a pytest-fixture hook, intentionally NOT exposed via
# `__all__`. Tests import it by name (`from marcus.facade import reset_facade`).
# Keeping it out of `__all__` prevents `from marcus.facade import *` from
# leaking the test-only helper into production namespaces.
