# Production Run Reproducibility Report — C1-M1-PRES-20260419B

**Lesson:** APC C1·M1 (Tejal Gandhi) · Part 1 — "The Call: Setting the Stage & Chapter 1"
**Workflow template:** `narrated-lesson-with-video-or-animation` (prompt pack v4.2)
**Author:** Marcus (APP orchestrator) · **Issued:** 2026-04-21
**Verdict on creative outcome:** All three creative deliverables (slides, motion, audio) were **operator-validated as successful**. This report captures the principal settings and parameter values that produced them, plus the fix-on-the-fly events and deferred remediation/enhancement plans, so the next operator can retrace the same path or deliberately depart from it.

**Scope:** §01 → §15 closed end-to-end. Not a session-wrapup; that runs separately via [`docs/workflow/production-session-wrapup.md`](../../docs/workflow/production-session-wrapup.md).

**Companion artifacts (read alongside this report):**
- Trial-run log (chronological narrative): [`trial-run-c1m1-tejal-20260419.md`](trial-run-c1m1-tejal-20260419.md)
- Bundle-internal run-report: [`course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/run-report.md`](../../course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/run-report.md) (gitignored bundle copy with sha256 pins)
- Deferred inventory: [`_bmad-output/planning-artifacts/deferred-inventory.md`](../planning-artifacts/deferred-inventory.md)

---

## 1. Run Constants — the global control plane

These were locked at §01 Activation + Preflight and never changed for the duration of the run. To reproduce: copy this block verbatim into the next bundle's `run-constants.yaml`.

| Field | Value | Why it mattered |
|---|---|---|
| `run_id` | `C1-M1-PRES-20260419B` | Identity stamp on every receipt + asset |
| `lesson_slug` | `apc-c1m1-tejal` | Bundle directory naming |
| `execution_mode` | `tracked/default` | Marcus orchestrates with full HIL gates |
| `experience_profile` | `visual-led` | 60/25/15 mode-mix recipe (creative/literal-visual/literal-text) |
| `slide_mode_proportions` | `creative: 0.6, literal-visual: 0.25, literal-text: 0.15` | Drives Gary's per-slide treatment selection at §05 |
| `cluster_density` | `default` | Drives Irene's interstitial slide count per cluster |
| `motion_enabled` | `true` | Activates §07 Motion Gate + §08 motion-aware Pass 2 |
| `motion_budget.max_credits` | `125` | Pro-tier ceiling — actual spend ~60-70 |
| `motion_budget.model_preference` | `pro` | Kling pro-tier default |
| `double_dispatch` | `false` | Single-dispatch slide gen (no A/B variants) |
| `quality_preset` | `production` | Fidelity contract band |
| `theme_paramset_key` | `hil-2026-apc-nejal-A` | Slide visual theme — Gamma render style |
| `parent_slide_count` | `7` | Operator-specified at §04.5 (parent SME slides) |
| `target_total_runtime_minutes` | `7` | Operator-specified at §04.5 — actual delivery 7.08 min ✓ |
| `estimated_total_slides` | `14` | Profile-aware estimator output (14 = 7 parent + 7 interstitials at default density) |
| `avg_slide_seconds` | `29.3` | Estimator-derived target; actual range 10.5s → 57.7s |
| `primary_source_file` | `course-content/courses/tejal-APC-C1/C1M1Part01.md` | MD-primary authority (Notion-export, dev-agent unescape applied) |
| `optional_context_assets` | PDF + DOCX + JPG triple | Cross-validation only; MD remains primary |

**`run-constants.yaml` SHA-256 (frozen):** `24dbf820b88348e54c9222edc377d5277e387f6702500cf285b37c21d5f49ca8`

---

## 2. Slide creation — Gary, theme, mode mix

Slides were generated at §05 Gary Dispatch and rendered via Gamma. Nothing in the slide pipeline was tuned per-slide on the fly; the controls below produced the 14-slide deck in one dispatch.

| Knob | Value | Authority / where set |
|---|---|---|
| Slide engine | Gary (LLM-driven slide spec → Gamma deck render) | §05 Gary Dispatch |
| Theme parameter set | `hil-2026-apc-nejal-A` | `state/config/theme-paramsets/` (operator-curated) |
| Mode mix | `creative=0.6 / literal-visual=0.25 / literal-text=0.15` | run-constants `slide_mode_proportions` |
| Total slides | `14` | `estimated_total_slides` from profile-aware estimator |
| Authorized storyboard SSOT | `authorized-storyboard.json` sha256 `f95546b5…b4d9` | §06B identity lock; never modified after |
| Render path | Gamma exports → `gamma-export/apc-c1m1-tejal-20260419b-motion_slide_NN.png` (14 PNGs) | §06 deck approval |

