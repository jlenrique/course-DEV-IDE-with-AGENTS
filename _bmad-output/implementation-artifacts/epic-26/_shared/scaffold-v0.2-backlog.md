# BMB Scaffold v0.2 Backlog

**Opened:** 2026-04-17 (Story 26-3 code review)
**Scaffold:** `scripts/bmb_agent_migration/init_sanctum.py` — currently v0.1
**Lock policy:** v0.1 is frozen through Epic 26 pilot wave (Marcus 26-1, Irene 26-2, Dan 26-3). Defects surfaced during pilots are logged here and remediated in a dedicated v0.2 story, NOT patched inline in per-agent migrations.

## Fleet-wide defects (reproduce on all 3 pilots)

### V2-1 — Config path is wrong

**Observed:** Scaffold reads `{project_root}/_bmad/config.yaml` and `{project_root}/_bmad/config.user.yaml` (both missing). Actual repo config is at `{project_root}/_bmad/core/config.yaml`. As a result, `{user_name}` falls back to the literal string `"friend"`.

**Evidence:**
- Marcus BOND.md line 5: `**Operator:** friend`
- Irene BOND.md line 5: `**Operator:** friend`
- Dan BOND.md line 5: `**Operator:** friend`
- Actual `_bmad/core/config.yaml:6`: `user_name: Juanl`

**Location:** `scripts/bmb_agent_migration/init_sanctum.py:434`

**Fix in v0.2:** Read from `_bmad/core/config.yaml` first, then overlay `_bmad/config.yaml` and `_bmad/config.user.yaml` if present.

**Impact scope:** `user_name`, `communication_language` wrong in all sanctum files that substitute them (PERSONA, BOND, INDEX, etc.). BOND.md is overwritten at First Breath with accurate operator info, so runtime impact is bounded. But committed files contain wrong placeholders that look like test artifacts.

### V2-2 — INDEX.md ships absolute Windows paths

**Observed:** Rendered INDEX.md contains the author's local absolute path (`C:\Users\juanl\...`).

**Evidence:**
- Marcus INDEX.md line 3: `` Sanctum at `C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS\_bmad\memory\bmad-agent-marcus`. ``
- Irene INDEX.md line 3: same absolute path pattern
- Dan INDEX.md line 3: same absolute path pattern

**Root cause:** Scaffold substitutes `{sanctum_path}` with an absolute path (resolved via `Path.resolve()`). Should substitute with a project-root-relative path (`_bmad/memory/{skill_name}/`) for portability across machines/CI.

**Fix in v0.2:** Substitute `{sanctum_path}` with repo-relative form (`_bmad/memory/{skill_name}`). Optionally provide a separate `{sanctum_path_absolute}` variable for cases that genuinely need the absolute path.

**Impact scope:** Every rendered sanctum. Portability defect — sanctum files ship with author's local path baked in. Not runtime-breaking (agent re-reads INDEX cosmetically) but a git-hygiene smell.

### V2-3 — Copied references are not variable-substituted

**Observed:** `shutil.copy2` at `init_sanctum.py:368` copies source references verbatim into `{sanctum}/references/`. Any `{sanctum_path}` / `{project_root}` / `{user_name}` tokens in those references survive as literal curly-brace text in the rendered sanctum.

**Evidence:**
- Marcus `_bmad/memory/bmad-agent-marcus/references/memory-guidance.md:12` — literal `{sanctum_path}/sessions/YYYY-MM-DD.md`
- Marcus `.../references/capability-authoring.md:24` — literal `{sanctum_path}/capabilities/<slug>.md`
- Irene same two files, same literals
- Dan same two files, same literals

**Root cause:** `execute_plan` applies `render_template` only to `assets/*-template.md`; `references/*.md` go through `shutil.copy2` untouched.

**Fix in v0.2:** Decision tree:
- **(a)** Extend substitution to references (straightforward but invasive — references become build artifacts, not author-editable)
- **(b)** Source references use literal relative paths instead of placeholders (e.g., hard-code `_bmad/memory/bmad-agent-marcus/sessions/` in Marcus's seed refs — per-agent template duplication, acceptable given references are already per-agent)
- **(c)** Keep placeholders but have the agent's reader (PERSONA activation flow) resolve them at read time — push responsibility to runtime, keep sources editable

Recommendation: **(b)** — simplest, matches the canonical Texas pattern (Texas's seed refs don't use `{sanctum_path}`, they use literal paths).

**Impact scope:** Agent reads its own `memory-guidance.md` during Session Close. With unresolved `{sanctum_path}`, a literal-minded agent would write to a path containing `{` characters or ask for clarification. Not a test-failure, but a real-user-confusion case.

## Per-pilot defects that DO NOT trigger v0.2

(Listed here for completeness — these are per-agent fixes, not scaffold scope.)

- Dan SKILL.md "Intake Contract" paragraph wording (EH-4) — fixed in Dan's SKILL.md
- Dan first-breath.md urgency/discovery ordering (Blind Hunter S3) — fixed in Dan's first-breath.md
- Dan sidecar sibling files lack banner (EH-2) — fixed in Dan's dan-sidecar

## Story placeholder

A dedicated **Story 26-4: BMB Scaffold v0.2** will be opened after Dan's pilot is merged. Scope: fix V2-1, V2-2, V2-3; re-scaffold Marcus/Irene/Dan sanctums for consistency; add regression tests against each defect.

**Not blocking Dan:** The 3 v0.2 triggers above reproduce identically on already-merged Marcus and Irene. Dan is not worse than its predecessors; the defects are fleet-wide and deserve a dedicated fix cycle rather than inline patching that would leave Dan inconsistent with Marcus/Irene.
