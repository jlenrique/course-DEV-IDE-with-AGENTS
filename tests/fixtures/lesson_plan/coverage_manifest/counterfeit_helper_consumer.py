"""Fixture: same-name helper without canonical import path must be rejected."""


def assert_plan_fresh(surface) -> None:
    return None


def consume(surface) -> str:
    assert_plan_fresh(surface)
    return "consumed"
