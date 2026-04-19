# Story Cycle Efficiency

**Audience:** human orchestrator + BMAD dev/review agents working Lesson Planner MVP stories.
**Purpose:** codify the governance moves that compress story cycle time without sacrificing the layered-review insurance that caught two HIGH bugs on 27-2 and six MUST-FIXes on 31-1.

This document is the "faster, not looser" rulebook. Every rule here traces to an observed overhead in 31-1's ~1-hour cycle. Follow them on 31-2 onward.

---

## 1. K-floor discipline

### Rule

`tests_added ≥ K` is a **floor, not a ceiling multiplier**. Target range: **1.2× K to 1.5× K**. Beyond 1.5× K, the dev agent must name the specific coverage gap that justifies the extra tests.

### Evidence

Story 31-1 shipped 131 tests against K=25 (5.2×). Of the extra 106 tests, **one** was a genuine coverage gap flagged at G6 (MF-5 Dials boundary values). The remaining ~100 were parametrized-matrix expansion that didn't surface new failure modes.

### Application

- Dev agent at T2 picks a tentative test count in the 1.2-1.5× K range.
- Coverage-gap tests that emerge from thinking through the AC matrix are added without count discipline — that's legitimate.
- Parametrized cases over enum values are ONE test, not N tests; don't inflate the count by counting parametrization expansion.
- At T_final, if the actual count exceeds 1.5× K, the Dev Agent Record must name the specific coverage justification per extra ~5 tests.

## 2. Single-gate vs dual-gate review

### Rule

Not every story needs both pre-dev R2 party-mode review AND post-dev G5 party-mode review. For the Lesson Planner MVP, the split is:

**Dual-gate (R2 + G5):** foundation, refactor, or integration stories where spec risk is high and post-dev surprise is expensive.

- 30-1 (Marcus-duality refactor) — golden-trace baseline makes surprises catastrophic.
- 30-3a (4A skeleton + lock)
- 30-3b (dials + sync reassessment)
- 30-4 (plan-lock fanout)
- 31-2 (Lesson Plan log) — single-writer invariant is new architecture.
- 31-4 (blueprint-producer) — human-review loop is novel.
- 31-5 (Quinn-R two-branch) — gate logic affects trial-run PDG.
- 29-2 (Gagné diagnostician) — p95 budget gate requires upfront design review.
- 28-2 (Tracy three modes) — posture discrimination is the story's core risk.
- 32-3 (trial-run smoke harness) — end-to-end integration.

**Single-gate (post-dev review only):** schema-shape stories with clear precedent, narrow peripheral stories, doc charters.

- 31-3 (registries)
- 29-1 (fit-report validator — 31-1 absorbed the schema; 29-1 is the validator wrapper)
- 29-3 (Irene blueprint co-author)
- 28-1 (Tracy reshape charter — doc-only)
- 28-3 (Irene↔Tracy bridge)
- 28-4 (Tracy smoke fixtures)
- 30-2a (pre-packet extraction lift — refactor-only, tests pin byte-identical)
- 30-2b (pre-packet envelope emission)
- 30-5 (retrieval-narration-grammar — sentence templates)
- 32-1 (4A workflow wiring)
- 32-2 (coverage-manifest verifier)
- 32-4 (Maya journey walkthrough)

### Application

Single-gate stories run: `bmad-create-story` → dev execution → single post-dev review (party-mode or layered code review, not both for 2-point stories) → closure.

Dual-gate stories run the full 31-1 cycle: `bmad-create-story` → R2 party-mode green-light → dev execution → G5 party-mode implementation review → G6 bmad-code-review layered pass → closure.

### Why G6 stays non-negotiable

`bmad-code-review` layered pass (Blind Hunter + Edge Case Hunter + Acceptance Auditor) caught two HIGH correctness bugs on 27-2 and six MUST-FIXes on 31-1 that unit tests did not catch. Compressing this tier is where speed-quality tradeoffs go wrong. Keep it on dual-gate stories unconditionally; for single-gate stories, keep at least one of the three layers (Edge Case Hunter is the highest-value single layer).

## 3. Aggressive DISMISS rubric for G6

### Rule

At G6 triage, findings in the following categories get a one-line DISMISS without extended rationale:

- Cosmetic: naming preferences, comment phrasing, docstring style.
- DRY: "this regex appears in two places, refactor to a module constant" — only if the two places would actually evolve together.
- Pragma style: `# noqa` placement, `# type: ignore` wording, import order preferences not flagged by ruff.
- Test-count theater: "could add one more parametrize case for symmetry."

### Evidence

31-1's G6 dismissed 23 NITs. Even a one-minute triage per finding is 23 minutes. A one-line rubric cuts this to under 5 minutes.

### Application

G6 orchestrator at triage time uses this phrasing: `DISMISS (cosmetic)` / `DISMISS (DRY-noise)` / `DISMISS (pragma)` / `DISMISS (test-theater)`. No per-finding rationale. Findings flagged by any of the three hunters as confidence ≥0.7 are exempt from fast-dismiss — they get full triage regardless of category.

## 4. Template-reuse expectation

### Rule

For schema-shape stories (31-2, 31-3, 29-1, 32-2), the dev agent starts from the scaffold at `docs/dev-guide/scaffolds/schema-story/` rather than re-deriving from the 31-1 precedent.

