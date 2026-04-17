# Sprint Run Charter — Pre-Trial Prep (Epic 26 Wave 6)

**Run date opened:** 2026-04-17
**Branch:** `dev/epic-26-pretrial-prep` (from master `6084f04`)
**Operator:** Juan (sole operator, agents via Claude Code)
**Mode:** Authorized autonomous multi-story run
**Charter authority:** `bmad-sprint-run-charter` skill + `.cursor/rules/bmad-sprint-governance.mdc` + `CLAUDE.md`

## 1. Scope

| Story | Title | Status | Scope decision |
|-------|-------|--------|----------------|
| **26-6** | Marcus production-readiness capabilities (PR-HC, PR-PF, PR-RS, PR-RC) | **Primary target** | **IN** — pre-scoped via party-mode consensus 2026-04-17; the "Story 26-X" the operator has referred to throughout |
| **26-7** | Texas CLI cp1252 guard (one-line fix + test) | Proposed | **IN if time permits** — party-mode will confirm at green-light |
| **26-8** | Audra docs-vs-code schema lockstep (full L1-W expansion) | Partial already shipped | **OUT** — thin version shipped in commit `a944189` (`tests/contracts/test_pack_doc_matches_schema.py`); fuller L1-W expansion deferred pending post-trial defect data |
| **26-9** | Texas wrangler intake-surface expansion (DOCX + image provider) | Deferred prior | **OUT** — party consensus 2026-04-17: too large; defer until after first clean 15-min real run exposes which gaps actually hurt |
| **26-5** | BMB scaffold preservation semantics | Backlog | **OUT** — gates the batch migration wave (~14 agents), different epic timing; revisit after trial restart succeeds |

**Headline scope:** Story 26-6 is the required deliverable. Story 26-7 is a cheap add-on if 26-6 closes smoothly.

## 2. Workflow Pattern (per story)

Per `bmad-help` catalog + operator directive in `feedback_bmad_workflow_discipline.md`:

```
1. Add story entry to sprint-status.yaml (status: ready-for-dev)
2. [party-mode] Green-light — approach, AC spine, risks, scope of this story
3. [bmad-create-story CS]       — produce story artifact at _bmad-output/implementation-artifacts/26-N-*.md
4. [bmad-create-story VS]       — validate story readiness
5. [bmad-dev-story DS]          — execute implementation + tests
6. [party-mode] Review          — design/behavior review of the implementation
7. [bmad-code-review CR]        — adversarial layered review (Blind Hunter / Edge Case Hunter / Acceptance Auditor)
8. Remediate MUST-FIX (→ back to DS if needed, loop 5-7)
9. Mark story `done` in sprint-status.yaml
10. Update epic artifact with closure record
11. → next in-scope story
```

**Exception path:** `bmad-quick-dev` may be used for **26-7** (Texas CLI cp1252 guard) if the party at green-light decides the story is too small to warrant a full CS/VS/DS cycle. Party decides; default is formal cycle.

## 3. Party-Mode Composition

Default attendees chosen per topic relevance. Constants: Murat + Amelia + John. Rotating: domain-fit specialists.

| Round type | Attendees | Purpose |
|------------|-----------|---------|
| **Scope confirmation** (one-time, opens the run) | Murat, Winston, Amelia, John, Paige | Confirm scope decisions above; ratify charter |
| **Story 26-6 green-light** | Murat, Winston, Amelia, John, Paige | Approach critique before CS fires |
| **Story 26-6 implementation review** | Winston (architecture), Amelia (implementation), Murat (tests), Sally (HIL landing-point UX — this is operator-facing) | Design/behavior review before CR |
| **Story 26-7 green-light + review** | Murat + Amelia + John (small; no need for full roster) | Scope + sign-off combined |
| **Impasse arbitration** (if triggered) | All above + Mary or Dr. Quinn if root-cause analysis needed | Reach consensus or explicit impasse declaration |

**Rule:** Do not substitute a single improvised persona for any gate. The charter forbids it; so does `feedback_bmad_workflow_discipline.md`.

## 4. Stop Conditions

Per `.cursor/rules/bmad-sprint-governance.mdc` rules 5–6:

**Continue running** while:
- In-scope stories remain with status != `done`
- Party-mode reaches consensus (even if consensus is "defer this story to a later run")

