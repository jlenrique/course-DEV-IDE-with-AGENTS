# System-Level Test Design Plan: course-DEV-IDE-with-AGENTS

## Coverage Matrix

| Flow/Area                         | Test Type         | Test Pattern                   | Owner   | Gates      |
|-----------------------------------|-------------------|-------------------------------|---------|------------|
| Orchestrator-agent-skill handoff  | ATDD, Integration | E2E scenario, acceptance      | Murat   | CI/blocker |
| Prompt-pack workflow (all modes)  | Integration, Unit | Parametric, file snapshot     | Amelia  | CI/blocker |
| Config/cascade/ad-hoc/regulated   | Integration       | Path combo, state regression  | Murat   | CI/blocker |
| State Management & Artifact drift | Integration       | File verification (pre/post)  | Amelia  | Lint       |
| Memory sidecar & contract docs    | Contract, Doc     | Schema, trace matrix, DoD     | Paige   | Review     |
| Error/resiliency (API, CLI, UI)   | ATDD, Integration | Fault injection, harness      | Murat   | CI         |
| Operator error scenarios (manual) | E2E               | CLI harness, review           | Amelia  | Review     |
| Asset/contract integrity          | Contract          | Asset/file scan, matching     | Paige   | Lint/CI    |

## Execution Strategy
- Develop/maintain system-level acceptance (ATDD) flows first.
- Expand with parametric/unit tests for agent skills and edge cases.
- Automate integration of file/tree regression and contract/DoD scans.
- All test artifacts versioned, CI-enforced blocking for CI/blocker gates.
- Add failure-capture and review steps for non-critical flows.

## Priorities
1. End-to-end flows (orchestrator→agent→skill→output)
2. Config/cascade path coverage (all operational modes)
3. Error/fault injection to expose drift and resiliency gaps.
4. Documentation traceability: mapping tests to requirements and assets.

## Quality Gates
- All system-level ATDD/integration tests must pass for PR merge.
- Contract/asset checks must pass for release.
- Lint/format/review must pass for periodic/integration build.

## Resource/Estimate
- Modular by team/agent area; see Owner column for primary responsibility.
- Estimate: Epic timescale for full E2E pass, sprints for expansions/migrations by area.
