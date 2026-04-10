# Story 4.1: Production Run Lifecycle Management

Status: done

## Summary

Extended lifecycle tooling with run preset policy hydration, cross-run linkage persistence, run context entity generation, and resume support across default and ad-hoc mode.

## Acceptance Coverage

1. Run records created in SQLite with purpose, context, and status.
- Implemented in manage_run create path (default mode).

2. YAML run context entities are created in state/config.
- Implemented via skills/production-coordination/scripts/run_context_builder.py and create hook.

3. Stage completion updates run state and timestamps.
- Implemented in advance/checkpoint/approve/complete paths.

4. Interrupted runs can be resumed.
- Implemented in resume command for default and ad-hoc transient runs.

5. Cross-run context links previous runs for course/module.
- Implemented via context_json link list and run_context_links DB persistence when schema is available.

6. Run presets configure gate strictness.
- Preset policy is loaded from state/config/tool_policies.yaml and attached to run context.

## Files

Created:
- skills/production-coordination/scripts/run_context_builder.py

Modified:
- skills/production-coordination/scripts/manage_run.py
- scripts/state_management/db_init.py
