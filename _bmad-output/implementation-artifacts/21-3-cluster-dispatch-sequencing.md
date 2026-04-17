# Story 21-3: Cluster Dispatch Sequencing

**Epic:** 21 - Gary Cluster Dispatch — Gamma Interpretation  
**Status:** done (implemented, tested)  
**Sprint key:** `21-3-cluster-dispatch-sequencing`  
**Depends on:** `21-2-cluster-aware-prompt-engineering.md`

## Story
As the dispatch orchestrator, I need a deterministic, observable sequencing plan for per-cluster prompts so that dispatch honors priorities, dependencies, and throttles without starvation or duplicate work.

## Scope
- Plan generation only (no model execution).
- Deterministic ordering, batching, and retry/backoff metadata.
- Audit + telemetry around plan creation/failure.

## Acceptance Criteria (consensus, party mode)
- **AC1**: Given clusters with priorities/sizes/deps, ordering is deterministic (priority desc, size desc, ID tiebreak or manifest ordering per config) and yields a stable plan_hash.
- **AC2**: Batching respects configured batch_size and max concurrency; schedule preview emitted.
- **AC3**: Cycles or invalid policy yield `invalid_policy` with diagnostics; no plan persisted.
- **AC4**: Retry/backoff attached per step per config; retries bounded; idempotent dispatch key prevents duplicates.
- **AC5**: Partial failure handling: unaffected clusters proceed; blocked clusters surface dependency-blocked status.
- **AC6**: Telemetry emits `dispatch.plan.created` / `dispatch.plan.failed` with cluster_id (or plan scope), plan_hash, counts; audit record captures policy snapshot, hash, timestamp.

## Tasks / Subtasks
- Define dispatch policy in `config/dispatch.yaml` (ordering, batch_size, throttles, backoff, retries, retryable_statuses).
- Implement deterministic sort + batching + plan_hash (sha256) + schedule preview.
- Add cycle detection and invalid-policy guardrails.
- Attach retry/backoff + idempotent dispatch key per step.
- Emit audit + telemetry events; handle no-op/empty-plan gracefully.
- Tests: unit (sort, batching, cycle detect, idempotency), property (independent job addition does not reorder existing), integration (mixed priorities/deps, over-budget, rate-limit), contract (event schema).

## Dev Notes
- Idempotence: same inputs/policy → same plan/order/hash. Hash collision: salt and log.
- Rate-limit/budget guards: no bursts beyond configured window; over-budget queues hold.
- Dry-run mode recommended before enabling feature flag.

## Execution & Evidence
- Implementation: `skills/bmad-agent-marcus/scripts/cluster_dispatch_sequencing.py`
- Config: `state/config/dispatch.yaml`
- Tests: `skills/bmad-agent-marcus/scripts/tests/test_cluster_dispatch_sequencing.py`
- Test run: `python -m pytest skills/bmad-agent-marcus/scripts/tests/test_cluster_dispatch_sequencing.py` (pass)
- Full suite: `python -m pytest` (pass, 2026-04-11)

## Adversarial Review (BMAD)
- Edge Case Hunter: cycle detection, missing cluster_id, retry/backoff presence, plan hash stability; no new issues.
- Blind Hunter: deterministic ordering validated; batch boundaries stable across runs.
- Acceptance Auditor: AC1–AC6 satisfied; no blocking findings.

## Remediation/Notes
- Structural-walk global finding: ffmpeg absent for ElevenLabs audio; unrelated here but must be remediated/waived before production trial.

## References
- `config/dispatch.yaml` (new)
- `skills/bmad-agent-marcus/scripts/run_g1.5-cluster-gate.py` (for manifest order precedent)
