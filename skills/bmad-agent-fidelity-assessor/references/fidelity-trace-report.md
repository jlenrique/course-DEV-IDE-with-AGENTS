# Fidelity Trace Report

Standard output format for all fidelity assessments. Every gate evaluation produces one report.

## Report Structure

```yaml
report:
  gate: "G2"                    # Gate evaluated (G0–G6)
  gate_name: "Slide Brief"      # Human-readable gate name
  production_run_id: "C1-M1-P2S1-VID-001"
  producing_agent: "irene"      # Agent that produced the artifact
  evaluated_at: "2026-03-28T14:30:00Z"
  run_mode: "default"           # default | ad-hoc

  source_of_truth:
    description: "Lesson plan (LOs, content structure, assessment hooks)"
    artifact_paths:
      - "course-content/staging/ad-hoc/lesson-plan.md"

  evaluated_artifacts:
    - "course-content/staging/ad-hoc/slide-brief.md"

  perception:                   # Only present when sensory bridges were invoked
    bridges_used:
      - modality: "pptx"
        script: "pptx_to_agent.py"
        confidence: "HIGH"
        artifact: "course-content/staging/ad-hoc/slides/deck.pptx"
      - modality: "image"
        script: "png_to_agent.py"
        confidence: "HIGH"
        artifact: "course-content/staging/ad-hoc/slides/card-01.png"
    degraded: false             # true if fallback was used (e.g., image instead of PPTX)

  verdict:
    pass: true                  # Overall pass/fail
    fidelity_score: 0.92        # 0.0–1.0 (proportion of criteria passed)
    highest_severity: "medium"  # Highest severity among findings (critical/high/medium/none)
    criteria_evaluated: 6       # Total L1 criteria checked
    criteria_passed: 5
    criteria_failed: 1

  findings:
    omissions: []
    inventions: []
    alterations:
      - id: "F-G2-001"
        criterion_id: "G2-03"
        category: "alteration"
        severity: "medium"
        description: "Fidelity classification for Slide 7 may be incorrect"
        artifact_location: "slide-brief.md, Slide 7"
        source_ref: "lesson-plan.md#Block 4"
        output_ref: "slide-brief.md#Slide 7"
        evidence:
          resolved_source_slice: "Key Assessment Criteria: 1. Identify three signs..."
          output_slice: "Fidelity: creative. Content: 'Assessment criteria overview'"
          resolution_confidence: "exact"
          comparison_result: "alteration"
        suggested_remediation: "Slide 7 contains exact assessment criteria from lesson plan — fidelity should be literal-text, not creative"

  circuit_breaker:
    triggered: false
    action: "proceed"           # halt | retry | proceed
    remediation_target: null    # source-wrangler | irene | gary | elevenlabs-voice-director | null
    remediation_guidance: null
```

## Finding Taxonomy (O/I/A)

| Category | Definition | Severity Guidance |
|----------|-----------|-------------------|
| **Omission** | Source content missing from output | Critical if LO is missing. High if content block is missing. Medium if supplementary detail is absent. |
| **Invention** | Output content not traceable to source | Critical if clinical claims, statistics, or assessment items are invented. High if significant content is added without source basis. Medium if minor elaboration without factual claims. |
| **Alteration** | Source content present but meaning changed | Critical if medical/clinical meaning is changed. High if pedagogical intent is shifted. Medium if phrasing is changed but meaning preserved. |

## Finding Fields

Every finding includes all of these fields:

| Field | Description |
|-------|-------------|
| `id` | Unique finding ID within report (e.g., F-G3-002) |
| `criterion_id` | L1 contract criterion that was violated (e.g., G3-02) |
| `category` | omission, invention, or alteration |
| `severity` | critical, high, or medium |
| `description` | Human-readable description of the finding |
| `artifact_location` | Where in the output: slide number, line range, timestamp |
| `source_ref` | Source reference in provenance format (per `docs/source-ref-grammar.md`) |
| `output_ref` | Output reference location |
| `evidence` | Evidence retention block (see below) |
| `suggested_remediation` | Specific guidance for the producing agent to fix this |

## Evidence Retention

Every finding captures the comparison evidence for auditability:

```yaml
evidence:
  resolved_source_slice: "The exact text from the source of truth"
  output_slice: "The exact text from the output artifact"
  resolution_confidence: "exact"    # exact | approximate | broken
  comparison_result: "omission"     # omission | invention | alteration
```

This creates a self-contained, auditable comparison record. The human reviewer can verify Vera's finding by reading the evidence block without needing to open the source files.

## Severity-to-Response Mapping

From `docs/fidelity-gate-map.md` operating policy:

| Severity | Response | Circuit Break | Max Retries |
|----------|----------|:---:|:-----------:|
| **Critical** | Pipeline halts immediately | Yes | 0 (no auto-retry) |
| **High** | Producing agent receives report, may retry with remediation guidance | Yes | 1 |
| **Medium** | Warning — artifact proceeds to Quinn-R and HIL gate with findings attached | No | N/A |

In **ad-hoc mode**: high findings downgrade to medium (proceed with advisory). Critical findings still halt.

## Cumulative Drift Section (G3+ only)

For gates G3 and later, the report includes a `global_drift` block alongside the per-criterion findings:

```yaml
global_drift:
  gate: "G3"
  source_bundle: "path/to/extracted.md"
  total_source_themes: 8
  themes_represented: 7
  global_fidelity_score: 0.875
  drift: 0.125
  threshold_mode: "production"    # ad-hoc | production | regulated
  verdict: "warning"              # pass | warning | failure
  missing_themes: [...]
```

Drift verdicts are independent of per-criterion findings — a gate can pass all criteria but fail the drift check, or vice versa. Both are included in the report and both feed into the circuit breaker decision.

## Report Return to Marcus

When Vera completes evaluation, return this payload to Marcus:

```yaml
status: passed | failed | warning
gate: "G2"
verdict: { ... }       # Full verdict block
findings: { ... }      # Full findings block
circuit_breaker: { ... } # Circuit breaker block
```

Marcus handles routing based on `circuit_breaker.action`:
- `halt` → Stop pipeline, present full report to user
- `retry` → Re-invoke producing agent with remediation guidance
- `proceed` → Pass findings to Quinn-R as advisory
