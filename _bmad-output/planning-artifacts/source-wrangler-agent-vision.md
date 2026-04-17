# Source Wrangler → Full Agent: Strategic Vision

> Captured: 2026-04-15 (closeout session). Not yet scheduled.

## Current State

`skills/source-wrangler/` is a **skill** (not an agent). Marcus invokes it. It handles:

- Local PDFs via pypdf (text-native only; scanned/OCR out of scope)
- Notion pages via REST API
- Box Drive local files
- HTTP URL fetch + HTML-to-text
- Playwright-saved HTML → clean text

Output: `extracted.md` + `metadata.json` bundle. No intelligence about optimal extraction strategy per source type.

## Problem Statement

The 2026-04-15 trial run produced a **30-line extracted.md from a 24-page PDF** — a catastrophic extraction failure that passed the quality gate. The current skill has no concept of "is this extraction adequate for this source type?" and no ability to choose alternative extraction pathways.

As APP grows, source diversity will increase: PDFs with complex layouts, PPTX decks, Notion databases, web-scraped pages, video transcripts, spreadsheets, etc. A skill that does one thing per source type won't scale.

## Vision: Trainable Source Wrangler Agent

### Core Concept

Transform source content into its **most digestible format** given the attributes of the source. The agent selects the optimal extraction strategy from a transformation matrix, executes it, and validates the result.

### Transformation Matrix

A decision table mapping source attributes → optimal extraction pathway:

| Source Type | Attributes | Optimal Transformation | Rationale |
|---|---|---|---|
| PDF (text-native, simple layout) | Single-column, no tables | pypdf direct extraction | Fast, lossless |
| PDF (text-native, complex layout) | Multi-column, tables, sidebars | Export → DOCX via LibreOffice/pdf2docx, then extract | Preserves structure |
| PDF (scanned/image) | No selectable text | OCR pipeline (Tesseract/Azure Doc Intelligence) | Only path |
| PDF (mixed text+image) | Some pages text, some scanned | Hybrid: pypdf for text pages, OCR for image pages | Best of both |
| PPTX (slide deck) | Slides with speaker notes | Export as individual slide PNGs + notes extraction | Per-slide granularity |
| PPTX (data-heavy) | Tables, charts embedded | Export → individual CSVs + slide images | Structured data preserved |
| Notion page | Rich text, databases | Notion MCP → structured markdown | Native API fidelity |
| Notion database | Tabular data | Notion MCP → CSV/structured format | Query-friendly |
| Web page (static) | Simple HTML | URL fetch + readability extraction | Lightweight |
| Web page (JS-rendered) | SPA, dynamic content | Playwright MCP → saved HTML → extraction | Handles JS rendering |
| Web page (auth-walled) | Login required | Playwright MCP with session → saved HTML | Handles auth |
| Google Docs/Sheets | Cloud-hosted | Export API → DOCX/XLSX → extraction | Avoids scraping |
| Video transcript | SRT/VTT/plain | Direct text extraction + timestamp preservation | Timeline-aware |
| Spreadsheet (XLSX) | Tabular data | pandas/openpyxl → structured markdown tables | Data fidelity |
| Image (diagram/infographic) | Visual content | Vision API → structured description | Multimodal |

### Concrete Example: C1-M1 Tejal PDF

The APC C1-M1 Tejal source PDF is actually a **Notion export**. The current wrangler extracted it via pypdf and produced a 30-line stub. A smarter agent would:

1. **Detect provenance** — recognize the PDF is a Notion export (layout cues, metadata, or operator declaration)
2. **Cross-validate** — pull the same content directly from Notion via MCP/API and compare word counts
3. **Choose the better pathway** — if the Notion pull yields richer structured markdown than pypdf on the export, prefer it (or merge both)
4. **Record the delta** — log that pypdf produced N words vs. Notion API produced M words, flag which was authoritative

This pattern generalizes: any time a source has a known upstream (Notion page → PDF export, Google Doc → PDF export, PPTX → PDF export), the agent should consider pulling from the upstream directly.

### Key Capabilities

1. **Source profiling** — Analyze source attributes before choosing extraction pathway. Page count, file size, text-layer presence, layout complexity, embedded media. When the operator declares that a PDF is an export from Notion/Google/etc., the profiler should flag the upstream as an alternative extraction pathway.

2. **Pathway selection** — Consult the transformation matrix to pick the optimal extraction strategy. Fall back to simpler strategies if the optimal one fails.

3. **Multi-pathway extraction** — Some sources benefit from parallel extraction (e.g., PDF text extraction + image extraction for diagrams). Agent should orchestrate multiple passes.

4. **Extraction validation** — Built-in completeness checks (word count vs. expected, section count vs. ToC, structural integrity). The 30-line stub failure must never recur.

5. **MCP integration** — First-class pathways for:
   - **Playwright MCP** — web scraping, JS-rendered pages, auth-walled content
   - **Notion MCP** — page retrieval, database queries, content manipulation
   - Future MCPs as they become available

6. **Trainability** — Record extraction outcomes (success/failure, quality scores, pathway chosen) in a learning log. Over time, the agent refines its pathway selection heuristics based on what worked for similar source profiles.

7. **Provenance chain** — Every transformation step is recorded: source → intermediate format → final extraction. Downstream agents and Vera gates can audit the full chain.

### Architecture Sketch

```
Source Wrangler Agent
├── Source Profiler (analyze attributes)
├── Transformation Matrix (pathway selection)
├── Extraction Engines
│   ├── pypdf (text-native PDF)
│   ├── pdf2docx / LibreOffice (complex PDF)
│   ├── OCR pipeline (scanned PDF)
│   ├── python-pptx (PPTX)
│   ├── Playwright MCP (web)
│   ├── Notion MCP (Notion)
│   ├── openpyxl/pandas (spreadsheets)
│   └── Vision API (images/diagrams)
├── Extraction Validator (completeness + quality)
├── Bundle Writer (extracted.md + metadata.json)
└── Learning Log (pathway outcomes for training)
```

### Migration Path from Current Skill

1. **Phase 1:** Keep current skill, add extraction validation (DONE — Prompt 3 now has word-count completeness check)
2. **Phase 2:** Add source profiler and transformation matrix as reference data
3. **Phase 3:** Refactor skill into agent with SKILL.md → agent persona + specialist dispatch
4. **Phase 4:** Add MCP integrations (Playwright, Notion) as first-class pathways
5. **Phase 5:** Add learning log and trainability

### Non-Trivial Considerations

- **Security:** MCP integrations handle credentials; must follow existing .env patterns, never log secrets
- **Performance:** Some transformations (OCR, LibreOffice export) are slow; need timeout and progress reporting
- **Fallback chains:** If optimal pathway fails, agent should try the next-best option automatically
- **Bundle format:** Current bundle-format.md may need extension for multi-pass extractions (e.g., text + images + tables as separate sections)
- **Operator control:** Operator should be able to override the matrix recommendation ("use OCR even though text layer exists" for known bad text layers)

## References

- Current skill: `skills/source-wrangler/SKILL.md`
- Bundle format: `skills/source-wrangler/references/bundle-format.md`
- Notion client: `scripts/api_clients/notion_client.py`
- Extraction operations: `skills/source-wrangler/scripts/source_wrangler_operations.py`
- Prompt 3 completeness check: added 2026-04-15 (v4.2 prompt pack)
- Trial run failure: `run-records/run-record-2026-04-15T20-56-55.md`