**Per-slide treatment outcome:** 1 creative-fidelity anchor (card-01, video-led) + literal-text learning objectives (card-03) + a mix of literal-visual evidence/framework walkthroughs and creative interstitials (cards 02, 04-14). The exact per-slide `fidelity` and `slide_echo` values are in [`segment-manifest.yaml`](../../course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/assembly-bundle/segment-manifest.yaml).

**To reproduce the same visual look:** keep `theme_paramset_key=hil-2026-apc-nejal-A`. To deliberately depart, swap that key (e.g., `hil-2026-apc-nejal-B`) — everything else can stay the same.

---

## 3. Motion creation — Kling parameters that won

Only **card-01** received a motion clip (5.04s). The clip itself was selected from a multi-take exploration and locked at §07F Motion Gate.

| Knob | Value | Why it won |
|---|---|---|
| Provider | Kling | Pro-tier |
| Model | `kling-v2-6` | Operator selected v2.6 std K07 over v3 beat-chain clips |
| Mode | `std` | Standard quality, faster turnaround |
| Style preset | `K07-clinical-hallway-atmosphere` | Clinical B-roll register matched the lesson's emotional arc |
| Duration | `5.041s` (≈5.04s) | Native clip length; not retimed |
| Subject | Stressed physician with hurried background staff in hospital corridor | Operator-confirmed correct affect for "The Modern Clinician's Dilemma" framing |
| Asset path (final) | `motion/slide-01-motion.mp4` (later copied to `assembly-bundle/motion/`) | sha256-pinned implicitly via §09 Gate 3 lock on `motion_plan.yaml` |

**Rejected alternatives (retained for reference, not in production assembly):**
- `s01-beat-1-v3.mp4`, `s01-beat-2-v3.mp4`, `s01-beat-3-v3.mp4`, `s01-beat-4-v3.mp4` — v3 beat-chain. Beat-2 specifically rejected because the physician appeared serene; wrong emotional register for the dilemma framing.

**Why card-01 only:** the lesson's emotional anchor sits at the opening; remaining 13 cards are static-still-led explanatory beats. Operator policy (memorialized in user memory `feedback_kira_production_constraints.md`): clinical B-roll wins; no talking heads, no hyper-fast motion, no abstract geometry.

**To reproduce:** keep model `kling-v2-6`, mode `std`, style preset `K07-clinical-hallway-atmosphere`. The selection rationale was register-driven, not parameter-driven — if the next lesson's anchor needs a different register, change the style preset, not the model/mode.

---

## 4. Audio creation — ElevenLabs dial settings (the headline creative parameters)

This is the most reproducibility-sensitive section. The audio was the operator-selected high point of the run; these dials are what produced it.

### 4.1 Voice selection — APPROVED

| Field | Value |
|---|---|
| Voice ID | `BuaKXS4Sv1Mccaw3flfU` |
| Voice name | **Christina — Energetic Commercial American Female** |
| ElevenLabs category | `professional` |
| Voice profile (manifest) | `clinical-instructional` |
| Selection mode | `default_and_alternatives` (re-slate after operator excluded Olusola + Natasha) |
| Continuity context | Previous run used Marc B. Laurent (`o0t0Wz5oSDuuCV6p7rba`); operator deliberately departed to evaluate a female register |
| Override reason (verbatim) | "Deliberate departure from continuity (Marc Laurent) to evaluate a female voice register for this trial run B." |
| Approved at | 2026-04-21T02:35:53.918232+00:00 |

### 4.2 Voice direction — dials-only amp-up (the core creative knobs)

**Authority:** operator-approved at §11B Input Package HIL on 2026-04-21. Recorded to [`voice-selection.json::voice_direction_overrides`](../../course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/voice-selection.json) (NOT to the Gate-3-locked `pass2-envelope.json`).

**Operator rationale (verbatim from override block):** *"First synthesis of trial B: dial-only amp-up on `eleven_multilingual_v2` to exercise the ceiling of voice-settings-driven expressiveness within the locked script. Operator preference: err 'over the top' on first take; dial back later if needed."*

