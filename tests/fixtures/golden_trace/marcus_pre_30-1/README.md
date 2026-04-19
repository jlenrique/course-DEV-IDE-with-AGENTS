# Marcus Golden-Trace Baseline - `marcus_pre_30-1/`

**Purpose:** committed pre-refactor Marcus envelope I/O for Story `30-1`.

## Status

Empty on purpose until the authoritative capture lane runs the real baseline capture.

## Expected contents after capture

```text
tests/fixtures/golden_trace/marcus_pre_30-1/
|- README.md
|- golden-trace-manifest.yaml
|- step-01-ingestion-envelope.json
|- step-02-source-quality-envelope.json
|- step-03-audience-profile-envelope.json
|- step-04-ingestion-quality-gate-envelope.json
`- step-04-05-pre-packet-handoff-envelope.json
```

## Authoring flow

1. Commit the named SME source file under `tests/fixtures/trial_corpus/`.
2. Run:

```bash
python -m scripts.utilities.capture_marcus_golden_trace \
  --source <path> \
  --output tests/fixtures/golden_trace/marcus_pre_30-1/
```

3. Re-run the capture and confirm stable normalized output.
4. Run:

```bash
python -m scripts.utilities.validate_marcus_golden_trace_fixture \
  --fixture-dir tests/fixtures/golden_trace/marcus_pre_30-1/
```

5. Do not treat the bundle as ready until the validator passes.
6. Commit the source fixture, capture wiring, envelope files, and manifest together.

## Notes

- `_internal_emitter` is expected in each JSON file for human diff inspection.
- The four normalization rules are locked in `capture_marcus_golden_trace.py`.
- Story `30-1` should open only after this directory contains a validated baseline bundle.
