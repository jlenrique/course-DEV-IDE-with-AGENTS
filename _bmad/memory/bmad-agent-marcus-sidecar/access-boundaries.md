# Marcus — Access Boundaries

## Read Access (both modes)

- Entire project repository (source, docs, configs, planning artifacts)
- `config/` — bootstrap content defaults (fallback; superseded by style bible)
- `state/config/` — mutable per-tool parameter preferences, course context, run presets
- `state/runtime/` — SQLite database (production runs, coordination, quality gates)
- `_bmad/memory/bmad-agent-marcus-sidecar/` — own sidecar (primary)
- `_bmad/memory/*-sidecar/` — other agent sidecars (read-only, coordination)
- `resources/style-bible/` — authoritative brand identity, visual design, voice/tone, accessibility
- `resources/exemplars/` — worked production patterns, platform allocation policies/matrices
- `resources/tool-inventory/` — tool access matrix and capability reference
- `course-content/` — all courses, staging, templates
- `BOX_DRIVE_PATH` (env var) — local filesystem reference materials
- Notion pages via `source-wrangling` skill (API read)

## Write Access (default mode)

- `state/config/style_guide.yaml` — learned tool parameter preferences
- `state/runtime/` — production run state, coordination records
- `_bmad/memory/bmad-agent-marcus-sidecar/` — own sidecar (all files)
- `course-content/staging/` — production drafts awaiting review
- `course-content/courses/` — only after explicit human approval at review gate
- Notion pages via `source-wrangling` skill (API write)
- **Never writes to**: `config/` (static defaults), `resources/style-bible/` (human-curated), `resources/exemplars/` (human-curated)

## Write Access (ad-hoc mode — strict subset)

- `course-content/staging/ad-hoc/` — scratch area only
- `_bmad/memory/bmad-agent-marcus-sidecar/index.md` — transient ad-hoc section only
- All other state writes suppressed

## Deny Zones (both modes — never write)

- `.env` — secrets
- `.cursor-plugin/plugin.json` — plugin manifest (infrastructure)
- `config/` — static project defaults
- `resources/` — human-curated reference libraries
- API client source code
- `tests/`
- Other agents' memory sidecars (read yes, write never)
