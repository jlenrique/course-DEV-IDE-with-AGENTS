"""L1 lockstep check for Marcus dispatch registry vs code enum."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from marcus.dispatch.contract import DISPATCH_KIND_TO_SPECIALIST, DispatchKind
from scripts.utilities.file_helpers import project_root

DEFAULT_REGISTRY_PATH = (
    project_root()
    / "skills"
    / "bmad-agent-marcus"
    / "references"
    / "dispatch-registry.yaml"
)
REPORTS_ROOT = project_root() / "reports" / "dev-coherence"


def _load_registry(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing dispatch registry: {path}")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("dispatch-registry root must be a mapping")
    rows = loaded.get("dispatch_edges")
    if not isinstance(rows, list):
        raise ValueError("dispatch-registry missing dispatch_edges list")
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"dispatch_edges[{index}] must be a mapping")
        kind = str(row.get("dispatch_kind") or "").strip()
        specialist = str(row.get("specialist_id") or "").strip().lower()
        if not kind:
            raise ValueError(f"dispatch_edges[{index}] missing dispatch_kind")
        if not specialist:
            raise ValueError(f"dispatch_edges[{index}] missing specialist_id")
        normalized.append({"dispatch_kind": kind, "specialist_id": specialist})
    return normalized


def _trace_payload(
    checks: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    closure_gate: str,
) -> dict[str, Any]:
    return {
        "lane": "L1",
        "scope": "dispatch-registry-lockstep",
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "closure_gate": closure_gate,
        "l1_checks_run": checks,
        "findings": findings,
    }


def run_check(registry_path: Path = DEFAULT_REGISTRY_PATH) -> tuple[int, dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    try:
        rows = _load_registry(registry_path)
    except Exception as exc:  # noqa: BLE001
        return 2, _trace_payload(
            checks,
            [{"check": "structural", "message": str(exc)}],
            "STRUCTURAL",
        )

    code_kinds = {kind.value for kind in DispatchKind}
    registry_kinds = [row["dispatch_kind"] for row in rows]
    registry_kind_set = set(registry_kinds)

    duplicate_kinds = sorted({kind for kind in registry_kinds if registry_kinds.count(kind) > 1})
    duplicates_ok = len(duplicate_kinds) == 0
    checks.append({"check": 1, "name": "no-duplicate-dispatch-kind", "pass": duplicates_ok})
    if not duplicates_ok:
        findings.append({"check": 1, "message": "Duplicate dispatch_kind entries", "duplicates": duplicate_kinds})

    set_ok = code_kinds == registry_kind_set
    checks.append({"check": 2, "name": "dispatch-kind-set-equality", "pass": set_ok})
    if not set_ok:
        findings.append(
            {
                "check": 2,
                "message": "dispatch_kind set mismatch between code and registry",
                "code_only": sorted(code_kinds - registry_kind_set),
                "registry_only": sorted(registry_kind_set - code_kinds),
            }
        )

    specialist_ok = True
    specialist_mismatches: list[dict[str, str]] = []
    for row in rows:
        kind_value = row["dispatch_kind"]
        try:
            kind = DispatchKind(kind_value)
        except ValueError:
            specialist_ok = False
            specialist_mismatches.append(
                {
                    "dispatch_kind": kind_value,
                    "reason": "unknown_dispatch_kind",
                    "registry_specialist": row["specialist_id"],
                }
            )
            continue

        expected_specialist = DISPATCH_KIND_TO_SPECIALIST[kind].value
        if row["specialist_id"] != expected_specialist:
            specialist_ok = False
            specialist_mismatches.append(
                {
                    "dispatch_kind": kind_value,
                    "expected_specialist": expected_specialist,
                    "registry_specialist": row["specialist_id"],
                }
            )

    checks.append({"check": 3, "name": "dispatch-kind-specialist-alignment", "pass": specialist_ok})
    if not specialist_ok:
        findings.append(
            {
                "check": 3,
                "message": "dispatch_kind -> specialist_id alignment mismatch",
                "rows": specialist_mismatches,
            }
        )

    if findings:
        return 1, _trace_payload(checks, findings, "FAIL")
    return 0, _trace_payload(checks, [], "PASS")


def _write_trace(payload: dict[str, Any], exit_code: int) -> Path:
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%d-%H%M%S-%f")
    trace_dir = REPORTS_ROOT / ts
    trace_dir.mkdir(parents=True, exist_ok=True)
    suffix = "PASS" if exit_code == 0 else "STRUCTURAL" if exit_code == 2 else "FAIL"
    trace_path = trace_dir / f"check-dispatch-registry-lockstep.{suffix}.yaml"
    trace_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return trace_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check dispatch registry lockstep integrity.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    args = parser.parse_args(argv)

    exit_code, trace = run_check(args.registry)
    trace_path = _write_trace(trace, exit_code)
    print(f"dispatch-lockstep exit={exit_code} trace={trace_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
