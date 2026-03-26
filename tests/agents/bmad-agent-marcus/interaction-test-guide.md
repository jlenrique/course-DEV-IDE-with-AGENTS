# Marcus Interaction Test Guide

**Agent:** bmad-agent-marcus (Creative Production Orchestrator)
**Story:** 2.1 — Master Orchestrator Agent Creation
**Last Updated:** 2026-03-26
**Prerequisites:** Open a fresh Cursor chat session. No prior Marcus conversation in context.

## How to Use This Guide

Each test scenario describes:
1. **What to say** — your prompt to the agent
2. **What to expect** — the behavior and content Marcus should exhibit
3. **Pass/Fail criteria** — concrete checks you can verify

Run these in a **fresh Cursor chat session** to avoid context contamination. Say "Talk to Marcus" or "I want to talk to the production orchestrator" to activate the agent.

---

## Test 1: First Activation & Greeting

**Trigger:** Activate Marcus in a fresh session (first time, no sidecar memory exists yet).

**What to say:**
> Talk to Marcus

**Expected behavior:**
- Marcus loads `./references/init.md` (first-run onboarding) since no sidecar exists
- Asks discovery questions: your name, course context, style bible status, exemplar library status, tool availability
- Greets warmly, not with a system-status dump
- Offers to run a pre-flight check

**Pass criteria:**
- [ ] Marcus introduces himself by name and role (Creative Production Orchestrator)
- [ ] Uses the veteran executive producer persona — calm, professional, not robotic
- [ ] Asks for your name (or addresses you if config has it)
- [ ] Mentions or checks for `state/config/course_context.yaml`
- [ ] Mentions or checks for `resources/style-bible/`
- [ ] Mentions or checks for `resources/exemplars/`
- [ ] Offers to run pre-flight check
- [ ] Does NOT dump a menu or capability table unprompted

**Fail criteria:**
- Responds as a generic assistant without the Marcus persona
- Lists all capabilities in a raw table without conversational framing
- Asks for API keys or technical configuration details directly

---

## Test 2: Mode Awareness

**What to say (after activation):**
> What mode are we in?

**Expected behavior:**
- Marcus reports current mode (should be "default" for fresh session)
- Explains briefly what the mode means
- Does NOT require being asked twice

**Pass criteria:**
- [ ] Reports "default mode" (or reads from `mode_state.json` if present)
- [ ] Explanation is conversational, not a raw config dump
- [ ] Mentions key implications: "full state tracking, assets go to production staging"

---

## Test 3: Mode Switch to Ad-Hoc

**What to say:**
> Let's work ad hoc until further notice

**Expected behavior:**
- Marcus confirms the switch with an unambiguous statement
- Covers all affected systems in the confirmation

**Pass criteria:**
- [ ] Confirmation includes: assets route to staging scratch
- [ ] Confirmation includes: state tracking paused
- [ ] Confirmation includes: QA still active
- [ ] Tells you how to switch back ("say 'default mode' or 'full throttle'")
- [ ] Does NOT ask "are you sure?" — respects the request

---

## Test 4: Mode Switch Back to Default

**What to say:**
> Let's go full throttle

**Expected behavior:**
- Marcus switches back to default mode
- Confirms the change

**Pass criteria:**
- [ ] Reports "default mode" restored
- [ ] Mentions state tracking resumed
- [ ] Mentions assets route to production staging
- [ ] Mentions clearing ad-hoc session context

---

## Test 5: Capability Awareness

**What to say:**
> What can you help me with?

**Expected behavior:**
- Marcus describes capabilities in production scenarios, not a raw capability table
- Frames in terms of what the USER can accomplish, not system internals
- Mentions the key categories without overwhelming

**Pass criteria:**
- [ ] Mentions content production (slides, assessments, case studies, etc.)
- [ ] Mentions pre-flight checks / tool readiness
- [ ] Mentions source material assistance (Notion, Box Drive)
- [ ] Mentions quality review and standards
- [ ] Conversational framing — NOT a raw copy of the Capabilities table from SKILL.md
- [ ] Uses domain vocabulary (learning objectives, modules, assessments)

---

## Test 6: Style Bible Awareness

**What to say:**
> What style standards are we working with?

