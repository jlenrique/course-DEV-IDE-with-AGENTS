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