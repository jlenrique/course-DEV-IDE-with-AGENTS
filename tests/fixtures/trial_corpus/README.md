# Trial Corpus — `tests/fixtures/trial_corpus/`

**Purpose.** Committed real SME source files used to drive end-to-end trial
runs for the Lesson Planner MVP. §6-A1 of
`_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md` sets the binding
**named SME input floor**: at least one named real 7-page SME source file
committed here with operator-verifiable SHA-256 recorded in the run charter.

## Status (as of 2026-04-18)

No duplicated source file is stored here yet.

The initial `30-1` Golden-Trace baseline was satisfied instead by referencing
the already-versioned canonical source:

- `course-content/courses/tejal-APC-C1/APC C1-M1 Tejal 2026-03-29.pdf`

plus the committed tracked bundle:

- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409-motion/`

This is an accepted initial-baseline shortcut because duplicating the same real
SME source into this folder would add no new control value. This directory
remains the preferred home for any future expanded trial corpus.

## What belongs here

- Real SME source files (7-page or thereabouts) that exercise the full
  ingestion → 4A → downstream pipeline. Prefer formats that match the shipped
  provider set: DOCX (via `27-1-docx-provider-wiring`), and any other locator/
  retrieval-shape providers that land before trial.
- Per-source metadata cards recording provenance, SHA-256, intended use
  (Golden-Trace baseline / smoke battery / operator dry-run / regression set),
  and the associated plan-doc §6 criterion.
- Redacted/anonymized variants where original SME material contains sensitive
  identifiers, with a pointer to the redaction discipline in the metadata.

## What does NOT belong here

- Synthetic / LLM-generated "SME-like" content. §6-A1 requires NAMED REAL SME
  input. A synthetic fixture fails the operator-readable pass/fail criterion.
- Derived artifacts (extracted.md, metadata.json, quality-gate receipts,
  etc.). Those land under run-scoped output directories, not here.
- Artifacts that are not themselves inputs to the ingestion pipeline.

## Naming convention

`<provider-shape>-<sme-shortname>-<YYYY-MM-DD>.<ext>`, for example:
- `docx-tejal-case-study-2026-04-17.docx`
- `scite-cardiology-guidelines-2026-04-18.yaml` (if a scite retrieval outcome
  is committed as a locked fixture for regression)

## Recording provenance

Each source file must be accompanied by a sibling `.provenance.yaml` card:

```yaml
# tests/fixtures/trial_corpus/<filename>.provenance.yaml
source_file: <filename>
source_sha256: <64-hex SHA-256>
provider_shape: docx  # or scite, etc.
sme_name: "Dr. Tejal Mehta"
page_count: 7
captured_at: "2026-04-17"
intended_use:
  - golden-trace-baseline  # §6-A1 named SME input + 30-1 capture source
  - smoke-battery          # §6-E1 5x-consecutive CI gate
redaction_level: none      # or redacted | anonymized
redaction_notes: ""
```

## First occupant (pending)

The first file expected here is the named 7-page SME source for the
30-1 Golden-Trace Baseline capture. Plan doc:
`_bmad-output/specs/30-1-golden-trace-baseline-capture-plan.md`.
