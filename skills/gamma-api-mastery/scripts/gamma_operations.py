"""Agent-level Gamma operations wrapper.

Bridges Gary's parameter decisions and the GammaClient API layer.
Handles style guide loading, parameter merging, generation execution,
polling, export, and artifact download.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

import requests
import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    # Allow running this script directly without requiring manual PYTHONPATH.
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from scripts.api_clients.gamma_client import GammaClient

logger = logging.getLogger(__name__)


REQUIRED_OUTBOUND_FIELDS = {
    "gary_slide_output",
    "quality_assessment",
    "parameter_decisions",
    "recommendations",
    "flags",
}

REQUIRED_THEME_RESOLUTION_FIELDS = {
    "requested_theme_key",
    "resolved_theme_key",
    "resolved_parameter_set",
    "mapping_source",
    "mapping_version",
    "user_confirmation",
}


def _require_gamma_api_key() -> None:
    """Fail fast when Gamma credentials are unavailable."""
    if os.environ.get("GAMMA_API_KEY", "").strip():
        return
    raise RuntimeError(
        "GAMMA_API_KEY is not set. Add it to the environment or to .env at the "
        "repository root before running gamma_operations generate commands."
    )


def _log_run_suffix(run_id: str | None) -> str:
    """Optional APP run correlation for logs (additive; no behavior change)."""
    if run_id is None or not str(run_id).strip():
        return ""
    return f" run_id={str(run_id).strip()}"
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


VOCABULARY_TO_TEXTMODE = {
    "generate": "generate",
    "preserve": "preserve",
    "preserve-strict": "preserve",
}

VOCABULARY_TO_IMAGE_SOURCE = {
    "ai-generated": "aiGenerated",
    "no-images": "noImages",
    "theme-accent": "themeAccent",
    "user-provided": "aiGenerated",
}

VOCABULARY_LAYOUT_TEMPLATES = {
    "single-column": "Single column layout. One content area, full width.",
    "two-column": "Two-column parallel layout. Side-by-side comparison.",
    "full-bleed-image": "Full-bleed image layout. Image fills the slide.",
    "data-table": "Data table layout. Clean tabular presentation with headers.",
    "unconstrained": "",
}


def merge_parameters(
    style_defaults: dict[str, Any],
    content_template: dict[str, Any],
    envelope_overrides: dict[str, Any],
    *,
    style_preset: dict[str, Any] | None = None,
    fidelity_class: str = "creative",
) -> dict[str, Any]:
    """Merge parameters following the priority cascade.

    Priority (later wins):
        1. style guide defaults
        2. style preset (if provided)
        3. content type template
        4. context envelope overrides
        5. fidelity vocabulary enforcement (for literal slides)

    When fidelity_class is 'literal-text' or 'literal-visual', the
    fidelity-control vocabulary fields (text_treatment, image_treatment,
    layout_constraint, content_scope) override free-text
    additionalInstructions.
    """
    sources = [style_defaults]
    if style_preset:
        sources.append(style_preset)
    sources.extend([content_template, envelope_overrides])

    merged: dict[str, Any] = {}
    ai_parts: list[str] = []

    for source in sources:
        for key, value in source.items():
            if value is not None and value != "":
                if key == "additionalInstructions":
                    fragment = str(value).strip()
                    if fragment:
                        ai_parts.append(fragment)
                else:
                    merged[key] = value

    if fidelity_class in ("literal-text", "literal-visual"):
        text_treatment = merged.pop("text_treatment", "preserve")
        image_treatment = merged.pop("image_treatment", "no-images")
        layout_constraint = merged.pop("layout_constraint", "unconstrained")
        content_scope = merged.pop("content_scope", "exact-input-only")

        merged["textMode"] = VOCABULARY_TO_TEXTMODE.get(text_treatment, "preserve")
        merged["imageOptions"] = {
            "source": VOCABULARY_TO_IMAGE_SOURCE.get(image_treatment, "noImages")
        }

        layout_instruction = VOCABULARY_LAYOUT_TEMPLATES.get(layout_constraint, "")
        scope_instruction = (
            "Output ONLY the provided text. Do not add content, steps, or diagrams."
            if content_scope == "exact-input-only"
            else ""
        )
        deterministic_ai = " ".join(filter(None, [layout_instruction, scope_instruction]))
        if deterministic_ai:
            merged["additionalInstructions"] = deterministic_ai
    else:
        merged.pop("text_treatment", None)
        merged.pop("image_treatment", None)
        merged.pop("layout_constraint", None)
        merged.pop("content_scope", None)
        if ai_parts:
            merged["additionalInstructions"] = " ".join(ai_parts)

    return merged


def execute_generation(
    params: dict[str, Any],
    *,
    slides: list[dict[str, Any]] | None = None,
    module_lesson_part: str = "",
    diagram_cards: list[dict[str, Any]] | None = None,
    client: GammaClient | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Production entry point for slide generation.

    Routes to mixed-fidelity two-call split when slides contain different
    fidelity classes, or to single-call generation when all slides share
    the same class (or no fidelity data is provided).

    Args:
        params: Merged parameter dict.
        slides: Optional list of slide dicts with 'fidelity' fields. If
            provided and mixed fidelity is detected, routes to two-call split.
        module_lesson_part: Identifier for doc naming (required for mixed fidelity).
        diagram_cards: Optional literal-visual image URL entries.
        client: Optional pre-configured GammaClient.
        run_id: Optional APP production run id for log correlation.

    Returns:
        For single-call: completed generation data.
        For mixed-fidelity: dict with gary_slide_output, provenance, generation_mode, calls_made.
    """
    if slides:
        groups = partition_by_fidelity(slides)
        has_creative = len(groups["creative"]) > 0
        has_literal = len(groups["literal"]) > 0

        if has_creative and has_literal:
            return generate_deck_mixed_fidelity(
                slides, params, module_lesson_part,
                client=client, diagram_cards=diagram_cards, run_id=run_id,
            )

    return generate_slide(params, client=client, run_id=run_id)


