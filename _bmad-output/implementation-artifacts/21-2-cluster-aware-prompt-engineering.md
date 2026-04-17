# Story 21-2: Cluster-Aware Prompt Engineering

**Epic:** 21 - Gary Cluster Dispatch — Gamma Interpretation  
**Status:** done (implemented, tested)  
**Sprint key:** `21-2-cluster-aware-prompt-engineering`  
**Depends on:** `21-1-visual-design-constraint-library.md`, `19-4-validator-hardening-cluster-aware-payloads.md`

## Story
As the cluster prompt engineer, I need per-cluster prompt templates that incorporate cluster metadata and the locked interstitial visual constraints so that generated prompts remain on-theme, safe, and deterministic across different cluster shapes.

## Scope
- Prompt envelopes and templates only (no dispatch execution).
- Deterministic rendering that binds cluster metadata, constraints, and safety rails.
- Auditability: prompt IDs/hashes and template versions recorded.
- Fallback path when required metadata is missing.

## Acceptance Criteria (consensus, party mode)
- **AC1**: Prompt template renders with cluster metadata placeholders (cluster_id, intents/goals, constraints). Missing required fields returns a structured error (`config_missing` / `prompt_over_budget`), no prompt persisted.
- **AC2**: Anti-bleed/safety clauses are injected; safety/PII filters block emission on violation with logged reason codes.
- **AC3**: Interstitial visual constraints (21-1) are applied when present; if absent, prompt renders without dangling text and logs a downgrade.
- **AC4**: Deterministic mode: given identical inputs/config + seed, prompt_id (hash) and prompt text are identical.
- **AC5**: Audit record per prompt includes template version, constraints applied, token budget used, hash/checksum, timestamp; telemetry emits `prompt.rendered`/`prompt.failed` with cluster_id + prompt_id.
- **AC6**: Example scaffolds for small (≤3 items) and large (≥8 items) clusters are provided and pass the validation checklist.

## Tasks / Subtasks
- Define prompt envelope schema + tokens for cluster metadata and constraint slots.
- Implement deterministic renderer + prompt hash (sha256) with audit emit.
- Add safety/PII pre-check hook; return structured errors on violation.
- Wire interstitial constraints (21-1) into rendering; graceful omission path.
- Provide small/large cluster prompt examples + validation checklist.
- Tests: unit (render, safety, determinism), property (unused metadata invariant), integration (fixture clusters, safety violation, constraint mismatch).

## Dev Notes
- Declarative config: `config/prompting.yaml` (templates, safety clauses, token budgets, hashing algorithm).
- Idempotence requirement: same inputs/config → same prompt_id/text; log payload fingerprints, not full bodies.
- Budget: fail fast if prompt exceeds configured token budget; include delta in error.

## Execution & Evidence
- Implementation: `skills/bmad-agent-marcus/scripts/cluster_prompt_engineering.py`
- Config: `state/config/prompting.yaml`
- Tests: `skills/bmad-agent-marcus/scripts/tests/test_cluster_prompt_engineering.py`
- Test run: `python -m pytest skills/bmad-agent-marcus/scripts/tests/test_cluster_prompt_engineering.py` (pass)
- Full suite: `python -m pytest` (pass, 2026-04-11)

## Adversarial Review (BMAD)
- Edge Case Hunter: covered missing required fields, budget overrun, absent constraints, safety blocked terms, seed determinism; no new issues.
- Blind Hunter: prompt hash determinism confirmed with/without seed; config-missing path handled.
- Acceptance Auditor: AC1–AC6 satisfied; no blocking findings.

## Remediation/Notes
- Structural-walk global finding: ffmpeg absent for ElevenLabs audio; unrelated to this story but must be remediated or waived before production trial.

## References
- `skills/bmad-agent-gamma/references/interstitial-visual-constraints.md`
- `skills/bmad-agent-marcus/scripts/validate-cluster-plan.py`
- `skills/bmad-agent-marcus/scripts/run-g1.5-cluster-gate.py`
