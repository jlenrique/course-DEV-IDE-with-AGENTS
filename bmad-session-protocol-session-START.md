# BMAD v6 Session Protocol: Multi-Agent Course Content Production

This file is the single source for how BMAD sessions are run for the **course-DEV-IDE-with-AGENTS** project across Cursor Composer and Claude Code chats. It covers cold start (first session), recurring hot start, session shutdown, and cross-context handoffs.

---

## First Session Setup (Cold Start)

Use this section the first time you open this BMAD project in a new tool context. Once confirmed, you will not need to repeat these checks — proceed directly to the Start-of-Session sequence for all subsequent sessions.

1. Confirm these paths exist in the project root:
   - `_bmad/` (BMad Method configuration)
   - `_bmad-output/` (planning and implementation artifacts)
   - `docs/` (project documentation and agent guidance)
   - Skill folder for your tool: `.cursor/skills/` (Cursor) or `.claude/skills/` (Claude Code)
2. If any path is missing, install or initialize BMAD before continuing.
3. **Course content project specifics**: Confirm these paths exist:
   - `course-content/staging/` (agent drafts for human review)
   - `course-content/courses/` (approved/published content)
   - `config/content-standards.yaml` (voice, audience, accessibility defaults)
   - `.env` file (Canvas API, CourseArc, other platform credentials)
4. Once confirmed, proceed to the **Start-of-Session** sequence below.

---

## Start-of-Session (Hot Start)

Execute these steps in order at the beginning of every session.

### 1. Load session context

Open and read:
- `next-session-start-here.md`
- `docs/project-context.md`
- **Course content context**: `docs/agent-environment.md` (MCP, API, platform guidance)

### 2. Confirm branch

Check the current Git branch and checkout the intended working branch if different.

### 3. Identify session target

- **If in brainstorming/ideation phase**: identify which brainstorming session to continue or which analysis skill to run
- **If in planning phase**: identify target artifact (PRD, architecture, epics/stories)
- **If in implementation phase**: identify the target epic, story, and acceptance criteria
- **If in content creation**: identify target course module/lesson and content type (presentation, assessment, discussion)
- In all phases: state a single session objective

### 4. Confirm BMAD phase

Determine which BMAD phase applies to this session's objective: 
- **1-analysis** (brainstorming, research, ideation)
- **2-planning** (PRD, UX design, architecture documentation) 
- **3-solutioning** (epics/stories, implementation readiness)
- **4-implementation** (story development, code review, testing)

Some subsequent steps are implementation-only; skip those steps in earlier phases.

### 5. Review BMAD status artifacts

