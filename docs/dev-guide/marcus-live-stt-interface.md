# Marcus Live STT Interface

## Integration seams used

- `Facade.run_4a(..., intake_callable=...)` in `marcus/facade.py` is the stable voice-entry seam.
- `IntakeCallable` in `marcus/orchestrator/loop.py` is preserved exactly; voice is implemented as an adapter, not a loop rewrite.
- `scripts/utilities/marcus_live_stt.py` runs an interactive STT session without changing pipeline-manifest lockstep.
- `marcus/orchestrator/voice_interface.py` is the new sidecar module for chunked STT orchestration.

## MVP voice session architecture

1. Capture one short audio chunk per turn (`chunk_provider` callback).
2. Transcribe chunk with `ElevenLabsChunkTranscriber`.
3. Parse transcript into one `ScopeDecision` + rationale with `VoiceDecisionParser`.
4. Confirm transcript in terminal.
5. On low confidence or parse failure, retry up to `max_attempts_per_unit`.
6. If retries fail, fall back to typed input and continue `run_4a`.

This supports near-real-time interaction while keeping all existing Marcus event logging and lock behavior unchanged.

## Delivery effort bands

- **MVP (implemented in this change)**: 6-9 days
  - Chunked STT adapter
  - Transcript parser + confidence gating
  - Interactive fallback path
  - Unit tests
- **Production hardening**: +6-9 days
  - Better observability (latency, confidence, retry outcomes)
  - Better retry/backoff + network error policy
  - Deterministic integration tests around external STT calls
- **Advanced low-latency streaming**: +8-12 days
  - True bidirectional transport with incremental hypotheses
  - Turn arbitration and interruption handling
  - Session-level QoS and backpressure controls

## Test strategy

- Unit tests in `tests/test_marcus_voice_interface.py` cover:
  - transcript parsing (valid and ambiguous decisions),
  - confidence threshold behavior,
  - retry + fallback behavior,
  - STT payload normalization.
- Existing Marcus loop contract tests remain the primary non-regression gate:
  - `tests/test_marcus_4a_loop.py`
  - `tests/test_marcus_facade_4a.py`
  - pipeline/event lockstep checks.
- Recommended next phase:
  - add an integration test that runs `Facade.run_4a` with a stub chunk provider and mocked STT adapter end-to-end.

