# BMAD v6 Session Protocol: Start-of-Session

Companion to `bmad-session-protocol-session-WRAPUP.md`. Together these two files guarantee reliable context transfer between sessions.

## Canonical Session Protocol Set

The canonical BMAD session protocol is this pair:
- `bmad-session-protocol-session-START.md`
- `bmad-session-protocol-session-WRAPUP.md`

If a user or older note refers to a literal "session xyz" document and no such file exists, treat that as a stale label and use this start/wrapup pair instead. Record the assumption in session notes if it affects execution.

## §0: Project Purpose TL;DR (For Unfamiliar Agents)

**Purpose**: Build a persistent collaborative intelligence infrastructure for systematically scaling creative expertise in online course content production. A custom master orchestrator agent (Marcus) coordinates specialist agents that manipulate professional media tools through skills backed by Python scripts for API calls, while systematically capturing creative decision-making patterns in BMad memory sidecars for iterative refinement and reuse.

**Architecture**: Agents are skill directories created via `bmad-agent-builder` six-phase discovery process, living under `skills/bmad-agent-{name}/`. Skills are SKILL.md directories with references/ + scripts/ for tool mastery. Cursor plugin packaging enables native IDE integration.

**Repo Contract**:
```
course-content/courses/     # Published content
course-content/staging/     # Agent drafts (human review queue)
skills/                     # Agent skill directories (auto-discovered)
_bmad/                      # BMad Method artifacts
docs/                       # Architecture + agent guides
scripts/                    # Python infrastructure
state/                      # YAML configs + SQLite runtime
```

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

> **Key principle:** `next-session-start-here.md` is the sole ramp-up document for the next session. Any risk, blocker, or unresolved issue that affects the next session MUST appear there, not only in SESSION-HANDOFF.

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

> **Gitignore caveat:** `.env`, `state/runtime/*.db`, and binary media under `course-content/` are all gitignored. File-search tools (glob, find, ripgrep) that respect `.gitignore` will not see them. Always verify gitignored files by **reading the file directly** (e.g. `Read .env`), never by pattern search. This applies to Cold Start checks and Hot Start step 6.

---

## Start-of-Session (Hot Start)

Execute these steps in order at the beginning of every session.

### 1. Load session context

Open and read:
- `next-session-start-here.md`
- `docs/project-context.md`
- **Course content context**: `docs/agent-environment.md` (MCP, API, platform guidance)

### 1.5: APP Agent Team & Skills Catalog (For Coding Agents)

**Master Orchestrator**: Marcus (`skills/bmad-agent-marcus/SKILL.md`) — Creative Production Orchestrator. Coordinates all APP runs. Consult for production workflows.

**Core APP Agents** (Top 12, see `_bmad/_config/agent-manifest.csv` for full 16):
| Agent | Role | Path |
|-------|------|------|
| Marcus 🎬 | Production orchestrator | `skills/bmad-agent-marcus/` |
| Irene 📝 | Content creator (lesson plans, scripts) | `skills/bmad-agent-content-creator/` |
| Gary 🎨 | Slide generation (Gamma API) | `skills/bmad-agent-gamma/` |
| ElevenLabs 🎤 | Voice synthesis | `skills/bmad-agent-elevenlabs/` |
| Canvas 📚 | LMS deployment | `skills/bmad-agent-canvas/` |
| Kira 🎥 | Video generation (Kling) | `skills/bmad-agent-kling/` |
| Quinn-R 🧪 | Quality review | `skills/bmad-agent-quality-reviewer/` |
| Vera 🔍 | Fidelity assessment | `skills/bmad-agent-fidelity-assessor/` |
| Source Wrangler 📄 | External content ingestion | `skills/source-wrangler/` |
| Tech Spec Wrangler 🔧 | Tool documentation refresh | `skills/tech-spec-wrangler/` |
| Compositor 🎬 | Video assembly | `skills/compositor/` |
| Woodshed 🏋️ | Exemplar mastery training | `skills/woodshed/` |

**Shared Skills** (available to all agents):
- `pre-flight-check` — System readiness verification
- `production-coordination` — Workflow management
- `sensory-bridges` — Multimodal perception (image/audio/PDF)
- `parameter-intelligence` — Tool parameter optimization

**Do NOT create ad-hoc scripts**: Use existing agents/skills first. If missing, request via `bmad-agent-builder`.

### 2. Confirm branch

Check the current Git branch and compare it with the branch instructions recorded in `next-session-start-here.md`.

