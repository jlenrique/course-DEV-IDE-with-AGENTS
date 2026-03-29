# /// script
# requires-python = ">=3.10"
# ///
"""Content entity tracking and objective alignment utilities.

Implements asset evolution history, learning-objective alignment persistence,
and release manifest generation for production runs.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any

try:
    from scripts.utilities.ad_hoc_persistence_guard import enforce_ad_hoc_boundary, resolve_run_mode
    from scripts.utilities.file_helpers import project_root
except ModuleNotFoundError:
    def _load_util_module(file_name: str, module_name: str) -> Any:
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "scripts" / "utilities" / file_name
            if candidate.exists():
                spec = importlib.util.spec_from_file_location(module_name, candidate)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
        raise

    _guard_mod = _load_util_module("ad_hoc_persistence_guard.py", "ad_hoc_persistence_guard_local")
    _file_mod = _load_util_module("file_helpers.py", "file_helpers_local")
    enforce_ad_hoc_boundary = _guard_mod.enforce_ad_hoc_boundary
    resolve_run_mode = _guard_mod.resolve_run_mode
    project_root = _file_mod.project_root


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else project_root() / "state" / "runtime" / "coordination.db"
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _hash_path(path: Path) -> str:
    hasher = hashlib.sha256()
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def _load_module(module_name: str, file_path: Path) -> ModuleType:
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Unable to load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _brand_validator() -> ModuleType:
    path = project_root() / "skills" / "quality-control" / "scripts" / "brand_validator.py"
    return _load_module("skills.quality_control.scripts.brand_validator", path)


def _normalize_tokens(text: str) -> set[str]:
    token = ""
    tokens: set[str] = set()
    for ch in text.lower():
        if ch.isalnum() or ch in {"_", "-"}:
            token += ch
        else:
            if len(token) >= 4:
                tokens.add(token)
            token = ""
    if len(token) >= 4:
        tokens.add(token)
    return tokens


def track_asset_evolution(
    *,
    run_id: str,
    asset_id: str,
    artifact_path: str | Path,
    decision_rationale: str,
    metadata: dict[str, Any] | None = None,
    run_mode: str | None = None,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Record a new asset evolution entry for a run."""
    mode = resolve_run_mode(run_mode)
    path = Path(artifact_path)
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")

    guard = enforce_ad_hoc_boundary("production_run_db", mode)
    content_hash = _hash_path(path)

    if not guard["allowed"]:
        return {
            "persisted": False,
            "run_id": run_id,
            "asset_id": asset_id,
            "version": None,
            "content_hash": content_hash,
            "code": guard["code"],
            "reason": guard["reason"],
        }

    conn = _connect(db_path)
    try:
        prior = conn.execute(
            (
                "SELECT MAX(version) AS max_version "
                "FROM asset_evolution WHERE run_id = ? AND asset_id = ?"
            ),
            (run_id, asset_id),
        ).fetchone()
        previous_version = (
            int(prior["max_version"])
            if prior and prior["max_version"] is not None
            else 0
        )
        next_version = previous_version + 1

        conn.execute(
            """
            INSERT INTO asset_evolution (
                run_id,
                asset_id,
                version,
                content_hash,
                decision_rationale,
                metadata_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                asset_id,
                next_version,
                content_hash,
                decision_rationale,
                json.dumps(metadata or {}),
                _now(),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "persisted": True,
        "run_id": run_id,
        "asset_id": asset_id,
        "version": next_version,
        "content_hash": content_hash,
    }


def validate_learning_objective_alignment(
    *,
    run_id: str,
    asset_id: str,
    objectives: list[str],
    content: str | None = None,
    artifact_path: str | Path | None = None,
    run_mode: str | None = None,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Validate and optionally persist objective alignment results."""
    mode = resolve_run_mode(run_mode)
    content_text = content or ""
    if not content_text and artifact_path:
        file_path = Path(artifact_path)
        if file_path.exists():
            content_text = file_path.read_text(encoding="utf-8")

    content_tokens = _normalize_tokens(content_text)

    rows: list[dict[str, Any]] = []
    aligned_count = 0
    for objective in objectives:
        objective_tokens = _normalize_tokens(objective)
        overlap = sorted(content_tokens.intersection(objective_tokens))
        aligned = len(overlap) > 0
        if aligned:
            aligned_count += 1
        rows.append(
            {
                "objective_id": objective,
                "status": "aligned" if aligned else "not-aligned",
                "matched_terms": overlap,
            }
        )

    if not rows:
        alignment_status = "no-objectives"
    elif aligned_count == len(rows):
        alignment_status = "aligned"
    elif aligned_count > 0:
        alignment_status = "partial"
    else:
        alignment_status = "not-aligned"

    guard = enforce_ad_hoc_boundary("course_progress_rollup", mode)
    persisted = False
    if guard["allowed"]:
        conn = _connect(db_path)
        try:
            for row in rows:
                conn.execute(
                    """
                    INSERT INTO learning_objective_map (
                        run_id, asset_id, objective_id, validation_status, aligned_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        asset_id,
                        row["objective_id"],
                        row["status"],
                        _now(),
                    ),
                )
            conn.commit()
            persisted = True
        finally:
            conn.close()

    return {
        "run_id": run_id,
        "asset_id": asset_id,
        "alignment_status": alignment_status,
        "aligned_count": aligned_count,
        "objective_count": len(rows),
        "rows": rows,
        "persisted": persisted,
        "run_mode": mode,
        "blocked": (
            None
            if persisted
            else (
                {"code": guard["code"], "reason": guard["reason"]}
                if not guard["allowed"]
                else None
            )
        ),
    }


def run_brand_enforcement(
    *,
    content: str,
    style_bible_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run brand validation for an asset payload."""
    validator = _brand_validator()
    bible_path = Path(style_bible_path) if style_bible_path else None
    return validator.run_brand_validation(content, style_bible_path=bible_path)


def generate_release_manifest(
    *,
    run_id: str,
    assets: list[dict[str, Any]],
    quality_certified: bool,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Generate a release manifest for final deployment."""
    manifest = {
        "run_id": run_id,
        "generated_at": _now(),
        "quality_certified": bool(quality_certified),
        "asset_count": len(assets),
        "assets": assets,
    }

    target = (
        Path(output_path)
        if output_path
        else project_root() / "state" / "runtime" / "release-manifests" / f"{run_id}.json"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "run_id": run_id,
        "manifest_path": str(target),
        "manifest": manifest,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage content entities and objective alignment")
    parser.add_argument("--db", help="Override coordination database path")

    sub = parser.add_subparsers(dest="command", required=True)

    p_evolve = sub.add_parser("evolve", help="Track asset evolution")
    p_evolve.add_argument("--run-id", required=True)
    p_evolve.add_argument("--asset-id", required=True)
    p_evolve.add_argument("--artifact-path", required=True)
    p_evolve.add_argument("--decision-rationale", default="")
    p_evolve.add_argument("--metadata", default="{}", help="JSON object")
    p_evolve.add_argument("--run-mode", default=None)

    p_align = sub.add_parser("align", help="Validate objective alignment")
    p_align.add_argument("--run-id", required=True)
    p_align.add_argument("--asset-id", required=True)
    p_align.add_argument("--objectives", required=True, help="JSON array of objective strings")
    p_align.add_argument("--content", default="")
    p_align.add_argument("--artifact-path")
    p_align.add_argument("--run-mode", default=None)

    p_manifest = sub.add_parser("manifest", help="Generate release manifest")
    p_manifest.add_argument("--run-id", required=True)
    p_manifest.add_argument("--assets", required=True, help="JSON array of asset records")
    p_manifest.add_argument("--quality-certified", action="store_true")
    p_manifest.add_argument("--output-path")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "evolve":
        result = track_asset_evolution(
            run_id=args.run_id,
            asset_id=args.asset_id,
            artifact_path=args.artifact_path,
            decision_rationale=args.decision_rationale,
            metadata=json.loads(args.metadata),
            run_mode=args.run_mode,
            db_path=args.db,
        )
    elif args.command == "align":
        result = validate_learning_objective_alignment(
            run_id=args.run_id,
            asset_id=args.asset_id,
            objectives=json.loads(args.objectives),
            content=args.content,
            artifact_path=args.artifact_path,
            run_mode=args.run_mode,
            db_path=args.db,
        )
    elif args.command == "manifest":
        result = generate_release_manifest(
            run_id=args.run_id,
            assets=json.loads(args.assets),
            quality_certified=args.quality_certified,
            output_path=args.output_path,
        )
    else:
        result = {"error": f"Unknown command: {args.command}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
