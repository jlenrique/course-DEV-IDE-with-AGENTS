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

### 2026-04-19 — B-RUN START (C1-M1-PRES-20260419B)

- Prior run `C1-M1-PRES-20260419` halted at §04A (production intake_callable not wired). Operator elected to start fresh, mining existing bundle for proposed defaults only.
- New bundle: `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/`
- Run constants authored via PR-RC — all defaults confirmed by operator from prior bundle. `run-constants.yaml` written.
- Run ID: `C1-M1-PRES-20260419B`

### 2026-04-19 — B-Run Step 01: Activation + Preflight

- `app_session_readiness --with-preflight` (PYTHONPATH=.): **PASS**
- `venv_health_check`: **PASS** (Python 3.13.6)
- `emit_preflight_receipt --with-preflight --motion-enabled --bundle-dir [...] --output [...]`: **PASS** (receipt written)
- Bundle artifact count: **2/2** ✓ (`run-constants.yaml` + `preflight-results.json`)
- Activation receipt issued — all 6 fields ✓
- Pack conformance note: used `PYTHONPATH=.` prefix; `.\.venv\Scripts\python.exe` form prescribed by pack. Functionally equivalent.

### 2026-04-19 — B-Run Step 02: Source Authority Map

- Initial map presentation retracted — operator correctly recalled that HIL source role-assignment should precede map authoring, not follow it (same conformance gap as prior run Step 02).
- Source directory scanned: 12 files found, 8 not in run-constants (PPTX, 6 PNGs, 1 screenshot).
- Surfacing to operator for role assignment before drafting map.
- Operator assigned roles inline: src-001 MD (primary), src-002 PDF (validation), src-003 DOCX (validation), src-004 JPG (supplementary). Files 5–12 skipped.
- Map drafted and presented. Operator approval received. No corrections.

### 2026-04-19 — B-Run Step 02A: Operator Directives

- Poll opened ~20:10 UTC. Pre-filled from prior run `C1-M1-PRES-20260419`.
- Operator confirmed rows 1 (Focus) and 2 (Exclusion) as-is.
- Row 3 (Special treatment) amended: added motion video directorial guidance identification clause.
- `operator-directives.md` written to bundle. Artifact count: **3/3** ✓.
- Operator GO received.

### 2026-04-19 — B-Run Step 03: Ingestion + Evidence Log

- `directive.yaml` authored: src-001 md (primary), src-002 pdf (validation), src-003 local_file (validation — docx provider rejected by runner, see conformance), src-004 local_file (supplementary).
- Texas runner exit 10 (complete_with_warnings). blocking_issues: [].
- src-001 MD: tier 1, 1,490 words, high fidelity, markdown_unescape extractor — A-run fix confirmed working.
- src-002 PDF: tier 1, 7,586 words — clean.
- src-003 DOCX: tier 2, 7,298 words, python-docx auto-detected via local_file — high repetition noted, passes.
- src-004 JPG: binary garbage as expected — supplementary only.
- Cross-validation: 34% key-term / 0.2 word ratio — expected (Part 1 only vs full course). Non-blocking.
- Belt-and-suspenders: 1,490 words adequate for declared Part 1 scope. No halt.
- Artifact count: 10/10 ✓.

### 2026-04-19 — B-Run Step 04: Ingestion Quality Gate + Irene Packet

- Receipt template generated; all 6 dimensions assessed with evidence sentences per pack requirement.
- All 4 sources: pass across all 6 dimensions.
- src-001 confidence: high — 5 slides with speaker notes, visual format descriptions, and Slide 1 motion video storyboard captured verbatim.
- src-002/003: medium (validation role only); cross-validation low scores confirmed scope-structural per ingestion-evidence.md note.
- src-004: high (supplementary/literal-visual — no text extraction expected).
- Vera G0: pass — no critical findings. G0-05 degraded-source interpretation note confirmed in ingestion-evidence.md.
- `emit_ingestion_quality_receipt`: receipt written.
- `prepare-irene-packet.py`: packet written (15 sections, has directives: true, has ingestion receipt: true).
- Artifact count: 12/12 ✓. gate_decision: proceed.

