# Epics: Interstitial Slide Clusters (Workflow A)

Status: Draft — Party Mode consensus, 2026-04-10
Approach: Workflow A (clusters planned and generated from the initial plan, single Gamma pass)

## Problem Statement

Narrated slide presentations for asynchronous online courses dwell too long on a single static image (~35 seconds average). The solo student has no live presenter, no talking head — the slide is the entire visual field. We need **interstitial slides** that form **clusters** (head slide + 1-3 supporting interstitials) for progressive visual disclosure, changing the visual every 2-3 sentences while maintaining coherent topical units.

## Design Principles

- Interstitials = **progressive disclosure**, not decoration
- A cluster (head + interstitials) is one coherent visual thought
- Illustrations are judicious — not "Where's Waldo"
- Interstitials reveal, emphasize, or reframe content from the head slide — never introduce new concepts
- The visual evolves in step with narration, keeping the student anchored without overwhelming

## Interstitial Type Vocabulary

Five types, each with distinct visual grammar and prompt strategy:

| Type | Purpose | Visual Rule |
|------|---------|-------------|
| **reveal** | Surface one element from head at larger scale or with annotation | Same visual DNA, zoomed/isolated |
| **emphasis-shift** | Isolate one of several points with typographic weight | Others fade or disappear |
| **bridge-text** | Single key phrase, statistic, or quote in large type | Atmospheric background from head, no new imagery |
| **simplification** | Strip information-dense head to one data series or element | Cognitive load deliberately drops |
| **pace-reset** | Near-blank or icon-only visual rest | Used after dense clusters, before next head |

## Cluster Narrative Positions

| Position | Narrative Role | Timing |
|----------|---------------|--------|
| **establish** (head) | Orient, plant the hook, thesis | 80-140 words (32-56 sec) |
| **develop** (interstitial) | Deepen, reframe, or exemplify | 25-40 words (10-16 sec) |
| **tension** (interstitial) | Complicate, contrast, "yes but" | 25-40 words (10-16 sec) |
| **resolve** (interstitial) | Land the meaning, echo the head | 25-40 words (10-16 sec) |

`develop` carries a sub-type: `deepen` | `reframe` | `exemplify`

## Sequencing

```
19 (Schema) → 20a (Intelligence Design) → 20b (Intelligence Impl) → 21 (Gary Dispatch)
                                                                          ↓
                                                                    ┌─────┴─────┐
                                                                    22 (Storyboard) ‖ 23 (Pass 2 Narration)
                                                                    └─────┬─────┘
                                                                          ↓
                                                                    24 (Assembly & Regression)
```

MVP validation gate: After Epic 20b + Epic 21 Story 1 — human judgment on whether Irene's cluster brief produces a coherent Gary output. Go/no-go before investing in downstream epics.

Double-dispatch is disabled for clustered presentations in MVP scope.

---

## Epic 19: Cluster Schema & Manifest Foundation

**Purpose:** Establish the data model that every downstream epic depends on. Must be airtight and backward-compatible.

### Story 19.1: Segment Manifest Cluster Schema Extension

Add to segment manifest YAML schema:
- `cluster_id` (string, nullable — null = non-clustered slide)
- `cluster_role` enum: `head` | `interstitial`
- `cluster_position` enum: `establish` | `develop` | `tension` | `resolve`
- `develop_type` enum (optional, for develop position): `deepen` | `reframe` | `exemplify`
- `parent_slide_id` (string, nullable — set for interstitials, references head)
- `interstitial_type` enum: `reveal` | `emphasis-shift` | `bridge-text` | `simplification` | `pace-reset`
- `isolation_target` (string — what specific element is surfaced)
- `narrative_arc` (string — one-sentence emotional journey, set on head slide, inherited by cluster)
- `cluster_interstitial_count` (integer — recommended count for this cluster, 1-3)
- `double_dispatch_eligible` (boolean, default true — false for interstitials)

Backward compatibility: all cluster fields nullable/optional. Existing non-clustered runs work unchanged.

Schema version bump with migration notes.

### Story 19.2: Gary Dispatch Contract Extensions

