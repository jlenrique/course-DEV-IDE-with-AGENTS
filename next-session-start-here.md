# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> **Current objective:** Run `bmad-party-mode` over Amelia's Lesson Planner MVP plan, then `bmad-create-story 31-1-lesson-plan-schema` to start Epic 31 foundation work.

## Immediate Next Action (pick-up point)

1. **Run BMAD Session Protocol Session START.**
2. **Confirm branch**: `dev/lesson-planner` (created 2026-04-18 from `dev/epic-27-texas-intake`). Only session-wrapup planning artifacts on this branch so far — no code commits yet.
3. **Run `bmad-party-mode`** to pressure-test Amelia's MVP plan at [_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md](_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md). Panel suggestion: same four-panel that produced the plan (John PM / Winston Architect / Dr. Quinn / Sally UX) with possible addition of Murat (Test) for acceptance-criteria pressure. Specifically test:
   - 19-story sequencing and point estimates
   - R1 pre-split recommendation on story 30-3 (4A conversation loop, 8pts)
   - First-trial-run readiness criteria (section 6 of the plan)
   - Epic 31 as foundation-first — is it sequenced correctly?
4. **After plan ratification**, run `bmad-create-story 31-1-lesson-plan-schema` to author the foundation story (schema + plan_unit + dials + gaps + revision/digest).
5. Subsequent stories follow critical path: `31-1 → 31-2 → 31-3 → 29-1 → 29-2 → 30-1 → 30-2 → 30-3 → 28-1 → 28-2 → 28-3 → 30-4 → 31-4 → 29-3 → 31-5 → 32-1 → 32-2 → 32-3`.

## Startup Commands

```bash
# Verify branch
git status                 # expect clean on dev/lesson-planner
git log --oneline -3       # last commit should be session-wrapup planning artifact

# Open the plan for party review
cat _bmad-output/planning-artifacts/lesson-planner-mvp-plan.md
```

## Hot-Start Summary

**Prior session (2026-04-18)** had two distinct phases:

### Phase 1 — Story 27-2 BMAD-closed

