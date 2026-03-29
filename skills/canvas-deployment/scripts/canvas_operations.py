# /// script
# requires-python = ">=3.10"
# ///
"""Canvas deployment orchestration for the Deployment Director.

This script validates deployment manifests, enforces accessibility pre-checks,
executes Canvas API operations through the shared CanvasClient, verifies module
structure, and returns confirmation URLs for human checkpoint review.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

from scripts.api_clients import APIError, AuthenticationError, CanvasClient

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STYLE_GUIDE_PATH = PROJECT_ROOT / "state" / "config" / "style_guide.yaml"


class DeploymentError(Exception):
    """Raised when manifest validation or deploy orchestration cannot proceed."""


def _load_module(module_name: str, file_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Unable to load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_accessibility_checker() -> ModuleType:
    checker_path = (
        PROJECT_ROOT
        / "skills"
        / "quality-control"
        / "scripts"
        / "accessibility_checker.py"
    )
    if not checker_path.exists():
        raise FileNotFoundError(f"Accessibility checker not found: {checker_path}")
    return _load_module("skills.quality_control.scripts.accessibility_checker", checker_path)


def _load_style_defaults() -> dict[str, Any]:
    if not STYLE_GUIDE_PATH.exists():
        return {}
    raw = yaml.safe_load(STYLE_GUIDE_PATH.read_text(encoding="utf-8")) or {}
    return raw.get("tool_parameters", {}).get("canvas", {})


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_manifest(manifest_path: Path | str) -> dict[str, Any]:
    path = Path(manifest_path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _expect_list(value: Any, field_name: str) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise DeploymentError(f"{field_name} must be a list")
    for entry in value:
        if not isinstance(entry, dict):
            raise DeploymentError(f"{field_name} entries must be objects")
    return value


def validate_manifest(manifest: dict[str, Any]) -> None:
    modules = manifest.get("modules")
    if not isinstance(modules, list) or not modules:
        raise DeploymentError("Manifest requires a non-empty 'modules' list")

    module_names = [str(module.get("name", "")).strip() for module in modules]
    duplicates = sorted(
        {
            name for name in module_names if name and module_names.count(name) > 1
        }
    )
    if duplicates:
        raise DeploymentError(
            f"Manifest contains duplicate module names: {duplicates}"
        )

    for index, module in enumerate(modules, start=1):
        if not isinstance(module, dict):
            raise DeploymentError(f"Module {index} must be an object")
        if not str(module.get("name", "")).strip():
            raise DeploymentError(f"Module {index} requires a non-empty 'name'")

        pages = _expect_list(module.get("pages"), f"modules[{index}].pages")
        for page_idx, page in enumerate(pages, start=1):
            if not str(page.get("title", "")).strip():
                raise DeploymentError(
                    f"modules[{index}].pages[{page_idx}] requires 'title'"
                )
            if not str(page.get("body", "")).strip():
                raise DeploymentError(
                    f"modules[{index}].pages[{page_idx}] requires 'body'"
                )

        assignments = _expect_list(
            module.get("assignments"), f"modules[{index}].assignments"
        )
        for assignment_idx, assignment in enumerate(assignments, start=1):
            if not str(assignment.get("name", "")).strip():
                raise DeploymentError(
                    f"modules[{index}].assignments[{assignment_idx}] "
                    "requires 'name'"
                )

        discussions = _expect_list(
            module.get("discussions"), f"modules[{index}].discussions"
        )
        for discussion_idx, discussion in enumerate(discussions, start=1):
            if not str(discussion.get("title", "")).strip():
                raise DeploymentError(
                    f"modules[{index}].discussions[{discussion_idx}] "
                    "requires 'title'"
                )
            if not str(discussion.get("message", "")).strip():
                raise DeploymentError(
                    f"modules[{index}].discussions[{discussion_idx}] "
                    "requires 'message'"
                )


def run_accessibility_precheck(
    manifest: dict[str, Any],
    target_grade: float = 12.0,
) -> dict[str, Any]:
    try:
        checker = _load_accessibility_checker()
    except (FileNotFoundError, ImportError) as exc:
        return {
            "status": "fail",
            "summary": {"total": 1, "critical": 1, "high": 0, "medium": 0, "low": 0},
            "findings": [
                {
                    "severity": "critical",
                    "location": "accessibility-checker",
                    "description": str(exc),
                    "fix_suggestion": "Restore accessibility checker before deployment",
                }
            ],
            "checks": [],
        }

    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    for module_idx, module in enumerate(manifest.get("modules", []), start=1):
        for page_idx, page in enumerate(module.get("pages", []), start=1):
            result = checker.run_accessibility_check(
                str(page.get("body", "")), target_grade=target_grade
            )
            result["artifact"] = f"modules[{module_idx}].pages[{page_idx}]"
            checks.append(result)
            for finding in result.get("findings", []):
                finding_copy = dict(finding)
                finding_copy["artifact"] = result["artifact"]
                findings.append(finding_copy)

        for assign_idx, assignment in enumerate(module.get("assignments", []), start=1):
            text = str(assignment.get("description", "")).strip()
            if not text:
                continue
            result = checker.run_accessibility_check(text, target_grade=target_grade)
            result["artifact"] = f"modules[{module_idx}].assignments[{assign_idx}]"
            checks.append(result)
            for finding in result.get("findings", []):
                finding_copy = dict(finding)
                finding_copy["artifact"] = result["artifact"]
                findings.append(finding_copy)

        for disc_idx, discussion in enumerate(module.get("discussions", []), start=1):
            result = checker.run_accessibility_check(
                str(discussion.get("message", "")), target_grade=target_grade
            )
            result["artifact"] = f"modules[{module_idx}].discussions[{disc_idx}]"
            checks.append(result)
            for finding in result.get("findings", []):
                finding_copy = dict(finding)
                finding_copy["artifact"] = result["artifact"]
                findings.append(finding_copy)

    summary = {
        "total": len(findings),
        "critical": sum(1 for f in findings if f.get("severity") == "critical"),
        "high": sum(1 for f in findings if f.get("severity") == "high"),
        "medium": sum(1 for f in findings if f.get("severity") == "medium"),
        "low": sum(1 for f in findings if f.get("severity") == "low"),
    }
    status = "pass" if summary["critical"] == 0 else "fail"

    return {
        "status": status,
        "summary": summary,
        "findings": findings,
        "checks": checks,
    }


def _scope_check_result() -> dict[str, Any]:
    required_raw = os.environ.get("CANVAS_REQUIRED_SCOPES", "")
    granted_raw = os.environ.get("CANVAS_TOKEN_SCOPES", "")
    required = {s.strip() for s in required_raw.split(",") if s.strip()}
    granted = {s.strip() for s in granted_raw.split(",") if s.strip()}

    if not required:
        return {
            "status": "pass",
            "reason": "No required scope list configured",
            "required": [],
            "granted": sorted(granted),
        }

    if not granted:
        return {
            "status": "warning",
            "reason": "Required scopes configured but granted scope list is unavailable",
            "required": sorted(required),
            "granted": [],
        }

    missing = sorted(required - granted)
    if missing:
        return {
            "status": "fail",
            "reason": "Missing required Canvas token scopes",
            "required": sorted(required),
            "granted": sorted(granted),
            "missing": missing,
        }

    return {
        "status": "pass",
        "reason": "Granted scopes satisfy required scope set",
        "required": sorted(required),
        "granted": sorted(granted),
    }


def _resolve_course_id(
    manifest: dict[str, Any],
    client: CanvasClient,
    style_defaults: dict[str, Any],
) -> int | str:
    from_manifest = manifest.get("course_id")
    if from_manifest not in (None, ""):
        return from_manifest

    from_style = style_defaults.get("default_course_id")
    if from_style not in (None, ""):
        return from_style

    courses = list(client.list_courses())
    if not courses:
        raise DeploymentError(
            "No Canvas course_id provided and no accessible courses were found"
        )
    return courses[0]["id"]


def _resolve_publish_flag(
    entry: dict[str, Any],
    style_defaults: dict[str, Any],
) -> bool:
    if "published" in entry:
        return bool(entry.get("published"))
    return bool(style_defaults.get("publish_immediately", False))


def _module_position(
    module: dict[str, Any],
    style_defaults: dict[str, Any],
) -> int | None:
    if module.get("position") not in (None, ""):
        return int(module["position"])

    configured = style_defaults.get("default_module_position")
    if isinstance(configured, int):
        return configured
    if isinstance(configured, str) and configured.isdigit():
        return int(configured)
    return None


def _post_module_item(
    client: CanvasClient,
    course_id: int | str,
    module_id: int | str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return client.post(
        f"/courses/{course_id}/modules/{module_id}/items",
        data=payload,
    )


def _canvas_web_root(client: CanvasClient) -> str:
    return client.base_url.split("/api/v1")[0].rstrip("/")


def _confirmation_urls(
    client: CanvasClient,
    course_id: int | str,
    module_ids: list[int | str],
) -> dict[str, Any]:
    root = _canvas_web_root(client)
    return {
        "course": f"{root}/courses/{course_id}",
        "modules": [
            f"{root}/courses/{course_id}/modules/{module_id}" for module_id in module_ids
        ],
    }


def verify_module_structure(
    client: CanvasClient,
    course_id: int | str,
    expected_module_names: list[str],
) -> dict[str, Any]:
    actual_modules = list(client.list_modules(course_id))
    actual_names = [str(module.get("name", "")).strip() for module in actual_modules]

    missing = [name for name in expected_module_names if name not in actual_names]
    in_order = True
    filtered_actual = [name for name in actual_names if name in expected_module_names]
    if filtered_actual[: len(expected_module_names)] != expected_module_names:
        in_order = False

    status = "pass" if not missing and in_order else "fail"
    return {
        "status": status,
        "expected_modules": expected_module_names,
        "actual_modules": actual_names,
        "missing_modules": missing,
        "in_order": in_order,
    }


def _rollback_created(
    client: CanvasClient,
    course_id: int | str,
    created: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    attempted = 0
    failures: list[dict[str, str]] = []

    def _delete(endpoint: str) -> None:
        nonlocal attempted
        attempted += 1
        try:
            client.delete(endpoint)
        except Exception as exc:  # pragma: no cover - defensive fallback
            failures.append({"endpoint": endpoint, "error": str(exc)})

    for item in reversed(created["module_items"]):
        _delete(f"/courses/{course_id}/modules/{item['module_id']}/items/{item['id']}")

    for discussion in reversed(created["discussions"]):
        _delete(f"/courses/{course_id}/discussion_topics/{discussion['id']}")

    for assignment in reversed(created["assignments"]):
        _delete(f"/courses/{course_id}/assignments/{assignment['id']}")

    for page in reversed(created["pages"]):
        page_ref = page.get("url") or page.get("id")
        _delete(f"/courses/{course_id}/pages/{page_ref}")

    for module in reversed(created["modules"]):
        _delete(f"/courses/{course_id}/modules/{module['id']}")

    return {
        "attempted": attempted,
        "failed": len(failures),
        "failures": failures,
        "status": "ok" if not failures else "partial",
    }


def deploy_manifest(
    manifest: dict[str, Any],
    *,
    dry_run: bool = False,
    target_grade: float = 12.0,
) -> dict[str, Any]:
    validate_manifest(manifest)

    style_defaults = _load_style_defaults()
    accessibility = run_accessibility_precheck(manifest, target_grade=target_grade)
    if accessibility["status"] != "pass":
        return {
            "status": "blocked",
            "reason": "Accessibility pre-check failed",
            "accessibility": accessibility,
            "created": {},
            "warnings": [],
            "errors": [],
            "timestamp": _now_iso(),
        }

    scope_check = _scope_check_result()
    if scope_check["status"] == "fail":
        return {
            "status": "blocked",
            "reason": scope_check["reason"],
            "scope_check": scope_check,
            "accessibility": accessibility,
            "created": {},
            "warnings": [],
            "errors": [],
            "timestamp": _now_iso(),
        }

    warnings: list[str] = []
    if scope_check["status"] == "warning":
        warnings.append(scope_check["reason"])

    client = CanvasClient()
    try:
        auth_check = client.get_self()
    except AuthenticationError as exc:
        return {
            "status": "failed",
            "reason": "Canvas authentication failed",
            "errors": [str(exc)],
            "warnings": warnings,
            "timestamp": _now_iso(),
        }

    course_id = _resolve_course_id(manifest, client, style_defaults)
    expected_module_names = [str(module["name"]).strip() for module in manifest.get("modules", [])]

    if dry_run:
        return {
            "status": "dry-run",
            "course_id": course_id,
            "actor": auth_check.get("name") or auth_check.get("id"),
            "accessibility": accessibility,
            "scope_check": scope_check,
            "planned_modules": expected_module_names,
            "module_structure_verification": {
                "status": "dry-run",
                "expected_modules": expected_module_names,
            },
            "confirmation_urls": _confirmation_urls(client, course_id, []),
            "created": {
                "modules": [],
                "pages": [],
                "assignments": [],
                "discussions": [],
                "module_items": [],
            },
            "warnings": warnings,
            "errors": [],
            "timestamp": _now_iso(),
        }

    created: dict[str, list[dict[str, Any]]] = {
        "modules": [],
        "pages": [],
        "assignments": [],
        "discussions": [],
        "module_items": [],
    }

    try:
        for module in manifest.get("modules", []):
            module_resp = client.create_module(
                course_id,
                str(module["name"]).strip(),
                position=_module_position(module, style_defaults),
                require_sequential_progress=bool(
                    module.get("require_sequential_progress", False)
                ),
            )
            module_id = module_resp["id"]
            created["modules"].append({"id": module_id, "name": module_resp.get("name")})

            for page in module.get("pages", []):
                page_resp = client.create_page(
                    course_id,
                    title=str(page["title"]).strip(),
                    body=str(page["body"]),
                    published=_resolve_publish_flag(page, style_defaults),
                )
                created["pages"].append(
                    {
                        "id": page_resp.get("page_id") or page_resp.get("id"),
                        "url": page_resp.get("url"),
                        "title": page_resp.get("title") or page.get("title"),
                    }
                )

                page_url = page_resp.get("url")
                if not page_url:
                    raise DeploymentError(
                        "Canvas page response missing 'url' for module "
                        "attachment"
                    )

                item = _post_module_item(
                    client,
                    course_id,
                    module_id,
                    {
                        "module_item[type]": "Page",
                        "module_item[page_url]": page_url,
                    },
                )
                created["module_items"].append(
                    {"id": item["id"], "module_id": module_id, "type": "Page"}
                )

            for assignment in module.get("assignments", []):
                assign_resp = client.create_assignment(
                    course_id,
                    name=str(assignment["name"]).strip(),
                    submission_types=assignment.get("submission_types"),
                    points_possible=assignment.get("points_possible"),
                    description=str(assignment.get("description", "")),
                    published=_resolve_publish_flag(assignment, style_defaults),
                )
                assignment_id = assign_resp["id"]
                created["assignments"].append(
                    {"id": assignment_id, "name": assign_resp.get("name")}
                )

                item = _post_module_item(
                    client,
                    course_id,
                    module_id,
                    {
                        "module_item[type]": "Assignment",
                        "module_item[content_id]": assignment_id,
                    },
                )
                created["module_items"].append(
                    {"id": item["id"], "module_id": module_id, "type": "Assignment"}
                )

            for discussion in module.get("discussions", []):
                discussion_resp = client.post(
                    f"/courses/{course_id}/discussion_topics",
                    data={
                        "title": str(discussion["title"]).strip(),
                        "message": str(discussion["message"]),
                        "published": _resolve_publish_flag(discussion, style_defaults),
                    },
                )
                discussion_id = discussion_resp["id"]
                created["discussions"].append(
                    {"id": discussion_id, "title": discussion_resp.get("title")}
                )

                item = _post_module_item(
                    client,
                    course_id,
                    module_id,
                    {
                        "module_item[type]": "Discussion",
                        "module_item[content_id]": discussion_id,
                    },
                )
                created["module_items"].append(
                    {"id": item["id"], "module_id": module_id, "type": "Discussion"}
                )

        verification = verify_module_structure(client, course_id, expected_module_names)
        module_ids = [module["id"] for module in created["modules"]]

        status = "deployed" if verification["status"] == "pass" else "warning"
        if status == "warning":
            warnings.append("Module structure verification reported gaps")

        return {
            "status": status,
            "course_id": course_id,
            "actor": auth_check.get("name") or auth_check.get("id"),
            "accessibility": accessibility,
            "scope_check": scope_check,
            "module_structure_verification": verification,
            "confirmation_urls": _confirmation_urls(client, course_id, module_ids),
            "created": created,
            "warnings": warnings,
            "errors": [],
            "timestamp": _now_iso(),
        }

    except (APIError, DeploymentError, KeyError, ValueError) as exc:
        rollback = _rollback_created(client, course_id, created)
        return {
            "status": "failed",
            "course_id": course_id,
            "reason": str(exc),
            "accessibility": accessibility,
            "scope_check": scope_check,
            "rollback": rollback,
            "created": created,
            "warnings": warnings,
            "errors": [str(exc)],
            "timestamp": _now_iso(),
        }


def deploy_manifest_file(
    manifest_path: Path | str,
    *,
    dry_run: bool = False,
    output_path: Path | str | None = None,
    target_grade: float = 12.0,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    result = deploy_manifest(manifest, dry_run=dry_run, target_grade=target_grade)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Canvas deployment operations")
    parser.add_argument("--manifest", required=True, help="Path to deployment manifest YAML")
    parser.add_argument("--dry-run", action="store_true", help="Validate and plan only")
    parser.add_argument("--output", help="Optional JSON output path")
    parser.add_argument("--target-grade", type=float, default=12.0)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    try:
        result = deploy_manifest_file(
            args.manifest,
            dry_run=args.dry_run,
            output_path=args.output,
            target_grade=args.target_grade,
        )
    except (FileNotFoundError, DeploymentError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}))
        sys.exit(2)

    print(json.dumps(result, indent=2))
    if result.get("status") in {"failed", "blocked"}:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
