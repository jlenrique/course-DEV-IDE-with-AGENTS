# Story 28-2: Tracy Gate Family + Regression Hardening

**Epic:** 28 — Tracy the Detective
**Status:** ratified-stub
**Sprint key:** `28-2-tracy-gate-hardening`
**Added:** 2026-04-17
**Points:** 3
**Depends on:** 28-1 (Tracy pilot ships the first gate test; 28-2 rounds out the family).
**Blocks:** Epic 28 closure.

## Story

As the production pipeline operator,
I want exhaustive gate-fidelity tests covering the three failure classes (absent receipt, stale receipt, tampered receipt) plus the asset-intent-registry orphan-detector,
So that silent bypass of the Tracy gate or silent orphan of asset intents cannot happen in production — both are high-blast-radius failures worth costing test dollars against.

## Background

Per Murat's Round-2 risk analysis, the pre-Pass-2 gate is the linchpin of the Tracy lane. A silent skip — where Pass 2 proceeds without Tracy's inputs because the receipt check malfunctioned — is worse than a loud failure. This story treats the gate as a family of three tests + one contract-registry test, not a single check.

Also: Murat's asset-intent-registry check (`tests/contracts/test_asset_intent_registry.py`) is the test that catches the "Tracy emits intent tag no consumer recognizes" silent-orphan failure. Lives in cross-agent contract layer.

## Acceptance Criteria (Stub Level)

- **AC-1:** `tests/test_tracy_pass2_gate.py::test_gate_blocks_with_stale_receipt` — receipt exists but `run_id` doesn't match current run → Pass 2 refuses.
- **AC-2:** `tests/test_tracy_pass2_gate.py::test_gate_blocks_with_tampered_receipt` — receipt exists, valid shape, but `operator_acknowledged: false` when status requires acknowledgment → Pass 2 refuses.
- **AC-3:** `tests/contracts/test_asset_intent_registry.py` — bidirectional check: every `intent_class` value Tracy can emit is registered in the cross-agent asset-intent-registry; every registered value has at least one consumer declaring it handles this intent.
- **AC-4:** `tests/e2e/test_tracy_gate_refusal.py` — one E2E test: gate receipt missing, Pass 2 invocation produces exit code + grep-able error line. Confirms the refusal is loud, not silent.
- **AC-5:** Regression: full pytest green including all xfail-strict Tracy tests flipping to passing; zero new `skip`/`xfail` in default suite.
- **AC-6:** `bmad-code-review` run adversarially on the gate test family; MUST-FIX remediated.

## Notes for Create-Story

- The asset-intent-registry test depends on at least one asset consumer agent declaring it handles Tracy's intent values. In v1 pilot, Irene is the sole consumer (handles `narration_citation`, `supporting_evidence`, `counter_example`). If follow-on asset agents ship between 28-1 merge and 28-2 merge, extend the registry accordingly.
- Gate-tamper test requires the gate logic to distinguish `operator_acknowledged` vs. raw receipt presence — this is the semantic-validity check per AC-S3 of the shared spine.

## Party Input Captured
- **Murat (Test, Round 2+3):** gate family of 3 is load-bearing; ratification test already in 28-1; registry test lives in contract layer not Tracy suite to force bidirectional running.
- **Operator (NN3):** hard pre-Pass-2 gate is non-negotiable.
