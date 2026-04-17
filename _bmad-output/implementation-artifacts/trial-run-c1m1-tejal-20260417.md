# Trial Run — APC C1-M1 Tejal (2026-04-17)

**Opened:** 2026-04-17
**Operator:** Juanl
**Playbook:** [docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md)
**Branch:** `dev/epic-26-scaffold-v02`
**Session-anchor head:** `5e073cf` (trial-readiness wire-up)

## Scribe Contract

Operator drives every step — CLI, HIL gate judgments, rework decisions. Claude acts as scribe + on-call support:
- Logs operator-reported actions and outcomes (timestamp, command, exit code, artifact paths, decision + rationale).
- Provides expert interpretation + routing when the operator surfaces an issue.
- Does not execute CLI, approve gates, or write to production state on operator's behalf.

## Run Config

_(populated as the prompt pack's Prompt 1 assigns them)_

- **Run ID:**
- **Source bundle:**
- **Experience profile:**
- **Cluster density:**
- **Motion enabled:**
- **Quality preset:**
- **Requested content type:**

## Session Log

_(append-only; one entry per operator action)_

### 2026-04-17 — Trial opened

- Pre-trial full-repo Audra L1 sweep: **CLEAN**. Report: [reports/dev-coherence/2026-04-17-1900/harmonization-summary.md](reports/dev-coherence/2026-04-17-1900/harmonization-summary.md)
- Structural walk motion dry-run: **READY, 0 critical findings**. Report: `reports/structural-walk/motion/structural-walk-motion-dry-run-20260417-191717.md`

### 2026-04-17 — Marcus invoked by operator

- Default Claude Code agent declined operator's pre-run checklist invocation (said Marcus was not registered in the harness). After a wait, Marcus loaded and responded.
- Marcus preflight verdict: pre-flight constants **clean** for 20260415 bundle's `run-constants.yaml`. EXPERIENCE_PROFILE=visual-led, MOTION_ENABLED+125-credit budget, slide_mode_proportions canonical, CLUSTER_DENSITY=default. Three items carried forward (Irene packet, HIL emphasis, post-run doc) — downstream gate enforcement.
- **Marcus flagged stale-context discrepancy:** DB shows `C1-M1-PRES-20260409` as active; v4.2 pack run-constants and bundle on disk reference `C1-M1-PRES-20260415`.
- Marcus asked two operator questions before Prompt 1:
  1. Confirm target run — 20260415 (fresh) or continue 20260409?
  2. Update coordination DB to register new run + close 20260409, or leave 20260409 active intentionally?

### 2026-04-17 — Scribe investigation (support for operator decision)

Reviewed both candidate bundles + coordination DB:

- **20260415 bundle** (`apc-c1m1-tejal-20260415/`): has `run-constants.yaml`, `extracted.md`, `irene-packet.md`, `metadata.json`, gates dir with `gate-04-result.yaml`. **Gate-04 status: FAIL** — "Extraction too thin — 30-line stub from 24-page PDF; 120 words vs 3000-word floor." Bundle is unusable as a trial starting point.
- **20260409-motion bundle** (`apc-c1m1-tejal-20260409-motion/`): fully scaffolded — `assembly-bundle/`, `authorized-storyboard.json`, `dispatch-params.json`, `elevenlabs-dispatch-preview.json`, `gamma-export/` + `gamma-export-B/`, `gary-diagram-cards.json`, `gary-outbound-envelope.yaml`, `motion/`, `pass2-envelope.json`, `storyboard/`, etc. No `gates/` dir. `requested_content_type: narrated-deck-video-export` (legacy name; motion_enabled=true → `narrated-lesson-with-video-or-animation` via `select_workflow_variant`).
- **Coordination DB `production_runs` table (timeline):**
  - 20260403 — cancelled
  - 20260404 — cancelled (superseded by 20260406)
  - 20260406 — **completed** — stopped at Storyboard B HIL review 2026-04-08
  - 20260409 — **active** (DB status) — re-run with double-dispatch, deliberate variants, 15 slides, 125-credit motion; last DB update 2026-04-09
  - 20260415 — NOT in DB. Only on disk; G4 failed.
- **Critical observation:** The v4.2 pack (post-commit `5ffc76b`) requires 4 new workflow stages (creative-directive, cluster-prompt-engineering, cluster-dispatch-sequencing, cluster-coherence). The 20260409 bundle predates those stages — running the current pack against it would either skip them or hit integration gaps.

### 2026-04-17 — Operator decision

Operator instruction to Marcus: **fresh run**. Update the coordination DB accordingly; close the prior run (`C1-M1-PRES-20260409`). Operator is in charge of run-level decisions for this trial.

### 2026-04-17 — Marcus DB update + new run registered

- `C1-M1-PRES-20260409` → **cancelled** (baton closed, no stages had run)
- `C1-M1-PRES-20260415` → **active/planning** — tracked, production preset, double-dispatch, motion-enabled @ 125 credits (pro tier)
- Cross-run lineage registered: 20260409 → 20260406 → 20260404 → 20260403
- Context paths scaffolded at `state/config/runs/C1-M1-PRES-20260415/`
- Preflight alignment confirmed: DB ↔ bundle ↔ canonical profile all agree — visual-led, default cluster density, motion budget.

### 2026-04-17 — Marcus offers next-move options

Marcus presented operator with two choices before moving:

1. **Issue Prompt 1** (source intake + scope confirmation with Texas) to kick off the run.
2. **Source-prompting pass first** — Notion / Box Drive check for anything Texas should see beyond the primary PDF + roadmap asset.

### 2026-04-17 — Operator instruction to Marcus

"Yes. Work with Texas to get our sourcing done right."

### 2026-04-17 — Marcus source-prompting execution

Marcus loaded his source-prompting capability + Texas delegation-contract + source-interview, then executed folder scan per Texas's source-interview protocol.

**Texas `run_wrangler.py --help` hit a Windows cp1252 encoding error** (UnicodeEncodeError on `\u2194` character at position 139). This is a latent Texas CLI defect — `--help` output crashes on Windows default stdout without `PYTHONIOENCODING=utf-8`. **Flag for post-trial remediation story** (same defect class as scaffold v0.2's V2-1..V2-3 scaffold hardening; Texas's CLI needs the same `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` guard we added to `init_sanctum.py:399-403`).

**Marcus surfaced 3 findings + proposed Texas directive:**

- **⚠️ Path mismatch in `run-constants.yaml:4`:** declares flat `course-content/courses/APC C1-M1 Tejal 2026-03-29.pdf` but actual files live under `course-content/courses/tejal-APC-C1/`. Same for roadmap. Needs correcting.
- **⚠️ Freshness flag:** DOCX modified 2026-04-16 21:25 (yesterday); PDF is 2026-03-29 (2.5 weeks older). DOCX may carry later edits the PDF doesn't.
- **Materials scan in `course-content/courses/tejal-APC-C1/`:**
  - Primary candidate: `APC C1-M1 Tejal 2026-03-29.pdf` (268 KB)
  - Validation candidates: `APC C1-M1 Tejal 2026-03-29.docx` (55 KB, NEWER), `C1M1Part01.md` (11 KB, Part 1 only, modified today)
  - Supplementary: `APC Content Roadmap.jpg`, `Intro to Innovative Leadership in Healthcare 2026.pptx` (12 MB course-level deck)
  - Style exemplars (CD/Gary, not Texas): 2 VISUAL-style EXEMPLAR PNGs + 4 CREATIVE slide-treatment PNGs + 1 differential-diagnosis screenshot

**Marcus's proposed Texas directive:**
- `src-001` primary: PDF (canonical per constants)
- `src-002` validation: MD (Part 1 only)
- `src-003` validation: DOCX (full-module cross-check) — contingent on operator confirming PDF canonical despite newer DOCX
- Quality gate: `min_completeness: 0.80`, `structural_fidelity: true`
- Exemplars + PPTX + roadmap **routed to CD/Gary, not Texas**

**Marcus's 4 questions before dispatch:**

1. **Path fix:** update `PRIMARY_SOURCE_FILE` and `OPTIONAL_CONTEXT_ASSETS` in `run-constants.yaml` to use the `tejal-APC-C1/` subpath. OK?
2. **Freshness:** PDF canonical (ignore later DOCX edits), or DOCX canonical (swap primary)?
3. **External sources:** Notion pages, Box Drive folders, URLs to add?
4. **Exemplar handling:** hold the 6 visual exemplars aside for CD briefing later — confirm that's the intent.

### 2026-04-17 — Marcus update: paths fixed, Notion blocked

- **Q1 path fix: ✅** — `run-constants.yaml` now points at `tejal-APC-C1/` subpath for primary + roadmap.
- **Q3 Notion fetch: ❌ 404** — MCP integration authenticated at workspace level but not granted to page `24718552-3a39-806d-b1d7-c55ae9e2e801` (sharing issue, not auth). Marcus offered 3 paths:
  1. Grant integration access in Notion → re-fetch live (clean path, proper cross-validation).
  2. Export Outline page to MD/PDF → drop in `tejal-APC-C1/` → Marcus adds as `local_file` validation asset. Fast, but snapshot not live.
  3. Skip for this run if Outline is scaffolding notes only. PDF + DOCX + MD triangle already strong.
- **Draft Texas directive** (YAML structure) presented — 4 sources:
  - `src-001` PDF (primary, canonical)
  - `src-002` MD (validation, Part-1 only)
  - `src-003` DOCX (validation, full-module; freshness flag noted in `known_issues`)
  - `src-004` JPG roadmap (supplementary) — **Marcus flagged: format enum mismatch**.
- **New question (Q5):** Include `src-004` JPG in Texas manifest as supplementary (non-extractable, downstream ref only), or exclude from Texas directive and route separately to CD/Irene?

- Awaiting operator answers on Q2 (freshness), Q3 (Notion 1/2/3), Q5 (image handling).

### 2026-04-17 — Marcus drill on image handling + A/B recommendation

Marcus confirmed against `run_wrangler.py:228-244`: `.jpg` with `provider: local_file` falls through to `read_text_file()` → binary decode error → FAILED extraction outcome recorded in `metadata.json`. Supplementary role means no cross-validation runs, but the FAILED badge still lands in the extraction report (noise without signal).

**Marcus's two cleaner options:**
- **A. Route roadmap outside Texas's directive (Marcus's recommendation):** already declared as `OPTIONAL_CONTEXT_ASSETS` in `run-constants.yaml:5`; flows through Marcus-owned context envelope to CD → Irene → Gary. Texas directive stays focused on text extraction, report stays clean.
- **B. Include anyway, accept FAILED badge:** single unified manifest, but noisy report that requires mental filtering.

