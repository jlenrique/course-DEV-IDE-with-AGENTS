# APP Logging & Observability — Evaluation Framework, Report, and Recommendations

**Project:** course-DEV-IDE-with-AGENTS  
**Scope:** Agentic Production Platform (APP) — multi-step workflows with review, repair, and study of inputs/outputs.  
**Method:** Repository review against a formal rubric; analytic “party mode” lens (Architect, Orchestrator, Fidelity, QA, Tooling, Reliability). This document is not a transcript of a live Party Mode session.

**See also:** [app-logging-channels.md](./app-logging-channels.md) — authoritative three-channel map for operators (SQLite vs artifacts vs tool logs).

---

## 1. Formal evaluation framework

Use this rubric to score how well logging and observability support **review**, **repair**, and **study** of complex APP runs.

| ID | Dimension | Question | Strong signal | Weak signal |
|----|-----------|----------|---------------|-------------|
| **L1** | **Run correlation** | Can every log line or record be tied to `run_id`, stage, and gate? | Single ID flows through DB, baton, envelopes, reports | IDs only in chat or fragmented across files |
| **L2** | **Lifecycle coverage** | Are plan → delegate → execute → gate → repair → complete all represented? | Tables/events for each transition | Only start/end or only tool logs |
| **L3** | **Evidence depth** | Can someone reconstruct inputs/outputs without re-running? | Payloads, artifact paths, API status, rubric findings | Status-only records, no payloads |
| **L4** | **Structured queryability** | Can you filter, sort, and aggregate across runs? | SQL/JSONL + summarizers | Free text only |
| **L5** | **Human study ergonomics** | Can a reviewer find “what failed and why” in one place? | Run report + fidelity trace + quality findings linked | Chasing scattered logs |
| **L6** | **Tool/API layer** | Are external calls traceable (latency, errors, artifacts)? | Per-call run logs or structured API fields | Silent failures or stderr-only |
| **L7** | **Mode honesty** | Is ad-hoc vs default visible and consistent? | Explicit mode on rows + transient fallbacks documented | Silent defaulting or split brain |
| **L8** | **Enforcement vs protocol** | Are critical logs guaranteed or only recommended? | Hooks, tests, or mandatory CLI returns | “Marcus should…” only |
| **L9** | **Session/IDE bridge** | Does the Cursor session connect to run state? | Hooks emit run/session linkage | Disconnected chat and DB |

**Scoring (optional):** Per dimension assign **0–2** (missing / partial / strong), then average for an overall logging maturity score.

---

## 2. Party Mode lens (roles)

- **Architect:** Do persistence layers (`production_runs`, `agent_coordination`, `quality_gates`, `observability_events`) form a coherent evidence model, or are they optional satellites?
- **Orchestrator (Marcus):** Is the operational contract (delegate log → invoke → completion log) something operators will always run, or easy to skip?
- **Fidelity (Vera):** Is source-to-output auditability owned by agent deliverables (Fidelity Trace Report) separate from platform telemetry?
- **QA:** Are review outcomes (`findings_json`, scores) first-class and durable?
- **Tooling engineer:** Do Python `logging` and SQLite/JSON tell one story or two?
- **Reliability engineer:** What happens when observability import fails or mode is ad-hoc?

---

## 3. Evaluation report

### 3.1 Overall verdict

APP logging is **strong on designed persistence and narrative specs**, **uneven on automatic capture**, and **weak on IDE/session and LLM-turn correlation**. It supports effective APP use when the team **diligently uses** `manage_run`, `log_coordination`, quality logging, `observability_hooks`, and Vera trace artifacts. It **under-supports** “open Cursor, work, debug later” without that discipline.

---

### 3.2 L1 — Run correlation

**Strengths**

- `run_id` is central in `production_runs`, `agent_coordination`, `quality_gates`, and `observability_events` (see `skills/production-coordination/references/run-state-schema.md` and `scripts/state_management/db_init.py`).
- Baton files are namespaced: `state/runtime/run_baton.<run_id>.json`.
- Marcus’s delegation protocol explicitly ties logging to `run_id` in `skills/bmad-agent-marcus/references/conversation-mgmt.md` (steps: log delegation → invoke → log completion).

