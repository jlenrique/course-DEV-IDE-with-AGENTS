# Story 27-1: DOCX Provider Wiring (Contract Drift Fix)

**Epic:** 27 — Texas Intake Surface Expansion
**Status:** ratified-stub
**Sprint key:** `27-1-docx-provider-wiring`
**Added:** 2026-04-17
**Points:** 2
**Depends on:** none (standalone drift fix)
**Blocks:** Tejal trial restart success (DOCX cross-validation cannot pass today without this fix)

## Story

As the Texas wrangler,
I want DOCX files to be extracted via `python-docx` (as `transform-registry.md` advertises),
So that operator-provided or cross-validation DOCX sources produce faithful text extraction instead of binary garbage from the fall-through `read_text_file()` path.

## Background — Why This Story Exists

The 2026-04-17 APC C1-M1 Tejal trial exposed a contract-vs-code drift. Texas's [`references/transform-registry.md`](../../skills/bmad-agent-texas/references/transform-registry.md) (line 19) advertises `python-docx` as the DOCX extractor with one documented known-loss (formatting / table flattening). Texas's [`scripts/run_wrangler.py`](../../skills/bmad-agent-texas/scripts/run_wrangler.py) (lines 228-244, as of 2026-04-17) does **not** implement it. The `local_file` provider handler has PDF-specific extraction branches but everything else — including `.docx` — falls through to `read_text_file()`, which performs a plain-text read against the DOCX ZIP-of-XML container and produces binary garbage.

**Evidence from the trial run** (archived in [trial-run-c1m1-tejal-20260417.md](./trial-run-c1m1-tejal-20260417.md)):
- DOCX extraction reported 2,044 "words" and 1,522 "lines" but `structural_fidelity: low`, 0 headings.
- Cross-validation reported 2% key-term overlap — the "missing key terms" list contained literal unicode replacement characters and ZIP-compressed byte sequences (e.g., `]\u0307\uFFFD\\...`, `jvbtj\x1A?...`, `ezw`, `vni`, `bjh`), not actual vocabulary.
- The DOCX content was almost certainly fine; Texas just couldn't read it.

This is the cheapest, highest-severity story in Epic 27: wire the library the registry already promises.

## Acceptance Criteria

**AC-1: `python-docx` wired into `.docx` branch of `local_file` handler**
- `skills/bmad-agent-texas/scripts/run_wrangler.py` grows a `.docx` branch in the `local_file` provider dispatch.
- The branch uses `python-docx` (`from docx import Document`) to extract paragraphs, table text, and heading-style runs in document order.
- No fallback to `read_text_file()` for DOCX — if `python-docx` raises, the outcome is a FAILED `SourceOutcome` with `error_kind: docx_extraction_failed`, `error_detail` containing the exception message, and `known_losses: ["docx_open_failed"]`.

