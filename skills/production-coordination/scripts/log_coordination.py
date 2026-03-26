# /// script
# requires-python = ">=3.10"
# ///
"""Log and query agent coordination events.

Records delegation events in the agent_coordination table for
production run tracking and pattern analysis.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
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


def get_db_path(root: Path | None = None) -> Path:
    """Return the coordination database path."""
    root = root or find_project_root()
    return root / "state" / "runtime" / "coordination.db"


def connect_db(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a connection to the coordination database."""
    path = Path(db_path) if db_path else get_db_path()
    if not path.exists():
        print(json.dumps({"error": f"Database not found: {path}"}), file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def cmd_log(args: argparse.Namespace) -> dict[str, Any]:
    """Record a coordination event."""
    conn = connect_db(args.db)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    conn.execute(
        """INSERT INTO agent_coordination (run_id, agent_name, action, payload_json, timestamp)
           VALUES (?, ?, ?, ?, ?)""",
        (args.run_id, args.agent, args.action, args.payload, now),
    )
    conn.commit()
    event_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()

    return {
        "event_id": event_id,
        "run_id": args.run_id,
        "agent": args.agent,
        "action": args.action,
        "timestamp": now,
    }


def cmd_history(args: argparse.Namespace) -> dict[str, Any]:
    """Query coordination events for a run."""
    conn = connect_db(args.db)
    rows = conn.execute(
        """SELECT event_id, run_id, agent_name, action, payload_json, timestamp
           FROM agent_coordination WHERE run_id = ? ORDER BY timestamp ASC""",
        (args.run_id,),
    ).fetchall()
    conn.close()

    events = []
    for r in rows:
        event: dict[str, Any] = {
            "event_id": r["event_id"],
            "agent": r["agent_name"],
            "action": r["action"],
            "timestamp": r["timestamp"],
        }
        if r["payload_json"]:
            try:
                event["payload"] = json.loads(r["payload_json"])
            except (json.JSONDecodeError, TypeError):
                event["payload_raw"] = r["payload_json"]
        events.append(event)

    return {"run_id": args.run_id, "events": events, "count": len(events)}


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(description="Agent coordination event logging")
    parser.add_argument("--db", help="Override database path")
    sub = parser.add_subparsers(dest="command", required=True)

    p_log = sub.add_parser("log", help="Record a coordination event")
    p_log.add_argument("--run-id", required=True, help="Production run ID")
    p_log.add_argument("--agent", required=True, help="Agent name")
    p_log.add_argument("--action", required=True, help="Action type (delegated, completed, failed)")
    p_log.add_argument("--payload", help="JSON payload")

    p_history = sub.add_parser("history", help="Query events for a run")
    p_history.add_argument("run_id", help="Production run ID")

    return parser


COMMANDS = {"log": cmd_log, "history": cmd_history}


def main(argv: list[str] | None = None) -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    result = COMMANDS[args.command](args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
