# Story 12.1: Dual-Dispatch Infrastructure

**Epic:** 12 — Double-Dispatch Gamma Slide Selection
**Status:** backlog
**Sprint key:** `12-1-dual-dispatch-infrastructure`
**Added:** 2026-04-05
**Depends on:** All existing epics complete. Extends `gamma_operations.py` and `gary_slide_output` contract.

## Summary

Extend `gamma_operations.py` to support a `double_dispatch` mode that executes two independent Gamma generate calls per slide position, producing two distinct visual treatments. This is the foundational infrastructure for the entire double-dispatch epic.

## Goals

1. Add `double_dispatch` boolean to `run-constants.yaml` (default: `false`).
2. When enabled, `execute_generation()` dispatches two independent API calls per slide position.
3. Both exports downloaded with variant labeling (`_variant_A.png`, `_variant_B.png`).
4. Extend `gary_slide_output` with `dispatch_variant` field.
5. Zero regression when flag is `false`.

## Key Files

- `skills/gamma-api-mastery/scripts/gamma_operations.py` — dual-dispatch loop in `execute_generation()`
- `state/config/run-constants.yaml` — `double_dispatch` parameter
- `skills/bmad-agent-gamma/SKILL.md` — Gary reference updates for variant handling

## Acceptance Criteria

1. `run-constants.yaml` gains `double_dispatch: boolean` (default: `false`).
2. When `double_dispatch: true`, `execute_generation()` makes two independent Gamma API calls per slide position (separate calls, not retries).
3. Both exports downloaded with variant labeling: `{slide_id}_variant_A.png`, `{slide_id}_variant_B.png`.
4. `gary_slide_output` records gain `dispatch_variant: "A" | "B"` field.
5. Provenance (`literal_visual_source`) tracked independently per variant.
6. When `double_dispatch: false` (default), behavior is identical to current single-dispatch — zero regression.
7. Unit tests cover dual-dispatch path with mocked API responses.

## Party Mode Consensus (2026-04-05)

- Per-run flag, not per-slide.
- Two calls are independent dispatches (not retries of the same call).
- Both variants carry independent provenance tracking.
