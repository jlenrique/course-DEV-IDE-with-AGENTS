# Story 27-3: Image Provider (Sensory-Bridges Integration)

**Epic:** 27 — Texas Intake Surface Expansion
**Status:** ratified-stub
**Sprint key:** `27-3-image-provider`
**Added:** 2026-04-17
**Points:** 3
**Depends on:** 27-2 must land first (atomic-write hygiene + transform-registry lockstep pattern).
**Blocks:** nothing.

## Story

As the Texas wrangler,
I want to accept image source files (`.jpg`, `.png`, `.webp`) via a `provider: image` directive and route them through `sensory-bridges` for perception-based extraction,
So that first-class visual sources (a roadmap image that IS the primary source for a learning-objective chain) flow through Texas's manifest + fidelity chain instead of being rejected with a binary-decode error.

## Background

Original defect from the 2026-04-17 Tejal trial preflight: a `.jpg`/`.png` dropped into a Texas directive with `provider: local_file` falls through to `read_text_file()` → binary decode error → FAILED manifest entry. The operator's workaround is `OPTIONAL_CONTEXT_ASSETS` in `run-constants.yaml`, which routes images via Marcus's context envelope — but that path is for **context**, not **source-of-truth visuals**.

Per operator direction (2026-04-17 backlog stub): Texas owns the intake surface; images must not be rejected; internal routing to sensory-bridges is the architecture (Option A).

## Acceptance Criteria (Stub Level)

- **AC-1:** `provider: image` registered in `transform-registry.md` and dispatched in `run_wrangler.py`.
- **AC-2:** Image dispatch routes through `skills/sensory-bridges/scripts/image_to_agent.py` (new helper) OR the existing `pdf_to_agent.py` pattern adapted for image inputs — architecture decision at create-story time.
- **AC-3:** Extraction output for an image row includes: structured perception output (caption, detected entities, text-in-image via OCR if present), tier classification, any detected-text heading structure.
- **AC-4:** New G0 fidelity criteria for visual sources: `visual_structural_fidelity`, `visual_completeness`. Integrate with existing G0 criteria — do not bifurcate the schema.
- **AC-5:** Transform-registry row with documented known-losses (OCR partial on stylized fonts, semantic-perception model limits).
- **AC-6:** New contract roles accepted in directive schema: `visual-primary`, `visual-supplementary`.
- **AC-7:** Cassette-backed tests for the perception model calls; synthetic image fixtures for OCR cases.
- **AC-8:** Lockstep check passes. Epic 27 AC-S spine satisfied.
- **AC-9:** No pytest regressions, no new skips.

## File Impact (Preliminary)

- `skills/bmad-agent-texas/scripts/run_wrangler.py` — `image` branch dispatch
- `skills/bmad-agent-texas/scripts/providers/image_provider.py` — new provider module
- `skills/sensory-bridges/scripts/image_to_agent.py` — new helper OR adapted from `pdf_to_agent.py`
- `skills/bmad-agent-texas/references/transform-registry.md` — add image row
- `tests/test_image_provider.py` — new
- `tests/fixtures/texas/images/` — new fixture directory

## Notes for Create-Story

- Decide at story-open time: new sibling helper vs. extension of existing `pdf_to_agent.py`.
- Fidelity-chain decision for `visual-primary` role requires Quinn-R input on audit implications.
- Perception model choice (OpenAI GPT-4V vs. Anthropic Claude vision vs. local CLIP-based): party-mode consultation warranted at create-story time if not already settled.

## Party Input Captured
- **Operator (backlog stub):** Option A (extend runner with image provider via sensory-bridges) adopted. Option C (reject images) withdrawn.
- **John (PM, Round 3):** bundled originally with 27-4 as "active-providers batch" at 3 pts; standalone promotion at this level for clarity.
