# Pre-Flight Check Integration

## Purpose

Describes how Marcus integrates with the existing `pre-flight-check` skill to validate tool readiness before production runs.

## When to Run Pre-Flight

1. **User requests** — "Run pre-flight check", "Are all tools ready?", "Check tool status"
2. **Before production run** — Marcus proactively suggests pre-flight when initiating a run that requires specific tools
3. **After tool failure** — When a production stage fails due to tool unavailability, suggest re-running pre-flight

## Invocation

Marcus delegates to the `pre-flight-check` skill (already active at `skills/pre-flight-check/`):

1. Load `skills/pre-flight-check/SKILL.md` for capability routing
2. The skill references `skills/pre-flight-check/references/diagnostic-procedures.md` for per-tool check strategy
3. For programmatic checks: invoke `skills/pre-flight-check/scripts/preflight_runner.py`
4. For documentation scanning: reference `skills/pre-flight-check/references/tool-doc-scanning.md`

## Result Presentation

Marcus translates pre-flight results into conversational reporting:

**All green:**
> "All systems ready — Gamma, Canvas, and ElevenLabs are responding. Ready to start production."

**Partial issues:**
> "Heads up — Gamma and Canvas are green, but ElevenLabs isn't responding. Want me to retry, or should we work with what we have? If we skip audio, I can still do outline and slides."

**Multiple failures:**
> "Several tools are down — [list]. This might not be the best time for a production run. Want me to try again in a few minutes, or should we switch to ad-hoc mode and plan instead?"

## Logging

Pre-flight results are logged as coordination events:
```
log_coordination.py log --run-id {run_id or "preflight"} --agent "pre-flight-check" --action "completed" --payload '{results_json}'
```

## Tool Documentation Changes

When the pre-flight check detects API changes or new capabilities, Marcus highlights them:
> "ElevenLabs has new voice options since your last check — want me to update the style guide with recommended voices?"

This feeds into the parameter-intelligence capability (Story 2.4).
