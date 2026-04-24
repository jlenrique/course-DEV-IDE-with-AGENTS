# Story: Wondercraft Specialist Agent

**Epic:** cross-cutting (leaf specialist agent — parallel to Kira/Kling and Voice Director/ElevenLabs)
**Status:** ratified-stub
**Sprint key:** `wondercraft-specialist-agent`
**Added:** 2026-04-24
**Points:** ~5 (stub estimate; expand at create-story)
**Depends on:** [5-4 Tier-2 API integrations](5-4-remaining-tier2-api-integrations.md) (done — Wondercraft client at [wondercraft_client.py](../../scripts/api_clients/wondercraft_client.py) exists as 152-LOC hardened surface).
**Blocks:** nothing hard; enables podcast and audio-first workflow-family work in Epic 18-5.

## Story

As the course production team,
I want a Wondercraft specialist agent that wraps the existing Wondercraft API client and produces podcast-quality audio assets (multi-voice dialogue, music-bedded narration, chapter-marked episodes),
So that Marcus can dispatch "make this lesson a podcast" or "add a podcast companion to this module" as a first-class capability, parallel to how Kira dispatches Kling video work and Voice Director dispatches ElevenLabs narration.

## Background

The Wondercraft API client was hardened in Story 5-4 (Tier-2 API integrations, done) but **no agent currently wraps it**. This leaves podcast-style production as raw API-call territory rather than a dispatchable capability.

Parallel pattern already established in repo:
- [Story 3-1](3-1-gamma-specialist-agent.md) — Gary wraps `gamma_client.py`
- [Story 3-3](3-3-kling-video-specialist-agent.md) — Kira wraps `kling_client.py`
- [Story 3-4](3-4-elevenlabs-specialist-agent.md) — Voice Director wraps `elevenlabs_client.py`

The Wondercraft specialist completes this pattern for the audio-production surface. It is a **leaf specialist** (no flow-control responsibilities; no orchestrator event emission; no Lesson Plan log writes) — maximally LangGraph-portable.

## Story Scope

Produce the agent skill + capability cards + dispatch wiring + tests. Scope does **not** include the `18-5 Podcasts workflow family` discovery work, though this story's close unblocks that discovery in a concrete way (the agent exists to consume whatever the discovery defines).

## Acceptance Criteria (Stub Level)

- **AC-1:** New agent skill at `skills/bmad-agent-wondercraft/` following BMB sanctum shape (Epic 26 conformance): SKILL.md (specialist-tier, ≤60 lines), sanctum scaffolded at `_bmad/memory/bmad-agent-wondercraft/`.
- **AC-2:** Agent name/persona: operator-chosen at create-story; stub name placeholder is **Winston-Podcast** (operator naming ratified by 26-series convention).
- **AC-3:** Capability cards authored for:
  - `podcast_episode_produce` — single-host monologue episode from narration script
  - `podcast_dialogue_produce` — multi-voice interview/discussion format
  - `audio_summary_produce` — short recap/summary audio
  - `music_bed_apply` — apply background music bed to existing audio
  - `chapter_markers_emit` — generate chapter-marked output with metadata
  - `audio_assembly_handoff` — emit assembly guide for Descript finish (manual-tool pattern, paralleling 24-2 Descript guide)
- **AC-4:** Agent delegates API calls to existing `scripts/api_clients/wondercraft_client.py`; **no new HTTP layer**. Extends client only if Wondercraft API surface area missing for a capability card.
- **AC-5:** Marcus dispatch registry ([dispatch-registry.yaml](../../skills/bmad-agent-marcus/references/dispatch-registry.yaml) from Sprint 1 PR-R) extended with Wondercraft edges for each capability card. L1 dispatch-lockstep check passes.
- **AC-6:** Voice-match tuning — when Wondercraft agent is invoked on a lesson that already has ElevenLabs narration, it consults Voice Director's voice selection so podcast variant maintains vocal identity (if operator opts in via dial).
- **AC-7:** Fidelity contract: Wondercraft-produced audio consumed by Vera's G5 audio fidelity verification (existing Epic 2A pattern) — no new gate, existing G5 handles audio sources generically.
- **AC-8:** Cassette-backed tests for capability-card invocations; live-smoke test for one episode production gated behind env var (live Wondercraft API cost).
- **AC-9:** **Portability guard (AST contract test):** agent must not import `marcus.orchestrator.*`, must not write to `lesson_plan.log`. Leaf-specialist discipline.
- **AC-10:** Pre-flight-check integration: Wondercraft API key readiness surfaced alongside existing tool-readiness checks.
- **AC-11:** Lockstep check passes. No pytest regressions.

