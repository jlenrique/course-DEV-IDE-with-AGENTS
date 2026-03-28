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
STYLE_PRESETS_PATH = PROJECT_ROOT / "state" / "config" / "gamma-style-presets.yaml"
STAGING_DIR = PROJECT_ROOT / "course-content" / "staging"


def load_style_guide_gamma() -> dict[str, Any]:
    """Load Gamma-specific defaults from the style guide."""
    if not STYLE_GUIDE_PATH.exists():
        return {}
    data = yaml.safe_load(STYLE_GUIDE_PATH.read_text(encoding="utf-8"))
    tool_params = data.get("tool_parameters", {})
    return tool_params.get("gamma", {})


# ---------------------------------------------------------------------------
# Style Preset Library
# ---------------------------------------------------------------------------

def _load_presets_file(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the raw presets list from YAML."""
    p = path or STYLE_PRESETS_PATH
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return []
    return data.get("presets", [])


def list_style_presets(
    *,
    scope: str | None = None,
    path: Path | None = None,
) -> list[dict[str, Any]]:
    """Return all style presets, optionally filtered by scope.

    Args:
        scope: If provided, return only presets whose scope matches.
            Matching rules: exact match, or preset scope ``"*"`` matches
            everything, or the requested scope starts with the preset
            scope (e.g., request ``"C1 > M1"`` matches preset ``"C1"``).
        path: Override preset file path (for testing).

    Returns:
        List of preset dicts (complete, including parameters and provenance).
    """
    presets = _load_presets_file(path)
    if scope is None:
        return presets
    matched: list[dict[str, Any]] = []
    for preset in presets:
        ps = preset.get("scope", "*")
        if ps == "*" or ps == scope or scope.startswith(ps):
            matched.append(preset)
    return matched


def load_style_preset(
    name: str,
    *,
    path: Path | None = None,
) -> dict[str, Any] | None:
    """Load a single style preset by name and return its parameters dict.

    Args:
        name: The preset name (e.g., ``"hil-2026-apc-nejal"``).
        path: Override preset file path (for testing).

    Returns:
        The ``parameters`` dict from the matching preset (ready for
        merge), or ``None`` if no preset with that name exists.
    """
    for preset in _load_presets_file(path):
        if preset.get("name") == name:
            return preset.get("parameters", {})
    return None


def resolve_style_preset(
    name: str | None = None,
    *,
    theme_id: str | None = None,
    scope: str | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    """Resolve the best-matching style preset parameters.

    Resolution order:
    1. If ``name`` is provided, look up by exact name.
    2. If ``theme_id`` is provided, find a preset that matches that theme.
    3. If ``scope`` is provided, find the most specific scope match.
    4. Return empty dict if no match.

    The returned dict contains flattened Gamma API parameters suitable for
    injection into the merge cascade at level 3.

    Returns:
        Parameter dict (may be empty).
    """
    presets = _load_presets_file(path)
    if not presets:
        return {}

    # 1. Exact name match
    if name:
        for p in presets:
            if p.get("name") == name:
                return _flatten_preset_params(p)

    # 2. Theme ID match
    if theme_id:
        for p in presets:
            if p.get("theme_id") == theme_id:
                return _flatten_preset_params(p)

    # 3. Scope match (most specific wins)
    if scope:
        candidates = list_style_presets(scope=scope, path=path)
        if candidates:
            # Sort by scope specificity: longer scope string = more specific
            candidates.sort(key=lambda c: len(c.get("scope", "")), reverse=True)
            # Skip wildcard-only matches unless it's the only option
            specific = [c for c in candidates if c.get("scope", "*") != "*"]
            best = specific[0] if specific else candidates[0]
            return _flatten_preset_params(best)

    return {}


def _flatten_preset_params(preset: dict[str, Any]) -> dict[str, Any]:
    """Extract and flatten parameters from a preset for merge.

    Handles two image style modes:

    **Approach A — Named stylePreset (tile selection):**
        ``imageOptions.stylePreset`` is a named value (e.g., ``illustration``,
        ``lineArt``, ``photorealistic``, ``abstract``, ``3D``).
        ``imageOptions.keywords`` are appended as comma-separated text to
        ``imageOptions.style`` to add specificity (``style`` is ignored by
        the API when stylePreset is named, but Gary can add keywords to
        ``additionalInstructions`` as fallback context).
        ``referenceImagePath`` is stripped — not used in named mode.

    **Approach B — Custom stylePreset (text prompt):**
        ``imageOptions.stylePreset`` is ``"custom"``.
        ``imageOptions.style`` is the full style prompt (1-500 chars).
        ``imageOptions.keywords`` are appended to the style prompt string.
        ``referenceImagePath`` is preserved as a hint for Marcus to use
        when crafting or refining the custom style prompt.

    Also pulls ``theme_id`` from the preset top level into ``themeId``.
    Also strips ``referenceImagePath`` from ``imageOptions`` in named mode
    (it's a design-intent field for Approach B only).
    """
    params = dict(preset.get("parameters", {}))
    if preset.get("theme_id") and "themeId" not in params:
        params["themeId"] = preset["theme_id"]

    img = params.get("imageOptions")
    if isinstance(img, dict):
        img = dict(img)  # shallow copy so we don't mutate the preset
        params["imageOptions"] = img

        style_preset_value = img.get("stylePreset", "")
        keywords = img.pop("keywords", None)
        kw_str = ", ".join(keywords) if keywords and isinstance(keywords, list) else ""

        if style_preset_value == "custom":
            # Approach B: style is the prompt; append keywords to it
            if kw_str:
                style_base = img.get("style", "").strip()
                img["style"] = f"{style_base}, {kw_str}" if style_base else kw_str
            # referenceImagePath stays — Marcus uses it to craft/refine the prompt
        else:
            # Approach A: named tile — style field is ignored by API for named presets.
            # Store keywords as a hint string in a separate key Gary can use in
            # additionalInstructions if needed. Remove referenceImagePath.
            if kw_str:
                img["_keywordsHint"] = kw_str  # Gary reads this, not sent to API
            img.pop("referenceImagePath", None)

    return params


def merge_parameters(
    style_defaults: dict[str, Any],
    content_template: dict[str, Any],
    envelope_overrides: dict[str, Any],
    *,
    style_preset: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge parameters following the priority cascade.

    Priority (later wins):
        1. style guide defaults
        2. style preset (if provided)
        3. content type template
        4. context envelope overrides

    The ``style_preset`` layer is optional for backward compatibility.
    When Gary resolves a named preset via ``resolve_style_preset()``,
    pass the result here so its parameters sit between style guide
    defaults and content type templates.

    Special handling for ``additionalInstructions``: values from all
    layers are **concatenated** (separated by a space) rather than
    overridden.  This lets the preset provide a base instruction
    (e.g., "keep the style uniform") while content-type and envelope
    layers append specifics.
    """
    sources = [style_defaults]
    if style_preset:
        sources.append(style_preset)
    sources.extend([content_template, envelope_overrides])

    merged: dict[str, Any] = {}
    ai_parts: list[str] = []  # additionalInstructions fragments

    for source in sources:
        for key, value in source.items():
            if value is not None and value != "":
                if key == "additionalInstructions":
                    fragment = str(value).strip()
                    if fragment:
                        ai_parts.append(fragment)
                else:
                    merged[key] = value

    if ai_parts:
        merged["additionalInstructions"] = " ".join(ai_parts)

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
