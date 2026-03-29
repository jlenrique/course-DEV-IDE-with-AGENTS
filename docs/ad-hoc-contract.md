# Ad-Hoc Mode Contract

## Purpose

Ad-hoc mode is a sandbox execution boundary. It allows full workflow rehearsal while preventing institutional ledger updates and long-lived learning writes.

Primary references:
- _bmad-output/planning-artifacts/epics.md (Story 4A-6)
- skills/bmad-agent-marcus/references/mode-management.md
- skills/bmad-agent-marcus/references/conversation-mgmt.md

## Invariants

1. No durable production ledger writes in ad-hoc mode.
- Blocked/no-op operations include production runs, coordination audit records, quality gate ledger writes, and observability DB writes.
- Enforcement utility: scripts/utilities/ad_hoc_persistence_guard.py.

2. Ad-hoc run lifecycle is transient.
- Run state is stored under state/runtime/ad-hoc-runs/.
- Default lifecycle writes continue to use SQLite only in default mode.

3. Ad-hoc observability is transient and tagged.
- Every observability event carries run_mode.
- Ad-hoc events are written to state/runtime/ad-hoc-observability/ as JSONL.

4. Course-progress intelligence excludes ad-hoc.
- Comparative and trend calculations must filter out ad-hoc runs.
- Observability rollups and production intelligence use run_mode filtering.

5. Sidecar learning is disabled in ad-hoc mode.
- No pattern or chronology persistence from ad-hoc runs.
- Only transient ad-hoc session sections are allowed.

6. User-facing behavior remains complete.
- Ad-hoc runs still execute QA checks and return conversational summaries.
- Blocking applies to durability, not to quality evaluation.

7. Ambiguous mode-state policy is explicit.
- `RUN_MODE_AMBIGUOUS=lenient` (default) preserves legacy fail-open resolution to `default` when mode state is missing/corrupt.
- `RUN_MODE_AMBIGUOUS=strict` fails closed to `ad-hoc` when mode state is missing/corrupt/invalid.

## Enforcement Surface

- scripts/utilities/ad_hoc_persistence_guard.py
- skills/production-coordination/scripts/manage_run.py
- skills/production-coordination/scripts/log_coordination.py
- skills/quality-control/scripts/quality_logger.py
- skills/production-coordination/scripts/observability_hooks.py
- skills/production-coordination/scripts/run_reporting.py

## Test Expectations

Minimum coverage:
- Mode detection and operation allow/block matrix.
- Representative forbidden write paths (coordination audit, quality gate DB, run ledger).
- Ad-hoc transient lifecycle persistence path.
- Reporting exclusion of ad-hoc in comparative rollups.
