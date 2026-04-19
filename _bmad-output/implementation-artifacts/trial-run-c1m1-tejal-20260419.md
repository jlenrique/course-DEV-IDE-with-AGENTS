# Trial Run — APC C1-M1 Tejal (2026-04-19)

**Opened:** 2026-04-19
**Operator:** Juanl
**Playbook:** [docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md)
**Branch:** `trial/2026-04-19`
**Session-anchor head:** `ca966de` (session-wrapup: Epic 33 closed; trial/2026-04-19 baseline ready)

## Scribe Contract

Operator drives every step — HIL gate judgments, rework decisions, source authority decisions. Marcus acts as orchestrator + scribe:
- Executes prescribed CLI commands per pack and logs outcomes (command, exit code, artifact paths, decision + rationale).
- Records conformance gaps and operator corrections in §Conformance Observations below.
- Does not approve gates unilaterally or write to production state outside canonical workflow paths.

## Run Config

- **Run ID:** `C1-M1-PRES-20260419`
- **Source bundle:** `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419-motion/`
- **Primary source:** `course-content/courses/tejal-APC-C1/C1M1Part01.md` (Part 1 only — "The Call: Setting the Stage & Chapter 1")
- **Validation sources:** PDF + DOCX (cross-confidence)
- **Supplementary:** APC Content Roadmap.jpg (orientation only)
- **Experience profile:** `visual-led` (60/25/15)
- **Cluster density:** `default`
- **Motion enabled:** `true` · 125 credits · pro tier
- **Double dispatch:** `false` (single-dispatch — cluster debut run)
- **Quality preset:** `production`
- **Requested content type:** `narrated-lesson-with-video-or-animation`
- **sha256 run-constants:** `24dbf820b88348e54c9222edc377d5277e387f6702500cf285b37c21d5f49ca8`

## Session Log

_(append-only; one entry per step or significant event)_

### 2026-04-19 — Session START

- BMAD session protocol run. Branch confirmed `trial/2026-04-19`. Working tree clean (CRLF line-ending artifacts only — no content changes). Commits verified: `ca966de` / `8b70076` / `2ba1e32` ✓
- Prior run `C1-M1-PRES-20260415` declared abandoned by operator.
- HUD launched: `reports/run-hud.html` — 33 steps confirmed current against `state/config/pipeline-manifest.yaml`.

### 2026-04-19 — Step 01: Activation + Preflight

- `app_session_readiness --with-preflight`: **PASS** (7 checks, tools ready=10, MCP: gamma/canvas-lms/notion/scite/consensus)
- `venv_health_check`: **PASS**
- `emit_preflight_receipt --with-preflight --motion-enabled`: **PASS** (written to bundle)
- Bundle artifact count: **2/2** ✓ (`run-constants.yaml` + `preflight-results.json`)
- Activation receipt issued — all 6 fields ✓
- Operator GO received.

### 2026-04-19 — TRIAL PAUSED at Step 04A

**Pause reason:** `Facade.run_4a()` requires a production `intake_callable` connecting the per-unit ratification loop to the operator interface. No production callable exists — only test stubs. Running the trial forward with a fixture-contaminated lesson plan log would produce meaningless results for the Lesson Planner functions, which are the entire point of this trial. Steps 01–04 completed cleanly. Trial resumes after gap-filling story is built and verified.

**Resume condition:** Production `intake_callable` wired, lesson-plan-log.jsonl reset/clean, Step 04A re-run producing correct scope_decision.set / plan.locked / fanout events for our actual 5 in-scope plan units.

### 2026-04-19 — Step 03: Ingestion + Evidence Log — PAUSED (fix-in-flight)

- directive.yaml authored: MD primary (src-001), PDF validation (src-002), DOCX validation (src-003), JPG supplementary (src-004).
- First Texas invocation: exit 30 (directive error) — `md` provider not in runner's accepted set. Fixed to `local_file` for MD + DOCX + JPG; re-ran.
- Second Texas invocation: exit 10 (complete_with_warnings).
- **src-001 (MD primary): quality_tier 2, structural_fidelity LOW, 1,509 words.** Root cause confirmed: Notion-exported MD file has backslash-escaped syntax (`\#`, `\*\*`, `\-`) + HTML entities (`&#x20;`). `local_text_read` reads raw — no unescape applied.
- **Cross-validation correctly flagged the issue:** 34% key-term coverage + 0.20 word-count ratio vs PDF/DOCX validation sources. System worked as designed.
- src-002 (PDF): quality_tier 1, 7,586 words, 24 headings — clean extraction.
- src-003 (DOCX): quality_tier 2, 7,298 words, 69 headings — acceptable.
- src-004 (JPG): 68,847 "words" of binary garbage — expected; supplementary role, does not affect extracted.md.
- Artifact count: 10/10 ✓ (PowerShell Get-ChildItem).
- **HOLD DECISION:** Operator directed hold at Step 03. Do NOT proceed to Step 04 until dev agent delivers MD provider fix (backslash-unescape + HTML entity decode + `md` wired into runner dispatch). Re-run Texas with original `md` provider directive once fix lands.
- Fix-in-flight spun off to dev agent. See conformance observations for full brief.

### 2026-04-19 — Step 02A: Operator Directives

