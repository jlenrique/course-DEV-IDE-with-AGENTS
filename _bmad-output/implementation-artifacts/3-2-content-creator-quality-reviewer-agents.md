# Story 3.2: Content Creator Agent & Quality Reviewer Agent

Status: done

## Story

As a user,
I want content creation and quality review specialist agents,
so that instructional content is pedagogically designed by a specialist who delegates writing to expert BMad agents, and all production outputs are systematically validated for quality.

## Acceptance Criteria

1. `skills/bmad-agent-content-creator/SKILL.md` exists with "Instructional Architect" persona whose core expertise is instructional design, not prose writing
2. The content creator delegates writing to BMad specialists: Paige (technical content), Sophia (narratives/dialogues/first-person), Caravaggio (slide narrative design)
3. The content creator provides each writer with learning objectives, Bloom's level, cognitive load constraints, and pedagogical intent
4. The content creator reviews delegated writing for pedagogical alignment before assembling final artifacts
5. The agent produces one sample of each output artifact type (lesson plan, narration script, dialogue script, slide brief, assessment brief, first-person explainer) on a designated topic
6. Sample artifacts are staged in `course-content/staging/` for human review
7. Output artifacts follow structured templates in `skills/bmad-agent-content-creator/references/`
8. `skills/bmad-agent-quality-reviewer/SKILL.md` exists with "Quality Guardian" persona and systematic review capabilities
9. The quality reviewer provides structured feedback with severity levels and actionable improvements
10. `skills/quality-control/SKILL.md` provides quality validation capability with references for standards
11. `skills/quality-control/scripts/` contains Python accessibility checking and brand validation code
12. Quality review results are logged to the production run audit trail in SQLite
13. Both agents have memory sidecars initialized with index.md, patterns.md, chronology.md, and access-boundaries.md
14. Party Mode team reviews both completed agent structures for accuracy and completeness
15. Human review (Juan) confirms sample artifacts meet quality standards for instructional soundness and prose quality

## Tasks / Subtasks

- [ ] Task 1: Party Mode coaching session for Content Creator + Quality Reviewer (AC: all)
  - [ ] 1.1 Run Party Mode coaching to produce refined bmad-agent-builder discovery answers for Content Creator
  - [ ] 1.2 Run Party Mode coaching to produce refined bmad-agent-builder discovery answers for Quality Reviewer
  - [ ] 1.3 Save coaching output to `_bmad-output/brainstorming/party-mode-coaching-content-creator-quality-reviewer.md`

