"""Marcus-Orchestrator: 4A conversation loop + plan-lock commit + downstream fan-out (05+).

This sub-package is part of the Marcus duality split landed in Story 30-1.

Maya-facing note
----------------

Maya never imports from this package. She interacts with a single Marcus
facade (``marcus.facade.get_facade()``). The sub-package exists internally
to isolate the conversation-orchestration + log-write side of Marcus from
the ingestion side.

Developer discipline note
-------------------------

* 30-1 (structural foundation, this commit): module shell + identity
  constant + negotiator seam + :mod:`marcus.orchestrator.write_api`
  single-writer entry point.
* 30-3a (4A skeleton + lock): lifts the 4A conversation loop into this
  package; will promote :data:`NEGOTIATOR_SEAM` from a string sentinel to
  a structural marker (typed placeholder class with loop state) if the
  loop requires it.
* 30-4 (plan-lock fanout): adds fan-out dispatch on plan-lock commit.

Negotiator seam
---------------

30-3a's 4A conversation loop plugs into the Orchestrator via the seam
named by :data:`NEGOTIATOR_SEAM`. At 30-1 the seam is a simple string
sentinel (grep-discoverable for the 30-3a dev agent). When 30-3a lands,
the seam MAY be upgraded to a structural marker if the 4A loop needs
handoff state (pending-queue, active-loop sentinel, dialogue history).

The seam is folded into ``marcus.orchestrator`` for MVP — no separate
``marcus/negotiator/`` sub-package. Downstream epics can extract if the
3-body problem of orchestrator-intake-negotiator becomes load-bearing.

LIFT-TARGET for 30-2a / 30-3a
-----------------------------

* 30-2a brings any orchestrator-side pipeline code from
  ``scripts/utilities/prepare-irene-packet.py`` + Marcus-skill
  orchestration prompts that currently live outside this package.
* 30-3a brings the 4A conversation-loop module and scope-decision intake;
  will land as ``marcus/orchestrator/loop.py`` (or similar) and upgrade
  :data:`NEGOTIATOR_SEAM` as needed.
* 30-4 brings the plan-lock fanout dispatcher.

Single-writer contract
----------------------

Marcus-Orchestrator is the SOLE caller of
:func:`marcus.orchestrator.write_api.emit_pre_packet_snapshot`. The facade
routes Intake-side artifacts through the Orchestrator; Intake never calls
the write API directly. R1 amendment 13 (Quinn single-writer rule); see
``tests/contracts/test_marcus_single_writer_routing.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Literal

ORCHESTRATOR_MODULE_IDENTITY: Literal["marcus-orchestrator"] = "marcus-orchestrator"
"""Programming-token identity for the Orchestrator half of the Marcus duality.

String-equal to the 31-2 ``WriterIdentity`` Literal value. Imported by
:mod:`marcus.orchestrator.write_api` as the single source of truth for
the writer-check string (avoids the three-place string-drift hazard).
See :data:`marcus.lesson_plan.log.WriterIdentity`.
"""


_NEGOTIATOR_SEAM_BACKCOMPAT_TOKEN: Final[str] = "marcus-negotiator"
"""Grep-discoverable 30-1 sentinel token. :class:`NegotiatorSeam.__str__`
returns this value to preserve backward-compat with 30-1's grep-based
tests (:mod:`tests.test_marcus_negotiator_seam_named`)."""


@dataclass(frozen=True)
class NegotiatorSeam:
    """Structural marker for the 4A conversation-loop negotiator (30-3a upgrade).

    At 30-1 this seam was a string sentinel. 30-3a upgrades it to a
    typed structural marker carrying the handoff state the 4A loop
    needs: the pending-intake queue, the per-turn dialogue history,
    and the active-loop flag.

    Backward-compat with 30-1's grep-based sentinel contract is
    preserved via :meth:`__str__`, which returns the literal string
    ``"marcus-negotiator"``.

    Fields:
        pending_queue: Tuple of ``unit_id`` strings awaiting scope-
            decision intake. Empty when the loop is idle or post-lock.
        dialogue_history: Tuple of ``(turn_kind, content)`` pairs
            recording the Maya↔Marcus exchange. ``turn_kind`` is one of
            ``"maya-prompt"`` / ``"marcus-echo"`` / ``"system-note"``;
            content is the verbatim string rendered.
        active_loop: True iff the loop is currently running
            (:meth:`FourALoop.run_4a` is on the stack).
    """

    pending_queue: tuple[str, ...] = field(default_factory=tuple)
    dialogue_history: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    active_loop: bool = False

    def __str__(self) -> str:
        return _NEGOTIATOR_SEAM_BACKCOMPAT_TOKEN


NEGOTIATOR_SEAM: Final[NegotiatorSeam] = NegotiatorSeam()
"""Singleton :class:`NegotiatorSeam` instance — grep-discoverable sentinel.

``str(NEGOTIATOR_SEAM) == "marcus-negotiator"`` preserves 30-1's
grep-based sentinel contract while exposing the structural fields
the 4A loop needs.
"""

__all__: Final[tuple[str, ...]] = (
    "NEGOTIATOR_SEAM",
    "NegotiatorSeam",
    "ORCHESTRATOR_MODULE_IDENTITY",
)
