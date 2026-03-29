# Story G.2: Tool Ecosystem Monitoring and Documentation Synthesis

Epic: G - Governance Synthesis and Intelligence Optimization
Status: done
Sprint key: g-2-tool-ecosystem-monitoring-synthesis
Completed: 2026-03-30

## Summary

Implemented a periodic synthesis engine that aggregates tool documentation refresh signals, cross-sidecar learning patterns, and governance observability metrics into a single actionable report with prioritized recommendations.

## Deliverables

- New synthesis engine:
  - skills/bmad-agent-marcus/scripts/tool_ecosystem_synthesis.py
- New test coverage:
  - skills/bmad-agent-marcus/scripts/tests/test_tool_ecosystem_synthesis.py
- Marcus capability registry update:
  - skills/bmad-agent-marcus/SKILL.md
- Report output contract:
  - _bmad-output/implementation-artifacts/reports/tool-ecosystem-synthesis-report.json (generated when run without --no-write)

## Acceptance Criteria Trace

- AC1: Tool capability changes detected by tech-spec-wrangler are surfaced.
  - Satisfied by parsing all skills/*/references/doc-sources.yaml and extracting refresh status/staleness signals.
- AC2: Agent memory sidecar patterns summarized across specialists.
  - Satisfied by scanning _bmad/memory/*-sidecar/patterns.md, counting entries, and extracting recurring pattern themes.
- AC3: Governance health metrics aggregated.
  - Satisfied by coordination DB aggregation for lane violations, baton redirects, and cache hit/miss rates.
- AC4: Synthesis report written to docs or _bmad-output.
  - Satisfied by default JSON artifact output in _bmad-output/implementation-artifacts/reports/.
- AC5: Actionable recommendations prioritized.
  - Satisfied by high/medium/low recommendation generation covering doc updates, agent revisions, and contract hardening.

## Validation

- pytest skills/bmad-agent-marcus/scripts/tests/test_tool_ecosystem_synthesis.py
  - Result: pass
- Assertions validated:
  - Tool refresh signals aggregated from doc-sources files
  - Governance metrics computed from observability + coordination events
  - Prioritized recommendations include doc-update and governance categories
  - Report file is emitted at expected output path when write mode is enabled

## Adversarial Review and Remediation

- Finding: Synthesis could silently miss governance fields if DB tables are absent.
  - Remediation: explicit table-existence checks with non-fatal error capture in report.errors.
- Finding: Reports without actionable triage are low value.
  - Remediation: enforced recommendation priority ordering and evidence payloads for each recommendation.

## Completion Notes

Story G.2 is complete. Epic G is now fully complete in sprint tracking.
