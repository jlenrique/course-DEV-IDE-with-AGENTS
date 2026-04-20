# Dev Agent Brief — Trial Run B Fix-in-Flight
**Issued by:** Marcus (Production Orchestrator)
**Date:** 2026-04-19
**Workflow:** `bmad-quick-dev`
**Branch:** `trial/2026-04-19`
**Source:** Conformance observations from `_bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260419.md` (B-run session)

---

## Context

This brief covers 5 issues surfaced during the B-run trial session (run ID `C1-M1-PRES-20260419B`). They are a mix of pack doc fixes, a code change, a Marcus behavior gate, and a SKILL.md update. All are low-blast-radius. Tackle in one pass; the trial is paused at §02A awaiting these fixes before resuming.

**Critical constraint:** The prompt pack (`docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`) is **generated** — do not edit it directly. All pack text changes must go through the Jinja2 template pipeline:

- **Generator entry point:** `scripts/generators/v42/render.py` — takes `--manifest` and `--output`
- **Manifest source:** `state/config/pipeline-manifest.yaml` — defines steps; renderer loops over them
- **Per-section templates:** `scripts/generators/v42/templates/sections/<step-id>-<slug>.md.j2` — one file per pack section
- **Layout template:** `scripts/generators/v42/templates/layout/pack.md.j2` — assembles sections
- **Rendered output:** `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`

After any template edit, re-run the generator and verify the rendered output matches intent. There are fixtures under `tests/generators/v42/fixtures/` — run those tests to confirm no regressions.

---

## Issue 1 — §01 Sequencing: Pack must document PR-RC as a prerequisite

**Problem:** `scripts/generators/v42/templates/sections/01-activation-preflight.md.j2` references `[RUN_ID]` and `[BUNDLE_PATH]` as template tokens in its required commands, but these values only exist after `run-constants.yaml` is authored (via Marcus PR-RC). A fresh operator following the numbered prompts has no RUN_ID when they reach §01.

**Fix — template edit only (`01-activation-preflight.md.j2`):**
Add a prerequisite block at the top of the section, before the numbered receipt items:

```
**Prerequisite:** Run constants must be authored (via Marcus PR-RC) before this prompt
can be executed. `RUN_ID` and `BUNDLE_PATH` are required by the commands below.
If run constants are not yet established, stop and run PR-RC first.
```

No code changes. No manifest changes. Re-render the pack after the template edit and verify the prerequisite block appears at the top of §01 in the rendered output.

---

## Issue 2 — Double Preflight: Consolidate or cache

**Problem:** When Marcus runs PR-PF (session-level preflight) and then §01's `emit_preflight_receipt`, all API health checks fire twice in the same session. Redundant pings; adds latency.

**Assessment question first:** `emit_preflight_receipt.py` (`scripts/utilities/emit_preflight_receipt.py`) calls `run_readiness()` from `app_session_readiness.py`, which includes the full tool preflight. PR-PF runs the exact same `run_readiness()`. If the checks are literally identical and staleness is not a concern within a single session, the right answer is: **do preflight once, at §01, and drop the separate PR-PF step** — or make PR-PF write a session-scoped receipt that §01's `emit_preflight_receipt` can consume without re-pinging.

**Recommended fix — add `--use-session-receipt` flag to `emit_preflight_receipt.py`:**

1. Add `--session-receipt PATH` argument to `emit_preflight_receipt.main()`.
2. If `--session-receipt` is supplied and the file exists and is less than N minutes old (suggest `session_receipt_max_age_minutes`, default `60`, see Issue 3 for parameter registry), load it as the preflight result instead of calling `run_readiness()`.
3. Write the (possibly cached) result to `--output` as normal — the bundle artifact is always written fresh regardless.
4. Log clearly whether the receipt came from cache or a live run.

**Staleness guard:** The age check (`session_receipt_max_age_minutes`) ensures a stale session receipt from a prior day can't sneak through. Default 60 minutes is conservative for a same-session use case.

**Template edit (`01-activation-preflight.md.j2`):** Update the `emit_preflight_receipt` command line to show the optional `--session-receipt` flag:

```
- `.\.venv\Scripts\python.exe -m scripts.utilities.emit_preflight_receipt --with-preflight --motion-enabled --bundle-dir [BUNDLE_PATH] --output [BUNDLE_PATH]/preflight-results.json [--session-receipt PATH_TO_SESSION_RECEIPT]`
```

---