**Expected behavior:**
- Marcus reads `resources/style-bible/master-style-bible.md` fresh
- Summarizes key brand elements (JCPH Navy, Medical Teal, Montserrat/Open Sans)
- References the style bible as the authoritative source

**Pass criteria:**
- [ ] Mentions specific brand colors (JCPH Navy, Medical Teal) or hex values
- [ ] Mentions typography (Montserrat, Open Sans)
- [ ] Mentions voice characteristics (clear, direct, physician audience)
- [ ] Attributes the information to the style bible, not from memory
- [ ] Does NOT reference `state/config/style_guide.yaml` for brand information

---

## Test 7: Source Material Prompting

**What to say:**
> I want to build slides for a pharmacology lecture

**Expected behavior:**
- Marcus parses intent (content type: lecture slides)
- Asks clarifying questions about scope (which module, which lesson)
- Proactively offers to pull source materials from Notion or Box Drive
- Does NOT immediately start producing

**Pass criteria:**
- [ ] Identifies content type as lecture slides
- [ ] Asks which module/lesson/course
- [ ] Offers to pull Notion notes or Box Drive references BEFORE production
- [ ] Asks about learning objectives if not provided
- [ ] Tone is collaborative — "let me help you plan this" not "provide parameters"

---

## Test 8: Production Planning (Conceptual)

**What to say (after providing module context):**
> Build lecture slides for Module 2, Lesson 1 on cardiac pharmacology. Learning objectives: explain mechanism of action of beta-blockers, compare and contrast selective vs non-selective agents.

**Expected behavior:**
- Marcus creates a production plan with specialist sequencing
- References the style bible for visual standards
- Checks exemplars for relevant patterns
- Presents the plan for user approval before proceeding
- Notes which specialist agents are planned but not yet built

**Pass criteria:**
- [ ] Presents a multi-stage production plan (outline → slides → review → checkpoint)
- [ ] Mentions consulting style bible for brand standards
- [ ] Mentions checking exemplars for patterns
- [ ] Identifies required specialists (content-creator, gamma-specialist, quality-reviewer)
- [ ] Acknowledges specialist agents are "planned" — does NOT pretend they're available
- [ ] Includes at least one human checkpoint gate
- [ ] Mentions the asset-lesson pairing requirement
- [ ] Asks for approval: "Shall I proceed?" or equivalent
- [ ] Gracefully degrades when specialists aren't built yet: suggests what can be done now vs. what requires future stories

---

## Test 9: Graceful Degradation

**What to say:**
> Go ahead and generate the slides now

**Expected behavior:**
- Marcus explains that the gamma-specialist agent doesn't exist yet
- Suggests alternatives or explains what's needed
- Does NOT hallucinate a slide generation workflow

**Pass criteria:**
- [ ] Clearly states the specialist agent is planned but not yet built
- [ ] Does NOT attempt to call Gamma API directly (that's not Marcus's job)
- [ ] Suggests alternatives: "I can help you plan the outline, and once the Gamma specialist is built, we'll generate slides"
- [ ] Remains helpful and in character — not just "error: agent not found"

---

## Test 10: Memory Save

**What to say:**
> Save our conversation context

**Expected behavior:**
- Marcus invokes the SM (Save Memory) capability
- Writes current session context to the sidecar
- Confirms what was saved

**Pass criteria:**
- [ ] Acknowledges the save request
- [ ] Reports what was saved (brief summary)
- [ ] In ad-hoc mode: only writes to transient section of index.md
- [ ] In default mode: writes to full sidecar

---

## Test 11: Does Not Do Boundaries

**What to say:**
> Can you edit the Gamma API client code to add a new parameter?

**Expected behavior:**
- Marcus declines — code modification is outside his scope
- Redirects appropriately

**Pass criteria:**
- [ ] Clearly states this is outside his role
- [ ] Does NOT attempt to read or modify `scripts/api_clients/`
- [ ] Suggests the appropriate path (developer agent, direct coding)
- [ ] Remains professional — not preachy about boundaries

---

## Test 12: Pre-Flight Check Delegation

**What to say:**
> Are all our tools ready?

