# Story 2A-5: G0-G1 Fidelity — Source Bundle & Lesson Plan Verification

Status: review

## Story

As a course content producer,
I want the Fidelity Assessor to verify source bundle extraction completeness (G0) and lesson plan faithfulness to the source material (G1),
So that the entire downstream pipeline inherits a faithful baseline from the very first step.

## Background & Motivation

Story 2A-4 created Vera (Fidelity Assessor) with G2-G3 coverage. This story extends Vera upstream to the earliest pipeline gates. G0 ensures source material is faithfully extracted before any content creation begins. G1 ensures the lesson plan (Irene's first output) is faithful to the extracted source. Together, these gates establish the baseline that all downstream fidelity checks depend on.

**Key architectural point:** G0 is the only gate where the original source materials may not be fully machine-readable (scanned PDFs). The `degraded_source` warning protocol handles this gracefully — the human is informed so they can provide alternatives before the pipeline proceeds on an incomplete baseline.

## Acceptance Criteria

### G0 (Source Bundle vs. Original SME Materials)

1. Vera evaluates G0 by loading the source bundle (`extracted.md` + `metadata.json`) and comparing against available source material metadata
2. Section coverage check: all major sections/headings from source material appear in `extracted.md` (G0-01)
3. Media capture: `metadata.json` contains `media_references[]` for images/diagrams/tables (G0-02)
4. Metadata completeness: provenance entries have valid `kind`, `ref`, `fetched_at` (G0-03)
5. No content invention: `extracted.md` contains only traceable content (G0-04)
6. Degraded source detection: PDF sources checked for scanned pages via PDF sensory bridge, flagged with `degraded_source` warning (G0-05)
7. O/I/A findings reported to Marcus with extraction confidence score

### G1 (Lesson Plan vs. Source Bundle)

8. Vera evaluates G1 by loading the lesson plan and comparing against the source bundle
9. Source theme coverage: every major theme in `extracted.md` is represented by at least one LO (G1-01)
10. LO structure: each LO has Bloom's level, traces to content blocks (G1-02)
11. Content block completeness: required fields populated (G1-03)
12. Assessment alignment: all LOs covered by assessment hooks (G1-04)
13. No orphaned content: every block traces to an LO (G1-05)
14. No content invention: no clinical/factual claims absent from source (G1-06)
15. `source_ref` links validated — cited sections exist in `extracted.md`

### Marcus Integration

16. Marcus delegation flow updated: Vera invoked at G0 (after source wrangling) and G1 (after Irene Pass 1 lesson plan, before G2)
17. G0 failures route back to source wrangler for re-extraction
18. G1 failures route back to Irene for revision

### Vera Updates

19. SKILL.md gate coverage table updated: G0 and G1 marked as "Active"
20. Gate evaluation protocol updated with G0 and G1 evaluation steps, including PDF bridge invocation for G0-05

### Interaction Tests

21. Interaction test guide updated with G0 and G1 scenarios (clean pass, omission, invention, degraded source)

## Tasks / Subtasks

- [x] Task 1: Extend gate evaluation protocol for G0 (AC: #1-#7, #20)
  - [x] 1.1 Added G0 evaluation steps to `references/gate-evaluation-protocol.md` — loading `extracted.md` + `metadata.json`, section coverage, provenance, PDF bridge for degraded detection
  - [x] 1.2 All 5 G0 L1 criteria documented: G0-01, G0-04 (agentic), G0-02, G0-03, G0-05 (deterministic, G0-05 perception-required via PDF bridge)

- [x] Task 2: Extend gate evaluation protocol for G1 (AC: #8-#15, #20)
  - [x] 2.1 Added G1 evaluation steps — loading lesson plan, source bundle, LO-to-theme cross-referencing, structure checks, source_ref validation
  - [x] 2.2 All 6 G1 L1 criteria documented: G1-01, G1-06 (agentic), G1-02, G1-03, G1-04, G1-05 (deterministic)

- [x] Task 3: Update Vera SKILL.md (AC: #19)
  - [x] 3.1 G0 and G1 changed to "Active" in gate coverage table with perception notes

- [x] Task 4: Update Marcus delegation flow (AC: #16, #17, #18)
  - [x] 4.1 Inserted Vera at G0 (after source wrangler) and G1 (after Irene P1, before G2) in pipeline dependency graph
  - [x] 4.2 Added G0/G1 fields to Fidelity Assessor envelope spec (bundle_dir, source_materials, lesson_plan)
  - [x] 4.3 Updated Marcus specialist registry: 4 Vera entries now (G0, G1, G2, G3)

- [x] Task 5: Update interaction tests (AC: #21)
  - [x] 5.1 Added 8 scenarios (13-20): G0 clean pass, G0 section omission, G0 degraded source (scanned PDF), G0 content invention, G1 clean pass, G1 theme omission, G1 orphaned content, G1 assessment gap

- [x] Task 6: Validate and complete
  - [x] 6.1 `validate_fidelity_contracts.py` — 7 contracts valid, 38 criteria, 0 errors, parity check PASS
  - [x] 6.2 131 tests pass, 2 known pre-existing failures, 3 skipped — no regressions
  - [x] 6.3 All G0 (5) and G1 (6) criteria addressed in gate evaluation protocol
  - [x] 6.4 Update sprint-status.yaml

## Dev Notes

### G0 is unique — source comparison without full originals

Unlike other gates where Vera has both source and output as text, G0's source of truth is the *original* SME materials which may be:
- Notion pages (fetched via API — full text available)
- Box Drive files (local filesystem — readable)
- PDFs (machine-readable or scanned — PDF bridge required for quality check)
- URLs/HTML (Playwright-saved — text available)

Vera cannot always read the originals directly. The evaluation strategy at G0 is **structural comparison**: verify that `extracted.md` has the expected sections, that `metadata.json` tracks all sources, and that no content was invented during extraction. Full content comparison (is every sentence from the original in the extraction?) is L2 agentic and will improve with model capability.

### PDF Bridge Invocation at G0

G0-05 is the only criterion requiring perception at G0. When source materials include PDFs:
1. Check `metadata.json` provenance entries for `kind: local_pdf`
2. For each PDF source, invoke the PDF bridge: `perceive(pdf_path, "pdf", "G0", "fidelity-assessor")`
3. Check the response's `pages[].is_scanned` flags
4. If any pages are scanned: emit `degraded_source` warning with affected page numbers
5. Surface to Marcus so human can provide manual transcription or alternatives

### Existing Components to Reuse

| Component | Location | Reuse |
|-----------|----------|-------|
| Vera agent | `skills/bmad-agent-fidelity-assessor/SKILL.md` | Extend gate coverage |
| Gate evaluation protocol | `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md` | Add G0/G1 sections |
| Fidelity Trace Report | `skills/bmad-agent-fidelity-assessor/references/fidelity-trace-report.md` | Same format, already gate-agnostic |
| G0 L1 contract | `state/config/fidelity-contracts/g0-source-bundle.yaml` | 5 criteria |
| G1 L1 contract | `state/config/fidelity-contracts/g1-lesson-plan.yaml` | 6 criteria |
| PDF bridge | `skills/sensory-bridges/scripts/pdf_to_agent.py` | G0-05 scanned PDF detection |
| Bundle format | `skills/source-wrangler/references/bundle-format.md` | `extracted.md` + `metadata.json` structure |
| Lesson plan template | `skills/bmad-agent-content-creator/references/template-lesson-plan.md` | G1 structure expectations |
| Marcus conversation mgmt | `skills/bmad-agent-marcus/references/conversation-mgmt.md` | Pipeline graph to update |
| Source-ref grammar | `docs/source-ref-grammar.md` | G1 source_ref validation |

### Previous Story Intelligence (2A-4)

- Vera's protocol already covers G2/G3 with full dual-bridge strategy
- Circuit breaker, O/I/A taxonomy, Fidelity Trace Report — all reusable, gate-agnostic
- Marcus delegation envelope pattern established — extend for G0/G1
- Interaction test guide at 12 scenarios — append G0/G1 scenarios

## Dev Agent Record

### Agent Model Used

Claude claude-4.6-opus (via Cursor)

### Debug Log References

No issues encountered. No Party Mode consultation needed — all design questions resolved from existing architecture.

### Completion Notes List

- Extended Vera's gate evaluation protocol with G0 (5 criteria) and G1 (6 criteria) evaluation steps
- G0 includes PDF bridge invocation for degraded source detection (scanned PDFs) with `degraded_source` warning protocol
- G0 evaluation strategy: structural comparison (section coverage, provenance completeness, invention detection) since original sources may not be fully readable
- G1 evaluation covers LO-to-theme traceability, structure completeness, assessment alignment, orphaned content, and content invention
- Updated Vera SKILL.md: G0 and G1 now "Active" in gate coverage table
- Updated Marcus pipeline graph: Vera now runs at 4 gates (G0, G1, G2, G3) — all before Quinn-R
- Updated Marcus specialist registry with 4 Vera entries
- Updated fidelity context envelope with G0/G1 fields (bundle_dir, source_materials)
- Added 8 interaction test scenarios (13-20) covering G0/G1 pass, omission, invention, degraded source, assessment gap
- Contract validation: 7 contracts valid, 38 criteria, parity check PASS
- Regression: 131 pass, 0 new failures

### File List

**Modified files:**
- `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md` (G0/G1 criteria, PDF bridge section, remediation targets)
- `skills/bmad-agent-fidelity-assessor/SKILL.md` (gate coverage table: G0/G1 Active)
- `skills/bmad-agent-marcus/references/conversation-mgmt.md` (pipeline graph, envelope spec)
- `skills/bmad-agent-marcus/SKILL.md` (specialist registry: 4 Vera entries)
- `tests/agents/bmad-agent-fidelity-assessor/interaction-test-guide.md` (8 new scenarios)
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/2a-5-g0-g1-fidelity-verification.md` (this file)

### Change Log

- 2026-03-28: Story 2A-5 implemented — Vera extended to G0 (source bundle) and G1 (lesson plan) fidelity verification with PDF bridge integration, Marcus pipeline update, and 8 interaction test scenarios
