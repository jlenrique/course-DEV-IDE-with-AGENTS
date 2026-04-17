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
    # All persistent memory directories under _bmad/memory/.
    # 17 follow the persona-based `<name>-sidecar/index.md` convention;
    # `bmad-agent-desmond` uses a distinct memory-sanctum pattern (`INDEX.md`).
    # Total: 18 memory directories. The legacy `master-orchestrator-sidecar`
    # redirect placeholder was removed on 2026-04-16 as part of the
    # persona-naming cascade cleanup.
    memory_entries: list[tuple[str, str]] = [
        ("aria-sidecar", "index.md"),
        ("audra-sidecar", "index.md"),
        ("bmad-agent-desmond", "INDEX.md"),
        ("canvas-specialist-sidecar", "index.md"),
        ("cora-sidecar", "index.md"),
        ("dan-sidecar", "index.md"),
        ("enrique-sidecar", "index.md"),
        ("gary-sidecar", "index.md"),
        ("irene-sidecar", "index.md"),
        ("kim-sidecar", "index.md"),
        ("kira-sidecar", "index.md"),
        ("marcus-sidecar", "index.md"),
        ("mike-sidecar", "index.md"),
        ("mira-sidecar", "index.md"),
        ("quinn-r-sidecar", "index.md"),
        ("tamara-sidecar", "index.md"),
        ("vera-sidecar", "index.md"),
        ("vyx-sidecar", "index.md"),
    ]
    for mem_dir, entry_filename in memory_entries:
        entry_file = memory_dir / mem_dir / entry_filename
        if entry_file.exists():
            print(f"  Verified memory dir: _bmad/memory/{mem_dir}/")
        else:
            errors.append(f"Missing memory entry: {entry_file}")
            print(f"  MISSING: _bmad/memory/{mem_dir}/{entry_filename}")

    if errors:
        print(f"\n  {len(errors)} issue(s) found. Run story tasks to resolve.")
        return 1

    print("\nState management infrastructure initialized successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
