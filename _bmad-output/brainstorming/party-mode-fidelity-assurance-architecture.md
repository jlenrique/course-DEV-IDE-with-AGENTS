# Executive Summary: Fidelity Assurance Architecture for the Agentic Production Platform

**Date:** 2026-03-28
**Participants:** Party Mode consultation — Marcus (Orchestrator), Gary (Gamma Specialist), Irene (Content Creator), Quinn-R (Quality Reviewer), Winston (Architect), Amelia (Developer), Victor (Innovation Strategist), Dr. Quinn (Problem Solver), Carson (Brainstorming Specialist)
**Cross-team synthesis:** Incorporates findings from a parallel independent analysis (Gemini Strategic Planning Team, same date)
**Status:** Synthesized consensus — ready for external review and feedback

---

## 1. What We Explored

Two interrelated consultations were conducted:

1. **Strategic framing:** What is the nature of a system in which an IDE is integral to an agentic framework that 10X-es content production — in volume, quality, and consistency — and what design principles should govern the balance between agentic intelligence and deterministic assurance?

2. **Practical gap analysis:** How do we ensure fidelity assessment at every step of our multi-agent production pipeline, grounded in a step-appropriate source of truth, and what must we build to close the gaps?

The connection between these two tracks is the core insight of the session: **the system's competitive advantage comes from embedding intelligence into the production pipeline — but intelligence without fidelity assurance is a liability, especially in higher education and medical education contexts where content must be exactly right.**

A parallel independent team explored the same problem space and arrived at strikingly convergent conclusions through a different analytical lens. This document synthesizes the strongest elements of both analyses into a unified plan.

---

## 2. The Agentic Production Platform (APP)

### Definition

An **Agentic Production Platform (APP)** is a system in which:

- The **IDE is the runtime environment** for a network of specialized agents — the agents don't exist outside it. The IDE *is* the platform, not a separate application accessed through the IDE.
- Agents bring **reasoning and judgment** into every production step — not just static, deterministic execution of code
- The platform **gets smarter over time** as agent capabilities improve with advancing LLM technology and as agent memory accumulates production experience
- Critical functions are executed by **custom agents with attendant skills, resources, and memory** — the intelligence is embedded in the pipeline, not applied after the fact

### What distinguishes an APP from conventional automation

Traditional content production tools are deterministic: push a button, get output. An APP has agents that *reason about* the production at every step. The system doesn't just *produce* content — it *understands* whether its own output is faithful, high-quality, and pedagogically sound. That understanding improves autonomously as the underlying models and the agents' accumulated experience improve.

The intelligence-fidelity architecture described in this document is itself a competitive differentiator: **anyone can bolt an LLM onto a content pipeline; architecturally separating the fidelity contract from the fidelity evaluator — so the evaluator improves without relaxing the contract — is a structural moat.**

### The 10X claim

The APP targets 10X improvement across all three dimensions simultaneously:

- **Volume:** More lessons produced per unit time through agent-coordinated multi-tool pipelines
- **Quality:** Each lesson is dramatically better than solo human production through specialist agent expertise, multi-pass review, and accumulated pattern memory
- **Consistency:** The 50th lesson is as good as the 1st because quality and fidelity standards are embedded in the agents, not dependent on human attention span

---

## 3. APP Design Principles

The session — and its cross-team synthesis — produced two complementary design principles that together govern the architecture of any APP capability.

### Principle 1: The Three-Layer Intelligence Model

Governs the **internal architecture** of any single assessment or production capability — how contracts, evaluation, and memory interact within each agent or gate.

#### Layer 1: Deterministic Contracts (what must be true)

- Per-gate criteria definitions: what fields to check, what sources to compare against, what constitutes pass/fail
- Defined in YAML or reference documents — versioned, human-reviewed, non-agentic
- Example: "All items in `slide_brief.content_items[]` must appear verbatim in generated slide text for `literal-text` slides"
- **These are the guardrails. They do not change when the LLM improves.**