Review (if they exist):
- `_bmad-output/planning-artifacts/` (PRD, architecture, epics/stories)
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/brainstorming/` (active brainstorming sessions)
- user guide in /docs
- admin guide in /docs
- dev guide in /docs

Interaction Testing: Confirm presence, if appropriate at this phase of the project work, of an 'Interaction test' for a newly created agent.  The test should be modeled on the interaction test guide now available in the project.

If these files don't exist yet, note their absence — the project may be in early ideation phase.

### 6. Check content creation state

**For course content sessions**:
- Review `course-content/staging/` for pending human review items
- Check `config/content-standards.yaml` for current voice/accessibility requirements  
- Verify `.env` has required platform credentials loaded
- Review any active content workflows in `workflows/`

*Skip if the session objective is pure system development (orchestrator, skills) only.*

### 7. Open implementation files

Open primary implementation files for the target acceptance criteria. If tests exist for the target scope, open those too.

*Skip if the session objective is analysis, planning, or review only.*

### 8. Review recent history

Review recent commits and unresolved TODOs/FIXMEs for the same scope.

### 9. Run a validation checkpoint

Run the smallest relevant validation for the feature slice:
- **System development**: automated tests, linter/type checks, or manual verification
- **Course content**: review staging content against content-standards.yaml, check platform connectivity
- **General**: confirm current implementation state against last recorded validation

If no automated validation exists, confirm against the last recorded validation evidence in story artifacts.

*Skip if the session objective is analysis, planning, or review only.*

### 10. State definition of done

State one explicit definition of done for this session. A session DoD is scoped to the session, not the story — a story may span multiple sessions.

**Course content session examples**:
- "Draft lesson 3 slides in staging/ with paired lesson plan, ready for human review"
- "Complete Canvas API integration for quiz deployment with one working example"
- "Generate Gamma prompt templates for presentation workflow with tool inventory entry"

### 11. Scope guard

Confirm the session objective is achievable within a single session. If the objective spans multiple sessions, decompose it into a single-session slice before proceeding.

### 12. Reuse-first pre-check

**For system development**: run a reuse-first check against the service catalog, design patterns, and existing code before creating anything new.

**For content creation**: check `course-content/_templates/` and `resources/exemplars/` before creating new content structures.

*Skip if the session is review, closure, or planning only.*

### 13. Route via BMAD

Invoke the `bmad-help` skill (`.cursor/skills/bmad-help/SKILL.md`) with your objective and current phase/story:

> Route me for this objective: <objective>. Current phase: <1-analysis | 2-planning | 3-solutioning | 4-implementation>. Current story: <id if applicable>.

`bmad-help` analyzes completed artifacts and recommends the next workflow or agent for the current phase.

**Course content routing examples**:
- For ideation: `bmad-brainstorming`, `bmad-product-brief`, CIS skills
- For content creation: `bmad-quick-dev`, content-focused custom skills
- For review: `bmad-editorial-review-prose`, `bmad-review-adversarial-general`

Follow only the routed workflow or agent for the current phase or story.

---

## End-of-Session (Shutdown)

Execute these steps in order before ending a session.

### 1. Run quality gate

Run the project's quality/hygiene checks:
- **System development**: linter + type checker commands (e.g., `ruff check .`, `npm run lint`)
- **Course content**: content-standards.yaml compliance check, broken link validation
- **General**: `git diff --check` + manual review if no automation exists

Fix findings before proceeding. If no quality mechanism exists, note this as a gap to address in a future story.

### 2. Update BMAD artifacts

Update canonical BMAD artifacts in `_bmad-output/` to reflect the session's work:
- **Planning phase**: PRD, architecture, epics/stories files
- **Implementation phase**: story artifacts, task checklists, Dev Agent Record entries
- **Brainstorming phase**: brainstorming session files with current phase status
- **Content creation**: staging content status, review checklist updates

### 3. Update workflow status

Update `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` only for significant workflow phase changes or status transitions (e.g., story started, story completed, phase advanced). Do not update for minor in-session progress.

### 4a. Update sprint status

Update `_bmad-output/implementation-artifacts/sprint-status.yaml` for epic and story Kanban state changes (e.g., `in-progress` → `review` → `done`).

### 4b. Interaction Testing: 
Confirm presence, if appropriate at this phase of the project work, of an 'Interaction test' for a newly created agent.  The test should be modeled on the interaction test guide now available in the project. If an agent or supporting skill has been modified, ensure the corresponding interaction test is updated, if warranted.

### 5. Update project context

Update `docs/project-context.md` only if rules, phase, or architecture changed this session. Do not update for routine implementation progress.

### 6. Update course content state

**For content creation sessions**:
- Move completed content from `course-content/staging/` to `course-content/courses/` if human-approved
- Update content workflow status in `workflows/`
- Log any platform integration results or issues

*Skip if no content creation occurred this session.*

### 7. Update next-session-start-here

Update `next-session-start-here.md` with:
- Next actions (immediate, concrete)
- Current branch and startup commands
- Hot-start notes (key file paths, API references, gotchas)
- **Course content context**: staging items pending review, workflow status, platform connection notes

This file is action-oriented and forward-looking. Its purpose is to give the next session's agent the fastest possible ramp-up to productive work.

### 8. Update session handoff

Update `SESSION-HANDOFF.md` with:
- What was completed this session (summary, not play-by-play)
- What is next (broader context than next-session-start-here)
- Unresolved issues or risks
- Key lessons learned
- Validation summary (what was tested, how, results)
- **Content creation summary**: what content was created/reviewed, platform status, human review queue
- Artifact update checklist (which canonical files were updated)

This file is record-oriented and backward-looking. Its purpose is to preserve context, decisions, and lessons that would otherwise be lost between sessions.

### 9. Review reuse and pattern artifacts

If the project maintains reuse, pattern, or service tracking files, review and update them. Check for:
- Design patterns discovered or refined → update `design-patterns.md`
- Services that should be cataloged → update `service-catalog.md`  
- **Course content patterns**: content templates, workflow improvements → update `course-content/_templates/`
- **Tool integration patterns**: new MCP/API integrations → update `resources/tool-inventory/`
- Reuse opportunities for future stories → update `reuse-first-protocol.md`

Update:
- user guide in /docs
- admin guide in /docs
- dev guide in /docs

*Skip if none of these files exist or no new patterns/services emerged.*

### 10. Clean up stale files

Remove or archive any stale session tracking files, orphaned artifacts, or deprecated references that are no longer canonical. This prevents context pollution in future sessions.

**Course content cleanup**: Remove outdated staging content, broken workflow references, stale tool configurations.

*Skip if the workspace is already clean.*

### 11. Verify artifact completeness

Cross-check that every artifact listed in `SESSION-HANDOFF.md` (artifact update checklist) is confirmed current. 

**Minimum verification**: story artifact, sprint-status, workflow-status, project-context, and next-session-start-here.

**Course content verification**: content-standards compliance, human review queue status, platform connectivity.

### 12. Commit

If changes were made this session, create a commit with a message summarizing the session's work. Push if the branch tracks a remote.

**Course content commit examples**:
- "Add lesson 3 presentation slides to staging with lesson plan scaffold"
- "Implement Canvas quiz API integration with working example"
- "Complete brainstorming Phase 2: clustered requirements into epic boundaries"

### 13. Optional: session close

Morale summary, party mode wrap-up, or any other team ritual.

---

## Cross-Context Handoff Template

Use this template when switching between tool contexts (e.g., Cursor Composer to Claude Code, or between long-running Cursor sessions). Copy, fill, and paste into the new context.

```md
## Handoff Context
- Current phase: <1-analysis | 2-planning | 3-solutioning | 4-implementation>
- Current story/epic: <id/title>
- Branch: <branch-name>
- Objective: <single outcome for next session>
- Content creation status: <staging items, human review queue>

