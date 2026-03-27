"""Gamma-specific exemplar evaluator.

Extends BaseEvaluator from the woodshed skill to provide Gamma-specific
analysis, reproduction, and comparison logic. This is the agent-specific
evaluation intelligence — the woodshed owns the process, this module
owns the Gamma knowledge.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

import importlib.util
from pathlib import Path as _Path

def _load_module(name: str, path: str):
    """Load a module from an absolute file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_PROJECT_ROOT = _Path(__file__).resolve().parents[3]

_gamma_client_mod = _load_module(
    "gamma_client",
    str(_PROJECT_ROOT / "scripts" / "api_clients" / "gamma_client.py"),
)
GammaClient = _gamma_client_mod.GammaClient

_gamma_ops_mod = _load_module(
    "gamma_operations",
    str(_Path(__file__).resolve().parent / "gamma_operations.py"),
)
download_export = _gamma_ops_mod.download_export
generate_slide = _gamma_ops_mod.generate_slide
load_style_guide_gamma = _gamma_ops_mod.load_style_guide_gamma

_woodshed_mod = _load_module(
    "woodshed_base",
    str(_PROJECT_ROOT / "skills" / "woodshed" / "scripts" / "woodshed_base.py"),
)
BaseEvaluator = _woodshed_mod.BaseEvaluator

logger = logging.getLogger(__name__)

LAYOUT_PATTERNS = {
    "two-column-parallel": {
        "additional_instructions": (
            "Two-column parallel comparison layout. "
            "Equal-width columns side by side. "
            "No additional content beyond what is provided."
        ),
    },
    "title-plus-body": {
        "additional_instructions": (
            "Single-focus layout with bold headline and short body paragraph. "
            "Minimal text, clean layout. "
            "Output ONLY the provided text. Do not add content."
        ),
    },
    "three-column-cards": {
        "additional_instructions": (
            "Three-column card layout with equal-width sections. "
            "Each section has a heading and one-line description. "
            "Output ONLY the provided text. Do not add content."
        ),
    },
    "assessment-interactive": {
        "additional_instructions": (
            "Interactive assessment layout. Question prompt should be prominent. "
            "Answer options clearly separated. "
            "This is a pedagogical assessment, not content delivery."
        ),
    },
    "narrative-progression": {
        "additional_instructions": (
            "Progressive narrative layout with three escalating beats. "
            "Forward momentum — past to present to future. "
            "Not three equal columns; this is a STORY with rising energy."
        ),
    },
}

LEVEL_RUBRIC_WEIGHTS: dict[str, dict[str, str]] = {
    "L1": {
        "structural_fidelity": "high",
        "parameter_accuracy": "high",
        "content_completeness": "medium",
        "context_alignment": "low",
        "creative_quality": "low",
    },
    "L2": {
        "structural_fidelity": "high",
        "parameter_accuracy": "high",
        "content_completeness": "medium",
        "context_alignment": "low",
        "creative_quality": "low",
    },
    "L3": {
        "structural_fidelity": "high",
        "parameter_accuracy": "high",
        "content_completeness": "high",
        "context_alignment": "medium",
        "creative_quality": "low",
    },
    "L4": {
        "structural_fidelity": "high",
        "parameter_accuracy": "medium",
        "content_completeness": "high",
        "context_alignment": "high",
        "creative_quality": "medium",
    },
}