Extend machine artifacts to carry cluster metadata:
- `gary-slide-content.json`: add `cluster_id`, `cluster_role`, `parent_slide_id` per slide entry
- `gary-fidelity-slides.json`: add `cluster_role` per slide; interstitials inherit fidelity class from head
- `gary-outbound-envelope.yaml`: add `clusters[]` section with per-cluster metadata
- `gary-diagram-cards.json`: interstitials do not carry diagram cards (carve-out)

### Story 19.3: Fidelity Gate Contract Updates

- **G2 (Slide Brief):** Exempt `cluster_role == interstitial` from G2-01 (LO traceability) and G2-03 (fidelity classification). Interstitials inherit their head's fidelity and LO coverage.
- **G3 (Generated Slides):** Replace `count(generated) == count(brief)` with cluster-aware counting: `count(heads) + sum(cluster_interstitial_counts) == count(generated)`.
- **G4 (Narration Script):** Add cluster-aware criteria (detailed in Epic 23).
- Update `state/config/fidelity-contracts/` YAML files.

### Story 19.4: Validator Hardening for Cluster-Aware Payloads

- **`validate-gary-dispatch-ready.py`:** Refactor `card_sequence` contiguity check (line ~499) to accept cluster-ordered sequences. Branch `double_dispatch` counter to skip `cluster_role == interstitial` entries when `double_dispatch_eligible == false`.
- **`validate-irene-pass2-handoff.py`:** Accept interstitial segment entries with `segment_type: interstitial`. Validate that interstitial segments carry `timing_role` and `cluster_id`.
- Regression tests: existing non-clustered payloads pass all validators unchanged.

---

## Epic 20a: Irene Cluster Intelligence — Design & Specification

**Purpose:** Define what makes a good cluster, what a brief must contain, and how Irene decides which topics warrant progressive disclosure. This is editorial/research work — the biggest conceptual lift.

### Story 20a.1: Cluster Decision Criteria

Define and document the criteria Irene uses to decide which slides become cluster heads:
- **Concept density:** Does the topic have enough substance for 2-3 beats of progressive disclosure?
- **Visual complexity:** Does the head slide's content benefit from visual decomposition?
- **Pedagogical weight:** Is this a core concept that warrants deeper dwell time?
- **Operator input:** Operator can pre-designate cluster candidates or set a target cluster count via `cluster_density` config (sparse | default | rich).

Output: documented decision framework in Irene's references.

### Story 20a.2: Interstitial Brief Specification Standard

Define the contract between Irene and Gary — the quality bar that makes or breaks coherence:

Each interstitial brief must specify:
- `interstitial_type` (one of the five types)
- `isolation_target` (what specific element/concept to surface — must reference actual content from head brief)
- `visual_register_constraint` (what to remove/suppress, not what to add)
- `content_scope` (1-2 sentences max of on-screen content)
- `narration_burden` (what % of meaning the visual carries vs. narration — target: visual 70%, narration 30%)
- `relationship_to_head` (zoom | isolate | simplify | reframe | rest)

Validation: a brief that says "continue the topic" fails. A brief that says "isolate the working memory box from the cognitive load diagram, suppress surrounding labels, enlarge to full-frame" passes.

### Story 20a.3: Cluster Narrative Arc Schema

Define the `narrative_arc` field per cluster:
- One-sentence statement of the emotional journey from establish to resolve
- Maps to Sophia's framework: orient → complicate → illuminate → resolve
- Per-cluster `master_behavioral_intent` that all segment behavioral_intents serve
- Cluster positions assigned with explicit develop sub-types (deepen | reframe | exemplify)

### Story 20a.4: Operator Cluster Density Controls

Define operator-facing controls for cluster planning:
- `cluster_density` config: sparse (1-2 clusters per presentation) | default (3-5) | rich (6+)
- Per-slide operator directive: "cluster this" or "no cluster" overrides
- Operator can set `cluster_interstitial_count` per cluster (1-3)
- Surface in operator directives (Prompt 2A) or as a run constant

### Story 20a.5: Retrofit Exemplar Library

