# Lesson Planner MVP — Story-Cycle Efficiency: Analysis & Remediation 1-Pager

**Date:** 2026-04-18
**Scope:** Cowork-side late session; Cursor-side uptake pending on `dev/lesson-planner` and `dev/30-1-baseline-capture`.

## 1. Original Ask

Diagnose **why Story 31-1's cycle ran ~5× its K-floor** (target 1.2–1.5×) and propose a remediation plan that (a) prevents recurrence on the 21 remaining Lesson Planner MVP stories, (b) de-risks the Marcus-duality refactor (30-1) under its byte-identical DoD, and (c) compounds leverage across the 3 remaining schema-shape stories (31-3, 29-1, 32-2). Deliverables had to land without colliding with Cursor + Claude-Code's authoritative `bmad-create-story` writes.

## 2. What I Did and Why

Four coordinated interventions, executed in a single Cowork-side session:

**(1) Sprint-status.yaml Epics 28-32 append-block.** 35 entries with points / deps / K-floors / amendment annotations; 5 `superseded_by` pointers on retired Epic-28 keys; Epic-28 reshape note. *Why:* Cursor's auto-discovery was blocked on all 21 remaining stories because sprint-status only knew about 31-1 and 31-2. Without this block, every `bmad-create-story` run required a human to hand-seed the target key.

**(2) 31-3 pre-seed relocated** from `_bmad-output/implementation-artifacts/` to `_bmad-output/specs/pre-seed-drafts/31-3-registries-PRE-SEED.md` with a prominent non-authoritative banner; directory README committed. *Why:* Cursor's `bmad-create-story` auto-writes to the implementation-artifacts path. Any Cowork-authored skeleton there would either be overwritten silently or collide noisily. Pre-seed directory makes the authority boundary explicit.

**(3) 30-1 Golden-Trace Baseline capture scaffold.** Capture script (`scripts/utilities/capture_marcus_golden_trace.py`) with CLI, 4 locked normalization rules (timestamp / UUID4 / SHA-256 / repo-absolute path per R1 amendment 12), manifest writer, and envelope writer all landed; `_run_marcus_pipeline()` deliberate stub with explicit Cursor-side TODO. Fixture + trial-corpus READMEs + plan-doc checklist split (Cowork-done vs. Cursor-pending). *Why:* Murat's binding PDG requires a pre-refactor byte-identical baseline committed BEFORE Story 30-1 opens, or the post-refactor diff test is circular. Splitting locked-contract (normalization / CLI / manifest) from Marcus-pipeline-wiring (Cursor-side, sanctum access) gets the blocking pre-work off 30-1's critical path and lets it run in a side worktree parallel with 31-2 dev.

**(4) One-command scaffold instantiator** (`scripts/utilities/instantiate_schema_story_scaffold.py`). 3 required args + 7 optional overrides, 5 auto-derived tokens, all 7 schema-story templates substituted in one shot, CHANGELOG entry emitted to stdout, collision-safe with `--force` override, `--dry-run` preview, pre-seed spec-target default. *Why:* ~60% of schema-story boilerplate is repeated typing; 31-1 caught 6 MUST-FIX Pydantic-v2 idioms at G6 that now ship pre-defused in the scaffold. The instantiator compounds that leverage across 31-3, 29-1, 32-2 — estimated 1.5–2 hours saved per story.

## 3. Evidence of Effects & Uptake

| Intervention | Verification | Downstream uptake |
|---|---|---|
| Sprint-status Epics 28-32 | `yaml.safe_load` parse-clean; 254 total keys; all 35 Epic-28-32 entries resolve correctly; retired keys carry `superseded_by` | Unblocks Cursor auto-discovery on 21 stories; first consumer is whoever opens 30-1 |
| 31-3 pre-seed relocation | File moved; banner prepended; status line changed `ready-for-R2` → `PRE-SEED DRAFT`; directory README + lifecycle doc in place | Cursor `bmad-create-story` for 31-3 writes cleanly to authoritative path; pre-seed readable as input material |
| 30-1 Golden-Trace scaffold | Capture script ruff-clean; 4 normalization rules smoke-tested (each token fires; UUID3 / 63-hex correctly don't match; double-normalize idempotent); stub raises with explicit TODO | Cursor-side capture agent on `dev/30-1-baseline-capture` wires `_run_marcus_pipeline()`; baseline captured BEFORE 30-1 opens |
| Scaffold instantiator | 8 unit assertions on token derivation (PascalCase→snake_case, story-slug, epic-number, module-path helpers); end-to-end dry-run writes 6 files at correct paths; zero `{{TOKEN}}` leakage across all 7 templates; ruff-clean; collision detection caught the real 31-3 pre-seed and refused to overwrite | 3 compounding targets queued (31-3 Registries, 29-1 Fit-Report, 32-2 Weather-Band); ~5 hours total expected savings |

**Governance lockstep.** All four interventions respect the single-writer and authority-boundary rules: sprint-status is the source of truth; pre-seeds never claim authority; the capture script's locked contract ships with the script itself so post-refactor diff is against a committed artifact; the instantiator's pre-seed default prevents accidental authority-theft. No change crossed a lane boundary; no parameter registry edits required.

**Open handoff.** The Cursor-side capture agent on `dev/30-1-baseline-capture` owns the remaining 6-box checklist in the Golden-Trace plan doc. Once that lands, Story 30-1 opens with its byte-identical DoD precondition already satisfied.