| Control | Envelope default | **Effective (this run)** | Δ | Layer | Real ElevenLabs API param? |
|---|---|---|---|---|---|
| `stability` | 0.5 | **0.25** | ↓ 0.25 | API direct | ✅ Yes — lower = wider expressive swing |
| `similarity_boost` | 0.75 | 0.75 | — | API direct | ✅ Yes — voice-identity fidelity |
| `style` | 0.0 | **0.25** | ↑ 0.25 | API direct | ✅ Yes — exaggerates Christina's "energetic commercial" character |
| `speed` (request) | 1.0 | 1.0 | — | API direct | ✅ Yes — no request-level time-stretch |
| `use_speaker_boost` | false | false | — | API direct | ✅ Yes |
| `emotional_variability` | 0.5 | **0.75** | ↑ 0.25 | Marcus wrapper | ❌ No — maps to API `stability = 1 − 0.75 = 0.25` when stability isn't explicitly set; consistent with explicit `stability=0.25` above |
| `pace_variability` | 0.05 | **0.15** | ↑ 0.10 | Marcus wrapper | ❌ No — per-segment client-side `speed` nudge bound (clamped 0.0–0.25); wider band = more cadence contrast |

### 4.3 Per-segment differentiation — what actually varies vs what's identical

| Control | Across the 14 calls |
|---|---|
| `stability` | **Identical** every call (0.25) |
| `similarity_boost` | **Identical** (0.75) |
| `style` | **Identical** (0.25) |
| `use_speaker_boost` | **Identical** (false) |
| `speed` | **Varies per segment** — nudged from base 1.0 by pace-variability band based on each segment's `duration_estimate_seconds` vs cluster mean |
| Emotional contrast between segments | Driven by **text content + `previous_request_ids` continuity stitching**, not by per-segment parameter values |

### 4.4 API-level call parameters

| Field | Value |
|---|---|
| Endpoint | `text-to-speech/{voice_id}/with-timestamps` |
| Model | `eleven_multilingual_v2` |
| Continuity | `previous_request_ids` chain — every segment N references the request_id of segment N-1 |
| Audio buffer | **2.0s** lead-in + 2.0s tail silence pad applied via ffmpeg |
| Caption offset | VTT cues offset by 2.0s lead-in to align with padded MP3s |
| Number of calls | 14 sequential (no parallelization — required for continuity stitching) |
| Wall time | 70 seconds (03:23:29Z → 03:24:39Z on 2026-04-21) |
| Total narration duration | 424.74s (7.08 min) — within 7.00-min target envelope |
| Duration spread | shortest card-05 10.50s → longest card-07 57.68s (5.5× range) |

### 4.5 Model ceiling — what the dials can NOT do on `eleven_multilingual_v2`

`eleven_multilingual_v2` does **not** support audio tags (`[laughs]`, `[whispers]`, `[shouts]`). The locked script is factual register (0 exclamations / 0 questions / 1 ellipsis). This synthesis measured the **dials-only ceiling** within those constraints. To exceed that ceiling, see deferred theatrical-direction follow-on (§7 below).

### 4.6 Reproducibility command (verbatim)

```bash
python scripts/marcus_shims/run_prompt12_narration.py \
  --bundle course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion
```

The shim reads `voice-selection.json::voice_direction_overrides` and passes them as `parameter_overrides` into `elevenlabs_operations.generate_manifest_narration()`. To reproduce the dial settings exactly, restore the §4.2 override block to `voice-selection.json`. Hash gates (`locked_manifest_hash`, `locked_script_hash`) ensure the script + manifest the synthesis ran against are byte-identical to the §09 Gate-3 lock.

---

## 5. Locked artifacts — sha256 pins (the script that produced this audio)

