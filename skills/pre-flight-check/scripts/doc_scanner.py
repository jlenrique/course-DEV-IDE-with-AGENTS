"""Tool documentation scanner — prepares scan instructions for Ref MCP.

This module defines scan targets and search patterns for detecting
tool API changes, deprecations, and new capabilities. The actual
scanning is performed by the agent using the Ref MCP tools
(ref_search_documentation, ref_read_url).

Usage:
    from skills.pre-flight-check.scripts.doc_scanner import get_scan_instructions
    instructions = get_scan_instructions()
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScanTarget:
    """A documentation scan target for a specific tool."""

    tool_name: str
    doc_url: str
    search_queries: list[str]
    focus_areas: list[str]


SCAN_TARGETS: list[ScanTarget] = [
    ScanTarget(
        tool_name="Gamma",
        doc_url="https://developers.gamma.app",
        search_queries=[
            "Gamma API changelog 2026",
            "Gamma API new endpoints",
        ],
        focus_areas=[
            "New generation parameters or LLM options",
            "Rate limit changes",
            "New output format support",
        ],
    ),
    ScanTarget(
        tool_name="ElevenLabs",
        doc_url="https://elevenlabs.io/docs/api-reference",
        search_queries=[
            "ElevenLabs API release notes 2026",
            "ElevenLabs new voice models",
        ],
        focus_areas=[
            "New voice models or languages",
            "TTS parameter changes",
            "Pricing or quota changes",
        ],
    ),
    ScanTarget(
        tool_name="Canvas LMS",
        doc_url="https://canvas.instructure.com/doc/api",
        search_queries=[
            "Canvas LMS API deprecation notice 2026",
            "Canvas API migration instructure",
        ],
        focus_areas=[
            "Endpoint deprecations (docs moving to developerdocs.instructure.com)",
            "Authentication changes",
            "New quiz or assignment API features",
        ],
    ),
    ScanTarget(
        tool_name="Qualtrics",
        doc_url="https://api.qualtrics.com",
        search_queries=[
            "Qualtrics API v3 changelog 2026",
        ],
        focus_areas=[
            "New question types or survey features",
            "API version changes",
            "Authentication updates",
        ],
    ),
    ScanTarget(
        tool_name="Canva",
        doc_url="https://canva.dev/docs/connect",
        search_queries=[
            "Canva Connect API updates 2026",
            "Canva MCP server updates",
        ],
        focus_areas=[
            "OAuth flow improvements (may resolve Cursor redirect issue)",
            "New design creation or export capabilities",
            "MCP server updates",
        ],
    ),
]


def get_scan_instructions() -> list[dict[str, object]]:
    """Generate agent-readable scan instructions for Ref MCP.

    Returns a list of instruction dicts, each containing the tool name,
    search queries to execute, and focus areas to watch for.
    """
    return [
        {
            "tool": target.tool_name,
            "doc_url": target.doc_url,
            "search_queries": target.search_queries,
            "focus_areas": target.focus_areas,
            "instruction": (
                f"Use ref_search_documentation with queries: {target.search_queries}. "
                f"Then use ref_read_url on {target.doc_url} if relevant changes found. "
                f"Focus on: {', '.join(target.focus_areas)}."
            ),
        }
        for target in SCAN_TARGETS
    ]


def format_scan_prompt() -> str:
    """Generate a formatted prompt for the agent to execute doc scanning."""
    lines = [
        "## Tool Documentation Scan",
        "",
        "Use the Ref MCP to check for recent changes in tool APIs.",
        "For each tool below, run the search queries and report any findings.",
        "",
    ]
    for target in SCAN_TARGETS:
        lines.append(f"### {target.tool_name}")
        lines.append(f"- Doc URL: {target.doc_url}")
        lines.append("- Search queries:")
        for q in target.search_queries:
            lines.append(f"  - `{q}`")
        lines.append("- Watch for:")
        for f in target.focus_areas:
            lines.append(f"  - {f}")
        lines.append("")

    return "\n".join(lines)