Analyze existing production runs (C1-M1) to identify where clusters would have improved engagement:
- Identify 3-5 slides from existing runs that are strong cluster head candidates
- Write exemplar cluster briefs for each
- Use as training/reference for Irene's cluster intelligence
- Store in Irene's memory sidecar for pattern reuse

---

## Epic 20b: Irene Cluster Intelligence — Implementation

**Purpose:** Implement the cluster planning capability in Irene Pass 1, with quality validation.

### Story 20b.1: Irene Pass 1 Cluster Planning Implementation

Extend Irene Pass 1 to produce cluster-grouped backbone:
- Evaluate each planned slide against cluster decision criteria
- For cluster heads, generate interstitial briefs meeting the specification standard
- Assign cluster positions (establish/develop/tension/resolve)
- Set `narrative_arc` per cluster
- Set `cluster_interstitial_count` per cluster (1-3, based on content complexity — not a fixed default)
- Produce bridge plan: bridges fire at cluster boundaries (`cluster_boundary`), not by arbitrary interval count
- Within-cluster transitions: `bridge_type: none` by default; `bridge_type: pivot` allowed for `tension` position only

### Story 20b.2: Cluster Plan Quality Gate (G1.5)

New validation pass between Irene Pass 1 and Gary dispatch:
- Are briefs specific enough? (isolation_target references actual head content)
- Is narration_burden specified per interstitial? (target: visual 70%)
- Is the cluster arc coherent? (positions form a logical progression)
- Does cluster count respect `cluster_density` config?
- Does interstitial count per cluster match `cluster_interstitial_count`?
- Are develop sub-types assigned and non-redundant within a cluster?

Operator HIL: reviews cluster plan as a structural document before Gamma spend.

### Story 20b.3: Narration Script Parameters Extension for Clusters

Extend `narration-script-parameters.yaml`:
- `cluster_head_word_range: [80, 140]` (upper bound extended for complex heads per Sophia)
- `interstitial_word_range: [25, 40]` (lower bound raised from 20 per Sophia)
- `within_cluster_bridge_policy: none` (default; `pivot` allowed for tension position)
- `cluster_boundary_bridge_style: synthesis_plus_forward_pull`
- `cluster_bridge_cadence_override: true` (bridges fire at cluster seams, not by slide/time count)

---

## Epic 21: Gary Cluster Dispatch — Gamma Interpretation

**Purpose:** Translate Irene's cluster briefs into Gamma prompts that maximize visual coherence, and validate the output.

### Story 21.1: Visual Design Constraint Library

Define locked Gamma prompt parameters per interstitial type:
- `reveal`: inherit head palette + accent color, single element focus, max 2 visual elements
- `emphasis-shift`: inherit head accent color, isolate one text block, suppress others
- `bridge-text`: inherit head atmospheric background, single phrase in large type, no imagery
- `simplification`: inherit head palette, disable multi-column layout, one data series only
- `pace-reset`: minimal chrome, icon or whitespace only, head palette undertone

Each type has explicit constraints on what Gary CANNOT include in the prompt.

Store as a reference document in Gary's skill directory.

### Story 21.2: Cluster-Aware Prompt Engineering

Gary translates interstitial briefs into Gamma prompts:
- Head and interstitial prompts dispatched in same Gamma session using `card_split: inputTextBreaks` with `\n---\n` separators
- `num_cards` = head count + total interstitial count for the dispatched cluster batch
- Each interstitial prompt includes a reference descriptor pulled from the head brief (not reconstructed)
- Prompt templates per interstitial_type from the constraint library
- Interstitial prompts specify what to REMOVE/ISOLATE, not what to ADD
- Element count caps per type (2 max for reveal/emphasis, 1 for bridge-text, 0 for pace-reset)

### Story 21.3: Cluster Dispatch Sequencing

- Gary dispatches clusters as atomic units — all slides in a cluster in one Gamma session
- Head card is always position 1 in the session
- If a cluster fails generation, the entire cluster re-dispatches (not individual interstitials)
- Double-dispatch is disabled for interstitial cards (`double_dispatch_eligible: false`); head slides may still use double-dispatch if the run constant is enabled
- Dispatch contract carries cluster lineage metadata

