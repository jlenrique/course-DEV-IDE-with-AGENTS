"""Image sensory bridge — LLM vision analysis for slide images.

For agents running in Cursor, image analysis uses the native LLM vision
capability (Claude can read images via the Read tool). This bridge provides
the canonical schema wrapper and structured output formatting.

For automated/script use, this module provides a function that accepts
a pre-computed vision analysis description and formats it into the
perception schema. Direct API vision calls require an API key for a
vision-capable model.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from skills.sensory_bridges.scripts.bridge_utils import build_response

logger = logging.getLogger(__name__)


def analyze_image(
    artifact_path: str | Path,
    gate: str = "G3",
    extracted_text: str = "",
    layout_description: str = "",
    visual_elements: list[dict[str, str]] | None = None,
    slide_title: str = "",
    text_blocks: list[str] | None = None,
    confidence: str = "HIGH",
    confidence_rationale: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    """Format an image perception result into the canonical schema.

    In the typical agent workflow, the agent reads the image via LLM vision,
    then calls this function to wrap its interpretation in the standard
    perception schema. The ``extracted_text``, ``layout_description``, and
    ``visual_elements`` parameters come from the agent's own vision analysis.

    Args:
        artifact_path: Path to the image file.
        gate: Production gate identifier.
        extracted_text: All text visible in the image (from LLM vision OCR).
        layout_description: Description of visual layout (columns, sections, etc.).
        visual_elements: List of identified visual elements.
        slide_title: Title text extracted from the slide.
        text_blocks: Individual text blocks identified on the slide.
        confidence: Agent's confidence in its interpretation.
        confidence_rationale: Why the agent assigned this confidence level.

    Returns:
        Canonical perception response for image modality.
    """
    path = Path(artifact_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    if not confidence_rationale:
        if extracted_text:
            confidence_rationale = f"Image analyzed: {len(extracted_text)} chars extracted, {len(visual_elements or [])} visual elements"
        else:
            confidence = "LOW"
            confidence_rationale = "No text extracted from image — may be blank or unparseable"

    return build_response(
        modality="image",
        artifact_path=path,
        confidence=confidence,
        confidence_rationale=confidence_rationale,
        extracted_text=extracted_text,
        layout_description=layout_description,
        visual_elements=visual_elements or [],
        slide_title=slide_title,
        text_blocks=text_blocks or [],
    )
