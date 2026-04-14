# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> Current objective: Build parameter registry, Creative Director agent, and two extreme experience profiles (Visual-Led + Text-Led). Cluster maturity and creative control develop in parallel through profile-driven trial runs.

## Current State (as of 2026-04-14)

- Active branch: `DEV/slides-redesign`
- Wave 1 (Foundation): COMPLETE — 158 consolidated tests.
- Wave 2A (Cluster Maturity): 20c-1 slice 1 done (10 templates), 20c-2 DONE (selector complete), 20c-3 compressed to static density configs. 229 total tests.
- Wave 2B (Creative Control): NEW — 8 stories (20c-7 through 20c-14) added for parameter registry, CD agent, profiles, and resolver.
- A/B trials: SKIPPED — replaced by experience-profile-driven trial runs (Party Mode consensus 2026-04-14).
- 20c-4/5/6 and 23-1: DEFERRED — reactivate after profile runs reveal specific gaps.
- Pass 2 mode: `structural-coherence-check` (Epic 23 not yet implemented)
- Sprint status test passes. YAML parses clean.

## Immediate Next Action

1. Stay on `DEV/slides-redesign`.
2. **Primary: Execute Wave 2B stories in dependency order:**
   - **20c-7** Parameter Audit & Registry Schema (no deps — START HERE)
     - Catalog all existing parameters across 3 families (Run Constants, Narration-time, Assembly-time)
     - Create `docs/parameter-directory.md` — master reference for CD, specialists, and operators
   - **20c-8** Assembly Timing Parameters (deps: 20c-7)
   - **20c-9** Narration Parameter Expansion (deps: 20c-7, parallel with 20c-8)
   - **20c-10** Creative Director Agent Creation via bmad-agent-builder (deps: 20c-7)
   - **20c-11** Creative Directive Schema & Writer (deps: 20c-10)
   - **20c-12** Experience Profile Definitions — Visual-Led + Text-Led (deps: 20c-8, 9, 10)
   - **20c-13** Profile Resolver Wiring (deps: 20c-12, 20c-3)
   - **20c-14** E2E Validation against C1-M1 with both profiles (deps: 20c-13)
3. **Parallel:** Complete 20c-1 remaining slices (runtime selection integration) and 20c-3 (static density configs) as Wave 2A cluster maturity work.
4. If `sprint-status.yaml` changes, run `.venv\Scripts\python.exe -m pytest -q tests/test_sprint_status_yaml.py`.

## Key Architecture Decisions (Party Mode 2026-04-14)

- **Three parameter families:** Run Constants (operational switches/budgets), Narration-time (how Irene writes scripts), Assembly-time (how Compositor arranges timing)
- **Creative Director agent:** LLM agent (not deterministic resolver) — second pillar alongside Marcus. Owns creative frame, parameter orchestration, gate-triggered review ("is this right?" vs Quinn-R's "is this good?")
- **CD interaction model:** Option B — params for deterministic executors (ElevenLabs, Compositor) + params AND structured creative briefs for LLM interpreters (Irene, Gary). All through Marcus's envelope system, no side-channels.
- **CD→Irene brief:** Minimal (~200 tokens): tone_reference, arc_shape, kill_list, coupling_intent, source_authority. Validated against narration-script-parameters.yaml before dispatch. Irene's perception drives specifics.
- **Two extreme profiles as proof of concept:** Visual-Led (compelling visuals, VO as gifted presenter) and Text-Led (slide being read with intention). Five key differentiators: narrator_source_authority, slide_echo, slide_content_density, ElevenLabs.style, variability_scale.
- **Parameter directory document:** `docs/parameter-directory.md` — master reference ("bible") for CD, specialists, and HIL operators.

## Key Risks / Unresolved Issues

- **Clustering quality unvalidated without A/B trials:** Profile-driven runs at 20c-14 serve as integration test. If clustering produces incoherent groupings, it will be visible in profile output. Reactivate deferred stories (20c-4, 23-1) as needed.
- **CD agent is the bottleneck:** 20c-10 requires a focused bmad-agent-builder session. Everything before is setup; everything after is wiring.
- **Irene Pass 2 complexity:** Adding CD creative briefs to Irene's already-complex input set (perception + params + cluster plan + fidelity). Priority order: source fidelity → parameter constraints → visual-motion coherence → creative directive.
- **Template scoring weights:** Still initial defaults in `cluster_template_selector.py`. Profile runs will reveal calibration needs.

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
- `docs/parameter-directory.md` (new — master parameter reference)
- `tests/test_sprint_status_yaml.py`