### Story 21.4: Cluster Coherence Validation (G2.5)

Post-dispatch, pre-Storyboard-A automated coherence check:
- Perception pass on all cluster members
- Specific computable checks per cluster:
  - **Typography match:** same font family and weight hierarchy between head and interstitials
  - **Background treatment consistency:** full-bleed head → interstitials should not go flat-color (except pace-reset)
  - **Element isolation fidelity:** isolation_target appears at comparable scale
  - **Whitespace ratio delta:** interstitials should have >= head whitespace (inverted ratio = flag)
  - **Color temperature consistency:** no warm-to-cool shift within cluster
- Output: per-cluster coherence score (pass | warn | fail) with specific failure reasons
- Flag clusters where interstitials diverge; operator decides: accept, re-dispatch interstitial, or re-dispatch whole cluster

### Story 21.5: Interstitial Re-dispatch Protocol

When an interstitial fails coherence or operator review:
- Targeted re-dispatch of failed interstitial with tightened prompt (now informed by head slide perception data from the first pass)
- Partial re-run contract: only failed interstitial re-dispatches
- Circuit breaker: max 2 re-dispatch attempts per interstitial (consistent with existing literal-visual retry pattern)
- If circuit breaker fires, operator chooses: accept as-is, replace with pace-reset, or drop interstitial from cluster

---

## Epic 22: Storyboard & Review Adaptation

**Purpose:** Extend Storyboard A and B to render clusters as coherent review units.

### Story 22.1: Storyboard A Cluster View

Extend `generate-storyboard.py` for Storyboard A:
- Clusters render as collapsible groups: head slide prominent, interstitials indented beneath
- Cluster header row: topic label, cluster arc, interstitial count, interstitial types
- Collapsed view = pacing audit (cluster count, duration balance)
- Expanded view = per-slide QA with thumbnails
- Per-interstitial G2.5 coherence indicator (green/yellow/red border based on coherence score)
- Inter-cluster gap visually distinct from within-cluster spacing

### Story 22.2: Storyboard B Cluster View with Script Context

Extend Storyboard B:
- Same cluster grouping as A, now with narration script per segment
- Within-cluster transitions visually distinguished from cluster-boundary transitions
- Per-cluster timing summary (total cluster duration, per-segment breakdown)
- Behavioral intent shown at cluster level (master) and segment level
- Timing metadata: timing_role, content_density, cluster_position per segment
- Voice-direction defaults and runtime-plan metadata in header (existing behavior, cluster-extended)

### Story 22.3: Flat-Play Sequential Preview Mode

Add a "view as student" flat-play mode to Storyboard B:
- Linear slide sequence with narration text shown in playback order
- No cluster grouping — pure student-perspective flow
- Visual transition indicators: subtle divider for within-cluster, prominent divider for cluster-boundary
- Allows operator to experience the pacing before assembly
- Accessible from Storyboard B HTML via toggle control

### Story 22.4: Storyboard Generation Script & Publish Updates

- `generate-storyboard.py` reads `cluster_id` from manifest, groups accordingly
- Publish-to-GitHub-Pages snapshot preserves cluster structure and flat-play mode
- Both Storyboard A and B publish routines updated

---

## Epic 23: Irene Pass 2 Cluster-Aware Narration

**Purpose:** Extend Irene Pass 2 to write narration that leverages the full clustered deck.

### Story 23.1: Cluster-Aware Dual-Channel Grounding

Irene perceives each slide (head and interstitial) and writes narration per segment:
- **Head segments (establish):** Fuller narration (80-140 words), establishes the topic, plants the hook
- **Interstitial segments (develop/tension/resolve):** Shorter narration (25-40 words, 10-16 sec), focused on the interstitial's isolation_target
- Narration for interstitials presumes the visual carries 70% of the meaning
- Within-cluster transitions: no spoken bridge (visual cut is sufficient). `bridge_type: none`
- Exception: `tension` position may use `bridge_type: pivot` with an explicit tonal shift word
- Cluster-boundary transitions: `bridge_type: cluster_boundary` — one sentence synthesis + one sentence forward pull (15-20 sec)
- Per-segment behavioral_intent must serve the cluster's `master_behavioral_intent`