| Artifact | SHA-256 | Role |
|---|---|---|
| `narration-script.md` | `5e7a7205d3255b61e7b57170bb6b34985dd45990457b5abbbde7e7bf327ed360` | Pass 2 narration script with full cluster context |
| `segment-manifest.yaml` (locked at §09) | `1ecbfcbae20f4551b2941157fd3b1fd0244b31a100d4591d5e3b6b7959b8081c` | SSOT for downstream |
| `pass2-envelope.json` | `3a99ab99ae6d8f7b552d980eebc515cadfdbf7a3f4d737592964cbbd4032b206` | Irene Pass 2 inbound envelope |
| `motion_plan.yaml` | `346268d61d22c4251de0f6ef33debacae027028c030f23a2d74240e7e2f2eda6` | Motion Gate-approved bindings |
| `authorized-storyboard.json` | `f95546b5a58ead796683d7f172ad3271563f83080144a144d60d3bef118eb4d9` | Slide identity SSOT |
| `motion-gate-receipt.json` | `051c1278…43dd` | Identity SSOT for motion |
| `segment-manifest.yaml` (post-§14 sync) | `8e35c387e6631fd6c5761a5fd89f7bf756f12a03df9b4d2ea58e9e341bfb7d04` | Bundle-relative paths after compositor sync |
| `DESCRIPT-ASSEMBLY-GUIDE.md` | `efee4a69c41341f3619a353bf87b560ae3213bd9be6b8194ff182d5cb57e7417` | Compositor baseline + Operator Decisions injection |
| `DESMOND-OPERATOR-BRIEF.md` | `97f20d3e31e2e0ecdb9e16705b4a8df9a30cdf3b3e225d37b456ddbcd907b0ef` | Run-scoped operator brief + Automation Advisory |

Hash drift since §09 lock on the four locked artifacts: **none** (re-verified at §11 voice approval, §11B input package review, §12 synthesis preflight, and §14 assembly-bundle copy).

---

## 6. Fix-on-the-fly events — patched in this run, NOT durable

Every entry below was a remediation Marcus performed during the run to keep moving. **None of these fixes survived to the next run automatically** — they are workarounds whose durable counterparts are tracked in §7 Deferred Remediation. Document the patch so the next operator knows it happened and what it covered for.

### 6.1 §13 Quinn-R — `ffprobe` absent from `imageio_ffmpeg` distribution
- **Symptom:** Quinn-R shim crashed when probing `slide-01-motion.mp4` duration.
- **Root cause:** The `imageio_ffmpeg` distribution ships `ffmpeg-win-x86_64-v7.1.exe` only — no companion `ffprobe.exe`.
- **Patch:** Switched the shim to `ffmpeg -i <clip>` and parsed the `Duration:` regex from stderr. No ffprobe needed.
- **Where the patch lives:** `scripts/marcus_shims/run_prompt13_quinnr_precomposition.py::_probe_motion_duration_seconds`.
- **Durable disposition:** This pattern should be lifted into a shared utility when Quinn-R is canonicalized (currently a Marcus shim).

### 6.2 §13 Quinn-R — path resolution against CWD instead of bundle root
- **Symptom:** Initial Quinn-R run reported false-positive blocking issues for card-01 (visual missing, motion fail), even though the assets were on disk.
- **Root cause:** Shim resolved relative paths against the current working directory, not the bundle root.
- **Patch:** Added `_resolve(path_str, bundle, fallback)` helper; routed all path lookups through it.
- **Where the patch lives:** Same shim, in path-resolution helpers.
- **Durable disposition:** Same as 6.1 — fold into the canonicalized Quinn-R utility.

### 6.3 §14 Compositor — duplicate `motion_asset` + `motion_asset_path` keys
- **Symptom:** `sync-visuals` refused manifest edit: `'motion/slide-01-motion.mp4' appears 2 times, expected 1`.
- **Root cause:** Irene Pass 2 emitted both the legacy `motion_asset` and the canonical `motion_asset_path` for card-01, with identical values. Compositor's text-replace count check rejected the ambiguity.
- **Patch:** Removed the redundant `motion_asset` key (compositor only references `motion_asset_path`; verified via repo-wide grep).
- **Where the patch lives:** Inline edit to `assembly-bundle/segment-manifest.yaml`.
- **Durable disposition:** Irene Pass 2 authoring template (§7.1) must emit only `motion_asset_path` going forward.

### 6.4 §14 Compositor — `visual_file` missing on cards 02-14
- **Symptom:** `sync-visuals` rejected card-02 with "missing visual_file"; same gap on cards 03-14 confirmed by inspection.
- **Root cause:** Irene Pass 2 only populated `visual_file` on card-01; the other 13 segments had no value.
- **Patch:** Inline patch script read `authorized-storyboard.json` (Gate-2-approved SSOT) and injected `visual_file: gamma-export/apc-c1m1-tejal-20260419b-motion_slide_NN.png` into 13 segments. 13 lines added in one pass.
- **Where the patch lives:** Inline manifest edit during §14 prep.
- **Durable disposition:** Irene Pass 2 authoring template (§7.1) — `visual_file` MUST be populated for every segment at Pass 2 emission, not back-filled at §14.

