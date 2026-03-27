"""Agent-level Gamma operations wrapper.

Bridges Gary's parameter decisions and the GammaClient API layer.
Handles style guide loading, parameter merging, generation execution,
polling, export, and artifact download.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import requests
import yaml

from scripts.api_clients.gamma_client import GammaClient

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STYLE_GUIDE_PATH = PROJECT_ROOT / "state" / "config" / "style_guide.yaml"
STAGING_DIR = PROJECT_ROOT / "course-content" / "staging"


def load_style_guide_gamma() -> dict[str, Any]:
    """Load Gamma-specific defaults from the style guide."""
    if not STYLE_GUIDE_PATH.exists():
        return {}
    data = yaml.safe_load(STYLE_GUIDE_PATH.read_text(encoding="utf-8"))
    tool_params = data.get("tool_parameters", {})
    return tool_params.get("gamma", {})


def merge_parameters(
    style_defaults: dict[str, Any],
    content_template: dict[str, Any],
    envelope_overrides: dict[str, Any],
) -> dict[str, Any]:
    """Merge parameters following the priority cascade.

    Priority (later wins): style guide → content template → envelope overrides.
    """
    merged: dict[str, Any] = {}
    for source in [style_defaults, content_template, envelope_overrides]:
        for key, value in source.items():
            if value is not None and value != "":
                merged[key] = value
    return merged


def generate_slide(
    params: dict[str, Any],
    *,
    client: GammaClient | None = None,
) -> dict[str, Any]:
    """Execute a text-based Gamma generation with merged parameters.

    Args:
        params: Merged parameter dict with at least ``input_text``
            and ``text_mode``.
        client: Optional pre-configured GammaClient.

    Returns:
        Completed generation data including ``gammaUrl`` and
        ``exportUrl`` (if export was requested).
    """
    if client is None:
        client = GammaClient()

    input_text = params.pop("input_text", params.pop("inputText", ""))
    text_mode = params.pop("text_mode", params.pop("textMode", "generate"))

    gen_kwargs: dict[str, Any] = {}
    key_map = {
        "format": "format",
        "numCards": "num_cards",
        "num_cards": "num_cards",
        "cardSplit": "card_split",
        "card_split": "card_split",
        "themeId": "theme_id",
        "theme_id": "theme_id",
        "additionalInstructions": "additional_instructions",
        "additional_instructions": "additional_instructions",
        "textOptions": "text_options",
        "text_options": "text_options",
        "imageOptions": "image_options",
        "image_options": "image_options",
        "cardOptions": "card_options",
        "card_options": "card_options",
        "sharingOptions": "sharing_options",
        "sharing_options": "sharing_options",
        "exportAs": "export_as",
        "export_as": "export_as",
        "folderIds": "folder_ids",
        "folder_ids": "folder_ids",
    }
    for param_key, kwarg_key in key_map.items():
        if param_key in params and params[param_key] is not None:
            gen_kwargs[kwarg_key] = params[param_key]

    result = client.generate(input_text, text_mode, **gen_kwargs)
    gen_id = result.get("generationId") or result.get("id", "")
    logger.info("Generation started: %s", gen_id)

    completed = client.wait_for_generation(gen_id)
    return completed


def generate_from_template(
    gamma_id: str,
    prompt: str,
    params: dict[str, Any] | None = None,
    *,
    client: GammaClient | None = None,
) -> dict[str, Any]:
    """Execute a template-based Gamma generation.

    Args:
        gamma_id: The template's gammaId.
        prompt: Content/instructions for the template.
        params: Optional additional params (theme_id, export_as, etc.).
        client: Optional pre-configured GammaClient.

    Returns:
        Completed generation data.
    """
    if client is None:
        client = GammaClient()
    if params is None:
        params = {}

    gen_kwargs: dict[str, Any] = {}
    if params.get("theme_id") or params.get("themeId"):
        gen_kwargs["theme_id"] = params.get("theme_id") or params.get("themeId")
    if params.get("export_as") or params.get("exportAs"):
        gen_kwargs["export_as"] = params.get("export_as") or params.get("exportAs")
    if params.get("folder_ids") or params.get("folderIds"):
        gen_kwargs["folder_ids"] = params.get("folder_ids") or params.get("folderIds")
    if params.get("image_options") or params.get("imageOptions"):
        gen_kwargs["image_options"] = (
            params.get("image_options") or params.get("imageOptions")
        )

    result = client.generate_from_template(gamma_id, prompt, **gen_kwargs)
    gen_id = result.get("generationId") or result.get("id", "")
    logger.info("Template generation started: %s (template: %s)", gen_id, gamma_id)

    completed = client.wait_for_generation(gen_id)
    return completed


def download_export(
    export_url: str,
    output_dir: Path | str | None = None,
    filename: str | None = None,
) -> Path:
    """Download an exported artifact from a signed URL.

    Args:
        export_url: Signed download URL from completed generation.
        output_dir: Directory to save to. Defaults to staging.
        filename: Output filename. Auto-derived from URL if not provided.

    Returns:
        Path to the downloaded file.
    """
    if output_dir is None:
        output_dir = STAGING_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = export_url.split("/")[-1].split("?")[0]
        if not filename:
            filename = "gamma-export.pdf"

    output_path = output_dir / filename

    resp = requests.get(export_url, timeout=120)
    resp.raise_for_status()
    output_path.write_bytes(resp.content)
    logger.info("Downloaded %d bytes to %s", len(resp.content), output_path)

    return output_path
