# Qualtrics Specialist - Learned Patterns

Append-only in default mode. Read-only in ad-hoc mode.

## Foundational Policy

### 2026-03-29 - Objective traceability baseline

- Every assessment item requires learning_objective_id.
- Any objective without at least one item blocks publish.
- Dry-run validation must be used before write-capable operations.

## Woodshed Lessons

### 2026-03-29 - L1 survey inventory snapshot

- Snapshot helper should reject malformed page_size values (including booleans).
- Dry-run must validate question types and choice schemas with parity to execute mode.
- Retained exemplar artifacts should redact account and survey identifiers before commit.
