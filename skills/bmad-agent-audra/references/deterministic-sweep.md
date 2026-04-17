# L1 Deterministic Sweep

Audra's foundation. Every check below has an **exit-code contract** — the check returns a boolean (pass / fail) and concrete evidence (file path, schema diff, missing-row list). No judgment; only facts.

## Ordering

Run checks in this order. If any check fails, record the finding and continue — L1 collects all findings in one pass, then returns the aggregate exit code. Exit code 0 requires all checks clean. Exit code 1 means at least one finding.

## Check Catalog

### L1-1: Structural Walk

Invoke: `python -m scripts.utilities.structural_walk --workflow <standard|motion|cluster>`

- If the envelope specifies a workflow, run only that workflow.
- If scope is full-repo or since-handoff without a workflow specified, run all three.
- Exit 0 = READY. Any non-zero = L1 finding, type: `alteration`, severity: `high`, check: `structural-walk`.

### L1-2: Reference Resolution

For every doc in the changed-docs window (or full repo on full-repo scope), extract all file/path/flag references and verify each exists.

- Path references: absolute or project-root-relative paths cited in prose or tables.
- Script references: cited scripts under `scripts/`, `skills/`, `.agents/skills/`.
- Contract references: cited contract paths under `state/config/fidelity-contracts/`.
- Flag references: environment-variable names cited in docs, verified against `.env.example` or config schemas.

Unresolved reference -> L1 finding, type: `invention`, severity: `medium` (or `high` if the reference is in a lane-matrix row, L1-contract, or schema spec).

### L1-3: Parameter Directory <-> Schema Lockstep

Read `docs/parameter-directory.md` and `state/config/parameter-registry-schema.yaml`.

- Every parameter row in the directory must resolve to a schema entry.
- Every schema entry must have a row in the directory.
- Parameter family assignment (Run Constants / Narration-time / Assembly-time) must agree between the two sources.

Any mismatch -> L1 finding, type: `omission` or `alteration`, severity: `high`, check: `parameter-lockstep`.

### L1-4: Gate-Contract Lockstep

For every gate (G0-G6) referenced in `docs/fidelity-gate-map.md`, verify a matching contract file exists under `state/config/fidelity-contracts/g{n}-*.yaml`.

Missing contract -> L1 finding, type: `invention`, severity: `high`, check: `gate-contract-lockstep`.

### L1-5: Lane-Matrix Coverage

Read `docs/lane-matrix.md` Coverage Checklist. For every skill listed:

- Confirm the skill directory exists under `skills/`
- Confirm the skill's SKILL.md contains a `## Lane Responsibility` section

Missing directory -> L1 finding, type: `invention`, severity: `high`.
Missing Lane Responsibility section -> L1 finding, type: `omission`, severity: `medium`.

### L1-6: BMAD Closure-Artifact Audit

For every story in `_bmad-output/implementation-artifacts/sprint-status.yaml` with status `done`:

- Confirm acceptance criteria present in the story file
- Confirm automated verification logged (script exit code, test pass line)
- Confirm layered code review present
- Confirm remediated review record present

This check has two modes:

- **Spot mode:** single story ID (triggered by Cora's pre-closure protocol). Returns CA finding for that story.
- **Sweep mode:** all `done` stories in the current sprint. Returns findings for every story with gaps.

Any gap -> L1 finding, type: `omission`, severity: `high`, check: `closure-artifact`.

### L1-7: Placement Audit

For every file in the changed-files window (since-handoff scope) or newly-created file (sweep scope):

- Operational state files (`runtime`, `baton`, `session`) must not live under `config/` or `state/config/`
- Brand identity files (`style-bible`, `exemplars`) must live under `resources/`, never under `state/config/`
- Skill files must live under `skills/` or `.agents/skills/`, never under `_bmad/bmm/` or `_bmad/bmb/`

Placement violation -> L1 finding, type: `alteration`, severity: `medium`, check: `placement`.

### L1-8: Hot-Start-Pair Freshness

Verify `{project-root}/SESSION-HANDOFF.md` and `{project-root}/next-session-start-here.md` both exist and were modified within the session's expected freshness window (since the last session-WRAPUP, per Cora's chronology).

Stale pair -> L1 finding, type: `omission`, severity: `low`, check: `hot-start-freshness`. (Cora acts on this; Audra just reports it.)

### L1-9: Git-Anchored Change Window

Not a check per se — a parameter for the other checks. On since-handoff scope, the change window is the **union** of three git sets:

- Committed since the anchor: `git diff --name-only <handoff-anchor>..HEAD`
- Uncommitted modified (working tree vs. HEAD): `git diff --name-only HEAD`
- Untracked (not ignored): `git ls-files --others --exclude-standard`

`<handoff-anchor>` is resolved by the caller (typically Cora) via `git log -1 --format=%H -- SESSION-HANDOFF.md`. If the caller passes `changed_files_window` in the context envelope, Audra uses it as-is without recomputing. Untracked files are included deliberately: a new doc introduced this session but not yet committed can drift invariants just as easily as a modified one.

Checks L1-2 (reference resolution) and L1-7 (placement audit) respect this scope. L1-5 (lane-matrix coverage) respects it for the "skill directory exists" sub-check but always runs the `## Lane Responsibility` section check whole-repo because a missing-section regression anywhere in `skills/` is a real finding regardless of whether the file was touched this session.

Whole-repo invariant checks that do NOT respect the change window (they always run against the full repo):

- L1-3: Parameter Directory <-> Schema Lockstep
- L1-4: Gate-Contract Lockstep
- L1-6: Closure-Artifact Audit (sweep mode — spot mode is single-story by definition)
- L1-8: Hot-Start-Pair Freshness
- L1-10: Run HUD Lockstep

On full-repo scope, every check is whole-repo regardless of the classification above. On directory scope, the change window is constrained to files under the named directory.

### L1-10: Run HUD Lockstep

Whole-repo invariant (always runs regardless of change window). The Run HUD (`python -m scripts.utilities.run_hud`) is the operator’s live view of production-run position plus dev-cycle progress; it must stay aligned with canonical repo paths and the prompt-pack pipeline definition.

1. **Presence:** Confirm `scripts/utilities/run_hud.py`, `scripts/utilities/progress_map.py`, `tests/test_run_hud.py`, and `tests/test_progress_map.py` exist.
2. **Sprint tracker path:** In `run_hud.py`, confirm `SPRINT_STATUS` resolves to the canonical `_bmad-output/implementation-artifacts/sprint-status.yaml` (same file the rest of BMAD uses).
3. **Pipeline manifest comment:** Confirm the `SYNC-WITH:` line above `PIPELINE_STEPS` references an existing file (today: `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`). If the prompt pack is renamed or versioned, either update the comment and `PIPELINE_STEPS` together or record an L1 finding, type: `alteration`, severity: `high`, check: `hud-pipeline-lockstep`.
4. **Feed integrity:** Confirm `run_hud.py` imports `build_progress_report` from `progress_map` and that import path exists.

Any failure -> L1 finding with the appropriate type/severity above. This check is **not** a substitute for Murat’s behavioral tests; it ensures internal-artifact and routing descriptions the HUD displays do not silently drift from repo SSOT.

## Exit Code Contract

- `0` — every check returned clean
- `1` — at least one check returned a finding

L2 does not run until L1 returns 0.

## Mapping to Phase 2 Runner

When `scripts/utilities/dev_coherence_sweep.py` ships per vision Phase 2, every check above becomes a named sub-command of the single runner. Audra's behavior migrates from invoking checks directly to invoking the runner and parsing its structured output. The check catalog and exit-code contract must survive the migration unchanged.
