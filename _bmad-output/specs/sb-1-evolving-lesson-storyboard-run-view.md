# Story SB.1: Evolving lesson storyboard (run view)

**Epic:** SB — Storyboard & run visualization *(new; Marcus-owned)*  
**Status:** done  
**Sprint key:** `sb-1-evolving-lesson-storyboard-run-view`  
**Added:** 2026-03-31  
**Depends on:** Storyboard v1 complete (`spec-storyboard-gary-marcus-review.md` — `generate-storyboard.py`, `write-authorized-storyboard.py`, Marcus `SB` capability)

## Summary

Extend the storyboard from a **one-time post-Gary HIL artifact** into an **on-demand “alternative look into a run”**: Marcus can regenerate an updated view **at any time** as the lesson matures. Rows progress from **slides only** → **slide + script** (and other columns) as Irene and downstream stages produce artifacts. The storyboard becomes a **spine for the whole lesson design**, including **links to non-presentation assets** (video, audio, interactives, source docs) as the APP stages them.

## Problem

Operators need a **single scannable index** of “where this run stands” that is not locked to the moment Gamma finishes. Today’s v1 bundle is the right foundation but is **Gary-dispatch-shaped only**. Without an evolving manifest and regen path, Marcus cannot answer “show me the current storyboard” consistently as narration, audio, and other assets appear.

## Product intent (vision)

1. **On-demand refresh:** The operator asks Marcus for an **updated storyboard**; Marcus (via tooling) **rebuilds** HTML + JSON from **current run state**, not from stale copies.
2. **Progressive richness:** Rows show what exists: **pending / N/A** where something is not yet produced (same honesty as v1 **MISSING** for assets).
3. **Slide + script layout:** When Pass 2 narration exists, each row (or an expandable section) can show **visual + script text** (PPTX-notes mental model), still **view-only** in the browser unless a later story explicitly adds interaction.
4. **Multi-asset lesson design:** As the APP creates **non-slide** assets, the storyboard lists **stable links** (paths, URLs, run-scoped IDs) so the run view stays the **orchestration dashboard** for the lesson, not only a deck preview.
5. **Ownership unchanged:** **Marcus** remains the sole owner of storyboard **generation and operator-facing narrative**; specialists produce inputs; validators may **consume** authorized snapshots (separate stories).

## Architecture principles (non-negotiable)

| Principle | Meaning |
|-----------|---------|
| **Manifest is law for machines** | One structured JSON (versioned) is the source of truth for ordering, ids, stages, and links. |
| **HTML is a projection** | `index.html` (or paged HTML) is always derived from the manifest; no hand-edited HTML as authority. |
| **Deterministic regen** | “Updated storyboard” means **re-running a generator** over known inputs, not Marcus paraphrasing from memory. |
| **Authorization is explicit** | v1 **authorized slide snapshot** remains the gate where “only these slides for this run” matters; informational rows (e.g. planned B-roll) may use lighter status semantics. |
| **Extensible rows** | Support `artifact_class` (e.g. `slide`, `segment`, `video`, `interactive`, `source`) and `stage` (`planned`, `generated`, `authorized`, …) so the same table pattern scales. |

## Non-goals (this story — scoping boundary)

- Replacing production coordination DB or run reporting as the system of record.
- Building ElevenLabs/Canvas **inside** the HTML storyboard (links only at this vision layer).
- Mandatory enforcement in `validate-irene-pass2-handoff.py` until a follow-on story explicitly wires **authorized** + **extended** manifest (may remain Ask First).

## Phased increments (recommended order)

| Phase | Deliverable | Outcome |
|-------|-------------|---------|
| **P0** | **Regen contract** | Document + implement “inputs directory layout” or run manifest pointer Marcus uses to rebuild storyboard idempotently. |
| **P1** | **Irene script column** | Merge narration segment text (or path) into manifest rows when Pass 2 artifact exists; second HTML template or extra columns. |
| **P2** | **Lifecycle fields** | `artifact_class`, `stage`, `not_before_gate` in schema; show **Pending** in UI. |
| **P3** | **Linked assets** | Columns or nested `related_assets[]` for video/audio/interactive/source links with type labels. |
| **P4** | **Optional theming** | Print-friendly / “inspection mode” density; still no approval buttons unless product asks. |

