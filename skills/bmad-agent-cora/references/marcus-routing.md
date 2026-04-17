# Marcus-Routing Protocol (MR)

Handle in-envelope invocation from Marcus when the HIL operator asks Marcus mid-run for a harmonization or coherence check.

Same pattern Marcus uses with Creative Director (CD): Cora is invoked only through a Marcus-owned context envelope and returns a structured report back to Marcus — Cora never mutates run state directly and never surfaces independently to the operator during a Marcus-owned run.

## Envelope Fields Marcus Passes

- `invocation_source: "marcus-route"` — distinguishes from operator-direct invocation
- `run_id` — active production run ID
- `scope` — "since-handoff" / "directory:<path>" / "full-repo" (Marcus pre-decides based on operator request)
- `report_home` — path to write trace reports under `reports/dev-coherence/<run-id>-marcus-route-YYYY-MM-DD-HHMM/`
- `urgency` — "immediate" / "background" — affects whether Cora runs full L1+L2 or L1-only

## Steps

1. Skip the scope handshake; use Marcus's passed scope.
2. Run the harmonization protocol per `./harmonization-protocol.md` with the provided envelope.
3. Return structured report to Marcus (no operator-facing prose):

```yaml
source: cora
invocation: marcus-route
run_id: <run-id>
anchor: <commit>
scope: <scope>
l1_exit_code: 0|1
l1_findings:
  - {type: omission|invention|alteration, severity: low|med|high, ref: "<path-or-contract>", detail: "<one-line>"}
l2_findings:
  - {type: prose-drift|intent-of-change, severity: low|med|high, ref: "<doc-path>", detail: "<one-line>"}
paige_route_offered: true|false
report_home: <path>
```

4. Marcus relays to the operator as part of the run conversation, incorporating Cora's findings into the production-run narrative.

## What NOT To Do On Marcus-Route

- Do not greet the operator; Marcus is the conversational surface.
- Do not write to `SESSION-HANDOFF.md` or `next-session-start-here.md` — those are dev-session artifacts, not run artifacts.
- Do not update Cora's `chronology.md` with production-run events beyond a single line: `YYYY-MM-DD HH:MM — Marcus-route invocation. Run <id>. L1 exit <code>.`
- Do not promote a warn to the operator if Marcus's urgency is "background" — return findings and let Marcus decide when to surface.

## Role Clarity

Cora is a backing service for Marcus on this path. Marcus is the production orchestrator; Cora is the repo-coherence consultant. Same seam as Marcus → CD → Marcus.
