# Dev-Support Agents: Strategic Vision

> **Historical note (2026-04-16):** Paths of the form `<old>-specialist-sidecar/` and `bmad-agent-marcus-sidecar/` were renamed to persona-named sidecars. See `_bmad/memory/` for current paths.

> Captured: 2026-04-16. Not yet scheduled. First pass for operator review.
> Companion artifact to `maintenance/doc review prompt 2026-04-12.txt`, which is the best existing articulation of what these agents need to do.

## Current State

The APP has mature **production-side** orchestration — Marcus (SPOC), CD (creative frame), Irene (pedagogy), Gary/Kira/Voice Director/Compositor (tool execution), Vera (source fidelity), Quinn-R (quality), Desmond (Descript handoff). Each owns a single lane per `docs/lane-matrix.md`.

The **dev-side** equivalent is enforced procedurally, not agentically:

- `python -m scripts.utilities.structural_walk --workflow {standard|motion|cluster}` — deterministic architectural-drift detector, exit 0 = READY
- BMAD closure discipline — AC + automated verification + layered code review + remediated review record → `done` in `sprint-status.yaml`
- `bmad-session-protocol-session-START.md` / `session-WRAPUP.md` — session rituals
- `SESSION-HANDOFF.md` + `next-session-start-here.md` — hot-start pair
- `maintenance/doc review prompt 2026-04-12.txt` — operator-invoked doc-harmonization sweep
- `docs/directory-responsibilities.md` as scope-identifying spine
- `docs/parameter-directory.md` paired with `state/config/parameter-registry-schema.yaml` as lockstep contract

No **agent** owns invoking these. The operator does, or the session-protocol files do, or — sometimes — nothing does. As the platform grows, that asymmetry compounds: production-side drift is caught at Vera; dev-side drift accumulates silently until a trial run fails for a reason the doc-harmonization sweep should have caught a week earlier.

## Problem Statement

APP is an ever-growing collection of agents, skills, contracts, schemas, docs, and tests. Coherence among those artifacts is currently preserved by:

1. The operator's memory and discipline
2. A narrative dated-update log in `docs/project-context.md`
3. A procedural prompt (`doc review prompt 2026-04-12.txt`) that is good in planning intent but mechanically incomplete — see the six gaps audited on 2026-04-16: no structural-walk invocation, wall-clock change-window, no explicit L1-contract sync, no lane-matrix coverage check, no hot-start-pair update, no fixed report home

That works at today's scale. It will not at tomorrow's. The project has deliberately built **mechanical drift-detection infrastructure** (structural walk, L1 gate contracts, parameter-registry schema, lane-matrix coverage, BMAD closure checklist) and under-uses it because no agent is accountable for invoking it on a defined cadence.

This is the meta-layer mirror of the production-side asymmetry that led to Vera: *"Agents cannot verify what they cannot perceive."* For dev-side artifacts, no agent currently perceives the repo as a coherent whole.

## Vision: Two Dev-Support Agents

Symmetric with the production side's Marcus/Vera pattern, not proliferating to four.

### Cora — Dev-Session Orchestrator *(working name)*

The Marcus-analog for dev sessions. SPOC for session-boundary activity, doc-harmonization runs, and pre-closure checks. Owns **"is the repo ready for the next unit of work?"**

- Operator is the primary invoker. Cora greets on session START, wraps on session WRAPUP, and accepts on-demand `/harmonize` or `/coherence-check` invocations.
- Marcus is **Cora-aware**: when the HIL operator asks Marcus for a harmonization or regression sweep mid-run, Marcus routes to Cora through the existing context-envelope pattern. Cora returns a structured coherence report; Marcus never authors that judgment directly, just as CD authors creative directives on Marcus's behalf.
- Cora delegates deterministic work to Audra (see below) and agentic work (prose drift, intent-of-change) to itself or party-mode consultants.
- Cora writes to the hot-start pair (`SESSION-HANDOFF.md` + `next-session-start-here.md`) at session WRAPUP; no other agent does.

### Audra — Internal-Artifact Fidelity Auditor *(working name)*

The Vera-analog for *internal* artifacts (code-to-doc, contract-to-contract, schema-to-directory). Owns **"are the load-bearing artifacts still in lockstep with each other?"**

- Produces a trace-report output in the same O/I/A shape Vera uses, but applied to repo-internal relations:
  - **Omission** — a story closed in `sprint-status.yaml` without one of the four BMAD closure artifacts, a new parameter in the schema without a row in `parameter-directory.md`, a new skill without a `Lane Responsibility` section.
  - **Invention** — a doc references a file, script, or flag that does not exist (or no longer does).
  - **Alteration** — a contract row and its doc narrative describe different things; two sources-of-truth have drifted.
