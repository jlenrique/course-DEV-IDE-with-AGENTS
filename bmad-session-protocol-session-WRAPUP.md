# BMAD v6 Session Protocol: Multi-Agent Course Content Production

This file is the single source for how BMAD sessions are run for the **course-DEV-IDE-with-AGENTS** project across Cursor Composer and Claude Code chats. 

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

 content.