## Canonical BMAD Artifacts Updated
- _bmad-output/...: <files updated>
- bmm-workflow-status.yaml: <changed | no change>
- sprint-status.yaml: <changed | no change>
- docs/project-context.md: <changed | no change + why>
- course-content/ status: <staging → courses promotions, workflow updates>

## Implementation State
- System development completed:
  - <item>
- Content creation completed:
  - <item>  
- In progress:
  - <item>
- Blockers/Risks:
  - <item>

## Platform/Tool Status
- Canvas API: <connected | issues | not configured>
- CourseArc: <status>
- MCP connections: <status>
- Tool inventory: <updates made>

## Next Exact Actions
1. <action>
2. <action>
3. <action>

## Validation State
- Quality checks run: <command + result, or "none available">
- Content standards compliance: <checked | not applicable>
- Last validation evidence: <dry-run result, test output, content review, or "manual review — see story artifact">
```

---

## Reference Notes

### BMAD agents and workflows are skills

All BMAD agents (architect, dev, pm, qa, sm, etc.) and workflows (code-review, create-story, help, etc.) are packaged as **skill files** — markdown files in the IDE's skills folder:

- **Cursor:** `.cursor/skills/bmad-<name>/SKILL.md`
- **Claude Code:** `.claude/skills/bmad-<name>/SKILL.md`

**Course content relevant skills**:
- `bmad-brainstorming` — structured ideation sessions
- `bmad-product-brief` — product definition and scoping
- `bmad-quick-dev` — rapid content/feature development
- `bmad-editorial-review-prose` — content quality review
- `bmad-review-adversarial-general` — critical content evaluation
- CIS skills: `bmad-cis-storytelling`, `bmad-cis-design-thinking`, `bmad-cis-agent-presentation-master`

These are **not** slash commands, CSV files, or standalone executables. They are `.md` files that the AI agent reads and follows.

### Course Content Workflow Integration

This project uniquely combines:
- **BMAD Method**: Structured development process (analysis → planning → solutioning → implementation)
- **Course Content Production**: Multi-agent content creation with human-in-the-loop review
- **Platform Integration**: Canvas, CourseArc, and other LMS delivery

Session protocols must support both **system development** (building the orchestrator, skills, integrations) and **content creation** (generating presentations, assessments, discussions for actual courses).

### Other notes

- `who am i talking to?` is an optional model identity check only — not required for BMAD activation.
- Slash aliases such as `/bmad-master` are optional and valid only if locally configured.
- Each session should follow one phase or one story scope. Avoid mixing multiple stories or phases in a single session context.
- **Course content sessions**: Prefer `course-content/staging/` → human review → `course-content/courses/` workflow over direct edits to published content.