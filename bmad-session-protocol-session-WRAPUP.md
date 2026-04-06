# BMAD v6 Session Protocol: End-of-Session (Shutdown)

Companion to `bmad-session-protocol-session-START.md`. Together these two files guarantee reliable context transfer between sessions.

### Context transfer contract

The startup protocol **reads** certain files; the wrapup protocol **writes** them. Every read must have a corresponding write, or context is lost.

| File | Startup reads | Wrapup writes | Role |
|------|:---:|:---:|------|
| `next-session-start-here.md` | Step 1 | Step 7 | **Forward-looking hot-start** — next actions, branch, risks, gotchas |
| `docs/project-context.md` | Step 1 | Step 5 | Current state, key decisions, architecture summary |
| `docs/agent-environment.md` | Step 1 | Step 5 | MCP/API/tool/skill inventory for agents |
| `bmm-workflow-status.yaml` | Step 5 | Step 3 | BMAD phase and workflow transitions |
| `sprint-status.yaml` | Step 5 | Step 4a | Epic/story Kanban state |
| `SESSION-HANDOFF.md` | — | Step 8 | **Backward-looking record** — lessons, decisions, validation (permanent archive; startup does not read) |
| Guides (user/admin/dev) | Step 5 on-demand | Step 9a | Large stable docs — updated only when content changes |

> **Key principle:** `next-session-start-here.md` is the sole ramp-up document for the next session. Any risk, blocker, or unresolved issue from the current session MUST be surfaced there (Step 7), not only in SESSION-HANDOFF. SESSION-HANDOFF is the permanent record; next-session-start-here is the action trigger.

---

## Steps

Execute these steps in order before ending a session.

### 1. Run quality gate

Run the project's quality/hygiene checks:
- **System development**: linter + type checker commands (e.g., `ruff check .`, `npm run lint`)
- **Course content**: content-standards.yaml compliance check, broken link validation
- **General**: `git diff --check` + manual review if no automation exists

Fix findings before proceeding. If no quality mechanism exists, note this as a gap to address in a future story.

### 2. Update BMAD planning and story artifacts

Update canonical BMAD artifacts in `_bmad-output/` to reflect the session's work. This step covers **content artifacts only** — status YAMLs are handled separately in Steps 3 and 4a.

- **Planning phase**: PRD, architecture, epics/stories files in `_bmad-output/planning-artifacts/`
- **Implementation phase**: story artifacts and task checklists in `_bmad-output/implementation-artifacts/` (excluding the two status YAMLs)
- **Brainstorming phase**: brainstorming session files in `_bmad-output/brainstorming/`
- **Content creation**: staging content status, review checklist updates

### 3. Update workflow status

Update `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` only for significant workflow phase changes or status transitions (e.g., story started, story completed, phase advanced). Do not update for minor in-session progress.

### 4a. Update sprint status

Update `_bmad-output/implementation-artifacts/sprint-status.yaml` for epic and story Kanban state changes (e.g., `in-progress` → `review` → `done`).

### 4b. Interaction Testing: 
Confirm presence, if appropriate at this phase of the project work, of an 'Interaction test' for a newly created agent.  The test should be modeled on the interaction test guide now available in the project. If an agent or supporting skill has been modified, ensure the corresponding interaction test is updated, if warranted.

### 5. Update project context and agent environment

Update `docs/project-context.md` only if rules, phase, or architecture changed this session. Do not update for routine implementation progress.

Update `docs/agent-environment.md` if any of the following changed this session:
- MCP servers added, removed, or reconfigured
- API clients added or auth patterns changed
- Shared skills added, renamed, or retired
- Tool tier classifications changed in the tool inventory

Both files are read at startup Step 1 — stale content here means the next session starts with wrong assumptions.

### 6. Update course content state

**For content creation sessions**:
- Move completed content from `course-content/staging/` to `course-content/courses/` if human-approved
- Update content workflow status in `docs/workflow/` (and `workflows/` if your project later adds that directory)
- Log any platform integration results or issues

*Skip if no content creation occurred this session.*

### 7. Update next-session-start-here

Update `next-session-start-here.md` with:
- **Immediate next action** (concrete, unambiguous — the first thing the next session should do)
- **Unresolved issues or blockers** from this session that affect the next session's work (do not bury these only in SESSION-HANDOFF — surface them here)
- Branch metadata and startup commands:
  - `Repository baseline branch` after closeout (commonly `master`)
  - `Next working branch` for implementation in the next session
  - Exact checkout/create commands for the next working branch
