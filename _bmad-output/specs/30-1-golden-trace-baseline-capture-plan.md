# 30-1 Golden-Trace Baseline Capture - Execution Plan

**Date authored:** 2026-04-18  
**Purpose:** capture pre-refactor Marcus envelope I/O on the trial corpus as a committed fixture before Story `30-1-marcus-duality-split` opens. Required by R1 ruling amendment 12 and Murat's binding PDG.  
**Runway discipline:** this capture is independent of `31-2` / `31-3` dev and should execute in a side worktree during their in-flight time per `docs/dev-guide/story-cycle-efficiency.md`.

---

## Why this runs before 30-1

Story `30-1` refactors Marcus into `marcus/intake/` and `marcus/orchestrator/`. Its binding DoD requires byte-identical envelope I/O after refactor, modulo timestamp and UUID normalization. Without a committed pre-refactor fixture, any post-refactor diff is circular.

Capturing the baseline before `30-1` opens makes the later diff meaningful and keeps `30-1` scoped as a real refactor instead of a re-specification exercise.

## Trial corpus selection

Use one named real 7-page SME source file per section 6-A1 of `_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md`.

- Commit the source under `tests/fixtures/trial_corpus/`.
- Record its SHA-256 in a sibling `.provenance.yaml` card.
- Keep the first capture narrow. Broader corpus expansion can happen later.

## Capture scope

Capture the current Marcus output for these five points:

1. Step `01` - ingestion envelope
2. Step `02` - source-quality envelope
3. Step `03` - audience-profile envelope
4. Step `04` - ingestion quality gate envelope
5. Step `04-05` - pre-packet handoff envelope

For each capture point, record:

- full JSON payload of the emitted envelope
- timestamp fields
- UUID fields
- any log-relevant fields already embedded in the envelope payload

## Locked normalization rules

Only these four substitutions are allowed:

1. timestamps -> `{{TIMESTAMP}}`
2. UUID4 values -> `{{UUID4}}`
3. SHA-256 digests -> `{{SHA256}}`
4. repo-absolute paths -> `{{REPO_ROOT}}`

No other normalization is permitted. Apply the same rules symmetrically to pre- and post-refactor output.

## Capture method

Use:

```bash
python -m scripts.utilities.capture_marcus_golden_trace \
  --source <path-to-trial-corpus-file> \
  --output tests/fixtures/golden_trace/marcus_pre_30-1/
```

The script:

- runs the current Marcus path through steps `01 -> 04 -> 04/05`
- writes one JSON file per capture point
- writes `golden-trace-manifest.yaml`
- applies the locked normalization rules before writing

Fixture output path:

`tests/fixtures/golden_trace/marcus_pre_30-1/`

Script and fixtures must commit together before `30-1` opens.

## Concrete wiring map for the capture agent

The remaining work in `_run_marcus_pipeline()` is bounded to a small set of repo surfaces:

- `scripts/utilities/marcus_prompt_harness.py`
  - Prompt 3 checks the ingestion artifact set:
    - `extracted.md`
    - `metadata.json`
    - `ingestion-evidence.md`
  - Prompt 4 checks the pre-packet handoff surface:
    - `irene-packet.md`
    - `ingestion-quality-gate-receipt.md`
- `scripts/utilities/prepare-irene-packet.py`
  - canonical builder for `irene-packet.md`
- `_bmad/memory/bmad-agent-marcus/references/conversation-mgmt.md`
  - authoritative step ordering and the `01 -> 04 -> 04/05` dependency graph

The capture agent's job is to execute the current Marcus pre-30-1 path far enough to materialize those artifacts, then pack one JSON envelope per capture point in the locked order from `CAPTURE_POINTS`.

Each emitted fixture JSON must:

- remain a top-level object
- include `_internal_emitter`
- serialize cleanly with `json.dumps`

## Facade-leak debugging support

Each captured envelope should carry `_internal_emitter` naming the internal Marcus identity that emitted it. This is for human diff inspection only. It is not a user-facing field and is not a relaxation of the byte-identical comparison contract.

## Execution window

Run this in parallel with `31-3` or other non-blocking story work.

- branch: `dev/30-1-baseline-capture`
- merge target: `dev/lesson-planner`

## Pre-capture checklist

### Already landed in support lane

- [x] `scripts/utilities/capture_marcus_golden_trace.py` scaffolded with CLI, normalization rules, manifest writer, and envelope writer
- [x] normalization rules smoke-tested
- [x] `tests/fixtures/golden_trace/marcus_pre_30-1/` scaffolded with README
- [x] `tests/fixtures/trial_corpus/` scaffolded with README
- [x] `scripts/utilities/validate_marcus_golden_trace_fixture.py` added to validate a completed fixture bundle

### Pending in the authoritative capture lane

- [ ] Select and commit the named SME source file under `tests/fixtures/trial_corpus/`
- [ ] Add the sibling `.provenance.yaml` card with SHA-256
- [ ] Wire `_run_marcus_pipeline()` in `scripts/utilities/capture_marcus_golden_trace.py`
- [ ] Run one clean capture and write the manifest
- [ ] Run `python -m scripts.utilities.validate_marcus_golden_trace_fixture --fixture-dir tests/fixtures/golden_trace/marcus_pre_30-1/`
- [ ] Re-run the capture and confirm identical normalized output
- [ ] Commit source fixture, pipeline wiring, captured envelopes, and manifest together
- [ ] Append capture date and commit SHA back into this plan or linked status notes

## Out of scope

- the `30-1` post-refactor regression test itself
- steps `05+`
- multi-corpus capture

## References

- `_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `scripts/utilities/capture_marcus_golden_trace.py`
- `scripts/utilities/validate_marcus_golden_trace_fixture.py`
- `scripts/utilities/prepare-irene-packet.py`
- `scripts/utilities/marcus_prompt_harness.py`
- `_bmad/memory/bmad-agent-marcus/references/conversation-mgmt.md`
- `tests/fixtures/golden_trace/marcus_pre_30-1/README.md`
- `tests/fixtures/trial_corpus/README.md`