### 6.5 §14 Compositor — `motion_duration_seconds: null` on card-01
- **Symptom:** Compositor's `validate_manifest` rejected card-01 (non-static segment without `motion_duration_seconds`).
- **Root cause:** Irene Pass 2 didn't populate `motion_duration_seconds` even though §07F Motion Gate had approved a clip with a known duration.
- **Patch:** Quinn-R had ffmpeg-probed the clip at §13 (5.04s); Marcus injected that value into the manifest before re-running `sync-visuals`.
- **Where the patch lives:** Inline manifest edit during §14 prep.
- **Durable disposition:** Irene Pass 2 authoring template (§7.1) — `motion_duration_seconds` MUST be carried forward from Motion Gate receipt, not left null.

### 6.6 §13 receipt — operator decisions captured AFTER first receipt write
- **Symptom:** The `quinnr-precomposition-receipt.json` was written before the operator HIL ("Yes. on 1 and 2"). Required a re-write to embed the `operator_acceptance` block.
- **Root cause:** Receipt schema didn't reserve a slot for operator-acceptance fields when status is `pass_with_advisories`.
- **Patch:** Re-wrote the receipt with `operator_acceptance: { card_01_motion_fit: "A", card_01_motion_fit_decision: "...", slow_wpm_accepted: true, slow_wpm_segments: [...] }` after operator approval.
- **Durable disposition:** Quinn-R receipt schema should formalize an `operator_acceptance` block when status is `pass_with_advisories`. Add to Quinn-R canonicalization scope.

---

## 7. Deferred remediation + enhancements

Items that this run made tangible but did not implement. All are filed in [`_bmad-output/planning-artifacts/deferred-inventory.md`](../planning-artifacts/deferred-inventory.md). Cross-reference here so the reproducibility report is self-contained for the next operator's planning pass.

### 7.1 Irene Pass 2 authoring template (HIGH — single highest-friction step in the pipeline this run)
**Inventory entry:** §Named-But-Not-Filed Follow-Ons → "Irene Pass 2 authoring template / schema contract".
**Concrete failure modes harvested from this run** (extends the existing entry):
- 6.3 — duplicate `motion_asset` + `motion_asset_path` keys
- 6.4 — `visual_file` missing on 13/14 segments
- 6.5 — `motion_duration_seconds` null when Motion Gate already had it
**What "done" looks like:** A schema-validated emission template + lint pass that fail-closes Pass 2 if any of these fields are missing/duplicated/null when their upstream source has them.
**Trigger:** before next Pass 2 run on any lesson.

### 7.2 Theatrical-direction synthesis (Tier 1 + Tier 2) — operator's highest-value next dial
**Inventory entry:** §Named-But-Not-Filed Follow-Ons → "Theatrical-direction synthesis (Tier 1 + Tier 2)".
**Tier 1 (~3-5 pts):** Per-segment `voice_settings` authored by Irene (instead of identical settings across all 14 calls). Allows e.g. `stability=0.15` on emotional anchor segments and `stability=0.45` on literal-text LO segments.
**Tier 2 (~5-8 pts):** Model swap to `eleven_v3` + Irene-authored audio tags (`[laughs]`, `[pause]`, `[whispers]` per segment). Requires script-Pass-2 to author both the prose and the tag annotations.
**Trigger:** operator evaluates this run's audio output against Tier 1/2 ceiling. Operator's stated posture: "err over the top first; dial back later." This run was the dials-only baseline; Tier 1 is the natural next escalation.

### 7.3 CLI canonicalization for `voice_direction_overrides`
**Inventory entry:** §Named-But-Not-Filed Follow-Ons. Priority: MEDIUM.
**What's missing:** `elevenlabs_operations.py manifest` CLI doesn't read `voice_direction_overrides` from `voice-selection.json` today. This run used `scripts/marcus_shims/run_prompt12_narration.py` as a workaround.
**What "done" looks like:** CLI `--apply-voice-direction-overrides voice-selection.json` flag (or implicit read), and the shim retires.

### 7.4 `voice-preview --exclude-voice-ids` flag
**Inventory entry:** §Named-But-Not-Filed Follow-Ons. Priority: MEDIUM.
**Why:** Re-slating a continuity preview required an ad-hoc shim because the operator excluded Olusola + Natasha mid-flow. A first-class exclusion flag eliminates the shim.