- Runs the deterministic sweep first (structural walk, reference resolution, schema lockstep, coverage checklist) and the agentic sweep second (prose drift on recently-changed docs). This preserves the hourglass model: deterministic neck first, agentic top after.

### Naming

Working names only. The production-side roster is Marcus/Irene/Gary/Kira/Vera/Quinn-R/Desmond/CD. Dev-side candidates considered: **Cora** (coherence/core), **Nora** (norm/normalization), **Lex** (lockstep) for the orchestrator; **Audra** (audit), **Justus** (justice/verification), **Lux** (illumination) for the auditor. Bikeshed at build time.

## Invocation Model

| Trigger | Path | Produces |
|---|---|---|
| Operator opens dev session | Cora on session START hook | Welcome packet: hot-start-pair summary, git-log diff since last handoff, sprint-status delta, Audra baseline sweep result |
| Operator closes dev session | Cora on session WRAPUP hook | Closeout packet + updated `SESSION-HANDOFF.md` + updated `next-session-start-here.md` |
| Operator invokes `/harmonize` on demand | Cora direct invocation | Full doc-harmonization run per the six-gap-closed prompt (see below) |
| Story about to flip to `done` in `sprint-status.yaml` | Audra pre-closure hook | Closure-artifact audit: AC present, automated verification logged, layered review present, remediated review record present |
| HIL asks Marcus mid-run for a coherence check | Marcus → Cora via context envelope | Scoped coherence report returned to Marcus for operator relay |
| CI (future) | Audra headless | Structural-walk exit code + lockstep report, suitable for pre-merge gate |

Operator is the primary invoker in every row. Marcus routes on behalf of the HIL when asked. CI is explicitly future.

## Relationship to Installed BMAD Agents

The BMAD installation under `_bmad/` ships several built-in agents (see `_bmad/_config/agent-manifest.csv` for the canonical registry). Two of them are directly relevant and must be accounted for before standing up Cora and Audra:

**`bmad-tea` — Murat, Master Test Architect** (`_bmad/tea/agents/bmad-tea`). Risk-based testing, fixture architecture, ATDD, CI/CD governance, scalable quality gates, contract testing. Murat's domain is *production code under test* — test suites, quality gates on behavior, CI discipline. This is adjacent to Audra, not identical. Audra's domain is **internal-artifact lockstep** — do the docs, contracts, schemas, and registries still describe the code, and do they describe each other consistently? Two candidate resolutions:

- **Option A (distinct lanes, explicit boundary).** Audra is new. Murat owns "does the code still work?" (test suites, regression, CI). Audra owns "do the load-bearing artifacts still describe the code?" (lockstep, references, directory placement). The lane matrix gets two rows, clearly fenced. *Recommended.*
- **Option B (Audra as Murat specialization).** Extend Murat with a dev-artifact-lockstep capability. Slower to stand up, higher lane-collision risk, and Murat's identity is strongly test-engineering-shaped, so the fit would be uncomfortable.

Pick Option A unless party-mode review surfaces a reason to collapse. Murat should still be routed to for the **regression** half of "harmonization + regression checking" — structural-walk is cheap architectural regression, but actual test-suite regression on a story-done transition is Murat's lane, not Audra's.

**`bmad-agent-tech-writer` — Paige, Technical Documentation Specialist** (`_bmad/bmm/1-analysis/bmad-agent-tech-writer`). CommonMark, DITA, diagram discipline, audience-aware prose. This is the tech writer the `doc review prompt 2026-04-12.txt` refers to when it says "consult with a BMAD party mode team, including their tech writer agent." Paige is already installed; the dev-support agents should **route to Paige for prose-polish party-mode consults**, not duplicate her. Cora's L2 prose-drift pass can be done by Cora directly for small changes and routed to Paige for substantial doc reworks.

Other installed agents worth noting as optional party-mode consultants: **Winston (architect)** for lane-matrix and hourglass-integrity review, **Amelia (dev)** for story-closure artifact audits where the issue is code-structural rather than doc-structural, **Mary (analyst)** when a harmonization run surfaces an actual requirements gap.

Namespace note: `_bmad/cis/skills/bmad-cis-agent-creative-problem-solver` is **Dr. Quinn**, which is not the same as this project's **Quinn-R** (`skills/bmad-agent-quality-reviewer`). Keep them distinct in Cora/Audra references.

## Lane Matrix Additions

