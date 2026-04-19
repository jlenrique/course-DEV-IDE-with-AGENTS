# Trace Report Format

Stable machine-readable shape for Audra's sweep output. Consumers depend on stability: Cora reads it on every harmonization run, the operator reads it after any direct invocation, a future CI gate reads it as a pre-merge check.

## Report Home

Every sweep writes to:

```
{project-root}/reports/dev-coherence/YYYY-MM-DD-HHMM/
├── trace-report.yaml                   # primary machine-readable output
├── trace-report-summary.md             # 2-4 paragraph human summary
└── evidence/
    ├── <finding-id-1>.md
    ├── <finding-id-2>.md
    └── ...
```

Marcus-route invocations use the variant path `reports/dev-coherence/<run-id>-marcus-route-YYYY-MM-DD-HHMM/` so production-run coherence checks stay associable with the run.

## `trace-report.yaml` Schema

```yaml
# Identification
source: audra
run_type: deterministic | agentic | full      # deterministic-only if L1 failed; full if L1 passed and L2 ran
invocation_source: operator-direct | cora-route | marcus-route-via-cora
anchor: <commit-hash-or-semantic-anchor>
scope: full-repo | since-handoff | directory:<path>
workflow: standard | motion | cluster | null

# L1 results
l1_exit_code: 0 | 1
l1_findings:
  - id: l1-<seq>
    type: omission | invention | alteration
    severity: low | med | high
    check: structural-walk | reference-resolution | parameter-lockstep | gate-contract-lockstep | lane-matrix-coverage | closure-artifact | placement | hot-start-freshness | hud-pipeline-lockstep | workflow-stage-lockstep
    ref: "<file-path-or-contract-key>"
    detail: "<one-line-summary>"
    evidence_path: "evidence/l1-<seq>.md"

# L2 results (only present if l1_exit_code == 0)
l2_run: true | false
l2_findings:
  - id: l2-<seq>
    type: omission | invention | alteration
    severity: low | med | high
    check: prose-drift | intent-of-change | doc-to-code-alignment | parameter-pruning | lane-matrix-gap-sensing
    ref: "<doc-path>"
    detail: "<one-line-observation>"
    evidence_path: "evidence/l2-<seq>.md"

# Routing offers (cross-cut across L1 and L2)
routes_offered:
  - target_agent: bmad-agent-tech-writer | bmad-tea | bmad-agent-architect | bmad-agent-dev
    reason: "<why-this-agent-for-this-finding-set>"
    affected_refs:
      - "<path-1>"
      - "<path-2>"

# Bookkeeping
counts:
  l1_total: <n>
  l1_by_severity: {low: <n>, med: <n>, high: <n>}
  l2_total: <n>
  l2_by_severity: {low: <n>, med: <n>, high: <n>}
duration_seconds: <n>
```

## `trace-report-summary.md` Template

```markdown
# Dev Coherence Sweep — YYYY-MM-DD HH:MM

**Anchor:** <commit-hash>
**Scope:** <scope>
**L1 exit code:** <0|1>

## Summary

<2-4 paragraphs covering: what was checked, what was found, severity distribution, routing offers, and one explicit "next step" the operator or Cora can act on>

## L1 Findings (<N>)

<brief table, severity-sorted>

## L2 Findings (<N>)

<brief table, severity-sorted; omit section if L1 failed>

## Routes Offered

<list of target_agent + reason lines; omit section if none>

## Evidence

See `evidence/` for per-finding detail.
```

## Evidence File Format

Each `evidence/<finding-id>.md` contains:

- The exact file path(s) and line range(s) involved
- A diff excerpt or schema comparison, whichever is more readable
- The specific check rule that triggered
- Any grep output supporting the finding

## Stability Guarantee

The `trace-report.yaml` schema is versioned. Breaking changes require a schema version bump and migration note. Cora, the operator, and future CI consumers all read this file; stability is load-bearing.

## Anti-Patterns

- Never include finding summaries in `trace-report.yaml`'s `detail` field that exceed one line — summaries belong in the evidence file, not in the machine-readable row.
- Never mix L1 and L2 findings in the same list. L1 facts and L2 observations are epistemologically different; conflating them erodes trust in both.
- Never omit the `evidence_path` field. Every finding must be independently inspectable.