**Expected behavior:**
- Marcus recognizes this as a pre-flight check request
- Delegates to the `pre-flight-check` skill
- Presents results conversationally

**Pass criteria:**
- [ ] Recognizes the intent without needing exact wording
- [ ] References the pre-flight-check skill (status: active)
- [ ] Presents results in natural language, not raw JSON
- [ ] Highlights any issues with suggestions

---

## Test 13: Production Run Initiation (Story 2.2)

**What to say:**
> Create lecture slides for Module 2, Lesson 1 on cardiac pharmacology. Learning objectives: explain mechanism of action of beta-blockers, compare selective vs non-selective agents.

**Expected behavior:**
- Marcus parses intent → content type: lecture slides, scope: M2-L1
- Marcus builds a production plan using `generate-production-plan.py`
- Marcus presents the plan with stages, specialists, and checkpoints
- Marcus asks for confirmation: "Shall I proceed?"

**Pass criteria:**
- [ ] Identifies content type as lecture-slides
- [ ] Resolves scope to Module 2, Lesson 1
- [ ] References learning objectives in the plan
- [ ] Presents multi-stage plan with specialist assignments
- [ ] Includes human checkpoint gate(s)
- [ ] Asks for confirmation before proceeding
- [ ] Does NOT attempt execution without user approval

---

## Test 14: Progress Reporting During Run (Story 2.2)

**What to say (after approving a plan):**
> What's the status of our current run?

**Expected behavior:**
- Marcus queries run state via `manage_run.py status`
- Reports current stage, completed stages, and next steps conversationally

**Pass criteria:**
- [ ] Reports current mode (default/ad-hoc)
- [ ] Reports active run and content type
- [ ] Shows completed vs total stages
- [ ] Identifies current stage and specialist
- [ ] Conversational format — NOT raw JSON

---

## Test 15: Checkpoint Gate Presentation (Story 2.2)

**What to say (when a stage completes):**
> Show me what we've got so far

**Expected behavior:**
- Marcus presents checkpoint with artifact, quality criteria, and specialist self-assessment
- Asks for explicit decision: approve, revise, or reject

**Pass criteria:**
- [ ] Presents the work product with relevant context
- [ ] References style bible standards
- [ ] Shows quality assessment
- [ ] Requests explicit user decision
- [ ] Handles approval and advances the run
- [ ] Handles revision request and routes back to specialist

---

## Deferred Tests (Require Future Stories)

These tests become relevant as more stories are completed:

| Test | Requires | Story |
|------|----------|-------|
| Multi-specialist workflow execution | Specialist agents built | Stories 3.1-3.4 |
| Quality gate review cycle | Quality reviewer agent | Story 3.4 |
| Full production run with state tracking | Production coordination skill | Story 4.1 |
| Run reporting and analytics | Run reporting skill | Story 4.4 |
| Source wrangling from Notion/Box | Source wrangling skill + NotionClient | Story 3.7 |
| Ad-hoc to production promotion | Promotion capability | Future story |

---

## Traditional Code Tests

Marcus's Python scripts have traditional automated tests in `skills/bmad-agent-marcus/scripts/tests/`:

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test-read-mode-state.py` | 8 | DB queries, mode file reading, fallback behavior, CLI flags |
| `test-generate-production-plan.py` | 7 | All 7 content types, JSON/markdown output, module args, human checkpoints |

Run with: `.venv\Scripts\python skills\bmad-agent-marcus\scripts\tests\test-read-mode-state.py`

---

## Testing Strategy for Future Agents

Every agent built via `bmad-agent-builder` should get:

1. **Interaction test guide** (this pattern) at `tests/agents/{agent-name}/interaction-test-guide.md`
   - Covers persona, capabilities, boundaries, graceful degradation
   - Updated as new stories add capabilities to the agent
   - Human-executed in a fresh Cursor chat session

2. **Traditional code tests** (if scripts exist) co-located at `skills/{agent-name}/scripts/tests/`
   - Automated, run via pytest or direct execution
   - Cover script I/O, error handling, CLI behavior

3. **Integration tests** (when end-to-end flows are possible) at `tests/integration/`
   - Cover cross-agent workflows, state persistence, quality gates
   - Require multiple agents and skills to be built
