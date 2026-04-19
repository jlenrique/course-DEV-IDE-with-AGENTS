"""Contract check for 15-1-lite meta-test evidence completeness."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORY_PATH = ROOT / "_bmad-output" / "implementation-artifacts" / "15-1-lite-marcus.md"


def test_dev_agent_record_contains_meta_test_pass() -> None:
    text = STORY_PATH.read_text(encoding="utf-8")
    section_match = re.search(
        r"### META-TEST PASS Record\s+```yaml(.*?)```",
        text,
        flags=re.DOTALL,
    )
    assert section_match is not None
    section = section_match.group(1)

    trace_path = re.search(r"l1_trace_path:\s*(.+)", section)
    timestamp = re.search(r"timestamp:\s*(.+)", section)
    operator_message = re.search(r"operator_message:\s*(.+)", section)

    assert trace_path is not None
    assert "reports/dev-coherence/" in trace_path.group(1)
    assert timestamp is not None
    assert ("+" in timestamp.group(1)) or timestamp.group(1).endswith("Z")
    assert operator_message is not None
    assert operator_message.group(1).strip()