#### Layer 2: Agentic Evaluation (how we verify it's true)

- The agent's judgment layer that *interprets* contracts against actual artifacts
- Today: keyword matching, item counting, structural comparison
- Tomorrow: semantic equivalence analysis, cognitive function preservation assessment, pedagogical intent verification
- **This layer improves without changing the contracts — same criteria, smarter detection**

#### Layer 3: Learning Memory (how intelligence improves over time)

- Patterns captured in BMad memory sidecars: what works, what fails, what the user corrects
- Accumulated assessment outcomes that refine future evaluation
- User preference calibration that aligns automated judgment with human expectations
- **This is the compound interest of the APP — every production run makes the next one better**

#### Critical insight

The fidelity *requirement* is the invariant — it never relaxes. The fidelity *assessment mechanism* is agentic — it evolves. The *methods* of assessing fidelity become more sophisticated as LLM capabilities advance (e.g., from string-matching to semantic equivalence to cognitive function analysis), but the *standards* remain fixed. This separation is the architectural key to a system that gets smarter without getting less reliable.

### Principle 2: The Hourglass Model

*(Contributed by the parallel Gemini analysis; adopted as complementary framework.)*

Governs the **flow topology** of the production pipeline — where in the pipeline intelligence should be applied vs. constrained.

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

**Key rule:** Intelligence must not be used to enforce constraints that can be handled by deterministic code. When intelligence *is* used for enforcement, that is a design defect — a "leaky neck."

### The "Leaky Neck" Diagnostic

*(Contributed by the parallel Gemini analysis; adopted as a testable diagnostic.)*

A **leaky neck** is any point in the pipeline where agentic judgment is used to enforce a constraint that could instead be handled by a schema validation, parameter mapping, or code check.

**Example of a leaky neck (pre-Story 3.11):** Telling Gamma via natural-language `additionalInstructions` to "not change this text" — using intelligence to enforce a deterministic constraint. Gamma's `generate` mode structurally rewrites content regardless of instructions.

**Example of plugging the leak (Story 3.11):** Mapping fidelity tags directly to API parameters — `fidelity: literal-text` → `textMode: preserve`. The constraint is now in the schema and parameter binding, not in the LLM's compliance with a natural-language instruction.

**The Leaky Neck diagnostic is repeatable:** At any point in the pipeline, ask: "Are we using an agent's judgment to enforce something that could be a schema rule, a parameter value, or a validation script?" If yes, plug the leak.

### How the two principles interact

The Hourglass Model tells you **where** determinism belongs in the pipeline flow. The Three-Layer Model tells you **how** to build the assessment capability at each point. Together, they form the complete APP design framework:

- The Hourglass identifies the *neck* — where deterministic contracts should live
- The Three-Layer Model defines what a contract *is* (L1), how it's *evaluated* (L2), and how evaluation *improves* (L3)
- The Leaky Neck diagnostic identifies violations — where intelligence is misused for enforcement

---

## 4. Audit Findings: Current APP Fidelity Maturity

The team conducted a systematic audit of every production gate against the four pillars of APP design.

### Audit Matrix

| Gate | Artifact | L1 Contracts | L2 Evaluation | L3 Memory | Perception |
|------|----------|:---:|:---:|:---:|:---:|
| **G0** Source Bundle | extracted.md from SME materials | WEAK | ABSENT | ABSENT | PARTIAL |
| **G1** Lesson Plan | LOs + content structure | PARTIAL | ABSENT | PARTIAL | OK |
| **G2** Slide Brief | Per-slide specs + fidelity tags | PARTIAL | ABSENT | PARTIAL | OK |
| **G3** Generated Slides | Gamma PNGs + metadata | PARTIAL | SELF-GRADED | GOOD (params) | PARTIAL |
| **G4** Narration Script | Script + segment manifest | WEAK | ABSENT | PARTIAL | **GAP** |
| **G5** Audio | ElevenLabs MP3/WAV | — | ABSENT | — | **BLIND** |
| **G6** Composed Video | Descript export | — | ABSENT | — | **BLIND** |

