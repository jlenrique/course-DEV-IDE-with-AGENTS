# Epic 4 & 4A Implementation — Adversarial Review and Formal Remediation

**Project:** course-DEV-IDE-with-AGENTS  
**Scope:** Completed stories for Epic 4A (Agent Governance, Quality Optimization & APP Observability) and Epic 4 (Workflow Coordination & State Infrastructure).  
**Review basis:** Python CLIs under `skills/production-coordination/scripts/`, `scripts/utilities/` (guard + archive), `skills/sensory-bridges/scripts/perception_cache.py`, `scripts/state_management/db_init.py`, and governance docs — not every markdown change in the branch.

---

## Part A — Status snapshot (at review time)

### Epic 4A

Per `_bmad-output/implementation-artifacts/sprint-status.yaml`, Epic 4A is marked **done** with all six stories **done**: 4A-1 run baton, 4A-2 lane matrix, 4A-3 envelope governance, 4A-4 agent QA release gate, 4A-5 perception caching / observability, 4A-6 ad-hoc ledger enforcement. `bmm-workflow-status.yaml` aligns with that narrative.

### Epic 4

The same sprint file shows Epic 4 as **done** with stories 4-1 through 4-5 all **done** (production run lifecycle, quality-gate coordination, content-entity management, production intelligence / reporting, export / platform deployment).

**Note:** If work continues operationally after YAML is marked complete, treat that as follow-on outside sprint file tracking.

### BMM program phase

Implementation phase may remain `in-progress` at the program level; next planned work may resume Epic 3 (e.g. 3.6) or Epic 5 per prioritization.

---

## Part B — Adversarial review narrative

### Critical / high severity

1. **Ad-hoc mode still writes canonical run YAML before the ledger guard**  
   `manage_run` builds run context via `run_context_builder.build_run_context`, which **always** creates `state/config/runs/<run_id>/` YAML files. That happens **before** `enforce_ad_hoc_boundary("production_run_db", ...)` in the create path.  
   `ad_hoc_persistence_guard` does **not** name an operation for those YAML writes, so **FR76-style “suppress institutional config writes in ad-hoc” is not fully enforced** at the automation layer. Anyone relying on ad-hoc for “no footprint” can still leave versioned-adjacent config tree artifacts.

2. **Governance is boundary-based, not database-enforced**  
   `enforce_ad_hoc_boundary` only runs in the touched scripts. **Direct SQLite edits**, other scripts, or agents writing `state/` **bypass** the guard. That is acceptable for a v1, but it is a **real compliance gap** if the epic intent was “system shall” rather than “these CLIs shall.”

3. **Mode resolution fails open to `default`**  
   Missing or corrupt `mode_state.json` → `default`, so **production persistence is allowed** when state is ambiguous. Adversarial reading: safer for availability, weaker for “regulated” guarantees.

4. **Run baton: multiple “active” batons and TOCTOU**  
   “Latest active” is chosen by scanning files; **nothing prevents two active batons** for different `run_id`s. **No file locks** on baton updates. **`cmd_check_specialist` with no baton returns `proceed`** — baton discipline is **opt-in**; forgetting `init` silently weakens authority (4A-1 story risk).

5. **Perception cache: lost-update race**  
   `PerceptionCache.get` / `put` is **read–modify–write** JSON without locking. Parallel writers can drop entries (4A-5).

### Medium severity

6. **Deployment story is largely orchestration + placeholders**  
   `_platform_urls` uses `canvas.example` / `coursearc.example`. Fine as scaffolding, but **4-5 is not “integrated deployment”** — it is **structured logging and URL-shaped placeholders**. Easy to mistake for production-ready LMS export.

7. **Silent degradation on policy load**  
   `quality_gate_coordinator._load_policies` uses `except Exception: return {}` — **empty policies** without surfacing error to operators (4-2).

8. **`run_reporting` learning capture assumes non-empty lists**  
   `_capture_learning_insights` indexes `report['bottlenecks'][0]` and `report['optimization_recommendations'][0]` after generation; if those lists were ever empty due to future changes, you would get **IndexError** (fragility in 4-4).

9. **Duplicate observability schema definitions**  
   `observability_hooks._ensure_schema` and `db_init.SCHEMA_SQL` both define `observability_events`. They match today but are a **drift risk** if one is edited.

10. **Accessibility gate scope**  
    Final check only considers `.md`, `.txt`, `.html`. **PDFs, PPTX, media** common in this domain are skipped — “final accessibility verification” can **pass with zero real checks** if artifacts are only non-text (4-5).

### Lower severity / process

11. **Agent QA release gate (4A-4)**  
    `archive_agent_quality_scan.py` validates shape and scores but **cannot prove** scores came from an independent scanner; it is **process + filesystem discipline**, not cryptographic attestation. Appropriate for internal use; weak against a motivated “check the box” workflow.

