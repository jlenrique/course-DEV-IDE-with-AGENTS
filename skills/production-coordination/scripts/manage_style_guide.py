# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Read and write tool parameter preferences in the style guide.

Provides Marcus with programmatic access to `state/config/style_guide.yaml`
for parameter intelligence — reading established preferences and saving
newly elicited ones.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def find_project_root() -> Path:
    """Walk up from script location to find the project root (contains state/)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "state").is_dir():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


def get_style_guide_path(root: Path | None = None) -> Path:
    """Return the style guide YAML path."""
    root = root or find_project_root()
    return root / "state" / "config" / "style_guide.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not yaml:
        return {"error": "pyyaml not installed"}
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _save_yaml(path: Path, data: dict[str, Any]) -> None:
    if not yaml:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def cmd_get(args: argparse.Namespace) -> dict[str, Any]:
    """Read parameter preferences for a tool."""
    path = Path(args.file) if args.file else get_style_guide_path()
    data = _load_yaml(path)
    params = data.get("tool_parameters", {})

    if args.tool:
        tool_params = params.get(args.tool, {})
        if args.key:
            value = tool_params.get(args.key)
            return {"tool": args.tool, "key": args.key, "value": value, "found": value is not None}
        return {"tool": args.tool, "parameters": tool_params}

    return {"tools": list(params.keys()), "all_parameters": params}


def cmd_set(args: argparse.Namespace) -> dict[str, Any]:
    """Write a parameter preference for a tool."""
    path = Path(args.file) if args.file else get_style_guide_path()
    data = _load_yaml(path)

    if "tool_parameters" not in data:
        data["tool_parameters"] = {}
    if args.tool not in data["tool_parameters"]:
        data["tool_parameters"][args.tool] = {}

    old_value = data["tool_parameters"][args.tool].get(args.key)

    try:
        value: Any = json.loads(args.value)
    except (json.JSONDecodeError, TypeError):
        value = args.value

    data["tool_parameters"][args.tool][args.key] = value
    _save_yaml(path, data)

    return {
        "tool": args.tool,
        "key": args.key,
        "value": value,
        "previous_value": old_value,
        "saved": True,
    }


def cmd_list_tools(args: argparse.Namespace) -> dict[str, Any]:
    """List all tools with configured parameters."""
    path = Path(args.file) if args.file else get_style_guide_path()
    data = _load_yaml(path)
    params = data.get("tool_parameters", {})
    tools = []
    for tool, prefs in params.items():
        configured = [k for k, v in prefs.items() if v not in (None, "", False)]
        tools.append({"tool": tool, "configured_keys": len(configured), "total_keys": len(prefs)})
    return {"tools": tools, "count": len(tools)}


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(description="Style guide parameter management")
    parser.add_argument("--file", help="Override style guide path")
    sub = parser.add_subparsers(dest="command", required=True)

    p_get = sub.add_parser("get", help="Read parameter preferences")
    p_get.add_argument("--tool", help="Tool name (e.g. gamma, elevenlabs)")
    p_get.add_argument("--key", help="Specific parameter key")

    p_set = sub.add_parser("set", help="Write a parameter preference")
    p_set.add_argument("tool", help="Tool name")
    p_set.add_argument("key", help="Parameter key")
    p_set.add_argument("value", help="Parameter value (JSON-parsed if valid)")

    sub.add_parser("list-tools", help="List configured tools")

    return parser


COMMANDS = {"get": cmd_get, "set": cmd_set, "list-tools": cmd_list_tools}


def main(argv: list[str] | None = None) -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    result = COMMANDS[args.command](args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
