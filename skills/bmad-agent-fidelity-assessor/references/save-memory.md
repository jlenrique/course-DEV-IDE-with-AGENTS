# Save Memory

Immediately persist the current session context to memory.

## Process

Update `index.md` with current assessment context: active gate, production run, calibration summary, recurring fidelity patterns. Checkpoint `patterns.md` with any new gate-specific findings, fidelity class patterns, or human calibration adjustments. Checkpoint `chronology.md` with assessment outcomes, circuit breaker events, and human waivers.

## Calibration Save

When the human provides feedback on Vera's findings (waives, accepts, or adjusts severity), immediately update:
- `index.md` calibration summary with the adjustment
- `patterns.md` with the specific calibration event, gate, producing agent, fidelity class, and reasoning
- `chronology.md` with the timestamp and context

## Circuit Breaker Save

When a circuit breaker triggers (critical or high finding), immediately record:
- `chronology.md` with gate, finding details, producing agent, remediation guidance, and outcome (retry/escalation/waiver)

## Output

Confirm save with brief summary: "Memory saved. {brief-summary-of-what-was-updated}"
