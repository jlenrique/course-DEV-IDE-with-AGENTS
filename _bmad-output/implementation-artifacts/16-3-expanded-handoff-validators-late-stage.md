# Story 16.3: Expanded Handoff Validators for Late-Stage Transitions

**Epic:** 16 — Bounded Autonomy Expansion
**Status:** backlog
**Sprint key:** `16-3-expanded-handoff-validators-late-stage`
**Added:** 2026-04-06
**Depends on:** Existing validator patterns from Stories 11.2-11.4 (Gary outbound, Irene Pass 2, theme-mapping). Can parallel with Stories 16.1-16.2.

## Summary

Extend deterministic validator coverage from the well-covered Gary/Irene handoffs to all remaining high-cost pipeline transitions: Irene Pass 1 output, Quinn-R pre-composition input, ElevenLabs write-back, compositor manifest readiness, and final composition bundle. Each validator is fail-closed and produces structured reports.

## Goals

1. Irene Pass 1 output bundle integrity validator.
2. Quinn-R pre-composition input completeness validator.
3. ElevenLabs write-back completeness and path integrity validator.
4. Compositor manifest readiness validator.
5. Final composition bundle completeness validator.
6. Integration with existing gate coordinator.

## Existing Infrastructure To Build On

- `scripts/utilities/validate_source_bundle_confidence.py` — existing source bundle validator pattern
- Gary outbound contract validation from Story 11.2 — `gamma_operations.py` contract validators
- Irene Pass 2 dual-input validator from Story 11.3 — perception grounding enforcement
- Theme-mapping handshake validator from Story 11.4 — parameter validation pattern
- `scripts/utilities/structural_walk.py` — structural validation engine with pass/fail reporting
- `scripts/utilities/app_session_readiness.py` — readiness check pattern (imports, state, DB sanity)
- `skills/compositor/` — compositor skill (assembly guide generation, manifest reading)
- `skills/elevenlabs-audio/` — ElevenLabs audio skill (write-back fields: audio path, timestamps, VTT)
- Quality gate coordination from Story 4-2 — gate entry/exit criteria enforcement

## Key Files

- `scripts/utilities/handoff_validators.py` — new: late-stage handoff validation functions
- `skills/production-coordination/` — update: wire validators into gate transitions

## Acceptance Criteria

1. `validate_irene_pass1_output(bundle)` — checks lesson plan completeness, slide brief completeness, learning objective coverage, required fields present.
2. `validate_quinn_pre_composition_input(run_dir)` — checks all segments reviewed, all audio assets present, all visual assets present, manifest fully populated.
3. `validate_elevenlabs_writeback(segment_manifest)` — checks audio file existence at declared paths, timestamp validity, VTT monotonicity, segment coverage completeness.
4. `validate_compositor_manifest_readiness(manifest)` — checks all write-back fields populated, all referenced assets exist and are downloadable, motion assets present for motion-designated segments.
5. `validate_final_composition_bundle(bundle_dir)` — checks assembly guide present, all audio referenced by guide exists, all visual assets referenced exist, captions/VTT present.
6. Each validator is fail-closed: missing or invalid inputs block the transition.
7. Each validator produces structured report: `{validator, status, findings[{field, issue, severity}]}`.
8. Validators integrate with existing gate coordinator.
9. Unit tests cover each validator with realistic pass and fail scenarios (at least 3 pass + 3 fail per validator).
