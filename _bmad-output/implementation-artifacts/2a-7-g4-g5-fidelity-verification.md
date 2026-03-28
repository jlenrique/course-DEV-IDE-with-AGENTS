# Story 2A-7: G4-G5 Fidelity — Script & Audio Verification

Status: done

## Story

As a course content producer,
I want the Fidelity Assessor to verify narration script fidelity against the actual slides (G4) and audio fidelity against the narration script (G5),
So that what the learner hears accurately matches what they see, and what was spoken matches what was written.

## Tasks / Subtasks

- [x] Task 1: Extend gate evaluation protocol for G4 (6 criteria: 2 deterministic, 4 agentic) and G5 (5 criteria: 2 deterministic, 3 agentic, all perception-required)
- [x] Task 2: Update Vera SKILL.md gate coverage (G4, G5 now Active — Vera covers G0-G5)
- [x] Task 3: Update Marcus delegation flow (Vera at G4 after Irene P2/before Quinn-R, G5 after ElevenLabs/before Kira) + specialist registry (6 Vera entries)
- [x] Task 4: Add 6 interaction test scenarios (21-26): G4 pass, visual accuracy failure, terminology inconsistency, G5 pass, script accuracy failure, audio invention
- [x] Task 5: 38 contracts valid, parity check PASS, no regressions

## Dev Agent Record

### Agent Model Used
Claude claude-4.6-opus (via Cursor)
### Completion Notes List
- G4: 6 criteria (slide correspondence, visual accuracy via perception_artifacts, assessment exactness, terminology consistency, no invention, manifest alignment)
- G5: 5 criteria (STT script accuracy <5% WER, WPM 130-170, pronunciation accuracy, no hallucinated audio, duration ±15%)
- Vera now covers G0-G5 (30 criteria across 6 gates). Only G6 (composition) remains future.
- Marcus pipeline: Vera inserted at G4 (after Irene P2, before Quinn-R/Gate 3) and G5 (after ElevenLabs, before Kira)
- Marcus specialist registry: 6 Vera entries (G0-G5)
- 6 new interaction test scenarios (total now 26)
### File List
**Modified:**
- `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md` (G4/G5 criteria, source loading, remediation targets)
- `skills/bmad-agent-fidelity-assessor/SKILL.md` (G4/G5 Active in gate coverage)
- `skills/bmad-agent-fidelity-assessor/references/fidelity-trace-report.md` (elevenlabs-voice-director in remediation_target)
- `skills/bmad-agent-marcus/references/conversation-mgmt.md` (pipeline graph, remediation_target)
- `skills/bmad-agent-marcus/SKILL.md` (specialist registry: G4, G5 entries)
- `tests/agents/bmad-agent-fidelity-assessor/interaction-test-guide.md` (6 new scenarios)
### Change Log
- 2026-03-28: Story 2A-7 — Vera extended to G4 (narration vs slides) and G5 (audio vs script) with STT-based verification