### Story 23.2: G4 Gate Extension for Clusters

Extend G4 fidelity criteria:
- **G4-16 (Cluster narration coherence):** Do interstitial segments serve the cluster's master_behavioral_intent?
- **G4-17 (Interstitial word budget):** Are interstitial segments within the 25-40 word range? Are head segments within 80-140?
- **G4-18 (No new concepts in interstitials):** Interstitial narration must not introduce concepts absent from the head segment's source_ref scope
- **G4-19 (Cluster arc integrity):** Does the sequence establish → develop → tension → resolve form a coherent progression? Does resolve echo establish?
- Existing G4 criteria (G4-01 through G4-15) apply per-segment as before; cluster-role-aware where needed

### Story 23.3: Bridge Cadence Adaptation

Update bridge cadence logic in `narration-script-parameters.yaml`:
- `cluster_bridge_cadence_override: true` — when clusters are present, bridges fire at cluster seams rather than by arbitrary slide-count or time-interval
- `require_intro_or_outro_every_minutes` and `require_intro_or_outro_every_slides` still apply as upper bounds but cluster_boundary bridges satisfy them
- Spoken bridge enforcement (`spoken_bridge_policy`) applies to `cluster_boundary` bridge_type; within-cluster `none` is exempt from enforcement

---

## Epic 24: Assembly, Handoff & Regression Hardening

**Purpose:** Ensure the assembly bundle, Descript guide, and all downstream contracts handle clustered presentations gracefully.

### Story 24.1: Assembly Contract Hardening

- Segment manifest order is authoritative — assembly respects cluster sequence
- Slide-index-to-audio mapping handles interstitials (shorter audio segments)
- Assembly bundle preserves cluster structure: visuals sorted by cluster
- `sync-visuals` compositor handles interstitial PNGs identically to head PNGs

### Story 24.2: Descript Assembly Guide Enhancement

- Label each slide with cluster membership and role: `[HEAD — Cluster 3: "Cognitive Load Theory"]`, `[INTERSTITIAL 2/3 — emphasis-shift: "working memory"]`
- Explicit within-cluster vs between-cluster transition annotations in the guide
- Within-cluster: cut (no transition effect)
- Between-cluster: beat/pause (brief black or fade)
- Audio treatment note per interstitial: VO segment, not silence
- Preserve `behavioral_intent` and `bridge_type` context in guide

### Story 24.3: ElevenLabs Short Segment Handling

- Validate that ElevenLabs handles 10-16 second audio segments without degradation
- Audio buffer policy: within-cluster segments use reduced buffer (0.5s lead-in + 0.5s tail vs standard 1.5s) to maintain flow
- Between-cluster segments retain standard buffer
- Update `elevenlabs_operations.py` to accept per-segment buffer overrides keyed to `cluster_role`

### Story 24.4: Regression Test Suite

- Non-clustered presentations pass all validators unchanged (backward compatibility)
- Existing production run (C1-M1) can be re-run without clusters as baseline
- Cluster-enabled run produces valid assembly bundle end-to-end
- Validator regression tests: `validate-gary-dispatch-ready.py` accepts both flat and clustered payloads
- `validate-irene-pass2-handoff.py` accepts interstitial segment entries
- G2, G3, G4 gate contracts handle cluster carve-outs correctly
- Double-dispatch + non-clustered still works (double-dispatch disabled for interstitials only)

---

## Summary

| Epic | Stories | Difficulty | Key Risk |
|------|---------|------------|----------|
| **19: Schema Foundation** | 4 | Medium | Must be airtight — everything depends on it |
| **20a: Intelligence Design** | 5 | High (editorial) | Open-ended research; brief quality determines everything |
| **20b: Intelligence Impl** | 3 | High (engineering) | Irene must produce briefs that Gamma can execute |
| **21: Gary Dispatch** | 5 | High | Gamma's probabilistic output vs. coherence requirements |
| **22: Storyboard** | 4 | Medium | Flat-play mode is essential, not optional |
| **23: Pass 2 Narration** | 3 | Medium | Irene already writes well; cluster awareness is additive |
| **24: Assembly & Regression** | 4 | Medium | Validator hardening is highest regression risk |

