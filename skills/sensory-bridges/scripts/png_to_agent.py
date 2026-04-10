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


def _classify_visual_complexity(
    *,
    extracted_text: str,
    layout_description: str,
    visual_elements: list[dict[str, str]],
    text_blocks: list[str],
) -> tuple[str, str]:
    """Estimate how much visual burden the slide places on the narrator.

    The result is heuristic on purpose: it gives Irene a grounded nudge about
    whether the slide is visually simple, balanced, or dense enough to justify
    slower orientation and richer explanation.
    """
    normalized_blocks = [block.strip() for block in text_blocks if str(block).strip()]
    word_count = len(extracted_text.split())
    visual_count = len(visual_elements)
    layout_text = layout_description.lower()
    element_descriptions = " ".join(
        str(element.get("type", "")) + " " + str(element.get("description", ""))
        for element in visual_elements
        if isinstance(element, dict)
    ).lower()

    score = 0
    if len(normalized_blocks) >= 4:
        score += 1
    if len(normalized_blocks) >= 7:
        score += 1
    if word_count >= 35:
        score += 1
    if word_count >= 75:
        score += 1
    if visual_count >= 2:
        score += 1
    if visual_count >= 4:
        score += 1

    complexity_cues = (
        "two-column",
        "split",
        "comparison",
        "matrix",
        "roadmap",
        "timeline",
        "diagram",
        "chart",
        "table",
        "process",
        "sequence",
        "stacked",
    )
    simplicity_cues = ("minimal", "single definition", "single paragraph", "single column")

    if any(cue in layout_text or cue in element_descriptions for cue in complexity_cues):
        score += 1
    if any(cue in layout_text for cue in simplicity_cues):
        score -= 1

    if score <= 1:
        level = "low"
    elif score <= 4:
        level = "moderate"
    else:
        level = "high"

    if visual_count > len(normalized_blocks):
        burden = "visual-heavy"
    elif word_count >= 50 and visual_count <= 1:
        burden = "text-led"
    else:
        burden = "balanced"

    summary = (
        f"{level.title()} visual complexity: {len(normalized_blocks)} text block(s), "
        f"{visual_count} visual element(s), and a {burden} layout. "
    )
    if level == "low":
        summary += "This slide should need only brief orientation before advancing the point."
    elif level == "moderate":
        summary += "This slide likely benefits from moderate orientation and selective detail."
    else:
        summary += "This slide likely warrants slower orientation and more deliberate narration support."

    return level, summary


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
            confidence_rationale = "No text extracted from image - may be blank or unparseable"

    complexity_level, complexity_summary = _classify_visual_complexity(
        extracted_text=extracted_text,
        layout_description=layout_description,
        visual_elements=visual_elements or [],
        text_blocks=text_blocks or [],
    )

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
        visual_complexity_level=complexity_level,
        visual_complexity_summary=complexity_summary,
    )