def validate_outbound_contract(payload: dict[str, Any]) -> None:
    """Validate required outbound fields for Gary mixed-fidelity results.

    Raises:
        ValueError: If required fields are missing or malformed.
    """
    missing = sorted(k for k in REQUIRED_OUTBOUND_FIELDS if k not in payload)
    if missing:
        raise ValueError(
            "Gary outbound contract validation failed. Missing required "
            f"field(s): {', '.join(missing)}"
        )
    if not isinstance(payload.get("recommendations"), list):
        raise ValueError("Gary outbound contract validation failed: recommendations must be a list")
    if not isinstance(payload.get("flags"), dict):
        raise ValueError("Gary outbound contract validation failed: flags must be an object")
    if not isinstance(payload.get("quality_assessment"), dict):
        raise ValueError(
            "Gary outbound contract validation failed: quality_assessment must be an object"
        )


def _confirmation_is_true(value: Any) -> bool:
    """Return True when user confirmation is explicitly affirmative."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "approved", "confirmed"}
    return False


def resolve_theme_mapping_handshake(params: dict[str, Any]) -> dict[str, Any]:
    """Resolve theme-mapping handshake from params or embedded theme_resolution.

    Accepts either:
    - params["theme_resolution"] object, or
    - top-level dispatch keys populated by pre-dispatch packaging.
    """
    embedded = params.get("theme_resolution")
    if isinstance(embedded, dict):
        return dict(embedded)

    return {
        "requested_theme_key": params.get("requested_theme_key") or params.get("theme_selection"),
        "resolved_theme_key": params.get("resolved_theme_key")
        or params.get("theme_id")
        or params.get("themeId"),
        "resolved_parameter_set": params.get("resolved_parameter_set")
        or params.get("theme_paramset_key"),
        "mapping_source": params.get("mapping_source"),
        "mapping_version": params.get("mapping_version"),
        "user_confirmation": params.get("user_confirmation"),
    }


def validate_theme_mapping_handshake(theme_resolution: dict[str, Any]) -> None:
    """Fail closed if theme selection -> parameter mapping is incomplete."""
    missing = sorted(
        key
        for key in REQUIRED_THEME_RESOLUTION_FIELDS
        if key not in theme_resolution
        or theme_resolution.get(key) is None
        or (isinstance(theme_resolution.get(key), str) and not str(theme_resolution.get(key)).strip())
    )
    if missing:
        raise ValueError(
            "Theme mapping handshake failed. Missing required field(s): "
            f"{', '.join(missing)}"
        )
    if not _confirmation_is_true(theme_resolution.get("user_confirmation")):
        raise ValueError(
            "Theme mapping handshake failed. user_confirmation must be explicit "
            "(true/yes/approved/confirmed)."
        )


def generate_slide(
    params: dict[str, Any],
    *,
    client: GammaClient | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Execute a single text-based Gamma API call with merged parameters.

    This is the low-level single-call function. For production use with
    fidelity-aware routing, use ``execute_generation()`` instead.

    Args:
        params: Merged parameter dict with at least ``input_text``
            and ``text_mode``.
        client: Optional pre-configured GammaClient.
        run_id: Optional APP production run id for log correlation.

    Returns:
        Completed generation data including ``gammaUrl`` and
        ``exportUrl`` (if export was requested).
    """
    _require_gamma_api_key()

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
    logger.info(
        "Gamma generation started: generation_id=%s%s",
        gen_id,
        _log_run_suffix(run_id),
    )

    completed = client.wait_for_generation(gen_id)
    return completed