- Hot-start notes (key file paths, API references, gotchas discovered this session)
- **Course content context**: staging items pending review, workflow status, platform connection notes

This file is action-oriented and forward-looking. Its purpose is to give the next session's agent the fastest possible ramp-up to productive work. It is the **sole ramp-up document** — the next session reads this file first and may not read SESSION-HANDOFF at all.

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

### 9a. Update guides (if affected)

Update these only if the session changed something they document (new skill, new API client, new workflow, architecture change). Do not update for routine content creation.

- `docs/user-guide.md` — user-facing workflows, Marcus interactions, content organization
- `docs/admin-guide.md` — credentials, MCP config, environment setup, operational procedures
- `docs/dev-guide.md` — architecture, extension recipes, testing, coding standards

These are startup "read on demand" docs (Step 5). Stale guide content wastes context window when the next session loads them.

### 9b. Review reuse and pattern artifacts

If the project maintains reuse, pattern, or service tracking files, review and update them. Check for:
- Design patterns discovered or refined → update `design-patterns.md`
- Services that should be cataloged → update `service-catalog.md`
- **Course content patterns**: content templates, workflow improvements → update `course-content/_templates/`
- **Tool integration patterns**: new MCP/API integrations → update `resources/tool-inventory/`
- Reuse opportunities for future stories → update `reuse-first-protocol.md`

*Skip if none of these files exist or no new patterns/services emerged.*

### 9c. Update structural-walk definitions if control structure changed

If the session changed any of the following, update the structural-walk configuration before shutdown:
- canonical workflow or control docs
- gate names or checkpoint sequencing
- required artifact contracts
- expected bundle assets or validation targets
- workflow families covered by the walk manifests

Touch the smallest required set:
- `state/config/structural-walk/standard.yaml`
- `state/config/structural-walk/motion.yaml`
- `docs/structural-walk.md`

Do not update the walks for routine content or code changes that do not alter what the walks are expected to validate.

### 10. Clean up stale files

Remove or archive any stale session tracking files, orphaned artifacts, or deprecated references that are no longer canonical. This prevents context pollution in future sessions.

**Course content cleanup**: Remove outdated staging content, broken workflow references, stale tool configurations.

*Skip if the workspace is already clean.*

### 11. Verify artifact completeness

Cross-check that every artifact listed in `SESSION-HANDOFF.md` (artifact update checklist) is confirmed current. 

**Minimum verification**: story artifact, sprint-status, workflow-status, project-context, and next-session-start-here.

Also verify branch metadata consistency:
- `next-session-start-here.md` branch instructions match the intended post-closeout Git state
- Startup commands in `next-session-start-here.md` are executable as written

**Course content verification**: content-standards compliance, human review queue status, platform connectivity.

### 11a. Worktree hygiene closeout (mandatory)

Before Git closeout, run:
- `git worktree list`

If a temporary merge/investigation worktree was created during the session, remove it now:
- `git worktree remove <path-to-temporary-worktree>`

If a temporary worktree directory was deleted manually outside Git, clean stale metadata:
- `git worktree prune --verbose`

If you intentionally keep more than one worktree, record why and the exact paths in `next-session-start-here.md` Step 7.

### 12. Git closeout (default)

Default end-of-session flow is:
1. Finalize `next-session-start-here.md` branch metadata for expected post-closeout state (baseline + next working branch + startup commands)
2. Stage all intended changes (`git add ...`)
3. Commit session work on the working branch with a clear summary message
4. Checkout and update `master` from `origin/master`
5. Merge the working branch into `master`
6. Push `master` to `origin`
7. Create the **next working branch** from updated `master` (for the next session), and push with upstream
8. Re-run `git worktree list` and verify only intended worktrees remain registered
9. Re-verify `next-session-start-here.md` branch metadata matches reality. If it does not, make a small docs-only follow-up commit and push.

If your team intentionally skips merge-to-master for a session, explicitly record that exception and the exact resume branch in both `next-session-start-here.md` and `SESSION-HANDOFF.md`.

**Course content commit examples**:
- "Add lesson 3 presentation slides to staging with lesson plan scaffold"
- "Implement Canvas quiz API integration with working example"
- "Complete brainstorming Phase 2: clustered requirements into epic boundaries"

### 13. Optional: session close

Morale summary, party mode wrap-up, or any other team ritual.