**Gaps**

- LLM chat turns in Cursor are not automatically stamped with `run_id`; correlation is protocol-dependent.
- Tool-layer modules (e.g. `skills/gamma-api-mastery/scripts/gamma_operations.py`) use `logging.getLogger(__name__)` without a documented run-scoped logging context, so API logs may not join to `RUN-xxx` unless logging is configured accordingly.

---

### 3.3 L2 — Lifecycle coverage

**Strengths**

- Production coordination documents create → advance → checkpoint → approve → complete (`skills/production-coordination/SKILL.md`).
- Delegation and completion logging are explicit in `conversation-mgmt.md`.
- Observability supports `gate_result`, `lane_violation`, `cache_hit` / `cache_miss` (`skills/production-coordination/scripts/observability_hooks.py`).

**Gaps**

- Cursor hooks do not tie sessions to runs. `hooks/scripts/session-end.mjs` remains a placeholder (“run reporting will be integrated in Epic 4”). `session-start.mjs` is similarly a placeholder for pre-flight.
- Session boundaries are therefore not automatically reflected in APP persistence.

---

### 3.4 L3 — Evidence depth (review, repair, study)

**Strengths**

- `log_coordination.py` stores `payload_json` for delegate/complete events — suitable for envelope and result snapshots.
- `skills/quality-control/scripts/quality_logger.py` persists `findings_json` and scores.
- Fidelity Assessor references (`skills/bmad-agent-fidelity-assessor/references/fidelity-trace-report.md`) emphasize auditable comparison records per finding — appropriate for study and repair at fidelity gates.
- Woodshed `run-log.yaml` captures API interaction detail for mastery runs (`skills/woodshed/scripts/reproduce_exemplar.py`) — a strong pattern for tool forensics (woodshed-scoped).

**Gaps**

- `record_gate_result` in observability carries O/I/A counts and optional payload; rich Vera findings may live in agent-produced documents unless explicitly bridged into `observability_events`.
- Gamma production path logs sparse `logger.info` lines (e.g. generation id, download size) rather than a full structured run log per production call comparable to woodshed.

---

### 3.5 L4 — Structured queryability

**Strengths**

- `run_reporting.py` aggregates quality, coordination, and observability for a run.
- `summarize_run()` in `observability_hooks.py` computes gate pass rate, O/I/A totals, quality dimension averages, lane violations, and cache metrics.

**Gaps**

- If importing `observability_hooks` fails, `run_reporting._observability_summary` catches `Exception` and returns a generic `"observability summary unavailable"` without surfacing the underlying error — which can hide misconfiguration when reports look empty.

---

### 3.6 L5 — Human study ergonomics

**Strengths**

- Run reporting conceptually bundles stage metrics, quality, coordination, observability, bottlenecks, and recommendations.
- Production coordination exposes JSON status for conversational use.

**Gaps**

- No single mandated “run folder” always containing chat transcript, DB slice, and artifacts; reviewers still assemble narrative from Cursor history, `state/`, and `course-content/`.
- IDE lifecycle is not first-class in APP logs while hooks remain placeholders.

---

### 3.7 L6 — Tool/API layer

**Strengths**

- Woodshed run logs demonstrate the desired depth for API forensics.
- Sensory bridge scripts use module loggers for operational debugging.

**Gaps**

- Production tool scripts vary in logging richness; there is no unified request/response logging policy across all API clients comparable to woodshed’s run log.

---

### 3.8 L7 — Mode honesty

**Strengths**

- `observability_hooks._persist_or_transient` writes JSONL under `state/runtime/ad-hoc-observability/` when DB persistence is blocked by ad-hoc policy — explicit dual path.
- `quality_logger` returns a non-persisted record in ad-hoc with an explicit reason string.

**Gaps**