- [ ] Task 2: Create Content Creator agent via bmad-agent-builder (AC: #1, #2, #3, #4, #7)
  - [ ] 2.1 Run bmad-agent-builder six-phase discovery with coached answers for Content Creator
  - [ ] 2.2 Output: `skills/bmad-agent-content-creator/SKILL.md` with Instructional Architect persona
  - [ ] 2.3 Follow Marcus/Gary SKILL.md pattern: Overview, Identity, Communication Style, Principles, Does Not Do, On Activation, Capabilities (Internal + External)
  - [ ] 2.4 Internal capabilities: instructional analysis (IA), learning objective decomposition (LO), Bloom's taxonomy application (BT), cognitive load management (CL), content sequencing (CS), assessment alignment (AA), pedagogical quality review (PQ)
  - [ ] 2.5 External agents routing: Paige (tech writer), Sophia (storyteller), Caravaggio (presentation expert)
  - [ ] 2.6 External skills routing: editorial review agents for polish
  - [ ] 2.7 Create reference templates in `skills/bmad-agent-content-creator/references/` for all 6 output artifact types

- [ ] Task 3: Create Quality Reviewer agent via bmad-agent-builder (AC: #8, #9)
  - [ ] 3.1 Run bmad-agent-builder six-phase discovery with coached answers for Quality Reviewer
  - [ ] 3.2 Output: `skills/bmad-agent-quality-reviewer/SKILL.md` with Quality Guardian persona
  - [ ] 3.3 Follow Marcus/Gary SKILL.md pattern
  - [ ] 3.4 Internal capabilities: quality assessment (QA), compliance checking (CC), feedback generation (FG), brand consistency validation (BV), accessibility review (AR)
  - [ ] 3.5 External skills routing: `quality-control` skill for automated checks

- [ ] Task 4: Create quality-control skill (AC: #10, #11, #12)
  - [ ] 4.1 Create `skills/quality-control/SKILL.md` with routing and invocation instructions
  - [ ] 4.2 Create `skills/quality-control/references/quality-standards.md` — review dimensions, severity levels, pass/fail thresholds
  - [ ] 4.3 Create `skills/quality-control/references/accessibility-standards.md` — WCAG 2.1 AA checklist for educational content
  - [ ] 4.4 Create `skills/quality-control/references/brand-validation.md` — style bible compliance rules
  - [ ] 4.5 Create `skills/quality-control/scripts/accessibility_checker.py` — automated accessibility scanning
  - [ ] 4.6 Create `skills/quality-control/scripts/brand_validator.py` — automated brand consistency checks
  - [ ] 4.7 Create `skills/quality-control/scripts/quality_logger.py` — log results to SQLite `quality_gates` table
  - [ ] 4.8 Create `skills/quality-control/scripts/tests/` with pytest coverage for all scripts

- [ ] Task 5: Initialize memory sidecars (AC: #13)
  - [ ] 5.1 Update `_bmad/memory/quality-reviewer-sidecar/index.md` with activation context
  - [ ] 5.2 Create `_bmad/memory/quality-reviewer-sidecar/patterns.md`
  - [ ] 5.3 Create `_bmad/memory/quality-reviewer-sidecar/chronology.md`
  - [ ] 5.4 Create `_bmad/memory/quality-reviewer-sidecar/access-boundaries.md`
  - [ ] 5.5 Create `_bmad/memory/content-creator-sidecar/index.md` with activation context
  - [ ] 5.6 Create `_bmad/memory/content-creator-sidecar/patterns.md`
  - [ ] 5.7 Create `_bmad/memory/content-creator-sidecar/chronology.md`
  - [ ] 5.8 Create `_bmad/memory/content-creator-sidecar/access-boundaries.md`

- [ ] Task 6: Produce sample artifacts for human review (AC: #5, #6, #15)
  - [ ] 6.1 Select a designated topic from the course context (Module 1, Lesson 1 or similar)
  - [ ] 6.2 Content Creator produces one of each: lesson plan, narration script, dialogue script, slide brief, assessment brief, first-person explainer
  - [ ] 6.3 Stage all artifacts in `course-content/staging/` following directory conventions
  - [ ] 6.4 Quality Reviewer reviews sample artifacts and produces structured feedback
  - [ ] 6.5 Human review checkpoint: Juan confirms sample artifacts meet quality standards for instructional soundness and prose quality

- [ ] Task 7: Register agents with Marcus (AC: #1, #8)
  - [ ] 7.1 Update Marcus SKILL.md External Specialist Agents table: `content-creator` → active
  - [ ] 7.2 Update Marcus SKILL.md External Specialist Agents table: `quality-reviewer` → active

- [ ] Task 8: Party Mode validation (AC: #14)
  - [ ] 8.1 Run Party Mode review of both completed agents + quality-control skill

## Dev Notes

### Agent Creation Pattern: Follow Gary (Story 3.1) Workflow

Story 3.1 established the canonical pattern for agent creation in this project:

```
1. Party Mode coaching → produce coached bmad-agent-builder discovery answers
2. bmad-agent-builder six-phase discovery (one fresh invocation per agent)
3. Build reference docs for agent capabilities
4. Initialize memory sidecar with all 4 files
5. Test invocations: verify agent responds in character
6. Run quality scan (bmad-code-review for agent files)
7. Party Mode validation: team reviews for accuracy and completeness
```

### Content Creator: Instructional Design Director Model

The Content Creator is NOT a writer. It is the **instructional design authority** that:
- Analyzes learning objectives and decomposes them using Bloom's taxonomy
- Designs content structure for optimal cognitive load
- Provides each BMad writer with precise briefs: learning objectives, target Bloom's level, cognitive load constraints, audience profile, pedagogical intent
- Reviews delegated prose for pedagogical alignment (not prose quality — that's the writer's domain)
- Assembles reviewed content into structured artifact templates

**Delegation model:**
| Writer | Delegated Content Types | When to Use |
|--------|------------------------|-------------|
| **Paige** (Tech Writer) | Procedures, protocols, technical descriptions, data-driven explanations | Structured explanatory content requiring precision |
| **Sophia** (Storyteller) | Case study dialogues, patient vignettes, first-person clinical explainers, emotional engagement pieces | Narrative content requiring engagement and empathy |
| **Caravaggio** (Presentation Expert) | Slide narrative design, visual hierarchy advice, presentation flow, audience attention sequencing | Visual flow and slide-script pairing |
| **Editorial review agents** | All written output before downstream handoff | Polish pass on all delegated work |

### Six Output Artifact Types

Each requires a reference template in `skills/bmad-agent-content-creator/references/`:

1. **Lesson Plans** (`references/template-lesson-plan.md`) — Structured outlines with learning objectives, content blocks, assessment hooks, timing estimates
2. **Narration Scripts** (`references/template-narration-script.md`) — Per-slide scripts with stage directions (tone, pacing, emphasis) for ElevenLabs consumption
3. **Dialogue Scripts** (`references/template-dialogue-script.md`) — Multi-speaker scripts with character labels and tone direction for case study scenarios
4. **Slide Briefs** (`references/template-slide-brief.md`) — Per-slide content specifications (text, key visuals, layout hints) for Gary/Gamma consumption
5. **Assessment Briefs** (`references/template-assessment-brief.md`) — Question/answer specs for Qualtrics integration
6. **First-Person Explainers** (`references/template-first-person-explainer.md`) — Expert-voice content (clinical reasoning walkthrough, procedure narration)

### Quality Reviewer: Systematic Validation Agent

The Quality Reviewer operates independently from the Content Creator. It receives completed artifacts and validates against multiple dimensions:

| Dimension | What It Checks | Source of Truth |
|-----------|---------------|----------------|
| Brand consistency | Colors, typography, voice, tone | `resources/style-bible/master-style-bible.md` |
| Accessibility | WCAG 2.1 AA compliance | `skills/quality-control/references/accessibility-standards.md` |
| Learning objective alignment | Every content element traces to an objective | `state/config/course_context.yaml` |
| Instructional soundness | Bloom's taxonomy, cognitive load, sequencing | Content Creator's pedagogical design |
| Content accuracy | Medical/clinical content correctness | Human review (escalation) |

**Feedback format:** Structured report with severity levels (critical/high/medium/low), specific location in artifact, description, and actionable fix suggestion. Always constructive — never just identifies problems without solutions.

### Quality-Control Skill: Automated Validation Scripts

`skills/quality-control/` provides the automated checking backend for the Quality Reviewer agent:

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `accessibility_checker.py` | WCAG 2.1 AA scanning for text contrast, alt text, reading level, heading hierarchy | Standard library + existing utilities |
| `brand_validator.py` | Style bible compliance: color codes, typography, voice/tone markers | Reads `resources/style-bible/` |
| `quality_logger.py` | Logs review results to SQLite `quality_gates` table | `scripts/state_management/db_operations.py` |

These scripts follow the same pattern as `skills/production-coordination/scripts/` — Python modules importable by the agent's skill, using existing infrastructure (BaseAPIClient not needed here, but SQLite via db_operations.py is).

### Existing Infrastructure to Reuse (DO NOT REINVENT)

| Component | Location | Reuse For |
|-----------|----------|-----------|
| SQLite `quality_gates` table | `scripts/state_management/init_db.py` | Logging quality review results |
| `db_operations.py` | `scripts/state_management/db_operations.py` | Insert/query quality gate records |
| Production-coordination scripts | `skills/production-coordination/scripts/` | Pattern for skill scripts (logging, mode awareness) |
| Marcus SKILL.md | `skills/bmad-agent-marcus/SKILL.md` | Agent .md structure template (118 lines) |
| Gary SKILL.md | `skills/bmad-agent-gamma/SKILL.md` | Specialist agent pattern (delegation, context envelope, activation) |
| Gary references/ pattern | `skills/bmad-agent-gamma/references/` | 9 reference files demonstrating progressive disclosure |
| Memory sidecar pattern | `_bmad/memory/gamma-specialist-sidecar/` | 4-file sidecar (index, patterns, chronology, access-boundaries) |
| BMad writer agents | `.cursor/skills/bmad-agent-tech-writer/`, `.cursor/skills/bmad-cis-agent-storyteller/`, `.cursor/skills/bmad-cis-agent-presentation-master/` | Already installed — Content Creator delegates to these |
| Editorial review skills | `.cursor/skills/bmad-editorial-review-prose/`, `.cursor/skills/bmad-editorial-review-structure/` | Already installed — Content Creator invokes for polish |
| Content standards | `config/content-standards.yaml` | Fallback defaults if no style bible |
| Style bible | `resources/style-bible/master-style-bible.md` | Brand standards for Quality Reviewer |

### File Structure (Expected Output)

```
skills/
├── bmad-agent-content-creator/
│   ├── SKILL.md                           # Agent definition (Instructional Architect)
│   └── references/
│       ├── init.md                        # First-run onboarding
│       ├── memory-system.md               # Sidecar interaction protocol
│       ├── save-memory.md                 # Memory save capability
│       ├── delegation-protocol.md         # How to brief BMad writers
│       ├── pedagogical-framework.md       # Bloom's, cognitive load, sequencing
│       ├── template-lesson-plan.md        # Output template
│       ├── template-narration-script.md   # Output template
│       ├── template-dialogue-script.md    # Output template
│       ├── template-slide-brief.md        # Output template
│       ├── template-assessment-brief.md   # Output template
│       └── template-first-person-explainer.md  # Output template
│
├── bmad-agent-quality-reviewer/
│   ├── SKILL.md                           # Agent definition (Quality Guardian)
│   └── references/
│       ├── init.md                        # First-run onboarding
│       ├── memory-system.md               # Sidecar interaction protocol
│       ├── save-memory.md                 # Memory save capability
│       ├── review-protocol.md             # Systematic review procedure
│       └── feedback-format.md             # Structured feedback template
│
├── quality-control/
│   ├── SKILL.md                           # Skill overview + routing
│   ├── references/
│   │   ├── quality-standards.md           # Review dimensions, severity levels
│   │   ├── accessibility-standards.md     # WCAG 2.1 AA checklist
│   │   └── brand-validation.md            # Style bible compliance rules
│   └── scripts/
│       ├── accessibility_checker.py
│       ├── brand_validator.py
│       ├── quality_logger.py
│       └── tests/
│           ├── test_accessibility_checker.py
│           ├── test_brand_validator.py
│           └── test_quality_logger.py

_bmad/memory/
├── content-creator-sidecar/               # NEW — must create all 4 files
│   ├── index.md
│   ├── patterns.md
│   ├── chronology.md
│   └── access-boundaries.md
└── quality-reviewer-sidecar/              # EXISTS — index.md only, must add 3 files
    ├── index.md                           # UPDATE with activation context
    ├── patterns.md                        # CREATE
    ├── chronology.md                      # CREATE
    └── access-boundaries.md               # CREATE
```

### Agent Location Convention

**Established project pattern:** Agent .md files live at `skills/bmad-agent-{name}/SKILL.md`, NOT in `agents/`. Both Marcus and Gary follow this convention. The `agents/` directory exists but contains only a README.md. The acceptance criteria in the epics originally referenced `agents/quality-reviewer.md`, but this story normalizes to the established pattern: `skills/bmad-agent-quality-reviewer/SKILL.md`.

Marcus's SKILL.md External Specialist Agents table already lists both as planned:
- `content-creator` → planned
- `quality-reviewer` → planned

After this story, both become `active`.

### Validation Model

**No exemplars. No woodshed.** This is a content creation story, not a tool-API mastery story. Validation is:
1. Content Creator produces one sample of each 6 artifact types on a designated topic
2. Samples staged in `course-content/staging/`
3. Quality Reviewer validates samples using quality-control skill
4. Human review (Juan) confirms instructional soundness and prose quality

### Key Lessons from Story 3.1 (Apply Here)

1. **Guide the tool, don't suppress it.** When delegating to BMad writers, provide rich context about desired outcome rather than restrictive constraints.
2. **Separate agent concerns.** Content Creator owns pedagogy. Writers own prose. Quality Reviewer owns validation. No overlap.
3. **Memory sidecar `patterns.md` grows from user checkpoint reviews** — not from internal agent decisions. Content Creator learns which BMad writers produce best results for which content types through user feedback.
4. **Follow the SKILL.md structure exactly.** Gary's 118-line SKILL.md with 9 references and clear capability routing is the template.
5. **Cross-skill imports** use `importlib.util.spec_from_file_location` for hyphenated directory names.

### Testing Standards

- Use pytest for all quality-control scripts
- Mock SQLite operations in unit tests (don't require live database)
- `accessibility_checker.py` tests should use fixture content with known accessibility issues
- `brand_validator.py` tests should use fixture style bible data
- `quality_logger.py` tests should verify correct SQL operations via mocked db_operations

### Anti-Patterns to Avoid

- Do NOT make the Content Creator write prose — it designs and delegates, period
- Do NOT duplicate editorial review logic — use existing `bmad-editorial-review-prose` and `bmad-editorial-review-structure` skills
- Do NOT hardcode quality thresholds — read from `state/config/tool_policies.yaml`
- Do NOT create separate databases — use existing `quality_gates` table in `state/runtime/coordination.db`
- Do NOT place agent files in `agents/` directory — follow established `skills/bmad-agent-{name}/` convention
- Do NOT modify other agents' memory sidecars — each agent writes only to its own
- Do NOT cache style bible content — always re-read from disk

### Project Structure Notes

- Both agents follow `skills/bmad-agent-{name}/SKILL.md` convention (consistent with Marcus, Gary)
- Quality-control skill follows `skills/{skill-name}/` convention (consistent with pre-flight-check, production-coordination, gamma-api-mastery)
- Content Creator sidecar directory `_bmad/memory/content-creator-sidecar/` does NOT exist yet — must be created
- Quality Reviewer sidecar `_bmad/memory/quality-reviewer-sidecar/` exists but only has `index.md` — must add 3 files
- `pyproject.toml` already has `pythonpath = ["."]` for project-root imports in skill tests

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 3.2] — Epic definition with discovery answers and ACs
- [Source: _bmad-output/planning-artifacts/architecture.md#Agent Boundaries] — Agent + skill file locations
- [Source: _bmad-output/planning-artifacts/architecture.md#Quality Control] — FR23-27, FR48-49 mapping
- [Source: _bmad-output/planning-artifacts/prd.md#Quality Control & Review] — FR23-FR27 requirements
- [Source: _bmad-output/implementation-artifacts/3-1-gamma-specialist-agent.md] — Gary creation pattern and lessons
- [Source: skills/bmad-agent-marcus/SKILL.md] — Agent SKILL.md structure template
- [Source: skills/bmad-agent-gamma/SKILL.md] — Specialist agent pattern
- [Source: skills/production-coordination/] — Skill scripts pattern (4 scripts, 4 refs, 40 tests)
- [Source: _bmad/memory/gamma-specialist-sidecar/] — Memory sidecar 4-file pattern
- [Source: _bmad/memory/quality-reviewer-sidecar/index.md] — Existing QR sidecar scaffold
- [Source: docs/directory-responsibilities.md] — Configuration hierarchy
- [Source: docs/dev-guide.md#Agent Anatomy] — Agent creation recipes
- [Source: docs/dev-guide.md#Evaluator Design Requirements] — Quality validation principles

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
