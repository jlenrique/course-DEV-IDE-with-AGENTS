from typing import Literal


def create_event(run_id: str, gate: str, event_type: str) -> dict[str, str]:
    return {"run_id": run_id, "gate": gate, "event_type": event_type}


def validate_event(event: dict[str, str]) -> bool:
    event_type: Literal["approval", "revision", "waiver"] = event["event_type"]  # noqa: F841
    return True
