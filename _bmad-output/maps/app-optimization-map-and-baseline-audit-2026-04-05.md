# APP Optimization Map and Baseline Audit

**Date:** 2026-04-05
**Scope:** APP architecture, agent/skill contracts, deterministic enforcement, probabilistic judgment, learning maturity, and cross-agent system synergy
**Builds on:** `_bmad-output/implementation-artifacts/fidelity-audit-baseline-2026-03-28.md`

---

## Executive Assessment

The APP is no longer a Level 0 fidelity architecture. It now operates as a real bounded-stochastic system:

- deterministic where governance, handoffs, contracts, schemas, and state must be stable
- probabilistic where pedagogy, visual reasoning, parameter choice, fidelity interpretation, and quality judgment should remain adaptive

This is the correct architectural direction for the product vision.

Current state:

- **Deterministic layer maturity:** strong and materially improved since 2026-03-28
- **Probabilistic specialist layer maturity:** promising but uneven
- **Learning layer maturity:** present in structure, weak in realized compound learning
- **System synergy maturity:** good in architecture, partial in operational feedback closure

Headline conclusion:

**The platform's main optimization opportunity is no longer "add more contracts." It is "convert system experience into calibrated specialist intelligence without collapsing creativity into brittle rules."**

---

## Design Position

The repo already encodes the correct philosophical stance in `docs/app-design-principles.md`:

- L1 deterministic contracts define what must be true
- L2 agentic evaluation determines how the system judges whether it is true
- L3 learning memory captures what improves over time

The right optimization target is therefore not "more determinism everywhere" and not "more freedom everywhere." It is:

1. tighten deterministic enforcement at the neck
2. preserve specialist freedom above and below the neck
3. make learning compound instead of merely append-only

---

## Optimization Map

## 1. Components That Should Become More Deterministic

| Area | Why | Current State | Optimization Target |
|------|-----|---------------|---------------------|
| Governance validation | Scope, outputs, and authority are safety boundaries | Mostly enforced in agent instructions and baton scripts | Add reusable code-level middleware/helpers for envelope validation before specialist execution |
| Contract validation | Contracts are core invariants | YAML contracts exist and are rich, but structural validation is not the center of daily ops | Add routine contract lint/validation to maintenance and pre-merge checks |
| Gate entry/exit criteria | Prevent drift between docs and execution | Several validators already exist for Gary/Irene handoffs | Expand explicit validators for all high-cost transitions, especially audio/composition stages |
| Memory write discipline | Learning quality depends on structured capture | Sidecars exist, but most are placeholder or free-form | Add structured memory append schemas by agent and by gate |
| Cross-run observability | Needed for compound learning and system tuning | Runtime state exists; learning rollups are thin | Add gate outcome summaries and recurring issue aggregation across runs |
| Quality-control script coverage | Scriptable checks should not be done by prose-only judgment | Accessibility/brand/logging exist; other checks are partial | Expand deterministic validators for manifest consistency, timing, caption sync, asset completeness, and contract drift |

## 2. Components That Should Remain Probabilistic

| Area | Why | Current State | Optimization Target |
|------|-----|---------------|---------------------|
| Marcus production planning | User intent, context, and tradeoffs are not fully enumerable | Strong | Keep probabilistic; improve with better run retrospectives and routing heuristics |
| Irene pedagogy and narration strategy | Instructional design is judgment-heavy and should evolve with model quality | Strong conceptually | Preserve freedom; constrain only outputs and evidence requirements |
| Gary parameter selection and visual treatment | Visual execution benefits from experimentation and model evolution | Strong | Preserve freedom above deterministic vocabulary bindings |
| Vera source-fidelity interpretation | Semantic fidelity judgment will improve materially with better models | Good direction | Preserve judgment; strengthen evidence capture and calibration loops |
| Quinn-R learner-effect quality judgment | Intent fidelity and instructional soundness are not reducible to pure rules | Good direction | Preserve judgment; tighten structured output and calibration capture |

## 3. Components That Must Stay Hybrid

