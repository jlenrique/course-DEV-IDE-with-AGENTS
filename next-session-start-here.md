# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> Current objective: Run a fresh trial production run using updated prompt pack v4.2f with extraction completeness validation.

## Current State (as of 2026-04-16 closeout)

- Active branch: `DEV/slides-redesign`
- Story 20c-15: DONE (profile-aware estimator, 96 tests GREEN, code review PASS)
- Story 22-2: DONE (storyboard B cluster view with script context)
- Trial run C1-M1-PRES-20260415: PAUSED after Prompt 4 — extracted.md was a stub (~30 lines from 24-page PDF). Not resumable.
- Prompt pack v4.2f: Updated with extraction completeness validation, per-dimension evidence requirements, directive governance rules, Notion cross-validation hint, and preamble reorder.
- Source Wrangler agent vision: Captured in `_bmad-output/planning-artifacts/source-wrangler-agent-vision.md` (future epic, not scheduled).

## Immediate Next Action

1. **Start a fresh trial run** using the updated prompt pack v4.2f.
2. Either delete/rename the old bundle at `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260415/` or create a new dated bundle folder.
3. Follow the Pre-Run Checklist and Initialization Instructions in the prompt pack.
4. **Key attention areas during the trial:**
   - Prompt 3: Extraction completeness validation — the word-count floor check should catch a repeat of the 30-line stub. Expected: 24 pages × 250 = 6000 word floor, HALT if < 3000.
   - Prompt 3: Consider Notion cross-validation — the C1-M1 Tejal PDF is a Notion export; pulling from Notion directly provides an independent completeness check.
   - Prompt 4: Per-dimension evidence — each quality gate dimension must include a specific evidence sentence (not bare PASS/FAIL).
   - Prompt 1: Preflight should run with `--bundle-dir` flag.

## Key Architecture Decisions (Party Mode 2026-04-14)

- Three parameter families: Run Constants (operational switches/budgets), Narration-time (how Irene writes scripts), Assembly-time (how Compositor arranges timing)
- Creative Director agent: LLM agent (not deterministic resolver) - second pillar alongside Marcus.
- Two extreme profiles as proof of concept: Visual-Led and Text-Led.
- Parameter directory document: `docs/parameter-directory.md` - master reference for CD, specialists, and HIL operators.

## Key Risks / Unresolved Issues

- **Extraction completeness:** v4.2f adds a prompt-level word-count guard, but a proper script-level extraction validator would be more robust. Track as candidate for Source Wrangler agent evolution.
- **Notion cross-validation** depends on operator declaring the PDF is a Notion export. Future: Source Wrangler agent should detect this automatically.
- **Preflight --bundle-dir:** Confirm the preflight command in Prompt 1 includes `--bundle-dir` on the next trial.
- `20c-4/5/6`: remain deferred unless trial run exposes a concrete composition/design gap.

## Protocol Status

- Follows the canonical BMAD session protocol pair (`bmad-session-protocol-session-START.md` / `bmad-session-protocol-session-WRAPUP.md`).

## Branch Metadata

- Repository baseline branch: `DEV/slides-redesign`
- Next working branch: `DEV/slides-redesign`

Resume commands:

```powershell
cd c:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS
git checkout DEV/slides-redesign
git status --short
```

## Hot-Start Files

- `SESSION-HANDOFF.md` — backward-looking record of this session
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` — the updated prompt pack
- `_bmad-output/planning-artifacts/source-wrangler-agent-vision.md` — future evolution plan
- `run-records/run-record-2026-04-15T20-56-55.md` — last trial run record
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260415/` — old bundle (stub extraction)
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- `scripts/utilities/slide_count_runtime_estimator.py` — new estimator from 20c-15
- `skills/source-wrangler/SKILL.md` — current wrangler skill (future agent candidate)
- `skills/bmad-agent-marcus/scripts/tests/test_prepare_irene_pass2_handoff.py`
- `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py`
- `tests/test_sprint_status_yaml.py`
- `_bmad-output/implementation-artifacts/23-3-bridge-cadence-adaptation.md`
