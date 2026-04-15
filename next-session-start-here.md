# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> Current objective: Formally review the remaining Wave 2B foundation stories (`20c-9` through `20c-12`) and decide what can now move to `review` or `done` before reactivating deferred downstream work.

## Current State (as of 2026-04-15 closeout)

- Active branch: `DEV/slides-redesign`
- Wave 1 (Foundation): COMPLETE - 158 consolidated tests.
- Wave 2A (Cluster Maturity): `20c-1` slice 1 done (10 templates), `20c-2` DONE (selector complete), `20c-3` DONE after review fixes and full-suite validation.
- Wave 2B (Creative Control): actively executing.
- `20c-7`: done (parameter registry + directory + tests)
- `20c-8`: done (assembly timing parameters + validators/tests)
- `20c-9`: in-progress (slice expansion implemented: narration profile control set broadened and validated; not yet formally reviewed)
- `20c-10`: in-progress (CD contract-first scaffold; Marcus-only intake contract closed by `20c-14`)
- `20c-11`: in-progress (creative directive schema artifacts + validator path and tests)
- `20c-12`: in-progress (bootstrap experience profile definitions; Marcus conversational surface and proof closed by `20c-14`)
- `20c-13`: done (resolver wiring implemented and formally reviewed clean after contract tightening and full-suite validation)
- `20c-14`: done (Marcus-facing profile intake, CD intake contract, envelope propagation, validator audit surface, and proof artifacts formally reviewed clean after full-suite validation)
- A/B trials: SKIPPED - replaced by experience-profile-driven trial runs (Party Mode consensus 2026-04-14).
- `20c-4/5/6` and `23-1`: deferred pending the next post-proof behavior slice.
- Pass 2 mode: `structural-coherence-check` (Epic 23 not yet implemented)
- Latest closeout validation passes: `670 passed, 1 skipped, 27 deselected`.

## Immediate Next Action

1. Stay on `DEV/slides-redesign`.
2. Formally review the remaining Wave 2B foundation stories:
   - Start with `20c-10` (Creative Director Agent), `20c-11` (Creative Directive Schema), and `20c-12` (Experience Profile Definitions).
   - Then decide whether `20c-9` is already review-ready or still needs another implementation slice.
3. Only after that status cleanup, re-evaluate whether to reactivate `23-1` or one of the deferred `20c-4/5/6` stories.
4. If `sprint-status.yaml` changes, run `.venv\Scripts\python.exe -m pytest -q tests/test_sprint_status_yaml.py`.

## Key Architecture Decisions (Party Mode 2026-04-14)

- Three parameter families: Run Constants (operational switches/budgets), Narration-time (how Irene writes scripts), Assembly-time (how Compositor arranges timing)
- Creative Director agent: LLM agent (not deterministic resolver) - second pillar alongside Marcus. Owns creative frame, parameter orchestration, gate-triggered review.
- CD interaction model: Option B - params for deterministic executors (ElevenLabs, Compositor) plus params and structured creative briefs for LLM interpreters (Irene, Gary). All through Marcus's envelope system, no side-channels.
- CD -> Irene brief: Minimal (~200 tokens): tone_reference, arc_shape, kill_list, coupling_intent, source_authority. Validated against narration-script-parameters.yaml before dispatch. Irene's perception drives specifics.
- Two extreme profiles as proof of concept: Visual-Led and Text-Led. Five key differentiators: narrator_source_authority, slide_echo, slide_content_density, ElevenLabs.style, variability_scale.
- Parameter directory document: `docs/parameter-directory.md` - master reference for CD, specialists, and HIL operators.

## Key Risks / Unresolved Issues

- Wave 2B status drift risk: `20c-10`, `20c-11`, and `20c-12` may now be largely implemented but are still marked `in-progress`; next session should resolve that formally rather than guessing.
- Scope hygiene risk: Ambient unrelated worktree noise exists; keep next implementation edits tightly scoped to the intended story files.
- Future reactivation choice: After the remaining Wave 2B stories are reviewed, re-evaluate whether the next best move is `23-1` or one of the deferred `20c-4/5/6` stories.

## Protocol Status

- Follows the canonical BMAD session protocol pair (`bmad-session-protocol-session-START.md` / `bmad-session-protocol-session-WRAPUP.md`).

## Branch Metadata

- Repository baseline branch: `DEV/slides-redesign`
- Next working branch: `DEV/slides-redesign`

Closeout exception:

- This session commits and pushes the working branch directly rather than merging to `master`.
- Reason: the user requested a branch push closeout, and ambient unrelated workspace changes remain outside the scoped session commit.

Resume commands:

```powershell
cd c:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS
git checkout DEV/slides-redesign
git status --short
```

## Ambient Workspace State

- No known ambient local changes are expected after the final cleanup commit/push for this session.
- If a dirty tree appears on next startup, treat it as new post-closeout work rather than part of this handoff.

## Hot-Start Files

- `SESSION-HANDOFF.md`
- `next-session-start-here.md`
- `bmad-session-protocol-session-START.md`
- `bmad-session-protocol-session-WRAPUP.md`
- `_bmad-output/implementation-artifacts/20c-14-e2e-validation-both-profiles.md`
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/epics-interstitial-clusters.md`
- `reports/proofs/20c-14/c1-m1-visual-led/run-constants-proof.json`
- `reports/proofs/20c-14/c1-m1-visual-led/pass2-envelope.json`
- `reports/proofs/20c-14/c1-m1-text-led/run-constants-proof.json`
- `reports/proofs/20c-14/c1-m1-text-led/pass2-envelope.json`
- `docs/parameter-directory.md`
- `state/config/parameter-registry-schema.yaml`
- `state/config/experience-profiles.yaml`
- `scripts/utilities/run_constants.py`
- `scripts/utilities/marcus_prompt_harness.py`
- `scripts/utilities/progress_map.py`
- `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py`
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
- `tests/test_run_constants.py`
- `tests/test_experience_profiles.py`
- `tests/test_marcus_prompt_harness.py`
- `tests/test_progress_map.py`
- `skills/bmad-agent-marcus/scripts/tests/test_prepare_irene_pass2_handoff.py`
- `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py`
- `tests/test_sprint_status_yaml.py`
