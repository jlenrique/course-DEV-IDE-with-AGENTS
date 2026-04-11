# APP Design Principles

This document defines the architectural principles governing the Agentic Production Platform (APP). All agents, skills, and infrastructure must conform to these principles.

**Source:** Party Mode consultation + parallel Gemini analysis, 2026-03-28. Full record: `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md`

---

## Principle 1: The Three-Layer Intelligence Model

Governs the **internal architecture** of any assessment or production capability.

### Layer 1: Deterministic Contracts (what must be true)

- Per-gate criteria defined in YAML at `state/config/fidelity-contracts/`
- Versioned, human-reviewed, non-agentic
- **These do not change when the LLM improves.**

### Layer 2: Agentic Evaluation (how we verify it's true)

- The agent's judgment that interprets L1 contracts against actual artifacts
- Today: keyword matching, item counting, structural comparison
- Tomorrow: semantic equivalence, cognitive function preservation, pedagogical intent verification
- **Improves without changing contracts — same criteria, smarter detection**

### Layer 3: Learning Memory (how intelligence improves over time)

- BMad memory sidecars capture: what works, what fails, what the user corrects
- Accumulated outcomes refine future evaluation
- **Compound interest — every production run makes the next one better**

### Critical insight

The fidelity *requirement* is the invariant. The fidelity *assessment mechanism* is agentic and evolves. This separation is the architectural key to a system that gets smarter without getting less reliable.

---

## Principle 2: The Hourglass Model

Governs the **flow topology** of the production pipeline — where intelligence is applied vs. constrained.

```
    ╔═══════════════════════════╗
    ║   WIDE COGNITIVE TOP      ║   Agents apply maximum intelligence
    ║   (Synthesis & Design)    ║   to synthesize messy, unstructured
    ║   SME notes → Lesson Plan ║   human inputs into structured
    ║   → Slide Brief → Script  ║   pedagogical artifacts
    ╚═══════════╦═══════════════╝
                ║
        ╔═══════╩═══════╗
        ║  NARROW NECK   ║   Strict schemas, parameter validation,
        ║ (Deterministic ║   hard file contracts (YAML, JSON)
        ║  Contracts)    ║   execute API calls without relying
        ╚═══════╦═══════╝   on LLM interpretation
                ║
    ╔═══════════╩═══════════════╗
    ║   WIDE COGNITIVE BOTTOM   ║   Agents apply intelligence again
    ║   (Creative Execution)    ║   to generate modal-specific outputs
    ║   Gamma slides, ElevenLabs║   based STRICTLY on the deterministic
    ║   audio, Kling video      ║   data passing through the neck
    ╚═══════════════════════════╝
```

**Key rule:** Intelligence must not be used to enforce constraints that can be handled by deterministic code.

---

## The Leaky Neck Diagnostic

A **leaky neck** is any point in the pipeline where agentic judgment enforces a constraint that could be a schema validation, parameter mapping, or code check.

**Test question:** "Are we using an agent's judgment to enforce something that could be a schema rule, a parameter value, or a validation script?" If yes, plug the leak.

**Example (pre-remediation):** Telling Gamma via `additionalInstructions` to "not change this text" — using intelligence to enforce a deterministic constraint.

**Example (post-remediation):** Mapping `fidelity: literal-text` → `textMode: preserve` via the fidelity-control vocabulary. The constraint is now in schema and parameter binding.

---

## Principle 3: The Sensory Horizon

**An agent cannot verify the fidelity of an artifact it cannot perceive.**

The platform must provide sensory bridges that convert non-text modalities into agent-interpretable representations. Without these bridges, agents are blind or deaf to actual outputs.

### Sensory Bridge requirement

Every modality the pipeline produces (image, audio, video, PDF) must have a corresponding bridge script with:
- A canonical request/response schema (defined in `skills/sensory-bridges/references/perception-schema.md`)
- Structured output consumable by both the Fidelity Assessor and Quinn-R's validators

### Confidence Calibration requirement

Confidence levels (HIGH/MEDIUM/LOW) must be operationally defined per modality in a calibration rubric (defined in `skills/sensory-bridges/references/confidence-rubric.md`) with quantitative thresholds — not left to individual agent interpretation.

### Universal Perception Protocol

Every agent consuming a multimodal artifact must follow: **Receive → Perceive → Confirm → Proceed/Escalate**. The confirmation step surfaces the agent's interpretation so perception errors are caught before they propagate.

---

## Principle 3: Event-Driven Contract Enforcement

Governs the **operational enforcement** of canonical contracts — when and how they are validated.

**Core rule:** Canonical contracts are enforced continuously via event hooks, not ad-hoc audits. Enforcement is fail-closed and mandatory.

**Event-driven enforcement layers:**
- **Development/startup:** Session startup (app_session_readiness + preflight), post-story (structural walk), periodic maturity audits
- **Runtime:** Per-gate (Vera fidelity checks), human checkpoints (Storyboard A/B), cumulative drift scans
- **Merge-time:** Contract linting (planned Story 16.4) — fail on schema changes without lane-matrix updates

**Anti-drift mechanism:** Events trigger validation before spend (e.g., preflight before runs, Vera before Quinn-R). Failures circuit-break the pipeline.

**Gap:** Pre-merge linting (Story 16.4) is backlog — contracts can drift between commits.

---

## How the principles interact

- The **Hourglass** identifies *where* determinism belongs in the pipeline flow
- The **Three-Layer Model** defines *how* to build the assessment at each point
- The **Leaky Neck diagnostic** identifies violations — where intelligence is misused for enforcement
- The **Sensory Horizon** defines the *prerequisite* — you cannot assess what you cannot perceive
