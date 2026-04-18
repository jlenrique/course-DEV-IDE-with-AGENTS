"""CLI encoding guard shared across Texas CLI entrypoints.

Prevents ``UnicodeEncodeError`` when a Windows operator runs a Texas CLI
in a ``cp1252`` terminal and the payload contains any codepoint outside
cp1252's 256-entry repertoire — combining diacritics, CJK characters,
emoji, mathematical symbols, and so on.

Note: cp1252 *does* cover en-dashes (0x96), curly quotes (0x91-0x94),
and the acute-accent é (0xE9) — those common "looks non-ASCII" marks
encode fine. The real boundary-trippers are codepoints outside
Windows-1252 altogether: combining marks (U+0300-U+036F), snowmen
(U+2603), anything CJK, most emoji.

One helper, one import, one call per entrypoint — no 7× drift when
Epic 27 adds 7 providers inheriting this pattern (AC-S7).

See story ``_bmad-output/implementation-artifacts/26-7-texas-cli-cp1252-guard.md``.
"""

from __future__ import annotations

import sys


def ensure_utf8_stdout() -> None:
    """Force stdout/stderr to UTF-8 at CLI startup.

    - Calls ``reconfigure(encoding="utf-8")`` on both streams when they
      expose it (standard ``TextIOWrapper`` as seen on a live console).
    - Silently no-op when ``reconfigure`` is unavailable (pytest capture
      streams, redirected pipes, already-replaced wrappers). The guard
      must never raise — failure here would break every CLI we attach
      it to.
    - Idempotent: calling twice in the same process is safe; the second
      call sees UTF-8 already and does nothing meaningful.

    Invariant Epic 27 AC-S7 depends on: after this returns,
    ``sys.stdout.encoding.lower()`` is ``"utf-8"`` on any terminal where
    ``reconfigure`` is available, regardless of the OS codepage.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except (ValueError, OSError):
            # Stream was opened in a mode that forbids reconfiguration
            # (e.g., already closed, detached). Nothing to do — defensive
            # no-op per the "never raises" contract above.
            continue
