# Story 21-4: Cluster Coherence Validation

**Epic:** 21 - Gary Cluster Dispatch — Gamma Interpretation  
**Status:** done (implemented, tested)  
**Sprint key:** `21-4-cluster-coherence-validation`  
**Depends on:** `21-1-visual-design-constraint-library.md`, `21-2-cluster-aware-prompt-engineering.md`, `21-3-cluster-dispatch-sequencing.md`

## Story
As the coherence validator, I need to verify that generated cluster outputs stay on-theme, respect constraints, and align with sequencing outcomes, so that clusters only advance when consistent and reviewable.

## Scope
- Read-only validation of generated outputs vs. manifests/constraints.
- Coherence scoring, violation reporting, deterministic report hash.
- No content mutation; produces pass/warn/block decisions.

## Acceptance Criteria (consensus, party mode)
- **AC1**: Validator returns per-cluster scores (tone/coherence/constraint adherence) with configurable thresholds; report_hash deterministic for identical inputs + seed.
- **AC2**: Violations include missing outputs, forbidden interstitial placements, visual/constraint breaches (21-1), and cross-item conflicts; fail reasons enumerated.
- **AC3**: Sequencing expectations from 21-3 audited; out-of-order or skipped steps trigger failure with explicit references.
- **AC4**: Sampling mode declared (full vs stratified); coverage recorded in the report.
- **AC5**: Machine-readable report (schema) plus human-readable summary emitted; telemetry `validation.report.created`/`failed` with cluster_id, report_hash, pass/fail, violation counts.
- **AC6**: Graceful error on invalid inputs (`config_missing` / `missing_output` / `invalid_output_format`), no partial reports persisted.

## Tasks / Subtasks
- Define validation rules in `config/validation.yaml` (coherence thresholds, ordering rules, interstitial rules, length bounds, safety blocks, sampling).
- Implement validator: align outputs to manifest order; run rule checks; compute scores; produce pass/warn/block decision + report_hash.
- Detect cross-item conflicts and constraint violations; attach suggested minimal fixes/re-run hints.
- Emit audit + telemetry events; persist report + audit record (rule versions, inputs hash, timestamp).
- Tests: unit (rule evaluators, threshold gating, sampling determinism), property (tightening threshold never flips fail→pass; same inputs/seed → same report), integration (mixed-quality cluster, missing outputs, conflict case), contract (report schema, status codes).

## Dev Notes
- Idempotence: same inputs/rules/seed → same report_hash/verdict.
- Performance: target completion under budget for N≈200 items; sampling reduces cost when configured.
- Outputs are non-mutating; failures block downstream dispatch until addressed.

## Execution & Evidence
- Implementation: `skills/bmad-agent-marcus/scripts/cluster_coherence_validation.py`
- Config: `state/config/validation.yaml`
- Tests: `skills/bmad-agent-marcus/scripts/tests/test_cluster_coherence_validation.py`
- Test run: `python -m pytest skills/bmad-agent-marcus/scripts/tests/test_cluster_coherence_validation.py` (pass)
- Full suite: `python -m pytest` (pass, 2026-04-11)

## Adversarial Review (BMAD)
- Edge Case Hunter: missing outputs, ordering mismatch, forbidden term, invalid output type; no additional blockers.
- Blind Hunter: report_hash determinism with/without seed confirmed on fixtures.
- Acceptance Auditor: AC1–AC6 satisfied; recommended follow-up to expand sequencing_expectations coverage in integration flow.

## Remediation/Notes
- Structural-walk global finding: ffmpeg absent for ElevenLabs audio; unrelated here but must be remediated/waived before production trial.

## References
- `skills/bmad-agent-gamma/references/interstitial-visual-constraints.md`
- `skills/bmad-agent-marcus/scripts/validate-cluster-plan.py`
- `config/validation.yaml` (new)
