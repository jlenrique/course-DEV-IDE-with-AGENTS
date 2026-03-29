# Agent QA Release Gate

## Purpose

Define the mandatory quality gate for any new or revised agent under skills/bmad-agent-*/.

This gate formalizes the existing bmad-agent-builder quality optimizer scan as a release-blocking step.

## Required Scan Dimensions

Every scan must score these dimensions:

- structure_compliance
- prompt_craft_quality
- cohesion
- execution_efficiency
- script_opportunity_analysis

Score normalization:

- Each dimension score must be a float in [0.0, 1.0].
- Threshold must be a float in [0.0, 1.0].

## Pass/Fail Criteria

Default threshold per dimension: 0.80

Rules:

1. Pass only if all dimensions are >= threshold.
2. Any dimension below threshold is a blocking failure.
3. Blocking failures require revision and re-scan before acceptance.
4. A passing scan is required before agent stories can move to review/done.

## Archive Requirement

Each scan result must be archived at:

- skills/reports/bmad-agent-{name}/quality-scan/{timestamp}.json

Required archive fields:

- timestamp
- agent_name
- scanner
- threshold
- dimensions
- failed_dimensions
- status
- blocking
- notes

## Workflow Integration Rules

Create-story workflow requirement:

- If a story creates or revises any file under skills/bmad-agent-*/, include explicit tasks for:
  - running the QA scan,
  - archiving scan output in skills/reports/bmad-agent-{name}/quality-scan/,
  - blocking acceptance on failures.

Dev-story workflow requirement:

- For agent stories, before status review/done:
  - execute scan,
  - confirm pass,
  - archive timestamped result,
  - record archive path in story file and change log.

## Recommended Command

Use the lightweight archive helper in this repo:

- python scripts/utilities/archive_agent_quality_scan.py --agent-name {name} --structure-compliance 0.90 --prompt-craft-quality 0.88 --cohesion 0.86 --execution-efficiency 0.85 --script-opportunity-analysis 0.83

This command computes pass/fail and writes the canonical archived report.

Exit behavior:

- `0`: pass
- `1`: fail (blocking)
- `2`: invalid input (for example invalid score range, timestamp format, or agent name)
