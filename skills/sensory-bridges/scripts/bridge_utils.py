"""Shared utilities for sensory bridge scripts.

Provides the canonical perception schema, validation, confidence scoring,
and the top-level ``perceive()`` dispatcher.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "1.0"

VALID_MODALITIES = frozenset({"image", "audio", "pdf", "pptx", "video"})

VALID_CONFIDENCE = frozenset({"HIGH", "MEDIUM", "LOW"})

MODALITY_EXTENSIONS: dict[str, set[str]] = {
    "image": {".png", ".jpg", ".jpeg", ".gif", ".webp"},
    "audio": {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"},
    "pdf": {".pdf"},
    "pptx": {".pptx"},
    "video": {".mp4", ".webm", ".mkv", ".mov", ".avi"},
}


def build_request(
    artifact_path: str | Path,
    modality: str,
    gate: str,
    requesting_agent: str,
    purpose: str = "",
) -> dict[str, Any]:
    """Build a canonical perception request dict."""
    if modality not in VALID_MODALITIES:
        raise ValueError(f"Invalid modality '{modality}'. Must be one of {VALID_MODALITIES}")

    path = Path(artifact_path)
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")

    ext = path.suffix.lower()
    expected = MODALITY_EXTENSIONS.get(modality, set())
    if expected and ext not in expected:
        logger.warning("Extension '%s' is unusual for modality '%s'", ext, modality)

    return {
        "artifact_path": str(path),
        "modality": modality,
        "gate": gate,
        "requesting_agent": requesting_agent,
        "purpose": purpose,
    }


def build_response(
    modality: str,
    artifact_path: str | Path,
    confidence: str,
    confidence_rationale: str,
    **modality_fields: Any,
) -> dict[str, Any]:
    """Build a canonical perception response dict."""
    if confidence not in VALID_CONFIDENCE:
        raise ValueError(f"Invalid confidence '{confidence}'. Must be one of {VALID_CONFIDENCE}")

    return {
        "schema_version": SCHEMA_VERSION,
        "modality": modality,
        "artifact_path": str(artifact_path),
        "confidence": confidence,
        "confidence_rationale": confidence_rationale,
        "perception_timestamp": datetime.now(timezone.utc).isoformat(),
        **modality_fields,
    }


def validate_response(response: dict[str, Any]) -> list[str]:
    """Validate that a response dict conforms to the canonical schema.

    Returns a list of error strings (empty means valid).
    """
    errors: list[str] = []
    required = {"schema_version", "modality", "artifact_path", "confidence",
                "confidence_rationale", "perception_timestamp"}
    for field in required:
        if field not in response:
            errors.append(f"Missing required field: {field}")

    if response.get("confidence") not in VALID_CONFIDENCE:
        errors.append(f"Invalid confidence: {response.get('confidence')}")

    if response.get("modality") not in VALID_MODALITIES:
        errors.append(f"Invalid modality: {response.get('modality')}")

    modality = response.get("modality")
    modality_required: dict[str, set[str]] = {
        "image": {"extracted_text", "layout_description"},
        "audio": {"transcript_text", "total_duration_ms", "wpm"},
        "pdf": {"pages", "total_pages"},
        "pptx": {"slides", "total_slides"},
        "video": {"keyframes", "audio_transcript", "total_duration_ms"},
    }

    if modality and modality in modality_required:
        for field in modality_required[modality]:
            if field not in response:
                errors.append(f"Missing {modality}-specific field: {field}")

    return errors


def serialize_response(response: dict[str, Any], output_path: str | Path | None = None) -> str:
    """Serialize response to JSON string, optionally writing to a file."""
    json_str = json.dumps(response, indent=2, ensure_ascii=False, default=str)
    if output_path:
        Path(output_path).write_text(json_str, encoding="utf-8")
    return json_str


def perceive(
    artifact_path: str | Path,
    modality: str,
    gate: str,
    requesting_agent: str,
    purpose: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    """Top-level dispatcher: invoke the appropriate bridge for the modality."""
    request = build_request(artifact_path, modality, gate, requesting_agent, purpose)

    if modality == "pptx":
        from skills.sensory_bridges.scripts.pptx_to_agent import extract_pptx
        return extract_pptx(request["artifact_path"], gate=gate, **kwargs)

    if modality == "pdf":
        from skills.sensory_bridges.scripts.pdf_to_agent import extract_pdf
        return extract_pdf(request["artifact_path"], gate=gate, **kwargs)

    if modality == "audio":
        from skills.sensory_bridges.scripts.audio_to_agent import transcribe_audio
        return transcribe_audio(request["artifact_path"], gate=gate, **kwargs)

    if modality == "image":
        from skills.sensory_bridges.scripts.png_to_agent import analyze_image
        return analyze_image(request["artifact_path"], gate=gate, **kwargs)

    if modality == "video":
        from skills.sensory_bridges.scripts.video_to_agent import extract_video
        return extract_video(request["artifact_path"], gate=gate, **kwargs)

    raise ValueError(f"No bridge implemented for modality '{modality}'")