**Scribe observation surfaced to operator:** this exposes a genuine architectural gap in Texas's contract (no first-class visual-source role). Pre-Texas-runtime (Story 25-1, 2026-04-17), image sources flowed through the ad-hoc source-prompting loop inside Marcus. Texas formalized extraction as a contract-gated runtime step and accidentally narrowed the input surface. **Backlog story stub opened:** [_bmad-output/implementation-artifacts/texas-visual-source-gap-backlog.md](_bmad-output/implementation-artifacts/texas-visual-source-gap-backlog.md). Three options (A: extend Texas with image provider, B: sibling visual-wrangler, C: explicit reject + documented escape hatch) laid out for party-mode consensus post-trial.

**Scribe recommendation for THIS trial:** proceed with Marcus's Option A — the escape hatch is architecturally clean (run-constants already carries the roadmap), doesn't require mid-trial code changes, and the backlog story captures the gap for proper post-trial remediation.

### 2026-04-17 — Operator scope direction on Texas gap

> "We'll extend Texas capabilities in a new story either as directly extending the runner or adding another. As a 'wrangler' Texas must be savvy at finding and handling anything and everything that might be out there or be presented. But that doesn't mean there can't be very deliberate routing of one source type or another for efficient processing by Texas."

Backlog story updated: [texas-visual-source-gap-backlog.md](texas-visual-source-gap-backlog.md) now records the operator principle — Texas owns the intake surface; internal deliberate routing to specialist extractors is allowed and encouraged; Option C (reject-with-error) is withdrawn as it would violate the wrangler identity.

