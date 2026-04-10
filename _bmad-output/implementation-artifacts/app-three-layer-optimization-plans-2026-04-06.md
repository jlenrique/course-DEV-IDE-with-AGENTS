# APP Three-Layer Optimization Plans

**Date:** 2026-04-06
**Purpose:** Convert the APP maturity audit into three concrete optimization plans:

1. deterministic layer optimization
2. probabilistic layer optimization
3. learning and synergy layer optimization

**Source inputs:**

- `docs/app-design-principles.md`
- `_bmad-output/implementation-artifacts/app-optimization-map-and-baseline-audit-2026-04-05.md`
- `_bmad-output/implementation-artifacts/fidelity-audit-baseline-2026-03-28.md`

## BMAD Epic Seed Note

This document is intended to seed two near-future BMAD epics for this repo:

- **Learning epic**
  - primary basis: Plan 3 in this document
  - target: convert tracked runs, gates, retrospectives, and cross-agent corrections into compound organizational intelligence
- **Autonomy epic**
  - complementary basis: Plans 1 and 2, with selected dependencies on Plan 3
  - target: expand bounded system autonomy without bypassing governance, specialist lanes, or human checkpoint authority

Recommended dependency order:

1. use tracked trial runs to generate real operational evidence
2. shape the learning epic from that evidence
3. shape the autonomy epic after the learning design clarifies what the system should autonomize and what it should continue to route through specialists and human gates

Core warning for both epics:

Do not optimize by flattening specialist intelligence into procedural shortcuts.
The design objective is stronger bounded intelligence, not thinner intelligence.

---

## How To Read This

These are not three independent projects.

They are three interacting optimization tracks:

- the **deterministic** plan hardens invariants
- the **probabilistic** plan improves specialist judgment quality
- the **learning/synergy** plan turns repeated runs into compound system intelligence

If forced to prioritize, do not start with only deterministic hardening.
The biggest underdeveloped advantage in this repo is the **learning/synergy layer**.

Recommended sequencing:

1. deterministic hardening of the most important weak points
2. immediate instrumentation for learning capture
3. specialist calibration upgrades
4. cross-agent retrospection and compound learning loops

---

## Plan 1: Deterministic Layer Optimization

## Strategic Goal

Make the narrow neck more explicit, reusable, and enforceable in code so specialists spend less cognition enforcing rules and more cognition exercising judgment.

## Success Definition

- governance constraints are enforced by shared code, not repeated prose
- high-cost handoffs are fail-closed with explicit validators
- core contracts are linted and version-safe
- mode, baton, gate, and output-scope behavior are unambiguous and testable
- deterministic checks cover everything that should not depend on model interpretation

## Main Problems To Solve

1. Governance validation is duplicated in agent instructions.
2. Some transition checks are strong in the middle of the pipeline but thin at the tail.
3. Contract integrity is rich but not treated as a first-class continuously validated asset.
4. Some deterministic obligations are still implicit in documentation rather than executable.

## Workstreams

### D1. Shared Governance Enforcement Utilities

Build a shared helper module that validates:

- `governance.allowed_outputs`
- `governance.decision_scope.owned_dimensions`
- `authority_chain`
- `route_to`
- required envelope fields per specialist

Use it across:

- Marcus dispatch helpers
- Gary
- Irene
- Vera
- Quinn-R

Target outcome:

- specialists stop implementing governance discipline as repeated prose-only ritual
- scope violations become consistent, machine-checkable outputs

### D2. Expand Handoff Validators

Current handoff validation is strongest around Gary and Irene.
Extend that model to remaining expensive transitions:

- Irene Pass 1 output bundle integrity
- Quinn-R pre-composition input completeness
- ElevenLabs write-back completeness and path integrity
- compositor manifest readiness
- final composition bundle completeness

Target outcome:

- every expensive transition has a deterministic gatekeeper script
- fewer late-stage surprises

### D3. Contract Linting and Drift Protection

Create or formalize a contract-validation routine for:

- fidelity contract YAML structure
- schema field consistency
- template references in contracts
- perception modality references
- gate names and ownership consistency

Run it:

- on contract edits
- in pre-merge checks
- in APP maturity audits

Target outcome:

- contracts become operational assets, not only architectural documents

### D4. Deterministic Final-Mile Hardening

Strengthen G5/G6 deterministic checks:

- audio file presence and naming integrity
- segment coverage completeness
- VTT monotonicity and segment alignment
- motion asset existence and readiness
- assembly bundle completeness
- manifest field completeness for composition

Target outcome:

- terminal stages stop lagging the maturity of the core pipeline

## Deliverables

- shared governance validation module
- expanded validator suite for late-stage handoffs
- contract lint command and tests
- updated maturity audit procedure to call deterministic validation explicitly

## Metrics

- % of specialists using shared governance enforcement
- % of high-cost transitions with explicit validator coverage
- contract drift incidents per month
- late-stage failures caused by missing/invalid inputs

## Risks

- over-hardening can push nuanced specialist choices into rigid code
- duplicated checks can create maintenance drag if not centralized

## Guardrail

