# Epic 28 — Tracy Dispatch Runbook

Canonical procedure for executing a Tracy dispatch end-to-end. Referenced by 28-1 (pilot) and inherited by all future 28-N stories.

**Governing principles:**
- Marcus owns every dispatch edge (AC-S1).
- Artifacts travel via filesystem, written atomically (AC-S2).
- Hard pre-Pass-2 gate must resolve to `complete | empty | failed` with operator acknowledgment where needed (AC-S3).

## 14-Step Sequence

```
RUN STATE                                      ARTIFACT                                      AGENT
──────────                                     ────────                                      ─────
T+0  Irene Pass 1 completes                    runs/<id>/irene/pass-1-output.yaml           Irene
     (arc + clusters + gaps[] populated)
T+1  Irene surfaces Tracy-dispatch             (in-band recommendation in landing point)    Irene → Marcus
     recommendation to Marcus
T+2  Marcus synthesizes Tracy brief            runs/<id>/tracy/brief.yaml                   Marcus
     from Irene's gaps[]
T+3  Marcus landing-point to operator:         (interactive)                                Marcus ↔ Operator
     "Dispatch Tracy for clusters X, Y?
     Default: yes. Accept / skip / scope?"
T+4  Operator accepts. Marcus dispatches       (runtime call)                               Marcus → Tracy
     Tracy with brief.yaml as input
T+5  Tracy formulates queries, hits scite.ai   runs/<id>/tracy/dispatch-log.yaml (append)  Tracy
     via Texas-owned scite provider (27-2)     (see note A)
     from pre-indexed scite_client.
T+6  Tracy evaluates candidates, scores,       runs/<id>/tracy/suggested-resources.yaml    Tracy
     writes manifest atomically                (atomic write per AC-S2)
     (editorial_note per row)
     Also: runs/<id>/tracy/research-brief.md  (human narrative)
T+7  Marcus receives Tracy-complete signal,    (freshness + atomicity check)                Marcus
     validates manifest atomicity +            (see note B)
     staleness against brief
T+8  Marcus landing-point to operator:         (interactive)                                Marcus ↔ Operator
     redlineable manifest table grouped
     by cluster, confidence-tiered
     (auto-adopt / review / auto-reject)
T+9  Operator redlines + confirms.             runs/<id>/tracy/tracy-approved-resources.yaml Marcus writes
     Approved rows written atomically
T+10 Marcus dispatches Texas second-pass       (runtime call)                               Marcus → Texas
     with --tracy-approved-resources flag
T+11 Texas reads approved file, fetches        runs/<id>/texas/extraction-report.yaml      Texas
     via scite provider, appends rows          (append; rows tagged
     to fidelity manifest                       source_origin: tracy-suggested)
T+12 Marcus writes pre-Pass-2 gate receipt     runs/<id>/receipts/tracy-complete.yaml      Marcus
     (status: complete, approved count,        (atomic)
     texas pass-2 ref)
T+13 HARD GATE — Irene Pass 2 invocation       (gate check)                                 Marcus (gate)
     blocked unless receipt validates
T+14 Irene Pass 2 reads Tracy's approved       runs/<id>/irene/pass-2-output.yaml          Irene
     material + asset-intent-map, finalizes
     scripts, triggers asset fan-out
```

## Notes

**Note A — scite provider ownership.** Tracy does not own the scite.ai fetch; she **issues queries against Texas's scite provider module** (Epic 27 Story 27-2). Tracy's `search_scite.py` script is a thin wrapper that invokes Texas's `providers/scite_client.py` as a library, not as a runtime specialist dispatch. This is the pattern for every future Tracy provider: Texas owns the library, Tracy owns the judgment about how to query it.

**Note B — Marcus's freshness + atomicity check.** Before invoking the operator landing point at T+8, Marcus verifies:
1. `suggested-resources.yaml` was written AFTER `brief.yaml` (freshness — Tracy did not respond to a stale brief)
2. Manifest parses cleanly and validates against schema (atomicity — write completed)
3. All rows have non-empty `editorial_note` (Tracy did not ship vacuous output)

Any failure = Marcus routes to failure handling (see below) rather than surfacing a broken manifest to the operator.

## Failure-Mode Resolution

Tracy's dispatch can resolve three ways at T+6 / T+7:

### Case: `complete` (happy path)
- Manifest has ≥1 resource; operator approves ≥1 row.
- Receipt at T+12 carries `tracy_status: complete` + `approved_rows_count > 0`.
- Irene Pass 2 reads Tracy inputs.

### Case: `empty` (Tracy found nothing)
- Manifest has zero rows OR operator rejects all rows.
- Tracy emits explicit `status: no_sources_found` in `suggested-resources.yaml` — this is semantically distinct from a manifest parse failure.
- Marcus landing-point at T+8 surfaces the empty result with three options:
  - **Proceed without enrichment** (default — Pass 2 runs with primary material only)
  - **Retry Tracy with loosened threshold** (e.g., drop authority_tier bar by one rank)
  - **Operator provides manual source** (converts Tracy's empty-outcome to operator-named second pass)
- Receipt at T+12 carries `tracy_status: empty` + `operator_acknowledged: true`.

### Case: `failed` (timeout / error / partial)
- Tracy's dispatch exceeded budget (180s hard cap) OR crashed OR partial-wrote.
- Marcus dispatch check at T+7 catches the failure.
- Landing-point at T+8 surfaces the failure with three options:
  - **Retry Tracy** (fresh dispatch, same brief)
  - **Proceed without enrichment** (accept Pass 2 runs without supplementary material)
  - **Abort run** (hard stop; investigate before resuming)
- Receipt at T+12 carries `tracy_status: failed` + `operator_acknowledged: true` + `failure_reason`.

## Invariants

These must hold at every moment of a Tracy-active run:

- **I-1:** No direct Tracy→Texas runtime call path exists in the code. (Grep verification in `tests/contracts/test_dispatch_topology.py`.)
- **I-2:** Every file Tracy writes is atomically visible to Marcus (no partial writes observable).
- **I-3:** Pre-Pass-2 gate is fail-closed. Missing receipt = refuse Irene Pass 2, never skip.
- **I-4:** Every operator action is logged with timestamp + rationale in `dispatch-log.yaml`.
- **I-5:** Tracy's output writes are bounded — one `suggested-resources.yaml` + one `research-brief.md` + one `dispatch-log.yaml` entry per dispatch. No scope creep into other agents' lanes.

## Rollback

If a Tracy dispatch produces visibly-incorrect output mid-run:

1. Operator can abort at T+8 landing-point — writes receipt `tracy_status: failed` + `operator_acknowledged: true` + `failure_reason: operator_aborted`.
2. Marcus proceeds to Pass 2 without Tracy inputs if operator chose "proceed without enrichment" (treats as `empty` with prejudice).
3. Dispatch log preserved for post-run analysis — *why* Tracy produced bad output is learnable signal for v2 scoring rubric.
4. No automatic retry without explicit operator consent — retries only via the landing-point option.

## Links

- [Epic 28 AC Spine](./ac-spine.md)
- [Story 28-1: Tracy pilot](../28-1-tracy-pilot-scite-ai.md)
- [Story 28-2: Gate hardening](../28-2-tracy-gate-hardening.md)
- [Tracy sanctum bundle](../../../skills/bmad-agent-tracy/)