- For this trial: Option A (route roadmap via run-constants context envelope) stands.

### 2026-04-17 — Texas dispatch + extraction result (exit 10, complete_with_warnings)

Marcus wrote directive to `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260415/texas-directive.yaml` (3 sources: PDF primary, MD Part-1 validation, DOCX full-module validation; image route-around applied). Invoked `skills/bmad-agent-texas/scripts/run_wrangler.py`. Exit code 10 = `complete_with_warnings`.

**Per-source results:**

| Source | Role | Tier | Words / Lines / Headings | Extraction | Cross-val |
|---|---|---|---|---|---|
| src-001 PDF | primary | 1 (Full Fidelity) | 7,586 / 834 / 24 | ✅ PASS | — (is primary) |
| src-002 MD (Part 1) | validation | 2 | 1,500 / 194 / 0 | PASS w/ gaps | ✅ Strong: 10/10 sections, 99% key terms |
| src-003 DOCX | validation | 2 | 2,044 / 1,522 / 0 | PASS w/ gaps | ❌ Failed: 2% key-term overlap |

Primary extraction matches prior-run baseline (~7,586 words vs expected ~6,000 = 24 pages × 250 wpp; ±1% consistency). 5 LOs captured, slide-by-slide structure preserved, M&M-of-Innovation terminology intact. Gate met (`min_completeness: 0.80` cleared at 15.86×; structural fidelity medium — acceptable for narrative content).