**Total: 7 epics, 28 stories** (Epics 19-24 defined here)

**MVP validation gate:** PASSED (Storyboard A trial, 2026-04-11). All downstream unblocked.

**Parallel execution window:** Epics 22 and 23 run simultaneously after Epic 21.

---

## Epic 20c: Cluster Intelligence + Creative Control (Iterative)

Added 2026-04-12, replanned 2026-04-14 (Party Mode consensus).

### Scope

Iterative epic combining cluster intelligence maturity (Wave 2A) with parameter registry, Creative Director agent, experience profiles, and profile resolver (Wave 2B). A/B trials SKIPPED — replaced by experience-profile-driven trial runs. Clustering and creative control mature together through profile-driven runs against C1-M1.

### SPOC Invariant: Marcus as Single Point of Contact

**Architectural invariant:** An HIL operator completes an entire production run by chatting exclusively with Marcus. No direct specialist invocation, no manual YAML editing, no parameter configuration outside Marcus conversations.

This invariant applies to all stories in Epic 20c. During development, a story may deliberately leave SPOC unenforced for a bounded interval when a prerequisite or complementary feature has not yet shipped. Such gaps must be:

1. **Documented in the opening story** — the story that creates the gap states what is unenforced and which story closes it.
2. **Documented in the closing story** — the story that closes the gap has an explicit acceptance criterion for SPOC enforcement.
3. **Bounded** — no gap spans more than two stories in the critical path.

**SPOC gap ledger (Epic 20c):**

| Gap | Opened by | Closed by | Description |
|-----|-----------|-----------|-------------|
| Profile selection not in prompt packs | 20c-12 | 20c-14 | CLOSED 2026-04-14 - Marcus prompt pack + conversation flow now surface the plain-language choice and persist the mapped profile id |
| CD has no Marcus-only intake contract | 20c-10 | 20c-14 | CLOSED 2026-04-14 - CD SKILL.md now declares Marcus-only invocation and structured return path |
| Resolver exists but prompt packs don't trigger it | 20c-13 | 20c-14 | CLOSED 2026-04-14 - Marcus intake now drives the resolver and copied C1-M1 proof bundles validate the runtime path |

### Wave 2A — Cluster Maturity

Bring clustering to "good enough for profile runs" state.

#### Story 20c-1: Cluster Structure Template Library
- **Status:** In-progress (Slice 1 done: 10 templates)
- Template library for cluster structures (head + interstitial patterns)
- AC: At least 10 templates covering all 5 interstitial types

#### Story 20c-2: Content-Aware Template Selection Logic
- **Status:** Done
- Selector, bridge, hydration, fail-closed, evaluator (5 slices)

#### Story 20c-3: Static Density Configs
- **Status:** Ready-for-dev
- COMPRESSED: Two hardcoded density configs (visual-led, text-led), not full engine
- AC: Density configs align with experience profile proportions

#### Story 20c-4: Master Arc Cluster Arc Composition — DEFERRED
#### Story 20c-5: Presentation Architect Agent (Pax) — DEFERRED
#### Story 20c-6: Cluster Design Advisor Capability (Lens) — DEFERRED

Deferred until profile-driven runs (20c-14) reveal specific gaps.

### Wave 2B — Parameter Registry + Creative Director

Build the parameter infrastructure and CD agent that unlocks creative control. Three parameter families: Run Constants (operational), Narration-time (Irene script controls), Assembly-time (Compositor timing).

#### Story 20c-7: Parameter Audit & Registry Schema
- **Status:** Done
- Cataloged 3 parameter families, added `docs/parameter-directory.md`, added `state/config/parameter-registry-schema.yaml`
- AC: Registry schema validates; parameter directory covers all implemented parameters
- **SPOC:** No gap — parameters are system-defined, not operator-configured