- Studying ad-hoc runs requires merging transient files and chat; the SQLite timeline is intentionally incomplete for ad-hoc, which complicates post-hoc analytics unless sources are merged deliberately.

---

### 3.9 L8 — Enforcement vs protocol

**Strengths**

- Skills and references encode what to log (Marcus delegation steps; production-coordination script table).
- Tests exist for coordination logging (e.g. `skills/production-coordination/scripts/tests/test_log_coordination.py`).

**Gaps**

- No automated enforcement that every delegation invokes `log_coordination`; skipping still “works” at runtime.
- Observability CLI exists but is not universally wired from every agent execution path.

---

### 3.10 L9 — Session/IDE bridge

**Strengths**

- `hooks/hooks.json` declares `sessionStart` and `sessionEnd` hooks.

**Gaps**

- Hook scripts remain placeholders; IDE session start/end do not append to APP run state or emit run correlation metadata.

---

## 4. Synthesis table

| Need | Assessment |
|------|------------|
| **Review** (human gates) | **Good** — `quality_gates` and findings; checkpoint flow in `manage_run`; envelope governance supports scoped review. |
| **Repair** (iterate on one run) | **Moderate** — Strong if payloads and Vera reports are saved; weak if teams skip coordination logging or do not persist trace reports with artifacts. |
| **Study I/O** (deep debugging) | **Split** — Strong in woodshed and fidelity-report design; thinner for arbitrary production API calls; disconnected from Cursor session hooks. |
| **Reliability** (operations) | **Moderate** — SQLite summaries, WAL on coordination DB, ad-hoc fallbacks; some silent degradation in reporting when observability is unavailable. |

---

## 5. Top recommendations

1. **Treat “logging” as three explicit channels**  
   - (a) SQLite APP ledger (`production_runs`, `agent_coordination`, `quality_gates`, `observability_events`)  
   - (b) Artifact-native evidence (Fidelity Trace Report, run-scoped YAML under `state/config/runs/`, sidecars)  
   - (c) Tool run logs (API id, latency, paths, errors)  
   Document which channel is **authoritative** for which question (e.g. “why did Vera fail?” vs “what did Gamma return?”).

2. **Close the IDE gap**  
   Replace hook placeholders with at least append-only session metadata (timestamp, workspace root, optional `run_id` from env or last `manage_run` query) so session boundaries are visible next to APP state.

3. **Harden run reporting**  
   When `_observability_summary` fails, surface the underlying exception (e.g. stderr or a `detail` field) so empty observability sections are diagnosable.

4. **Optional enforcement**  
   Add a dry-run integration test or pre-flight check that a scripted sequence produces expected coordination/observability rows, or a Marcus checklist enforced in workflow docs/CI.

5. **Align production tool logging with woodshed**  
   Adopt a minimal structured record per significant API call (request id, latency, artifact paths, error class) keyed by `run_id` when the run context is known — without requiring full woodshed verbosity for every call.

---

## 6. Reference paths (quick index)

| Area | Path |
|------|------|
| Run state schema | `skills/production-coordination/references/run-state-schema.md` |
| Delegation / envelope | `skills/production-coordination/references/delegation-protocol.md` |
| Marcus delegation + logging steps | `skills/bmad-agent-marcus/references/conversation-mgmt.md` |
| Coordination DB logger | `skills/production-coordination/scripts/log_coordination.py` |
| Observability | `skills/production-coordination/scripts/observability_hooks.py` |
| Run reports | `skills/production-coordination/scripts/run_reporting.py` |
| Quality persistence | `skills/quality-control/scripts/quality_logger.py` |
| DB schema | `scripts/state_management/db_init.py` |
| Cursor hooks | `hooks/hooks.json`, `hooks/scripts/session-start.mjs`, `hooks/scripts/session-end.mjs` |
| Fidelity trace format | `skills/bmad-agent-fidelity-assessor/references/fidelity-trace-report.md` |
| Woodshed run log pattern | `skills/woodshed/scripts/reproduce_exemplar.py` |

---

*Last updated: 2026-03-29. Revisit after hook implementation or unified tool logging adoption.*
