"""Marcus package namespace.

This package hosts Marcus-side modules.

* Story 31-1 introduced the first sub-package :mod:`marcus.lesson_plan`
  — the foundation schema for the Lesson Planner MVP.
* Story 30-1 introduced the Marcus duality split: :mod:`marcus.intake`
  (steps 01-04 + pre-packet construction) and :mod:`marcus.orchestrator`
  (4A loop + log write-API + 05+ fan-out), both hidden behind a single
  Maya-facing facade at :mod:`marcus.facade`.

Maya-facing public surface
--------------------------

The ONE top-level export is :func:`get_facade` (re-exported from
:mod:`marcus.facade`). Sub-packages :mod:`marcus.intake` and
:mod:`marcus.orchestrator` are NOT re-exported at the top level — they
are internal development surfaces, not Maya's consumption path.

R1 amendment 17 (Marcus-as-one-voice): Maya sees one Marcus. No
hyphenated sub-identity tokens appear in any Maya-facing string.
"""

from __future__ import annotations

from marcus.facade import get_facade

__all__ = ("get_facade",)