Two new rows in `docs/lane-matrix.md`:

| Judgment Dimension | Owner | Scope | NOT Owned By |
|---|---|---|---|
| Dev-session orchestration and repo coherence | Cora | Session START/WRAPUP choreography, doc-harmonization routing, hot-start-pair maintenance, pre-closure hook choreography | Marcus, specialist agents, Audra |
| Internal-artifact lockstep and regression audit | Audra | Structural-walk invocation, L1-contract ↔ parameter-directory ↔ schema lockstep, lane-matrix coverage checklist, BMAD closure-artifact audit, doc-to-code reference resolution, prose-drift detection on changed docs | Vera (source fidelity — different lane), Quinn-R (quality standards — different lane), Marcus (production orchestration — different lane), Cora (orchestration, not judgment) |

Note the deliberate non-overlap with Vera (production-artifact source fidelity) and Quinn-R (production-artifact quality). Audra's domain is the **repo about itself**.

## L1 / L2 / L3 Decomposition

Clean three-layer model cut per `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md`.

### L1 Deterministic Contracts (Audra runs first, never gets wrong)

- `scripts.utilities.structural_walk --workflow {standard|motion|cluster}` → exit code 0
- Reference resolution: every path/file/flag named in a doc must exist
- Parameter lockstep: every row in `parameter-directory.md` resolves to a schema entry in `state/config/parameter-registry-schema.yaml`, and vice versa
- Gate-contract lockstep: every gate referenced in a doc has a matching `state/config/fidelity-contracts/g{n}-*.yaml`
- Lane-matrix coverage: every skill listed in the `Lane Responsibility Coverage Checklist` actually contains a `Lane Responsibility` section
- BMAD closure-artifact audit: stories `done` in `sprint-status.yaml` have AC + automated verification + layered review + remediated review record
- Placement audit: recently-created files are placed per `docs/directory-responsibilities.md` (operational state not in `config/`, brand identity not in `state/config/`)
- Git-anchored change window: `git diff --stat <anchor>..HEAD` where `<anchor>` defaults to the most recent `SESSION-HANDOFF.md` commit

### L2 Agentic Evaluation (Cora and Audra, judgment required)

- Prose drift: does a dated update in `docs/project-context.md` still describe what the code does?
- Intent-of-change: a story changed the parameter registry but didn't touch `parameter-directory.md` — real gap or internal schema move?
- Doc-to-code narrative alignment: the Marcus SKILL.md describes a capability that the scripts no longer support
- Pruning candidates in `parameter-directory.md`: parameters present but not referenced by any validator or consumer

### L3 Learning Memory (memory sidecars)

Following the memory-system pattern from Marcus (`_bmad/memory/bmad-agent-marcus-sidecar/`):

- `_bmad/memory/cora-sidecar/` — session chronology, operator preferences for harmonization depth, which files drift most often
- `_bmad/memory/audra-sidecar/` — drift-velocity patterns, which contracts have been brittle, which kinds of stories tend to leave closure-artifact gaps, which authors generate which kinds of drift

Memory should capture only what `git log` and `git blame` cannot. Snapshot state is git's job; *patterns* are the sidecar's.

## Architecture Sketch

Following the conventions documented in `.agents/skills/bmad-agent-builder/references/` (quality-dimensions.md, agent-type-guidance.md, standard-fields.md). Both agents are **Memory agents** per the agent-type gradient — they need to remember across sessions.

```
skills/bmad-agent-cora/
├── SKILL.md                             # identity, capabilities table, on-activation, lane responsibility
├── references/
│   ├── memory-system.md                 # sidecar discipline (mirror Marcus's pattern)
│   ├── save-memory.md
│   ├── init.md                          # first-run onboarding
│   ├── session-start-protocol.md        # welcome-packet generation
│   ├── session-wrapup-protocol.md       # hot-start-pair update
│   ├── harmonization-protocol.md        # six-gap-closed version of doc-review prompt
│   └── delegation-to-audra.md           # context envelope Cora → Audra
└── scripts/
    ├── session_start_packet.py          # deterministic welcome-packet builder
    ├── session_wrapup_packet.py         # hot-start-pair reconciler
    └── tests/
        └── ...

skills/bmad-agent-audra/
├── SKILL.md                             # identity, lane responsibility, trace-report format
├── references/
│   ├── memory-system.md
│   ├── save-memory.md
│   ├── init.md
│   ├── lockstep-contracts.md            # which artifacts move together
│   ├── deterministic-sweep.md           # L1 checks catalog
│   ├── agentic-sweep.md                 # L2 checks catalog
│   └── trace-report-format.md           # O/I/A adapted for internal artifacts
└── scripts/
    ├── dev_coherence_sweep.py           # single-command L1 runner, exit code contract
    ├── check_closure_artifacts.py       # BMAD-done audit
    ├── check_parameter_lockstep.py      # parameter-directory ↔ schema
    ├── check_lane_coverage.py           # lane-matrix checklist
    └── tests/
        └── ...

_bmad/memory/cora-sidecar/
├── index.md
├── patterns.md
├── chronology.md
└── access-boundaries.md

_bmad/memory/audra-sidecar/
├── index.md
├── patterns.md
├── chronology.md
└── access-boundaries.md
```

