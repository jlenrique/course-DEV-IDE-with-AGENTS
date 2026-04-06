# Story 15.7: Agent Judgment Calibration Harness (autoresearch-inspired)

**Epic:** 15 — Learning & Compound Intelligence
**Status:** backlog
**Sprint key:** `15-7-agent-judgment-calibration-harness`
**Added:** 2026-04-06
**Depends on:** Story 15.1 (learning events provide labeled data from gate decisions). Existing woodshed skill and exemplar library (foundation to extend). Multiple tracked runs recommended (builds labeled corpus from real gate decisions).

## Summary

Build an automated calibration harness — inspired by Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) methodology — that iteratively refines individual agent judgment criteria against human-labeled ground truth. The harness adapts the autoresearch pattern (hypothesis → modify → run → evaluate → persist) from ML training experiments to agent prompt/criteria calibration.

Instead of modifying training code and measuring loss, this harness modifies agent evaluation criteria/references and measures agreement rate with human-labeled examples. Each specialist agent (Quinn-R, Vera, Gary, Irene) has specific judgment tasks that can be calibrated this way.

## Design Inspiration

Autoresearch's core loop:
1. Read current state (training script)
2. Form a hypothesis for improvement
3. Modify the code
4. Run experiment, evaluate results
5. Persist improvements, log everything

Adapted for agent calibration:
1. Read current evaluation criteria (SKILL.md references, fidelity contracts, quality rubrics)
2. Form a hypothesis (e.g., "adding a visual density check improves slide quality discrimination")
3. Modify the criteria
4. Run agent judgment against labeled corpus, score agreement with human labels
5. If improved → persist to sidecar; if not → revert and try alternative direction

## Goals

1. Automated calibration loop for agent judgment refinement.
2. Human-labeled corpus management (build from tracked-run gate decisions).
3. Agreement scoring against ground truth.
4. Criteria modification proposals (add/adjust/refine/reweight).
5. Persist-on-improvement / revert-on-regression logic.
6. Calibration reporting with before/after metrics.
7. Extend woodshed skill pattern, not replace it.

## Target Agents and Judgment Tasks

| Agent | Judgment Task | Labeled Data Source | Criteria Location |
|-------|---------------|--------------------|--------------------|
| Quinn-R | Slide quality discrimination (good/bad/marginal) | Gate 2 human approvals/revisions + Quinn-R scores | `skills/bmad-agent-quality-reviewer/references/` |
| Vera | Fidelity assessment (O/I/A detection accuracy) | Gate decisions with Vera findings + human waiver/confirm | `state/config/fidelity-contracts/g0-g6.yaml` |
| Gary | Parameter-to-outcome mapping (human preference) | Gate 2 approvals/revisions correlated with Gamma parameters | `skills/gamma-api-mastery/references/`, sidecar patterns |
| Irene | Pedagogical structure quality (first-pass approval rate) | Gate 1 approvals/revisions on lesson plans/slide briefs | `skills/bmad-agent-content-creator/references/` |

## Existing Infrastructure To Build On

- `skills/woodshed/SKILL.md` — study → reproduce → compare → reflect → register workflow; circuit breaker pattern (3/session, 7 total); two-mode mastery (faithful/creative)
- `resources/exemplars/_shared/comparison-rubric-template.md` — scoring framework for reproductions
- `resources/exemplars/` — per-tool exemplar libraries with labeled artifacts
- `scripts/utilities/learning_event_capture.py` (Story 15.1) — structured gate decisions as labeled data
- `_bmad/memory/*/patterns.md` — sidecar pattern entries (target for persisted refinements)
- `_bmad/memory/*/access-boundaries.md` — scope control for sidecar writes
- `state/config/fidelity-contracts/` — Vera's evaluation criteria (G0-G6)
- `skills/bmad-agent-quality-reviewer/references/` — Quinn-R quality dimensions and rubrics
- `scripts/utilities/marcus_prompt_harness.py` — existing harness pattern (evidence-driven, not runtime executor)

## Key Files

- `scripts/utilities/calibration_harness.py` — new: automated calibration loop engine
- `state/config/calibration/` — new: per-agent labeled corpus storage and calibration config
- `state/config/calibration/{agent}-corpus.yaml` — new: labeled examples per agent
- `reports/calibration/{agent}-calibration-{date}.md` — new: calibration run reports
- `skills/woodshed/SKILL.md` — update: reference calibration harness as automated extension

## Acceptance Criteria

1. Calibration harness loads an agent's current evaluation criteria from SKILL.md references, fidelity contracts, or quality rubrics.
2. Runs the agent's judgment against a labeled corpus, scoring agreement with human labels (exact match, partial match, miss).
3. Proposes a criteria modification: add a check, adjust severity, refine wording, reweight dimension.
4. Re-runs against the same corpus and compares agreement rate.
5. If agreement improves: persist the refinement to the agent's sidecar `patterns.md` with evidence (`{corpus_size, before_agreement, after_agreement, change_description, run_ids_sourced}`).
6. If agreement does not improve: revert the modification and try an alternative direction.
7. Iterates up to configurable `max_cycles` (default: 10) or until convergence (`agreement_delta < 0.02`).
8. Produces a calibration report: `{agent, judgment_task, corpus_size, initial_agreement, final_agreement, refinements_accepted, refinements_rejected, cycles_run, duration}`.
9. Labeled corpus built from tracked-run learning events (Story 15.1): each gate approval/revision/waiver becomes a labeled data point.
10. Corpus management: `add_labeled_example(agent, example, human_label)`, `load_corpus(agent)`, `corpus_stats(agent)`.
11. Callable: `python -m scripts.utilities.calibration_harness --agent quinn-r --task slide-quality --max-cycles 10`.
12. Extends woodshed skill conceptually (automated refinement loop) without modifying woodshed's manual mastery workflow.
13. Unit tests: calibration loop, agreement scoring, persist/revert logic, corpus management, convergence detection.

## Calibration Loop Pseudocode

```
corpus = load_corpus(agent)
criteria = load_current_criteria(agent)
baseline_score = evaluate(agent, criteria, corpus)

for cycle in range(max_cycles):
    hypothesis = propose_modification(criteria, corpus, recent_failures)
    modified_criteria = apply_modification(criteria, hypothesis)
    new_score = evaluate(agent, modified_criteria, corpus)
    
    if new_score > baseline_score:
        persist_to_sidecar(agent, hypothesis, baseline_score, new_score)
        criteria = modified_criteria
        baseline_score = new_score
    else:
        revert(hypothesis)
    
    if convergence_reached(baseline_score, new_score):
        break

generate_report(agent, cycles, baseline_score, final_score, accepted, rejected)
```

## Future Extensions

- Cross-agent calibration: run calibration for multiple agents in sequence, checking for regression in downstream agents after upstream calibration changes.
- Active learning: identify which labeled examples are most informative for calibration (highest disagreement between agent and human).
- Promotion pipeline: when a calibration refinement is stable across 3+ calibration runs, promote from sidecar pattern to deterministic contract criterion (ties into Story 15.5 condensation and Story 16.4 contract linting).