- Poll opened: 22:00:00 UTC. Submission received: 22:03:17 UTC (valid — 17s past 3-minute hold).
- Defaults surfaced from prior run `C1-M1-PRES-20260415` (apc-c1m1-tejal-20260415/operator-directives.md) — operator accepted all three categories as-is.
- `operator-directives.md` written to bundle.
- Artifact count: **3/3** ✓ (PowerShell Get-ChildItem — prescribed command used).
- Operator confirmation received.

### 2026-04-19 — Step 02: Source Authority Map

- Source map produced from scratch (greenfield run).
- Initial map revised mid-step after operator corrections (see §Conformance Observations).
- Final map: 4 sources — MD (primary), PDF (validation), DOCX (validation), JPG (supplementary).
- `run-constants.yaml` updated to reflect revised source list. New sha256: `24dbf8...ca8`.
- Operator approval received.

---

## Conformance Observations

_(Marcus self-assessment of pack conformance gaps, recorded per operator instruction. Append-only.)_

### Step 01 — Three invocation-form deviations

1. **`app_session_readiness` invocation:** Pack specifies `.\.venv\Scripts\python.exe scripts/utilities/app_session_readiness.py --with-preflight`. Marcus used `python -m scripts.utilities.app_session_readiness --with-preflight --json-only` — wrong Python reference, module form vs script path, undocumented `--json-only` flag added.
2. **`venv_health_check` invocation:** Pack specifies `.\.venv\Scripts\python.exe -m scripts.utilities.venv_health_check`. Marcus used bare `python` — same root issue as above.
3. **Artifact verification method:** Pack specifies `Get-ChildItem [BUNDLE_PATH] -File | Measure-Object | Select-Object -ExpandProperty Count` (PowerShell). Marcus used Python `Path.iterdir()` count instead.
4. **`emit_preflight_receipt` module path:** Pack originally referenced hyphenated form (`emit-preflight-receipt`) which failed with bare `python` — workaround used. Fix-in-flight spun off to dev agent (rename + generator template update + manifest gate promotion).

**Pattern:** All Step 01 deviations share a root cause — Marcus did not use `.\.venv\Scripts\python.exe` explicitly as the pack prescribes. Functionally correct outcomes; audit trail diverged from spec. Dev agent fix-in-flight in progress.

### Step 03 — Six findings

1. **Directive authored with wrong provider values (avoidable exit-30):** Marcus wrote `provider: "md"` and `provider: "docx"` without first verifying the runner's accepted provider set. Pack example clearly shows `local_file | pdf | url | notion | playwright_html`. Should read delegation contract provider list before authoring directive, not after failure. Caused unnecessary exit-30 iteration and a fix-in-flight.
2. **`result.yaml` not explicitly read into production envelope:** Pack 3.c says "read this into the production envelope." Marcus reported from stdout YAML — functionally identical but not the prescribed method. File read of `result.yaml` should be explicit.
3. **Word count not recorded in `ingestion-evidence.md`:** Pack 3.d.4 requires: "Record the actual word count in `ingestion-evidence.md` alongside the page count for audit." Marcus ran the PowerShell check and reported the number but never wrote it into `ingestion-evidence.md`. Audit trail is incomplete for this step.
4. **`pages_total` not set in directive:** Pack 3.d.2 requires comparing word count against `metadata.json` page count (page_count × 250 floor). No page count was available because `pages_total` was not set in directive for the MD source. Belt-and-suspenders comparison was therefore incomplete for the primary source.
5. **Pack inconsistency (9 vs 10) not surfaced:** Section 3.e heading says "expected file count: 9" but body text immediately below says "total 10 files." Marcus accepted 10 as correct without flagging the discrepancy. This is a pack error requiring a dev agent fix.
6. **Cross-validation proved its value (positive finding):** PDF + DOCX validation sources correctly detected degraded MD extraction (34% key terms, 0.20 word ratio) on first pass. Multi-source validation architecture earned its keep. Fix-in-flight spun off; re-run confirmed clean extraction (tier 1, high fidelity, markdown_unescape extractor).

1. **`md` provider not wired into runner dispatch:** Runner's accepted provider set (line ~207) excludes `md` despite it being registered as `ready` in the provider directory. Fallback to `local_file` → `local_text_read` bypasses backslash-unescape. Fix-in-flight spun off.
2. **Cross-validation proved its value:** PDF + DOCX validation sources correctly detected the degraded MD primary via 34% key-term coverage and 0.20 word-count ratio. The multi-source validation architecture earned its keep on this very step.

### Step 02 — Two substantive content gaps

1. **Run-constants accepted uncritically:** Initial source map reflected `run-constants.yaml` at face value (PDF primary, JPG only optional context) without first scanning the source directory to check correctness. Operator had to surface the DOCX and MD file's relevance. Marcus should proactively reconcile run-constants against the actual source directory before producing the map, and surface candidate sources not listed in run-constants for operator role-assignment.
2. **DOCX misclassified as excluded:** Marcus labelled the DOCX "excluded to avoid double-extraction" — plausible-sounding but wrong. The correct role is `validation` (cross-confidence against primary). Operator corrected this. Marcus should recognise a same-content DOCX alongside a PDF as a canonical validation candidate without prompting.

**Net:** Structurally conformant (all 8 fields present, stopped and waited). Intellectually incomplete on first pass. HIL operator approval loop caught both errors — confirming gate value. Deferred inventory updated with "best-available-medium selection" follow-on (Epic 27/15 candidate).