Both SKILL.md files stay under the ~250-line guideline from `quality-dimensions.md`. Long detail lives in `references/`.

## SKILL.md Conformance Checklist (per BMAD quality dimensions)

Applied to both agents:

- [ ] Frontmatter: `name:` and `description:` (5-8 word summary + "Use when user says 'X' or 'Y'.")
- [ ] `## Lane Responsibility` section that names the single lane and explicitly what the agent does **not** own
- [ ] `## Identity` — role, title, communication style
- [ ] `## Principles` — ~10 grounded principles (mirror Marcus pattern)
- [ ] `## Does Not Do` — explicit scope fence (critical for avoiding leaky necks in the meta layer)
- [ ] `## On Activation` — config load, memory-system load, access-boundaries load, sidecar load, mode/session-state read
- [ ] `## Capabilities` — Internal Capabilities table (code, capability, route) + External Skills table
- [ ] Outcome-driven prompts (what, not how), intelligence placement (scripts handle plumbing, prompts handle judgment), progressive disclosure (references for detail)
- [ ] Path construction: `{project-root}` for project-scope, `./` for skill-internal
- [ ] Quality scan candidate reports land under `skills/reports/bmad-agent-{cora,audra}/quality-scan/` (mirror Marcus pattern)

## Migration Path

1. **Phase 1 — Vision review (this doc).** Operator review and party-mode pressure test. Open questions to resolve: naming, exact lane boundaries with Vera/Quinn-R/Marcus, **whether Audra is distinct from `bmad-tea` (Murat) or a specialization of it — Option A recommended**, whether pre-closure hook blocks or warns, whether Cora's L2 prose-drift pass routes to Paige (`bmad-agent-tech-writer`) by default.
2. **Phase 2 — Codify the L1 sweep.** Build `scripts/utilities/dev_coherence_sweep.py` as a single-command runner covering every L1 check. Exit code contract: 0 = READY, 1 = remediation required (same pattern as structural walk). This script ships *before* Audra and becomes Audra's deterministic core.
3. **Phase 3 — Audra skill directory.** Thin agentic wrapper over the L1 sweep plus the L2 prose-drift pass. Memory sidecar with access-boundaries.md read-only to most of the repo, write-only to its own sidecar + run-scoped trace reports under `reports/dev-coherence/`.
4. **Phase 4 — Cora skill directory.** Session-boundary orchestrator with Audra delegation. Memory sidecar. Writes to the hot-start pair only (tight access-boundary scope).
5. **Phase 5 — Marcus awareness.** Add Cora to Marcus's `External Specialist Agents` table with the HIL-request invocation path. Add one Marcus principle covering when to route to Cora vs. handle in-run.
6. **Phase 6 — Pre-closure hook.** Instrument `sprint-status.yaml` transition-to-done with an Audra check. Start in **warn** mode; promote to **block** only after one full wave of experience validates the signal quality.
7. **Phase 7 — Memory curation.** Once patterns accumulate, condense periodically (same discipline as existing sidecars).

## Risks and Unresolved Issues

**Leaky necks in the meta layer.** Audra must run L1 deterministic checks *strictly first* and never use agentic judgment to skip them. Same anti-pattern the production side avoids; easier to commit in the meta layer because the operator often knows "it's fine." Mitigation: the L1 sweep is a script with an exit code contract. Audra's agentic pass runs only after L1 returns 0.

**Redundancy with git.** Memory sidecars should capture patterns, not snapshots. Snapshots are git's job. Access-boundaries.md must forbid sidecars from storing file-content copies.

**Lane overlap with Vera and Quinn-R.** Vera owns *source-to-output* (G0–G5 production artifacts); Quinn-R owns *quality standards* on production artifacts. Audra owns *internal artifacts* only — the repo about itself. The lane-matrix entries must be unambiguous or we create the exact leaky-neck we are trying to prevent.

