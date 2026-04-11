# Automation Advisory — required output

Every Desmond response that gives **Descript operator guidance** for an **APP assembly handoff** (final edit path toward publish) MUST end with a section titled exactly:

## Automation Advisory

This section is **not optional**. It summarizes **what could be scripted or assisted** vs **what stays manual**, using the **current** Descript surfaces below. When uncertain, say so and point to `references/cache/` or [docs.descriptapi.com](https://docs.descriptapi.com/) refresh.

## Automation channels (terminology)

| Channel | What it is |
|--------|------------|
| **REST API** | `https://descriptapi.com/v1` — Bearer token; async **jobs**; see OpenAPI. |
| **Remote MCP** | `https://api.descript.com/v2/mcp` — assistant/connector flow; overlaps API capabilities for natural-language driven tasks. |
| **CLI** | Descript CLI (documented under API docs *Using the CLI*); wraps common API flows from the terminal. |
| **App (manual)** | Descript desktop/web UI — required where API/export coverage is incomplete or for fine timeline work. |

## APP finishing tasks to classify (always scan the bundle)

Map these to **Full**, **Partial**, or **Manual (app)** for automation, and note **REST** vs **MCP** vs **CLI** where relevant:

1. **Project + asset ingest** — Bring narration MP3s, VTTs, still PNGs, motion MP4s into a composition in order.
2. **Timeline assembly** — Segment order, durations, transitions, holds; motion vs still handling.
3. **Caption alignment** — Import VTT, adjust timing if drifted vs audio.
4. **Audio finishing** — Ducking, levels, room tone; policy-driven.
5. **Visual finishing** — Motion/narration length mismatch resolution (hold, loop, cover — editorial).
6. **Review / QC** — Spot-check against manifest intent before export.
7. **Export / publish** — Render master, captions sidecar or burn-in, handoff to LMS or hosting.

## Default expectations (ground truth until docs prove otherwise)

- **REST:** Strong on **creating projects**, **importing media**, **agent/Underlord-style edit jobs**, **job polling** (`/jobs/...`, `/status`). Treat **export/publish** as **verify in docs** — Descript has historically limited **fully automated export**; often **manual in app** for final masters.
- **MCP:** Good for **orchestrating** the same families via an assistant (imports, edits) with **login/connector**; not a substitute for reading current MCP tool list.
- **Manual:** Fine **timeline** tweaks, **final export** packaging, and any step **not** exposed or stable in the API you have cached.

## Output format (use this structure)

```markdown
## Automation Advisory

**REST API (`descriptapi.com/v1`):**
- *Task* — Full | Partial | Manual — one line why.

**MCP (`api.descript.com/v2/mcp`):**
- *Task* — Full | Partial | Manual — one line why (overlap vs REST or conversational ops).

**CLI:** (if applicable)
- *Task* — …

**Manual / app:** (required line items for gaps)
- …

**Notes:** API beta / changing surface; re-run `refresh_descript_reference.py` if behaviors shift.
```

Keep the advisory **honest**: **Partial** is often the right call for steps that mix API import with human trimming.
