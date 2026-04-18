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