**src-002 MD cross-val:** 10/10 sections matched, 99% key-term coverage (81/82); single missing term `"m\&m of innovation"` — ampersand-encoding artifact, not substantive.

**src-003 DOCX cross-val: FAILED = Texas extractor defect, NOT content divergence.** Marcus's diagnosis at `run_wrangler.py:228-244`: `local_file` handler has PDF-specific extraction but everything else (including `.docx`) falls through to `read_text_file()` — a plain-text read against a DOCX ZIP-of-XML container, producing binary garbage. Confirmed: the reported "missing key terms" are literal unicode replacement characters and ZIP-compressed byte sequences (`]\u0307\uFFFD\\...`, etc.), not real vocabulary.

**This is a contract-vs-code drift, not just a gap.** `skills/bmad-agent-texas/references/transform-registry.md` line 19 advertises `python-docx` as the default DOCX extractor, but `run_wrangler.py` doesn't invoke it — it falls through to `read_text_file()`. The registry is making a promise the code doesn't keep. **Higher severity than the image-source gap** — updating backlog story accordingly.

**Marcus's next-move options for operator:**
1. Proceed to Prompt 2 (Irene Pass 1 handoff packet build) — Marcus's recommendation.
2. Pre-convert DOCX → MD outside Texas, drop in bundle, re-run for clean cross-val (~2 min).
3. Pause, review extracted.md before advancing.

**Unused assets parked for downstream context envelopes:** `APC Content Roadmap.jpg` (CD/Irene/Gary); 6 visual exemplars (CD creative-frame briefing at Prompt 4).

- Awaiting operator decision.

### 2026-04-17 — Operator confirmed Option 1 (proceed to Prompt 2) implicitly; scribe flagged prompt-pack order gap

Operator recognized that Texas source-wrangling ran ahead of formal Prompt 1. Prompt-pack sequencing calls for: Run Constants (persisted as `run-constants.yaml`) → Initialization Instructions → Execution Rules (bound to Marcus) → Prompt 1 (Activation + Preflight Contract Gate) → explicit GO → subsequent prompts. We had persisted run-constants.yaml and run Texas source-wrangling, but:

- **Execution Rules never bound to Marcus** — SPOC, Artifact Verification Protocol, Motion-first ordering unpasted. Highest-priority gap because Artifact Verification Protocol is the defense against agent write-confirmation-lies.
- **Prompt 1 required commands never ran** — `app_session_readiness.py --with-preflight`, `emit-preflight-receipt --with-preflight --motion-enabled`, `venv_health_check`, double-dispatch compatibility confirm. Existing `preflight-results.json` is stale (2026-04-15 21:11, from the prior failed run).
- **Stale gate verdicts in bundle** — `gates/gate-01-result.yaml` and `gates/gate-04-result.yaml` are FAIL records from the prior failed run; must be cleared for this fresh run.
- **Stale `operator-directives.md`** (2026-04-15 21:45) — from prior attempt; needs review + possible rewrite.
- **No explicit GO** from operator yet.