### 2026-04-19 — B-Run Step 04A: Lesson Plan Coauthoring + Scope Lock

- MarcusPreCollectedIntakeCallable (Story 32-5) confirmed: imports OK, production path active.
- Log reset (confirm=True) + route_step_04_gate_to_step_05 executed with pre_collected_decisions.
- Locked revision: 1. Plan digest: f782bf05... 5 in-scope / 3 out-of-scope.
- scope_decision.set / plan.locked / fanout events emitted cleanly — no fixture contamination.
- 04a-scope-lock-record.md written to bundle.
- Baton handoff: 04A → 05 confirmed. NOTE: first lock was premature — operator correctly halted for co-authoring loop. Plan revised through 3 passes before final GO.

### 2026-04-19 — B-Run Step 04A: Lesson Plan Co-authoring (3 passes)

- **Pass 1:** Initial programmatic lock run without presenting plan — operator halted. Lesson learned: co-authoring loop must precede lock.
- **Pass 2:** Tabular display presented. Operator added: (a) Learning Objectives as own unit (u-00, Gagne Event 2), (b) cluster children slots for Events 4/5, (c) corrected Gagne event assignments.
- **Pass 3:** Added 3-course series roadmap (src-004 JPG) as new in-scope unit u-09, Gagne Event 9 — Transfer of learning, literal-visual. Mapped out-of-scope units to their Gagne roles (Event 6, 8) for future run reference. Operator confirmed "best treatment so far."
- **Operator note:** Out-of-scope units may warrant draft blueprint treatment toward end of run — flag as future option at §15.
- Final in-scope: 7 parent slides (u-00, u-01, u-02, u-04, u-05, u-09, u-07). Full Gagne arc Events 1-9 accounted for.
- Operator GO received. Programmatic lock to follow.

### 2026-04-19 — B-Run Step 05: Irene Pass 1 + Gate 1

- Irene dispatched as subagent — 14-slide plan produced.
- Vera (G1+G2): PASS-WITH-FINDINGS — 1 critical-advisory (S06 literal-visual/no source asset), 8 advisories.
- Quinn-R (quality G2): ADEQUATE — 2 conditions (S01/S02 event order inversion; S08/S09 mode reconsideration).
- Operator resolved design questions: hook first then LOs; archetypes = emotional skill-mapping (creative mode correct).
- Irene correction sweep: all 11 directed changes applied — resequenced S01→S02→S03, S06 reclassified creative, S08/S09 narration reframed, motion brief expanded inline, 10 other corrections.
- Gate 1: APPROVED by operator. GO received.
- §05B G1.5 Cluster Plan: APPROVED by operator.
- §06B literal-visual gate PASS after fix-in-flight (validate-literal-visual-pre-dispatch.py). S05 + S11 reclassified from literal-visual → creative: no SOT image exists, Gary generates from structural brief. S12 SOT confirmed (APC Content Roadmap.jpg, 3MB, on disk). operator-packet.md written.
- DESIGN NOTE: literal-visual mode lacks upstream enforcement that a SOT image is required. Fix documented in dev-brief Issue 10 — Irene Pass 1 constraint + Gate 1 image inventory HIL surface. Defer to next run.
- §06 Pre-Dispatch Package: all 7 artifacts written — gary-slide-content.json, gary-fidelity-slides.json, gary-diagram-cards.json, gary-theme-resolution.json, gary-outbound-envelope.yaml, g2-slide-brief.md, pre-dispatch-package-gary.md. S12 preintegration path confirmed (src-004 JPG). Awaiting operator GO for Gary dispatch (§07).
- §5.5 HIL mode approval: written — 9 creative / 3 literal-visual / 2 literal-text, within 10% tolerance. gate_decision: approved.
- §05B G1.5 Cluster Gate: BLOCKED — script requires segment-manifest.yaml (Pass 2 artifact); Irene Pass 1 emits markdown only, no machine-readable cluster plan. Fix-in-flight executed (party-mode → story → dev): cluster-plan.yaml introduced as Pass 1 structural artifact; runner now probes cluster-plan.yaml first; validate_cluster_plan() gains mode param; 46 tests pass. Gate now runs: PASS, 0 errors, 14/14 criteria, 5 clusters (default target 3–5 ✓).
- **PACK MAINTENANCE REQUIRED:** `cluster-plan.yaml` is now a first-class bundle artifact but the prompt pack does not document it. Two Tier-1 prose template edits needed before next run: (1) `05-irene-pass-1-gate-1-fidelity.md.j2` — add `cluster-plan.yaml` to required writes for cluster-enabled runs; (2) `05B-cluster-plan-g1-5-gate.md.j2` — clarify gate reads `cluster-plan.yaml` at Pass 1 time (not `segment-manifest.yaml`), document the artifact's write-once lifecycle after gate passage. After template edits: regenerate pack + run check_pipeline_manifest_lockstep.py. Added to dev brief Issue 9.