Each phase should ship with **pytest** on manifest merge logic and a **fixture run folder** in tests.

## Acceptance criteria (traceable)

| # | Criterion |
|---|-----------|
| AC1 | Operator-facing doc (Marcus `SKILL.md` or `references/`) states that an **updated storyboard** is produced by **regenerating** from current artifacts, not by editing the previous HTML. |
| AC2 | Extended manifest schema is **versioned** (`storyboard_version` or new key); v1 consumers fail closed or ignore unknown fields predictably. |
| AC3 | When Pass 2 script text (or agreed path) is present, regenerated HTML shows **slide + script** for applicable rows (layout agreed in implementation — table column vs notes row). |
| AC4 | Rows can represent **non-slide** assets with at least **label + link + type** without breaking existing slide rows. |
| AC5 | `pytest` covers merge/regression: Gary-only → +Irene → +extra asset link (fixture chain). |
| AC6 | **Marcus** remains documented owner; no new specialist registry entry for “storyboard” as a delegate. |

## Suggested implementation tasks (unchecked — for when story moves to ready-for-dev)

- [ ] Specify **run bundle layout** or **run index file** that lists paths to: Gary dispatch, Irene Pass 2 output, optional asset manifest.
- [ ] Extend or wrap `generate-storyboard.py` with a **merge** step (or new `build-run-storyboard.py`) that ingests multiple sources into one manifest.
- [ ] HTML template variants or column config driven by manifest `columns_active[]`.
- [ ] Update `skills/bmad-agent-marcus/SKILL.md` (`SB` section) with “refresh storyboard” operator flow.
- [ ] Follow-on story (optional): wire `validate-irene-pass2-handoff.py` to prefer `authorized-storyboard.json` + extended manifest when present.

## References

- `_bmad-output/implementation-artifacts/spec-storyboard-gary-marcus-review.md` — v1 spec (done).
- `skills/bmad-agent-marcus/scripts/generate-storyboard.py`, `write-authorized-storyboard.py`
- `skills/bmad-agent-marcus/SKILL.md` — **SB** capability and ownership.
- `skills/gamma-api-mastery/scripts/gamma_operations.py` — `gary_slide_output` contract.
- `skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py`, `validate-irene-pass2-handoff.py` — gate context.

## Dev Agent Record

Implementation followed the spec-driven approach in `spec-sb-1-storyboard-run-view-refresh.md` (status: done) and earlier storyboard v1 spec `spec-storyboard-gary-marcus-review.md`. The suggested implementation tasks above were planning-phase guidance; actual delivery was tracked via the spec's execution tasks and acceptance criteria.

### File List

- `skills/bmad-agent-marcus/scripts/generate-storyboard.py` — manifest builder, HTML projection, CLI (generate + summarize), segment-manifest merge, related-assets support, `--run-id` traceability
- `skills/bmad-agent-marcus/scripts/write-authorized-storyboard.py` — authorized slide snapshot writer
- `skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py` — 14 tests (v1 regression, Pass 2 narration, related assets, CLI, run-id, literal visuals)
- `skills/bmad-agent-marcus/SKILL.md` — SB capability, operator refresh flow, related-assets input documented
- `_bmad-output/implementation-artifacts/spec-sb-1-storyboard-run-view-refresh.md` — implementation spec (done)
- `_bmad-output/implementation-artifacts/spec-storyboard-gary-marcus-review.md` — v1 spec (done)

### Change Log

- 2026-04-01: v1 storyboard (Gary dispatch → HTML + authorized snapshot) — commit `48b70ce`
- 2026-04-01: Pass 2 slide+narration via optional segment manifest — commit `311ae15`
- 2026-04-02: SB.1 related-asset rows, spec, SKILL.md update — commit `26afb8e`
- 2026-04-02: Storyboard hardening, validators, session wrapup — commit `4a475ce`
- 2026-04-02: `--run-id` CLI argument wired for manifest traceability, 14/14 tests green
