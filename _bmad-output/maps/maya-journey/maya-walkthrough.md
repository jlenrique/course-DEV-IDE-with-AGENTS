# Maya Journey Walkthrough — Tuesday-Morning Script

This is a human-runnable walkthrough. You role-play Maya with a real 7-page
source. The goal is one full loop in under 12 minutes, ending with a locked
plan you can articulate aloud.

If something on this script doesn't match what you see on your screen,
that's the bug — stop and re-run from a clean session.

## What this walkthrough tests in the current MVP

**The MVP ships UX contracts, not rendered UX.** The current Lesson Planner
MVP (Epics 28–32) does not contain a built user interface. When you read
"paste", "click", "see the ribbon", or "card turns gold" below, you are
reading the **experience Maya will have once the UI layer lands**. Today,
this walkthrough exercises the backend substrate that the future UI layer
must faithfully render:

- You "paste" by invoking the source-load entry point in a terminal.
- You "see the ribbon" by inspecting `plan_unit.weather_band` on the
  returned plan.
- You "click a gray card" by selecting the gray unit by hand from the
  returned plan.
- The "card turns gold" by the plan unit carrying a ratified
  `scope_decision` with your rationale stored verbatim — **not** by a
  visible color change. The color change is a downstream UI-layer
  concern tracked in the post-MVP UX rendering backlog.

In other words: this walkthrough proves the backend is UX-faithful. It
does not prove Maya has had her experience — that arrives with the
rendered layer.

If you are observing this walkthrough for MVP ratification, your
"observation" is reading JSON / CLI output at a terminal. The invariants
you are verifying are rationale verbatim, band-closed-to-four-values,
one-voice discipline, and 12-minute elapsed budget.

## Before you start

- Open a fresh session (new log file, no partial state left over).
- Have your 7-page source ready. The canned fixture at
  [tests/fixtures/maya_walkthrough/sme_corpus/](../../../tests/fixtures/maya_walkthrough/sme_corpus/)
  stands in for a real source if you're running the automated version.
- Set a visible timer. You're aiming for under 12 minutes wall-clock.

## Stage 1 — Paste the source

What you do: paste the source into the paste box and press go.

What you should see: a confirmation that the source was accepted and
prepared. You should be able to keep working immediately — no long wait,
no error banner.

"Looks wrong" tells: a raw exception surfaced; an internal programming
name surfaced in a user-facing message; the confirmation took longer
than a few seconds.
→ re-run from a clean session.

## Stage 2 — See the weather ribbon

What you see: a ribbon of colored cards, one per plan unit. The colors
are gold, green, amber, and gray. No red — ever.

- **Gold** — you've got this cold (source fully covers it).
- **Green** — we're in step (source covers it well).
- **Amber** — your call (source is partial; you decide).
- **Gray** — Marcus leans in more (he wants to propose something).

"Looks wrong" tells: any red card; a band you don't recognize; the
ribbon is empty. → re-run from a clean session.

## Stage 3 — Click a gray card

What you do: click on any gray card. It's the signal that Marcus wants
to help with that unit specifically.

What you should see: the card opens and shows Marcus's diagnosis — one
short sentence naming what he thinks the unit needs.

"Looks wrong" tells: the diagnosis references internal tooling by
programming-layer name or is an apology instead of a diagnosis.
→ re-run from a clean session.

## Stage 4 — Marcus proposes delegation

What you see: one sentence from Marcus naming a research posture he can
lean into. The three postures are:

- **I found a detail that enriches this section, and I can weave it in
  if you want?** (embellish)
- **I found evidence that supports it for this claim, and I can anchor
  that nuance here if you want?** (corroborate — supporting)
- **I found source material that fills the missing background here,
  and I can fold it in if you want?** (gap-fill)

The sentence ends with a question — Marcus is handing the move back to
you. That's the contract.

"Looks wrong" tells: the sentence is a statement, not a question; the
sentence uses "we" or "Marcus will" instead of "I"; the sentence
references internal tooling. → re-run from a clean session.

## Stage 5 — Type one sentence

What you do: type one sentence describing why this unit matters the
way you're scoping it. Your exact words, verbatim. Marcus stores them
as-is — no rephrasing, no cleanup, no enum.

Example from the canned fixture:

> I want students to feel like they've earned the moment of realization,
> not had it handed to them.

"Looks wrong" tells: Marcus repeats back a cleaned-up version of your
sentence; the confirmation truncates your words; an enum or category
label appears where your sentence should be. → re-run from a clean
session.

## Stage 6 — Card ratifies with your sentence attached

What you see: the card settles into its decided state. Your sentence is
stored on that card exactly as you typed it. When the plan locks, the
card's scope is sealed with your reasoning attached.

(In the current MVP the card's color doesn't auto-refresh to gold —
that's a downstream UI rendering concern. The contract that matters is
your sentence stored verbatim on the ratified decision.)

"Looks wrong" tells: your sentence doesn't appear on the decided card;
the card stays in an unsettled state; a decision landed but has no
rationale. → re-run from a clean session.

## After the loop — read back

For every card you declined, read your sentence aloud. If you cannot
finish the thought in one breath — the stored rationale isn't a
verbatim capture of what you meant. That's the contract leaking.

Stop your timer. If you came in under 12 minutes, the experiential
contract held.

## If you need to re-run

Delete the session log; reload the canned fixture; start at stage 1.
Each stage is designed to be re-enterable from a clean bundle.
