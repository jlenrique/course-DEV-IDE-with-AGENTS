# Project Entry Point — course-DEV-IDE-with-AGENTS

Standard-Version: 1.0.0
Standard-Source: project-registry-maintenance/docs/standards/START_HERE_STANDARD.md
Standard-Revision: 3da386e2c0c65ae49c2beba21e9a3f8d5b9d0bfe
Status: Active
Project: PRJ-0006 — course-DEV-IDE-with-AGENTS

Develop an agent-assisted course and media authoring environment.

This is the project-owned entry map. Existing detailed instructions remain at
their sources. Discovery does not authorize live actions or agent activation.

[Shared standard](https://github.com/jlenrique/project-registry-maintenance/blob/3da386e2c0c65ae49c2beba21e9a3f8d5b9d0bfe/docs/standards/START_HERE_STANDARD.md) · [Audit procedure](https://github.com/jlenrique/project-registry-maintenance/blob/3da386e2c0c65ae49c2beba21e9a3f8d5b9d0bfe/docs/standards/START_HERE_AUDIT.md)

Location: repository/project root on the current host. Relative paths resolve
against this root, not a fixed username or drive. Git clones remain one project;
verify remote identity and local revision. Host deployment is verified separately.

## Resource map

| Resource role | Status | Existing resource(s) | Scope and authority |
|---|---|---|---|
| **Agents** | Mapped | [skills/bmad-agent-marcus/SKILL.md](skills/bmad-agent-marcus/SKILL.md); [skills/bmad-agent-marcus/references/specialist-registry.yaml](skills/bmad-agent-marcus/references/specialist-registry.yaml) | Use the linked source within its stated scope; preserve its authority. Discovery is not execution evidence. |
| **Resource Directory** | Mapped | [docs/directory-responsibilities.md](docs/directory-responsibilities.md); [docs/parameter-directory.md](docs/parameter-directory.md) | Use the linked source within its stated scope; preserve its authority. Discovery is not execution evidence. See Agents for specialist routing. |
| **Session Start** | Mapped | [skills/bmad-agent-cora/references/session-start-protocol.md](skills/bmad-agent-cora/references/session-start-protocol.md); [docs/workflow/production-session-start.md](docs/workflow/production-session-start.md) | Use the linked source within its stated scope; preserve its authority. Discovery is not execution evidence. |
| **Preflight** | Mapped | [skills/pre-flight-check/scripts/preflight_runner.py](skills/pre-flight-check/scripts/preflight_runner.py) | Use the linked source within its stated scope; preserve its authority. Discovery is not execution evidence. |
| **Session Handoff** | Mapped | [SESSION-HANDOFF.md](SESSION-HANDOFF.md); [next-session-start-here.md](next-session-start-here.md) | Use the linked source within its stated scope; preserve its authority. Discovery is not execution evidence. |
| **Role Guides** | Mapped | [docs/user-guide.md](docs/user-guide.md); [docs/admin-guide.md](docs/admin-guide.md); [docs/dev-guide.md](docs/dev-guide.md) | Use the linked source within its stated scope; preserve its authority. Discovery is not execution evidence. |

## Reading order

1. Confirm project identity, current host/platform and the intended task; read
   applicable project instructions without overwriting existing constraints.
2. Consult Agents for existing custom/predefined roles before specialist dispatch.
3. Follow the mapped Session Start, source/handoff reads and relevant Preflight.
   When the mapping points here, establish current state and next action from
   the latest applicable task handoff; surface missing/conflicting sources.
4. Use Resource Directory and Role Guides for the task. Keep operational detail
   in its original source, and use the closeout routine below when finishing.

## Lightweight preflight

Confirm the relevant sources are accessible and their versions/scopes apply.
Identify current authorization and any task-specific prerequisites. Distinguish
document availability from live service/tool readiness. If a mapped operational
preflight exists, follow that source's checks within current task authorization.

## Rapid currency and quality audit

At every meaningful session close, inspect START_HERE and resources affected by
the session, plus known unresolved findings. Keep this rapid and bounded:

1. Check project/host/revision identity and affected links. Do not infer another
   clone has pulled changes or a cloud upload is synchronized with a local file.
2. Check currency against relevant code, source and workflow changes; age alone
   is not staleness. Check quality: authority, clarity, completeness for the task,
   usability, consistency and unnecessary duplication.
3. Check Agents ownership, capabilities, definitions/activation paths, runtime
   availability and shared-resource references. A skill is not an agent registry.
4. Recommend the smallest effective repair. Verify the actual environment can
   use a recommended skill/tool. For outdated graph-derived onboarding, suggest
   Understand Anything only if relevant and available; otherwise identify an
   existing capable environment, established alternative or targeted manual
   update. Installing a missing skill is a proposal, not an automatic action.
5. Record findings with evidence, impact, recommended action, prerequisites,
   availability, fallback and next action. Report scope not checked. Escalate
   broad drift to a separately scoped audit rather than an unbounded scan.

## Session-closeout rule

Follow the existing closeout procedure and perform the rapid audit above in all
session classes. Update authoritative catalogs/docs first, then this map only
when its pointers, scope, authority or reading order changes. Do not copy agent
rosters, procedures or session history here. Preserve unrelated user changes.

When available, run the shared `tools/check_start_here.py START_HERE.md --root .`
from the Registry maintenance checkout (use an absolute document/root path when
working elsewhere). Cloud-only sessions use the same checklist manually if no
Python/file access exists; record why automated validation was not run.

Record in the existing handoff, or the session's closing response if no durable
handoff exists: project ID; host/platform/revision; standard 1.0.0; structural
result or not-run reason; currency AND quality audit scope/findings; Agents check;
map unchanged/updated/blocked; recommendations, prerequisites/fallbacks and next
action. No unperformed check may be reported as passed. Unchanged mappings need
no timestamp-only edit. Update registry pointers only for changed entry location,
identity/access or deployment status, under its own update contract.

## Known mapping limitations

2026-11-05 — Local content reviewed at e2e2559; no root README. hooks/scripts/session-start.mjs is a placeholder, not enforced startup. Checkers inspected, not run.
