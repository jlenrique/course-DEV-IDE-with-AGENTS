# Lane Matrix

This matrix defines judgment ownership across the APP workflow.

Rules:
- Exactly one owner per judgment dimension.
- "NOT Owned By" is explicit to prevent overlap and lane drift.
- This matrix extends `docs/fidelity-gate-map.md` and is compatible with its role matrix.

| Judgment Dimension | Owner | Scope | NOT Owned By |
|---|---|---|---|
| Orchestration and human interaction | Marcus | Run planning, delegation routing, checkpoint choreography, exception handling, user-facing decision flow | Specialist agents |
| Winner authorization and motion-control governance | Marcus | Double-dispatch winner collapse, `authorized-storyboard.json`, Gate 2M coverage, Motion Gate closure, prompt-pack selection by workflow template | Gary, Kira, Irene, Quinn-R |
| Instructional design and pedagogy | Irene | Learning objective strategy, Bloom's alignment, sequencing, delegation intent, behavioral intent specification | Gary, Kira (Kling specialist), Voice Director, Vera, Quinn-R |
| Tool execution quality (slides) | Gary | Layout integrity, parameter confidence, embellishment control, output usability against delegated brief | Irene, Vera, Quinn-R |
| Tool execution quality (video) | Kira (Kling specialist) | Operation selection, model/mode choices, prompt quality, output usability against delegated brief | Irene, Vera, Quinn-R |
| Tool execution quality (audio) | Voice Director | Voice/mode settings, pronunciation handling, timing completeness, manifest write-back integrity | Irene, Vera, Quinn-R |
| Tool execution quality (composition planning) | Compositor | Deterministic manifest interpretation, assembly guide completeness and clarity for human execution | Irene, Vera, Quinn-R |
| Motion designation and gate governance | Marcus | Gate 2M presentation, winner-deck binding, motion plan completeness, Motion Gate closure choreography | Kira, Irene, Quinn-R |
| Cluster plan validation (G1.5) | Vera + Marcus HIL | Deterministic structural validation of cluster plan (13 criteria), operator approval choreography before Gary dispatch | Gary, Quinn-R |
| Cluster coherence validation (G2.5) | Vera + Marcus HIL | Perception-based coherence scoring per cluster (typography, background, isolation, whitespace, element count), operator remediation routing | Gary, Quinn-R |
| Perception (shared infrastructure) | Sensory Bridges | Canonical multimodal perception payloads, confidence-scored interpretation handoff, caching for validator reuse | Individual specialists inventing separate perception stacks |
| Source-to-output fidelity | Vera | Omission/Invention/Alteration findings, source-ref traceability, cumulative drift signals, fidelity contract adherence | Quinn-R, Irene, producing specialists |
| Quality standards | Quinn-R | Brand consistency, accessibility, instructional soundness, learner-effect intent fidelity, audio/composition quality | Vera, producing specialists |
| Content accuracy (flag only) | Quinn-R | Detect potential medical accuracy concerns and escalate to human review; never adjudicate clinical correctness | All agents (adjudication) |
| Platform deployment | Active platform specialist for the run* | Canvas/CourseArc/LMS execution details, platform-specific formatting and verification | Marcus, Irene, Vera, Quinn-R |
| Literal-visual operator checkpoint governance | Marcus | Prompt 6B packet completeness, operator-ready confirmation, pre-dispatch confirmation before Gary side effects | Gary, Irene, Quinn-R |

*Per-run owner selection rule: owner is the specialist explicitly assigned by Marcus for that deployment stage (for example Canvas specialist or CourseArc specialist).

## Intent Terms

- Behavioral intent (Irene): The learner behavior targeted by instructional design and delegation briefs.
- Intent fidelity (Quinn-R): Whether the finished learner experience achieves that intended behavior.
- Source fidelity (Vera): Whether output remains faithful to source material and provenance.

## Lane Responsibility Coverage Checklist

Files that must explicitly include a `Lane Responsibility` section in this pipeline:

- [x] `skills/bmad-agent-marcus/SKILL.md`
- [x] `skills/bmad-agent-content-creator/SKILL.md`
- [x] `skills/bmad-agent-gamma/SKILL.md`
- [x] `skills/bmad-agent-kling/SKILL.md`
- [x] `skills/bmad-agent-elevenlabs/SKILL.md`
- [x] `skills/bmad-agent-fidelity-assessor/SKILL.md`
- [x] `skills/bmad-agent-quality-reviewer/SKILL.md`
- [x] `skills/compositor/SKILL.md`

Reference files that must not leak lane ownership beyond their agent's lane:

- [x] `skills/bmad-agent-gamma/references/quality-assessment.md`
