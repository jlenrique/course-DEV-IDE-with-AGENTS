"""Texas retrieval foundation — Shape 3-Disciplined contract.

Story 27-0 (Epic 27 Texas Intake Surface Expansion). See
`_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md` for
the full contract specification and Round-3 party-mode consensus record.

The retrieval subsystem partitions source-fetch work by knowledge-locality:

- **Editorial knowledge** (intent, acceptance criteria, provider choice) lives
  with Tracy (Epic 28 agent) — she authors `RetrievalIntent` objects.
- **Provider-DSL knowledge** (query formulation, fetch, pagination, native
  signal filtering) lives in per-provider `RetrievalAdapter` subclasses.
- **Dispatch + iteration orchestration** lives in this package's `dispatcher`
  module — thin routing layer with cross-validation fan-out support.

No real provider ships in 27-0. `FakeProvider` is the reference adapter
for contract-validation tests. Real providers land in follow-on stories:
scite (27-2), Consensus (27-2.5), image-sources (27-3), YouTube (27-4).
"""
