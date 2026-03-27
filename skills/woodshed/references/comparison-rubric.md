# Comparison Rubric Reference

This reference provides guidance for scoring exemplar reproductions. The canonical rubric template lives at `resources/exemplars/_shared/comparison-rubric-template.md`.

## Scoring Dimensions

### Structural Fidelity (Weight: High)

Does the reproduction match the exemplar's structure?

- **Presentations (Gamma)**: Same slide count, same section ordering, same content-per-slide distribution
- **Audio (ElevenLabs)**: Same duration range, same pacing, same section breaks
- **LMS deployment (Canvas)**: Same module structure, same content types, same navigation flow
- **Assessments (Qualtrics)**: Same question count, same question types, same flow logic
- **Designs (Canva)**: Same layout structure, same element positioning, same hierarchy

### Parameter Accuracy (Weight: High)

Were the correct API/MCP parameters used?

Compare `reproduction-spec.yaml` parameters against what the exemplar analysis identifies as optimal. Every parameter choice should be justified by the brief or style guide.

### Content Completeness (Weight: Medium)

Is all key content from the exemplar present?

Check for: key terms, data points, section headings, learning objectives, speaker notes (if applicable). Minor phrasing differences are acceptable; missing content sections are not.

### Context Alignment (Weight: Medium)

Does the reproduction reflect the course/module/lesson context?

Verify: correct course name, module reference, audience tone, learning objective alignment. The reproduction should feel like it belongs in the same course as the exemplar.

### Creative Quality (Weight: Low → grows with difficulty)

How close is the aesthetic/tonal quality?

For simple exemplars, this is a soft check. For advanced exemplars, creative quality becomes a hard requirement — the reproduction should be indistinguishable from the original in professional quality.

## Tool-Specific Comparison Notes

### Gamma
- Compare slide count and section flow (structural)
- Verify theme, style, and additional_instructions parameters (parameter accuracy)
- Check that slide content covers the same key points (content completeness)
- Gamma returns URLs — comparison may require visual inspection or content extraction

### ElevenLabs
- Compare audio duration and pacing (structural)
- Verify voice_id, model_id, stability, similarity_boost parameters (parameter accuracy)
- Spot-check pronunciation of domain-specific terms (content completeness)

### Canvas
- Compare module structure and content types (structural)
- Verify course_id, module positioning, publish settings (parameter accuracy)
- Check page/quiz/assignment content completeness (content completeness)

### Qualtrics
- Compare question count, types, and flow logic (structural)
- Verify survey settings, distribution parameters (parameter accuracy)
- Check question text and answer option completeness (content completeness)