12. **Lane matrix / envelope docs**  
    Strong for **human clarity**; **no runtime validator** ties agent envelopes to `docs/lane-matrix.md` automatically. Drift between doc and live agent behavior remains possible.

13. **`log_coordination` guard**  
    Uses `coordination_audit_db` — consistent with other paths; still subject to the same **non-invocation bypass** as above.

### Summary judgment

- **Tracking:** Both epics are recorded **complete** in `sprint-status.yaml`; operational follow-through may extend beyond that file.  
- **Technical honesty:** The stack delivers **coherent CLIs, SQLite coordination, ad-hoc branching, observability split (DB vs JSONL), baton checks, and reporting** — a solid **v1 governance shell**.  
- **Main adversarial punch:** **Ad-hoc institutional YAML still written on run create**, **baton optional / multi-active**, **cache and baton races**, **fail-open mode**, and **deployment / accessibility checks that are narrower than the product surface**.

---

## Part C — Formal remediation tickets

IDs are local (`REM-###`) for tracking; map to your issue tracker as needed.

### REM-001 — Ad-hoc run create must not write canonical `state/config/runs/` YAML

| Field | Value |
|--------|--------|
| **Severity** | Critical |
| **Source** | Epic 4A-6 / FR76 alignment; `manage_run` + `run_context_builder` |
| **Problem** | Run-scoped YAML under `state/config/runs/<run_id>/` is created before `enforce_ad_hoc_boundary`, so ad-hoc runs still leave institutional-style config tree artifacts. |
| **Remediation** | When `mode` is `ad-hoc`, either skip `build_run_context` under canonical paths, or redirect all such writes to a scratch prefix (e.g. `state/runtime/scratch/runs/<run_id>/` or existing ad-hoc area). Default mode behavior unchanged. |

**Acceptance criteria**

- Creating a run with `ad-hoc` produces **no new files** under `state/config/runs/` **or** only under an explicitly documented scratch path.  
- Unit/integration test covers create path for both modes.  
- `docs/ad-hoc-contract.md` (or equivalent) states the rule in one sentence.

---

### REM-002 — Extend ad-hoc guard vocabulary for config / sidecar operations

| Field | Value |
|--------|--------|
| **Severity** | High |
| **Source** | Epic 4A-6; `ad_hoc_persistence_guard.py` |
| **Problem** | Guard lists omit operations that correspond to YAML/config writes; new scripts can silently bypass intent. |
| **Remediation** | Add explicit operation tokens for run-context YAML, release-manifest-adjacent writes, and any other durable paths you treat as “ledger.” Wire callers to use them. |

**Acceptance criteria**

- Enumerated operations documented next to `_BLOCKED_IN_AD_HOC` / `_ALLOWED_IN_AD_HOC`.  
- Any script that writes under `state/config/` or Marcus sidecars in production flow calls `enforce_ad_hoc_boundary` with the correct token.  
- Unknown operation in ad-hoc remains fail-closed (current behavior preserved).

---

### REM-003 — Run mode resolution: configurable fail-closed vs fail-open

| Field | Value |
|--------|--------|
| **Severity** | High |
| **Source** | Epic 4A-6; `resolve_run_mode` |
| **Problem** | Missing/corrupt `mode_state.json` defaults to `default`, allowing production persistence when state is ambiguous. |
| **Remediation** | Support explicit policy: e.g. env var or config flag `RUN_MODE_AMBIGUOUS=strict|lenient` where `strict` fails closed (treat as ad-hoc or refuse writes) and `lenient` keeps current behavior. Default for “regulated” presets should be documented. |

**Acceptance criteria**

- Documented behavior for missing file, invalid JSON, and unknown `mode` field.  
- Tests for strict vs lenient.  
- Release notes / admin guide mention the knob.

---

### REM-004 — Run baton: single active baton invariant + concurrency-safe updates

| Field | Value |
|--------|--------|
| **Severity** | High |
| **Source** | Epic 4A-1; `manage_baton.py` |
| **Problem** | Multiple active batons possible; JSON updates are not locked; “no baton” → `proceed` weakens authority. |
| **Remediation** | **Option A:** Enforce at most one active baton globally (init fails if another active exists unless `--force` with explicit override). **Option B:** Keep multiple runs but require explicit `run_id` for specialist checks and never use “latest” for mutating production state. Additionally: advisory lock or small lockfile for read-modify-write on the same baton. |

**Acceptance criteria**

- Documented semantics for multi-run vs single-run.  
- Tests for concurrent `update_gate` / `init`.  
- `cmd_check_specialist` behavior when no baton matches policy (e.g. `redirect` for production preset vs `proceed` for draft) if you adopt preset-aware rules.

---

### REM-005 — Perception cache: concurrent-safe writes

