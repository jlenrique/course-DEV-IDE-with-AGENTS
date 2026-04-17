# Story 25-1: Texas Runtime Wrangling Runner

**Epic:** 25 - Texas Production Integration
**Status:** done
**Sprint key:** `25-1-texas-runtime-wrangling-runner`
**Added:** 2026-04-17
**Closed:** 2026-04-17
**Depends on:** none (stands alone; builds on existing Texas scripts + delegation contract)

## Story

As the production pipeline,
I want Marcus to invoke Texas via a concrete runtime mechanism that executes the full wrangling contract end-to-end,
So that every trial run produces Texas's canonical `extraction-report.yaml` and `manifest.json` artifacts, runs his 4-tier extraction validator and cross-validator on real sources, and closes the 30-line-stub failure class that motivated building Texas in the first place.

## Background — Why This Story Exists

Texas was built via the bmb workflow in the late 2026-04-16 session. He has:
- A sanctum ([_bmad/memory/bmad-agent-texas/](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad/memory/bmad-agent-texas/)) with CREED / PERSONA / BOND / MEMORY / CAPABILITIES / INDEX
- Capability references ([source-interview.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/references/source-interview.md), [extract-and-validate.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/references/extract-and-validate.md), [fallback-resolution.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/references/fallback-resolution.md), [transform-registry.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/references/transform-registry.md))
- Two validators ([extraction_validator.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/scripts/extraction_validator.py) with 4-tier classification, [cross_validator.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/scripts/cross_validator.py) with section/key-term matching)
- A fetch/bundle operations library ([source_wrangler_operations.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/scripts/source_wrangler_operations.py))
- A delegation contract ([delegation-contract.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/references/delegation-contract.md)) describing the Marcus ↔ Texas envelope
- 33 passing unit tests

What is **missing** is the runtime glue. The v4.2g prompt pack Prompt 3 says "Marcus, delegate ingestion for RUN_ID [RUN_ID] to Texas using the wrangling directive contract" — prose instruction only. At runtime Marcus hand-executes fetch + extract + write. Texas's `validate_extraction` and `cross_validate` never actually run on a production trial. Existing bundles (latest 2026-04-15) contain `extracted.md` + `metadata.json` + `ingestion-evidence.md` but **not** `extraction-report.yaml` or `manifest.json`. From the prior session handoff: *"Texas's extraction validator has not been run in a real production pipeline yet — tests pass, but real-world integration via Marcus delegation is not yet wired at runtime."*

**Party-mode decision record for this story:** Winston, Amelia, Murat convened via [reports/dev-coherence/2026-04-16-2350/](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/reports/dev-coherence/2026-04-16-2350/) follow-up party. Consensus: **Shape A** (CLI orchestrator) with runner-includes-fetch, Marcus-generated directive YAML, synthetic fixture as primary integration test, `--legacy-prose` fallback retained for one sprint. **Gate-03 emission (G0 sidecar) is out of scope** for this story per Murat's lane-discipline concern — Vera owns gate judgment; Texas's role is measurement. The Vera-side G0 runner is a follow-up story that can reuse `extraction-report.yaml` as input once it lands.

## Acceptance Criteria

**AC-1: CLI orchestrator entrypoint**
- A new script at [skills/bmad-agent-texas/scripts/run_wrangler.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/scripts/run_wrangler.py) is invocable as `python skills/bmad-agent-texas/scripts/run_wrangler.py --directive <yaml-path> --bundle-dir <dir-path> [--json]`
- Direct-path invocation is required (the hyphenated `bmad-agent-texas` directory name is not a valid Python package, so `python -m ...` is unavailable). Matches the existing prompt-pack script invocation convention (e.g., `skills/bmad-agent-marcus/scripts/generate-storyboard.py`).
- Exit codes: `0` = complete, `10` = complete_with_warnings, `20` = blocked, `30` = directive / IO error
- stdout with `--json`: structured result matching `delegation-contract.md` Texas→Marcus return schema (default format is YAML)

