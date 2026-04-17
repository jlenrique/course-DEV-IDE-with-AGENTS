# Cowork Project Instructions — course-DEV-IDE-with-AGENTS

> Paste the content below (everything inside the `--- BEGIN / --- END` fences) into the **Instructions** field of the Cowork Project. Keep this file as the canonical source; edit it here and re-paste when it changes.

--- BEGIN INSTRUCTIONS ---

You are supporting development of **course-DEV-IDE-with-AGENTS**, a Python-based multi-agent system for producing narrated educational course content through a G0–G6 fidelity pipeline. The repo is connected as the project's working folder; read files directly from it rather than relying on uploaded copies.

## Sources of Truth (respect this hierarchy)

- `_bmad-output/implementation-artifacts/sprint-status.yaml` — authoritative story/epic state. Do not contradict it without a flagged reason.
- `docs/project-context.md` — rolling narrative and dated update log. Use the most recent dated update as current status.
- `docs/directory-responsibilities.md` — governs where things live; read this first before any doc-harmonization or placement decision.
- `docs/structural-walk.md` — canonical "what matters when" map of the pipeline; uses G0–G6 plus workflow-specific manifests under `state/config/structural-walk/`.
- `docs/fidelity-gate-map.md` — gate definitions, HIL choreography, L1 contract pointers.
- `docs/lane-matrix.md` — single-owner judgment lanes (Marcus / CD / Quinn-R / Vera / specialists).
- `docs/parameter-directory.md` + `state/config/parameter-registry-schema.yaml` — parameter lifecycle. Update the directory and the schema in the same change set.
- `SESSION-HANDOFF.md` and `next-session-start-here.md` — rolling hot-start pair; always consult at session start.

## Orchestration Model (respect the lanes)

- **Marcus** — execution orchestrator; "is this done?"
- **Creative Director (CD)** — LLM agent; experience-profile resolution and creative directives; "is this right?"
- **Quinn-R** — quality reviewer; "is this good?"
- **Vera** — fidelity assessor; "is this faithful to source?"
- Do not cross lanes without calling it out. The lane matrix enforces single owner per judgment dimension.

## Parameter Families

Three families, all governed by `parameter-registry-schema.yaml`:

1. **Run Constants** (operational, `run_constants.py`) — frozen at run start.
2. **Narration-time** (Irene Pass 2 script controls).
3. **Assembly-time** (Compositor timing, G4/G6 contracts).

## Protocols and Rituals

- **Session rituals:** follow `bmad-session-protocol-session-START.md` and `bmad-session-protocol-session-WRAPUP.md`.
- **Doc harmonization:** follow `maintenance/doc review prompt 2026-04-12.txt`. Always read `directory-responsibilities.md` first.
- **Structural sanity:** `python -m scripts.utilities.structural_walk --workflow {standard|motion|cluster}` after contract, prompt-pack, or orchestration changes.
- **Closure discipline:** BMAD story closure requires acceptance criteria, automated verification, layered code review, and a remediated review record — then `done` in `sprint-status.yaml`.

## Default Branch and Context

- Active development branch: `DEV/slides-redesign`.
- Current operator focus: fresh trial run using prompt pack v4.2f after the paused C1-M1-PRES-20260415 trial (stub extraction).
- Source Wrangler agent evolution is a future epic (`_bmad-output/planning-artifacts/source-wrangler-agent-vision.md`); captured but not scheduled.

## Working Style

- Prefer repo file reads over re-uploading content. The folder is connected.
- When making edits, respect directory responsibilities — do not put operational state in `config/`, brand identity in `state/config/`, or vice versa.
- Flag when a task wants full BMAD party-mode fidelity (multi-agent review including tech writer): Cowork mode can simulate this via subagents, but real party mode belongs in Cursor + Claude Code where the `.claude/.cursor/` skill bundles load as addressable agents. Recommend 1M context mode for full-repo harmonization runs.
- When delivering files, share them as `computer://` links into the connected folder so they're immediately openable.
- Before multi-step work, ask clarifying questions about scope and deliverable form. Do not charge into doc-harmonization or trial runs without confirming the time anchor and output location.

## What Good Looks Like

- Changes that keep `sprint-status.yaml`, `project-context.md`, `parameter-directory.md`, and the relevant L1 gate contracts in lockstep.
- Explicit evidence for each gate dimension (no bare PASS/FAIL), per prompt pack v4.2f.
- Structural walk exit code `0` (READY) before claiming architectural work is done.

--- END INSTRUCTIONS ---
