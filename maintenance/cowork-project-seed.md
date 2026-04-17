# Cowork Project Seed — course-DEV-IDE-with-AGENTS

> Condensed orientation for new Cowork chats. Upload this to the Project's **Files** section so every chat has it in context from the start. Refresh after major milestones (epic closures, architecture shifts, prompt-pack revs).
>
> Last refreshed: 2026-04-16

## What this repo is

A Python-based collaborative-intelligence infrastructure for producing narrated educational course content through a seven-gate fidelity pipeline. Agents are implemented as **skill directories** under `skills/bmad-agent-*`, each with SKILL.md, references, scripts, and a BMad memory sidecar. IDE-native by design (Cursor plugin packaging; `.claude/.cursor/.cline/.github/.agents` parallels).

Project name: `course-DEV-IDE-with-AGENTS`
Phase: 4 — Implementation (Wave 2B reviewed clean, Wave 4 in motion)
Active branch: `DEV/slides-redesign`

## Pipeline — what matters when

```
G0 Source Bundle (Source Wrangler)
 → G1 Lesson Plan (Irene Pass 1)
   → G1.5 Cluster Plan [cluster only]
   → G2 Slide Brief (Irene) ── HIL 1 ──
     → G3 Generated Slides (Gary)
     → G3.5 PNG Export Validation
     → G2.5 Cluster Coherence [cluster only] ── HIL 2 ──
       → [motion overlay: Gate 2M → Kira/Kling → Motion Gate]
       → G4 Narration Script + Segment Manifest (Irene Pass 2) ── HIL 3 ──
         → G5 Audio (ElevenLabs Voice Director)
           → G6 Composed Video (Compositor → Descript) ── HIL 4 ──
```

Three workflow variants share this spine: `standard`, `motion`, `cluster`. Each has a declarative parity manifest under `state/config/structural-walk/`. L1 contracts per gate live in `state/config/fidelity-contracts/g{n}-*.yaml`.

Operational checkpoints layered on top: Prompt 6B literal-visual packet (pre-G3), Storyboard A (post-G3, pre-HIL 2), Storyboard B (post-G4, pre-audio), creative-directive resolution (when `experience_profile` is set).

## Orchestration — two pillars plus quality/fidelity

- **Marcus** — execution orchestrator. "Is this done?"
- **Creative Director (CD)** — LLM agent; owns experience-profile resolution, `slide_mode_proportions`, `narration_profile_controls`, creative-directive artifacts. "Is this right?"
- **Quinn-R** — quality reviewer. "Is this good?"
- **Vera** — source-to-output fidelity assessor. "Is this faithful?"

Single-owner judgment per dimension; `docs/lane-matrix.md` is authoritative.

## Parameter governance — three families

Governed by `docs/parameter-directory.md` and `state/config/parameter-registry-schema.yaml`:

1. **Run Constants** — operational (`scripts/utilities/run_constants.py`).
2. **Narration-time** — Irene Pass 2 script controls.
3. **Assembly-time** — Compositor timing / G4 / G6.

CD directive is the bridge: experience-profile → concrete knobs → resolved into `run-constants.yaml` and `narration-script-parameters.yaml` before specialist delegation.

## Directory hierarchy (authority layers)

| Tier | Directory | Purpose | Who writes |
|---|---|---|---|
| 1 (authoritative) | `resources/style-bible/` | Brand, voice, accessibility | Humans only |
| 2 (operational) | `state/config/` | Runtime config, gate contracts, profiles, schemas | Marcus + scripts |
| 3 (fallback) | `config/` | Bootstrap defaults | Developer |

Higher tier wins. Agents inside Marcus's workflow never consult `config/` directly.

Supporting trees:
- `skills/` — agent and tool skills (SKILL.md + references/ + scripts/)
- `scripts/` — API clients, state management, utilities (including `slide_count_runtime_estimator.py`, `creative_directive_validator.py`, `structural_walk.py`)
- `state/runtime/` — ephemeral SQLite coordination DB (not git-versioned)
- `_bmad-output/` — planning artifacts, implementation artifacts, strategic decisions, sprint/workflow status
- `course-content/` — real source bundles and produced outputs
- `run-records/` — dated trial-run records
- `reports/structural-walk/` — architectural sanity reports
- `maintenance/` — operator protocols and audit scripts

## Current momentum (as of 2026-04-16)

- **Epic 23 closed** (cluster-aware narration; G4-16..19 codified in `g4-narration-script.yaml`).
- **Wave 2B reviewed clean:** stories 20c-3, 20c-9..14.
- **Wave 4 done:** `22-2` (Storyboard B cluster view), `20c-15` (profile-aware estimator).
- **Paused:** trial run `C1-M1-PRES-20260415` — Prompt 4 pause, stub `extracted.md` from 24-page PDF. Not resumable.
- **Next operator action:** fresh trial with prompt pack **v4.2f** (adds extraction-completeness validation + per-dimension evidence + Notion cross-validation hint + preamble reorder).
- **Test baseline:** 670 passed / 1 skipped / 27 deselected as of 2026-04-15 closure; 96 tests on the new estimator alone.
- **Future, not scheduled:** Source Wrangler agent evolution (vision in `_bmad-output/planning-artifacts/source-wrangler-agent-vision.md`) — current skill → trainable agent with Notion MCP cross-validation.
- **Deferred:** `20c-4/5/6` (reactivate only if profile runs expose composition/design gaps); `22-3/22-4` and Epic 24 queued; Epics 15–18 backlog.

## Known risks / ambient fragilities

- **Extraction completeness** is still only prompt-level. A script-level validator is the obvious next infra piece and would close the Source Wrangler failure mode that paused the last trial.
- **Notion cross-validation** depends on operators declaring PDFs as Notion exports. Source Wrangler agent would automate detection.
- **Preflight `--bundle-dir`** flag was skipped on the last trial; v4.2f preflight command must include it.
- **Contract ↔ code drift** is the single biggest architectural risk; structural walk is the guard.
- **Prompt-pack discipline:** act-mode agents will rubber-stamp gates with "PASS (0.95)" and no evidence if prompts don't explicitly require evidence sentences. v4.2f hardens this.

## Canonical protocols

- Session start: `bmad-session-protocol-session-START.md`
- Session wrapup: `bmad-session-protocol-session-WRAPUP.md`
- Doc harmonization: `maintenance/doc review prompt 2026-04-12.txt`
- Structural sanity: `python -m scripts.utilities.structural_walk --workflow {standard|motion|cluster}`
- Story closure (BMAD): AC satisfied → verification green → layered review complete → `done` in `sprint-status.yaml`

## Canonical reference docs (read in this order for orientation)

1. `docs/project-context.md`
2. `docs/structural-walk.md`
3. `docs/fidelity-gate-map.md`
4. `docs/lane-matrix.md`
5. `docs/directory-responsibilities.md`
6. `docs/parameter-directory.md`
7. `SESSION-HANDOFF.md` + `next-session-start-here.md`
8. `_bmad-output/implementation-artifacts/sprint-status.yaml`
