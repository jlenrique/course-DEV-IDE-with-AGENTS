# Claude Code — project instructions

This repository uses BMAD methodology. For sprint-style runs, follow the **BMAD sprint governance** checklist below (mirrors `.cursor/rules/bmad-sprint-governance.mdc` and `.github/copilot-instructions.md` for VS Code / GitHub Copilot).

## BMAD sprint governance

1. **Epics and stories** must be produced with BMAD workflows only (for example `bmad-create-epics-and-stories`, `bmad-create-story`, `bmad-create-prd` / architecture / UX chains as appropriate, or `bmad-quick-dev` when that is the right path). If unsure which variant to use, read **`bmad-help`**, run **`bmad --help`**, or convene **`bmad-party-mode`** and ask the team to recommend full planning vs quick-dev vs another module skill.
2. **Green-lighting** and **initial review** of completed work must use **`bmad-party-mode`** (multi-agent roundtable). Do not substitute a single improvised persona for those gates.
3. Before marking any story **done**, you must run **`bmad-code-review`** on the changes in scope (or honor the user’s explicit “run code review” / equivalent invocation).
4. Proceed by **BMAD team consensus** across the active workflow steps and party-mode rounds; keep a short written record of agreed decisions when it affects scope or quality.
5. **Do not** stop the run except when **(a)** every in-scope story is **done** according to `_bmad-output/implementation-artifacts/sprint-status.yaml`, or **(b)** **impasse**: after documented party-mode rounds the team still cannot agree on a path—then pause and escalate to the human.
6. **Impasse** means: relevant voices in party mode have had at least one full round, the disagreement is stated explicitly, and no consensus option remains acceptable to all; it does not mean routine questions or a single agent’s uncertainty.

Related skills: `bmad-help`, `bmad-party-mode`, `bmad-code-review`, `bmad-quick-dev`, `bmad-sprint-run-charter`.

## Texas retrieval

Shape 3-Disciplined retrieval contract lives at [`skills/bmad-agent-texas/references/retrieval-contract.md`](skills/bmad-agent-texas/references/retrieval-contract.md). The provider directory (`run_wrangler.py --list-providers`, or `retrieval.list_providers()`) is authoritative for "what Texas can fetch." Schema v1.1 changelog at [`_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md`](_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md).

## Lesson Planner MVP — dev-agent references

For any Lesson Planner MVP story (Epics 28-32), the dev agent reads the following references at T1 before any code is written:

- [`docs/dev-guide/pydantic-v2-schema-checklist.md`](docs/dev-guide/pydantic-v2-schema-checklist.md) — the 14 schema idioms that prevent the G6 MUST-FIX findings seen on Story 31-1 (`validate_assignment=True`, timezone-aware datetimes, UUID4 validation, triple-layer red-rejection on closed enums, `Field(exclude=True) + SkipJsonSchema` for internal audit fields, etc.).
- [`docs/dev-guide/dev-agent-anti-patterns.md`](docs/dev-guide/dev-agent-anti-patterns.md) — catalog of traps harvested from 27-0, 27-2, 31-1 Dev Notes and G6 code-review findings. Organized by category (schema, test-authoring, review-ceremony, refinement-iteration, Marcus-duality).
- [`docs/dev-guide/story-cycle-efficiency.md`](docs/dev-guide/story-cycle-efficiency.md) — governance rules for K-floor discipline (target 1.2-1.5× K, not 5×), single-gate vs dual-gate review policy with per-story designation, aggressive DISMISS rubric for G6 cosmetic NITs, T-task parallelism, and scaffold-adoption enforcement.

**Schema-shape stories** (31-2, 31-3, 29-1, 32-2, and any future story whose deliverable is a Pydantic-v2 model family + emitted JSON Schema + shape-pin tests) default to the scaffold at [`docs/dev-guide/scaffolds/schema-story/`](docs/dev-guide/scaffolds/schema-story/). Pre-instantiated stubs live at the story's target paths before `bmad-dev-story` begins; the dev agent extends those stubs rather than re-deriving from the 31-1 precedent. Scaffold updates and Pydantic-checklist updates land in lockstep.

## Lesson Planner governance enforcement

For Lesson Planner MVP stories (Epics 28-32), guidance is not enough; run the repo validator at the workflow gates:

- Before a story is finalized as `ready-for-dev`, run
  `python scripts/utilities/validate_lesson_planner_story_governance.py <story-file>`.
- Before `bmad-dev-story` begins on a Lesson Planner story, run the same validator again.
- Treat a non-zero result as a governance failure that must be remediated before proceeding.

Default behavior is **self-remediate first, escalate second**:

- If the validator fails, automatically fix every policy-preserving issue you can correct in the story spec or adjacent workflow artifacts.
- Rerun the validator after remediation and continue the run without waiting for the human if the story reaches PASS.
- Escalate to the human only if the remaining failure requires one of the following:
  - a gate-mode change (`single-gate` vs `dual-gate`)
  - a K-policy or target-range policy change
  - an intentional edit to
    [`docs/dev-guide/lesson-planner-story-governance.json`](docs/dev-guide/lesson-planner-story-governance.json)
  - a deliberate policy exception
  - a true party-mode impasse on scope, architecture, or governance interpretation

The validator currently enforces:

- expected `single-gate` vs `dual-gate` mode per story
- explicit `T1 Readiness` block presence
- required readings citation
- scaffold reference on schema-shape stories
- story-status vs `sprint-status.yaml` sync
- K-floor / target-range rules, including any story-specific K contract encoded in the policy file

Closeout hygiene remains mandatory:

- update `sprint-status.yaml` first
- update `next-session-start-here.md` second
- update any top-level plan or status line that would otherwise drift