### Instantiation contract

The story spec's File Impact section lists pre-instantiated stub paths. The scaffold is copied, placeholders filled, and stubs committed to their target paths BEFORE `bmad-dev-story` begins. The dev agent at T2 reads files that already exist with correct idioms; it extends them with story-specific logic.

### Scaffold maintenance

When a new Pydantic-v2 pitfall is caught at G6 on a real story, updates land in lockstep across:

1. The story's code (the fix).
2. `docs/dev-guide/scaffolds/schema-story/` (the idiom pre-wired).
3. `docs/dev-guide/pydantic-v2-schema-checklist.md` (the rule documented).
4. `docs/dev-guide/dev-agent-anti-patterns.md` (the trap cataloged).

One PR, four files. Never a scaffold update without matching checklist update.

## 4A. Validator gate

### Rule

Lesson Planner story preferences are enforced by command, not memory.

Before a Lesson Planner story is finalized as `ready-for-dev`, and again before
`bmad-dev-story` starts, run:

`python scripts/utilities/validate_lesson_planner_story_governance.py <story-file>`

### Scope

The validator checks:

- per-story `single-gate` vs `dual-gate` policy
- explicit `## T1 Readiness` block presence
- required reading citations
- scaffold references on schema-shape stories
- story-file status vs `sprint-status.yaml`
- K-floor / target-range discipline

Story-specific preferences live in
`docs/dev-guide/lesson-planner-story-governance.json`.

## 5. T-task parallelism

### Rule

BMAD T-tasks within a story are serialized by default. They can be batched into a single tool-call burst if ALL of these hold:

- No file-scope overlap (T_a and T_b don't write the same file).
- No output dependency (T_b doesn't need T_a's output as input).
- No gate-order dependency (e.g., schema pin T depends on schema code T landing first).

### Application

At T1, the dev agent inspects the task list and groups independent tasks. Example from the schema-story scaffold shape:

**Serial group 1 (schema landing):** T2 author schema.py → T3 author state-machine model_validators → T4 emit JSON Schema artifact.

**Parallel burst 1 (independent test files):** T5 shape-stable test + T6 parity test + T7 no-leak grep test + T8 digest determinism test. All four write to different `tests/contracts/` files, all four depend only on T2-T4 landing. Fire them in a single multi-tool-call message.

**Serial group 2 (closure):** T_final-1 full regression → T_final closure check.

### Expected savings

On a schema-shape story with ~6 test files, batching them into one burst saves ~5 minutes of sequential tool-call overhead. Compounds across 8-10 downstream schema stories.

## 6. Pre-work parallelism (across stories)

### Rule

Work that doesn't depend on the currently-in-flight story should run in a side worktree during idle agent time.

### Currently active opportunities

- **30-1 Golden-Trace Baseline capture:** can run during 31-2 or 31-3 dev. Plan at `_bmad-output/specs/30-1-golden-trace-baseline-capture-plan.md`.
- **Spec skeleton authoring for 29-1, 32-1, 32-2, 32-4:** can run during 30-* dev. These stories don't block until their epic opens.

### Application

The human orchestrator maintains a "runway queue" of idle-time tasks. When an in-flight story enters a wait state (party-mode deliberation, code-review patch cycle, human-review checkpoint), spawn a subagent on the next runway task.

## 7. Scaffold-adoption enforcement

### Rule

Schema-shape stories adopt the scaffold via three independent vectors so that missing one doesn't mean adoption fails:

1. **Pre-instantiated stubs** at target paths before `bmad-dev-story` starts. (Strongest.)
2. **Story spec Testing Standards section** references the scaffold + this doc + the Pydantic checklist + the anti-patterns catalog.
3. **Project-level CLAUDE.md** names the scaffold as the default starting point for schema-shape stories.

### Detection

If a schema-shape story lands without using the scaffold (detectable by the absence of the characteristic idioms in shipped code), that's a G5 finding. The remediation is to lift the story into the scaffold before closure, not to paper over.

---

## Expected cycle-time reduction

Applied across the remaining 21 Lesson Planner MVP stories, these rules together target a ~40% reduction relative to the 31-1 baseline cycle. Breakdown:

- K-floor discipline: ~20 min per schema story × 8 schema stories = ~2.5 hrs.
- Single-gate review: ~30 min per story × 12 single-gate stories = ~6 hrs.
- Aggressive dismissal: ~15 min per story × 20 stories = ~5 hrs.
- Template-reuse: ~15 min per schema story × 4 downstream schema stories = 1 hr.
- T-task parallelism: ~5 min per story × 20 stories = ~1.5 hrs.

Total: ~16 hours compressed across the remaining plan. Combined with the ~4 hours from Lane 1 parallelism, the MVP prep lands in the 3-6 hour range rather than the naive 15-hour extrapolation.

---

## Non-goals

This document does NOT:

- Change the acceptance criteria for any story.
- Change the `bmad-code-review` layered pass format.
- Reduce G6 code-review coverage on dual-gate stories.
- Override any R1 ruling amendment or R2 rider that's already binding on a story.

Everything here is process efficiency. Contract-level quality gates are unchanged.

---

## Changelog

| Version | Date | Source |
|---------|------|--------|
| v1 | 2026-04-18 | Extracted from Story 31-1 ~1-hour cycle diagnosis + review-record findings |