- If `next-session-start-here.md` includes both a repository baseline branch and a next working branch, use the **next working branch** as the implementation target.
- If the current branch differs from the recorded target, do **not** assume the current branch is wrong. First determine whether a legitimate post-wrapup event occurred after the handoff was written (for example: the user created the next branch, a docs-only closeout follow-up commit landed, or the branch was advanced intentionally outside the prior session's wrapup flow).
- If the current branch is a plausible successor to the recorded target and the repo state is otherwise coherent, treat the current branch as authoritative and reconcile `next-session-start-here.md` at the next wrapup instead of force-checking out the older branch.
- Only checkout the recorded target immediately when the current branch is clearly unrelated to the intended next work.
- If there is an unexplained mismatch, treat `next-session-start-here.md` as stale and record a reconciliation note for wrap-up Step 7 before ending the session.

> **Post-merge convention:** If your team merges to `master` at session end, the next session may open on `master` first. In that case, use the startup commands in `next-session-start-here.md` to checkout/create the next working branch.

### 2b. Dirty-worktree scope fence

Run:
- `git status --short`

Classify changes before doing any work:
- **Session-owned changes**: files this session is expected to touch
- **Pre-existing unrelated changes**: modified or untracked files outside the session scope
- **Collaborative in-scope changes**: changes made during the same session by the user or by other active agents/browser contexts working on the same objective

Rules:
- Do not revert, normalize, or silently absorb unrelated changes into the session.
- Do not misclassify same-session collaborative changes as unrelated just because this agent did not author them.
- If another browser, terminal, or agent has been working on the same session objective, treat those changes as in-scope until evidence shows otherwise.
- If unrelated changes could interfere with the session objective, record the conflict immediately and plan around it.
- If you proceed with unrelated changes still present, carry that forward into wrap-up notes so closeout does not falsely imply a clean tree.

### 2a. Worktree and IDE alignment guard (mandatory)

Run these commands in every active IDE terminal (for example, VS Code and Cursor) and confirm they match:
- `git worktree list`
- `git rev-parse --show-toplevel`
- `git branch --show-current`

Expected result for aligned sessions:
- Same `--show-toplevel` path in each IDE
- Same current branch in each IDE
- No unexpected extra worktree directories in `git worktree list`

If a stale worktree appears (directory was manually removed earlier), run:
- `git worktree prune --verbose`

If one IDE points to a different worktree path, stop and re-open that IDE on the intended project path before making changes.

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

### 4.5: BMAD Glossary (For Unfamiliar Agents)

| Term | Meaning |
|------|---------|
| **BMAD Phases** | 1-analysis → 2-planning → 3-solutioning → 4-implementation |
| **Artifacts** | Deliverables: PRD (requirements), architecture (design), epics/stories (work breakdown), sprint-status.yaml (progress) |
| **Agents** | Custom AI assistants created via `bmad-agent-builder` (e.g., Marcus orchestrator) |
| **Skills** | Reusable capabilities (SKILL.md + scripts/) for tool mastery |
| **Memory Sidecars** | `_bmad/memory/{agent}-sidecar/` for learning/persistence |
| **Party Mode** | Multi-agent discussions via `bmad-party-mode` skill |
| **Woodshed** | Exemplar-driven skill training (study → reproduce → compare) |

### 5. Review BMAD status artifacts

**Always read** (small, frequently changing):
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

**Scan for relevance** (read only the listing or headers, not full content):
- `_bmad-output/planning-artifacts/` (PRD, architecture, epics/stories)
- `_bmad-output/brainstorming/` (active brainstorming sessions)

**Read on demand** (large, stable documents — read only when the session objective involves onboarding, system development, or cross-cutting changes):
- `docs/user-guide.md` (~260 lines)
- `docs/admin-guide.md` (~475 lines)
- `docs/dev-guide.md` (~730 lines)

These guides are already summarized in `docs/project-context.md` (loaded in Step 1). Read the full guide only when you need detail beyond what the project context provides.

**Interaction Testing:** Confirm presence, if appropriate at this phase of the project work, of an 'Interaction test' for a newly created agent. The test should be modeled on the interaction test guide now available in the project.

If these files don't exist yet, note their absence — the project may be in early ideation phase.

### 6. Check content creation state

**For course content sessions**:
- Review `course-content/staging/` for pending human review items
- Check `config/content-standards.yaml` for current voice/accessibility requirements  
- Verify `.env` has required platform credentials loaded — **read the file directly** (`.env` is gitignored; pattern searches will not find it)
- Review active workflow docs in `docs/workflow/` (at minimum `human-in-the-loop.md`)

*Skip if the session objective is pure system development (orchestrator, skills) only.*

### 7. Open implementation files

Open primary implementation files for the target acceptance criteria. If tests exist for the target scope, open those too.

**Coding Entry Points** (for APP development):
- **Marcus Orchestrator**: `skills/bmad-agent-marcus/scripts/` (production run scripts)
- **API Clients**: `scripts/api_clients/` (Gamma, ElevenLabs, Canvas, etc.)
- **Utilities**: `scripts/utilities/` (file ops, logging, state management)
- **State Management**: `state/runtime/coordination.db` (SQLite), `state/config/` (YAML configs)
- **Tests**: `tests/` (unit/integration for agents/skills)

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

