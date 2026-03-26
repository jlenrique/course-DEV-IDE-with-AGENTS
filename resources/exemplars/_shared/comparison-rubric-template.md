# Exemplar Comparison Rubric Template

Use this rubric to score an agent's reproduction of an exemplar. Each dimension is rated 1–5. A reproduction **passes** when every High-weight dimension scores >= 4 and no dimension scores < 3.

## Dimensions

| Dimension | Weight | Description | Score Guide |
|-----------|--------|-------------|-------------|
| **Structural fidelity** | High | Output has the same number of sections/slides/segments, content follows the same flow as the exemplar | 5 = identical structure; 3 = minor reordering; 1 = wrong structure |
| **Parameter accuracy** | High | Correct API/MCP parameters used (theme, layout, voice, model, format) matching the reproduction spec | 5 = all params correct; 3 = minor deviations; 1 = wrong params |
| **Content completeness** | Medium | All key content from the exemplar is present in the reproduction | 5 = nothing missing; 3 = minor omissions; 1 = major content gaps |
| **Context alignment** | Medium | Reproduction reflects the course/module/lesson context described in the brief | 5 = fully aligned; 3 = partially aligned; 1 = context mismatch |
| **Creative quality** | Low (grows over time) | Aesthetic, stylistic, or tonal similarity to the exemplar | 5 = indistinguishable; 3 = recognizably similar; 1 = clearly different |

## Scoring Template

```yaml
exemplar_id: "{exemplar-id}"
agent: "{agent-name}"
attempt_date: "YYYY-MM-DD"
attempt_number: 1

scores:
  structural_fidelity: { score: 0, notes: "" }
  parameter_accuracy:  { score: 0, notes: "" }
  content_completeness: { score: 0, notes: "" }
  context_alignment:   { score: 0, notes: "" }
  creative_quality:    { score: 0, notes: "" }

overall_pass: false
gaps_identified: []
refinement_actions: []
```

## Pass/Fail Rules

- **Pass**: All High-weight dimensions >= 4, no dimension < 3
- **Conditional pass**: All High-weight dimensions >= 3, agent documents gaps and refinement plan
- **Fail**: Any High-weight dimension < 3, or two or more dimensions < 3

## Progressive Difficulty

As exemplars increase in difficulty tier, raise the bar:
- **Simple**: Structural fidelity and parameter accuracy are primary; creative quality weight stays Low
- **Intermediate**: Content completeness weight rises to High; context alignment becomes strict
- **Advanced**: Creative quality weight rises to Medium; all dimensions must score >= 4
