# Canvas Specialist — Learned Patterns

Append-only in default mode. Read-only in ad-hoc mode.

## Institutional Baseline

### 2026-03-30 — Founding policy

- Accessibility pre-check is a hard gate before any Canvas write operation.
- Return confirmation URLs for every deployment attempt (including warnings).
- Verify module structure after publish; report missing or out-of-order modules explicitly.

## Woodshed Lessons

### 2026-03-29 — Canvas L1 snapshot hardening

- Woodshed runtime must hydrate `.env` before invoking API clients outside pytest.
- Reproduction loader must support `scripts.api_clients.*` import paths.
- Course snapshot helper should return structured `status: error` payloads for invalid IDs or API failures.

## Operator Targeting Requirements

### 2026-03-29 - Term and course targeting must be first-class

- Real deployments need a term-aware survey mode to show "what is there" before writes.
- Provide an interactive menu-based select path: term -> courses -> target course.
- Provide a direct input path that accepts term descriptor plus course ID for fast execution.
- Require explicit target confirmation before any write-capable deployment operation.