class GammaEvaluator(BaseEvaluator):
    """Gamma-specific evaluator for slide exemplar mastery."""

    @property
    def tool_name(self) -> str:
        return "gamma"

    def analyze_exemplar(
        self, brief: str, source_artifacts: list[Path]
    ) -> dict[str, Any]:
        """Extract layout pattern, content structure, and pedagogical type from brief."""
        analysis: dict[str, Any] = {
            "layout_pattern": None,
            "content_sections": [],
            "pedagogical_type": None,
            "title": None,
            "word_count": 0,
            "has_multiple_sections": False,
        }

        for pattern_name in LAYOUT_PATTERNS:
            if pattern_name in brief.lower().replace(" ", "-"):
                analysis["layout_pattern"] = pattern_name
                break

        layout_markers = {
            "parallel": "two-column-parallel",
            "two-column": "two-column-parallel",
            "comparison": "two-column-parallel",
            "title-plus-body": "title-plus-body",
            "bold headline": "title-plus-body",
            "bold conceptual headline": "title-plus-body",
            "single-focus": "title-plus-body",
            "explanatory slide": "title-plus-body",
            "three-column": "three-column-cards",
            "card layout": "three-column-cards",
            "feature cards": "three-column-cards",
            "assessment": "assessment-interactive",
            "comprehension check": "assessment-interactive",
            "categorization": "assessment-interactive",
            "narrative": "narrative-progression",
            "story arc": "narrative-progression",
            "three-beat": "narrative-progression",
            "progression": "narrative-progression",
        }

        if analysis["layout_pattern"] is None:
            brief_lower = brief.lower()
            for marker, pattern in layout_markers.items():
                if marker in brief_lower:
                    analysis["layout_pattern"] = pattern
                    break

        title_match = re.search(r"\*\*Title\*\*:\s*(.+)", brief)
        if title_match:
            analysis["title"] = title_match.group(1).strip()

        section_matches = re.findall(
            r"\*\*(?:Section|Beat|Left|Right|Body|Prompt)\s*\d*[^*]*\*\*", brief
        )
        analysis["content_sections"] = section_matches
        analysis["has_multiple_sections"] = len(section_matches) > 1

        content_words = brief.split()
        analysis["word_count"] = len(content_words)

        ped_markers = {
            "assessment": "assessment",
            "comprehension": "assessment",
            "quiz": "assessment",
            "narrative": "narrative",
            "story": "narrative",
            "motivational": "narrative",
            "comparison": "content-delivery",
            "lecture": "content-delivery",
            "synthesis": "synthesis",
            "conclusion": "synthesis",
        }
        brief_lower = brief.lower()
        for marker, ped_type in ped_markers.items():
            if marker in brief_lower:
                analysis["pedagogical_type"] = ped_type
                break

        if analysis["pedagogical_type"] is None:
            analysis["pedagogical_type"] = "content-delivery"

        return analysis

    def derive_reproduction_spec(
        self,
        analysis: dict[str, Any],
        style_guide: dict[str, Any],
    ) -> dict[str, Any]:
        """Map exemplar analysis to Gamma API parameters."""
        layout = analysis.get("layout_pattern", "title-plus-body")
        layout_config = LAYOUT_PATTERNS.get(layout, LAYOUT_PATTERNS["title-plus-body"])

        spec: dict[str, Any] = {
            "input_text": "",
            "text_mode": "preserve",
            "format": "presentation",
            "num_cards": 1,
            "additional_instructions": layout_config["additional_instructions"],
            "image_options": {"source": "noImages"},
            "export_as": "pdf",
        }

        if style_guide.get("default_llm"):
            spec["llm"] = style_guide["default_llm"]
        if style_guide.get("theme_id"):
            spec["theme_id"] = style_guide["theme_id"]

        if analysis.get("pedagogical_type") == "assessment":
            spec["text_options"] = {"amount": "brief"}
        elif analysis.get("word_count", 0) < 50:
            spec["text_options"] = {"amount": "brief"}

        return spec

    def execute_reproduction(
        self,
        spec: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute reproduction via GammaClient through gamma_operations."""
        result: dict[str, Any] = {
            "output": None,
            "api_interaction": {},
            "status": "error",
            "error": None,
            "artifact_path": None,
        }

        try:
            params = dict(spec)
            completed = generate_slide(params)
            result["output"] = completed
            result["api_interaction"] = {
                "endpoint": "POST /v1.0/generations",
                "parameters": spec,
                "generation_id": completed.get("id", ""),
                "gamma_url": completed.get("gammaUrl", ""),
            }

            export_url = completed.get("exportUrl")
            if export_url:
                artifact_path = download_export(export_url)
                result["artifact_path"] = str(artifact_path)
                result["api_interaction"]["export_url"] = export_url
                result["api_interaction"]["artifact_path"] = str(artifact_path)

            result["status"] = "completed"

        except Exception as exc:
            result["error"] = str(exc)
            logger.error("Reproduction failed: %s", exc)

        return result

    def compare_reproduction(
        self,
        source_artifacts: list[Path],
        reproduction_output: dict[str, Any],
        analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Compare reproduction against source using Gamma-specific criteria."""
        scores: dict[str, dict[str, Any]] = {}

        if reproduction_output.get("status") != "completed":
            return {
                "scores": {
                    dim: {"score": 0, "notes": "Reproduction failed"}
                    for dim in [
                        "structural_fidelity",
                        "parameter_accuracy",
                        "content_completeness",
                        "context_alignment",
                        "creative_quality",
                    ]
                },
                "conclusion": f"Reproduction failed: {reproduction_output.get('error', 'unknown')}",
            }

        gamma_url = reproduction_output.get("output", {}).get("gammaUrl", "")
        artifact_path = reproduction_output.get("artifact_path", "")
        has_artifact = bool(artifact_path and Path(artifact_path).exists())

        expected_layout = analysis.get("layout_pattern", "unknown")
        scores["structural_fidelity"] = {
            "score": 4 if has_artifact else 2,
            "notes": (
                f"Artifact produced at {artifact_path}. "
                f"Expected layout: {expected_layout}. "
                "Visual layout verification requires human review of the PDF."
            ),
        }

        api_params = reproduction_output.get("api_interaction", {}).get("parameters", {})
        param_checks = [
            api_params.get("num_cards") == 1 or api_params.get("numCards") == 1,
            api_params.get("text_mode") == "preserve" or api_params.get("textMode") == "preserve",
            api_params.get("export_as") == "pdf" or api_params.get("exportAs") == "pdf",
            bool(api_params.get("additional_instructions") or api_params.get("additionalInstructions")),
        ]
        param_score = sum(param_checks)
        scores["parameter_accuracy"] = {
            "score": min(param_score + 1, 5),
            "notes": f"{sum(param_checks)}/4 key parameters correctly set",
        }

        scores["content_completeness"] = {
            "score": 4 if has_artifact else 1,
            "notes": (
                "Artifact produced; content completeness requires visual review. "
                "Check: all sections present, no content dropped, no unauthorized additions."
            ),
        }

        scores["context_alignment"] = {
            "score": 4 if analysis.get("pedagogical_type") else 3,
            "notes": f"Pedagogical type: {analysis.get('pedagogical_type', 'unknown')}",
        }

        scores["creative_quality"] = {
            "score": 3,
            "notes": "Creative quality assessment requires human visual review of the PDF.",
        }

        conclusion_parts = [
            f"Layout: {expected_layout}",
            f"Artifact: {'downloaded' if has_artifact else 'MISSING'}",
            f"Parameters: {sum(param_checks)}/4 correct",
            f"Gamma URL: {gamma_url}",
        ]

        return {
            "scores": scores,
            "conclusion": ". ".join(conclusion_parts),
        }

    def get_custom_rubric_weights(self, level: str) -> dict[str, str]:
        """Adjust rubric weights per L-level."""
        base_level = re.match(r"L\d+", level)
        if base_level:
            key = base_level.group(0)
            if key in LEVEL_RUBRIC_WEIGHTS:
                return LEVEL_RUBRIC_WEIGHTS[key]
        return super().get_custom_rubric_weights(level)
