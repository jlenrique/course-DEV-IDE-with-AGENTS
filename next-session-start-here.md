# Next Session Start Here

## Immediate Next Action

**Create and implement Story 2A-4: Fidelity Assessor Agent — Foundation (G2-G3)**

This is the most substantial story in Epic 2A. It requires:
1. Creating the Fidelity Assessor agent via `bmad-agent-builder` (six-phase discovery)
2. Implementing G2 evaluation (slide brief vs. lesson plan fidelity checking)
3. Implementing G3 evaluation (generated slides vs. slide brief, using PPTX and image sensory bridges)
4. Building the Fidelity Trace Report output format (Omissions/Inventions/Alterations)
5. Implementing the circuit breaker and operating policy
6. Integrating with Marcus's delegation flow

Story file needs to be created first (2A-4 is still `backlog` — no detailed story file exists yet). Use the epic AC from `_bmad-output/planning-artifacts/epics.md` (search for "Story 2A-4") as the source for the detailed story file.

---

## Current Status — Epic 2A: 3/9 stories DONE

| Story | Status | Key Deliverables |
|-------|--------|-----------------|
| **2A-1** | DONE | Fidelity audit baseline, 7 L1 contracts (38 criteria), `validate_fidelity_contracts.py`, `docs/app-design-principles.md`, `docs/fidelity-gate-map.md` (role matrix, operating policy) |
| **2A-2** | DONE | 5 sensory bridges (pptx, image, audio, pdf, video) at `skills/sensory-bridges/`, canonical perception schema, confidence rubric, universal perception protocol, validator handoff spec, 34 tests |
| **2A-3** | DONE | `source_ref` fields in 5 live templates (lesson plan, slide brief, narration script, segment manifest, context envelope), `docs/source-ref-grammar.md`, delegation protocol updated |
| **2A-4** | BACKLOG | Fidelity Assessor agent — next to implement |
| **2A-5 through 2A-9** | BACKLOG | G0-G1 fidelity, agent perception upgrades, G4-G5, drift tracking, maturity audit skill |

**Story 3.11** remains ON HOLD pending Epic 2A's G2-G3 coverage.

---

## Critical Discoveries This Session

**APP Design Principles established (Party Mode + Gemini synthesis):**
- **Three-Layer Intelligence Model:** L1 deterministic contracts (invariant), L2 agentic evaluation (evolves), L3 learning memory (compounds)
- **Hourglass Model:** Wide cognitive → narrow deterministic neck → wide cognitive
- **Leaky Neck Diagnostic:** Intelligence must not enforce constraints that can be deterministic
- **Sensory Horizon:** Agents cannot verify what they cannot perceive

**GOLD document:** `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md` — the synthesized architecture from both teams. Treat as authoritative for Epic 2A implementation.

**Key implementation decisions:**
- PPTX bridge is the **primary deterministic path** for G3 text verification (exact text objects, not OCR)
- ElevenLabs Scribe v2 STT is the audio bridge (word-level timestamps, keyterm prompting, ≤5% WER English, accepts video files directly)
- `python-pptx` added to `requirements.txt`
- All sensory bridges use a canonical request/response JSON schema — no free-form output
- Confidence calibration rubric defines operational meaning of HIGH/MEDIUM/LOW per modality
- Fidelity-control vocabulary (Story 2A-8) will replace free-text `additionalInstructions` for literal slides

**10 implementer-grade findings were addressed** in Stories 2A-1 through 2A-9 (perception schema, confidence rubric, source_ref grammar, fidelity-control vocabulary, Gary-Irene handoff normalization, role matrix, validator integration, scanned PDF gap, operating policy, drift resolver).

---

## Branch

**`dev/story-3.11-mixed-fidelity`** (note: branch was created for 3.11 but now carries Epic 2A work)

**Startup:** `git checkout dev/story-3.11-mixed-fidelity`

---

## Key File Paths for Story 2A-4

| File | Role |
|---|---|
| `_bmad-output/planning-artifacts/epics.md` | Epic 2A story ACs (search "Story 2A-4") |
| `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md` | GOLD document — Fidelity Assessor spec |
| `state/config/fidelity-contracts/` | L1 contracts the Assessor evaluates against |
| `skills/sensory-bridges/` | Bridges the Assessor invokes for G3 perception |
| `docs/fidelity-gate-map.md` | Role matrix, operating policy, gate definitions |
| `docs/app-design-principles.md` | Three-Layer Model, Hourglass, design principles |
| `docs/source-ref-grammar.md` | source_ref format the Assessor resolves |
| `skills/bmad-agent-content-creator/references/template-slide-brief.md` | G2 source of truth |
| `skills/bmad-agent-gamma/references/context-envelope-schema.md` | G3 output contract |
| `skills/bmad-agent-quality-reviewer/references/review-protocol.md` | Quinn-R's dimensions (boundary reference) |
| `skills/bmad-agent-marcus/references/conversation-mgmt.md` | Marcus delegation flow to update |

## Gotchas

- **Branch name mismatch:** Branch is `dev/story-3.11-mixed-fidelity` but we're working Epic 2A — this is intentional, the branch was repurposed
- PowerShell doesn't support `&&` chaining — use `;` or sequential commands
- Python 3.13 is the active interpreter (pyenv), not the 3.10 in `.pyenv/versions/3.10.5`
- `skills/` directories use hyphens (e.g., `sensory-bridges`) which are invalid Python package names — use `conftest.py` with `importlib.util.spec_from_file_location` for test imports (see `skills/sensory-bridges/scripts/tests/conftest.py` for pattern)
- 2 pre-existing test failures: venv detection (running outside venv) and style guide `brand` key — not regressions
- Gamma credits: 7,290 remaining
