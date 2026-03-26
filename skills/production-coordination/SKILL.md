---
name: production-coordination
description: "Manage production run lifecycle — create runs, advance stages, coordinate checkpoints, and track completion. Use when Marcus needs to initiate, track, or finalize a content production workflow."
---

# Production Coordination

## Purpose

This skill manages the lifecycle of content production runs — from creation through stage progression, human checkpoint gates, and completion. It bridges Marcus's conversational workflow management with persistent state in the SQLite coordination database.

Marcus invokes this skill when a user initiates a production run, when stages complete, when checkpoint gates need recording, and when runs finalize.

## Capabilities

| Action | Description | Script |
|--------|-------------|--------|
| Create run | Initialize a new production run with stages, specialist assignments, and metadata | `./scripts/manage_run.py create` |
| Advance stage | Move a run to its next workflow stage | `./scripts/manage_run.py advance` |
| Record checkpoint | Mark a stage as awaiting human review | `./scripts/manage_run.py checkpoint` |
| Record approval | Record user approval and advance past a checkpoint | `./scripts/manage_run.py approve` |
| Complete run | Finalize a run with completion timestamp | `./scripts/manage_run.py complete` |
| Query status | Get current run state as JSON for conversational reporting | `./scripts/manage_run.py status` |
| List runs | List active or recent production runs | `./scripts/manage_run.py list` |

## Usage from Marcus

Marcus invokes these commands through his CM (Conversation Management) capability when orchestrating production workflows. The script outputs JSON that Marcus translates into natural conversational updates.

**Typical flow:**
1. User requests content → Marcus parses intent, calls `generate-production-plan.py`
2. User approves plan → Marcus calls `manage_run.py create` with the plan's stages
3. Each stage completes → Marcus calls `manage_run.py advance`
4. Human checkpoint reached → Marcus calls `manage_run.py checkpoint`, presents work for review
5. User approves → Marcus calls `manage_run.py approve`
6. All stages done → Marcus calls `manage_run.py complete`

| Log delegation | Record specialist delegation events for tracking | `./scripts/log_coordination.py log` |
| Query history | View coordination events for a run | `./scripts/log_coordination.py history` |

## References

- `./references/workflow-lifecycle.md` — Stage transition rules, dependency management, recovery procedures
- `./references/run-state-schema.md` — SQLite schema reference, JSON status envelope format
- `./references/delegation-protocol.md` — Context envelope spec, specialist matching, graceful degradation