### 2026-04-17 — Catch-up message composed for Marcus

Operator-voice consolidated message drafted covering: Execution Rules binding (SPOC + Artifact Verification Protocol + Motion-first ordering + repo-local interpreter convention), formal Prompt 1 directive (6 receipt items + 3 required commands + double-dispatch compatibility check), required write of fresh `preflight-results.json`, deterministic file-count verification against bundle, stale-artifact remediation (clear gates/ verdicts, review operator-directives.md, leave irene-packet.md for Pass-1 overwrite), gate rule + wait-for-GO contract. Operator to paste; awaiting Marcus's Prompt 1 receipt.

### 2026-04-17 — Marcus Prompt 1 execution: HALT on validator fail (good halt)

Marcus bound Execution Rules and executed Prompt 1. Performed the stale-artifact remediation first:
- ✅ Cleared `gates/gate-01-result.yaml` and `gates/gate-04-result.yaml` (prior-run FAIL verdicts removed).
- ✅ Reviewed `operator-directives.md`: still correct for this run's constants (visual-led + default cluster + motion-enabled + double-dispatch). No rewrite needed.

Preflight command results:
- ✅ `venv_health_check` PASS — Python 3.13.6, core imports OK.
- ✅ `app_session_readiness.py --with-preflight` PASS (without `--bundle-dir`; bundle_run_constants skipped as optional).
- ❌ `emit-preflight-receipt.py --with-preflight --motion-enabled --bundle-dir ...` **FAIL** — validator `bundle_run_constants` reported "Missing or empty required string field: run_id".

**Marcus halted per gate rule and root-caused.**

**Root cause:** Pack-doc-vs-validator schema drift.
- Validator `scripts/utilities/run_constants.py:96-99` performs case-sensitive `data.get("run_id")` and expects lowercase snake_case keys + nested `motion_budget:` block (per prior working bundles: 20260409, 20260406-motion).
- Pack doc `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` (lines 22-37) displays constants UPPERCASE flat: `RUN_ID`, `MOTION_BUDGET_MAX_CREDITS`, etc.
- Operator wrote `run-constants.yaml` following pack-doc presentation → uppercase flat → validator rejects.
- This is a **pack-doc defect**, not operator error and not a validator issue. Prior runs avoided the trap by copying from prior-bundle templates.

**Marcus's proposed fix:** rewrite `run-constants.yaml` to canonical schema (lowercase snake_case, nested `motion_budget:` block). Values preserved; no semantic change. Adds optional `schema_version`, `frozen_at_utc`, `frozen_note` anchors per 20260406 precedent. This is schema compliance repair, not a value change — does not violate the "do not change run constants mid-run" rule.

**Marcus explicitly offered alternative:** change validator to accept uppercase (code change out of his lane). Flagged as slower path since lowercase is established precedent across every working prior run.

**Bundle file-count check:**
- Bash equivalent: 12 entries at bundle root (11 files + `gates/` dir), gates/ now empty post-cleanup.
- Pack Prompt-1 minimum: 2. Actual: higher due to Texas artifacts already in place. Expected and noted.

**Marcus waiting on operator approval for the rewrite.**

## Gate Outcomes

_(filled as each gate clears)_

| Gate | Status | Decision | Evidence | Timestamp |
|------|--------|----------|----------|-----------|
| G0 Source Bundle | — | — | — | — |
| G1 Lesson Plan | — | — | — | — |
| G2 Slides | — | — | — | — |
| G2M Motion Designation | — | — | — | — |
| G3 Narration | — | — | — | — |
| G4 Final Package | — | — | — | — |

## Issues Surfaced

_(append when issues arise)_

## Closure

_(filled at trial end)_
