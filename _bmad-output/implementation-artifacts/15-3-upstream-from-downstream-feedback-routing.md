# Story 15.3: Upstream-From-Downstream Feedback Routing

**Epic:** 15 — Learning & Compound Intelligence
**Status:** backlog
**Sprint key:** `15-3-upstream-from-downstream-feedback-routing`
**Added:** 2026-04-06
**Depends on:** Story 15.2 (retrospective generates the per-specialist recommendations that feedback routing operationalizes).

## Summary

Formalize the rule that every downstream failure should be mapped to the earliest upstream point that could have prevented it, and implement a YAML-driven routing taxonomy that converts retrospective findings into targeted sidecar pattern entries for the responsible upstream specialist.

## Goals

1. Causal attribution taxonomy: downstream failure → upstream prevention point.
2. YAML-driven routing rules (extensible without code changes).
3. Targeted sidecar writes respecting access-boundaries.md.
4. Evidence-linked attribution (tied to specific learning events, not guessed).
5. Integration with retrospective generation (Story 15.2).

## Existing Infrastructure To Build On

- `scripts/utilities/run_retrospective.py` (Story 15.2) — retrospective with per-specialist recommendations
- `_bmad/memory/*/patterns.md` — sidecar pattern files (target for routed feedback)
- `_bmad/memory/*/access-boundaries.md` — scope control per sidecar (must be respected)
- `docs/lane-matrix.md` — agent lane ownership map (informs routing rules)
- Vera (fidelity failures) → routes upstream to Gary/Irene
- Quinn-R (quality failures) → routes upstream to Irene/Gary
- Compositor issues → routes to Irene/ElevenLabs specialist
- Marcus planning failures → routes to Marcus sidecar

## Key Files

- `state/config/feedback-routing-rules.yaml` — new: routing taxonomy (downstream gate → upstream specialist → sidecar target)
- `scripts/utilities/feedback_router.py` — new: routing engine that reads rules and writes to sidecars
- `_bmad/memory/*/patterns.md` — existing: target for routed feedback entries

## Acceptance Criteria

1. Routing taxonomy defined in `state/config/feedback-routing-rules.yaml` with entries like:
   - Quinn-R learner-effect failure → Irene sidecar (pedagogical calibration)
   - Vera source drift in slides → Irene sidecar (brief accuracy) + Gary sidecar (execution fidelity)
   - Composition manifest ambiguity → Irene sidecar (manifest clarity) + compositor knowledge
   - Repeated Gate 2 human revisions → Gary sidecar (visual quality) + Marcus sidecar (planning)
2. `feedback_router.py` provides: `route_findings(retrospective, routing_rules)` → list of sidecar writes.
3. Each sidecar write is structured: `## Feedback from Run {run_id}\n- Gate: {gate}\n- Finding: {description}\n- Root cause: {classification}\n- Recommended adjustment: {action}`.
4. Sidecar writes respect `access-boundaries.md` constraints for each target sidecar.
5. Attribution is evidence-based: every routed finding links to a specific learning event `run_id` + `gate` + `event_type`.
6. New routing rules can be added to the YAML without code changes.
7. Unit tests: routing logic, sidecar write format, access-boundary enforcement, evidence linking.