| Area | Deterministic Portion | Probabilistic Portion | Optimization Target |
|------|-----------------------|-----------------------|---------------------|
| Sensory bridges | Canonical schema, cache, modality routing | Image/video interpretation | Improve confidence thresholds and downstream reuse |
| Fidelity gates | Gate ordering, contract fields, severity policy | Semantic comparison, invention detection, drift interpretation | Add more exercised examples and calibration memories |
| Style system | Style bible precedence, style-guide parameter merges | Specialist application and adaptation to context | Distinguish immutable standards from learned tactical preferences |
| Motion workflow | Gate 2M, Motion Gate, manifest hydration | Creative motion concept selection and narration integration | Keep motion governance deterministic and motion design agentic |

---

## Baseline Audit: 2026-04-05

### Scoring Key

- **ABSENT**: capability missing
- **WEAK**: partial and unreliable
- **PARTIAL**: implemented but with meaningful gaps
- **GOOD**: implemented and operational
- **STRONG**: implemented, tested, and integrated into normal operation

### Gate × Pillar Matrix

| Gate | Artifact | L1 Contracts | L2 Evaluation | L3 Memory | Perception |
|------|----------|:---:|:---:|:---:|:---:|
| **G0** | Source bundle | GOOD | PARTIAL | WEAK | GOOD |
| **G1** | Lesson plan | GOOD | PARTIAL | WEAK | OK |
| **G2** | Slide brief | GOOD | PARTIAL | WEAK | OK |
| **G3** | Generated slides | STRONG | GOOD | PARTIAL | GOOD |
| **G4** | Narration + manifest | STRONG | GOOD | WEAK | GOOD |
| **G5** | Audio | GOOD | PARTIAL | WEAK | GOOD |
| **G6** | Composition | PARTIAL | WEAK | ABSENT | PARTIAL |

### Baseline Interpretation

- **Biggest improvement since 2026-03-28:** G4 moved from the riskiest blind spot to a governed gate with explicit perception lineage and validator support.
- **Most mature gates today:** G3 and G4.
- **Least mature gate today:** G6. The composition end of the pipeline still lags the rest of the system in independent fidelity maturity and learning capture.
- **Weakest pillar overall:** L3 memory. The architecture for learning exists; the realized learning loop is still thin.

### Delta vs 2026-03-28

| Area | 2026-03-28 | 2026-04-05 | Change |
|------|------------|------------|--------|
| G0 contracts | ABSENT | GOOD | major improvement |
| G1/G2 contracts | WEAK | GOOD | clear improvement |
| G3 contract formalization | PARTIAL/self-graded | STRONG/GOOD | clear improvement |
| G4 perception | GAP | GOOD | critical improvement |
| G5 audio blind spot | BLIND | GOOD/PARTIAL | major improvement |
| G6 coverage | ABSENT/BLIND | PARTIAL/WEAK | some improvement |
| Learning maturity | mostly empty | still weak | little change |

---

## Named-Agent Intelligence Audit

This section rates not raw model intelligence, but how well each specialist's intelligence is architected, grounded, and operationalized inside the APP.

### Marcus

**Rating:** 4.5 / 5

**Strengths**

- Very clear lane ownership: orchestration, user interaction, checkpoint choreography
- Strong separation from tool execution
- Strong state discipline: mode, baton, gate transitions
- Good grounding in style bible, exemplars, and workflow templates
- Good whole-system awareness and route planning

**Constraints / gaps**

- Some governance enforcement still depends on specialist instruction compliance rather than shared enforcement utilities
- System retrospection is richer in doctrine than in aggregated telemetry

**Assessment**

Marcus is one of the most developed agent designs in the repo. He already functions as a real orchestrator, not just a branded prompt.

### Gary

**Rating:** 4.2 / 5

**Strengths**

- Strong mastery architecture: clear separation between judgment, skill, and API client
- Good parameter reasoning and strong deterministic bindings through `gamma-api-mastery`
- Good articulation of visual tradeoffs and embellishment control
- Good use of perception before self-assessment
- Sidecar patterns show real knowledge crystallization, not only placeholders

**Constraints / gaps**

- Learning is still narrow: parameter patterns are richer than run-outcome patterns
- Theme/template calibration is still earlier than it could be
- Tool-quality self-assessment is stronger than cross-run fidelity learning

**Assessment**

Gary is one of the most operationally mature specialists. He is already realizing a good portion of his potential, especially on the tool-execution side.

### Irene