### Key findings

1. **Zero independent fidelity evaluation exists at any gate.** Every agent either self-grades (Gary at G3) or doesn't grade at all. The only fidelity check is the human at each HIL gate.
2. **Perception is unconfirmed everywhere.** No agent is required to confirm it successfully interpreted an artifact before proceeding. Slides are not visually verified. Audio cannot be heard at all.
3. **Audio and video are perception-blind.** The agents literally cannot interpret these modalities without a transcription/extraction intermediary, and no such intermediary exists in the pipeline.
4. **Cumulative drift is undetected.** Each gate checks (if at all) against its immediate input, not against the original source material. A 5% drift at each of 6 gates compounds to ~26% drift from SME intent — and no single gate flags a failure.
5. **Memory captures parameter tuning but not fidelity outcomes.** Agents learn "which Gamma settings work" but not "which types of content tend to drift at which gates."
6. **Leaky necks exist at G3.** Prior to Story 3.11, fidelity enforcement at the Gamma generation step relied on natural-language instructions rather than deterministic parameter binding — a textbook leaky neck.
7. **No provenance traceability.** Artifact schemas do not carry `source_reference` citations. The Fidelity Assessor (or any reviewer) cannot trace a learning objective back to its origin in the source bundle without re-reading and searching the entire upstream artifact.
8. **Story 3.11 (Mixed-Fidelity Gamma Generation) partially addresses G2-G3** by introducing fidelity classification (`creative`/`literal-text`/`literal-visual`) and provenance tracking, but it was designed before this analysis and does not include independent evaluation, perception confirmation, or source reference traceability.

### Maturity assessment

**The current APP is at Level 0 for fidelity assurance.** It has quality assurance (Quinn-R), process assurance (Marcus), but no systematic fidelity assurance. The system operates on trust — each agent trusts the previous agent's output. This is not sustainable for higher education content where accreditation, assessment alignment, and clinical accuracy are non-negotiable.

---

## 5. The Fidelity Assessor Agent

### Role definition

A new specialist agent — the **Fidelity Assessor** — owns source-material-to-output traceability across the entire production pipeline. Its mandate is strictly **forensic**: it answers **"Is this output faithful to its source of truth?"**

This is distinct from Quinn-R's role, which answers: **"Is this output good against our quality standards?"** The Fidelity Assessor determines whether the content is *right*; Quinn-R determines whether the content is *good*. The Fidelity Assessor runs first — fidelity is a precondition for quality. If the output isn't faithful, quality review is premature.

### Key design characteristics

- **Operates at every gate** with gate-specific criteria and gate-specific sources of truth
- **Runs before Quinn-R** at each gate — fidelity is a precondition for quality
- **Uses the three-layer model:**
  - L1: Gate-specific fidelity contracts in YAML (deterministic, versioned)
  - L2: Agentic evaluation that interprets contracts against artifacts (evolves with LLM capability)
  - L3: Memory sidecar capturing fidelity patterns, drift tendencies, user corrections
- **Perception-first protocol:** Never evaluates an artifact it can't interpret. Must confirm interpretation with confidence level before proceeding. Escalates to human when confidence is low.
- **Tracks both local and global fidelity:**
  - Local: Is this gate's output faithful to this gate's input?
  - Global: Is this gate's output still faithful to G0 (original SME source material)?
- **Cumulative drift metric:** Monitors compounding fidelity loss across the pipeline and alerts when global drift exceeds threshold
- **Acts as a circuit breaker:** A fidelity failure halts the pipeline at that gate, routing the artifact back to the producing agent for correction before it reaches the human checkpoint. This prevents wasted human review effort on unfaithful artifacts.

### Fidelity Trace Report: Standard Output Format

