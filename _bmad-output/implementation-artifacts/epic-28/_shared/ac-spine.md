# Epic 28 — Shared Acceptance Criteria Spine

Every 28-N story MUST satisfy these cross-cutting acceptance criteria. Per-story ACs are layered on top; these are the contract all of Tracy's lane obeys.

## AC-S1 — Dispatch-vs-artifact rule (governing architecture principle)

**Tracy never invokes Texas at runtime.** Marcus owns every dispatch edge. Artifact handoffs via filesystem are not a rule violation.

The flow is exactly six steps, no shortcuts:

1. Irene flags a research gap in her cluster manifest → signal to Marcus
2. Marcus dispatches Tracy with a scoped research brief
3. Tracy writes `suggested-resources.yaml` (atomic; see AC-S2)
4. Operator reviews via Marcus landing-point, approves/rejects/refines → approved rows written to `tracy-approved-resources.yaml`
5. Marcus dispatches Texas with `--tracy-approved-resources <path>`; Texas reads the file at that trigger and fetches
6. Texas appends second-pass rows to its fidelity manifest with `source_origin: tracy-suggested` + `tracy_row_ref`

Tests assert Marcus is on the dispatch edge in every code path. A direct Tracy→Texas runtime call is a MUST-FIX regression.

**Ratified:** Winston, 2026-04-17.

## AC-S2 — Artifact atomicity

All Tracy output artifacts are written atomically. Implementation options:

- **Option A (preferred):** temp file + rename. Marcus never sees a partial write.
- **Option B:** explicit `status: complete` marker field at top of file. Marcus's dispatch-time freshness check validates the marker before proceeding.

Partial-write protection is load-bearing because Tracy's output drives a hard downstream gate (AC-S3). A half-written manifest that appears complete would bypass the gate silently.

**Added:** Winston hygiene edge case, 2026-04-17.

## AC-S3 — Hard pre-Pass-2 gate

Irene Pass 2 cannot start unless:
- `runs/<run-id>/receipts/tracy-complete.yaml` exists AND
- Receipt validates against `tracy-complete.schema.yaml` AND
- Receipt `tracy_status` is one of: `complete | empty | failed` AND
- If `empty | failed`, receipt includes `operator_acknowledged: true` from a Marcus landing-point

Missing or invalid receipt = Marcus refuses to invoke Irene Pass 2 with an explicit, grep-able error. No silent skips, no quiet defaults.

Gate fidelity tested as a family of three (28-2):
- `test_gate_blocks_without_receipt`
- `test_gate_blocks_with_stale_receipt` (run_id mismatch)
- `test_gate_blocks_with_tampered_receipt` (`operator_acknowledged: false` when status requires acknowledgment)

**Ratified:** operator NN3, 2026-04-17.

## AC-S4 — Manifest schema compliance

Every Tracy output validates against the published schema at `skills/bmad-agent-tracy/schemas/suggested-resources.schema.yaml`. Contract test in `tests/contracts/test_tracy_manifest_shape.py` asserts the schema is a binding, versioned contract. Schema drift between Tracy's emit code and the schema file = CI failure.

## AC-S5 — Vocabulary SSOT

`skills/bmad-agent-tracy/references/vocabulary.yaml` is the single source of truth for Tracy's controlled vocabulary (`intent_class` values, `authority_tier` values, `fit_score` scale interpretation, `editorial_note` constraints).

- Generated human-readable doc at `skills/bmad-agent-tracy/references/vocabulary.md` — produced from vocabulary.yaml, checked in, diff-reviewed at commit.
- L1 check: `tracy-vocab-lockstep` asserts every value Tracy's code emits is defined in vocabulary.yaml, and every value in vocabulary.yaml has a code-path handler. Divergence = commit fail.

This is the DOCX-drift pattern (Epic 27) applied preemptively to Tracy.

## AC-S6 — `editorial_note` required and meaningful

Every resource row in `suggested-resources.yaml` carries a non-empty `editorial_note`. Lint enforces:

- Length: 40-500 characters.
- Must reference at least one of: a specific slide/claim/cluster, a scite (or future-provider) signal, or an authority-tier rationale.
- Vacuous notes (would apply unchanged to any other resource) surface as WARN in static heuristic review but do not hard-fail in v1. Hard-fail promotion evaluated post-pilot.

The test Paige codified: "Could this editorial_note be copy-pasted onto a different resource row and still make sense?" If yes, it's vacuous.

## AC-S7 — Test coverage floor

Minimum per-story test floor per Murat's Round-2 doctrine:

- All new behavior covered by a test at the lowest viable level (unit > integration > E2E).
- `xfail(strict=True)` during pre-implementation ratification; remove marker one test at a time as AC lands.
- Cassette-backed for all network calls. No real-network tests in default suite.
- Schema-canary test for each external-API dependency, warn-only on drift.
- No new `@pytest.mark.skip` or `xfail` in default suite at story closure.

**Regression-proof tests** per operator hard-preference: classify any failure as update / restore / delete. Measure coverage; don't trust intuition.

## AC-S8 — Dispatch audit trail

Every Tracy dispatch produces an entry in `runs/<run-id>/tracy/dispatch-log.yaml` carrying:

- `dispatch_id` (UUID)
- `requested_at`, `resolved_at`
- `requesting_agent` (default: irene)
- `brief` (the scoped research question Tracy received)
- `queries_issued[]` (list of scite.ai search queries Tracy actually ran)
- `candidates_evaluated_count`
- `candidates_surfaced_count` (what landed in suggested-resources.yaml)
- `operator_actions[]` (per-row: approved / rejected / refined with rationale)
- `outcome` (`complete | empty | failed`)

This is the feedback loop that makes post-pilot retro possible. Without it, we can't measure Loop A (confidence drift), Loop B (supply creates demand), or Loop D (adversarial calibration).
