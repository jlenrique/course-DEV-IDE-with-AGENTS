"""CLI entry point for initializing all state management infrastructure.

Usage:
    python -m scripts.state_management.init_state

Creates the SQLite coordination database and verifies YAML config files exist.
"""

from __future__ import annotations

import sys

from scripts.state_management.db_init import init_database
from scripts.utilities.file_helpers import project_root


def main() -> int:
    """Initialize state management infrastructure."""
    root = project_root()
    errors: list[str] = []

    print("Initializing state management infrastructure...")

    db_path = init_database()
    print(f"  Created database: {db_path.relative_to(root)}")

    config_dir = root / "state" / "config"
    expected_configs = [
        "course_context.yaml",
        "style_guide.yaml",
        "tool_policies.yaml",
    ]
    for cfg in expected_configs:
        path = config_dir / cfg
        if path.exists():
            print(f"  Verified config: state/config/{cfg}")
        else:
            errors.append(f"Missing config: {path}")
            print(f"  MISSING: state/config/{cfg}")

    memory_dir = root / "_bmad" / "memory"
    sidecars = [
        "master-orchestrator-sidecar",
        "gamma-specialist-sidecar",
        "elevenlabs-specialist-sidecar",
        "canvas-specialist-sidecar",
        "quality-reviewer-sidecar",
    ]
    for sidecar in sidecars:
        sidecar_dir = memory_dir / sidecar
        index_file = sidecar_dir / "index.md"
        if index_file.exists():
            print(f"  Verified sidecar: _bmad/memory/{sidecar}/")
        else:
            errors.append(f"Missing sidecar index: {index_file}")
            print(f"  MISSING: _bmad/memory/{sidecar}/index.md")

    if errors:
        print(f"\n  {len(errors)} issue(s) found. Run story tasks to resolve.")
        return 1

    print("\nState management infrastructure initialized successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
