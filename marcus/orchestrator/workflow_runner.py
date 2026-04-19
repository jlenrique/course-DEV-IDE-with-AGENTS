"""Lesson Planner workflow runner seam for Step 4A insertion (Story 32-1)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from marcus.facade import Facade
from marcus.lesson_plan.log import LessonPlanLog
from marcus.lesson_plan.schema import LessonPlan
from marcus.orchestrator.loop import IntakeCallable


class StepBatonHandoff(BaseModel):
    """Baton payload handed from Step 4A to Step 05."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_from: str = Field(default="04A")
    step_to: str = Field(default="05")
    lesson_plan_revision: int = Field(..., ge=0)
    lesson_plan_digest: str = Field(..., min_length=1)


class Step4AWorkflowResult(BaseModel):
    """Result emitted by the 32-1 workflow seam."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    locked_plan: LessonPlan
    handoff: StepBatonHandoff


def insert_4a_between_step_04_and_05(steps: Iterable[str]) -> tuple[str, ...]:
    """Ensure 4A appears in the pipeline between step 04 and step 05."""
    ordered = list(steps)
    if "04" not in ordered:
        raise ValueError("pipeline is missing required step '04'")
    if "05" not in ordered:
        raise ValueError("pipeline is missing required step '05'")

    idx_04 = ordered.index("04")
    idx_05 = ordered.index("05")
    if idx_04 >= idx_05:
        raise ValueError("pipeline order invalid: step '04' must precede step '05'")

    between = ordered[idx_04 + 1 : idx_05]
    if "04A" in between or "4A" in between:
        return tuple(ordered)

    ordered.insert(idx_05, "04A")
    return tuple(ordered)


def route_step_04_gate_to_step_05(
    packet_plan: LessonPlan,
    *,
    intake_callable: IntakeCallable,
    facade: Facade | None = None,
    prior_declined_rationales: tuple[tuple[str, str], ...] = (),
    log: LessonPlanLog | None = None,
    tracy_bridge: Any | None = None,
) -> Step4AWorkflowResult:
    """Run the 4A loop and return the baton contract for step 05."""
    if len(packet_plan.plan_units) == 0:
        raise ValueError("step-04 handoff requires at least one plan unit before 4A routing")

    resolved_facade = facade or Facade()
    locked_plan = resolved_facade.run_4a(
        packet_plan,
        intake_callable=intake_callable,
        prior_declined_rationales=prior_declined_rationales,
        log=log,
        tracy_bridge=tracy_bridge,
    )
    handoff = StepBatonHandoff(
        lesson_plan_revision=locked_plan.revision,
        lesson_plan_digest=locked_plan.digest,
    )
    return Step4AWorkflowResult(locked_plan=locked_plan, handoff=handoff)