Only harden what is actually invariant.
Do not encode pedagogy, style judgment, or semantic reasoning into brittle rules.

## Suggested Implementation Sequence

1. shared governance validation
2. G5/G6 validator expansion
3. contract linting
4. audit integration

---

## Plan 2: Probabilistic Layer Optimization

## Strategic Goal

Increase the quality, calibration, and effective range of specialist judgment without turning specialists into deterministic shells.

## Success Definition

- Marcus routes more intelligently with better use of prior outcomes
- Irene produces more consistently strong pedagogical structures and better writer delegation
- Gary improves theme/parameter choices with less trial friction
- Vera and Quinn-R become more calibrated, evidence-rich evaluators
- specialists get better over time while staying within their lanes

## Main Problems To Solve

1. Specialist identities and lanes are strong, but realized calibration is uneven.
2. Gary has real crystallized knowledge; the others are earlier in maturity.
3. Many specialist capabilities exist conceptually before they exist behaviorally in repeated production outcomes.
4. The system has strong doctrines for judgment, but lighter mechanisms for comparing judgment quality over time.

## Workstreams

### P1. Marcus Orchestration Calibration

Improve Marcus using structured post-run evidence:

- which routing patterns led to fewer revisions
- which gates caught the most useful issues
- which specialists required repeated correction in which contexts
- when Marcus should escalate earlier vs continue autonomously

Target outcome:

- Marcus becomes a better producer, not just a better traffic router

### P2. Irene Instructional Calibration

Formalize structured calibration capture for Irene:

- which lesson structures were approved first-pass
- which narration patterns led to Quinn-R praise vs revision
- which writer-delegation patterns actually worked
- which Bloom/content-type mappings produced good learner-effect outcomes

Target outcome:

- Irene becomes measurably better at pedagogy and delegation, not just structurally compliant

### P3. Gary Visual/Parameter Mastery Expansion

Gary is currently the strongest realized specialist.
Extend that strength by capturing:

- theme-to-content-type success patterns
- template vs free generation success conditions
- literal vs creative slide treatment outcomes
- failure signatures by layout family
- preferred fallback patterns by artifact type

Target outcome:

- Gary's specialist intelligence becomes reusable production capital, not isolated know-how

### P4. Vera Calibration and Evidence Density

Strengthen Vera's evaluation quality by capturing:

- waived findings and why
- false-positive patterns
- missed-finding postmortems
- gate-specific evidence standards
- calibration by mode and preset

Target outcome:

- Vera evolves from principled evaluator to calibrated evaluator

### P5. Quinn-R Quality Calibration

Capture and learn from:

- which findings humans care about most
- severity adjustments requested by the user
- repeated specialist failure patterns
- which feedback phrasing leads to fastest remediation

Target outcome:

- Quinn-R becomes more aligned to actual reviewer values without losing rigor

## Deliverables

- per-specialist calibration schema
- specialist-specific retrospective prompts or append routines
- lightweight judgment QA rubric per specialist
- periodic sidecar condensation process

## Metrics

- first-pass approval rate by specialist
- average revisions per specialist by artifact type
- waiver rate by evaluator and finding class
- specialist-specific recurring issue counts over time
- human correction reuse rate

## Risks

- sidecars can become bloated and low-signal
- specialists can overfit to one user's preferences if learning is captured naively
- too much meta-evaluation can slow production

## Guardrail

Optimize specialist judgment quality, not specialist conformity.
The goal is better decisions, not flatter behavior.

## Suggested Implementation Sequence

1. Irene and Vera calibration capture
2. Quinn-R severity-learning capture
3. Marcus routing retrospection
4. Gary advanced theme/template outcome tracking

---

## Plan 3: Learning and Synergy Layer Optimization

## Strategic Goal

Turn the APP from a well-governed multi-agent pipeline into a compound-learning production system where specialists improve not only individually, but through each other.

This is the most underdeveloped and highest-upside layer in the current repo.

## Success Definition

- user approvals, revisions, waivers, and escalations become structured learning signals
- handoffs improve because downstream failures flow back upstream in reusable form
- recurring problems are attributed systemically, not only locally
- the platform develops cross-agent intelligence, not just isolated specialist memory
- mature workflow families become easier, faster, and more reliable over time

## Core Diagnosis

Right now the repo has:

- sidecars
- gates
- validators
- strong architecture

But it only partially has:

- cross-agent retrospective memory
- causal learning loops
- system-level pattern extraction
- compound synergy intelligence

The result is:

- good bounded execution
- weak learning closure

## Main Problems To Solve

1. Human corrections are not consistently harvested into reusable calibration.
2. Sidecars learn locally, but the system rarely learns across lanes.
3. Downstream failures are not systematically converted into upstream improvement signals.
4. There is no clear recurring “run retrospective” mechanism that updates the whole team.
5. Synergy quality is inferred ad hoc rather than measured.

## Workstreams

### L1. Structured Learning Event Capture

Create a canonical learning-event format for each meaningful production event:

- gate approval
- gate revision
- gate waiver
- circuit break
- quality failure
- fidelity failure
- successful first-pass approval
- manual override

Each event should capture:

