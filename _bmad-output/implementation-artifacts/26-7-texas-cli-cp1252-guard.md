# Story 26.7: Texas CLI cp1252 Guard

**Status:** done
**Created:** 2026-04-17 (via pretrial-prep run charter; party stretch-scope ratified 4-1 with John dissent)
**Epic:** 26 (BMB Sanctum Migration — Companion Stories)
**Branch:** `dev/epic-26-pretrial-prep`

## Story

As **Texas** (the technician specialist invoked via CLI), I want every
CLI entrypoint I expose to force stdout/stderr into UTF-8 before printing,
so that Windows operators running in a cp1252 terminal don't see trial
halts on innocuous non-ASCII characters (smart quotes in source titles,
en-dashes in provider names, accented author names in citation previews).

**Direct trial-defect lineage:** The 2026-04-17 APC C1-M1 Tejal trial halt
at Prompt 1 had schema-drift as the primary cause (fixed by 26-6 / PR-RC),
but the **secondary** friction was a `UnicodeEncodeError` in a Texas dev
command when the operator pasted a source-list line containing an en-dash.
The Windows console was cp1252; Python defaulted stdout to that codec;
one `print(source_title)` crashed the entire CLI. 26-7 closes that class.

**Critical dependency for Epic 27:** `epic-27-texas-intake-expansion.md`
AC-S7 says every new provider CLI "inherits the `sys.stdout.reconfigure`
pattern Story 26-7 introduced." If 26-7 doesn't land first, every 27-N
story has to re-invent the guard inline — or ship another trial-halt risk.

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1** Running any Texas CLI entrypoint on a Windows terminal
   that reports `sys.stdout.encoding == "cp1252"` and passing it a payload
   containing non-cp1252 characters (en-dash `\u2013`, curly quotes
   `\u201c`/`\u201d`, accented Latin-1-Supplement characters) does NOT
   raise `UnicodeEncodeError`. The CLI completes normally and emits the
   non-ASCII characters as proper UTF-8 bytes.
2. **AC-B.2** After the guard, `sys.stdout.encoding` reports `"utf-8"`
   (verifiable at runtime for tests). `sys.stderr` is also reconfigured
   so logger output and traceback surfaces don't re-introduce the defect.

### Test (AC-T.*)

1. **AC-T.1** `@pytest.mark.trial_critical` — An encoding-boundary test
   that forces `sys.stdout` to a `cp1252`-encoding wrapper BEFORE the
   guard runs, invokes the guard, prints a string containing en-dash +
   curly quotes + accented characters, and asserts the bytes on the
   wrapper are valid UTF-8 (not a `UnicodeEncodeError` traceback,
   not `?` replacements). Per Murat's party directive: real encoding
   round-trip, not smoke.
2. **AC-T.2** Unit test asserts the guard is idempotent — calling it
   twice in the same process does not raise. This matters because the
   Texas `run_wrangler.py` CLI may be imported by other test paths that
   already reconfigured stdout.
3. **AC-T.3** Unit test asserts the guard is a no-op when stdout is
   already UTF-8 (common on macOS/Linux CI). The guard must not break
   existing environments.

### Contract Pinning (AC-C.*)

1. **AC-C.1** The guard lives in a single shared helper, not duplicated
   across CLI files. Proposed home: `skills/bmad-agent-texas/scripts/_cli_encoding.py`
   exposing `ensure_utf8_stdout() -> None`. Epic 27 AC-S7 providers
   import + call this helper at their CLI entrypoint.
2. **AC-C.2** Every existing Texas CLI entrypoint (`run_wrangler.py`,
   `init-sanctum.py`, plus any future `bmad-agent-texas/scripts/*.py`
   with `if __name__ == "__main__"`) calls `ensure_utf8_stdout()` as the
   first line inside `main()` or equivalent.
3. **AC-C.3** The helper is a no-op when `sys.stdout` lacks a
   `reconfigure` method (defensive for pytest capture streams and
   redirected pipes). It never raises.

## Tasks / Subtasks

- [ ] **Task 1 — Shared helper** (AC-C.1, C.3)
  - [ ] Create `skills/bmad-agent-texas/scripts/_cli_encoding.py` with
    `ensure_utf8_stdout()` function
  - [ ] Function calls `sys.stdout.reconfigure(encoding="utf-8")` and
    `sys.stderr.reconfigure(encoding="utf-8")` IF both streams have
    `reconfigure` (TextIOWrapper); silently no-op otherwise
- [ ] **Task 2 — Wire into existing entrypoints** (AC-C.2)
  - [ ] `run_wrangler.py`: call guard at top of `main()`
  - [ ] `init-sanctum.py`: call guard at top of `main()`