**Rating:** 3.9 / 5

**Strengths**

- Strong pedagogical identity and lane clarity
- Good two-pass architecture
- Major improvement through mandatory Pass 2 perception contract
- Good downstream awareness through segment-manifest contract

**Constraints / gaps**

- Learning sidecar remains mostly unexercised
- Writer-delegation intelligence is architecturally present but not yet richly evidenced in memory
- Instructional calibration patterns are less crystallized than Gary's execution patterns

**Assessment**

Irene is conceptually strong and strategically placed in the pipeline. Her realized intelligence lags her designed potential mainly because calibration and memory exploitation are still early.

### Vera

**Rating:** 3.8 / 5

**Strengths**

- Excellent lane discipline
- Strong conceptual grounding in the three-layer model
- Clear forensic posture and evidence requirements
- Good use of shared sensory infrastructure

**Constraints / gaps**

- Memory/calibration is still largely empty
- Production evidence of repeated gate-by-gate learning is still limited
- G6 remains underdeveloped

**Assessment**

Vera is architecturally well-designed, but still maturing from "good framework" to "deeply calibrated evaluator."

### Quinn-R

**Rating:** 3.8 / 5

**Strengths**

- Clean separation from Vera and Irene
- Strong hybrid design: scriptable checks delegated, judgment retained
- Good articulation of learner-effect quality and intent fidelity
- Good two-pass review design

**Constraints / gaps**

- Quality-control deterministic coverage is still narrower than Quinn-R's full conceptual scope
- Calibration memory remains mostly unrealized
- More systematic cross-run pattern extraction is needed

**Assessment**

Quinn-R is well-conceived and likely to become very strong, but today is not yet extracting enough learning from repeated review activity.

### Whole-Core-Team Assessment

**Core named team:** Marcus + Irene + Gary + Vera + Quinn-R

**Rating:** 4.1 / 5 for architecture, 3.6 / 5 for realized adaptive intelligence

Interpretation:

- the design is ahead of the realized learning state
- the lanes are unusually well defined
- the system is better at bounded execution than at accumulating judgment capital

---

## System Synergy Audit

## Positive Synergies

### 1. Marcus -> Irene -> Gary -> Irene is structurally sound

This is the system's most important productive loop:

- Marcus frames and routes
- Irene turns intent into pedagogy
- Gary turns pedagogy into visuals
- Irene rebinds narration to actual approved visuals

That is a strong cross-agent design. It preserves creativity while reducing downstream drift.

### 2. Vera and Quinn-R are not redundant

The repo correctly distinguishes:

- source-faithfulness
- quality standards
- tool-execution quality

This reduces category confusion and improves auditability.

### 3. Shared perception infrastructure improves whole-system coherence

The sensory-bridges layer creates reusable perception rather than ad hoc agent-specific interpretation. That is a major platform-level synergy.

### 4. The baton contract reduces hidden side-channel edits

The specialist redirect vs standalone-consult behavior lowers orchestration corruption risk and keeps Marcus authoritative during active runs.

## Negative Synergies / Friction Points

### 1. Learning is siloed rather than compounded

Each sidecar exists, but the system does not yet strongly aggregate:

- recurring cross-agent failure themes
- user waivers by gate and severity
- upstream causes of downstream failures

This means the platform learns locally more than systemically.

### 2. Deterministic checks are stronger at the center than at the tail

Mid-pipeline handoffs are better governed than the final composition end. That creates asymmetry: the system is most disciplined before publish-facing assembly, not at it.

### 3. Some governance still lives in prose instead of shared enforcement

Many specialists validate `allowed_outputs` and `decision_scope` in instructions. That is philosophically correct but operationally weaker than reusable code-level validation wrappers.

### 4. Human approval is strong, but human correction harvesting is weak

The human is deeply integrated at gates, but the system is still not consistently converting human corrections into structured agent calibration.

---

## Repeatable Audit Framework

This audit can be re-run at any time. It should become a standard maintenance instrument.

## A. Deterministic vs Probabilistic Boundary Audit

For each subsystem, ask:

1. What must be invariant?
2. Is that invariant represented in code, schema, or versioned config?
3. What should remain a specialist judgment?
4. Is that judgment constrained by contract and evidence?
5. Is the outcome being learned from?

