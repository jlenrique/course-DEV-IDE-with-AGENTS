"""Stable CLI wrapper for source-bundle confidence validation.

This wrapper exists so workflow docs can invoke a module path that is resilient
to environment quirks around direct script execution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import ModuleType


def _load_validator_module(script_path: Path) -> ModuleType:
    source = script_path.read_text(encoding="utf-8")
    if source.startswith("# /// script"):
        marker = "\n# ///"
        end = source.find(marker, 1)
        if end != -1:
            source = source[end + len(marker) :].lstrip("\n")

    module = ModuleType("validate_source_bundle_confidence_script")
    module.__file__ = str(script_path)
    code = compile(source, str(script_path), "exec")
    exec(code, module.__dict__)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate source bundle confidence consistency")
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    script = (
        repo_root
        / "skills"
        / "bmad-agent-marcus"
        / "scripts"
        / "validate-source-bundle-confidence.py"
    )
    mod = _load_validator_module(script)

    result = mod.validate_source_bundle_confidence(
        bundle_dir=args.bundle_dir,
        receipt_path=args.receipt,
        repo_root=args.repo_root,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