### 2026-04-19 — B-Run Step 04.5: Parent Slide Count Polling

- Estimator run: 7 parents / 7 min target → avg 29.3 sec/slide → PASS.
- Operator preference: 30 sec average max — confirmed at 29.3 sec.
- Locked into run-constants.yaml: parent_slide_count=7, target_total_runtime_minutes=7, estimated_total_slides=14, avg_slide_seconds=29.3.

### 2026-04-19 — B-Run Step 04.55: Estimator + Run Constants Lock

- All required fields verified in run-constants.yaml. sha256: 22b52196... LOCK: PASS.

### 2026-04-19 — B-Run Step 4.75: Creative Directive Resolution

- experience_profile: visual-led. Directive authored from state/config/experience-profiles.yaml.
- creative-directive.yaml written and validated: PASS (no errors).
- narration-script-parameters.yaml updated: narrator_source_authority changed from balanced → source-grounded per visual-led profile.
- run-constants.yaml slide_mode_proportions already matched directive (60/25/15). No update needed.
- Artifact count: 14 (13 required + 04a-scope-lock-record.md additive). Non-blocking.
- gate_decision: proceed to §05.
- **CONFORMANCE GAP — §4.75:** Dan (CD) was never invoked. Marcus read experience-profiles.yaml defaults verbatim and wrote the directive himself. No creative judgment applied to this lesson's specific content family. Directive is schema-valid but is a profile printout, not a CD resolution. Flag for next run: wire CD invocation properly.
- **OPERATOR PREFERENCE ESTABLISHED — Agent Provenance:** Every display of information to the operator must carry explicit attribution to the sourcing specialist agent ("Irene recommends...", "Dan decided...", "Quinn-R warns...", "Texas extracted...", "Vera found..."). Marcus is SPOC — dispatches and presents, never authors specialist content without attribution. Saved to sanctum BOND.md. Applies to all future runs.

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

### B-Run §02A — Poll timing policy misread (pack clarification)

**Pack text:** "Enforce a hard 3-minute reply hold from poll start before any submission can be accepted. Submissions before the 3-minute mark are invalid and must be re-polled."

**Operator correction:** The 3-minute window is a *minimum open window* — the poll must not close or auto-proceed before 3 minutes have elapsed. It is NOT a required delay on the operator. If the operator provides complete feedback before 3 minutes, it is valid and should be accepted. The pack text ("submissions before the 3-minute mark are invalid") is misleading and should be rewritten.

**Auto-close:** Pack specifies 15 minutes total from poll open (i.e., 15 minutes, not 3+10). Operator believes there may be a configurable parameter for this; default is 15 min per pack. Carry forward to pack v4.3 for wording fix and parameter surfacing.

**Marcus behavior going forward:** Open the poll, note the auto-close deadline, accept operator input immediately if complete — do not impose a waiting period on the operator.

### B-Run §01 — Sequencing glitch + double preflight (two pack findings)