#### Story 20c-8: Assembly Timing Parameters
- **Status:** Done
- onset_delay, dwell, cluster_gap, transition_buffer wired into manifest reference, Pass 2 and precomposition validators
- AC: Assembly timing parameters validated in handoff and precomposition paths
- **SPOC:** No gap — assembly params flow through Irene manifest, not operator config

#### Story 20c-9: Narration Parameter Expansion
- **Status:** In-progress
- Expanded narration_profile_controls set (11 controls) aligned across config, registry, and schema validation
- AC: All narration profile controls have enum validation in narration-script-parameters.yaml
- **SPOC:** No gap — narration params are system defaults consumed by Irene through delegation

#### Story 20c-10: Creative Director Agent
- **Status:** In-progress
- Contract-first CD scaffold with `slide_mode_proportions` validation path
- AC: CD SKILL.md exists with output contract, guardrails, and references; creative directive validator enforces schema compliance
- **SPOC:** Gap OPENED — CD scaffold exists but has no structural "Marcus-only intake" contract. Currently enforced by prose only ("CD output is advisory input"). **Closed by 20c-14** (intake contract formalized + E2E validation proves Marcus-mediated flow)

#### Story 20c-11: Creative Directive Schema
- **Status:** In-progress
- Schema artifacts (JSON + YAML) for creative directive validation
- AC: Schema defines required fields (schema_version, experience_profile, slide_mode_proportions, narration_profile_controls, creative_rationale); validator rejects non-conforming directives
- **SPOC:** No gap — schema is a validation contract, not an operator-facing surface

#### Story 20c-12: Experience Profile Definitions
- **Status:** In-progress
- Bootstrap profile targets (visual-led, text-led) with schema validation tests
- AC: Two profiles in `experience-profiles.yaml` with validated `slide_mode_proportions` (sum to 1.0) and `narration_profile_controls` (required keys present); creative directive validator enforces profile parity
- **SPOC:** Gap OPENED — profiles defined but not surfaced through Marcus's conversational flow. Operator cannot select a profile through Marcus yet. **Closed by 20c-14** (prompt pack update + Marcus reference update)

#### Story 20c-13: Profile Resolver Wiring
- **Status:** Done
- Resolve selected `experience_profile` to canonical `slide_mode_proportions` and `narration_profile_controls`. Propagate resolved `slide_mode_proportions` into `RunConstants`. Return `narration_profile_controls` for Marcus to pack into delegation envelope.
- **Dependencies:** 20c-12 (profiles defined), 20c-3 (density configs, soft)
- **Implementation constraints (Party Mode consensus 2026-04-14):**
  1. Resolver is a pure function in `run_constants.py` — not a CLI, not a service
  2. Resolver output merges into the raw dict BEFORE `parse_run_constants()` — frozen dataclass cannot be mutated after construction
  3. `experience_profile` added as `Optional[str] = None` on `RunConstants` for traceability and backwards compatibility
  4. `narration_profile_controls` do NOT land on `RunConstants` (wrong parameter family) — Marcus packs them into the delegation envelope for Irene
  5. Unknown profile rejection raises `RunConstantsError` at resolve time with "unknown experience profile" error message (error locality)
  6. Resolver reads `experience-profiles.yaml` as sole source of truth — no hardcoded values
  7. Irene must never import or reference `experience-profiles.yaml` directly — controls arrive only via envelope
- **Acceptance criteria:**
  1. `resolve_experience_profile(name)` returns `slide_mode_proportions` + `narration_profile_controls` for known profiles
  2. Unknown profile name raises `RunConstantsError`
  3. Resolved `slide_mode_proportions` round-trips through `parse_run_constants()` without mutation
  4. `experience_profile` field on `RunConstants`: absent defaults to `None` (backwards compat), present validates against known profiles
  5. Contract test: every profile name in `experience-profiles.yaml` is accepted by `parse_run_constants()`
  6. Static analysis test: no downstream agent directory contains direct references to `experience-profiles.yaml`
  7. Integration test: profile name -> resolver -> merge into raw dict -> `parse_run_constants()` -> success
  8. All existing tests remain green (229+ baseline)
