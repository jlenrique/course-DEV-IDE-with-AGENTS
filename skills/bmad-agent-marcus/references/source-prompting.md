# Source Material Prompting

## Purpose

Marcus proactively offers to pull course development notes and reference materials before production tasks begin. Context enrichment before creation beats revision after.

## When to Offer

Before starting any content production task, assess whether source materials would improve the output:

- **New lesson creation** — Offer to pull Notion course development notes for the relevant module/lesson
- **Content revision** — Offer to check Box Drive for updated reference materials
- **Assessment creation** — Offer to pull learning objectives and competency frameworks from Notion
- **Case study development** — Offer to check for existing clinical case references

## Source Channels

### Notion (via `source-wrangler` skill + `NotionClient`)
- Course development notes and planning documents
- Learning objective mappings
- Faculty content submissions and feedback
- Readiness assessments

### Box Drive (via `source-wrangler` skill — local filesystem)
- Reference materials, textbook excerpts, journal articles
- Previously created content for reuse or revision
- Institutional templates and guidelines
- Media assets (images, diagrams)

### Local PDFs (via `source-wrangler`)
- SME module notes (e.g. under `course-content/courses/`) — use `wrangle_local_pdf()` then `write_source_bundle()`
- Before a trial run, ensure expected paths exist (`require_local_source_files`) so missing files surface immediately

### Web exemplars (Playwright MCP + `source-wrangler`)
- User or Cursor session captures a page (save HTML) or provides a URL
- Skill extracts readable text, stores `extracted.md` + `metadata.json` under a staging bundle path
- Marcus passes `extracted.md` paths into Irene/Gary envelopes as `user_constraints` / `input_text` supplements

### Gamma exemplar links
- **Not** plain HTTP fetch: `gamma.app/docs/...` is blocked in source-wrangler by design
- Route through **Gary** (export) or Playwright HTML capture, then ingest with the skill — same bundle contract as other sources

## Prompting Style

Natural, not mechanical. Examples:
- "Before we build slides for the cardiac assessment lesson — do you have Notion notes on learning objectives for this module? I can pull them to make sure we're aligned from the start."
- "I see there's a Box Drive reference folder for Pharmacology. Want me to check for anything relevant before we draft?"
- "Last time we built a case study, the Notion feedback was really useful for getting the clinical scenario right. Should I pull the latest notes?"

## Integration with Production Planning

When source materials are retrieved, Marcus incorporates them into the specialist context envelope — they become part of the context passed to content-creator, quality-reviewer, and other specialists who need domain grounding.
