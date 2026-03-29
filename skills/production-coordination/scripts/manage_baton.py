# /// script
# requires-python = ">=3.10"
# ///
"""Run baton lifecycle management.

Provides a lightweight JSON runtime contract for production run authority.
"""
from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

REDIRECT_MESSAGE_TEMPLATE = (
    "Marcus is running {run_id}, currently at {gate}. "
    "Redirect, or enter standalone consult mode?"
)

LOGGER = logging.getLogger(__name__)


def find_project_root() -> Path:
    """Walk up from script location to find the project root (contains state/)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "state").is_dir():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


def get_runtime_dir(runtime_dir: str | None = None) -> Path:
    """Return runtime directory for baton files."""
    if runtime_dir:
        return Path(runtime_dir)
    return find_project_root() / "state" / "runtime"


def _baton_path(run_id: str, runtime_dir: str | None = None) -> Path:
    """Return baton file path for a run id."""
    return get_runtime_dir(runtime_dir) / f"run_baton.{run_id}.json"


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _write_json(path: Path, data: dict[str, Any]) -> None:
    """Write JSON atomically to avoid partial files."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


def _read_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@contextmanager
def _file_lock(lock_path: Path, timeout_seconds: float = 3.0):
    """Acquire a lightweight exclusive lock using lock-file semantics."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            try:
                yield
            finally:
                os.close(fd)
                lock_path.unlink(missing_ok=True)
            return
        except FileExistsError:
            if time.monotonic() - start >= timeout_seconds:
                raise TimeoutError(f"Timed out waiting for lock: {lock_path}")
            time.sleep(0.05)


def _parse_timestamp(value: str | None) -> datetime.datetime | None:
    """Parse an ISO-like timestamp used by baton files."""
    if not value:
        return None
    try:
        return datetime.datetime.fromisoformat(value)
    except ValueError:
        return None


def _find_latest_active(runtime_dir: str | None = None) -> tuple[str, Path, dict[str, Any]] | None:
    """Return latest active baton tuple of (run_id, path, data)."""
    root = get_runtime_dir(runtime_dir)
    if not root.exists():
        return None

    latest: tuple[str, Path, dict[str, Any]] | None = None
    latest_marker: datetime.datetime | None = None

    for path in root.glob("run_baton.*.json"):
        try:
            data = _read_json(path)
        except (json.JSONDecodeError, OSError) as exc:
            LOGGER.warning("Skipping unreadable baton file '%s': %s", path, exc)
            continue

        if not data.get("active", True):
            continue

        marker = _parse_timestamp(data.get("updated_at"))
        if marker is None:
            marker = datetime.datetime.fromtimestamp(path.stat().st_mtime)

        if latest_marker is None or marker > latest_marker:
            run_id = data.get("run_id") or (
                path.name.removeprefix("run_baton.").removesuffix(".json")
            )
            latest = (str(run_id), path, data)
            latest_marker = marker

    return latest


def _list_active_batons(runtime_dir: str | None = None) -> list[tuple[str, Path, dict[str, Any]]]:
    """List all active baton files in runtime directory."""
    root = get_runtime_dir(runtime_dir)
    if not root.exists():
        return []

    active: list[tuple[str, Path, dict[str, Any]]] = []
    for path in root.glob("run_baton.*.json"):
        try:
            data = _read_json(path)
        except (json.JSONDecodeError, OSError) as exc:
            LOGGER.warning("Skipping unreadable baton file '%s': %s", path, exc)
            continue
        if not data.get("active", True):
            continue
        run_id = data.get("run_id") or path.name.removeprefix("run_baton.").removesuffix(".json")
        active.append((str(run_id), path, data))
    return active


def _resolve_baton(args: argparse.Namespace) -> tuple[str, Path, dict[str, Any]] | None:
    """Resolve baton from explicit run_id or latest active baton."""
    if args.run_id:
        path = _baton_path(args.run_id, args.runtime_dir)
        if not path.exists():
            return None
        try:
            data = _read_json(path)
        except (json.JSONDecodeError, OSError):
            return None
        if not data.get("active", True):
            return None
        return (args.run_id, path, data)
    return _find_latest_active(args.runtime_dir)


# -- Commands ---------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> dict[str, Any]:
    """Initialize (or replace) a run baton."""
    path = _baton_path(args.run_id, args.runtime_dir)
    global_lock = get_runtime_dir(args.runtime_dir) / "run_baton.global.lock"

    try:
        with _file_lock(global_lock):
            active_batons = _list_active_batons(args.runtime_dir)
            conflicting = [rid for rid, _, _ in active_batons if rid != args.run_id]

            if conflicting and not args.force:
                return {
                    "error": (
                        "Active baton already exists for another run: "
                        f"{', '.join(sorted(conflicting))}. "
                        "Close it first or re-run with --force."
                    )
                }

            if path.exists() and not args.force:
                try:
                    existing = _read_json(path)
                    if existing.get("active", True):
                        return {
                            "error": (
                                f"Active baton already exists for {args.run_id}. "
                                "Close it first or re-run with --force."
                            )
                        }
                except (json.JSONDecodeError, OSError):
                    # Corrupt baton should not block explicit re-initialization.
                    pass

            if args.force:
                for _, conflict_path, _ in active_batons:
                    if conflict_path != path:
                        conflict_path.unlink(missing_ok=True)

            allowed = sorted(set(args.allowed_delegate or []))
            now = _now()
            baton = {
                "run_id": args.run_id,
                "orchestrator": args.orchestrator,
                "current_gate": args.current_gate,
                "invocation_mode": args.invocation_mode,
                "allowed_delegates": allowed,
                "escalation_target": args.escalation_target,
                "blocking_authority": args.blocking_authority,
                "active": True,
                "created_at": now,
                "updated_at": now,
            }

            _write_json(path, baton)
    except (TimeoutError, OSError) as exc:
        return {"error": f"Failed to initialize baton: {exc}"}

    return {
        "status": "initialized",
        "run_id": args.run_id,
        "baton_file": str(path),
        "baton": baton,
    }


def cmd_get(args: argparse.Namespace) -> dict[str, Any]:
    """Get baton by run id or latest active baton."""
    resolved = _resolve_baton(args)
    if not resolved:
        return {
            "status": "not-found",
            "message": "No active baton found",
        }

    run_id, path, baton = resolved
    return {
        "status": "ok",
        "run_id": run_id,
        "baton_file": str(path),
        "baton": baton,
    }


def cmd_update_gate(args: argparse.Namespace) -> dict[str, Any]:
    """Update current gate for a baton."""
    path = _baton_path(args.run_id, args.runtime_dir)
    if not path.exists():
        return {"error": f"Baton not found for run: {args.run_id}"}

    lock_path = path.with_suffix(path.suffix + ".lock")
    try:
        with _file_lock(lock_path):
            try:
                baton = _read_json(path)
            except (json.JSONDecodeError, OSError):
                return {"error": f"Baton is unreadable for run: {args.run_id}"}

            if not baton.get("active", True):
                return {"error": f"Baton is inactive for run: {args.run_id}"}

            previous_gate = baton.get("current_gate")
            baton["current_gate"] = args.current_gate
            baton["updated_at"] = _now()
            _write_json(path, baton)
    except (TimeoutError, OSError) as exc:
        return {"error": f"Failed to update baton for run {args.run_id}: {exc}"}

    return {
        "status": "updated",
        "run_id": args.run_id,
        "previous_gate": previous_gate,
        "current_gate": args.current_gate,
    }


def cmd_check_specialist(args: argparse.Namespace) -> dict[str, Any]:
    """Evaluate specialist action against active baton authority."""
    if args.delegated_call and not args.run_id:
        return {
            "action": "redirect",
            "reason": "run_id_required_for_delegated_check",
            "specialist": args.specialist,
            "message": "Delegated specialist checks require explicit --run-id.",
            "escalation_target": "marcus",
        }

    resolved = _resolve_baton(args)
    if not resolved:
        return {
            "action": "redirect",
            "reason": "no_active_baton",
            "specialist": args.specialist,
            "message": "No active baton found. Initialize baton, or use standalone consult mode.",
            "escalation_target": "marcus",
        }

    run_id, _, baton = resolved
    gate = baton.get("current_gate", "unknown")
    baton_mode = baton.get("invocation_mode", "delegated")
    allowed = set(baton.get("allowed_delegates", []))

    redirect_message = REDIRECT_MESSAGE_TEMPLATE.format(run_id=run_id, gate=gate)

    if baton_mode == "standalone":
        return {
            "action": "proceed",
            "mode": "standalone",
            "reason": "baton_invocation_mode_standalone",
            "run_id": run_id,
            "specialist": args.specialist,
            "current_gate": gate,
        }

    if args.standalone_mode:
        return {
            "action": "proceed",
            "mode": "standalone-consult",
            "reason": "explicit_standalone_mode",
            "run_id": run_id,
            "specialist": args.specialist,
            "baton_invocation_mode": baton_mode,
            "note": "Do not mutate active production run state while in standalone consult mode.",
        }

    if args.delegated_call and args.specialist in allowed:
        return {
            "action": "proceed",
            "mode": "delegated",
            "reason": "authorized_delegate",
            "run_id": run_id,
            "specialist": args.specialist,
            "current_gate": gate,
            "baton_invocation_mode": baton_mode,
        }

    return {
        "action": "redirect",
        "reason": "active_baton_redirect",
        "run_id": run_id,
        "specialist": args.specialist,
        "current_gate": gate,
        "baton_invocation_mode": baton_mode,
        "message": redirect_message,
        "escalation_target": baton.get("escalation_target", "marcus"),
    }


def cmd_close(args: argparse.Namespace) -> dict[str, Any]:
    """Close baton by run id or latest active baton."""
    if args.run_id:
        path = _baton_path(args.run_id, args.runtime_dir)
        was_active = path.exists()
        if not was_active:
            return {
                "status": "closed",
                "run_id": args.run_id,
                "was_active": False,
                "message": "No active baton found to close",
            }
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            return {"error": f"Failed to close baton for {args.run_id}: {exc}"}

        return {
            "status": "closed",
            "run_id": args.run_id,
            "was_active": True,
            "baton_file": str(path),
        }

    resolved = _resolve_baton(args)
    if not resolved:
        return {
            "status": "not-found",
            "message": "No active baton found to close",
        }

    run_id, path, _ = resolved
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        return {"error": f"Failed to close baton for {run_id}: {exc}"}

    return {
        "status": "closed",
        "run_id": run_id,
        "baton_file": str(path),
    }


# -- CLI --------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser."""
    parser = argparse.ArgumentParser(description="Run baton lifecycle management")
    parser.add_argument("--runtime-dir", help="Override runtime directory (default: state/runtime)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize or replace a run baton")
    p_init.add_argument("run_id", help="Production run ID")
    p_init.add_argument("--orchestrator", default="marcus", help="Orchestrator identity")
    p_init.add_argument("--current-gate", default="planning", help="Current gate/stage")
    p_init.add_argument(
        "--invocation-mode",
        default="delegated",
        choices=["delegated", "standalone"],
        help="Current invocation mode",
    )
    p_init.add_argument(
        "--allowed-delegate",
        action="append",
        help="Allowed delegate identifier (repeat for multiple values)",
    )
    p_init.add_argument("--escalation-target", default="marcus", help="Escalation target")
    p_init.add_argument("--blocking-authority", default="human", help="Blocking authority")
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Allow replacing existing active baton(s)",
    )

    p_get = sub.add_parser("get", help="Get baton by run id or latest active baton")
    p_get.add_argument("--run-id", help="Production run ID")

    p_update = sub.add_parser("update-gate", help="Update current gate on an active baton")
    p_update.add_argument("run_id", help="Production run ID")
    p_update.add_argument("current_gate", help="Target gate/stage")

    p_check = sub.add_parser(
        "check-specialist",
        help="Check specialist action against baton authority",
    )
    p_check.add_argument("specialist", help="Specialist identifier")
    p_check.add_argument("--run-id", help="Production run ID (omit to use latest active baton)")
    p_check.add_argument(
        "--delegated-call",
        action="store_true",
        help="Set when call was delegated by Marcus (not direct user invocation)",
    )
    p_check.add_argument(
        "--standalone-mode",
        action="store_true",
        help="Set when user explicitly requested standalone consult mode",
    )

    p_close = sub.add_parser("close", help="Close baton by run id or latest active baton")
    p_close.add_argument("--run-id", help="Production run ID")

    return parser


COMMANDS = {
    "init": cmd_init,
    "get": cmd_get,
    "update-gate": cmd_update_gate,
    "check-specialist": cmd_check_specialist,
    "close": cmd_close,
}


def main(argv: list[str] | None = None) -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    result = COMMANDS[args.command](args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
