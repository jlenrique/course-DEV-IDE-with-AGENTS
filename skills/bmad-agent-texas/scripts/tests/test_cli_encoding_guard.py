"""Encoding-boundary tests for the Texas CLI cp1252 guard (Story 26-7).

Direct regression coverage for the 2026-04-17 APC C1-M1 trial secondary
friction: a Windows operator's cp1252 terminal raised ``UnicodeEncodeError``
when a Texas dev command printed a source title containing characters
outside Windows-1252. The guard ``ensure_utf8_stdout()`` at CLI
entrypoints prevents that class.

Payload choice matters: en-dashes, curly quotes, and the acute-é all
*encode fine* in cp1252 (they live at 0x96, 0x91-0x94, 0xE9). The real
trippers are codepoints outside Windows-1252: combining marks, CJK,
snowmen, emoji. The test payload uses a snowman (U+2603) plus a
combining acute accent (U+0301) — the snowman is the load-bearing
codepoint (it is not in cp1252 AND cannot be collapsed by Unicode
normalization); the combining mark is a second safety net.

Per Murat's party directive: real encoding round-trip, not smoke. Test
simulates the cp1252 terminal by wrapping a ``BytesIO`` in a
``TextIOWrapper(encoding="cp1252")``, runs the guard, prints
outside-cp1252 characters, and asserts the on-the-wire bytes decode
cleanly as UTF-8.
"""

from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path

import pytest

pytestmark = [pytest.mark.trial_critical]

_THIS_DIR = Path(__file__).resolve().parent
_HELPER_PATH = _THIS_DIR.parent / "_cli_encoding.py"