## Issue 3 — §02A Poll Timing: Fix wording + make timing values parameters

**Problem:** `scripts/generators/v42/templates/sections/02A-operator-directives.md.j2` says:

> "Enforce a hard 3-minute reply hold from poll start before any submission can be accepted."
> "Submissions before the 3-minute mark are invalid and must be re-polled."

This is wrong. The intent is: the poll must stay **open** for at least 3 minutes (Marcus cannot rush through or auto-close early). The operator may submit valid input at any time, including before 3 minutes. The 3-minute floor prevents Marcus from racing through the gate before the operator has had a chance to respond.

**Fix — template edit (`02A-operator-directives.md.j2`):**

Replace the poll timing policy block with:

```
Poll timing policy (hard requirement):
- Start a poll timer when Prompt 2A is issued.
- The poll must remain open for a minimum of {{ poll_min_open_minutes | default(3) }} minutes — Marcus
  may not auto-close or auto-advance before this floor has elapsed.
- Operator input received before the floor elapses is valid and accepted immediately.
- Auto-close the poll {{ poll_auto_close_minutes | default(15) }} minutes after poll start
  if a complete submission has not been received.
- If the poll auto-closes, keep ingestion blocked and require a new Prompt 2A poll.
```

**Parameter registry:** Check whether `poll_min_open_minutes` and `poll_auto_close_minutes` exist in `state/config/`. If not, add them to an appropriate config file (suggest `state/config/workflow-policy.yaml`, creating it if it doesn't exist). Wire the Jinja2 template to read them via the generator's `env.py` or pass them through the manifest. Parameters must have sensible defaults (3 and 15) so the template renders correctly even without the config file.

Also update the gate rule line:
- Old: "Any poll auto-close, submission before the 3-minute hold, or missing directive category blocks progression until re-polled."
- New: "Any poll auto-close or missing directive category blocks progression until re-polled. Early operator submission within the minimum open window is valid."

---

## Issue 4 — §02 Source Directory Scan: Hardwire as a gate before map authoring

**Problem:** Marcus produced the Source Authority Map directly from `run-constants.yaml` without first scanning the source directory and asking the operator to assign roles to discovered files. This is the same mistake made in the A-run. It is a behavioral gap, not just a pack gap — Marcus needs a gate that forces the scan-and-ask step before any map is drafted.

**Fix — two-part:**

**Part A — template edit (`02-source-authority-map.md.j2`):**

Replace the current instruction block with a gate that enforces the scan-first sequence:

```
**Required pre-map gate (mandatory — do not skip):**
Before drafting the source authority map:
1. Scan the source directory containing `[PRIMARY_SOURCE_FILE]` and list every file found.
2. Present the full file list to the operator with a numbered row per file, proposed role
   for each (primary / validation / supplementary / skip), and a brief note on each.
3. Wait for operator role assignments.
4. Draft the source authority map only after operator assignments are received.

Operator-assigned roles are authoritative. Do not infer roles from run-constants alone —
run-constants lists intended sources but the directory is ground truth.
```

**Part B — this is a Marcus behavioral gate, not just pack text.** Use the project's existing gate pattern. Check whether a `gate_check` or pre-step guard mechanism exists in `scripts/utilities/` or the Marcus capability framework. If a lightweight gate helper exists, wire a `source-directory-scan-gate` that fails closed if called before the operator role-assignment artifact exists. Follow the DRY pattern already established — do not invent a new mechanism.

---

## Issue 5 — Marcus HIL Usability: Numbered rows + paginated output

**Problem A:** Marcus presented source file tables without numbered rows, making it slow for the operator to reference specific items by number. This was corrected mid-session by operator request.

**Problem B (broader):** Marcus dumps multi-item displays (tables, lists, receipts) as a single block. In a terminal-based HIL interaction, large dumps are hard to scan. Operator preference is paginated / show-next-on-demand for long displays.

**Fix — SKILL.md update (`skills/bmad-agent-marcus/SKILL.md`):**

Add to the `## Lane Responsibility` or a new `## HIL Display Standards` section:

```markdown
## HIL Display Standards

**Numbered rows:** Every table or list requiring operator selection or reference must
include a unique sequential row number as the first column (1, 2, 3…). Apply this to
source file lists, plan unit tables, variant selection displays, and any other operator-
facing enumeration. This allows the operator to reply "1, 3, skip 4" without ambiguity.

**Paginated output:** For displays exceeding ~15 rows or ~30 lines, do not dump the
entire content at once. Present the first page and offer "show next" on demand. Apply to:
file listings, storyboard summaries, gate receipts with many items, and any operator-
review surface. Exception: machine-readable artifacts (JSON, YAML) written to disk need
not be paginated; only conversational displays are subject to this rule.
```

Also update Marcus's SKILL.md `CREED.md` or `references/conversation-mgmt.md` in the sanctum to mirror this so it persists across sessions. The SKILL.md is the registration layer; the sanctum is the runtime layer — both need the rule.

---

## Issue 6 — Resource Discovery: ffmpeg and .venv-resident tools

**Observation from operator:** Tools like `ffmpeg` installed in `.venv` (or known locations) get "lost" because agents and scripts search PATH or standard system locations rather than the repo-local resolver.

**Fix:** Check `scripts/utilities/ffmpeg.py` (already referenced in the pack's §07E implementation note). Ensure it is used consistently as the single resolver for `ffmpeg` across all scripts that invoke it. Grep for bare `subprocess` calls to `ffmpeg` that bypass the utility:

```bash
grep -rn "ffmpeg" skills/ scripts/ --include="*.py" | grep -v "ffmpeg.py" | grep -v "__pycache__"
```

For any hits: replace bare `ffmpeg` invocations with the repo utility's resolved path. Add a docstring note to `scripts/utilities/ffmpeg.py` making it the canonical reference for all ffmpeg resolution in this repo.

Extend this pattern audit to other `.venv`-resident binaries if the grep surfaces similar issues (e.g., `ffprobe`, `yt-dlp`, etc.).

---

## Issue 8 — §4.75 CD (Dan) Not Invoked — Creative Directive Authored by Marcus Directly

**Problem:** §4.75 requires delegating creative directive resolution to the Creative Director (CD) agent. Marcus bypassed CD and read `state/config/experience-profiles.yaml` defaults verbatim, writing the directive himself. The directive is schema-valid but is a profile printout, not a CD creative resolution. Dan never shaped narrative tension, emotional coloring, or rhetorical richness for this specific lesson content.

**Fix:** Wire a CD invocation path in the §4.75 execution flow. CD's sanctum is at `_bmad/memory/bmad-agent-cd/`. The `skills/bmad-agent-cd/references/creative-directive-contract.md` defines the output contract. CD should receive: operator emphasis answer, run-constants.yaml, style-bible signals, and experience-profiles.yaml — and return a `creative-directive.yaml` with content-specific creative judgments, not just profile defaults.

**Low priority for current trial** — directive is functionally sound. Wire before next production run.

## Issue 7 — `docx` Provider Listed as Ready but Rejected by Runner

Same class as the A-run `md` provider gap. `--list-providers` shows `docx` as `ready`, but the runner's accepted provider set in dispatch (line ~207 of `run_wrangler.py`) does not include `docx`. The runner auto-recovers via `local_file` → `python-docx` extractor, so results are functionally correct, but the directive must specify `local_file` instead of the semantically correct `docx` — a papercut that will recur every run.

**Fix:** Wire `docx` into the runner's accepted provider dispatch, same pattern as the `md` fix from the A-run. Confirm `--list-providers` and runner dispatch are kept in sync going forward.

---

## Acceptance Criteria

- [ ] Pack re-generated cleanly after template edits; generator fixture tests pass
- [ ] §01 template shows PR-RC prerequisite block
- [ ] `emit_preflight_receipt.py` accepts `--session-receipt` with age-gated cache; existing behavior unchanged when flag is absent
- [ ] §02A template uses corrected poll timing language; `poll_min_open_minutes` / `poll_auto_close_minutes` exist as parameters with defaults
- [ ] §02 template enforces scan-first gate with numbered-row instruction; gate follows existing gate pattern (DRY)
- [ ] `skills/bmad-agent-marcus/SKILL.md` updated with HIL Display Standards section
- [ ] `_bmad/memory/bmad-agent-marcus/references/conversation-mgmt.md` updated to mirror HIL Display Standards
- [ ] `scripts/utilities/ffmpeg.py` confirmed as canonical resolver; bare subprocess ffmpeg calls replaced or noted

## Do Not Touch

- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` directly — generated file only
- Other pack sections not named above
- Active bundle `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/` — trial is live
- Pipeline manifest `state/config/pipeline-manifest.yaml` step ordering — no step additions without party-mode consensus