### 7.5 Quinn-R canonicalization (lifts §6.1, §6.2, §6.6 fixes into the standard tool)
**Implied by §6 fix-on-the-fly entries.** Currently a Marcus shim (`scripts/marcus_shims/run_prompt13_quinnr_precomposition.py`). Should become a first-class capability under `skills/` with:
- ffmpeg-stderr duration probing pattern lifted into a shared utility
- bundle-rooted path resolution baked into the API
- formal `operator_acceptance` block in the receipt schema for `pass_with_advisories` status

### 7.6 Desmond Descript doc-cache refresh (operational hygiene)
**Inventory:** not yet a formal follow-on; flagged in §14.5 receipt + §15 receipt open-notes.
**Why:** Desmond's sanctum `MEMORY.md` records Descript version target as **Unknown** and doc cache as **never refreshed**. Brief was authored honestly with this disclosure (per Desmond's "never lie / never fake continuity" creed), but next run should ground in current Descript surfaces.
**Action:** `python skills/bmad-agent-desmond/scripts/refresh_descript_reference.py` and update sanctum `MEMORY.md` with version notes.

### 7.7 Stray asset cleanup
`assembly-bundle/audio/apc-c1m1-tejal-20260419b-motion-card-04.zip` is leftover from an earlier alignment-zip experiment, not manifest-referenced. Operator may delete before Descript import. Non-blocking; cosmetic.

### 7.8 Operator-noted enhancements for next run (captured 2026-04-22 in trial-run log §"High-value enhancements")
1. Reproducibility report (this document satisfies the principle; formalize as an automatic post-run emission).
2. Ad hoc production mode (unlock profile settings mid-run, optionally save).
3. Segment-level audio control (per-segment `voice_settings` + audio tags — overlaps with §7.2 Tier 1).
4. Source content type — `collateral` catch-all.
5. Dan as ongoing creative-treatment-profile keeper, not one-off directive author.
6. Activate research retrieval and injection in the production path.
7. Surface pronunciation dictionary before audio synthesis spend.

---

## 8. Closed gates — downstream must-not-modify boundary

§02A · §04 · §04A · §07C · §07D · §07F · §08B · **§09 (Gate 3 Lock)** · **§10 (Fidelity + Quality)** · **§11 (Voice Selection)** · **§11B (Input Package HIL)** · **§12 (ElevenLabs Synthesis)** · **§13 (Quinn-R Pre-Composition)** · **§14 (Compositor Assembly)** · **§14.5 (Desmond Operator Brief)** · **§15 (Operator Handoff)**

---

## 9. Receipts trail — every gate's evidence

All receipts live at the bundle root: `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/`.

| Stage | Receipt |
|---|---|
| §07F Motion Gate | `motion-gate-receipt.json` |
| §09 Gate 3 Lock | `gate3-lock-receipt.json` |
| §10 Fidelity + Quality | `gate10-fidelity-quality-receipt.json` |
| §11 Voice Selection | `voice-selection.json` (status: approved + `voice_direction_overrides`) |
| §11B Input Package HIL | `elevenlabs-input-review.md` |
| §12 ElevenLabs Synthesis | `prompt12-synthesis-receipt.json` |
| §13 Quinn-R Pre-Composition | `quinnr-precomposition-receipt.json` |
| §14 Compositor Assembly | `prompt14-compositor-receipt.json` |
| §14.5 Desmond Operator Brief | `prompt14_5-desmond-receipt.json` |
| §15 Operator Handoff | `prompt15-handoff-receipt.json` |

**Bundle-internal run-report (with the same data, locally):** `run-report.md` at the bundle root.

---

## 10. To retrace this run on a new lesson

1. Copy the §1 run-constants block into the new lesson's bundle.
2. Keep `theme_paramset_key=hil-2026-apc-nejal-A` (or pick a curated alternative if a different visual register is wanted).
3. For motion: keep model `kling-v2-6` + mode `std`; pick a style preset that matches the new lesson's emotional register (this run's `K07-clinical-hallway-atmosphere` is lesson-specific).
4. For voice: pick the voice (Christina here was a deliberate departure; the next run may continuity-carry her or depart again). Then **copy §4.2's `voice_direction_overrides` block verbatim** into the new bundle's `voice-selection.json` to reproduce the dials-only amp-up audio character.
5. Run §01 → §15 per pack v4.2. Watch for the §6 fix-on-the-fly traps; they will recur until §7's deferred remediations land.
