# APP Fidelity Maturity Audit — {date}

**Date:** {date}
**Auditor:** {auditor}
**Scope:** All 7 production gates (G0–G6), evaluated against 4 pillars
**Previous audit:** {previous_audit_path}
**Reference:** `docs/app-design-principles.md`, `docs/fidelity-gate-map.md`

---

## Maturity Scoring Key

| Score | Definition |
|-------|-----------|
| **ABSENT** | No capability exists for this pillar at this gate |
| **WEAK** | Partial/informal capability exists but is not testable or reliable |
| **PARTIAL** | Capability exists but has significant gaps |
| **GOOD** | Capability exists and covers most requirements |
| **STRONG** | Capability is complete, testable, and operationalized |

---

## Audit Matrix (Heat Map)

| Gate | Artifact | L1 Contracts | L2 Evaluation | L3 Memory | Perception |
|------|----------|:---:|:---:|:---:|:---:|
| **G0** | Source Bundle | {score} | {score} | {score} | {score} |
| **G1** | Lesson Plan | {score} | {score} | {score} | {score} |
| **G2** | Slide Brief | {score} | {score} | {score} | {score} |
| **G3** | Generated Slides | {score} | {score} | {score} | {score} |
| **G4** | Narration Script | {score} | {score} | {score} | {score} |
| **G5** | Audio | {score} | {score} | {score} | {score} |
| **G6** | Composition | {score} | {score} | {score} | {score} |

**Overall Maturity: LEVEL {N}**

---

## Maturity Delta (vs. Previous Audit)

| Gate | Pillar | Previous | Current | Change |
|------|--------|----------|---------|--------|
| {gate} | {pillar} | {prev_score} | {curr_score} | {improved/regressed/unchanged} |

**Net improvements:** {count}
**Regressions:** {count}

---

## Leaky Neck Report

| Location | Constraint | Current Enforcement | Proposed Fix | Status |
|----------|-----------|-------------------|-------------|--------|
| {agent/file} | {what's being enforced} | {agentic prose / code / schema} | {deterministic alternative} | {open/resolved} |

---

## Sensory Horizon Report

| Modality | Bridge Script | Exists | Schema Conformant | Referenced In Contracts | Cache Integrated |
|----------|--------------|:---:|:---:|:---:|:---:|
| PPTX | `pptx_to_agent.py` | {Y/N} | {Y/N} | {gates} | {Y/N} |
| Image | `png_to_agent.py` | {Y/N} | {Y/N} | {gates} | {Y/N} |
| Audio | `audio_to_agent.py` | {Y/N} | {Y/N} | {gates} | {Y/N} |
| PDF | `pdf_to_agent.py` | {Y/N} | {Y/N} | {gates} | {Y/N} |
| Video | `video_to_agent.py` | {Y/N} | {Y/N} | {gates} | {Y/N} |

---

## Cumulative Drift Summary

{Most recent production run drift data, or "No production runs completed yet."}

---

## Recommendations

{Prioritized list of improvements to advance APP maturity}