**Who writes the hot-start pair.** Today the operator updates these manually at session boundaries. Cora writing them means the operator loses that forcing function. Mitigation: Cora writes, operator reviews before session close — same party-mode pattern that governs production artifact approval.

**Cost of agents that run every session.** Session-START/WRAPUP hooks invoke Cora every session. Token cost is real. Mitigation: L1 sweep is deterministic (cheap); L2 agentic pass is scoped to recently-changed docs (git-diff-bounded, small).

**Closure-hook block vs. warn.** A `block` on `sprint-status.yaml` transitions could halt the operator on a false positive. Phase 6 starts in warn-only to calibrate.

**Naming bikeshed.** Captured. Not blocking.

## Operator Decisions — 2026-04-16

Recorded here so the design record matches what was actually built.

**Names — Cora and Audra, confirmed.** "Cora" (Dev-Session Orchestrator) and "Audra" (Internal-Artifact Fidelity Auditor) are the built-and-shipped names. The existing Canva specialist also named "Cora" is slated for rename during P0 remediation of the custom-agent roster; the dev-session orchestrator has priority on the name.

**Audra-vs-Murat lane resolution — Option A (distinct lanes with explicit boundary).** Murat owns "does the code still work under test?" — production-side regression and test-engineering judgment. Audra owns "do the load-bearing artifacts still describe the code?" — internal-artifact lockstep and prose-drift detection. The boundary is stated explicitly in Audra's SKILL.md Lane Responsibility section and mirrored in `docs/lane-matrix.md` (additions pending).

**Pre-closure hook starts in warn mode.** Audra's closure-artifact audit returns `warn` on gaps but never blocks `sprint-status.yaml` transitions. The operator still flips stories; Audra surfaces what's missing so nothing closes silently-incomplete. Phase 6 revisits whether to upgrade any dimension to block-level after warn-mode data accumulates.

**Paige confirmed as party-mode prose consultant.** When Audra's L2 pass surfaces a finding that warrants substantial prose rework (beyond paragraph scope), the finding carries `route_offered: bmad-agent-tech-writer` in the trace report. Cora relays, operator decides whether to route.

**Party mode stays BMAD-stock-only — separation of concerns.** `_bmad/_config/agent-manifest.csv` continues to list only BMAD-provided agents (Mary, Paige, John, Sally, Winston, Amelia, Carson, Dr. Quinn, Maya, Victor, Caravaggio, Sophia, Murat). Our custom roster — including Cora and Audra — is **intentionally NOT registered** in the manifest. Rationale: BMAD party mode's value is independent multi-agent review with bounded scope; mixing our specialty agents into that roster would dilute the review lens and couple our agent lifecycle to BMAD's. Custom agents are invoked directly by the operator or routed through Marcus (production side) / Cora (dev side). A dedicated specialty-agent party mode for our custom roster is possible future work but not in this vision's scope.

**Validation tier — Tier 1 + Tier 2 executed; Tier 3 authored, not yet executed.** Initial validation for Cora and Audra is (1) static conformance against the Marcus template and (2) single-turn behavioral smoke tests for activation, lane awareness, and out-of-lane refusal. Multi-turn scripted scenarios (session-START-to-WRAPUP for Cora; deterministic-first full-sweep for Audra) are authored in the test guides under `tests/agents/bmad-agent-{cora,audra}/interaction-test-guide.md` and will be executed on demand, not as part of the initial build.

**Custom-agent naming convention — human persona names required.** Every custom agent in our roster should carry a short, human, persona-style name (e.g., "Marcus", "Irene", "Cora", "Audra"). During P0/P1 remediation of existing custom agents, any agent that lacks a persona name gets one. After the naming pass, a dedicated propagation run (Cora coordinates; Audra audits the lockstep of old-name → new-name references across repo) ensures no dangling references remain.

## Source Seeding for Audra's Checklist

`maintenance/doc review prompt 2026-04-12.txt` plus the 2026-04-16 six-gap audit on that prompt become Audra's initial L1/L2 catalog seed:

1. `git diff --stat <session-handoff-anchor>..HEAD` for scope (L1)
2. Run structural walk for each implicated workflow, capture exit code (L1)
3. Verify parameter-directory ↔ parameter-registry-schema ↔ gate-contracts lockstep (L1)
4. Verify lane-matrix coverage checklist (L1)
5. Verify hot-start-pair freshness against session anchor (L1)
6. Verify report home exists at `reports/dev-coherence/YYYY-MM-DD-HHMM/` (L1)
7. Prose-drift pass on cha