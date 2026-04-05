"""Load and validate frozen per-run constants from a source bundle directory.

Tracked production runs may place ``run-constants.yaml`` at the bundle root.
Agents and CLIs should use this module so RUN_ID, paths, and presets stay
aligned with the frozen file.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - pyyaml is a declared dependency
    yaml = None  # type: ignore[assignment]

from scripts.utilities.file_helpers import project_root as default_project_root

RUN_CONSTANTS_BASENAME = "run-constants.yaml"

ALLOWED_QUALITY_PRESETS = frozenset({"explore", "draft", "production", "regulated"})


class RunConstantsError(ValueError):
    """Invalid or inconsistent run constants."""


@dataclass(frozen=True)
class RunConstants:
    """Canonical fields for a frozen run (matches v4 prompt pack + bundle artifact)."""

    run_id: str
    lesson_slug: str
    bundle_path: str
    primary_source_file: str
    optional_context_assets: tuple[str, ...]
    theme_selection: str
    theme_paramset_key: str
    execution_mode: str
    quality_preset: str
    double_dispatch: bool = False
    schema_version: int | None = None
    frozen_at_utc: str | None = None
    frozen_note: str | None = None


def run_constants_file(bundle_dir: Path) -> Path:
    """Return the path to run-constants.yaml inside the bundle directory."""
    return Path(bundle_dir) / RUN_CONSTANTS_BASENAME


def _coerce_optional_assets(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        stripped = raw.strip()
        if not stripped or stripped.lower() == "none":
            return []
        return [p.strip() for p in stripped.split(",") if p.strip()]
    if isinstance(raw, list):
        out: list[str] = []
        for item in raw:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
        return out
    raise RunConstantsError(
        "optional_context_assets must be a list, comma-separated string, or none; "
        f"got {type(raw).__name__}"
    )


def _require_non_empty_str(data: dict[str, Any], key: str) -> str:
    val = data.get(key)
    if not isinstance(val, str) or not val.strip():
        raise RunConstantsError(f"Missing or empty required string field: {key}")
    return val.strip()


def _normalize_execution_mode(mode: str) -> str:
    m = mode.strip()
    if m in {"tracked", "default", "tracked/default"}:
        return "tracked/default"
    if m in {"ad-hoc", "ad_hoc"}:
        return "ad-hoc"
    raise RunConstantsError(
        "execution_mode must be tracked/default (or aliases tracked|default) or ad-hoc; "
        f"got {mode!r}"
    )


def load_run_constants_dict(path: Path) -> dict[str, Any]:
    """Parse run-constants.yaml into a dict (internal helper)."""
    if yaml is None:
        raise RunConstantsError("pyyaml is required to load run constants")
    if not path.is_file():
        raise RunConstantsError(f"Run constants file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RunConstantsError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise RunConstantsError(f"Expected mapping at root of {path}")
    return raw


def parse_run_constants(data: dict[str, Any]) -> RunConstants:
    """Validate a mapping and return a RunConstants instance."""
    run_id = _require_non_empty_str(data, "run_id")
    lesson_slug = _require_non_empty_str(data, "lesson_slug")
    bundle_path = _require_non_empty_str(data, "bundle_path")
    primary = _require_non_empty_str(data, "primary_source_file")
    theme_sel = _require_non_empty_str(data, "theme_selection")
    theme_params = _require_non_empty_str(data, "theme_paramset_key")
    execution_mode = _normalize_execution_mode(_require_non_empty_str(data, "execution_mode"))
    quality = _require_non_empty_str(data, "quality_preset").lower()
    raw_double_dispatch = data.get("double_dispatch", False)
    if not isinstance(raw_double_dispatch, bool):
        raise RunConstantsError("double_dispatch must be a boolean when present")

    if quality not in ALLOWED_QUALITY_PRESETS:
        raise RunConstantsError(
            f"quality_preset must be one of {sorted(ALLOWED_QUALITY_PRESETS)}; got {quality!r}"
        )
    optional_assets = tuple(_coerce_optional_assets(data.get("optional_context_assets")))

    schema_version = data.get("schema_version")
    if schema_version is not None and not isinstance(schema_version, int):
        raise RunConstantsError("schema_version must be an integer when present")

    frozen_at = data.get("frozen_at_utc")
    if frozen_at is not None and not isinstance(frozen_at, str):
        raise RunConstantsError("frozen_at_utc must be a string when present")
    frozen_note = data.get("frozen_note")
    if frozen_note is not None and not isinstance(frozen_note, str):
        raise RunConstantsError("frozen_note must be a string when present")

    return RunConstants(
        run_id=run_id,
        lesson_slug=lesson_slug,
        bundle_path=bundle_path.replace("\\", "/"),
        primary_source_file=primary,
        optional_context_assets=optional_assets,
        theme_selection=theme_sel,
        theme_paramset_key=theme_params,
        execution_mode=execution_mode,
        quality_preset=quality,
        double_dispatch=raw_double_dispatch,
        schema_version=schema_version,
        frozen_at_utc=frozen_at.strip() if isinstance(frozen_at, str) else None,
        frozen_note=frozen_note.strip() if isinstance(frozen_note, str) else None,
    )


def load_run_constants(
    bundle_dir: Path | str,
    *,
    root: Path | None = None,
    verify_paths_exist: bool = False,
) -> RunConstants:
    """Load ``run-constants.yaml`` from *bundle_dir* and validate fields.

    Args:
        bundle_dir: Absolute or relative path to the bundle directory.
        root: Repository root for ``bundle_path`` alignment (default: discovered).
        verify_paths_exist: If True, require primary PDF and context assets to exist on disk.
    """
    root = root or default_project_root()
    bdir = Path(bundle_dir).resolve()
    path = run_constants_file(bdir)
    data = load_run_constants_dict(path)
    rc = parse_run_constants(data)

    declared = (root / Path(rc.bundle_path)).resolve()
    if declared != bdir:
        raise RunConstantsError(
            "bundle_path does not resolve to the provided bundle_dir: "
            f"bundle_path={rc.bundle_path!r} -> {declared} != {bdir}"
        )

    if verify_paths_exist:
        primary_path = Path(rc.primary_source_file)
        if not primary_path.is_file():
            raise RunConstantsError(f"primary_source_file is not a file: {primary_path}")
        for extra in rc.optional_context_assets:
            ep = Path(extra)
            if not ep.is_file():
                raise RunConstantsError(f"optional context asset is not a file: {ep}")

    return rc


def run_constants_errors(
    bundle_dir: Path | str,
    *,
    root: Path | None = None,
    verify_paths_exist: bool = False,
) -> list[str]:
    """Return a list of human-readable errors; empty if load/validation passed."""
    try:
        load_run_constants(bundle_dir, root=root, verify_paths_exist=verify_paths_exist)
    except RunConstantsError as exc:
        return [str(exc)]
    except OSError as exc:
        return [f"os_error: {exc}"]
    return []


_RUN_ID_SAFE = re.compile(r"^[A-Za-z0-9._\-]+$")


def validate_run_id_for_bundle(rc: RunConstants, bundle_dir: Path) -> list[str]:
    """Optional consistency checks used by bundle validators (warnings, not hard fail)."""
    issues: list[str] = []
    if not _RUN_ID_SAFE.match(rc.run_id):
        issues.append(
            f"run_id contains unusual characters (recommend alphanumeric + ._- only): {rc.run_id!r}"
        )
    # Folder name often includes slug + date; soft hint only
    if rc.lesson_slug and rc.lesson_slug.lower() not in bundle_dir.name.lower():
        issues.append(
            f"lesson_slug {rc.lesson_slug!r} does not appear in bundle folder name "
            f"{bundle_dir.name!r} (verify this is the intended bundle)."
        )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Load and print frozen run-constants.yaml for a source bundle directory."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Path to the source bundle directory containing run-constants.yaml",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root override (defaults to discovered project root).",
    )
    parser.add_argument(
        "--verify-paths",
        action="store_true",
        help="Require primary_source_file and optional_context_assets to exist on disk.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a short text summary.",
    )
    args = parser.parse_args(argv)

    try:
        rc = load_run_constants(
            args.bundle_dir,
            root=args.root,
            verify_paths_exist=args.verify_paths,
        )
    except RunConstantsError as exc:
        if args.json:
            print(json.dumps({"status": "fail", "errors": [str(exc)]}, indent=2))
        else:
            print(f"FAIL: {exc}")
        return 1

    payload = {
        "status": "pass",
        "run_constants": asdict(rc),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"OK run_id={rc.run_id} lesson_slug={rc.lesson_slug} preset={rc.quality_preset}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
