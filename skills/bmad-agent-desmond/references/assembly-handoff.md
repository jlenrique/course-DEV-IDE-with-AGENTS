# Capability — Assembly handoff (APP → Descript)

## Outcome

Given a completed **`assembly-bundle/`** from the APP pipeline, produce **operator instructions a human can follow in Descript** that match the **intended final lesson**: segment order, narration integrity, caption alignment, still vs motion roles, and behavioral intent from the manifest/guide.

## Inputs to request or locate

- `assembly-bundle/segment-manifest.yaml`
- `assembly-bundle/DESCRIPT-ASSEMBLY-GUIDE.md` (compositor baseline)
- `audio/`, `captions/`, `visuals/`, `motion/` as present
- Team conventions from sanctum `MEMORY.md` / `BOND.md`
- Latest **Descript-relevant** notes from `references/cache/` (after doc refresh)

## What success looks like

- **Automation Advisory (mandatory):** Follow `references/automation-advisory.md` and always include a final **`## Automation Advisory`** section classifying APP finishing/publish tasks vs **REST API**, **MCP**, **CLI**, and **manual app** work.
- Instructions use **Descript product vocabulary** (sequences, scenes, timeline, tracks, layers — whichever matches the **documented** current UI in your cache and the owner’s stated version).
- Each segment lists **import targets** and **sync intent** without inventing new script or B-roll.
- **Motion segments:** explicit split between **playback clip** and **still/poster** reference; call out when duration differs from narration and how the team **finishes** that (hold, loop policy, cover frame — per owner policy, not generic filler).
- **Static segments:** single still held for narration duration unless guide says otherwise.
- A short **preflight checklist** the editor runs before export (captions, loudness intent, chapter markers if used).
- **No new creative:** if the editor needs a change that alters pedagogy or wording, stop and route back to production governance — document the gap instead of improvising.

## Memory integration

Merge any newly observed team preference into `BOND.md` or `MEMORY.md` after the owner confirms.

## After the session

Append session log; note if compositor guide sections were insufficient and why (feeds compositor improvements separately).
