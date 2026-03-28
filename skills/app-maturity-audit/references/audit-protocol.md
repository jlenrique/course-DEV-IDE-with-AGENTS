# APP Maturity Audit Protocol

## Four-Pillar Assessment

For each gate (G0–G6), assess maturity across four pillars:

### Pillar 1: L1 Contracts (Deterministic)

- Does a contract YAML exist at `state/config/fidelity-contracts/g{n}-*.yaml`?
- How many criteria are defined? Are they comprehensive for the gate's scope?
- Are `evaluation_type`, `severity`, `fidelity_class`, and `perception_modality` correctly specified per criterion?
- Run `scripts/validate_fidelity_contracts.py` to confirm structural validity

**Scoring:** ABSENT (no contract) → WEAK (exists but incomplete) → PARTIAL (covers key areas but has gaps) → GOOD (comprehensive) → STRONG (comprehensive + validated)

### Pillar 2: L2 Evaluation (Agentic)

- Does Vera's gate evaluation protocol include this gate?
- Are all contract criteria addressed in the protocol with evaluation instructions?
- Are deterministic and agentic criteria distinguished?
- Is the evaluation exercisable (not just documented but testable via interaction tests)?

**Scoring:** ABSENT (gate not in protocol) → WEAK (partial coverage) → PARTIAL (criteria addressed but not all testable) → GOOD (full coverage, interaction tests exist) → STRONG (full coverage, exercised in production, calibrated)

### Pillar 3: L3 Memory (Learning)

- Does Vera's memory sidecar capture outcomes for this gate?
- Does the producing agent's memory sidecar capture fidelity-relevant patterns?
- Are user corrections and calibration data being recorded?
- Has compound learning occurred (patterns from multiple runs)?

**Scoring:** ABSENT (no memory capture) → WEAK (sidecar exists but empty) → PARTIAL (captures data but not used for calibration) → GOOD (active calibration from captured data) → STRONG (compound learning demonstrably improves evaluation)

### Pillar 4: Perception

- Can Vera perceive the artifacts at this gate?
- Are the correct sensory bridges available and referenced in the contract?
- Does the perception confidence meet the gate's threshold requirements?
- Is perception shared via the caching model (not duplicate runs)?

**Scoring:** OK (text-only gate, no perception needed) → WEAK (bridge exists but not integrated) → PARTIAL (bridge integrated but confidence issues) → GOOD (bridge integrated, confidence adequate) → STRONG (bridge integrated, cached, high confidence, validated)

## Leaky Neck Assessment

Identify remaining points where agentic judgment enforces constraints that could be deterministic:

1. Scan each agent's SKILL.md and references for natural-language constraint enforcement
2. Check the fidelity-control vocabulary coverage — are all literal slides using vocabulary controls instead of free-text?
3. Check parameter bindings — are tool parameters derived from schema fields or from agent prose?
4. For each leak found: document the location, the constraint being enforced, and the proposed deterministic alternative

## Sensory Horizon Assessment

For each modality the pipeline produces, check bridge coverage:

| Modality | Bridge | Contract Gates Using It | Status |
|----------|--------|------------------------|--------|
| PPTX | `pptx_to_agent.py` | G3 (text verification) | Check |
| Image | `png_to_agent.py` | G3 (visual), G4 (slide content) | Check |
| Audio | `audio_to_agent.py` | G5 (STT verification) | Check |
| PDF | `pdf_to_agent.py` | G0 (degraded source) | Check |
| Video | `video_to_agent.py` | G6 (future) | Check |

For each: does the bridge script exist? Does it return the canonical perception schema? Is it referenced in the correct gate contract?

## Cumulative Drift Summary

If production runs have occurred, summarize:
- Most recent run's global drift scores per gate
- Average drift trend across runs (improving or degrading)
- Most-drifting content themes
- Source from Vera's memory sidecar `chronology.md`

## Maturity Delta

Compare the current audit against the most recent previous audit:
- For each gate × pillar cell: current score vs. previous score
- Highlight improvements and regressions
- Calculate overall maturity level change
