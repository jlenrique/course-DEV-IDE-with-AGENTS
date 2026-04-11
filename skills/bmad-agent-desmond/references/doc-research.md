# Capability — Descript doc & API surface refresh

## Outcome

Keep **local, citeable snapshots** of Descript help and (optionally) developer/API material so assembly instructions do not rely on model cutoff or vague memory.

## Procedure (deterministic + judgment)

1. Edit `references/descript-doc-registry.json`: set `"enabled": true` only for URLs your team trusts (official Descript domains preferred). Add stable `id` slugs.
2. From repo root, run:
   ```text
   python skills/bmad-agent-desmond/scripts/refresh_descript_reference.py
   ```
   Optional: `--dry-run` to list targets without fetching.
3. Review new files under `references/cache/` — they are **scraped text/HTML snapshots** for RAG-style reading, not legal redistribution. Prefer short excerpts in instructions; link out for readers when publishing runbooks externally.
4. Update `MEMORY.md` with **fetched_at** date and **Descript version** the team is targeting this month.

## API vs UI

- **UI assembly** is the default for this pipeline (human Descript editor).
- If the team uses **API** or **batch** workflows, add those doc URLs to the registry in a separate section and reflect capabilities in instructions **only** when confirmed by cache content.

## Headless mode

When invoked with `--headless`, perform steps 2–4 and exit with a short summary suitable for logs.

## After the session

Log which sources were enabled and any 403/redirect issues (site structure changes).
