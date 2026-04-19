"""Lesson Plan schema + log + registries/ABC foundation.

Stories 31-1 (schema) + 31-2 (log write-path) + 31-3 (registries + ModalityProducer ABC).

Public surface:
    - :class:`LessonPlan`, :class:`PlanUnit`, :class:`Dials`,
      :class:`IdentifiedGap`, :class:`LearningModel`, :class:`PlanRef`.
    - :class:`ScopeDecision` with :meth:`ScopeDecision.transition_to`
      state-machine classmethod.
    - :class:`FitReport`, :class:`FitDiagnosis`.
    - :class:`EventEnvelope` + :class:`ScopeDecisionTransition` event
      primitives (log write-path lives in 31-2).
    - :func:`compute_digest`, :func:`assert_digest_matches`.
    - :mod:`event_type_registry` with the Gagne-9 labels + reserved log
      event_types.
    - **31-3 surface:** :data:`MODALITY_REGISTRY` + :class:`ModalityEntry` +
      :data:`ModalityRef` + :data:`COMPONENT_TYPE_REGISTRY` +
      :class:`ComponentTypeEntry` + :class:`ModalityProducer` ABC +
      :class:`ProductionContext` + :class:`ProducedAsset` + registry query API.

Every shape here is the reviewable contract downstream stories (31-2
log, 31-3 registries, 29-1 fit-report validator, 30-1 Marcus duality
split, 30-2b pre-packet emission, 30-3a/b 4A loop, 30-4 plan-lock
fanout, 31-5 Quinn-R gate, 32-2 envelope audit, 32-3 trial-run smoke)
read and write against.

See ``_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md``,
``_bmad-output/implementation-artifacts/31-2-lesson-plan-log.md``, and
``_bmad-output/implementation-artifacts/31-3-registries.md`` for the
authoritative specs.
"""

from __future__ import annotations

from marcus.lesson_plan.component_type_registry import (
    COMPONENT_TYPE_REGISTRY,
    ComponentTypeEntry,
    get_component_type_entry,
)
from marcus.lesson_plan.digest import assert_digest_matches, compute_digest
from marcus.lesson_plan.events import (
    EventEnvelope,
    ScopeDecisionTransition,
    to_internal_actor,
)
from marcus.lesson_plan.log import (
    LOG_PATH,
    NAMED_MANDATORY_EVENTS,
    WRITER_EVENT_MATRIX,
    LessonPlanLog,
    LogCorruptError,
    PlanLockedPayload,
    PrePacketSnapshotPayload,
    SourceRef,
    StalePlanRefError,
    UnauthorizedWriterError,
    WriterIdentity,
    assert_plan_fresh,
)
from marcus.lesson_plan.modality_producer import ModalityProducer
from marcus.lesson_plan.modality_registry import (
    MODALITY_REGISTRY,
    ModalityEntry,
    ModalityRef,
    get_modality_entry,
    list_pending_modalities,
    list_ready_modalities,
)
from marcus.lesson_plan.produced_asset import ProducedAsset, ProductionContext
from marcus.lesson_plan.schema import (
    SCHEMA_VERSION,
    Dials,
    FitDiagnosis,
    FitReport,
    IdentifiedGap,
    LearningModel,
    LessonPlan,
    PlanRef,
    PlanUnit,
    ScopeDecision,
    StaleRevisionError,
)

__all__ = [
    "COMPONENT_TYPE_REGISTRY",
    "Dials",
    "ComponentTypeEntry",
    "EventEnvelope",
    "FitDiagnosis",
    "FitReport",
    "IdentifiedGap",
    "LOG_PATH",
    "LearningModel",
    "LessonPlan",
    "LessonPlanLog",
    "LogCorruptError",
    "MODALITY_REGISTRY",
    "ModalityEntry",
    "ModalityProducer",
    "ModalityRef",
    "NAMED_MANDATORY_EVENTS",
    "PlanLockedPayload",
    "PlanRef",
    "PlanUnit",
    "PrePacketSnapshotPayload",
    "ProducedAsset",
    "ProductionContext",
    "SCHEMA_VERSION",
    "ScopeDecision",
    "ScopeDecisionTransition",
    "SourceRef",
    "StalePlanRefError",
    "StaleRevisionError",
    "UnauthorizedWriterError",
    "WRITER_EVENT_MATRIX",
    "WriterIdentity",
    "assert_digest_matches",
    "assert_plan_fresh",
    "compute_digest",
    "get_component_type_entry",
    "get_modality_entry",
    "list_pending_modalities",
    "list_ready_modalities",
    "to_internal_actor",
]