*(The Omissions/Inventions/Alterations taxonomy was contributed by the parallel Gemini analysis; adopted as the Fidelity Assessor's standard finding format.)*

Every fidelity assessment produces a **Fidelity Trace Report** with findings categorized into three types:

| Finding Type | Definition | Example |
|-------------|-----------|---------|
| **Omission** | Source content missing from output | "KC topics 4, 7, and 9 from the source bundle's knowledge check list do not appear in the generated slide" |
| **Invention** | Output content not traceable to any source | "Slide 5 includes a 'Clinical Pearl' callout box with content not present in the source bundle or lesson plan" |
| **Alteration** | Source content present but meaning changed | "Source states 'contraindicated in patients with renal impairment'; slide states 'use with caution in patients with renal impairment' — clinical implication changed" |

Each finding includes: gate, artifact location (slide number, line range, timestamp), severity (critical/high/medium), the source reference, the output reference, and a suggested remediation.

### Fidelity assessment by fidelity class

The Fidelity Assessor adapts its criteria based on the fidelity classification established in Story 3.11:

| Fidelity Class | L1 Contract | L2 Evaluation (today) | L2 Evaluation (future) |
|----------------|------------|----------------------|----------------------|
| `literal-text` | All source items must appear verbatim in output | Exact string matching, item counting | Semantic equivalence with clinical precision awareness |
| `literal-visual` | SME-provided image must be faithfully placed; surrounding text verbatim | Image presence verification + text matching | Layout analysis, visual hierarchy assessment |
| `creative` | All source themes must be *covered* even if creatively enhanced | Keyword/concept coverage scoring | Cognitive function preservation analysis — does creative reframing change what the learner takes away? |

**Critical distinction from the parallel analysis:** The Gemini team characterized `creative` slides as "loose" — essentially exempt from fidelity assessment. We disagree. Creative enhancement is not a license to drop content. `creative` slides need **coverage-based fidelity contracts** (all themes represented) rather than **verbatim contracts** (exact words preserved). A creative slide that drops a learning objective is an Omission, regardless of how beautifully it presents the remaining content.

### Gate-specific sources of truth

| Gate | Source of Truth for Fidelity Assessment |
|------|----------------------------------------|
| G0 | Original SME materials (Notion pages, PDFs, Box files) |
| G1 | Source bundle (extracted.md) + SME learning intent |
| G2 | Lesson plan (LOs, content structure) |
| G3 | Slide brief (content items, fidelity tags, visual specs) |
| G4 | Lesson plan + actual generated slides (PNGs — perceived via sensory bridge) |
| G5 | Narration script (exact text, pronunciation guides — audio perceived via STT bridge) |
| G6 | Segment manifest (assembly order, timing, sync points) |

---

## 6. The Provenance Protocol

*(Contributed by the parallel Gemini analysis; adopted as a structural requirement.)*

### Problem

Currently, artifact schemas do not carry source references. When a learning objective appears in a lesson plan, there is no structured link back to the section of the source bundle it derives from. When a slide brief specifies content items, there is no link back to the lesson plan section they implement. The Fidelity Assessor — or any reviewer — must re-read and search entire upstream artifacts to establish traceability. This is expensive, error-prone, and does not scale.

### Solution: Mandatory `source_ref` fields

Every artifact schema field that carries pedagogical content must also carry a `source_ref` pointing to its origin:

```yaml
# In lesson plan
learning_objectives:
  - id: LO-1
    text: "Identify three macro trends reshaping healthcare delivery"
    bloom_level: Remember
    source_ref: "extracted.md#Chapter 1 > Macro Trends Overview"

# In slide brief
slides:
  - number: 3
    title: "The Three Macro Trends"
    content_items:
      - text: "Digital transformation of care delivery"
        source_ref: "lesson-plan.md#LO-1"
    fidelity: creative
```

This creates a **traceable provenance chain** from any downstream artifact back to the original SME material. The Fidelity Assessor can follow `source_ref` links to perform precise, targeted comparisons rather than full-document search.

### Schema updates required

| Schema | File | Change |
|--------|------|--------|
| Lesson plan template | `skills/bmad-agent-content-creator/references/template-lesson-plan.md` | Add `source_ref` to LOs and content blocks |
| Slide brief template | `skills/bmad-agent-content-creator/references/template-slide-brief.md` | Add `source_ref` to content items |
| Context envelope (Gary) | `skills/bmad-agent-gamma/references/context-envelope-schema.md` | Pass `source_ref` through for provenance |
| Narration script template | (to be created) | Add `source_ref` to narration segments |
| Segment manifest | (existing, extend) | Add `source_ref` to segment definitions |

---

## 7. The Sensory Horizon: Bridges to Multimodal Perception

*(The "Sensory Horizon" and "Sensory Bridges" terminology was contributed by the parallel Gemini analysis. The universal perception protocol — mandatory confirmation with confidence scoring — is from the primary analysis. Both are adopted.)*

### The Sensory Horizon Principle

**An agent cannot verify the fidelity of an artifact it cannot perceive.** The platform must provide infrastructural sensory bridges that convert non-text modalities into agent-interpretable representations. Without these bridges, agents are blind or deaf to actual outputs, rendering true fidelity assurance impossible.

### Sensory Bridge Specifications

| Modality | Bridge Script | Input | Output | Infrastructure |
|----------|--------------|-------|--------|----------------|
| **Image** | `png_to_agent.py` | PNG/JPG slide images | Structured description + OCR text extraction + layout analysis | LLM vision (native Claude capability) |
| **Audio** | `audio_to_agent.py` | MP3/WAV narration files | Timestamped transcript + WPM measurement + pronunciation log | ElevenLabs STT or local Whisper |
| **Video** | `video_to_agent.py` | MP4/WebM video files | Keyframe PNGs (at scene changes) + audio transcript | ffmpeg frame extraction + STT |
| **PDF** | `pdf_to_agent.py` | PDF exports/source docs | Text content + embedded image extraction as PNGs | pdfplumber or pymupdf |

### Universal Perception Protocol

Every agent consuming a multimodal artifact must follow this five-step protocol:

1. **Receive** — artifact file path delivered in context envelope
2. **Perceive** — invoke the modality-appropriate sensory bridge
3. **Confirm** — state what was perceived in structured format with confidence level:
   - `HIGH`: "I can see Slide 3 shows a two-column comparison of Treatment A vs Treatment B with 4 rows each."
   - `MEDIUM`: "I can see Slide 7 contains a diagram with labeled elements, but I cannot confidently read all labels."
   - `LOW`: "I cannot interpret this artifact — the image is too complex / the audio is unclear."
4. **Proceed** — only if confidence meets the gate-specific threshold
5. **Escalate** — if confidence is low, flag for human interpretation rather than guessing

This protocol applies to the Fidelity Assessor, Quinn-R, Irene (Pass 2 slide interpretation for narration writing), Gary (self-assessment of generated output), and any future agent that consumes non-text artifacts.

### Why confirmation is non-negotiable

The parallel Gemini analysis identified the need for sensory bridges but did not require agents to confirm successful interpretation. This is a critical gap: **a bridge that the agent crosses without confirming arrival is no assurance at all.** An agent could receive a PNG, misinterpret it due to visual complexity, and proceed to write narration or score fidelity against a wrong understanding. The confirmation step surfaces the agent's interpretation so the orchestrator — or the user — can catch perception errors before they propagate.

---

## 8. Recommended Stories (Prioritized)

### Priority 1 — Foundation (prerequisite for everything else)

**Story A: Sensory Bridges Skill**
Build a shared `sensory-bridges` skill with modality-specific interpreter scripts (`png_to_agent.py`, `audio_to_agent.py`, `pdf_to_agent.py`). Implement the universal perception protocol (receive → perceive → confirm → proceed/escalate) as a reusable skill reference that all consuming agents adopt. Initial modalities: image (LLM vision) and audio (STT via ElevenLabs or Whisper).

*Rationale:* Without sensory bridges, the Fidelity Assessor and all downstream improvements are perception-blind. This is the infrastructure layer that every other story depends on.

**Story B: Fidelity Assessor Agent — Foundation + Provenance Protocol**
Create the Fidelity Assessor agent via `bmad-agent-builder` with the three-layer architecture and the Fidelity Trace Report output format (Omissions/Inventions/Alterations). Initial gate coverage: G2 (slide brief vs. lesson plan) and G3 (generated slides vs. slide brief, using image sensory bridge). Initial L1 contracts for these two gates. L2 evaluation starts with structural comparison, keyword coverage, and item counting. Memory sidecar initialized. Runs before Quinn-R. Marcus updated to invoke Fidelity Assessor in delegation flow. Circuit breaker behavior: fidelity failure halts pipeline at gate.

Additionally, implement the **Provenance Protocol**: update `template-lesson-plan.md`, `template-slide-brief.md`, and `context-envelope-schema.md` to add mandatory `source_ref` fields. This gives the Fidelity Assessor traceable links rather than requiring full-document search.

*Rationale:* G2-G3 is the most acute pain point (Trial Run 2 failure) and the simplest source-of-truth chain (text → text → visual). Proves the pattern before extending to harder gates. The Provenance Protocol is bundled here because `source_ref` fields are the mechanism that makes fidelity assessment precise and scalable.

### Priority 2 — Pipeline extension

**Story C: Fidelity Assessor — G0 and G1 Coverage**
Extend Fidelity Assessor to validate source bundle completeness (G0: `extracted.md` vs. original SME materials) and lesson plan faithfulness (G1: LOs vs. source bundle themes). Define L1 contracts for content coverage at these gates. G0 assessment includes verifying that the source wrangler's extraction captured all relevant sections from SME materials.

*Rationale:* G0 is where the entire downstream fidelity chain inherits its baseline. If extraction is lossy, everything downstream is unfaithful by inheritance.

**Story D: Fidelity Assessor — G4 and G5 Coverage**
Extend to narration script fidelity (G4: script vs. lesson plan + actual slide PNGs via image sensory bridge) and audio fidelity (G5: spoken audio vs. narration script via audio sensory bridge/STT comparison). Audio bridge must produce timestamped transcript for precise WPM validation and word-level comparison.

*Rationale:* G4 is where Irene's narration must match actual slides — the perception gap identified in the audit. G5 is where audio must match script — currently perception-blind.

### Priority 3 — Intelligence optimization and APP maturity

**Story E: Cumulative Drift Tracking**
Implement global fidelity metric: at G3 and beyond, the Fidelity Assessor compares not just against the immediate input but against the original source material (G0). Uses `source_ref` chains from the Provenance Protocol. Drift threshold configurable per production mode (ad-hoc: relaxed, production: strict, regulated: zero-tolerance).

*Rationale:* Local gate-to-gate fidelity checks cannot detect compounding drift. A 5% loss per gate compounds silently. Global tracking is the only way to catch this.

**Story F: Existing Agent Perception Upgrades**
Update Irene (Pass 2), Gary (self-assessment), and Quinn-R (quality review) to adopt the universal perception protocol with sensory bridges. Irene receives and visually confirms slide PNGs before writing narration. Gary confirms his visual interpretation before returning results. Quinn-R confirms interpretation before scoring. All three agents state their perception in structured format before proceeding.

*Rationale:* The Fidelity Assessor is not the only agent that needs to perceive artifacts. Every agent that consumes multimodal output should confirm interpretation. This upgrades the entire pipeline's reliability.

**Story G: APP Maturity Audit Skill**
Build a repeatable `app-maturity-audit` skill that evaluates the current pipeline against the three-layer model + sensory horizon + Hourglass neck integrity. Produces an audit heat map (like Section 4 above) and a leaky neck report. Can be run after any architectural change to identify regression or new gaps.

*Rationale:* The audit in this session was manual. Making it a repeatable skill ensures the APP's design health is continuously monitored as the system evolves.

**Story H: Leaky Neck Remediation Pass**
Systematic review of all agent-to-tool interfaces for leaky necks — points where agentic judgment is used to enforce constraints that should be deterministic parameter bindings or schema validations. Plug identified leaks with schema rules, parameter mappings, or validation scripts.

*Rationale:* Story 3.11 plugs the most visible leak (Gamma `generate` mode for literal content). There may be others across the pipeline that the audit didn't surface because those gates haven't been exercised yet.

### Relationship to Story 3.11

Story 3.11 (Mixed-Fidelity Gamma Generation) is currently `ready-for-dev` and introduces fidelity classification and provenance tracking at G2-G3. It is a **partial foundation** that the Fidelity Assessor builds upon:

- 3.11 gives Irene the vocabulary to tag fidelity requirements (`creative`/`literal-text`/`literal-visual`) — L1 contract inputs
- 3.11 gives Gary the provenance manifest — L1 contract verification data
- 3.11 plugs the most critical leaky neck — `textMode: preserve` instead of natural-language enforcement
- The Fidelity Assessor (Story B) adds the missing **independent evaluation** that 3.11 does not include
- The Provenance Protocol (Story B) adds the **`source_ref` traceability** that 3.11 does not include

Recommendation: **Implement 3.11 as designed, then build Stories A and B on top of it.** Do not delay 3.11 — it unblocks Trial Run 2 and provides the schema the Fidelity Assessor will consume.

---

## 9. Risks and Open Questions

1. **Audio sensory bridge dependency.** Stories D and F require STT infrastructure. ElevenLabs provides STT capability; Whisper is an alternative for local processing. Neither is currently integrated into the pipeline. This is a hard prerequisite for audio fidelity assessment.

2. **Global fidelity is computationally expensive.** Comparing every gate's output against the original source material requires maintaining and re-reading the source bundle at every gate. For long courses with large source bundles, this may need optimization (e.g., indexed source chunks, embedding-based similarity, `source_ref` targeted lookups).

3. **Perception confidence calibration.** The universal perception protocol requires agents to report confidence levels, but we have no empirical baseline for what "high confidence" means for image interpretation of medical education slides. Early production runs should calibrate this.

4. **Fidelity contracts for creative slides.** The `creative` fidelity class intentionally allows Gamma to enhance content. What constitutes acceptable creative drift vs. unfaithful creative drift? This is a judgment call that may need user-specific calibration and will evolve as L2 evaluation capability improves.

5. **Provenance Protocol adoption cost.** Adding `source_ref` fields to all schemas requires updating every producing agent's workflow. Irene must learn to cite sources in structured format. This is a workflow change, not just a schema change.

6. **APP Maturity Audit model validation.** The four-pillar model (L1 contracts, L2 evaluation, L3 memory, perception) needs validation across more pipeline configurations. Are four pillars sufficient? Should there be sub-levels within each pillar?

7. **Interaction with accreditation requirements.** Medical education accreditation bodies (LCME, ACGME) may have specific traceability requirements for instructional content. The fidelity architecture — especially the Provenance Protocol and Fidelity Trace Reports — should be validated against these requirements before the `regulated` production mode is implemented.

8. **Video composition fidelity (G6).** The Descript composition step is a manual-tool pattern. Fidelity assessment at G6 requires either: (a) the user exports the composed video and the fidelity agent reviews it via video sensory bridge, or (b) the fidelity agent reviews the Descript Assembly Guide + individual assets pre-composition. Option (b) is more practical initially; option (a) is the eventual goal.

---

## 10. Cross-Team Synthesis: What Each Analysis Contributed

This section documents the provenance of ideas in this synthesized plan, ensuring credit and traceability.

### Adopted from the parallel Gemini analysis

| Contribution | How it enhanced our plan |
|-------------|------------------------|
| **Hourglass Model** (wide cognitive → narrow deterministic → wide cognitive) | Added as a complementary design principle governing pipeline flow topology — our Three-Layer Model governs assessment architecture; together they're the complete APP framework |
| **"Leaky Neck" diagnostic** | Adopted as a testable, repeatable diagnostic concept; added as audit finding #6 and as Story H |
| **Fidelity Trace Report: Omissions / Inventions / Alterations** | Adopted as the Fidelity Assessor's standard output format — cleaner and more actionable than our original unstructured findings |
| **Provenance Protocol with `source_ref` fields** | Adopted as a structural requirement in Story B — the traceability mechanism that makes fidelity assessment precise and scalable |
| **"Sensory Horizon" / "Sensory Bridges" terminology** | Adopted as the naming convention for our Perception Layer — more evocative and construction-oriented |
| **Specific bridge script names** (`png_to_agent.py`, `audio_to_agent.py`) | Adopted as concrete implementation targets in Story A |

### Retained from primary analysis (gaps in Gemini analysis)

| Contribution | Why it was essential |
|-------------|---------------------|
| **Layer 3: Learning Memory** | The Gemini analysis has no mechanism for the system to improve over time. Memory sidecars are essential for compound APP improvement. |
| **Perception confirmation protocol** (confidence-scored, escalation on low confidence) | Gemini builds bridges but doesn't require agents to confirm they crossed them. Unverified perception is no assurance. |
| **Creative slide fidelity assessment** | Gemini treats `creative` slides as "loose" (unassessed). Creative enhancement is not a license to drop content — coverage-based fidelity contracts are required. |
| **Cumulative drift metric** (local + global fidelity) | Gemini doesn't address compounding fidelity loss across gates. This is architecturally necessary for pipeline-length integrity. |
| **Gate-by-gate audit matrix** | Our granular four-pillar assessment is more actionable than a narrative gap description. |
| **Quinn-R / Fidelity Assessor interaction model** | Explicit ordering (fidelity first, quality second) and operational boundary definition. |
| **APP Maturity Audit as a repeatable skill** | Making the audit itself a platform capability, not a one-time exercise. |
| **Evolution path preservation** | Our L2 (agentic evaluation) explicitly allows assessment methods to evolve with LLM capability. A "rigid diff" architecture forecloses this evolution. |

---

## 11. Summary of Consensus

The synthesized plan reaches consensus on:

- **Naming:** The system is an **Agentic Production Platform (APP)** — the IDE is the platform, agents are the intelligence, the platform evolves as LLMs improve
- **Design principles:** Two complementary frameworks — the **Three-Layer Model** (contracts, evaluation, memory) governs assessment architecture; the **Hourglass Model** (cognitive → deterministic → cognitive) governs pipeline flow topology; the **Leaky Neck diagnostic** identifies violations
- **Audit result:** Current APP is at **Level 0 for fidelity assurance** — no independent evaluation, no perception confirmation, no provenance traceability, audio/video blind spots
- **New agent:** **Fidelity Assessor** — forensic, distinct from Quinn-R, operates at every gate, runs before quality review, produces Fidelity Trace Reports (Omissions/Inventions/Alterations), circuit breaker on failure
- **New protocol:** **Provenance Protocol** — mandatory `source_ref` fields in all artifact schemas enabling traceable provenance chains
- **New shared skill:** **Sensory Bridges** — modality-specific interpretation with mandatory perception confirmation protocol (confidence-scored, escalation-gated)
- **Story priority:** Sensory bridges + Fidelity Assessor foundation (G2-G3) first → pipeline extension (G0-G1, G4-G5) → intelligence optimization (drift tracking, maturity audit, leaky neck remediation)
- **Story 3.11 relationship:** Implement as designed — it provides the fidelity classification schema and the most critical leaky neck fix; the Fidelity Assessor builds on top

---

*This document is a synthesized Party Mode consultation record incorporating findings from two independent parallel analyses. It captures team consensus and recommendations for external review. It does not constitute approved stories or architectural decisions — those require standard BMAD workflow processing.*