def generate_from_template(
    gamma_id: str,
    prompt: str,
    params: dict[str, Any] | None = None,
    *,
    client: GammaClient | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Execute a template-based Gamma generation.

    Args:
        gamma_id: The template's gammaId.
        prompt: Content/instructions for the template.
        params: Optional additional params (theme_id, export_as, etc.).
        client: Optional pre-configured GammaClient.
        run_id: Optional APP production run id for log correlation.

    Returns:
        Completed generation data.
    """
    _require_gamma_api_key()

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
    logger.info(
        "Gamma template generation started: generation_id=%s template_id=%s%s",
        gen_id,
        gamma_id,
        _log_run_suffix(run_id),
    )

    completed = client.wait_for_generation(gen_id)
    return completed


def download_export(
    export_url: str,
    output_dir: Path | str | None = None,
    filename: str | None = None,
    *,
    run_id: str | None = None,
) -> Path:
    """Download an exported artifact from a signed URL.

    Args:
        export_url: Signed download URL from completed generation.
        output_dir: Directory to save to. Defaults to staging.
        filename: Output filename. Auto-derived from URL if not provided.
        run_id: Optional APP production run id for log correlation.

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
    logger.info(
        "Gamma export downloaded: bytes=%d path=%s%s",
        len(resp.content),
        output_path,
        _log_run_suffix(run_id),
    )

    return output_path


def generate_deck_mixed_fidelity(
    slides: list[dict[str, Any]],
    base_params: dict[str, Any],
    module_lesson_part: str,
    *,
    client: GammaClient | None = None,
    diagram_cards: list[dict[str, Any]] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Orchestrate two-call split generation for mixed-fidelity decks.

    When a deck contains both creative and literal slides, Gamma's deck-level
    textMode constraint requires two separate API calls: one in generate mode
    for creative slides and one in preserve mode for literal slides. This
    function partitions, generates, and reassembles the output.

    Args:
        slides: List of slide dicts with 'slide_number', 'content', 'fidelity'.
        base_params: Merged parameters from the cascade
            (style guide + preset + template + envelope).
        module_lesson_part: Identifier for doc naming (e.g., "C1-M1-P2-Macro-Trends").
        client: Optional pre-configured GammaClient.
        diagram_cards: Optional list of literal-visual image URL entries.
        run_id: Optional APP production run id for log correlation.

    Returns:
        Dict with 'gary_slide_output', 'provenance', 'generation_mode', 'calls_made'.
    """
    if client is None:
        client = GammaClient()

    theme_resolution = resolve_theme_mapping_handshake(base_params)
    validate_theme_mapping_handshake(theme_resolution)

    groups = partition_by_fidelity(slides)
    creative_slides = groups["creative"]
    literal_slides = groups["literal"]

    card_map = {dc["card_number"]: dc for dc in diagram_cards} if diagram_cards else {}

    creative_results: list[dict[str, Any]] = []
    literal_results: list[dict[str, Any]] = []
    calls_made = 0

    if creative_slides:
        creative_params = {**base_params, "textMode": "generate"}
        creative_params.pop("text_mode", None)
        creative_input = "\n---\n".join(s.get("content", "") for s in creative_slides)
        creative_nums = [s["slide_number"] for s in creative_slides]
        title = build_doc_title(module_lesson_part, "creative", creative_nums)
        creative_params["input_text"] = f"{title}\n---\n{creative_input}"
        creative_params["num_cards"] = len(creative_slides)
        creative_params["card_split"] = "inputTextBreaks"

        gen_result = generate_slide(creative_params, client=client, run_id=run_id)
        calls_made += 1
        creative_gen_id = gen_result.get("generationId", gen_result.get("id", ""))

        for slide in creative_slides:
            card_num = slide["slide_number"]
            creative_results.append({
                "slide_id": f"{module_lesson_part}-card-{card_num:02d}",
                "file_path": None,
                "card_number": card_num,
                "visual_description": f"[pending export — creative slide {card_num}]",
                "source_ref": slide.get("source_ref", f"slide-brief.md#Slide {card_num}"),
                "generation_id": creative_gen_id,
                "fidelity": "creative",
            })

    if literal_slides:
        literal_params = {**base_params}
        literal_params["textMode"] = "preserve"
        literal_params["text_mode"] = "preserve"
        literal_params.pop("additionalInstructions", None)
        literal_params["additional_instructions"] = (
            "Output ONLY the provided text. Do not add content, steps, "
            "or diagrams beyond what is given. Do not embellish or expand."
        )
        literal_params["image_options"] = {"source": "noImages"}

        literal_input_parts = []
        for s in literal_slides:
            content = s.get("content", "")
            if s["slide_number"] in card_map:
                img_url = card_map[s["slide_number"]]["image_url"]
                is_valid, reason = validate_image_url(img_url)
                if not is_valid:
                    raise ValueError(
                        f"diagram_cards card_number {s['slide_number']}: "
                        f"image URL validation failed: {reason} — URL: {img_url}"
                    )
                content = f"![diagram]({img_url})\n\n{content}"
                literal_params["image_options"] = {"source": "aiGenerated"}
            literal_input_parts.append(content)

        literal_nums = [s["slide_number"] for s in literal_slides]
        title = build_doc_title(module_lesson_part, "literal", literal_nums)
        literal_params["input_text"] = f"{title}\n---\n" + "\n---\n".join(literal_input_parts)
        literal_params["num_cards"] = len(literal_slides)
        literal_params["card_split"] = "inputTextBreaks"

        gen_result = generate_slide(literal_params, client=client, run_id=run_id)
        calls_made += 1
        literal_gen_id = gen_result.get("generationId", gen_result.get("id", ""))

        for slide in literal_slides:
            card_num = slide["slide_number"]
            fidelity = slide.get("fidelity", "literal-text")
            literal_results.append({
                "slide_id": f"{module_lesson_part}-card-{card_num:02d}",
                "file_path": None,
                "card_number": card_num,
                "visual_description": f"[pending export — {fidelity} slide {card_num}]",
                "source_ref": slide.get("source_ref", f"slide-brief.md#Slide {card_num}"),
                "generation_id": literal_gen_id,
                "fidelity": fidelity,
            })

    if not creative_slides and not literal_slides:
        empty_payload = {
            "gary_slide_output": [],
            "quality_assessment": {
                "overall_score": 0.0,
                "dimensions": {
                    "layout_integrity": 0.0,
                    "parameter_confidence": 0.0,
                    "embellishment_risk_control": 0.0,
                },
                "embellishment_detected": False,
                "embellishment_details": [],
            },
            "parameter_decisions": {
                "theme_id": theme_resolution["resolved_theme_key"],
                "requested_theme_key": theme_resolution["requested_theme_key"],
                "resolved_parameter_set": theme_resolution["resolved_parameter_set"],
                "text_mode": "generate",
                "card_split": "inputTextBreaks",
                "num_cards": 0,
            },
            "recommendations": [
                "No slides provided for mixed-fidelity generation; verify slide brief inputs.",
            ],
            "flags": {
                "embellishment_control_used": False,
                "constraint_phrasing": "",
                "constraint_effectiveness": 0.0,
                "theme_mapping_verified": True,
                "theme_mapping_source": theme_resolution["mapping_source"],
                "run_validation_artifact_pointer": (
                    f"run://{run_id}/gary/outbound-contract-validation"
                    if run_id
                    else "run://unknown/gary/outbound-contract-validation"
                ),
            },
            "theme_resolution": theme_resolution,
            "provenance": [],
            "generation_mode": "text",
            "calls_made": 0,
        }
        validate_outbound_contract(empty_payload)
        return empty_payload

    unified = reassemble_slide_output(creative_results, literal_results)

    card_numbers = [r.get("card_number", 0) for r in unified]
    sorted_unique = (
        card_numbers == sorted(card_numbers)
        and len(card_numbers) == len(set(card_numbers))
    )
    contiguous = (
        card_numbers == list(range(min(card_numbers), max(card_numbers) + 1))
        if card_numbers
        else True
    )
    layout_integrity = 1.0 if sorted_unique and contiguous else 0.75
    parameter_confidence = 0.9 if calls_made > 0 else 0.0
    literal_count = len(literal_slides)
    embellishment_risk_control = 0.9 if literal_count > 0 else 0.8
    quality_assessment = {
        "overall_score": round(
            (layout_integrity + parameter_confidence + embellishment_risk_control) / 3,
            2,
        ),
        "dimensions": {
            "layout_integrity": round(layout_integrity, 2),
            "parameter_confidence": round(parameter_confidence, 2),
            "embellishment_risk_control": round(embellishment_risk_control, 2),
        },
        "embellishment_detected": False,
        "embellishment_details": [],
    }

    parameter_decisions = {
        "theme_id": theme_resolution["resolved_theme_key"],
        "requested_theme_key": theme_resolution["requested_theme_key"],
        "resolved_parameter_set": theme_resolution["resolved_parameter_set"],
        "text_mode": "mixed (creative=generate, literal=preserve)",
        "card_split": "inputTextBreaks",
        "num_cards": len(unified),
        "image_options": {
            "literal_default": "noImages",
            "literal_diagram_override": "aiGenerated" if bool(diagram_cards) else "none",
        },
    }
    if base_params.get("export_as") or base_params.get("exportAs"):
        parameter_decisions["export_as"] = (
            base_params.get("export_as") or base_params.get("exportAs")
        )

    recommendations: list[str] = []
    if not contiguous:
        recommendations.append(
            "Card numbers are not contiguous; verify slide brief ordering and "
            "reassembly mapping."
        )
    if not sorted_unique:
        recommendations.append(
            "Duplicate or unsorted card numbers detected; resolve before Irene "
            "Pass 2 handoff."
        )

    flags = {
        "embellishment_control_used": literal_count > 0,
        "constraint_phrasing": (
            "Output ONLY the provided text. Do not add content, steps, or "
            "diagrams beyond what is given."
            if literal_count > 0
            else ""
        ),
        "constraint_effectiveness": round(embellishment_risk_control, 2),
        "theme_mapping_verified": True,
        "theme_mapping_source": theme_resolution["mapping_source"],
        "run_validation_artifact_pointer": (
            f"run://{run_id}/gary/outbound-contract-validation"
            if run_id
            else "run://unknown/gary/outbound-contract-validation"
        ),
    }

    payload = {
        "gary_slide_output": [
            {
                "slide_id": r["slide_id"],
                "file_path": r.get("file_path"),
                "card_number": r["card_number"],
                "visual_description": r.get("visual_description", ""),
                "source_ref": r.get("source_ref", ""),
            }
            for r in unified
        ],
        "quality_assessment": quality_assessment,
        "parameter_decisions": parameter_decisions,
        "recommendations": recommendations,
        "flags": flags,
        "theme_resolution": theme_resolution,
        "provenance": [
            {
                "card_number": r["card_number"],
                "source_call": r["source_call"],
                "generation_id": r.get("generation_id", ""),
                "fidelity": r.get("fidelity", "creative"),
            }
            for r in unified
        ],
        "generation_mode": "text",
        "calls_made": calls_made,
    }
    validate_outbound_contract(payload)
    return payload


def partition_by_fidelity(
    slides: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Partition slide brief slides into creative and literal groups.

    Args:
        slides: List of slide dicts, each with at minimum 'slide_number',
                'content', and 'fidelity' (defaults to 'creative').

    Returns:
        Dict with keys 'creative' and 'literal', each containing the
        slides assigned to that group with their original slide numbers preserved.
    """
    creative: list[dict[str, Any]] = []
    literal: list[dict[str, Any]] = []

    for slide in slides:
        fidelity = slide.get("fidelity", "creative")
        if fidelity in ("literal-text", "literal-visual"):
            literal.append(slide)
        else:
            creative.append(slide)

    return {"creative": creative, "literal": literal}


def build_doc_title(
    module_lesson_part: str,
    fidelity_class: str,
    slide_numbers: list[int],
) -> str:
    """Build a formulaic Gamma document title for archival integrity.

    Pattern: {module-lesson-part}_{fidelity-class}_{slide-range}
    Examples: C1-M1-P2-Macro-Trends_creative_s01-s09
              C1-M1-P2-Macro-Trends_literal_s10
    """
    if len(slide_numbers) == 1:
        slide_range = f"s{slide_numbers[0]:02d}"
    else:
        slide_range = f"s{min(slide_numbers):02d}-s{max(slide_numbers):02d}"
    return f"{module_lesson_part}_{fidelity_class}_{slide_range}"


def reassemble_slide_output(
    creative_results: list[dict[str, Any]],
    literal_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Reassemble results from two Gamma calls into unified slide output.

    Both lists should contain dicts with 'card_number' for ordering.
    Returns a unified list sorted by card_number with provenance metadata.
    """
    all_results = []

    for item in creative_results:
        item["source_call"] = "creative"
        item["fidelity"] = "creative"
        item["visual_description"] = (
            f"Creative slide generated by Gamma for card {item.get('card_number')}; "
            "final visual grounding occurs in perception artifacts."
        )
        all_results.append(item)

    for item in literal_results:
        item["source_call"] = "literal"
        fidelity = item.get("fidelity", "literal-text")
        item["visual_description"] = (
            f"{fidelity} slide generated by Gamma for card {item.get('card_number')}; "
            "source text constraints enforced for literal fidelity."
        )
        all_results.append(item)

    all_results.sort(key=lambda x: x.get("card_number", 0))
    return all_results


def validate_image_url(url: str, timeout: int = 10) -> tuple[bool, str]:
    """Validate that an image URL is HTTPS-accessible with an image content type.

    Returns:
        (is_valid, reason) tuple.
    """
    if not url.startswith("https://"):
        return False, "URL must use HTTPS"

    image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
    has_image_ext = any(url.lower().split("?")[0].endswith(ext) for ext in image_extensions)

    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            return False, f"HTTP {resp.status_code}"

        content_type = resp.headers.get("content-type", "")
        if "image/" in content_type or has_image_ext:
            return True, "OK"

        return (
            False,
            f"Content-Type '{content_type}' is not an image type and URL lacks image extension",
        )
    except requests.RequestException as e:
        return False, f"Request failed: {e}"


if __name__ == "__main__":
    import json
    import sys

    usage = (
        "Usage: python gamma_operations.py <command> [args]\n"
        "Commands:\n"
        "  generate <input_text_file> [--fidelity-json <slides_json>] [--module <id>]\n"
        "    [--diagram-cards <json>] [--run-id <production_run_id>]\n"
        "  validate-url <url>\n"
        "  merge-params <style_json> <template_json> <envelope_json> [--fidelity-class <class>]"
    )

    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "validate-url" and len(sys.argv) >= 3:
        valid, reason = validate_image_url(sys.argv[2])
        print(json.dumps({"valid": valid, "reason": reason}))
        sys.exit(0 if valid else 1)

    if cmd == "merge-params" and len(sys.argv) >= 5:
        style = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        template = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
        envelope = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
        fc = "creative"
        if "--fidelity-class" in sys.argv:
            fc = sys.argv[sys.argv.index("--fidelity-class") + 1]
        result = merge_parameters(style, template, envelope, fidelity_class=fc)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    if cmd == "generate" and len(sys.argv) >= 3:
        input_text = Path(sys.argv[2]).read_text(encoding="utf-8")
        slides_data = None
        module_id = ""
        diagram_cards_data = None

        if "--fidelity-json" in sys.argv:
            idx = sys.argv.index("--fidelity-json") + 1
            slides_data = json.loads(Path(sys.argv[idx]).read_text(encoding="utf-8"))
        if "--module" in sys.argv:
            idx = sys.argv.index("--module") + 1
            module_id = sys.argv[idx]
        if "--diagram-cards" in sys.argv:
            idx = sys.argv.index("--diagram-cards") + 1
            diagram_cards_data = json.loads(Path(sys.argv[idx]).read_text(encoding="utf-8"))

        run_id_cli: str | None = None
        if "--run-id" in sys.argv:
            idx = sys.argv.index("--run-id") + 1
            if idx < len(sys.argv):
                run_id_cli = sys.argv[idx]

        params = {"input_text": input_text, "textMode": "generate"}
        result = execute_generation(
            params,
            slides=slides_data,
            module_lesson_part=module_id,
            diagram_cards=diagram_cards_data,
            run_id=run_id_cli,
        )
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0)

    print(usage)
    sys.exit(1)