**Stop and escalate to operator** only if:
- **All in-scope stories are `done`** per `sprint-status.yaml` — completion path (normal exit)
- **Documented impasse** — at least one full party-mode round; disagreement is explicit; no consensus option acceptable to all. Pause, escalate with: the question, the split, the positions taken.

**Explicitly NOT stop conditions:**
- Routine uncertainty or ambiguity (resolve via party consensus, don't pause)
- Single-agent objection without majority support (majority consensus carries)
- Unexpected technical friction (handle in-run; escalate only if it becomes an architectural impasse)
- Pre-commit hook failure (remediate; pre-commit is working as intended to block regressions)

## 5. Branch Strategy

- **Working branch:** `dev/epic-26-pretrial-prep` (this run)
- **Base:** master at `6084f04`
- **Merge at run end:** after completion (all in-scope stories `done` + runbook written), merge to master via `--no-ff` merge commit matching the Epic 26 pattern (see `902a2a7` merge of `dev/epic-26-scaffold-v02`)
- **No force-push ever.** No pushes to master directly; merge only.
- **Feature sub-branches:** none planned. Single working branch for the run; if 26-7 expands unexpectedly, revisit.

## 6. Within-Run Course Correction

**Default:** resolve in-run via party-mode. `bmad-correct-course` is for cross-epic sprint-plan changes; it's overkill for within-story course adjustments.

**Invoke `bmad-correct-course` only if:**
- The run's scope needs to expand beyond 26-6 + 26-7 (crosses into 26-8/9/5 territory)
- Party-mode consensus proposes retiring or renaming an Epic 26 story mid-run
- The operator directs it

**For everything else** — scope trims within a story, AC refinements, approach pivots — document the party-mode decision in the story artifact's Review Record section and proceed.

## 7. Commit Cadence

**Per-phase within a story** (finer than per-story, coarser than per-file):

| Phase | Commit | Rationale |
|-------|--------|-----------|
| CS + VS complete | Commit: `feat(26-N): story artifact + ACs` | Spec is now canonical; separable from impl |
| DS in progress | Commits: `feat(26-N): <capability code or subsystem>` as capabilities land | Each capability is independently verifiable |
| Party review + CR remediation | Commits: `fix(26-N): <finding>` per MUST-FIX remediation | Traceable review trail |
| Closure | Commit: `chore(26-N): close story — sprint-status update + epic record` | Clean audit point |

**All commits on `dev/epic-26-pretrial-prep`.** Pre-commit hooks (ruff + orphan + co-commit) enforced — commits that violate the invariants are blocked; remediate and re-commit.

## 8. Run-Initialization Steps (before Story 26-6 starts)

Ordered checklist — complete 0→4 before the first party-mode green-light fires:

- [ ] **0.** Commit the governance anchors already present on this branch: `.cursor/rules/bmad-sprint-governance.mdc`, `CLAUDE.md`, `AGENTS.md`, plus `maintenance/IDE chat session run prompt 2026-04-17.txt` (if operator authored and intends to version). Also this charter.
- [ ] **1.** Add `26-6-marcus-production-readiness-capabilities: ready-for-dev` to `_bmad-output/implementation-artifacts/sprint-status.yaml` under Epic 26 block. Optionally add `26-7-texas-cli-cp1252-guard: backlog` if party confirms 26-7 in-scope.
- [ ] **2.** Update `_bmad-output/implementation-artifacts/epic-26-bmb-sanctum-migration.md` to reflect new stories in the roster.
- [ ] **3.** Convene party-mode **scope confirmation** round (see §3). Output: ratified scope (may differ from charter proposal — that's fine), ratified charter (amended if needed).
- [ ] **4.** Convene party-mode **Story 26-6 green-light** round. Output: approach approved, AC spine sketched, risks identified.
- [ ] **5.** Fire `bmad-create-story` with identifier `26-6`.

After that, follow the per-story workflow pattern from §2.

## 9. Success / Exit Criteria for This Run

**Minimum success:**
- Story 26-6 closed `done` in `sprint-status.yaml`
- 4 Marcus capability codes (PR-HC, PR-PF, PR-RS, PR-RC) live with verbose landing-point shape
- Prompt pack v4.2 pre-prompt sections stripped, pack is pure numbered prompts
- `pytest -m trial_critical` remains green (97+ tests)
- Full pytest suite green
- Branch merged to master via `--no-ff`

**Stretch success:** 26-7 also closed `done`.

**Session handoff artifact at run end:** updated `SESSION-HANDOFF.md` + `next-session-start-here.md` describing what shipped, trial-restart readiness, any deferred findings.

## 10. Memory Linkage

The following memories govern decisions within this run (read at party-mode time to inform voices):

- `feedback_bmad_workflow_discipline.md` — workflow + party + code-review + consensus discipline
- `feedback_regression_proof_tests.md` — never leave tests failing; three-way classification
- `feedback_landing_point_posture.md` — Marcus SPOC; verbose landing points (ask → default → recommend)
- `feedback_party_consensus.md` — resolve via party-mode, don't interrupt operator
- `project_production_run_speed_target.md` — 15-min target applies to real runs not trials
- `feedback_audio_variation.md`, `feedback_export_mapping_hardening.md`, `feedback_kira_sequencing.md` — production-quality preferences (relevant if 26-6 capabilities touch production flow)
- `project_sanctum_migration.md` — Epic 26 context
- `project_irene_cluster_iteration.md` — cluster-related considerations (if surfaced)

## 11. Open Questions (to resolve in scope-confirmation round)

1. Confirm 26-7 in-scope (yes/no)?
2. Confirm story ID `26-6` for Marcus production-readiness capabilities (no collision, no renaming preferred)?
3. Any preference on whether PR-RS (run-selection) should be its own capability vs folded into PR-HC? Party-mode to judge.
4. For the prompt-pack doc surgery — leave a "see Marcus capability PR-*" pointer at the former location, or strip cleanly? Party to decide.

These are not impasses; they're scoping questions the charter can leave open for the first party round to settle.

## 12. Scope-Confirmation Party Round — Results (2026-04-17)

Round attendees: 🧪 Murat, 🏗️ Winston, 💻 Amelia, 📋 John, 📚 Paige. Full transcript in the session log; synthesis below.

**Consensus (no impasse):**

- **26-6 ratified** with scope refinement: PR-PF + PR-RC **full implementation** (they directly fix the 2026-04-17 halt — `emit-preflight-receipt.py` rejecting run-constants.yaml for UPPERCASE-flat-vs-lowercase-nested schema drift; PR-RC is the direct fix, PR-PF is the gate). PR-HC + PR-RS **stubbed** with codes registered, script skeletons, xfail tests. **All four contracts pinned in ACs** per Winston (invocation envelope, return schema, error surface).
- **26-7 ratified** 4-1 (John dissents as opportunistic Windows-only ergonomics). Land as clean tail after 26-6 per Winston. Murat's test caveat: real encoding-boundary test (round-trip with non-ASCII), not smoke.
- **26-8 / 26-9 / 26-5 confirmed OUT** of this run's scope.
- **26-10 created** as follow-up backlog: promote PR-HC + PR-RS stubs to full impl after first trial restart reveals which stub gaps actually hurt.

**Doc surgery (Paige's amendment adopted):**

- Strip pre-prompt sections from prompt pack v4.2 doc with **redirect stubs** (not clean removal).
- Archive the stripped content verbatim at `docs/workflow/archive/prompt-pack-preprompt-2026-04.md`.
- Create new `docs/dev-guide/marcus-capabilities.md` as canonical PR-* reference.
- Link from `docs/dev-guide.md` alongside `testing.md`.

**Test design guardrails (Murat's red flags adopted into ACs):**

- Shared parametrized summarize-state contract test (one test × 4 capabilities), not 4 bespoke tests.
- Routing-glue tests tagged `trial_critical`.
- Execute-mode tests assert idempotency (re-run must be safe).
- Unit level; no E2E.

**John's "what broke at Prompt 1" reconciliation:** PR-RC (run-constants author+validate) is the direct fix; PR-PF (preflight) is the gate that caught the drift. Stubbing PR-HC + PR-RS keeps scope tractable AND answers John's causal-chain challenge.

**Amelia's sizing:** ~550 LOC + 5h for the trimmed 26-6 (PR-PF + PR-RC full, PR-HC + PR-RS stubs, contract pins). 26-7: ~40 LOC + 45 min.

**26-5 deferral defended:** PR-* capabilities live in Marcus sanctum only, not the scaffold template; adding new capabilities to Marcus does not collide with scaffold preservation semantics. John's concrete-pouring concern does not apply here.