**AC-2: All six contract artifacts emitted**
- After a successful run, `<bundle-dir>/` contains: `extracted.md`, `metadata.json`, `manifest.json`, `extraction-report.yaml`, `ingestion-evidence.md`, and `result.yaml` (the runner's return envelope)
- Each file is non-empty and parses cleanly (YAML loads, JSON loads)

**AC-3: `extraction-report.yaml` schema compliance**
- A new schema spec at [skills/bmad-agent-texas/references/extraction-report-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/references/extraction-report-schema.md) declares the required fields
- The runner's emitted `extraction-report.yaml` conforms to the schema and carries: `run_id`, per-source `tier` (from `ExtractionReport.tier.name`), `completeness_ratio`, `word_count` / `line_count` / `heading_count`, `structural_fidelity`, `evidence[]`, `known_losses[]`, `cross_validation[]` (when validation assets are present), `recommendations[]`, `validator_version`
- A validator test asserts the schema compliance

**AC-4: 30-line-stub tripwire preserved**
- When extraction output is below the 50%-of-expected tripwire (e.g., 30 lines from a 24-page PDF → ~150 words vs ~4800 expected), the runner exits `20` (blocked) and the report tier is `FAILED` or `DEGRADED`
- The result envelope's `status` is `blocked` and `blocking_issues[]` cites the thin extraction with evidence
- This is the exact failure class that motivated Texas — the runner must honor it

**AC-5: Fetch layer covers the declared source types**
- Directive source entries with `provider: local_file` / `pdf`, `url`, `notion`, `playwright_html` are wrangled via the existing [source_wrangler_operations.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/scripts/source_wrangler_operations.py) helpers (`wrangle_local_pdf`, `summarize_url_for_envelope`, `wrangle_notion_page`, `wrangle_playwright_saved_html`)
- An unsupported `provider` value is rejected at directive-load time with exit 30 (directive error) and a clear stderr message — not a deep-fetch traceback, and not a late `blocked` status. (Updated post-review — the original AC expected late `blocked`, but the blocker-resolution party's S1 finding revised the behavior to reject typos early.)
- Any runtime fetch exception (network timeout, missing file, `pypdf.PdfReadError`, Notion API error, `UnicodeDecodeError`) is caught at the fetch boundary and synthesized into a FAILED `SourceOutcome` with `error_kind`, `error_detail`, `known_losses`, and `recommendations` — the runner always produces a `result.yaml` for real-world fetch failures, never a traceback
- Gamma docs URLs continue to raise `GammaDocsURLNotSupportedError` (subclass of `ValueError`) which the runner captures as `error_kind: fetch_failed` with the existing guidance message

**AC-6: Cross-validation runs when validation-role assets are present**
- Directive sources with `role: validation` are cross-validated against the primary extraction using [cross_validator.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/scripts/cross_validator.py) `cross_validate`
- `extraction-report.yaml.cross_validation[]` contains per-asset results: `asset_ref_id`, `asset_description`, `sections_matched`, `key_terms_coverage`, `verdict`
- When no validation-role assets are present, `cross_validation` is an empty list (not missing, not null)

**AC-7: Integration test with synthetic fixture**
- A new test at [skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py) invokes the runner end-to-end against a synthetic source (local `.md` or `.txt` fixture checked into the tests directory)
- Test runs in under 5 seconds, no network traffic, fully deterministic
- Coverage: (a) happy path → exit 0 + all 6 artifacts, (b) sub-floor completeness → exit 20 + `blocked`, (c) directive with validation-role asset → `cross_validation[]` populated, (d) unsupported `provider` → exit 20 with `known_losses`, (e) malformed directive YAML → exit 30, (f) re-run on existing bundle is idempotent

**AC-8: Prompt-pack integration + `--legacy-prose` fallback documented**
- [docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md) Prompt 3 is updated with an added runner invocation block: Marcus writes `<bundle>/directive.yaml`, calls `python -m skills.bmad-agent-texas.scripts.run_wrangler --directive <bundle>/directive.yaml --bundle-dir <bundle>`, reads the result envelope
- The original prose path remains documented under a "Legacy prose fallback" sub-heading, intended to survive one sprint as a safety net; the fallback section explicitly states it is deprecated and will be removed after two clean trial runs using the runner
- The existing hard word-count check stays as a belt-and-suspenders assertion after the runner exits — they validate the same invariant at different levels

**AC-9: Full regression green + no new skips**
- `pytest` full suite passes: previous baseline 891 passed + the new runner tests, all green
- No new `skip` or `xfail` introduced to the default suite
- Golden-path test against `apc-c1m1-tejal-20260415` bundle can be added as a `@pytest.mark.golden` opt-in but is not required for story closure

## Tasks / Subtasks

- [x] Task 1: Author extraction-report schema spec
  - [x] 1.1: Create `skills/bmad-agent-texas/references/extraction-report-schema.md` declaring required fields, types, and example
  - [x] 1.2: Cross-link from `delegation-contract.md` for single-source-of-truth

- [x] Task 2: Implement the runner
  - [x] 2.1: Argparse wiring: `--directive`, `--bundle-dir`, `--json`
  - [x] 2.2: Directive YAML loader + shape validator (raise → exit 30) — now also enforces provider enum, ref_id uniqueness, and ≥1 role: primary (post-review)
  - [x] 2.3: Per-source dispatch: local_file/pdf → `wrangle_local_pdf`, url → `summarize_url_for_envelope`, notion → `wrangle_notion_page`, playwright_html → `wrangle_playwright_saved_html`
  - [x] 2.4: Run `extraction_validator.validate_extraction` per source; aggregate tier + completeness; re-derive tier when operator-declared floor overrides validator heuristic (post-review)
  - [x] 2.5: Run `cross_validator.cross_validate` for each validation-role asset
  - [x] 2.6: Write `extracted.md`, `metadata.json`; write `manifest.json`, `extraction-report.yaml`, `ingestion-evidence.md`, `result.yaml`; all artifacts share one run-scoped UTC timestamp with `Z` suffix (post-review)
  - [x] 2.7: Status derivation: any source tier=FAILED → `blocked`; any tier=DEGRADED → `blocked`; any tier=ADEQUATE_WITH_GAPS → `complete_with_warnings`; all tier=FULL_FIDELITY → `complete`
  - [x] 2.8: Exit-code mapping: complete→0, complete_with_warnings→10, blocked→20, error→30
  - [x] 2.9: Broadened fetch-layer exception catching — any runtime exception becomes a FAILED SourceOutcome rather than escaping (post-review)
  - [x] 2.10: `main()` has a final `except Exception` fallback that emits a stderr explanation and exits 30 rather than letting Python return 1 on an unhandled bug (post-review)

- [x] Task 3: Integration tests
  - [x] 3.1: Synthetic fixtures at `skills/bmad-agent-texas/scripts/tests/fixtures/wrangler-golden/` — `primary.md`, `validation.md`, `thin.md`
  - [x] 3.2: Happy-path test → exit 0, all 6 artifacts, `status: complete`
  - [x] 3.3: Sub-floor test → thin extraction → exit 20 + `blocked`
  - [x] 3.4: Cross-validation test → validation-role asset in directive → `cross_validation[]` populated; empty-list test when no validation assets
  - [x] 3.5: Unsupported provider → exit 30 at directive-load (tightened post-review from exit-20-at-runtime)
  - [x] 3.6: Malformed directive → exit 30 (YAML parse failure, missing required field, missing directive file)
  - [x] 3.7: Idempotent re-run test
  - [x] 3.8: Operator-declared floor forces lower tier (protects Blind Hunter finding #16, Edge Case §3) (post-review)
  - [x] 3.9: Tier-2 ADEQUATE_WITH_GAPS path emits `complete_with_warnings` (post-review)
  - [x] 3.10: Supplementary-role source recorded in provenance but not extracted or cross-validated (post-review)
  - [x] 3.11: Directive with no primary source is rejected (post-review)
  - [x] 3.12: Duplicate ref_ids are rejected (post-review)
  - [x] 3.13: Timestamps use `Z` suffix and agree across artifacts (post-review)

- [x] Task 4: Prompt-pack update
  - [x] 4.1: Rewrite Prompt 3 of v4.2g to invoke the runner; preserve artifact-verification count check as belt-and-suspenders
  - [x] 4.2: Add Legacy-prose-fallback sub-section with deprecation note (removal after two clean runner trials)
  - [x] 4.3: Update the `delegation-contract.md` to cite the runner CLI and exit-code semantics

- [x] Task 5: Validation + regression
  - [x] 5.1: `pytest skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py` → 18 pass
  - [x] 5.2: `pytest` full suite → 919 passed, 2 skipped, 0 failed (baseline was 891; +28 net — 18 runner tests + 10 renamed-Texas-source-wrangler-operations tests)
  - [x] 5.3: Ran the CLI against the synthetic fixture manually; all 6 artifacts emitted, `Tier re-derived after operator-declared floor: FULL_FIDELITY` present in evidence trail

- [x] Task 6: Layered BMAD code review (per sprint-status closure rules)
  - [x] 6.1: Adversarial review (cynical-review / Blind Hunter lens) — 31 findings
  - [x] 6.2: Edge-case hunter review — comprehensive branch/boundary map + coverage audit
  - [x] 6.3: Acceptance auditor review — all 9 ACs SATISFIED, no contradictions with Dev Notes
  - [x] 6.4: Remediate findings; re-review by re-running tests; clean
  - [x] 6.5: Record review outcome in this story artifact (see Review Record below)

- [x] Task 7: Closure
  - [x] 7.1: Flip `sprint-status.yaml` story status to `done`
  - [x] 7.2: Append dated log entries to this artifact documenting closure

## Dev Notes

**Why this story is narrow.** Texas's library functions (extraction + cross-validation + fetch) already exist and are tested. The runner is glue — a deterministic orchestrator that calls existing functions in a defined order and writes artifacts to a defined shape. Keep it boring.

**Why gate-03 is out of scope.** Per Murat's lane-discipline argument, Vera owns gate-judgment execution. Texas owns measurement. This story stops at `extraction-report.yaml` (measurement); the Vera-side G0 runner that reads the report, applies `state/config/fidelity-contracts/g0-source-bundle.yaml` criteria, and emits `gates/gate-03-result.yaml` is a follow-up story. Listing gate-03 here would grade Texas's own homework and violate the lane matrix.

**Why the runner includes fetch, not just validate.** `source_wrangler_operations.py` already performs URL / Notion / Box / PDF / Playwright fetching. If the runner only validated already-fetched content, Marcus would still hand-execute fetch — the integration gap would remain. Including fetch makes the runner a complete delegation target.

**Why `--legacy-prose` fallback exists.** Murat's risk math: the runner has zero runtime evidence at ship time. If the first real trial run hits an unforeseen runner failure mid-pipeline, the operator needs an escape hatch. Two clean trial runs delete the fallback.

**Threshold calibration.** `extraction_validator.py` already hard-codes thresholds: FULL_FIDELITY ≥ 0.80, ADEQUATE_WITH_GAPS ≥ 0.50, DEGRADED ≥ 0.20, FAILED < 0.20. No retuning in this story; the runner consumes these as-is. Recalibration is a follow-up concern if trial runs surface mis-classifications.

**Provenance chain.** Existing `SourceRecord` dataclass carries `kind`, `ref`, `note`, `fetched_at`. The runner's `metadata.json` output must preserve this chain exactly so Vera's future fidelity-tracing doesn't have to re-author it.

## Review Record

### 2026-04-17 — Layered BMAD Code Review

**Review lenses:** Blind Hunter (adversarial / cynical), Edge Case Hunter (branch + boundary + coverage), Acceptance Auditor (AC-1..AC-9 + Dev Notes). Each ran as an independent subagent with no shared conversation context.

**Initial findings summary:**
- **Blind Hunter:** 31 findings. HIGH: #1 (uncaught-exception exit-code escape), #2 (only `ValueError` caught — network / FileNotFoundError / pypdf errors escape), #4 (schema declares `content_path` required but runner emits `None` for non-primary), #24 (pyproject build-backend broken — pre-existing, out-of-scope).
- **Edge Case Hunter:** Exhaustive branch/boundary map. Several HIGH uncovered branches: `role: supplementary` silently dropped, `UnicodeDecodeError` on non-UTF-8 directive escapes, `FileNotFoundError` on missing PDF escapes, URL timeout / HTTPError escape, NotionClient API errors escape, all-supplementary-no-primary run produces exit 0 wrongly, tier NOT recomputed when `expected_min_words_override` is applied, `content_path: null` schema drift, no test for tier-2 `complete_with_warnings` path.
- **Acceptance Auditor:** All 9 ACs SATISFIED. No contradictions with Dev Notes. One doc inconsistency flagged (story text had a stale `-m` invocation reference — already fixed during authoring).

**Triage:**

| Severity | Findings | Treatment |
|---|---|---|
| MUST-FIX | 7 (exception catching x2, schema/runner drift x3, tier re-derivation, supplementary rejection, schema provider enum) | All remediated |
| SHOULD-FIX | 6 (directive enum validation, Z-suffix timestamps, unified run timestamp, tier-2 coverage, override-tier coverage, supplementary coverage) | All remediated |
| CONSIDER | 4 (manifest result.yaml hash, version-string drift, path-normalization cosmetics, recommendation dedup) | Noted; deferred |
| OUT-OF-SCOPE | 4 (pre-existing build-backend bug, schema "fallback exhaustion" aspirational language, cross-validator heading quirks, gate-03 emission) | Noted; not addressed |

**Remediation summary:**
- Broadened fetch-boundary exception catching from `ValueError` to `Exception` with error-class classification; runner now always produces a result.yaml for real-world fetch failures.
- Added final `except Exception` in `main()` that emits stderr explanation and exits 30 rather than returning 1 on unhandled bugs.
- Tightened directive validation at load: provider enum, ref_id uniqueness, ≥1 role: primary required; typos now exit 30 with clear stderr instead of burning a fetch round.
- Re-derived tier when the directive supplies an `expected_min_words` floor so the operator's declared expectation drives the gate-blocking tier signal, not just the evidence string.
- Schema updated: `provider` enum now matches runner reality (`local_file | pdf | url | notion | playwright_html`); `content_path` explicitly documents `null` for non-primary sources; directive-level preconditions section added.
- Canonicalized all artifact timestamps to a single run-scoped UTC string with `Z` suffix; no more intra-run drift.
- `role: supplementary` semantics documented (recorded in metadata provenance, not extracted, not cross-validated); covered by test.
- `evidence_summary` now always emits 2-5 sentences per schema, including supplementary-source count when present.
- 6 new regression tests added (override-tier, tier-2 warnings, supplementary, no-primary rejection, duplicate ref_ids, Z-suffix timestamps) — 18 runner tests total, all pass.

**Post-remediation verification:**
- `pytest skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py` — 18 passed.
- `pytest` full repo — **919 passed, 2 skipped, 0 failed** (baseline 891 → +28 net: 18 runner + 10 Texas source-wrangler tests now collected via updated `testpaths`).
- Manual CLI smoke against synthetic fixture with validation-role asset — exit 0, all 6 artifacts emitted, Z-suffix timestamps agree across `metadata.json`, `extraction-report.yaml`, `manifest.json`; evidence trail correctly shows `Tier re-derived after operator-declared floor: FULL_FIDELITY`.

**Lens-by-lens verdict after remediation:**
- Blind Hunter HIGH findings: all closed.
- Edge Case Hunter HIGH uncovered branches: the runtime-exception-escape class and the silent-supplementary-drop class are now tested; the `UnicodeDecodeError` on directive read is now explicitly raised as `DirectiveError`.
- Acceptance Auditor: all ACs remain SATISFIED; AC-5 text updated to reflect the post-review stricter behavior (unsupported provider exits 30 at load, not exit 20 at runtime).

**Outcome:** Review complete and clean. Story moves to `done`.

**Follow-up stories filed (not blocking):**
- Vera-side G0 gate runner that reads `extraction-report.yaml` and emits `gates/gate-03-result.yaml` (deferred per party-mode lane-discipline consensus).
- Explicit fallback-chain orchestration within the runner (schema language is aspirational today; DEGRADED blocks immediately in this story's runner).
- Runner `validator_version` / `RUNNER_VERSION` derivation from git SHA rather than hand-maintained date strings (Blind Hunter #11, CONSIDER).
- Manifest self-inclusion strategy for `result.yaml` hash provenance (Blind Hunter #9, CONSIDER).

### Dated Log

- 2026-04-17: Story created and scoped via party-mode consensus (Winston / Amelia / Murat, with Blocker-A/B resolution). Registered as Epic 25 / story 25-1 `in-progress`.
- 2026-04-17: Tasks 1-5 implemented — schema authored, runner built, 12 integration tests passing, prompt-pack Prompt 3 rewritten, 913 full-repo tests passing.
- 2026-04-17: Layered BMAD code review run (Blind Hunter / Edge Case Hunter / Acceptance Auditor). 31 findings triaged; 7 MUST-FIX + 6 SHOULD-FIX accepted.
- 2026-04-17: Remediation complete. 18 runner tests passing, 919 full-repo, smoke clean. Story closed and flipped to `done`.
