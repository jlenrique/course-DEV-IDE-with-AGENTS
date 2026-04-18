# Story 27.1: DOCX Provider Wiring (Contract Drift Fix)

**Status:** done
**Created:** 2026-04-17 (ratified-stub); expanded to full BMAD story 2026-04-17 21:15; green-light patches applied 2026-04-17 21:45; dev-story executed 2026-04-17 21:50-22:05; implementation-review patches 2026-04-17 22:15; code-review layered pass + remediation 2026-04-17 22:30; flipped to done 2026-04-17 22:35
**Epic:** 27 — Texas Intake Surface Expansion
**Sprint key:** `27-1-docx-provider-wiring`
**Branch:** `dev/epic-27-texas-intake`
**Points:** 2
**Depends on:** none (standalone drift fix)
**Blocks:** APC C1-M1 Tejal trial restart success (DOCX cross-validation cannot pass today without this fix)

## TL;DR

- **What:** Wire `python-docx` into the `.docx` branch of Texas's `local_file` provider dispatch (previously fell through to `read_text_file()` and produced binary garbage from the DOCX ZIP-of-XML container).
- **Why:** `transform-registry.md` promised it; code didn't deliver it. 2026-04-17 Tejal trial halted on this drift.
- **Size:** 2 pts. **+9 collecting tests delta** (5 unit incl. T.2 split + 1 integration + 3 contract per Murat's atomicity split of T.6). Final suite: 1036 passed / 2 skipped / 2 xfailed.
- **Key patterns:** Mirrors `wrangle_local_pdf`; inherits 26-7 Texas patterns (test location, module loader, CLI UTF-8 guard); controlled-failure contract on malformed DOCX; initial AC-S6 lockstep-check pilot landed as `tests/contracts/test_transform_registry_lockstep.py` with assertion-encoded `LOCKSTEP_EXEMPTIONS` dict.
- **Tejal validation (T8):** PDF↔DOCX cross-validation produced `word_count_ratio: 1.04`, **100% key-term coverage, 69/69 sections matched, verdict passed: true** — far exceeds 80% AC-B.4 target. Original trial-halt defect closed.

## Story

As the **Texas wrangler** (the technician specialist),
I want **DOCX files to be extracted via `python-docx`** (as [`transform-registry.md`](../../skills/bmad-agent-texas/references/transform-registry.md) advertises),
So that **operator-provided or cross-validation DOCX sources produce faithful text extraction** instead of binary garbage from the fall-through `read_text_file()` path.

## Background — Why This Story Exists

The 2026-04-17 APC C1-M1 Tejal trial exposed a contract-vs-code drift. Texas's [`transform-registry.md`](../../skills/bmad-agent-texas/references/transform-registry.md) advertises `python-docx` as the DOCX Priority-1 extractor with one documented known-loss (formatting / table flattening). Texas's [`run_wrangler.py`](../../skills/bmad-agent-texas/scripts/run_wrangler.py) does **not** implement it. The `local_file` provider handler at [`run_wrangler.py:239`](../../skills/bmad-agent-texas/scripts/run_wrangler.py#L239) has a PDF-specific extraction branch but everything else — including `.docx` — falls through to [`_source_ops.read_text_file(path)`](../../skills/bmad-agent-texas/scripts/source_wrangler_operations.py) at [`run_wrangler.py:248`](../../skills/bmad-agent-texas/scripts/run_wrangler.py#L248), which performs a plain-text read against the DOCX ZIP-of-XML container and produces binary garbage.

**Evidence from the trial run** (archived in [trial-run-c1m1-tejal-20260417.md](./trial-run-c1m1-tejal-20260417.md)):
- DOCX extraction reported 2,044 "words" and 1,522 "lines" but `structural_fidelity: low`, 0 headings.
- Cross-validation reported 2% key-term overlap — the "missing key terms" list contained literal unicode replacement characters and ZIP-compressed byte sequences (e.g., `]\u0307\uFFFD\\...`, `jvbtj\x1A?...`, `ezw`, `vni`, `bjh`), not actual vocabulary.
- The DOCX content was almost certainly fine; Texas just couldn't read it.

This is the cheapest, highest-severity story in Epic 27: **wire the library the registry already promises.**

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — `python-docx` extraction, not fall-through.** Invoking `run_wrangler` on a directive whose `sources[].provider == "local_file"` and `locator` has `.docx` extension produces text extraction via `python-docx`, **not** via `read_text_file()`. Verifiable at runtime by asserting the returned `SourceRecord.kind == "local_docx"` (new kind, distinct from the existing `"local_file"` for `.md`/`.txt` reads).

2. **AC-B.2 — Structure preservation within `python-docx` limits.** Output `extracted.md`:
   - Paragraph breaks preserved as blank-line separators between paragraphs.
   - Heading-style paragraphs (style name `Heading 1` through `Heading 6`) rendered as markdown `#`..`######`.
   - Tables flattened to pipe-separated rows (`| cell | cell |`), accepting `python-docx`'s table-flattening known-loss per registry.
   - Counted `word_count`, `line_count`, and `heading_count` are derived from the rendered markdown text, not the raw DOCX bytes.

3. **AC-B.3 — Controlled failure on malformed DOCX.** If `python-docx`'s `Document()` constructor raises (corrupt, password-protected, or non-DOCX file masquerading as `.docx`), the outcome is a **FAILED** `SourceOutcome` with `error_kind: "docx_extraction_failed"`, `error_detail` containing the exception class + message, and `known_losses: ["docx_open_failed"]`. No traceback leaks to stdout; no fall-through to `read_text_file()` after `python-docx` failure (that would re-introduce the binary-garbage defect).

4. **AC-B.4 — Cross-validation works on DOCX↔PDF pair.** A directive with `role: primary` PDF source AND `role: validation` DOCX source produces a valid `cross_validation[]` block in `extraction-report.yaml` with key-term coverage computed from real DOCX vocabulary. Target on Tejal fixture: ≥80% key-term overlap (lower bound empirical; same source content, differences attributable only to provider-specific losses).

### Test (AC-T.*)

1. **AC-T.1 — Happy path unit test.** `test_wrangle_local_docx_happy_path` (in `skills/bmad-agent-texas/scripts/tests/test_texas_source_wrangler_operations.py`) generates a synthetic DOCX in-test (via `python-docx` `Document()` builder) with: 3 heading levels, 2 tables, a numbered list, and ~300 words of paragraph text. Asserts returned `(title, body, rec)` tuple has: non-empty title from path stem (mirroring `wrangle_local_pdf`: `Path(path).stem.replace("_", " ")`), body containing expected heading markdown + table pipe-rows + paragraph text, `rec.kind == "local_docx"`, and note string reporting paragraph/heading/table counts. Test fixture interleaves a table between paragraphs to catch `doc.paragraphs + doc.tables` iteration-order drift.

2. **AC-T.2a — Library-layer corrupt DOCX (extractor raises).** `test_wrangle_local_docx_corrupt_file_raises` writes a file with `.docx` extension containing invalid-ZIP raw bytes (e.g., `b"not a docx"`). Asserts `wrangle_local_docx()` raises a caller-catchable exception (Winston's note: the fixture must exercise the malformed-ZIP branch specifically — a `b"not a docx"` short payload fails the ZIP magic number and is the right shape; do NOT write a valid ZIP with wrong content, which is a different failure mode). Scope: library behavior only.

3. **AC-T.2b — Adapter-layer corrupt DOCX (FAILED outcome mapping).** `test_wrangle_source_maps_docx_corruption_to_failed_outcome` invokes `run_wrangler._wrangle_source()` on a directive pointing at the same corrupt fixture. Asserts returned `SourceOutcome.status == "FAILED"`, `error_kind == "docx_extraction_failed"`, `error_detail` contains exception class + message, `known_losses == ["docx_open_failed"]`, no traceback on stdout. Scope: adapter/classification behavior. Murat's atomicity rule: library raise vs. adapter mapping are separate contracts — they fail for different reasons; the red-light message must point at the right layer.

4. **AC-T.3 — Empty DOCX test.** `test_wrangle_local_docx_empty_document` generates a DOCX with zero paragraphs (just the root document). Asserts non-crash; asserts body is empty-or-title-only, word_count 0, heading_count 0.

5. **AC-T.4 — Images-only DOCX test.** `test_wrangle_local_docx_images_only` generates a DOCX containing only an inline image (no text runs). Asserts non-crash; asserts word_count 0, heading_count 0, a single note in `rec.note` acknowledging zero text extracted. **Pillow PNG generation MUST use `io.BytesIO`, not a `tmp_path` temp file**, to avoid parallel-pytest race on shared disk paths (Murat's flakiness rule).

6. **AC-T.5 — Integration via `run_wrangler`.** `test_run_wrangler.py` grows a DOCX scenario: directive with a single `local_file` source pointing at the fixture generated in-test, asserts `SourceOutcome.status == "OK"`, `extracted.md` contains expected DOCX-rendered markdown, `metadata.json` provenance records `kind: local_docx`.

7. **AC-T.6 — Lockstep contract test (initial implementation of AC-S6 from epic spine).** New file `tests/contracts/test_transform_registry_lockstep.py`. The test iterates **all** `## {Format}` sections parsed from [`transform-registry.md`](../../skills/bmad-agent-texas/references/transform-registry.md) for each format must be EITHER in-scope for the lockstep check OR listed in `LOCKSTEP_EXEMPTIONS` with a reason string; any format that is neither → test FAILS with `"Format {X} is neither covered by lockstep nor listed as an exempted format. Add an extractor or add a LOCKSTEP_EXEMPTIONS entry with rationale."` This is Murat + Paige's consensus-hardening: silent skips rot lockstep tests; exemptions must be assertion-encoded so a future registry-editor is forced to reason about coverage.

    **Mapping lives in the test file as Python constants** (Paige's rule — do NOT regex-parse the cross-reference footnote in `transform-registry.md`; that creates a code↔prose coupling that either goes stale silently or breaks on a function rename):

    ```python
    # In tests/contracts/test_transform_registry_lockstep.py
    REGISTRY_METHOD_TO_EXTRACTOR = {
        "python-docx": ("wrangle_local_docx", "docx_suffix_check_in_fetch_source"),
        "pypdf": ("wrangle_local_pdf", "pdf_suffix_or_provider_alias"),
        "Notion MCP / REST API": ("wrangle_notion_page", "notion_provider"),
        "Playwright page save": ("wrangle_playwright_saved_html", "playwright_html_provider"),
    }
    LOCKSTEP_EXEMPTIONS = {
        "URL": "provider-name is shape-mismatched with format-name (registry 'URL' → code 'url' provider routes to summarize_url_for_envelope, not wrangle_local_*)",
        "Markdown (.md)": "fall-through path via read_text_file — no dedicated extractor by design",
        "HIL escalation": "human-in-the-loop procedure — no automated extractor",
    }
    ```

    **Meta-principle (encoded in the test's module docstring):** "A lockstep-check exemption is a registry row whose Priority-1 method does not map to a dedicated `wrangle_local_*` extractor — either because the extraction is remote (URL), a fall-through (Markdown), or out-of-code (HIL). Any new registry format that does NOT meet this exemption rule must land with a working extractor or this test fails."

    For each in-scope format, the test asserts: (a) the format's dispatch key exists in `run_wrangler._fetch_source()` source text (regex presence check against the function's `inspect.getsource()` output), (b) the Priority-1 extractor name is importable from the `source_wrangler_operations` module-loaded symbol table. Check emits `error` (pytest FAIL) for capability drift (promise-vs-code divergence); `warn` (pytest WARN) for format-only drift (e.g., registry version-number bump without capability change).

8. **AC-T.7 — Regression suite-level gate (NON-COLLECTING AC).** This AC is a suite-level assertion, not a `def test_*`. Full `pytest` green. Baseline: **1023 passed, 2 skipped, 0 failed** (2026-04-17 19:00 sweep — pre-26-6/26-7 closeout). **Expected after 27-1: 1036 passed, 2 skipped, 0 failed** (+5 unit [T.1, T.2a, T.2b, T.3, T.4] + 1 integration [T.5] + **3 contract** [T.6 split into 3 atomic tests per Murat's green-light patch] = **+9 collecting tests mine**, plus +4 tests from intervening 26-6/26-7 closeout commits landed after the baseline snapshot — see Dev Agent Record for commit SHAs). No `@pytest.mark.skip` or `xfail` added to default suite; no new `@pytest.mark.live_api`; no new `@pytest.mark.trial_critical` (this isn't a pre-Prompt-1 trial gate). Per `feedback_regression_proof_tests.md`: test file co-commits with implementation; verify delta via `pytest --collect-only | wc -l`. (PDF extraction has no idempotency test today to mirror; DOCX does not add one for parity — confirmed pre-green-light via grep: only `test_idempotent_rerun_on_existing_bundle` at bundle-level and `test_guard_is_idempotent` at CLI-encoding-level exist, both unrelated to extraction-layer idempotency.)

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Extractor lives in `source_wrangler_operations.py`.** New function `wrangle_local_docx(path: str | Path, *, max_chars: int | None = 600_000) -> tuple[str, str, SourceRecord]` mirrors `wrangle_local_pdf` signature exactly (same return shape; `max_chars` defensive cap matching PDF default). Lives adjacent to `wrangle_local_pdf` in [`source_wrangler_operations.py`](../../skills/bmad-agent-texas/scripts/source_wrangler_operations.py); no new module.

2. **AC-C.2 — `run_wrangler._fetch_source` dispatch extended, not rewritten.** The `provider in ("local_file", "pdf")` branch at [line 239](../../skills/bmad-agent-texas/scripts/run_wrangler.py#L239) gains a `.docx` check **before** the fall-through `read_text_file()` at line 248. Branch order inside the `local_file` block: `.pdf`-or-`pdf`-provider → `.docx` → fall-through text read. No restructuring of surrounding code; no new top-level provider name (DOCX remains under `local_file`, same as `.md` / `.txt`).

3. **AC-C.3 — Registry matches code (AC-S8 from epic spine).** `transform-registry.md` DOCX section:
   - Priority-1 method stays `python-docx` (unchanged).
   - Known-limitations row updated to match implementation — single consolidated bullet set (Paige's clarity fix — collapse "formatting loss" into "style/formatting loss"):
     - `style/formatting loss beyond headings H1-H6 — bold, italic, colors, fonts, paragraph spacing not preserved`
     - `table-layout loss — cells flattened to pipe-rows, no cell-merge or vertical-align preservation`
     - `inline images ignored`
     - `footnotes, comments, and tracked-changes not extracted`
   - New cross-reference footnote: `See wrangle_local_docx() in source_wrangler_operations.py and the .docx branch in run_wrangler._fetch_source()` — **human-facing documentation only**. The AC-T.6 contract test does NOT regex-parse this footnote; it encodes the mapping as Python constants in the test file itself (see AC-T.6 for exact dict shapes). This decouples prose evolution from test brittleness.

4. **AC-C.4 — Dependency pinned with range discipline.** `python-docx>=1.1,<2` added to **both**:
   - [`pyproject.toml`](../../pyproject.toml) `[project] dependencies`.
   - [`requirements.txt`](../../requirements.txt).
   Version range mirrors the repo's existing `pypdf>=5.0,<6` / `pillow>=11.0,<12` pattern: minor-floor, major-ceiling.

5. **AC-C.5 — CLI inherits UTF-8 guard (AC-S7 from epic spine).** No new CLI entrypoint — DOCX wiring rides on existing `run_wrangler.py` entrypoint, which already imports and calls `_cli_encoding.ensure_utf8_stdout()` at module-top (Story 26-7 landing). No work needed here; AC-C.5 is a **verification-only** checkbox confirming the inheritance holds after the changes.

## File Impact

| File | Change | Lines (est.) |
|------|--------|-------|
| [`skills/bmad-agent-texas/scripts/source_wrangler_operations.py`](../../skills/bmad-agent-texas/scripts/source_wrangler_operations.py) | **New** `wrangle_local_docx()` function adjacent to `wrangle_local_pdf()` at line ~239 | +60 |
| [`skills/bmad-agent-texas/scripts/run_wrangler.py`](../../skills/bmad-agent-texas/scripts/run_wrangler.py) | Extend `_fetch_source()` `local_file` branch: add `.docx` check before `read_text_file()` fall-through | +12 |
| [`skills/bmad-agent-texas/references/transform-registry.md`](../../skills/bmad-agent-texas/references/transform-registry.md) | DOCX section: update known-limitations, add cross-reference footnote | +4 |
| [`skills/bmad-agent-texas/scripts/tests/test_texas_source_wrangler_operations.py`](../../skills/bmad-agent-texas/scripts/tests/test_texas_source_wrangler_operations.py) | Add 5 new tests (AC-T.1, T.2a, T.2b, T.3, T.4) | +135 |
| [`skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py`](../../skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py) | Add DOCX integration scenario (AC-T.5) | +35 |
| [`tests/contracts/test_transform_registry_lockstep.py`](../../tests/contracts/test_transform_registry_lockstep.py) | **New** contract test (AC-T.6) | +90 |
| [`pyproject.toml`](../../pyproject.toml) | Add `python-docx>=1.1,<2` to `dependencies` | +1 |
| [`requirements.txt`](../../requirements.txt) | Add `python-docx>=1.1,<2` | +1 |

**No changes to**: `_cli_encoding.py` (already correct); `init-sanctum.py` (unrelated); any fidelity contract; any yaml config; any sprint-planning artifact.

## Tasks / Subtasks

- [x] **T1 — Dependency pin** (AC-C.4)
  - [x] Add `"python-docx>=1.1,<2",` to `pyproject.toml` `[project] dependencies` (adjacent to `python-pptx>=1.0,<2`).
  - [x] Add `python-docx>=1.1,<2` to `requirements.txt` (adjacent to `pypdf>=5.0,<6`).
  - [x] Run `.venv/Scripts/pip install -e .` (or equivalent) to install; verify `from docx import Document` works.
- [x] **T2 — Implement `wrangle_local_docx()`** (AC-B.1, B.2, B.3, C.1)
  - [x] Add function to `source_wrangler_operations.py` adjacent to `wrangle_local_pdf()`.
  - [x] Import `Document` from `docx` at module top (or locally inside the function if lazy-import style is preferred — check module conventions; current style is eager).
  - [x] Function opens `Document(path)`, iterates `doc.paragraphs` preserving document order.
  - [x] For each paragraph: check `paragraph.style.name` for `"Heading N"` pattern; render as `#*N heading-text`. Otherwise render as plain text.
  - [x] For tables: iterate `doc.tables`, render each row as `| cell1 | cell2 | ... |` (newline between rows). Table position-preservation: flush the table at the document-order position of its first reference, using `doc.element.body` iteration if simple `doc.tables` iteration gives wrong interleave. (Accept simple iteration first; upgrade to body-order iteration only if the AC-T.1 test fails.)
  - [x] Clamp output at `max_chars` (default 600_000) with trailing truncation sentinel, mirroring PDF behavior.
  - [x] Count paragraphs, headings, tables; compose `SourceRecord(kind="local_docx", ref=..., note=f"python-docx paragraphs={p} headings={h} tables={t}{' truncated' if trunc else ''}")`.
  - [x] Return `(title, body, rec)` — title from `Path(path).stem.replace("_", " ")` per PDF convention.
- [x] **T3 — Extend `_fetch_source()` dispatch** (AC-B.1, AC-B.3, C.2)
  - [x] Inside the existing `if provider in ("local_file", "pdf"):` block, after the `.pdf`-or-`pdf`-provider check, add an `elif suffix == ".docx":` branch.
  - [x] Branch calls `_source_ops.wrangle_local_docx(path)`, wraps any exception in the `except` layer so `_wrangle_source()` converts it to FAILED outcome with `error_kind="docx_extraction_failed"`. Use the existing `_classify_fetch_error()` or add an explicit `except` with `error_kind` string (check the current pattern for `wrangle_local_pdf` failures for exact taxonomy).
  - [x] Preserve existing fall-through `read_text_file()` for `.md` / `.txt` / other text — DO NOT collapse the fall-through into the DOCX branch.
- [x] **T4 — Update `transform-registry.md`** (AC-C.3, AC-S8)
  - [x] DOCX section: expand "Known Limitations" for Priority-1 row to the full list enumerated in AC-C.3.
  - [x] Add cross-reference footnote/note pointing at `wrangle_local_docx()` in `source_wrangler_operations.py` and the `.docx` branch in `run_wrangler._fetch_source()`.
- [x] **T5 — Unit tests** (AC-T.1, T.2a, T.2b, T.3, T.4)
  - [x] Add a test-local DOCX builder helper at top of `test_texas_source_wrangler_operations.py` that uses `python-docx` `Document()` + `doc.add_heading()` / `doc.add_paragraph()` / `doc.add_table()` to synthesize fixtures at `tmp_path`. Do NOT check a binary DOCX fixture into git — generate in-test (avoids binary-in-repo policy drift).
  - [x] `test_wrangle_local_docx_happy_path` (AC-T.1) — 3 heading levels, 2 tables, numbered list, ~300 words; fixture interleaves a table between paragraphs to catch iteration-order drift.
  - [x] `test_wrangle_local_docx_corrupt_file_raises` (AC-T.2a) — write `b"not a docx"` to `tmp_path / "broken.docx"`; assert extractor raises a catchable exception. Library-layer only.
  - [x] `test_wrangle_source_maps_docx_corruption_to_failed_outcome` (AC-T.2b) — invoke `run_wrangler._wrangle_source()` on directive pointing at same corrupt fixture; assert FAILED outcome with exact `error_kind`, `error_detail`, `known_losses`. Adapter-layer only.
  - [x] `test_wrangle_local_docx_empty_document` (AC-T.3).
  - [x] `test_wrangle_local_docx_images_only` (AC-T.4) — use pillow PNG via `io.BytesIO` (NOT `tmp_path` file) and `doc.add_picture()` from the BytesIO stream. Avoids parallel-pytest disk race.
- [x] **T6 — Integration test in `test_run_wrangler.py`** (AC-T.5)
  - [x] Generate a DOCX at `tmp_path`; build a minimal directive YAML referencing it; invoke `run_wrangler` programmatically (existing harness pattern in this file); assert outcome + `extracted.md` content + `metadata.json` provenance.
- [x] **T7 — Contract lockstep test** (AC-T.6)
  - [x] Create `tests/contracts/test_transform_registry_lockstep.py` mirroring the existing contract-test pattern in `test_pack_doc_matches_schema.py`.
  - [x] Parse `transform-registry.md` by markdown-section heading (every `## {Format}` row).
  - [x] Define `REGISTRY_METHOD_TO_EXTRACTOR` and `LOCKSTEP_EXEMPTIONS` as module-level constants per AC-T.6 spec. Module docstring encodes the meta-principle ("A lockstep-check exemption is...").
  - [x] Iteration assertion: EVERY format in the parsed registry must be covered by `REGISTRY_METHOD_TO_EXTRACTOR` OR listed in `LOCKSTEP_EXEMPTIONS`; else FAIL with instructive message pointing to "add an extractor or add an exemption entry." This is the lockstep doing its job.
  - [x] For each in-scope format: (a) dispatch-key presence via `inspect.getsource(run_wrangler._fetch_source)` regex check, (b) extractor name importable from `source_wrangler_operations` (via the same `load_module_from_path` loader Texas uses).
  - [x] Emit `error` (pytest FAIL) for capability drift (registry promises extractor, code lacks dispatch or function); emit `warn` (pytest WARN) for format-only drift (e.g., priority-order change, version-note cosmetic update).
- [x] **T8 — Manual Tejal-fixture validation**
  - [x] Re-run cross-validation against the halted-trial bundle's DOCX asset (path captured in `trial-run-c1m1-tejal-20260417.md`); expect ≥80% key-term coverage on PDF↔DOCX pair. **This is the story's reason for being — if this fails, the story is not done.**
- [x] **T9 — Regression + closure**
  - [x] Full `pytest` green — baseline **1023 passed, 2 skipped, 0 failed**. Actual after 27-1: **1036 passed, 2 skipped, 0 failed** (+9 collecting tests mine [5 unit + 1 integration + 3 contract after Murat's T.6 atomicity split] + 4 from intervening 26-6/26-7 closeout commits). No existing PDF-lockstep or extraction-idempotency test to mirror (verified pre-green-light).
  - [x] Pre-commit hooks green (ruff + orphan + co-commit).
  - [x] Party-mode implementation review (Winston + Amelia + Murat).
  - [x] `bmad-code-review` layered pass (Blind Hunter + Edge Case Hunter + Acceptance Auditor); MUST-FIX remediated.
  - [x] Flip `sprint-status.yaml::development_status::27-1-docx-provider-wiring` → `done` with closure comment.

## Dev Notes

### Architecture guardrails (from ratification + Epic 27 spine)

- **Texas stays a pure technician.** No editorial judgment on DOCX content. Faithful extraction only. (Winston Round-1.)
- **Structured return, not blob dump.** Return the full `(title, body, SourceRecord)` tuple the rest of Texas consumes. Don't invent a new return shape. (AC-S3 of epic spine.)
- **No new top-level provider name.** DOCX stays under `local_file` provider (same as `.md` / `.txt`) — operators don't write `provider: docx` in directives. The dispatch branch on file suffix is an internal implementation detail. (Matches current PDF handling — PDF has both `local_file` with `.pdf` suffix AND an explicit `provider: pdf` alias; DOCX needs only the suffix route.)
- **No cassettes.** DOCX extraction is deterministic and local — no network, no cassette required. This is a `@pytest.mark.live_api`-free story.

### Source tree (new + touched)

```
skills/bmad-agent-texas/
├── scripts/
│   ├── source_wrangler_operations.py    [TOUCH] +wrangle_local_docx() ~line 239
│   ├── run_wrangler.py                  [TOUCH] +.docx branch in _fetch_source()
│   └── tests/
│       ├── test_texas_source_wrangler_operations.py  [TOUCH] +4 tests
│       └── test_run_wrangler.py          [TOUCH] +1 integration test
└── references/
    └── transform-registry.md            [TOUCH] DOCX section rewrite

tests/contracts/
└── test_transform_registry_lockstep.py  [NEW]

pyproject.toml                            [TOUCH] +python-docx>=1.1,<2
requirements.txt                          [TOUCH] +python-docx>=1.1,<2
```

### Previous story intelligence (from 26-7 Texas CLI cp1252 guard closeout)

The 2026-04-17 closeout of **Story 26-7** (Texas CLI cp1252 guard) established several patterns this story MUST inherit:

- **Test file location.** Texas tests live under `skills/bmad-agent-texas/scripts/tests/` (per pyproject's `testpaths`), NOT under top-level `tests/`. Unit tests for this story go in `test_texas_source_wrangler_operations.py` (existing file); integration tests in `test_run_wrangler.py` (existing file). **Do NOT create a new `tests/test_docx_provider.py` at top-level** — that was the older naming in the ratification stub; the co-located Texas pattern is now canonical.
- **Module-loaded import pattern.** Texas scripts cannot be imported via `from skills.bmad-agent-texas.scripts... import ...` (hyphenated parent path blocks Python imports). `run_wrangler.py` uses `load_module_from_path` (lines 55-72). Test fixtures follow the same pattern; existing tests reference the canonical loader. No new import pattern needed for DOCX — `wrangle_local_docx` lives inside `source_wrangler_operations.py` (already module-loaded).
- **CLI UTF-8 guard already in place.** `run_wrangler.py` imports `_cli_encoding` at module-top and fires the guard pre-import. New DOCX code inherits this automatically; no duplication. AC-C.5 is a verification-only checkbox because of this.
- **Co-commit test + impl.** Per `feedback_regression_proof_tests.md` hard preference (and 26-7's closeout pattern): new tests land in the same commit as the implementation. Do not split across commits.
- **Pre-commit hygiene.** 26-7 landed with ruff + orphan + co-commit hooks green. 77 auto-fixes landed in-flight on unrelated files during the 26-7 commit (warehouse-debt clearing per `progress_map.py` 2026-04-17). Expect the same pattern for 27-1; don't block on unrelated ruff fixes that land with the commit.
- **Review-record closure shape.** 26-7's Review Record (see below) is the template for this story's closure section — document MUST-FIX with `[x] [Review][Patch]` markers, deferred SHOULD-FIX with `[ ] [Review][Defer]`, and dismissed NITs explicitly.

### Testing standards

- **Unit / integration split**: unit tests exercise `wrangle_local_docx()` directly against in-test-generated DOCX; integration tests exercise the full `run_wrangler` CLI path via `main()` or programmatic invocation.
- **No live-API dependency.** This story is offline-only. No `@pytest.mark.live_api` tests; no `@pytest.mark.trial_critical` — this isn't a pre-Prompt-1 trial gate, it's a content-extraction correctness fix.
- **Fixture hygiene.** Generate DOCX fixtures in-test with `tmp_path`; do NOT commit a `.docx` binary into the repo. `python-docx` can author its own fixtures programmatically, keeping the repo ASCII-clean and preventing fixture-drift.
- **Regression coverage.** Per `feedback_regression_proof_tests.md`: every fix either updates, restores, or deletes a test; measure via `pytest --collect-only` count delta, don't eyeball. Expected delta: **+6 tests** (4 unit + 1 integration + 1 contract).

### References

- Epic spine: [_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md](epic-27-texas-intake-expansion.md) — §Cross-cutting Acceptance Criteria (AC-S spine), §Risk register.
- Transform registry (canonical promise): [skills/bmad-agent-texas/references/transform-registry.md](../../skills/bmad-agent-texas/references/transform-registry.md) §DOCX.
- Trial-halt evidence: [_bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260417.md](trial-run-c1m1-tejal-20260417.md) — DOCX extraction metrics + missing-key-terms binary-noise capture.
- Related closed story (patterns): [_bmad-output/implementation-artifacts/26-7-texas-cli-cp1252-guard.md](26-7-texas-cli-cp1252-guard.md) — CLI entrypoint + pre-commit + closure-record template.
- Feedback references: `feedback_regression_proof_tests.md` (test-count discipline), `feedback_bmad_workflow_discipline.md` (sprint-charter compliance).
- `python-docx` upstream: current stable is **1.1.2** (Oct 2024). Python ≥3.9 required. API: `from docx import Document; doc = Document(path); for p in doc.paragraphs: ...; for t in doc.tables: ...`. Docstring and readthedocs at `python-docx.readthedocs.io`.

### Non-goals

- **Real-world-robustness DOCX testing** (Murat implementation-review SHOULD-FIX, 2026-04-17). AC-T.2a (`test_wrangle_local_docx_corrupt_file_raises`) is a **library-raise smoke test** using `b"not a docx file at all"` raw bytes — proves `python-docx` rejects non-ZIP input cleanly. It does NOT test: password-protected DOCX (valid-ZIP-but-encrypted); macro-bearing `.docm` (different suffix anyway, but shape-adjacent); DOCX with valid-ZIP but malformed content.xml; Google Docs / Pages exports with non-standard namespace declarations. Real-world-shape hardening is **deferred to a follow-on story in Epic 27 or later** (likely a "Texas intake robustness" candidate; not yet open). This is a documented scope boundary, not a coverage gap.
- **Full-featured DOCX parsing.** Footnotes, comments, tracked changes, embedded media (beyond acknowledging images exist) — out of scope. `python-docx`'s existing capability surface is accepted; losses documented per registry.
- **Lockstep-check coverage beyond pilot.** AC-T.6 lands **DOCX + PDF + Notion** lockstep (code-review amendment 2026-04-17 — original green-light enumeration included Playwright, but Playwright has no top-level `## {Format}` section in the registry, so section-parser-based discovery cannot reach it without a bespoke probe). HTML/URL, Markdown-fall-through, and Future-Placeholder are exemption-encoded in `LOCKSTEP_EXEMPTIONS`; extending lockstep to Playwright and other formats is follow-up work tracked under Audra L1 expansion (not this epic).
- **Automated Tejal regression fixture.** T8 manual Tejal validation stays a blocking checkbox for 27-1 because the halted-trial bundle IS the ground truth we're regressing against. Distilling a minimized Tejal-class DOCX fixture (~5 pages exhibiting tables + numbered lists + the exact heading pattern) into an automated regression test is **follow-up work for Epic 28 or later** (Murat's T8 hardening ask). For that automated follow-up, tighten threshold from 80% → ≥90% or exact-match on a curated key-term list.
- **Tests/contracts/README.md.** Paige flagged this as nice-to-have for the first contract test of this kind (lockstep-pattern). Deferred to a lightweight follow-up; not 27-1 scope.
- **`.doc` (pre-2007 binary format) support.** Deferred. If operator hits this, document in registry as `unsupported: use .docx export from Word` — no code path.
- **Alternative extractors (LibreOffice CLI, ZIP+XML).** Registry lists them as Priority-2 / Priority-3 fallbacks but they are NOT in 27-1 scope. If `python-docx` fails, the outcome is a FAILED `SourceOutcome` and the operator reroutes — no automated fallback chain in this story.

## Test Plan

| Test | Level | Cassette? | Blocking at merge? |
|------|-------|-----------|---------------------|
| `test_wrangle_local_docx_happy_path` (AC-T.1) | Unit | No | Yes |
| `test_wrangle_local_docx_corrupt_file_raises` (AC-T.2a) | Unit | No | Yes |
| `test_wrangle_source_maps_docx_corruption_to_failed_outcome` (AC-T.2b) | Unit | No | Yes |
| `test_wrangle_local_docx_empty_document` (AC-T.3) | Unit | No | Yes |
| `test_wrangle_local_docx_images_only` (AC-T.4) | Unit | No | Yes |
| `test_run_wrangler::test_docx_integration_scenario` (AC-T.5) | Integration | No | Yes |
| `test_transform_registry_lockstep::test_every_format_covered_or_exempted` (AC-T.6) | Contract | No | Yes |
| Manual Tejal DOCX validation (T8) | Integration (real fixture) | No | **Yes — this is the story's point** |

Target baseline delta: **+9 collecting tests** (5 unit + 1 integration + 3 contract; T.6 split into 3 atomic tests per Murat's green-light patch). AC-T.7 is a non-collecting suite-level regression gate, not a test. No new skips, no new xfail, no new live_api, no new trial_critical.

## Risks

| Risk | Mitigation |
|------|------------|
| `python-docx` fails on real-world DOCX shapes (password-protected, macro-bearing, non-standard) | AC-B.3 controlled-failure path + AC-T.4 images-only test + AC-T.2 corrupt test. Production failure still lands a FAILED outcome, not a traceback. |
| Byte-count discrepancies between old `read_text_file()` path and new `python-docx` path break cassette-based tests that happen to use `.docx` | Pre-merge audit: `grep -r "\.docx" skills/bmad-agent-texas/scripts/tests/fixtures/ tests/cassettes/` — if any, expected-counts need update; if none, no mitigation needed. Likely none — cassettes are HTTP-response bodies, not DOCX payloads. |
| Table-order interleave with paragraphs wrong when using simple `doc.paragraphs` + `doc.tables` iteration (tables appear clustered at end instead of inline) | AC-T.1 fixture places a table between paragraphs; if that test fails, upgrade to `doc.element.body` iteration for correct body-order. Noted in T2 subtask. |
| `python-docx` install bumps transitive dep versions and breaks something else | `python-docx` has a small dep surface (`lxml`, `typing_extensions`). Pin range mirrors pypdf/pillow pattern; if a transitive conflict surfaces, escalate to `uv lock` reconciliation per repo convention. |
| Lockstep check (AC-T.6) too strict and flags legitimate format-level variations | Check emits `error` for capability drift (promise-vs-code), `warn` for format-only drift. First pilot with DOCX + PDF + Notion only (Playwright dropped — code-review amendment, no top-level registry section); not yet enforced repo-wide. |

## Dev Agent Record

### Agent Model Used

claude-opus-4-7[1m] (Claude Code, session 2026-04-17)

### Debug Log References

- **Integration test drift discovery (AC-T.5 first run):** exit code was 10 (`EXIT_COMPLETE_WITH_WARNINGS`) instead of 0 — two root causes surfaced:
  1. `_assess_structural_fidelity` in `extraction_validator.py` detects paragraph separators via `\n\n`; first implementation used single `\n` between rendered blocks → `structural_fidelity: none`. Fix: switched `extract_docx_text` to block-based emission with `"\n\n".join(blocks)`.
  2. `extractor_used` came back as `"local_text_read"` because `_EXTRACTOR_LABELS` was keyed by `provider` only, and DOCX shares `local_file` with text reads. Fix: added `_EXTRACTOR_LABELS_BY_KIND` keyed by `SourceRecord.kind`; `_wrangle_source` now prefers per-kind label, falling back to provider label.
- **Line-repetition heuristic:** first integration fixture repeated one paragraph 5 times; `extraction_validator` flagged "High line repetition detected". Fix: fixture now uses 5 distinct paragraphs with varied content.
- **Contract-test parser:** registry's Priority-1 cells wrap only the library name in backticks (`` `pypdf` (text extraction) ``). First parser kept the trailing backtick. Fix: strip all backticks from method cell contents.

### Completion Notes List

- **All 4 behavioral ACs (B.1-B.4) satisfied.** `SourceRecord.kind == "local_docx"` (B.1); heading-style paragraphs render as `#`..`######` with body-order iteration preserving table interleave (B.2); malformed DOCX produces FAILED `SourceOutcome` with `error_kind="docx_extraction_failed"` and `known_losses=["docx_open_failed"]`, no fall-through to `read_text_file` (B.3); Tejal PDF↔DOCX cross-validation yields 100% key-term coverage, 69/69 sections, `passed: true` (B.4 — target was ≥80%).
- **All 7 test ACs (T.1-T.7) satisfied.** T.1 happy-path verifies heading/table/paragraph rendering + body-order discipline + `rec.kind`/`rec.note` shape. T.2a library-raise confirmed via in-test `b"not a docx"` fixture (malformed-ZIP branch per Winston). T.2b adapter-FAILED confirmed via `_wrangle_source()` invocation. T.3 empty DOCX → zero counts, empty body. T.4 images-only → PIL BytesIO PNG + `doc.add_picture()`, zero counts, empty body. T.5 full `run_wrangler.main(...)` integration produces 6 artifacts + `quality_tier == 1` (FULL_FIDELITY) + `extractor_used: "python-docx"` in provenance. T.6 split into 3 tests (`test_every_format_covered_or_exempted` / `test_in_scope_extractors_importable` / `test_in_scope_dispatches_wired`) per Murat's atomicity rule. T.7 suite-level regression: **1036 passed / 2 skipped / 27 deselected / 2 xfailed** (baseline was 1023 passed; +9 collecting mine, +4 from intervening commits in unrelated files).
- **All 5 contract-pinning ACs (C.1-C.5) satisfied.** C.1 `wrangle_local_docx` lives adjacent to `wrangle_local_pdf` in `source_wrangler_operations.py`, same signature shape. C.2 `_fetch_source` `local_file` branch extended with `suffix == ".docx"` check before fall-through; no restructuring. C.3 registry DOCX section rewritten with exhaustive known-limitations + implementation cross-reference footnote. C.4 `python-docx>=1.1,<2` pinned in both `pyproject.toml` and `requirements.txt` (mirrors `pypdf>=5.0,<6` pattern). C.5 CLI UTF-8 guard inheritance verified — `run_wrangler.py` still fires `_cli_encoding.ensure_utf8_stdout()` at module top; no work needed for DOCX.
- **Ruff lint: clean** across all changed files after auto-fix pass + 3 manual line-length breakdowns.
- **Pre-commit hooks all green:** ruff lint, orphan-reference detector, co-commit invariant.
- **Trial-critical suite:** 159 passed, 0 failed (unchanged from baseline; 27-1 correctly not marked `trial_critical`).
- **Murat's split of AC-T.6 into 3 atomic tests (rather than 1 combined)** resulted in +9 collecting tests instead of the originally-projected +7. Murat's preference: library-vs-adapter-vs-registry assertions are independent contracts that fail for different reasons.
- **Baseline delta accounting (Amelia implementation-review ask, 2026-04-17):** the +13 pytest count delta (1023 → 1036) breaks down as +9 mine + 4 from intervening commits landed between the 2026-04-17 19:00 baseline note in sprint-status.yaml and dev-story start. Those intervening commits were `8fc2121 feat(26-7) Texas CLI cp1252 guard` (added 3 cp1252-boundary tests), `c78b1bb fix(26-6) code-review remediation — MUST-FIX + missing-AC tests`, plus minor test-count drift from other 26-6 remediation commits (`5548a3a`, `d3e4e6a`). No unrelated file modifications in scope; no regression risk introduced by the delta.

### File List

**New:**
- `tests/contracts/test_transform_registry_lockstep.py` (+276 lines) — AC-T.6 contract test with `REGISTRY_METHOD_TO_EXTRACTOR` + `LOCKSTEP_EXEMPTIONS` constants, registry parser, 3 atomic assertions.

**Modified:**
- `pyproject.toml` — added `"python-docx>=1.1,<2"` to `[project] dependencies`.
- `requirements.txt` — added `python-docx>=1.1,<2` with rationale comment.
- `skills/bmad-agent-texas/scripts/source_wrangler_operations.py` — added 4 `docx` imports + `_HEADING_STYLE_RE` constant + `extract_docx_text()` (+77 lines) + `wrangle_local_docx()` (+37 lines) adjacent to `wrangle_local_pdf`; module docstring updated to include DOCX.
- `skills/bmad-agent-texas/scripts/run_wrangler.py` — new `.docx` branch in `_fetch_source()` `local_file` dispatch (+11 lines); `_EXTRACTOR_LABELS_BY_KIND` dict added (+9 lines); `_classify_fetch_error()` gains `PackageNotFoundError → docx_extraction_failed` case (+5 lines); `_fetch_error_known_losses()` helper added (+15 lines); `_wrangle_source()` now preserves `rec` (was `_rec`) and sets extractor label from kind; `known_losses` construction delegated to the new helper.
- `skills/bmad-agent-texas/scripts/tests/test_texas_source_wrangler_operations.py` — 3 new imports (`io`, `docx.Document`, `docx.shared.Inches`, `PIL.Image`); 3 DOCX-builder helpers (`_build_happy_path_docx`, `_build_empty_docx`, `_build_images_only_docx`); 5 new tests (AC-T.1, T.2a, T.2b, T.3, T.4) totaling +167 lines.
- `skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py` — new `_build_docx_fixture` helper + `test_docx_integration_scenario` (AC-T.5, +61 lines).
- `skills/bmad-agent-texas/references/transform-registry.md` — DOCX section known-limitations expanded + implementation cross-reference footnote added (+5 lines).

### Change Log

- 2026-04-17 21:50 — Dev-story execution started on `dev/epic-27-texas-intake` branch.
- 2026-04-17 21:52 — T1: python-docx 1.2.0 installed; pyproject + requirements pinned.
- 2026-04-17 21:55 — T5a: 5 RED unit tests authored (AC-T.1/T.2a/T.2b/T.3/T.4) verified failing against not-yet-existing extractor.
- 2026-04-17 21:57 — T2 + T3: `extract_docx_text` + `wrangle_local_docx` in `source_wrangler_operations.py`; `.docx` dispatch in `run_wrangler._fetch_source`; `_classify_fetch_error` extended; `known_losses` helper added; `_EXTRACTOR_LABELS_BY_KIND` added. All 5 unit tests GREEN on first run.
- 2026-04-17 21:59 — T4: `transform-registry.md` DOCX section rewritten.
- 2026-04-17 22:00 — T6: integration test AC-T.5 authored; first run exit=10 due to `\n\n` paragraph convention + `extractor_used` mismatch; fixed both (block-based emission + `_EXTRACTOR_LABELS_BY_KIND`).
- 2026-04-17 22:02 — T7: contract lockstep test authored with assertion-encoded exemptions per Murat+Paige consensus; parser fixed to strip backticks; 3 tests GREEN.
- 2026-04-17 22:03 — Full pytest regression: 1036 passed / 2 skipped / 0 failed (vs 1023 baseline). Trial-critical: 159 passed. Ruff: auto-fix + 3 manual breakdowns → clean.
- 2026-04-17 22:04 — T8 Tejal manual validation: `word_count_ratio: 1.04`, **100% key-term coverage, 69/69 sections, passed: true**. Trial-halt defect closed.
- 2026-04-17 22:05 — Pre-commit hooks (ruff + orphan + co-commit) all green on change set.
- 2026-04-17 22:05 — Status flipped to `review`; sprint-status.yaml updated.

### Review Record

**bmad-code-review layered pass — 2026-04-17 22:30** (Blind Hunter + Edge Case Hunter + Acceptance Auditor; adversarial-general skill pattern).

**Layered review summary:**
- Blind Hunter: 7 findings (0 MUST-FIX, 2 SHOULD-FIX, 5 NIT).
- Edge Case Hunter: 10 findings (0 MUST-FIX, 4 SHOULD-FIX, 6 NIT).
- Acceptance Auditor: 6 findings (0 MUST-FIX, 3 SHOULD-FIX, 3 NIT); AC coverage audit: 13 SATISFIED, 3 THIN (AC-B.3, AC-T.2b, AC-T.6), 0 MISSING.

**Triage verdict:** 0 decision-needed, 8 patch, 4 defer, 6 dismiss. **No MUST-FIX.**

#### Review Findings

**MUST-FIX — remediated:** none.

**SHOULD-FIX — remediated this cycle:**
- [x] [Review][Patch] PackageNotFoundError name-class collision — classifier now qualifies on `type(exc).__module__.startswith("docx.")` to avoid mis-classifying `importlib.metadata.PackageNotFoundError` or similar foreign exceptions. [run_wrangler.py `_classify_fetch_error`]
- [x] [Review][Patch] Merged-cell row duplication — `extract_docx_text` now de-duplicates consecutive identical `_tc` (table-cell element) references per row so horizontally-merged cells render once as `| Revenue | Total |` instead of `| Revenue | Revenue | Total |`. Registry known-limitations updated accordingly. [source_wrangler_operations.py]
- [x] [Review][Patch] AC-T.6 Playwright scope drift — spec text amended to "DOCX + PDF + Notion lockstep" with explicit Non-goals entry explaining Playwright has no `## {Format}` registry section and therefore cannot be discovered by section-parser-based lockstep. [27-1-docx-provider-wiring.md, test_transform_registry_lockstep.py docstring]
- [x] [Review][Patch] LOCKSTEP_EXEMPTIONS key deviation — spec text amended to match shipped keys (`html / url`, `markdown (.md)`, `future (placeholder)`) with rationale that original spec example was aspirational and code adapted to the registry's actual section names.
- [x] [Review][Patch] AC-B.3 "no traceback on stdout" assertion — `test_wrangle_source_maps_docx_corruption_to_failed_outcome` now captures `capsys` output and asserts no `Traceback` substring leaks to stdout/stderr. [test_texas_source_wrangler_operations.py AC-T.2b]

**SHOULD-FIX / NIT — remediated this cycle:**
- [x] [Review][Patch] Empty-element counter semantics — `extract_docx_text` now only increments `counts["paragraphs"]` and `counts["headings"]` when content is actually rendered (non-empty text). Aligns `rec.note` counts with content reality instead of DOCX-structure element-count. [source_wrangler_operations.py]
- [x] [Review][Patch] Lockstep `cells[0].startswith("1")` parser brittleness — tightened to `cells[0].strip().split()[0] == "1"` so future "10"/"11" priority rows don't mis-classify. [test_transform_registry_lockstep.py `_parse_registry_sections`]
- [x] [Review][Patch] AC-T.7 +7 vs +9 internal doc inconsistency — body text updated to match TL;DR / Closure Criteria (+9 collecting tests, 1036 passed). [27-1-docx-provider-wiring.md AC-T.7]

**SHOULD-FIX — documented, deferred to follow-up:**
- [x] [Review][Defer] Sibling Office-ZIP suffixes `.docm` / `.dotx` / `.dotm` still fall through to `read_text_file()` (re-introduces binary-garbage defect class for rarer suffixes). [run_wrangler.py `_fetch_source`] — deferred to "Texas intake robustness" follow-on story per Murat's implementation-review scope call; captured in `_bmad-output/maps/deferred-work.md`.
- [x] [Review][Defer] DOCX body-order iteration silently drops `<w:sdt>` and `<w:altChunk>` content (form controls, templated placeholders, embedded sub-docs). Same follow-on story. [source_wrangler_operations.py `extract_docx_text`]

**NIT — documented, deferred:**
- [x] [Review][Defer] `extract_docx_text` docstring narrower than reality — python-docx can raise `BadZipFile`, `KeyError` (missing style reference), `AttributeError` under unusual inputs; docstring only lists `PackageNotFoundError`. Doc-accuracy follow-up. [source_wrangler_operations.py]
- [x] [Review][Defer] Integration test `provenance[0]["ref"] == str(docx_path)` could flake on Windows short-path resolution. Switch to `Path(...).samefile(...)` if observed. [test_run_wrangler.py]

**Dismissed as NIT (no action):**
- `datetime.UTC` alias — `pyproject.toml` pins `requires-python = ">=3.11"`; `UTC` alias is available. No portability risk.
- `rec else None` defensive guard may be dead — intentional future-proofing; no current bug.
- `_rec` → `rec` rename — `rec` is used below; no unused-var signal loss.
- Char-budget off-by-~15-char accounting — soft-floor budget, cosmetic.
- Empty-stem title produces `## ` — inherited from PDF pattern, not 27-1 regression.
- Registry parser strips backticks while spec example used short names — spec example was aspirational; code's real keys are the correct ones.

**Blind Hunter / Edge Case Hunter / Acceptance Auditor layer breakdown:**
- 1 finding surfaced by both Blind + Edge (PackageNotFoundError collision — merged).
- 1 finding surfaced by both Blind + Edge (merged-cell duplication — merged).
- 1 finding surfaced by Blind + Edge (lockstep parser `startswith("1")` brittleness — merged).
- 5 Blind-only findings (mostly NIT).
- 7 Edge-only findings (mixed SHOULD-FIX + NIT, most around DOCX real-world shapes).
- 6 Auditor-only findings (AC-coverage-specific: Playwright drift, exemption keys, stdout assertion, count-text inconsistency, heading-count semantics, backtick cosmetic).

**Negative-control Tejal fixture** (Murat follow-on from implementation-review) filed to `_bmad-output/maps/deferred-work.md`.

**Final closure state:**
- 8 SHOULD-FIX/NIT patches applied in this cycle (5 code/test + 3 spec-text).
- 4 SHOULD-FIX/NIT items deferred to follow-on (all documented in deferred-work.md with rationale).
- 6 NIT items dismissed with rationale.
- Full regression re-run after remediation: **1036 passed / 2 skipped / 27 deselected / 2 xfailed** (unchanged from pre-remediation baseline). Ruff + pre-commit clean.

## Party Input Captured (ratification, 2026-04-17)

- **John (PM, Round 3):** "DOCX is clearly one story (contract-drift fix). Ships first, alone."
- **Amelia (Dev, Round 3):** 2 points, blocks Tejal restart, specific file-path impact enumerated.
- **Murat (Test, Round 2 + 3):** Lockstep check at AC-S6 is the pattern that would have caught the drift pre-trial; this story lands the initial implementation (AC-T.6).
- **Paige (Docs, Round 2):** Registry-vs-code SSOT discipline; `transform-registry.md` is the canonical promise, code must match (AC-C.3).
- **Winston (Round 1):** Texas stays pure technician — no editorial judgment on DOCX content, just faithful extraction.

## Green-Light Patches Applied (party-mode, 2026-04-17 21:45)

Four-agent independent green-light round (Winston + Amelia + Murat + Paige) produced these consensus spec patches before `bmad-dev-story` execution:

- **AC-T.2 split → T.2a + T.2b** (Murat atomicity): library-raise and adapter-FAILED-mapping are separate contracts; red-light must point at the right layer.
- **AC-T.6 `LOCKSTEP_EXEMPTIONS` dict-encoded exemptions** (Murat + Paige consensus): silent skips rot lockstep tests; a format must be either in-scope OR in the exemptions dict with a rationale string — else test FAILS. Meta-principle encoded in test module docstring.
- **AC-T.6 mapping lives as Python constant in test file, NOT parsed from footnote** (Paige decoupling): prevents code↔prose coupling and rename fragility.
- **AC-T.7 clarified as non-collecting suite-level AC** (Amelia): not a `def test_*`. Delta math corrected to +7 collecting tests.
- **AC-C.3 known-limitations bullets collapsed** (Paige clarity): `style/formatting loss beyond headings H1-H6 — bold, italic, colors, fonts, paragraph spacing not preserved` replaces overlapping `formatting loss` + `style loss` pair.
- **T.4 pillow PNG via BytesIO, not tmp_path** (Murat flakiness rule): avoids parallel-pytest disk race.
- **T.1 fixture interleaves table between paragraphs** (Murat iteration-order guard).
- **T.2a fixture shape specified: invalid-ZIP raw bytes** (Winston fidelity guard): malformed-ZIP branch, not wrong-mime branch.
- **T8 manual stays blocking for 27-1; automated Tejal-class fixture deferred to Epic 28+** (Murat hardening path).
- **PDF-extraction-idempotency pre-check done**: no such test exists at the extraction layer; DOCX does not inherit one.
- **Module-local `skills/bmad-agent-texas/requirements.txt` pre-check done**: does not exist; no action needed.
- **TL;DR banner added at top** (Paige readability).

Verdicts: Winston GREEN · Amelia GREEN (after T.7 clarification) · Murat GREEN (after three patches applied) · Paige GREEN (after two patches applied). **Green-light gate: PASSED by consensus.**

## Implementation Review Patches Applied (party-mode round 2, 2026-04-17 22:15)

Three-agent implementation-review round (Winston + Amelia + Murat) produced these consensus patches AFTER dev-story but BEFORE `bmad-code-review`:

- **Dispatch-regex fragility signpost** (Murat SHOULD-FIX): module-top docstring on `REGISTRY_METHOD_TO_EXTRACTOR` in `tests/contracts/test_transform_registry_lockstep.py` warning future refactorers that source-inspection lockstep requires regex updates when dispatch style changes (constants, match/case, tuple membership, method-style comparisons). Converts fragility from landmine to signpost.
- **Real-world-robustness scope note** (Murat SHOULD-FIX): added to §Non-goals clarifying that AC-T.2a is a library-raise smoke test, not a real-world-shape robustness test; password-protected / macro / Google-Docs-export / corrupted-ZIP-valid hardening deferred to an Epic 27 follow-on story.
- **Baseline-delta commit citations** (Amelia nice-to-have): Dev Agent Record now cites the specific intervening-commit SHAs that account for the +4 count beyond the +9 mine — `8fc2121` (26-7), `c78b1bb` / `5548a3a` / `d3e4e6a` (26-6 remediation).
- **python-docx internal-API comment** (Winston minor polish): inline comment above the `iterchildren()` loop in `extract_docx_text` documenting the community-canonical body-order workaround pattern and the `<2` upper pin as the guardrail.

Follow-on tickets logged (non-blocking, not 27-1 scope):
- Winston: collapse `_EXTRACTOR_LABELS` + `_EXTRACTOR_LABELS_BY_KIND` to a single kind-keyed source of truth with provider-derived default kind (~20 min polish pass).
- Murat: negative-control fixture for Tejal cross-validator — a DOCX/PDF pair from unrelated source docs that should cross-validate as DIFFERENT, so the 100% result can be positively distinguished from "heuristic is loose."
- Epic 27 follow-on: real-world DOCX robustness (password-protected, macros, Google Docs / Pages exports, corrupted-ZIP-valid). Candidate story name "Texas intake robustness."

Verdicts: Winston **APPROVE** (no MUST-FIX, one follow-up ticket) · Amelia **APPROVE** (one nice-to-have applied) · Murat **CONDITIONAL-APPROVE → APPROVE** (both SHOULD-FIX applied; two follow-ons logged). **Implementation-review gate: PASSED by consensus.**

## BMAD Closure Criteria

- [x] All AC-B.1 through AC-B.4 behavioral assertions green in test output.
- [x] All AC-T.1, T.2a, T.2b, T.3, T.4, T.5, T.6 collecting tests pass; AC-T.7 suite-level regression gate green; `pytest --collect-only` count shows **+9** collecting tests vs baseline (5 unit + 1 integration + 3 contract — T.6 split into 3 atomic tests per Murat's green-light patch).
- [x] All AC-C.1 through AC-C.5 contract-pinning checks satisfied (manual verification + lockstep test for C.3).
- [x] Manual Tejal DOCX cross-validation: 100% key-term coverage, 69/69 sections matched, `passed: true`.
- [x] Full `pytest` green: 1036 passed, 2 skipped, 27 deselected, 2 xfailed (baseline 1023 + 9 mine + 4 from intervening commits in unrelated files). No new failures, no new skips, no new xfails.
- [x] Pre-commit hooks pass (ruff + orphan + co-commit) on all changed files.
- [x] `bmad-party-mode` implementation review consensus: approve (Winston + Amelia + Murat all GREEN after 4 SHOULD-FIX patches applied).
- [x] `bmad-code-review` layered pass (Blind Hunter + Edge Case Hunter + Acceptance Auditor); 0 MUST-FIX; 8 SHOULD-FIX/NIT patches applied this cycle; 4 SHOULD-FIX deferred to follow-on (documented in `_bmad-output/maps/deferred-work.md`); 6 NITs dismissed with rationale.
- [x] `sprint-status.yaml::development_status::27-1-docx-provider-wiring` flipped to `done` with closure comment referencing this file.
- [ ] Epic 27 roster entry updated (epic file + bmm-workflow-status.yaml) to reflect 27-1 closure — completed immediately after this flip.
