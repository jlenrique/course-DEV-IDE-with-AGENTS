"""PDF sensory bridge — page-by-page text extraction with scanned page detection.

Uses pypdf (already in requirements) for text extraction. Detects scanned/OCR
pages via text content length heuristic.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from skills.sensory_bridges.scripts.bridge_utils import build_response

logger = logging.getLogger(__name__)

SCANNED_PAGE_THRESHOLD = 50  # chars — pages with less text are likely scanned


def extract_pdf(
    artifact_path: str | Path,
    gate: str = "G0",
    **kwargs: Any,
) -> dict[str, Any]:
    """Extract text content page-by-page from a PDF file.

    Args:
        artifact_path: Path to the .pdf file.
        gate: Production gate identifier.

    Returns:
        Canonical perception response with pages[], total_pages, confidence.
    """
    path = Path(artifact_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    try:
        reader = PdfReader(str(path))
    except Exception as e:
        return build_response(
            modality="pdf",
            artifact_path=path,
            confidence="LOW",
            confidence_rationale=f"Failed to parse PDF: {e}",
            pages=[],
            total_pages=0,
        )

    pages_data: list[dict[str, Any]] = []
    scanned_count = 0

    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
            is_scanned = len(text.strip()) < SCANNED_PAGE_THRESHOLD
            if is_scanned:
                scanned_count += 1

            pages_data.append({
                "page_number": i,
                "text": text.strip(),
                "is_scanned": is_scanned,
                "char_count": len(text.strip()),
            })
        except Exception as e:
            logger.warning("Error extracting page %d: %s", i, e)
            pages_data.append({
                "page_number": i,
                "text": "",
                "is_scanned": True,
                "char_count": 0,
                "extraction_error": str(e),
            })
            scanned_count += 1

    total = len(pages_data)

    if total == 0:
        confidence = "LOW"
        rationale = "PDF contains no pages"
    elif scanned_count == total:
        confidence = "LOW"
        rationale = f"All {total} pages appear to be scanned/image-only (< {SCANNED_PAGE_THRESHOLD} chars each)"
    elif scanned_count > 0:
        confidence = "MEDIUM"
        rationale = f"{scanned_count}/{total} pages appear scanned; {total - scanned_count} pages have machine-readable text"
    else:
        confidence = "HIGH"
        rationale = f"All {total} pages have machine-readable text"

    return build_response(
        modality="pdf",
        artifact_path=path,
        confidence=confidence,
        confidence_rationale=rationale,
        pages=pages_data,
        total_pages=total,
        scanned_pages=scanned_count,
    )
