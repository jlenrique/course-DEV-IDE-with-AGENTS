# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> Current objective: Continue Wave 2B contract-to-runtime path by wiring profile resolver flow (`20c-13`) after today’s registry/CD schema/profile groundwork.

## Current State (as of 2026-04-14 closeout)

- Active branch: `DEV/slides-redesign`
- Wave 1 (Foundation): COMPLETE — 158 consolidated tests.
- Wave 2A (Cluster Maturity): 20c-1 slice 1 done (10 templates), 20c-2 DONE (selector complete), 20c-3 compressed to static density configs. 229 total tests.
- Wave 2B (Creative Control): actively executing.
- `20c-7`: done (parameter registry + directory + tests)
- `20c-8`: done (assembly timing parameters + validators/tests)
- `20c-9`: in-progress (slice expansion implemented: narration profile control set broadened and validated)
- `20c-10`: in-progress (CD contract-first scaffold + strict `slide_mode_proportions` validation path)
- `20c-11`: in-progress (creative directive schema artifacts + validator path and tests)
- `20c-12`: in-progress (bootstrap experience profile definitions + tests)
- `20c-13`: ready-for-dev (next critical implementation step)
- A/B trials: SKIPPED — replaced by experience-profile-driven trial runs (Party Mode consensus 2026-04-14).
- 20c-4/5/6 and 23-1: DEFERRED — reactivate after profile runs reveal specific gaps.
- Pass 2 mode: `structural-coherence-check` (Epic 23 not yet implemented)
- Sprint status test passes. YAML parses clean.

## Immediate Next Action

1. Stay on `DEV/slides-redesign`.
2. Implement `20c-13` profile resolver wiring:
   - Resolve selected `experience_profile` to canonical `slide_mode_proportions` and narration profile controls.
   - Propagate resolved values into run-constants/runtime flow for Marcus path.
   - Add deterministic tests for valid profile mapping, unknown profile rejection, and propagation correctness.
3. Keep `20c-10/11/12` artifacts as contract source-of-truth while wiring resolver behavior.
4. If `sprint-status.yaml` changes, run `.venv\Scripts\python.exe -m pytest -q tests/test_sprint_status_yaml.py`.

## Key Architecture Decisions (Party Mode 2026-04-14)

- **Three parameter families:** Run Constants (operational switches/budgets), Narration-time (how Irene writes scripts), Assembly-time (how Compositor arranges timing)
- **Creative Director agent:** LLM agent (not deterministic resolver) — second pillar alongside Marcus. Owns creative frame, parameter orchestration, gate-triggered review ("is this right?" vs Quinn-R's "is this good?")
- **CD interaction model:** Option B — params for deterministic executors (ElevenLabs, Compositor) + params AND structured creative briefs for LLM interpreters (Irene, Gary). All through Marcus's envelope system, no side-channels.
- **CD→Irene brief:** Minimal (~200 tokens): tone_reference, arc_shape, kill_list, coupling_intent, source_authority. Validated against narration-script-parameters.yaml before dispatch. Irene's perception drives specifics.
- **Two extreme profiles as proof of concept:** Visual-Led (compelling visuals, VO as gifted presenter) and Text-Led (slide being read with intention). Five key differentiators: narrator_source_authority, slide_echo, slide_content_density, ElevenLabs.style, variability_scale.
- **Parameter directory document:** `docs/parameter-directory.md` — master reference ("bible") for CD, specialists, and HIL operators.

## Key Risks / Unresolved Issues

- **Resolver integration risk:** `20c-13` must avoid drift between `experience-profiles.yaml`, creative directive schema, and run-constants consumer expectations.
- **Scope hygiene risk:** Ambient unrelated worktree noise exists; keep next implementation commits narrowly scoped to intended resolver files.
- **End-to-end proof still pending:** Contract-level and validator-level hardening is complete, but runtime propagation proof is not complete until `20c-13` and `20c-14`.

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

## Ambient Workspace State

These files were present in the worktree before this session and are not owned by this closeout:

- deleted: `bmad-session-protocol-session-MISC.md`

## Hot-Start Files

- `SESSION-HANDOFF.md`
- `next-session-start-here.md`
- `bmad-session-protocol-session-START.md`
- `bmad-session-protocol-session-WRAPUP.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `docs/parameter-directory.md`
- `state/config/parameter-registry-schema.yaml`
- `state/config/experience-profiles.yaml`
- `state/config/schemas/creative-directive.schema.json`
- `state/config/schemas/creative-directive.schema.yaml`
- `scripts/utilities/run_constants.py`
- `scripts/utilities/creative_directive_validator.py`
- `tests/test_run_constants.py`
- `tests/test_creative_directive_schema.py`
- `tests/test_creative_directive_validator.py`
- `tests/test_experience_profiles.py`
- `tests/test_sprint_status_yaml.py`
