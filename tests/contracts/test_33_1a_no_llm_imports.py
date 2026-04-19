"""Contract: no LLM SDK imports in generator package."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN_ROOT = ROOT / "scripts/generators/v42"
FORBIDDEN = ("openai", "anthropic", "langchain", "transformers", "llm", "gpt", "claude", "bedrock")


def test_generator_has_no_llm_sdk_imports() -> None:
    for py_file in GEN_ROOT.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [n.name.lower() for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").lower()]
            else:
                continue
            for name in names:
                assert not any(
                    token in name for token in FORBIDDEN
                ), f"Forbidden import {name} in {py_file}"