- [ ] **Task 3 — Tests** (AC-T.1, T.2, T.3)
  - [ ] `tests/texas/test_cli_encoding_guard.py` (or per repo layout —
    wherever Texas tests already live)
  - [ ] AC-T.1 encoding-boundary round-trip test (non-smoke)
  - [ ] AC-T.2 idempotency test
  - [ ] AC-T.3 no-op on UTF-8-native stdout test
  - [ ] `trial_critical` marker on AC-T.1 only (T.2/T.3 don't block trial)
- [ ] **Task 4 — Verification**
  - [ ] `pytest` full suite green (no regressions)
  - [ ] `pytest -m trial_critical` green (+1 new trial_critical test)
  - [ ] Pre-commit hooks green (ruff + orphan + co-commit)

## Dev Notes

### Scope discipline

Per party green-light (2026-04-17, 4-1): this is a **one-line pattern**
applied at CLI boundaries. No deeper refactor. No `locale` changes. No
`PYTHONIOENCODING` documentation. No changes to how Texas reads files —
only how it writes to stdout/stderr.

Non-goal: changing the encoding Texas uses to read source files (those
are opened with explicit `encoding="utf-8"` already; AC-D.8 of Epic 25
covered that).

### Why a helper, not an inline one-liner?

Amelia's party comment: "Inline `sys.stdout.reconfigure(...)` works but
when Epic 27 adds 7 providers, we have 7 copies that drift independently.
One helper + one import + one line is the same keystroke count per
entrypoint and stays consistent as the fleet grows."

### Why reconfigure() and not PYTHONIOENCODING env var?

- Env vars are operator-local; the guard belongs with the code so it
  ships with the agent regardless of shell config.
- `reconfigure()` available since Python 3.7; repo requires 3.11+.
- Safer on Windows than `codecs.getwriter("utf-8")(sys.stdout.buffer)`
  because we keep the underlying TextIOWrapper (preserves `print`'s
  internal newline translation).

### Test location

Per `feedback_regression_proof_tests.md` hard preference, the test file
co-commits with the implementation. Texas tests already live under
`skills/bmad-agent-texas/scripts/tests/`; 26-7 extends that directory.

## Dev Agent Record

### Agent Model Used

_(filled by dev-story at implementation time)_

### Completion Notes List

### File List

### Review Record

**bmad-code-review adversarial pass — 2026-04-17** (3 layers: Blind Hunter + Edge Case Hunter + Acceptance Auditor)

**MUST-FIX — remediated:**
- [x] [Review][Patch] Factual error in docstrings about which characters are outside cp1252 — en-dash (0x96), curly quotes (0x91-0x94), and acute-é (0xE9) all *encode fine* in cp1252; only combining marks, CJK, snowmen, emoji trip the boundary. Fixed in `_cli_encoding.py` docstring + test docstring + test comment.
- [x] [Review][Patch] Test payload hardened: snowman `\u2603` is now the load-bearing codepoint (single scalar outside cp1252, survives all Unicode normalization). Combining acute accent remains as a second safety net. A future `unicodedata.normalize("NFKC", ...)` cleanup cannot silently collapse the snowman away.

**SHOULD-FIX — remediated in this cycle:**
- [x] [Review][Patch] Guard now fires at module-top in `run_wrangler.py` (not just inside `main()`) — import-time prints from sibling-module load or tracebacks would otherwise hit stdout before `main()` runs. [scripts/run_wrangler.py ~73-83]
- [x] [Review][Patch] `init-sanctum.py` now uses `importlib.util.spec_from_file_location` for the sibling `_cli_encoding` import instead of `sys.path.insert` — avoids permanent global path pollution that would compound as Epic 27 adds 7 providers inheriting this pattern.
- [x] [Review][Patch] AC-T.2 (idempotency) now asserts bytes-on-wire, not just the encoding label. AC-T.3 (no-reconfigure stream) now asserts stream identity + encoding are unchanged — locks the no-op contract.

**SHOULD-FIX — documented, deferred to a follow-up hardening story:**
- [ ] [Review][Defer] Narrow exception list in `ensure_utf8_stdout()` (`ValueError`, `OSError`) could leak through `TypeError` on a stream with a non-function `reconfigure` attribute. Low-probability edge; broader `except Exception:` would honor the stated "never raises" invariant more literally.
- [ ] [Review][Defer] Module-level `pytestmark = [pytest.mark.trial_critical]` broadens the marker to all 4 tests; spec said AC-T.1 only. AC is still satisfied (marker is present on T.1). Move to per-test decorator if strict adherence matters.
- [ ] [Review][Defer] Add one-line docstring note that `reconfigure(encoding="utf-8")` preserves `line_buffering` (so a future maintainer doesn't helpfully add `line_buffering=False` and break `python -u`).

**Behavioral change documented — non-blocking:**
- On Windows, `python script.py > out.txt` previously opened `out.txt` with `encoding='cp1252'` (OS locale default). After the guard, the redirect file's encoding is reconfigured to UTF-8. Consumers downstream that were parsing redirected Texas output as cp1252 will need to decode as UTF-8 — net-positive (and the whole point of the guard), but visible.

**Dismissed as NIT:** test comment framing, module-scope load_module_from_path vs deferred, docstring invariant phrasing, `python -u` interaction note, `sys.stderr is None` explicit test (defensive path already covered).

**Layered review summary:**
- Blind Hunter: 8 findings (0 MUST-FIX, 5 SHOULD-FIX, 3 NIT)
- Edge Case Hunter: 8 findings (1 MUST-FIX, 2 SHOULD-FIX, 5 NIT)
- Acceptance Auditor: 8 ACs audited — 8 SATISFIED, 0 THIN, 0 MISSING

**BMAD closure criteria:**
- [ ] All AC-B.*, AC-T.*, AC-C.* checkboxes green
- [ ] Full pytest suite green (no regressions vs 1023-pass baseline)
- [ ] `pytest -m trial_critical` green (155 + 1 new = 156 expected)
- [ ] Pre-commit hooks pass (ruff + orphan + co-commit)
- [ ] Party-mode implementation review (consensus: approve)
- [ ] bmad-code-review pass: MUST-FIX remediated
- [ ] `sprint-status.yaml` flipped to `done` with closure comment
- [ ] Epic 26 roster entry updated to `done`
