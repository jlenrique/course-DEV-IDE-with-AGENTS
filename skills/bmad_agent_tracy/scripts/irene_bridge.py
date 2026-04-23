import logging
from typing import Any

logger = logging.getLogger(__name__)


class IreneTracyBridge:
    """Bridge connecting Irene's lesson plan output to Tracy's research postures."""

    def __init__(self, posture_dispatcher: Any) -> None:
        self.dispatcher = posture_dispatcher

    def process_plan_locked(self, lesson_plan: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Scan lesson plan units for IdentifiedGap on in-scope units
        and automatically dispatch to Tracy.
        """
        results = []
        evidence_bolster = bool(lesson_plan.get("evidence_bolster", False))
        units = lesson_plan.get("units") or []
        for unit in units:
            if not isinstance(unit, dict):
                continue
            scope_decision = unit.get("scope_decision")
            if scope_decision != "in-scope":
                continue

            gaps = unit.get("identified_gaps") or []
            for gap in gaps:
                if not isinstance(gap, dict):
                    continue
                brief = {
                    "gap_type": gap.get("type"),
                    "evidence_bolster": evidence_bolster,
                    "scope_decision": scope_decision,
                    "target_element": unit.get("id", ""),
                    "gap_description": gap.get("description", ""),
                    "claim": gap.get("claim", ""),
                    "source_context": gap.get("source_context", ""),
                    "enrichment_type": gap.get("enrichment_type", "general"),
                    "content_type": gap.get("content_type", "explanation"),
                    "scope": gap.get("scope", "unit"),
                }
                # Remove None or empty string keys without dropping legitimate falsy values
                brief = {k: v for k, v in brief.items() if v is not None and v != ""}
                # Ensure scope_decision is always present
                brief["scope_decision"] = scope_decision

                try:
                    res = self.dispatcher.select_posture(brief)
                    results.append(res)
                except Exception as e:
                    logger.exception("Failed to dispatch Tracy posture for gap")
                    results.append({"status": "failed", "reason": str(e), "gap": gap})

        return results

    def process_dials(self, plan_unit: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Dispatch to Tracy based on dial operator endorsements.
        """
        results = []
        dials = plan_unit.get("dials") or {}
        if not isinstance(dials, dict):
            return results

        for dial_name, endorsement in dials.items():
            # Support both boolean flags and dictionary objects for endorsements
            is_endorsed = False
            if isinstance(endorsement, bool):
                is_endorsed = endorsement
            elif isinstance(endorsement, dict):
                is_endorsed = bool(endorsement.get("endorsed"))

            if is_endorsed:
                brief = {
                    "dial": dial_name,
                    "evidence_bolster": bool(plan_unit.get("evidence_bolster", False)),
                    "target_element": plan_unit.get("id", ""),
                    "scope_decision": plan_unit.get("scope_decision", "in-scope"),
                }
                try:
                    res = self.dispatcher.select_posture(brief)
                    results.append(res)
                except Exception as e:
                    logger.exception("Failed to dispatch Tracy posture for dial %s", dial_name)
                    results.append({"status": "failed", "reason": str(e), "dial": dial_name})

        return results
