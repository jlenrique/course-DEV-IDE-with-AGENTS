"""
Tracy Posture Dispatcher

Dispatches to retrieval.dispatcher for three postures: embellish, corroborate,
gap-fill. Each posture implements the four-part contract: input shape, output
shape, success signal, failure mode.
"""

from typing import Any


class PostureDispatcher:
    """Dispatcher for Tracy's three research postures."""

    def __init__(self, dispatcher: Any) -> None:
        """Accept a retrieval dispatcher (wired in Story 28-2)."""
        self.dispatcher = dispatcher

    def _dispatch_intent(self, intent: dict[str, Any]) -> dict[str, Any]:
        if hasattr(self.dispatcher, "dispatch"):
            result = self.dispatcher.dispatch(intent)
        elif callable(self.dispatcher):
            result = self.dispatcher(intent)
        else:
            raise TypeError("dispatcher must expose dispatch(intent) or be callable")

        if not isinstance(result, dict):
            raise TypeError("dispatcher returned non-dict result")
        return result

    def select_posture(self, brief: dict[str, Any]) -> dict[str, Any]:
        """Route an Irene bridge brief to a Tracy posture implementation."""
        dial = brief.get("dial")
        if dial == "enrich":
            return self.embellish(
                target_element=str(brief.get("target_element", "")),
                enrichment_type=str(brief.get("enrichment_type", "general")),
            )
        if dial == "corroborate":
            return self.corroborate(
                claim=str(brief.get("claim", "")),
                source_context=str(brief.get("source_context", "")),
                evidence_bolster=bool(brief.get("evidence_bolster", False)),
            )
        if dial in {"gap_fill", "gap-fill"}:
            return self.gap_fill(
                gap_description=str(brief.get("gap_description", "")),
                content_type=str(brief.get("content_type", "explanation")),
                scope=str(brief.get("scope", "unit")),
            )

        gap_type = brief.get("gap_type")
        if gap_type == "enrichment":
            return self.embellish(
                target_element=str(brief.get("target_element", "")),
                enrichment_type=str(brief.get("enrichment_type", "general")),
            )
        if gap_type == "evidence":
            return self.corroborate(
                claim=str(brief.get("claim", "")),
                source_context=str(brief.get("source_context", "")),
                evidence_bolster=bool(brief.get("evidence_bolster", False)),
            )
        if gap_type == "missing_concept":
            return self.gap_fill(
                gap_description=str(brief.get("gap_description", "")),
                content_type=str(brief.get("content_type", "explanation")),
                scope=str(brief.get("scope", "unit")),
            )

        return {
            "status": "failed",
            "reason": "unsupported Tracy posture brief",
            "brief": brief,
        }

    def embellish(self, target_element: str, enrichment_type: str) -> dict[str, Any]:
        """
        Embellish posture: Add enrichment content.

        Input Shape: target_element (plan_unit/event), enrichment_type
        Output Shape: enrichment content dict
        Success Signal: content_added=True
        Failure Mode: content_added=False, message="no enrichment available"
        """
        raise NotImplementedError("Embellish posture not implemented")

    def corroborate(
        self,
        claim: str,
        source_context: str,
        *,
        evidence_bolster: bool = False,
    ) -> dict[str, Any]:
        """
        Corroborate posture: Confirm/disconfirm claims.

        Input Shape: claim, source_context
        Output Shape: evidence assessment dict
        Success Signal: evidence_found=True, classification=supporting/contrasting/mentioning
        Failure Mode: evidence_found=False, message="insufficient evidence"
        """
        provider_hints = ["scite", "consensus"] if evidence_bolster else ["scite"]
        retrieval_intent = {
            "query": claim,
            "source_context": source_context,
            "cross_validate": evidence_bolster,
            "provider_hints": provider_hints,
            "max_results": 5,
        }

        try:
            output = self._dispatch_intent(retrieval_intent)
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "failed",
                "posture": "corroborate",
                "reason": str(exc),
                "input": {
                    "claim": claim,
                    "source_context": source_context,
                    "evidence_bolster": evidence_bolster,
                },
            }

        sources_raw = output.get("sources")
        sources = sources_raw if isinstance(sources_raw, list) else []
        classification = output.get("classification")
        if classification not in {"supporting", "contrasting", "mentioning"}:
            classification = "mentioning"
        confidence_raw = output.get("confidence_score", 0.0)
        confidence = float(confidence_raw) if isinstance(confidence_raw, (int, float)) else 0.0
        confidence = max(0.0, min(1.0, confidence))

        return {
            "status": "success",
            "posture": "corroborate",
            "input": {
                "claim": claim,
                "source_context": source_context,
                "evidence_bolster": evidence_bolster,
            },
            "output": {
                "evidence_found": len(sources) > 0,
                "classification": classification,
                "confidence_score": confidence,
                "sources": sources,
            },
        }

    def gap_fill(self, gap_description: str, content_type: str, scope: str) -> dict[str, Any]:
        """
        Gap-Fill posture: Fill knowledge gaps.

        Input Shape: gap_description, content_type, scope
        Output Shape: filler content dict
        Success Signal: gap_filled=True
        Failure Mode: gap_filled=False, message="gap unfillable"
        """
        raise NotImplementedError("Gap-Fill posture not implemented")
