# /// script
# requires-python = ">=3.10"
# ///
"""Manage run mode (default / ad-hoc) state.

Reads and writes the persistent mode state file at
`state/runtime/mode_state.json`.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def find_project_root() -> Path:
    """Walk up from script location to find the project root (contains state/)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "state").is_dir():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


def get_mode_file(root: Path | None = None) -> Path:
    """Return the mode state file path."""
    root = root or find_project_root()
    return root / "state" / "runtime" / "mode_state.json"


def _read_mode(path: Path) -> dict[str, Any]:
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"mode": "default", "switched_at": None, "switched_by": "system"}


def _write_mode(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def cmd_get(args: argparse.Namespace) -> dict[str, Any]:
    """Read the current mode."""
    path = Path(args.file) if args.file else get_mode_file()
    data = _read_mode(path)
    return {
        "mode": data.get("mode", "default"),
        "switched_at": data.get("switched_at"),
    }


def cmd_set(args: argparse.Namespace) -> dict[str, Any]:
    """Set the run mode."""
    if args.mode not in ("default", "ad-hoc"):
        return {"error": f"Invalid mode: {args.mode}. Must be 'default' or 'ad-hoc'."}

    path = Path(args.file) if args.file else get_mode_file()
    old = _read_mode(path)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    new_data = {
        "mode": args.mode,
        "switched_at": now,
        "switched_by": "marcus",
        "previous_mode": old.get("mode", "default"),
    }
    _write_mode(path, new_data)

    return {
        "mode": args.mode,
        "previous_mode": old.get("mode", "default"),
        "switched_at": now,
        "changed": old.get("mode", "default") != args.mode,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(description="Run mode management")
    parser.add_argument("--file", help="Override mode state file path")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("get", help="Read current mode")

    p_set = sub.add_parser("set", help="Set the run mode")
    p_set.add_argument("mode", choices=["default", "ad-hoc"], help="Target mode")

    return parser


COMMANDS = {"get": cmd_get, "set": cmd_set}


def main(argv: list[str] | None = None) -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    result = COMMANDS[args.command](args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