**AC-2: Extraction preserves document structure within `python-docx` limits**
- Output `extracted.md` preserves paragraph breaks.
- Heading paragraphs (style `Heading 1..6`) are rendered as `#`..`######` markdown headings.
- Table content is flattened to pipe-separated rows (accepting `python-docx`'s table-flattening known-loss per registry).
- Extracted word_count, line_count, and heading_count are counted from the rendered text, not the raw DOCX bytes.

**AC-3: `transform-registry.md` matches implementation (AC-S8 from Epic 27 spine)**
- Registry row for DOCX lists exactly the capabilities the code now implements.
- Known-losses are enumerated: formatting loss, some table-layout loss, any style loss beyond headings.
- A cross-reference pointer to `run_wrangler.py` line range is included so Audra's lockstep check (AC-S6) has a target.

**AC-4: Cross-validation works on DOCX against extracted primary**
- A directive with a PDF `role: primary` source AND a DOCX `role: validation` source produces a valid `cross_validation[]` block in `extraction-report.yaml`.
- Key-term coverage is computed from real DOCX vocabulary (not binary noise).
- Target: ≥80% key-term coverage on the Tejal fixture's PDF↔DOCX pair. (Lower bound empirical; the content is the same, difference is provider losses only.)

**AC-5: Test coverage (AC-S5 from spine)**
- `tests/test_docx_provider.py` (new) — happy-path extraction against a synthetic DOCX fixture in `tests/fixtures/texas/docx/sample.docx`.
- Failure-mode test: corrupt DOCX → FAILED outcome with correct `error_kind`.
- Integration test: the existing `test_run_wrangler.py` grows a DOCX scenario using the fixture. No network.
- Coverage of the new `.docx` branch ≥ 90%.

**AC-6: Lockstep check stub (AC-S6 from spine — initial pilot)**
- A new test `tests/contracts/test_transform_registry_lockstep.py` (new) asserts: every format advertised in `transform-registry.md` has a corresponding provider branch in `run_wrangler.py` AND a corresponding extractor import.
- DOCX is the pilot format for this check; PDF / URL / Notion / Playwright_html round out the existing coverage.
- Check emits `error` for promise-vs-code divergence (capability drift), `warn` for format-only drift.

**AC-7: Regression — no new failures, no new skips**
- Full pytest green. Baseline for this epic: 622 passing (as of 2026-04-17 progress-map hardening).
- No `@pytest.mark.skip` or `xfail` added to default suite.

## File Impact

| File | Change | Lines (est.) |
|------|--------|--------------|
| [`skills/bmad-agent-texas/scripts/run_wrangler.py`](../../skills/bmad-agent-texas/scripts/run_wrangler.py) | Add `.docx` branch in `_dispatch_local_file()` (or equivalent name); import `python-docx` | +40 |
| [`skills/bmad-agent-texas/references/transform-registry.md`](../../skills/bmad-agent-texas/references/transform-registry.md) | Update DOCX row: confirmed implementation, link to code lines, enumerate known-losses | +5 |
| `tests/test_docx_provider.py` | New — unit tests for `.docx` branch | +80 |
| `tests/fixtures/texas/docx/sample.docx` | New — synthetic DOCX fixture | binary |
| `tests/contracts/test_transform_registry_lockstep.py` | New — lockstep check | +60 |
| `tests/test_run_wrangler.py` | Add DOCX integration scenario | +20 |
| `requirements.txt` or `pyproject.toml` | Add `python-docx` dependency (if not already present) | +1 |

## Tasks / Subtasks

- [ ] T1: Verify `python-docx` is in the dependency set; add if absent.
- [ ] T2: Implement `.docx` branch in `run_wrangler.py` following the existing provider dispatch shape. Include: paragraph iteration, heading-style detection, table flattening, heading/line/word counting.
- [ ] T3: Update `transform-registry.md` DOCX row with the exact implementation capabilities.
- [ ] T4: Create synthetic DOCX fixture (non-trivial content: headings at 3 levels, 2 tables, ~300 words, numbered list) at `tests/fixtures/texas/docx/sample.docx`.
- [ ] T5: Write `tests/test_docx_provider.py` — happy path, corrupt DOCX, empty DOCX, DOCX with only images (no text).
- [ ] T6: Add DOCX scenario to `test_run_wrangler.py` integration suite.
- [ ] T7: Write `tests/contracts/test_transform_registry_lockstep.py` with initial coverage of PDF / DOCX / URL / Notion / playwright_html formats. Surface AC-S6 check as a real test.
- [ ] T8: Manual Tejal-fixture validation — rerun cross-validation against the halted-trial bundle's DOCX asset, expect ≥80% key-term coverage.
- [ ] T9: Regression pass — full pytest green, no new skips.

## Test Plan

| Test | Level | Cassette? | Blocking at merge? |
|------|-------|-----------|---------------------|
| `test_docx_provider::test_happy_path_extracts_structure` | Unit | No (local fixture) | Yes |
| `test_docx_provider::test_corrupt_docx_raises_controlled_failure` | Unit | No | Yes |
| `test_docx_provider::test_empty_docx_emits_empty_extraction` | Unit | No | Yes |
| `test_docx_provider::test_images_only_docx_produces_zero_word_count` | Unit | No | Yes |
| `test_run_wrangler::test_docx_integration_scenario` | Integration | No | Yes |
| `test_transform_registry_lockstep::test_every_format_has_extractor` | Contract | No | Yes |
| Manual Tejal DOCX validation | Integration (real fixture) | No | **Yes** — this is the story's point |

## Out of Scope

- Full-featured DOCX parsing (footnotes, comments, tracked changes, embedded media) — `python-docx`'s existing capability surface is accepted, with losses documented per registry.
- Extending lockstep check to all formats in one pass (AC-S6 full implementation is AC-S1 for each subsequent 27-N story).
- `.doc` (old binary format) support — deferred; if operator hits this, document in registry as unsupported.

## Risks

- `python-docx` failing on real-world DOCX shapes (password-protected, corrupt, non-standard) — mitigated by AC-1 controlled-failure path and AC-5 fixture diversity.
- Byte-count discrepancies between `read_text_file()` old path and `python-docx` new path could break existing cassette-based tests that happen to use DOCX — mitigation: audit `tests/cassettes/texas/` for DOCX content pre-merge.

## Done When

- [ ] All 9 ACs green.
- [ ] Tejal DOCX cross-validation manually re-run and passing ≥80% key-term coverage.
- [ ] `bmad-code-review` run adversarially (Blind Hunter + Edge Case Hunter + Acceptance Auditor), MUST-FIX remediated.
- [ ] Story closure record in `sprint-status.yaml` with review summary.

## Party Input Captured

- **John (PM, Round 3):** "DOCX is clearly one story (contract-drift fix). Ships first, alone."
- **Amelia (Dev, Round 3):** 2 points, blocks Tejal restart, specific file-path impact enumerated above.
- **Murat (Test, Round 2 + 3):** lockstep check at AC-S6 is the pattern that would have caught the drift pre-trial; this story lands the initial implementation.
- **Paige (Docs, Round 2):** registry-vs-code SSOT discipline; `transform-registry.md` is the canonical promise, code must match.
- **Winston (Round 1):** Texas stays pure technician — no editorial judgment on DOCX content, just faithful extraction.
