# Lesson Planner MVP — Ratification Preflight Flags

**Authored:** 2026-04-19 (during Story 32-4 close; immediately before
MVP-complete F4 party-mode green-light per
[lesson-planner-mvp-plan.md §6-F4](../planning-artifacts/lesson-planner-mvp-plan.md)).

**Purpose:** surface items to the human + party-mode panel BEFORE stamping
MVP-complete. Each flag names something the MVP-plan authors may have
implicitly assumed would be present at MVP close but that the landed
scope does not include. Not blockers — rather, things to say out loud so
the ratification is honest rather than implicit.

---

## Flag 1 — No rendered UX layer in MVP scope

**What's true:** Epics 28–32 land schema, log, specialists, harness, and
walkthrough scripts. None of them build a rendered user interface.

**Why this might surprise someone:** Sally's YELLOW pantomime AC on 32-4
reads as an experiential description ("Maya pastes source, sees weather
ribbon, clicks a gray card, Marcus proposes delegation, Maya types one
sentence, card turns gold"). A reader could reasonably infer that these
verbs map to a rendered UI by MVP close. They do not. The 32-4
walkthrough exercises the backend invariants a future UI must honor, not
the rendered layer itself.

**What landed instead:** UX *contracts* pinned at schema + validator +
grep-test level. Full list in
[deferred-work.md §MVP-deferred: rendered UX layer](deferred-work.md#mvp-deferred-rendered-ux-layer-cross-epic-no-owner-story).

**Ask for the ratification panel:**

1. Did Sally YELLOW-sign 32-4 expecting rendered UX by MVP close, or
   did she accept the "backend-faithfulness" framing? The current
   32-4 artifacts assume the latter.
2. Is a post-MVP `epic-33-ux-rendering-layer` (or equivalent) an
   accepted follow-on, or should MVP ratification block until a
   rendered shell lands?
3. If the ratification proceeds with "MVP = UX-ready backend, not
   UX", is that framing ratified explicitly so the retrospective
   and any external communication use the same words?

---

## Flag 2 — Sally §6-C Tuesday-morning experiential AC is currently
## runnable only at a terminal

**What's true:** §6-C requires an operator role-playing Maya to complete
one full 4A loop in under 12 minutes and articulate one sentence per
Declined card. 32-4 lands this as an automated walkthrough plus an
operator-runnable markdown script.

**Why this might surprise someone:** the phrase "role-playing Maya"
implies a UI to click through. The current MVP's operator test is: open
a terminal, run `run_maya_walkthrough(...)` against the canned fixture,
read the resulting JSON / `MayaWalkthroughResult`, mentally render the
ribbon, articulate Declined rationales aloud.

**What landed instead:** a 360-LOC walkthrough driver at
`marcus/orchestrator/maya_walkthrough.py`; a 7-section canned SME fixture
at `tests/fixtures/maya_walkthrough/sme_corpus/`; a human-runnable
markdown script at `_bmad-output/maps/maya-journey/maya-walkthrough.md`
whose preamble explicitly names the "backend-faithfulness, not UX"
framing.

**Ask for the ratification panel:**

1. Does §6-C pass for MVP if the operator has to read JSON, or does it
   require a rendered layer? The 32-4 walkthrough was built assuming
   the former.
2. Is there a stand-in rendered shell (even a minimal one) that should
   land before Sally runs the Tuesday-morning test for real?

---

## Flag 3 — "Card turns gold" is a UI rendering concern, not a schema
## mutation

**What's true:** the landed 4A loop (30-3a) + sync reassessment (30-3b)
do not auto-mutate `PlanUnit.weather_band` after Maya ratifies a scope
decision. The observable post-ratification state is
`scope_decision.state == "ratified"` + rationale stored verbatim.

**Why this might surprise someone:** Sally's AC literally says "card
turns gold". A code reader who expected this to mean a schema transition
(`gray → gold`) would be looking for mutation logic that does not exist.

**What landed instead:** `CardTurnedGoldEvidence.weather_band_observed`
is retained as an operator-debug observability field with no assertion
against it; the AC's semantic pin has been relocated to
`scope_decision.state` + `stored_rationale == operator input`.

**Ask for the ratification panel:**

1. Is the relocation of the AC semantic pin acceptable as-shipped, or
   does Sally want a schema-level `weather_band` transition added to
   a follow-on story?
2. If a follow-on story is warranted, does it sit in the post-MVP UX
   layer epic (where rendering + state-transition logic likely
   co-locate) or is it a foundation fix in Epic 31?

---

## Flag 4 — Stub-dials "coming soon" affordance is a Literal string
## with no operator-facing dial

**What's true:** 30-3a landed `StubDialsAffordance` as a frozen Pydantic
model with a `Literal["I'll learn to tune these next sprint."]` field.
The sentence is Marcus's one-voice rendering of "dials are coming".

**Why this might surprise someone:** "next sprint" in an operator-facing
string implies a commitment to deliver tunable dials in a near-term
follow-on. 30-3b landed dial tuning + sync reassessment — but only at
the `marcus/orchestrator/loop.py::tune_unit_dials` function level.
There is no operator-clickable dial.

**Ask for the ratification panel:**

1. Is the landed `tune_unit_dials` function sufficient to discharge
   the "next sprint" promise, or does Sally require a rendered dial
   control as a condition of MVP ratification?
2. If the sentence commits to a rendered control, should 30-3b's
   closure be revisited, or should the sentence be softened
   ("coming soon" → something less time-bound)?

---

## Flag 5 — MVP retrospectives are all `optional`

**What's true:** every epic retrospective (28, 29, 30, 31, 32) is marked
`optional` in sprint-status.yaml.

**Why this might matter:** MVP ratification without retrospectives risks
losing the lessons from a 22-story sprint. Several real pattern-level
findings surfaced during this cycle (the 2026-04-19 retroactive audit,
the false-closure of 30-3a, the phantom-module drift in 32-2, the
mid-dev AC-semantics discovery in 32-4). Those belong in durable
retrospective artifacts, not in commit messages.

**Ask for the ratification panel:**

1. Should one consolidated "Lesson Planner MVP retrospective" land
   before F4 green-light, even if the per-epic retrospectives stay
   optional?
2. The 2026-04-19 retroactive audit at
   [lesson-planner-mvp-retroactive-audit-2026-04-19.md](lesson-planner-mvp-retroactive-audit-2026-04-19.md)
   covers much of this ground — is that the retrospective, or a
   precursor to one?

---

## How to use this document at F4

1. Read each flag aloud at the start of the bmad-party-mode green-light
   round for MVP-complete.
2. For each flag, the panel either: (a) explicitly ratifies the
   as-shipped scope, (b) identifies a must-land item that blocks
   MVP close, or (c) adds the item to a post-MVP backlog with a
   named owner.
3. Record the verdict per flag in the F4 party-mode transcript.
4. If any flag blocks, surface to the human before proceeding.

This doc does not block MVP close by itself. It is the preflight
checklist that makes ratification explicit rather than implicit.
