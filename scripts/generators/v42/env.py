"""Jinja2 environment factory for deterministic rendering."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def make_env(template_root: Path | None = None) -> Environment:
    """Create a deterministic Jinja environment for markdown rendering."""
    root = template_root or (Path(__file__).parent / "templates")
    return Environment(
        loader=FileSystemLoader(str(root)),
        autoescape=False,
        keep_trailing_newline=True,
        newline_sequence="\n",
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
        optimized=True,
    )