- run id
- gate
- artifact type
- producing specialist
- reviewing specialist if applicable
- human decision
- root cause classification
- accepted remediation
- learning targets

Target outcome:

- the system stops losing its most valuable feedback

### L2. Upstream-From-Downstream Feedback Routing

Formalize the rule:

**every downstream failure should be mapped to the earliest upstream point that could have prevented it**

Examples:

- Quinn-R flags weak learner-effect -> feed back to Irene
- Vera flags source drift in slides -> feed back to Irene brief and Gary execution pattern
- composition issue from manifest ambiguity -> feed back to Irene and compositor
- repeated human revisions at Gate 2 -> feed back to Gary and Marcus planning

Target outcome:

- the system learns causally, not only descriptively

### L3. Cross-Agent Retrospective Artifact

After each tracked/default run, generate a structured retrospective containing:

- what worked unusually well
- what failed
- where failure originated
- where failure was detected
- what correction fixed it
- which agents should learn what
- whether the issue should become deterministic policy, specialist guidance, or a one-off note

Write outputs to:

- run history / implementation artifacts
- specialist sidecars where appropriate
- optionally a central system-patterns ledger

Target outcome:

- the APP starts accumulating organizational memory, not just personal memory

### L4. Synergy Scorecard

Define measurable health indicators for handoff quality:

- handoff completeness rate
- downstream usability rate
- first-pass acceptance of upstream artifacts
- correction locality
  - good: issue caught near source
  - bad: issue caught 2-3 stages later
- repeated cross-agent friction signatures

Audit key handoffs:

- Marcus -> Irene
- Irene -> Gary
- Gary -> Irene Pass 2
- Irene -> Vera
- Vera -> Quinn-R
- Quinn-R -> Marcus/Human
- manifest -> compositor

Target outcome:

- “synergy” becomes an operationally visible property, not just a design aspiration

### L5. Multi-Agent Pattern Condensation

Add a periodic condensation pass that produces:

- top recurring success patterns
- top recurring failure patterns
- patterns that belong in deterministic policy
- patterns that belong in specialist memory
- patterns that should remain case-specific

This should prevent:

- sidecar sprawl
- duplicated learnings in multiple agents
- contradictory local lessons

Target outcome:

- better signal density
- less memory fragmentation

### L6. Workflow-Family Learning

Learn not only by agent, but by workflow family:

- narrated deck video export
- motion-enabled narrated lesson
- assessment generation
- deployment workflows

For each workflow family, track:

- frequent failure modes
- expensive stages
- best escalation points
- best preset/mode combinations
- common human preferences

Target outcome:

- the platform becomes smarter at the level the user actually experiences: workflow families, not only internal agents

## Deliverables

- canonical learning-event schema
- run retrospective template and process
- cross-agent feedback routing taxonomy
- synergy scorecard
- periodic condensation routine
- workflow-family learning ledger

## Metrics

- % of tracked runs with retrospective completed
- % of human gate decisions converted into structured learning events
- reduction in repeated failure causes across runs
- correction locality score
- first-pass approval rate by workflow family
- number of insights promoted from memory into deterministic policy

## Risks

- too much retrospective overhead can slow operations
- learning capture can become verbose but low-value
- cross-agent attributions can become noisy if root causes are guessed instead of evidenced

## Guardrails

- only capture learning that changes future decisions
- distinguish clearly between:
  - deterministic policy candidate
  - specialist calibration note
  - workflow-family heuristic
  - one-off exception
- do not let memory become a dumping ground

## Suggested Implementation Sequence

1. define learning-event schema
2. implement tracked-run retrospective artifact
3. create cross-agent routing rules for failures and approvals
4. introduce synergy scorecard on core handoffs
5. add periodic condensation and policy-promotion review

---

## First 30 Days Roadmap

If you want a practical rollout rather than three abstract plans, do this:

### Days 1-10

- build shared governance validation helpers
- define learning-event schema
- add run retrospective template

### Days 11-20

- implement G5/G6 validator expansion
- wire human gate outcomes into structured learning events
- start Irene, Vera, and Quinn-R sidecar calibration capture

### Days 21-30

- add synergy scorecard for the six core handoffs
- run one condensation pass on accumulated patterns
- review which patterns should be promoted into deterministic policy

---

## What To Expect If You Execute These Plans Well

### If deterministic plan succeeds

- fewer preventable failures
- cleaner gates
- lower orchestration ambiguity
- more reliable cost control

### If probabilistic plan succeeds

- better pedagogy
- better visuals
- better evaluator judgment
- fewer low-value revisions

### If learning/synergy plan succeeds

- the platform gets better as a system, not just as a collection of agents
- downstream quality starts improving upstream behavior automatically
- your APP becomes more durable as LLMs change, because the organization of intelligence improves with the models

---

## Final Recommendation

The deterministic and probabilistic plans are both important.
But the **learning/synergy layer** is the strategic multiplier.

That is where this APP can move from:

- "well-designed agent pipeline"

to:

- "institutional intelligence system for course production"

If you neglect that layer, the system will remain competent but plateau.
If you build it well, the system should improve in quality, speed, and alignment with every serious tracked run.