| Field | Value |
|--------|--------|
| **Severity** | Medium |
| **Source** | Epic 4A-5; `perception_cache.py` |
| **Problem** | Lost updates under parallel `put`. |
| **Remediation** | File lock (`portalocker` / `msvcrt` / `fcntl` by OS), or SQLite/append-only log per run, or merge with version field and retry. |

**Acceptance criteria**

- Stress test or unit test with threaded concurrent `put` for same/different keys without silent loss.  
- Document thread/process expectations for agents invoking cache.

---

### REM-006 — Deployment coordinator: separate “stub” from “live” platform profiles

| Field | Value |
|--------|--------|
| **Severity** | Medium |
| **Source** | Epic 4-5; `deployment_coordinator.py` |
| **Problem** | Example URLs read like real deployment targets. |
| **Remediation** | Name platforms `canvas-stub` / `dry-run` vs `canvas` with real base URL from config; or require `--confirm-live` when not using stub. |

**Acceptance criteria**

- Default CLI path cannot log misleading “production” URLs without explicit opt-in.  
- README or admin guide table: stub vs live.

---

### REM-007 — Quality gate policies: fail loud on load errors

| Field | Value |
|--------|--------|
| **Severity** | Medium |
| **Source** | Epic 4-2; `quality_gate_coordinator._load_policies` |
| **Problem** | `except Exception: return {}` hides misconfiguration. |
| **Remediation** | Log warning to stderr; include `policy_load_error` in JSON output; optional `--strict-policies` to exit non-zero. |

**Acceptance criteria**

- Corrupt YAML produces visible error in CLI JSON and stderr.  
- Test with invalid YAML fixture.

---

### REM-008 — Run report learning capture: guard empty bottlenecks/recommendations

| Field | Value |
|--------|--------|
| **Severity** | Low (defensive) |
| **Source** | Epic 4-4; `run_reporting._capture_learning_insights` |
| **Problem** | Future refactors could empty lists and cause `IndexError`. |
| **Remediation** | Use safe defaults (`"n/a"`) before indexing; or only call capture when lists non-empty. |

**Acceptance criteria**

- Test with run that produces zero bottlenecks and single generic recommendation.

---

### REM-009 — Deduplicate observability schema source of truth

| Field | Value |
|--------|--------|
| **Severity** | Low |
| **Source** | Epic 4A-5 / Epic 4; `observability_hooks.py` vs `db_init.py` |
| **Problem** | Two `CREATE TABLE` definitions can drift. |
| **Remediation** | Single shared SQL fragment or migration module imported by both. |

**Acceptance criteria**

- One file defines `observability_events`; both paths use it.  
- Comment in secondary consumer points to canonical definition.

---

### REM-010 — Final accessibility pass: artifact coverage and explicit “skipped” semantics

| Field | Value |
|--------|--------|
| **Severity** | Medium |
| **Source** | Epic 4-5; `deployment_coordinator._verify_accessibility` |
| **Problem** | Only text-like extensions checked; video/PDF-heavy runs can pass without checks. |
| **Remediation** | Either expand checker inputs (if tooling exists), or return **`blocked` vs `pass-with-gaps`** with explicit `skipped_reason` and counts by MIME/extension. |

**Acceptance criteria**

- JSON includes `skipped_artifacts` list or summary when checkable count is zero but paths were provided.  
- Documented limitation until PDF/media checks exist.

---

### REM-011 — Agent QA release gate: optional attestation field

| Field | Value |
|--------|--------|
| **Severity** | Low (process hardening) |
| **Source** | Epic 4A-4; `archive_agent_quality_scan.py` |
| **Problem** | Scores are self-attested at archive time. |
| **Remediation** | Optional `scanner_run_id`, `input_hash`, or CI job URL field in JSON schema; workflow doc requires CI path for release branches. |

**Acceptance criteria**

- Schema documents optional attestation fields.  
- Validation still passes without them (backward compatible).

---

### REM-012 — Lane matrix / envelope: optional static validator

| Field | Value |
|--------|--------|
| **Severity** | Low (governance hygiene) |
| **Source** | Epic 4A-2 / 4A-3 |
| **Problem** | Docs and runtime agent text can drift. |
| **Remediation** | Script that greps SKILL/envelope templates for required `decision_scope` / governance block patterns, or JSON Schema for envelope fragments in CI. |

**Acceptance criteria**

- CI or `pytest` invokes validator on a defined file set.  
- Fails on missing governance block in listed agents.

---

## Part D — Suggested sequencing

| Wave | Items | Rationale |
|------|--------|-----------|
| 1 | REM-001, REM-002, REM-003 | FR76 / ledger correctness and ambiguous mode |
| 2 | REM-004, REM-005 | Authority and cache integrity under concurrency |
| 3 | REM-006, REM-007, REM-010 | Operator clarity and honest “done” semantics |
| 4 | REM-008, REM-009, REM-011, REM-012 | Hardening and drift prevention |

---

*This document is a snapshot for test and governance traceability; update it if remediation items are closed or superseded.*
