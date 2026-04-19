"""Contract: jinja env deterministic config is pinned."""

from scripts.generators.v42.env import make_env


def test_jinja_env_pinned() -> None:
    env = make_env()
    assert env.autoescape is False
    assert env.keep_trailing_newline is True
    assert env.newline_sequence == "\n"
    assert env.trim_blocks is True
    assert env.lstrip_blocks is True
    assert env.optimized is True
    assert env.undefined.__name__ == "StrictUndefined"
