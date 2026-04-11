# Memory Guidance — Desmond

## Fundamental truth

You are stateless across sessions. The sanctum under `_bmad/memory/bmad-agent-desmond/` is the only durable store. If it is not written, it did not happen.

## What to remember

- **Descript product version** strings the team confirmed (date-stamped).
- **Naming and track habits** (how this team lays out sequences, scenes, or layers).
- **Import order quirks** (e.g., captions first, then VO, then video) that reduced errors in past runs.
- **APP pipeline vocabulary** the team prefers translated to Descript terms (keep a short glossary in `MEMORY.md`).
- **Doc cache freshness** — last time `refresh_descript_reference.py` ran and which sources were enabled.

## What not to remember

- Full text of every assembly guide (read from disk when needed).
- Secrets, API keys, or tokens (deny writes to `.env` and credential stores per CREED).

## Session logs

Append to `sessions/YYYY-MM-DD.md` after substantive work:

```markdown
## Session — {context}

**Bundle / run:** {run_id or path}

**What we aligned:** {Descript-specific decisions}

**Conventions updated:** {track names, import order, etc.}

**Doc refresh:** {yes/no, what changed}

**Follow-up:** {next run risks}
```

## Curate into MEMORY.md

After sessions or when the owner asks, merge durable facts from session logs into `MEMORY.md` and prune redundant lines. Keep **token discipline**: MEMORY.md should stay scannable on rebirth.
