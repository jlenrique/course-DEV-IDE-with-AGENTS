from uuid import UUID


def create_event(*, run_id: UUID, gate: str, event_type: str):
    return {"run_id": str(run_id), "gate": gate, "event_type": event_type}


def record() -> None:
    create_event(run_id=UUID(int=1), gate="G2", event_type="approval")
    create_event(run_id=UUID(int=2), gate="G3", event_type="revision")
    create_event(run_id=UUID(int=3), gate="G5", event_type="waiver")
