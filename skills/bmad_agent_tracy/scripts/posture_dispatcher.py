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

    def embellish(self, target_element: str, enrichment_type: str) -> dict[str, Any]:
        """
        Embellish posture: Add enrichment content.

        Input Shape: target_element (plan_unit/event), enrichment_type
        Output Shape: enrichment content dict
        Success Signal: content_added=True
        Failure Mode: content_added=False, message="no enrichment available"
        """
        raise NotImplementedError("Embellish posture not implemented")

    def corroborate(self, claim: str, source_context: str) -> dict[str, Any]:
        """
        Corroborate posture: Confirm/disconfirm claims.

        Input Shape: claim, source_context
        Output Shape: evidence assessment dict
        Success Signal: evidence_found=True, classification=supporting/contrasting/mentioning
        Failure Mode: evidence_found=False, message="insufficient evidence"
        """
        raise NotImplementedError("Corroborate posture not implemented")

    def gap_fill(self, gap_description: str, content_type: str, scope: str) -> dict[str, Any]:
        """
        Gap-Fill posture: Fill knowledge gaps.

        Input Shape: gap_description, content_type, scope
        Output Shape: filler content dict
        Success Signal: gap_filled=True
        Failure Mode: gap_filled=False, message="gap unfillable"
        """
        raise NotImplementedError("Gap-Fill posture not implemented")