## B. Agent Maturity Audit

For each named specialist, score 1-5 on:

1. **Lane clarity**: does the agent own a distinct judgment domain?
2. **Contract discipline**: does it respect governance, outputs, and boundaries?
3. **Operational grounding**: are its references, skills, scripts, and templates sufficient?
4. **Perception discipline**: does it perceive before judging when required?
5. **Learning maturity**: does it capture and use calibration patterns?
6. **System contribution**: does it improve the whole pipeline rather than merely its local output?

## C. Synergy Audit

For each important handoff, rate:

1. clarity of source of truth
2. clarity of output contract
3. deterministic validation coverage
4. perception adequacy
5. downstream usability
6. feedback return path to the upstream producer

Audit these handoffs explicitly:

- Marcus -> Irene Pass 1
- Irene Pass 1 -> Gary
- Gary -> Marcus Gate 2 package
- Marcus/Gary -> Irene Pass 2
- Irene Pass 2 -> Vera
- Vera -> Quinn-R
- Quinn-R -> Marcus/Human
- ElevenLabs/Kira -> Quinn-R pre-composition
- manifest -> compositor -> human assembly

## D. Audit Cadence

- **Per story touching contracts or specialist behavior:** quick check
- **Per epic:** full audit
- **Before declaring production-ready workflow changes:** full audit + delta
- **After 3-5 real runs in a workflow family:** learning audit focused on sidecars and recurring patterns

---

## Recommended Optimization Priorities

## Priority 0: Convert learning from placeholder to operational

This is the biggest strategic gain.

Actions:

- define structured sidecar append formats for Marcus, Irene, Gary, Vera, Quinn-R
- require post-gate memory capture when user approves, revises, or waives
- aggregate recurring issues by gate, specialist, and content pattern

Expected payoff:

- actual compound intelligence
- faster calibration
- better routing and fewer repeated failures

## Priority 1: Move governance validation into shared utilities

Actions:

- implement reusable envelope validators for `allowed_outputs`, `decision_scope`, and authority chain
- reduce duplicated governance prose across specialist SKILL files
- standardize `scope_violation` creation in code

Expected payoff:

- less drift
- less prompt-fragility
- cleaner specialist prompts

## Priority 2: Strengthen G6 and terminal-pipeline assurance

Actions:

- raise composition-stage maturity to match G3/G4
- make final assembly validation less dependent on informal human checking alone
- improve video/composition bridge confidence and report integration

Expected payoff:

- stronger end-of-pipeline reliability
- better publication confidence

## Priority 3: Build cross-agent retrospective intelligence

Actions:

- add a periodic "run postmortem" artifact summarizing:
  - where drift originated
  - which gate caught it
  - which correction was accepted
  - what should be learned by which agent

Expected payoff:

- system-level synergy improves
- agents stop learning only in isolation

## Priority 4: Separate immutable standards from adaptive tactics even more sharply

Actions:

- keep style bible and contracts human-curated
- keep tactical parameter heuristics and specialist preferences adaptive
- periodically review whether any agentic tactic should be promoted into deterministic policy

Expected payoff:

- better long-term evolution as models improve
- less accidental ossification of things that should remain creative

---

## What Should Not Be "Optimized Away"

The following are strengths and should remain intentionally probabilistic:

- Irene's pedagogical interpretation
- Gary's visual and parameter judgment
- Vera's semantic fidelity interpretation
- Quinn-R's learner-effect judgment
- Marcus's orchestration and tradeoff handling

If these become over-determinized, the platform will become safer but dumber.

The platform's edge is not that it has agents.
Its edge is that it places deterministic rigor around agent intelligence without suffocating it.

---

## Baseline Conclusion

The current APP is best described as:

**A strong deterministic governance shell around a moderately mature but high-potential specialist intelligence system.**

Current maturity profile:

- **Architecture maturity:** high
- **Contract maturity:** high in the core middle of the pipeline
- **Operational validation maturity:** moderate to high
- **Named specialist maturity:** moderate to high
- **Learning maturity:** low to moderate
- **Whole-system synergy maturity:** moderate, with clear upside

If optimized correctly, the next major gain will not come from adding more named agents.
It will come from making the existing named agents learn better together.
