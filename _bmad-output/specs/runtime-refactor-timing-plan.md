# Runtime Refactor Timing Plan (Pre-4A-4)

Date: 2026-03-28
Owner: GPT-5.3-Codex (party-mode consensus synthesis)

## Purpose

Memorialize when and where to execute each course-runtime refactor recommendation (1-10), balancing delivery velocity for Story 4A-4 with runtime safety.

## Consensus Timing and Placement

| # | Recommendation | Where to refactor | Timing | Why this timing |
|---|---|---|---|---|
| 1 | Unify course-root helpers (`state/` walk vs `pyproject.toml`) | New shared paths utility in `scripts/utilities/` and callers in `skills/production-coordination/scripts/*.py`, `skills/bmad-agent-marcus/scripts/read-mode-state.py` | End of Epic 4A | High payoff but cross-cutting path behavior; safer after 4A-4 gate delivery. |
| 2 | Unify coordination DB path + connector policy | Shared connector module in `scripts/utilities/` (or production-coordination scripts package), then update `manage_run.py`, `log_coordination.py`, optional `read-mode-state.py` | End of Epic 4A | Moderate risk due to DB connection semantics (WAL policy and call-site assumptions). |
| 3 | Unify baton runtime paths + atomic JSON helpers | Shared baton runtime I/O helper module used by `manage_baton.py` and `manage_run.py` | End of Epic 4A | Newly-stabilized baton lifecycle should avoid structural churn right before 4A-4. |
| 4 | Make mode state JSON writes atomic | `skills/production-coordination/scripts/manage_mode.py` | Before 4A-4 | Low blast radius, immediate runtime safety gain against partial writes. |
| 5 | Replace `parents[3]`/`sys.path`/`load_dotenv` bootstrap duplication | Shared bootstrap helper under `scripts/utilities/` plus updates in skill scripts and related tests | Future Epic | High blast radius and import-path sensitivity; needs deliberate init-contract design. |
| 6 | Share style-guide `tool_parameters` loader | `scripts/utilities/` helper + wrappers in Gamma/ElevenLabs operations | End of Epic 4A | Useful dedup, but can subtly shift defaults if rushed. |
| 7 | Extract simple shallow merge helper (ElevenLabs only) | Local/shared small helper used by `skills/elevenlabs-audio/scripts/elevenlabs_operations.py` | Epic 4 | Low reward now; safe cleanup when touching related audio work. |
| 8 | Sensory bridges `if` chain -> registry map | `skills/sensory-bridges/scripts/bridge_utils.py` | End of Epic 4A | Small-medium maintainability gain; not currently blocking correctness. |
| 9 | Compositor root heuristic alignment/documentation | `skills/compositor/scripts/compositor_operations.py` + shared path docs | Epic 4 | Low urgency; defer until composition-focused changes. |
| 10 | API client inheritance/raw-HTTP drift audit | Audit scope: `scripts/`, `tests/`, `skills/*/scripts/`, `state/runtime/**/*.py` | Before 4A-4 | Low-risk governance check that catches client-boundary drift early. |

## "Now" Slice Executed Before 4A-4

### #4 Atomic mode state write

Implemented:
- `skills/production-coordination/scripts/manage_mode.py`
  - `_write_mode()` now writes to `mode_state.json.tmp` then atomically replaces target file.

Validation coverage added:
- `skills/production-coordination/scripts/tests/test_manage_mode.py`
  - Added assertion that no `.tmp` artifact remains after `set` operation.

### #10 Raw-HTTP drift audit (compact findings)

Audit method:
- Searched runtime script scope for direct HTTP usage patterns (`requests`, `httpx`, `urllib.request`).

Findings summary:
- Expected/approved base client usage: `scripts/api_clients/base_client.py`.
- Candidate exceptions to track (not auto-refactored in this slice):
  - `scripts/api_clients/kling_client.py` (CDN download helper)
  - `skills/gamma-api-mastery/scripts/gamma_operations.py` (signed export URL download)
  - `skills/sensory-bridges/scripts/audio_to_agent.py` (bridge-specific STT call)
  - `skills/source-wrangler/scripts/source_wrangler_operations.py` (generic URL ingestion)
  - `skills/pre-flight-check/scripts/preflight_runner.py` (`urllib` health checks)
- No immediate blocker found requiring pre-4A-4 code changes.

Recommended guardrail for next pass:
- Maintain an allowlist of intentional direct HTTP call sites and flag new call sites outside `scripts/api_clients/` during review.

## Pre-4A-4 Outcome

Proceed to Story 4A-4 after confirming targeted tests pass for mode-state write hardening.