- SciteProvider(RetrievalAdapter) shipped (620 LOC) as first real retrieval-shape consumer of 27-0 contract.
- run_wrangler.py AC-B.6 dispatcher-wiring cascade + AC-C.11 writer discriminant + AC-T.6 legacy-DOCX golden regression.
- Party-mode implementation review Round 2: unanimous GREEN after MH-1 (regenerate-goldens env-gate) + MH-2 (M-SF-2 promoted to 27-2.5 PDG binding).
- bmad-code-review layered pass: 82 findings → 15 PATCH applied (incl. 2 HIGH bugs: refinement key-order skip + primaries-only status derivation) + 19 DEFER logged + 48 DISMISS.
- Regression: **1149 passed / 2 skipped / 0 failed / 2 xfailed** (baseline 1106 → +43; above Murat's ≥1137 floor).
- Committed as `883f742` on `dev/epic-27-texas-intake`, pushed to origin.

### Phase 2 — Lesson Planner MVP Planning (four party-mode rounds)

Four-round party-mode deliberation on a new MVP vision for Marcus + Irene + Tracy + Lesson-Plan-driven production. Key evolution across rounds:

- **Round 1**: Initial MVP-shape debate. John wants minimal dict; Sally wants conversational pact; Winston wants durable artifact; Quinn wants provenance-tree root.
- **Round 2**: User ratified Sally's "Tuesday morning Maya" story verbatim — Lesson Plan born in Marcus-led conversation, Marcus stays SPOC + face, living pact not form.
- **Round 3**: User's expanded Step 4A vision — Irene produces Gagné-coherent outline + gaps; Maya iterates with Marcus; either can re-trigger Irene; locked plan has gaps → auto-dispatched to Tracy. Gagné as pluggable learning model. Multi-modal output first-class. Step 13 Quinn-R two-branch pre-composition check.
- **Round 4**: User's reframe — **Irene is the instructional designer** (formalizing what she already does, not training her up); she returns a **DIAGNOSIS, not an outline**; Maya's iteration moves are **scope decisions per event**, not outline edits.

**Key user ratifications:**
- **Marcus leads the 4A conversation** (Sally's Tuesday-morning story, verbatim quote-back from user).
- **Irene is attestor, not signatory** (Quinn's contract frame).
- **Blueprint catch-all** — anything APP can't produce is represented as a spec authored by Irene + writer; Quinn-R checks two-branch (real asset OR blueprint). Resolves the 1-vs-2-modalities question by adding blueprint as modality #2.
- **No spike** — user explicitly declined the proposed Friday spike ("I have greater confidence in the framework"). Goes straight to story authoring after plan review.
- **5-item MVP scope**: Tracy (embellish/corroborate/gap-fill) + Enhanced Irene (Gagné-diagnostic) + Enhanced Marcus (4A conversation) + Updated gates/contracts/validators + Step 4A landing + blueprint catch-all at step 13.

**Output:** Amelia's 19-story plan across 5 epics (~76 pts) at [_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md](_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md).

## Branch Metadata

- **Repository baseline branch**: `master`
- **Current working branch**: `dev/lesson-planner` (created 2026-04-18 from `dev/epic-27-texas-intake` @ `883f742`)
- **Prior work**: Story 27-2 committed on `dev/epic-27-texas-intake` (commit `883f742`, pushed). 27-2 BMAD-done.

## Unresolved Issues / Gotchas for the Next Session

1. **`bmad-session-protocol` skill not found in the skill registry** (attempted this session). Protocol docs live at `bmad-session-protocol-session-START.md` and `bmad-session-protocol-session-WRAPUP.md` at repo root — these are reference docs, not invokable skills. Session wrapup was executed manually against those docs.

2. **`dev/lesson-planner` branch is not merged to master**. Per session-wrapup §12, merge-to-master is default-skipped when a scoped checkpoint should stay isolated on the working branch. This session produced planning artifacts, not code; the planning-only commit stays on `dev/lesson-planner` until Epic 31 stories ship.

3. **27-2.5 Consensus adapter stays blocked** on the binding 27-2.5 Pre-Development Gate MUST-HAVE (CI 3x-run flake-detection gate must be wired before dev-story starts). Explicitly out of Lesson Planner MVP scope per user directive.

4. **Amelia's landmines** to verify during party-mode plan review:
   - **30-3 (4A conversation loop, 8pts)**: Amelia recommends pre-split into 30-3a (skeleton + lock) / 30-3b (dials + sync reassessment). Party should ratify or reject the split.
   - **28-1 Tracy charter**: MUST write down the three semantic definitions (embellish / corroborate / gap-fill) as operator-usable contract language — all three hit the same dispatcher, and if the distinction isn't codified the bridge will route incorrectly.
   - **R5 Marcus duality refactor**: don't combine refactor + feature work in the same story (30-1 is refactor-only; 30-2/3/4 add feature).

5. **Marcus-duality split**: Ratified in principle (two-agents-in-a-trenchcoat). John flagged it in round 2; Winston codified the split at plan-lock in round 3; Amelia's epic 30 breaks it into stories. Party should confirm the boundary still holds after plan-review pressure.

## Context Flags for Session-START

- **Cora §1a tripwire**: NOT fired (prior session clean). Default `since-handoff` scope fine for any opening `/harmonize`.
- **Story 27-2 is `done`** in sprint-status. No pending stories flipping to `done` in the next session's opening (story authoring only).
- **Epic 27**: no new stories (27-0/1/2 done; 27-2.5 blocked; 27-3+ deferred).
- **Epic 28**: 4 stories queued per Amelia's plan (28-1 through 28-4). Original Tracy spec superseded by 28-1 charter.
- **Epics 29, 30, 31, 32**: NEW per Amelia's plan; not yet formalized as sprint-status entries.
- **Test baseline**: 1149 passed / 2 skipped / 0 failed / 2 xfailed. Ruff clean.

## Critical-Path Reminder

When starting `bmad-create-story 31-1-lesson-plan-schema`, remember: **Epic 31 is the foundation**. Every other epic depends on 31-1/2/3 landing first. Don't start Epic 29 or 30 stories until Epic 31 foundation stories (31-1, 31-2, 31-3) are at minimum `ready-for-dev` with stable schemas.

Story 31-4 (blueprint-producer) and 31-5 (Quinn-R two-branch) can wait slightly longer — they land after Marcus + Irene stories are in-flight.