1. **§01 requires RUN_ID + BUNDLE_PATH before PR-RC establishes them:** Pack lists §01 as Prompt 1, but its required commands (`emit_preflight_receipt --bundle-dir`, `app_session_readiness`) need a concrete `BUNDLE_PATH` which only exists after PR-RC authors `run-constants.yaml`. Operator characterized as "a glitch in our approach." Fix: add §00 Run Constants step, or document PR-RC as an explicit prerequisite at the top of §01. Carry forward to pack v4.3.
2. **Preflight ran twice — PR-PF (session) then §01 (bundle receipt):** Correct by design but redundant API pings. If PR-PF already passed in the same session, §01 should write the receipt from cached results rather than re-pinging. Fix: `--use-cached-preflight` flag on `emit_preflight_receipt`. Carry forward to pack v4.3.

### Step 02 — Two substantive content gaps

1. **Run-constants accepted uncritically:** Initial source map reflected `run-constants.yaml` at face value (PDF primary, JPG only optional context) without first scanning the source directory to check correctness. Operator had to surface the DOCX and MD file's relevance. Marcus should proactively reconcile run-constants against the actual source directory before producing the map, and surface candidate sources not listed in run-constants for operator role-assignment.
2. **DOCX misclassified as excluded:** Marcus labelled the DOCX "excluded to avoid double-extraction" — plausible-sounding but wrong. The correct role is `validation` (cross-confidence against primary). Operator corrected this. Marcus should recognise a same-content DOCX alongside a PDF as a canonical validation candidate without prompting.

**Net:** Structurally conformant (all 8 fields present, stopped and waited). Intellectually incomplete on first pass. HIL operator approval loop caught both errors — confirming gate value. Deferred inventory updated with "best-available-medium selection" follow-on (Epic 27/15 candidate).

### B-Run §08 — Irene Pass 2 work product: structural debt revealed

**Observation (operator-flagged):** Irene's Pass 2 work product required an exceptional volume of post-hoc repair before `validate-irene-pass2-handoff.py` would return STATUS: pass. The remediation spanned two full sessions and multiple iterative rounds. Root causes and counts:

| Category | Issue count | Description |
|---|---|---|
| Envelope integrity | 2 | `pass2-envelope.json` had `perception_artifacts: []` (empty), causing cascading `<missing-id>` failures across all segments. `source_image_path` initially bundle-relative, but validator requires exact absolute paths matching `gary_slide_output.file_path`. |
| Segment manifest — field gaps | 3 | Missing `id` field on segments; missing `motion_asset_path`; missing `visual_file` on motion segment. |
| Segment manifest — value violations | 4 | `visual_detail_load: high` and `very_high` used; allowed values are `{light, medium, heavy}` only. |
| Cluster arc integrity | 2 | c-u07 head had `cluster_position: resolve` instead of `establish`; interstitial immediately jumped to `resolve` with no develop beat. |
| Behavioral intent format | 5+ | Interstitial `behavioral_intent` used full-sentence form; validator `_behavioral_intent_serves_master()` only accepts short-form keywords or exact match. |
| New-concept token violations | 8 | Interstitial narrations introduced tokens (e.g. `turned`, `filed`, `observation`, `applied`, `fundamental`, `process`, `tool`) not pre-seeded in the cluster head's narration. Tokens are 4+-char, non-stopword exact string matches. |
| Bridge cadence + spoken-cue violations | 6 | `cluster_boundary` bridge type requires BOTH intro-class AND outro-class spoken cues; several cluster boundaries missing outro phrases. Cadence resets required `cluster_boundary` type at true cluster transitions. |

**Operator instruction:** Note in the run log that a **data schema / structured template** for Irene's Pass 2 work product is a mandatory follow-on item. The validator's strict contract is not discoverable from the segment-manifest schema alone — the constraints (exact behavioral-intent form, token-level narration pre-seeding, absolute path matching, valid `visual_detail_load` values, bridge-cadence mechanics) are implicit in the validator logic and not surfaced to Irene at composition time.

**Deferred follow-on (file to deferred-inventory.md):** Design a structured **Irene Pass 2 authoring template** that encodes the validator's implicit contract as explicit schema constraints and authoring guidance at the point of composition — so that a correctly structured segment-manifest and pass2-envelope can be produced in one pass without post-hoc debugging. Priority: HIGH — this is the highest-friction single step in the production pipeline for this trial class.