## File Impact (Preliminary)

- `skills/bmad-agent-wondercraft/SKILL.md` — **new**, BMB-conformant specialist tier
- `skills/bmad-agent-wondercraft/references/` — capability cards, prompt-pack, handoff patterns
- `skills/bmad-agent-wondercraft/scripts/` — agent-side helpers (thin wrappers on `wondercraft_client.py`)
- `skills/bmad-agent-wondercraft/tests/` — agent-specific tests
- `_bmad/memory/bmad-agent-wondercraft/` — sanctum (via BMB scaffold v0.2, per 26-4)
- `scripts/api_clients/wondercraft_client.py` — **extend only if needed** for AC-3 capabilities (chapter markers, music beds)
- `skills/bmad-agent-marcus/references/dispatch-registry.yaml` — add Wondercraft edges
- `tests/cassettes/wondercraft/*.yaml` — cassette library
- `tests/wondercraft/test_specialist_dispatch.py` — **new**
- `tests/contracts/test_wondercraft_portability_guard.py` — **new** AST guard for AC-9
- `scripts/validators/check_dispatch_registry_lockstep.py` — regression coverage for new edges
- `skills/pre-flight-check/references/check-strategy-matrix.md` — Wondercraft API-key row

## Notes for Create-Story

- **Agent-birth via BMB scaffold v0.2** (per Epic 26): use `scripts/utilities/init-sanctum.py` to scaffold the agent conformantly. Scaffold preservation (Story 26-5, still backlog) not required for first-birth since no prior operator edits exist.
- **Capability-card authorship (Paige):** parallel to Kira's cards (kling-video capability cards are the nearest template). Voice assignment + music-bed selection are the novel surfaces.
- **Wondercraft API exploration:** [wondercraft_client.py](../../scripts/api_clients/wondercraft_client.py) is 152 LOC; confirm at create-story whether it covers chapter-markers + music-bed + multi-voice dialogue, or whether client-extension is needed (extensions must be minimal and covered by new tests).
- **Operator voice-match tuning (AC-6):** optional in v1 per Sally UX input; dial name TBD at create-story (candidate: `audio_voice_continuity: true/false` in run-constants).
- **LangGraph portability:** AC-9 AST guard is load-bearing. This story is explicitly shaped as a leaf specialist for the hybrid Python/LangGraph runtime — classifier/dispatch node in, audio-asset out.

## Party Input Expected at Create-Story

- **Winston** — dispatch-registry shape; capability-card contract
- **Amelia** — dev-story task breakdown; K-floor (expect ~14-18); scaffold adoption per Epic 26 discipline
- **Murat** — cassette-vs-live test boundaries; cost-gated live smoke
- **Paige** — capability-card authorship; agent SKILL.md ceiling (specialist ≤60 lines per 26-2/26-3 precedent)
- **Sally** — operator dial + UX for voice-continuity option; naming persona

## Open Questions for Party-Mode

1. Should Wondercraft agent subsume `elevenlabs`-based podcast production too (one podcast agent, two engines), or stay Wondercraft-only (with Voice Director delegated to for ElevenLabs segments)? Default posture: **Wondercraft-only, delegate ElevenLabs segments to Voice Director** — preserves existing specialist boundaries.
2. Persona name — operator to choose at create-story. Placeholder "Winston-Podcast" is tongue-in-cheek; real name needed.
3. Agent sequence in Sprint 2 — parallel-safe with everything else (Box, Notion, image providers, reading-path repertoire). Confirm at green-light.