def _load_helper():
    spec = importlib.util.spec_from_file_location(
        "texas_cli_encoding_under_test", _HELPER_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["texas_cli_encoding_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


_cli_encoding = _load_helper()


# ---------------------------------------------------------------------------
# AC-T.1: real encoding round-trip on a simulated cp1252 terminal
# ---------------------------------------------------------------------------


# Payload designed to trip a cp1252 stream even under Unicode normalization.
# The snowman (U+2603) is the load-bearing codepoint: it is outside cp1252
# AND is a single scalar value that no NFC/NFKC pass can collapse into a
# cp1252-representable form. The combining acute accent (U+0301) is a
# second safety net. En-dash and curly quotes are added for realistic
# "source title" flavor — they actually encode fine in cp1252 (0x96 / 0x91-0x94).
_NON_CP1252_PAYLOAD = (
    "PDF\u2013title with \u201csmart quotes\u201d and caf\u00e9\u0301 \u2603"
)


def test_guard_prevents_unicode_encode_error_on_cp1252_stream(monkeypatch):
    """AC-T.1: real encoding-boundary round-trip — not a smoke test.

    Simulate a Windows cp1252 terminal by replacing sys.stdout with a
    TextIOWrapper wrapping a BytesIO, encoding=cp1252. Without the guard,
    printing `_NON_CP1252_PAYLOAD` raises UnicodeEncodeError. After the
    guard runs, reconfigure() switches encoding to utf-8 and print
    succeeds — the bytes on the wire are valid UTF-8.
    """
    # Arrange: hostile cp1252 stdout stream.
    captured_buffer = io.BytesIO()
    hostile_stream = io.TextIOWrapper(
        captured_buffer, encoding="cp1252", write_through=True
    )
    monkeypatch.setattr(sys, "stdout", hostile_stream)
    monkeypatch.setattr(sys, "stderr", hostile_stream)

    # Sanity: without the guard, this would raise on print.
    assert sys.stdout.encoding.lower() == "cp1252"

    # Act: run the guard, then emit non-cp1252 bytes.
    _cli_encoding.ensure_utf8_stdout()
    assert sys.stdout.encoding.lower() == "utf-8", (
        "Guard did not flip stdout encoding to utf-8."
    )
    print(_NON_CP1252_PAYLOAD)
    sys.stdout.flush()

    # Assert: bytes on the wire round-trip cleanly as UTF-8 (no
    # UnicodeEncodeError, no `?` replacements).
    on_wire = captured_buffer.getvalue()
    decoded = on_wire.decode("utf-8")
    assert _NON_CP1252_PAYLOAD in decoded, (
        "Expected payload missing from utf-8-decoded output; "
        f"got: {decoded!r}"
    )
    assert "?" not in decoded.replace(_NON_CP1252_PAYLOAD, ""), (
        "cp1252 substitution character leaked through the guard."
    )


# ---------------------------------------------------------------------------
# AC-T.2: idempotency — calling guard twice must not raise
# ---------------------------------------------------------------------------


def test_guard_is_idempotent(monkeypatch):
    """AC-T.2: calling the guard twice in the same process is a no-op
    on the second call. Real risk: run_wrangler's main() is imported by
    test paths that may already have reconfigured stdout.

    Hardening per code review: we don't just check ``sys.stdout.encoding``
    (a broken guard could swap stdout for a UTF-8-labeled stream that
    drops bytes). We also print the hostile payload and decode the
    underlying buffer to prove bytes actually land."""
    captured_buffer = io.BytesIO()
    hostile_stream = io.TextIOWrapper(
        captured_buffer, encoding="cp1252", write_through=True
    )
    monkeypatch.setattr(sys, "stdout", hostile_stream)
    monkeypatch.setattr(sys, "stderr", hostile_stream)

    _cli_encoding.ensure_utf8_stdout()
    # Second call must not raise.
    _cli_encoding.ensure_utf8_stdout()
    assert sys.stdout.encoding.lower() == "utf-8"

    # Bytes-on-wire contract: the stream must still carry the payload
    # through as valid UTF-8 after two calls.
    print(_NON_CP1252_PAYLOAD)
    sys.stdout.flush()
    assert _NON_CP1252_PAYLOAD in captured_buffer.getvalue().decode("utf-8")


# ---------------------------------------------------------------------------
# AC-T.3: no-op when stdout is already UTF-8 (macOS/Linux CI common case)
# ---------------------------------------------------------------------------


def test_guard_is_noop_when_stdout_already_utf8(monkeypatch):
    """AC-T.3: the guard must not break environments where stdout is
    already UTF-8. Call-and-assert: encoding stays utf-8, no exception."""
    captured_buffer = io.BytesIO()
    friendly_stream = io.TextIOWrapper(captured_buffer, encoding="utf-8")
    monkeypatch.setattr(sys, "stdout", friendly_stream)
    monkeypatch.setattr(sys, "stderr", friendly_stream)

    _cli_encoding.ensure_utf8_stdout()
    assert sys.stdout.encoding.lower() == "utf-8"

    # Prove the stream still works post-guard.
    print(_NON_CP1252_PAYLOAD)
    sys.stdout.flush()
    on_wire = captured_buffer.getvalue()
    assert _NON_CP1252_PAYLOAD in on_wire.decode("utf-8")


def test_guard_silently_skips_streams_without_reconfigure(monkeypatch):
    """Defensive: pytest capture streams and redirected pipes may lack
    ``reconfigure``. The guard MUST NOT raise on those — it is a no-op.

    Hardening per code review: assert that the stream encoding label is
    unchanged (not silently swapped for something else)."""

    class _NoReconfigureStream:
        """A stub that looks like a stream but has no reconfigure method."""

        encoding = "ascii"

        def write(self, _s):  # pragma: no cover — not exercised in this test
            pass

        def flush(self):  # pragma: no cover
            pass

    stdout_stub = _NoReconfigureStream()
    stderr_stub = _NoReconfigureStream()
    monkeypatch.setattr(sys, "stdout", stdout_stub)
    monkeypatch.setattr(sys, "stderr", stderr_stub)

    # Must not raise.
    _cli_encoding.ensure_utf8_stdout()

    # No-op contract: stubs are untouched. A broken guard that swapped
    # streams for something else would fail this.
    assert sys.stdout is stdout_stub
    assert sys.stderr is stderr_stub
    assert sys.stdout.encoding == "ascii"
