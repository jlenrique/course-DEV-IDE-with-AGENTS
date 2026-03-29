# APP logging — three channels (authoritative map)

**Purpose:** When debugging, reviewing, or repairing a production run, use this map to know **where to look first** for each kind of question. This complements the evaluation in [app-logging-evaluation.md](./app-logging-evaluation.md).

**Party-mode consensus (2026-03-29):** Architect + Orchestrator + QA aligned on separating **durable coordination state**, **artifact-native evidence**, and **tool stderr logs** so operators are not forced to infer a single “log file” that does not exist.

---

## Channel A — SQLite APP ledger

**Location:** `state/runtime/coordination.db` (schema: `scripts/state_management/db_init.py`)

**Authoritative for:**

- Run lifecycle and stage index (`production_runs`, `context_json`)
- Delegation and completion events with JSON payloads (`agent_coordination`)
- Quality gate outcomes and findings (`quality_gates`)
- Governance observability aggregates when recorded (`observability_events`)

**Scripts:** `manage_run.py`, `log_coordination.py`, `quality_gate_coordinator.py` / `quality_logger.py`, `observability_hooks.py`, `run_reporting.py`

**Not authoritative for:** Raw LLM transcripts, Cursor chat history, or per-HTTP request/response bodies unless copied into `payload_json` by convention.

---

## Channel B — Artifact-native evidence

**Location:** Run-scoped YAML under `state/config/runs/<run_id>/`, generated artifacts under `course-content/` (and staging paths), Fidelity Trace Reports per Vera protocol, BMad sidecars under `_bmad/memory/`, woodshed `run-log.yaml` where used.

**Authoritative for:**

- What was **produced** (files, manifests, slide outputs)
- **Source-to-output** arguments (Fidelity Assessor trace format)
- **Human-readable** repair context (diffs, briefs, exports)

**Not authoritative for:** Cross-run SQL analytics without importing paths into the ledger.

---

## Channel C — Tool layer (Python `logging`)

**Location:** Process stderr or the environment’s logging configuration when skills/scripts run (e.g. `skills/gamma-api-mastery/scripts/gamma_operations.py`).

**Authoritative for:**

- **Ephemeral** operational detail: generation ids, download paths, latency-adjacent signals when logged
- Correlation with `run_id` when callers pass optional `run_id=` (additive API)

**Not authoritative for:** Compliance-grade audit on its own; pair with Channel A or B for durable narrative.

---

## Quick “which channel?” lookup

| Question | Start here |
|----------|----------------|
| What stage is the run in? | A — `manage_run.py status` |
| Who was delegated and what envelope was used? | A — `log_coordination.py history` |
| What did Quinn/Vera decide? | A — `quality_gates`; B — attached reports |
| Why is the run report’s observability section empty? | A + C — report JSON `observability_error_*` keys; Python logs for traceback |
| What did Gamma return / export? | B — artifacts; C — `gamma_operations` logs |
| Session vs run linkage? | Not yet first-class — see hooks status in [app-logging-evaluation.md](./app-logging-evaluation.md) |

---

*Operational doc only; no runtime behavior.*
