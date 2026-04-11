# Party Mode Kickoff: Narrated Slides Enhancement

**Date:** 2026-04-10  
**Branch:** `DEV/slides-redesign`  
**Scope:** New epics that enhance APP's narrated-slides design and production approach

## Why This Kickoff Exists

The formal `bmad-party-mode` skill is not installed in this checkout, so this brief captures the equivalent multi-agent kickoff synthesis from PM, architecture, QA, and implementation perspectives.

## Scope Decision

The team scoped this kickoff to:

- **Epic 15: Learning & Compound Intelligence**
- **Epic 16: Bounded Autonomy Expansion**
- **Epic 17: Research & Reference Services**

The team explicitly **did not** include Epic 18 in the first wave, because that epic expands APP into additional workflow families beyond narrated slides.

## Party Mode Consensus

### Start Order

1. **Start with Epic 15**
2. **Treat Epic 17 as optional, bounded support work**
3. **Defer Epic 16 until Epic 15 produces real evidence**

### Rationale

- The narrated-slides pipeline now needs to **learn from real tracked runs**, not only execute them.
- Epic 15 creates the evidence layer that later autonomy work depends on.
- Epic 17 can enrich narrated-slide production, but it is not required to improve the core production loop.
- Epic 16 is valuable, but unsafe to start first because it risks weakening governance before the system has enough evidence to automate routine decisions responsibly.

## First Wave Instruction

### Primary Story To Begin

**Begin with Story 15.1: Learning Event Schema & Capture Infrastructure**

This is the approved first slice for the narrated-slides enhancement track.

### Why 15.1 First

- It creates immediate value without widening the blast radius.
- It captures real gate decisions and revisions from narrated-slide runs.
- It unlocks Story 15.2 retrospectives and the later evidence baseline for Epic 16.
- It can be implemented additively against the current pipeline.

## First Build Slice

### Deliverables

- `state/config/learning-event-schema.yaml`
- `scripts/utilities/learning_event_capture.py`
- Per-run `learning-events.yaml` append path
- Initial integration into one or two high-signal narrated-slide decision points

### Recommended Initial Hook Points

- Irene Pass 2 validation outcomes
- Storyboard B approval / revision / waiver decisions

These are the smallest, highest-signal narrated-slide events to instrument first.

## Reuse-First Guidance

Use existing infrastructure before creating anything new:

- `scripts/utilities/ad_hoc_persistence_guard.py`
- production run lifecycle and stage management under `skills/production-coordination/`
- existing Marcus validators, especially Irene Pass 2 handoff validation
- YAML config patterns under `state/config/`
- existing run reporting and gate coordination surfaces

## Guardrails

### Do in Wave 1

- Capture learning events
- Generate structured retrospective-ready data
- Keep schema additive and evidence-linked
- Preserve current gate authority and HIL checkpoints

### Do Not Do in Wave 1

- Do not enable Marcus autonomous checkpoint skipping
- Do not implement full pattern condensation or calibration harnesses yet
- Do not inject research/citations directly into narration yet
- Do not redesign the whole narrated-slides architecture in one pass
- Do not downgrade hard validator failures to advisory just to keep momentum

## Epic-Specific Direction

### Epic 15

**Proceed now.**

Priority order inside the epic:

1. `15.1` learning-event schema and capture
2. `15.2` tracked-run retrospective artifact
3. `15.3` upstream-from-downstream feedback routing
4. `15.6` workflow-family learning ledger

Defer until more run evidence exists:

- `15.5` pattern condensation
- `15.7` judgment calibration harness

### Epic 17

**Optional bounded support track.**

If started early, limit it to:

- `17.1` research service foundation and API integration

Do **not** start with:

- inline citation injection into narration
- automatic research-driven script modification
- hypothesis mode inside production runs

### Epic 16

**Do not begin as a primary build wave yet.**

Epic 16 should wait until Epic 15 has produced enough tracked-run evidence to classify routine decisions safely.

If any Epic 16 work is touched early, limit it to low-risk deterministic foundations:

- shared governance enforcement utilities
- contract linting

Do **not** begin with:

- autonomous routing
- automatic checkpoint bypass
- policy changes that alter operator-visible control flow

## Definition of Success for This Kickoff

This kickoff is successful when:

- the team begins implementation on **Story 15.1**
- the first narrated-slide learning events are captured from real tracked-run decisions
- the resulting evidence is strong enough to support **15.2** next
- Epic 16 remains deferred until justified by data

## Working Instruction To The Team

Begin work on the narrated-slides enhancement track with **Epic 15, Story 15.1**.

Treat **Epic 17** as optional bounded support work only if it does not distract from the learning layer.

Hold **Epic 16** until the system has sufficient tracked-run evidence to expand autonomy safely.