- **SPOC:** Gap OPENED — resolver exists but no prompt pack triggers it. Marcus can pass `experience_profile` in run-constants but isn't conversationally prompted to do so. **Closed by 20c-14.**

#### Story 20c-14: E2E Validation (C1-M1, Both Profiles)
- **Status:** Done
- **Dependencies:** 20c-13 (resolver wired)
- Run C1-M1 through both profiles (visual-led, text-led) with comparison. This is the integration proof and the SPOC gap closure story.

#### Story 20c-15: Parent Slide Count — Profile-Aware Estimator
- **Status:** Done
- **Dependencies:** 20c-14 (E2E validation complete, profiles proven)
- Rename `locked_slide_count` → `parent_slide_count`. Operator polls for only `parent_slide_count` and `target_total_runtime_minutes`. All other parameters (`estimated_total_slides`, `avg_slide_seconds`, word budgets) are system-derived from the experience profile's `cluster_expansion` block. Estimator runs a 5-condition feasibility triangle (PASS/WARN/BLOCK). Operator polling loops on BLOCK, surfaces WARN for ACK.
- **Story file:** `_bmad-output/implementation-artifacts/20c-15-parent-slide-count-profile-aware-estimator.md`
- **Key changes:**
  1. `experience-profiles.yaml` schema 1.0→1.1, `cluster_expansion` blocks added
  2. `slide_count_runtime_estimator.py` rewritten with `estimate_and_validate()`
  3. `operator_polling.py` simplified to 2-input poll with feasibility loop
  4. Prompt 4.5 rewritten for profile-aware workflow
  5. G1.5 gate: 3 new criteria (expansion compliance, cluster balance, runtime fit)
  6. G4 gate: G4-10 and G4-17 updated for profile-derived values
  7. Field rename propagation across 8+ downstream files
- **Acceptance criteria:**
  1. Prompt pack updated with plain-language profile selection step during run-constants handshake (operator never sees "experience profile" terminology — Marcus asks "should the visuals lead or the text?")
  2. Marcus conversation-management reference updated to elicit, map, and confirm profile choice
  3. CD agent SKILL.md gains `## Intake Contract` section (modeled on Vera pattern): invoked exclusively through Marcus's envelope, receives all context from envelope, returns structured output to Marcus
  4. C1-M1 visual-led run produces resolved run-constants with correct proportions
  5. C1-M1 text-led run produces resolved run-constants with correct proportions
  6. Narration profile controls arrive in Irene's delegation envelope (not from direct file read)
  7. Storyboard HTML remains view-only with no operator-facing controls (design principle, not just implementation detail)
  8. All SPOC gaps from 20c-10, 20c-12, and 20c-13 are closed
  9. SPOC gap ledger in this epic definition is updated to mark all gaps as closed
- **SPOC:** All gaps CLOSED. After this story, the full profile -> CD -> resolver -> run-constants -> Marcus -> envelope -> Irene flow is tested end-to-end at the Marcus contract level with the operator interacting exclusively through Marcus. Proof artifacts were captured under `reports/proofs/20c-14/`.

### Critical Path

```
20c-7 -> 20c-8/9 (parallel) -> 20c-10 -> 20c-12 -> 20c-13 -> 20c-14
                                  |
                                  v
                               20c-11
```

### Risk Summary

| Risk | Severity | Mitigation |
|------|----------|------------|
| Resolver bypasses `parse_run_constants()` | Critical | Constraint #2: merge before parse, not after |
| Three-way coupling (profile YAML, validator, resolver) | High | Single source of truth: profile YAML, everything derives at runtime |
| Irene reads profiles directly | Critical | Constraint #7 + static analysis test |
| CD accumulates operator-facing surface | High | Intake contract (20c-14 AC #3) |
| Prompt pack never updated | Medium | 20c-14 AC #1 makes it explicit |
| Profile scaling beyond 4-5 choices | Low | Marcus shifts from "pick one" to "tell me what you want" (future story if needed) |
