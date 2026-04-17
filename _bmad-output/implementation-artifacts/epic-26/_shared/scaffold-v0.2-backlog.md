# BMB Scaffold v0.2 — Shipped Spec

**Opened:** 2026-04-17 (Story 26-3 code review)
**Shipped:** 2026-04-17 (Story 26-4 closed BMAD-clean)
**Scaffold:** `scripts/bmb_agent_migration/init_sanctum.py` — now v0.2
**Lock policy:** v0.1 was frozen through Epic 26 pilot wave (Marcus 26-1, Irene 26-2, Dan 26-3). Post-pilot, the 3 fleet-wide defects below were remediated in Story 26-4 as a dedicated scaffold-hardening cycle before the batch migration of the remaining ~14 agents.

## v0.2 Contract (what the batch wave inherits)

The scaffold v0.2 guarantees:

1. **Config source-of-truth:** Reads `_bmad/core/config.yaml` as the BMB-canonical base. Overlay order (later overrides earlier): `_bmad/core/config.yaml` → `_bmad/config.yaml` → `_bmad/config.user.yaml`. `user_name` and `communication_language` are pulled from the merged config; fallback to `"friend"` / `"English"` only when unset everywhere.
2. **`{sanctum_path}` is repo-relative POSIX:** `_bmad/memory/<skill_name>` (forward slashes even on Windows). Guarantees portability across machines and CI; no author-local absolute paths leak into committed artifacts. Cross-OS test: `test_sanctum_path_uses_posix_separators`.
3. **References are rendered, not copied:** `references/*.md` go through the same whitelist substitution as `assets/*-template.md`. The whitelist is 7 documented variables (`user_name`, `communication_language`, `document_output_language`, `birth_date`, `project_root`, `sanctum_path`, `skill_name`). Foreign `{...}` tokens — template literals authored by the agent for activation-time interpretation — survive unchanged. Test: `test_v2_3_reference_render_preserves_unknown_braces`.
4. **`--force` is the canonical re-render primitive:** Without `--force`, an existing sanctum (detected by `INDEX.md` presence) is preserved and the scaffold exits 0 with a skip notice. With `--force`, files are overwritten AND stale top-level/references/scripts files (no longer corresponding to a skill-bundle source) are purged to prevent drift across migrations. Preservation-of-operator-edits semantics will ship in Story 26-5 before operator edits accumulate at scale.
5. **`--project-root` validation:** Scaffold refuses to mkdir into a workspace where `--skill-path` is not inside `--project-root` (exit code 2). Prevents typo-level mistakes from polluting foreign directories.
6. **Version string:** `SCAFFOLD_VERSION = "0.2"` appears in dry-run + real-run banners for provenance.

Tests that enforce this contract live in `tests/migration/test_bmb_scaffold.py` under the `Story 26-4: scaffold v0.2 regression tests` block. Any attempt to regress the contract will fail one of the 10 v0.2 tests.

## Fleet-wide defects remediated in v0.2 (were reproducing on all 3 pilots)

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

## Story history

- **2026-04-17 (Story 26-3 close-out):** Opened as a backlog after Dan pilot review surfaced the 3 fleet-wide defects. Deferred from 26-3 because fixing inline would leave Dan inconsistent with already-merged Marcus + Irene.
- **2026-04-17 (Story 26-4 close-out):** Shipped as v0.2. All 3 defects remediated; 10 new regression tests added; Marcus/Irene/Dan sanctums re-scaffolded with `--force`; all 3 pilots verified clean (Operator: Juanl, repo-relative sanctum paths, rendered references).
- **Story 26-5 (preservation semantics):** Open in backlog. Scope: add file-level preservation heuristic so `--force` doesn't clobber operator edits. Target: before the batch migration of the remaining ~14 agents — operator edits start accumulating once agents go through First Breath with real runs.
