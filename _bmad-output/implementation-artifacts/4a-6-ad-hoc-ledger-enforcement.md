# Story 4A-6: Ad-Hoc Mode Ledger & Learning Boundary (Enforcement)

**Status:** done  
**Epic:** 4A  
**PRD:** FR91  
**Sprint key:** `4a-6-ad-hoc-ledger-enforcement`

## Source of truth

Full acceptance criteria and design notes: `_bmad-output/planning-artifacts/epics.md` → **Story 4A-6**.

## Dependencies

- **Story 4A-5:** Observability and cache records must carry `run_mode` so aggregations can exclude ad-hoc (see same epic, Story 4A-5).
- **Epic 4 / Story 4.4:** Production intelligence rollups must filter on `run_mode` (called out in Story 4.4 AC).

## Delivered

1. Fail-closed persistence policy for ad-hoc mode.
- Implemented centralized enforcement utility: `scripts/utilities/ad_hoc_persistence_guard.py`.
- Enforced no-op/blocked durable write behavior across:
	- `skills/production-coordination/scripts/manage_run.py`
	- `skills/production-coordination/scripts/log_coordination.py`
	- `skills/quality-control/scripts/quality_logger.py`
	- `skills/production-coordination/scripts/observability_hooks.py`

2. Ad-hoc lifecycle remains runnable without production ledger mutation.
- Implemented transient run store and resume behavior in `state/runtime/ad-hoc-runs/`.
- Ad-hoc observability persisted transiently in `state/runtime/ad-hoc-observability/`.

3. Sidecar and learning boundary respected.
- Reporting learning-capture path now honors ad-hoc guard and skips durable pattern writes in ad-hoc.

4. Tests lock representative boundary paths.
- Added/updated tests for ad-hoc no-op behavior and transient paths:
	- `skills/production-coordination/scripts/tests/test_log_coordination.py`
	- `skills/production-coordination/scripts/tests/test_manage_run.py`
	- `skills/production-coordination/scripts/tests/test_quality_gate_coordinator.py`

5. Normative contract doc added.
- `docs/ad-hoc-contract.md` created with invariants and enforcement surface.
