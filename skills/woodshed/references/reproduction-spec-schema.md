# Reproduction Spec Schema

The `reproduction-spec.yaml` file in each exemplar directory is the bridge between "here's what good looks like" and "here's what API calls to make." The agent derives this spec during the STUDY phase and executes from it during REPRODUCE.

## Schema

```yaml
tool: gamma | elevenlabs | canvas | qualtrics | canva
api_method: string          # MCP tool name or API client method
parameters:                 # tool-specific API parameters
  key: value
style_guide_overrides:      # which style guide settings apply
  key: value
expected_outputs:           # what the reproduction should produce
  - type: string            # presentation, audio, module, survey, design
    format: string          # url, file, json, etc.
    validation_rules:       # automated checks to verify output
      key: value
```

## Tool-Specific Examples

### Gamma

```yaml
tool: gamma
api_method: generate_content
parameters:
  topic: "Economic Reality of Higher Education"
  num_slides: 10
  theme: "professional-dark"
  style: "lecture"
  additional_instructions: |
    Focus on data visualization for enrollment trends.
    Include speaker notes for each slide.
style_guide_overrides:
  brand_colors: true
expected_outputs:
  - type: presentation
    format: url
    validation_rules:
      min_slides: 10
      must_contain_sections:
        - "Introduction"
        - "Enrollment Data"
```

### ElevenLabs

```yaml
tool: elevenlabs
api_method: text_to_speech
parameters:
  text: "Full narration script text..."
  voice_id: "voice-id-from-style-guide"
  model_id: "eleven_multilingual_v2"
  voice_settings:
    stability: 0.5
    similarity_boost: 0.75
style_guide_overrides:
  output_format: mp3_44100_128
expected_outputs:
  - type: audio
    format: mp3
    validation_rules:
      min_duration_seconds: 45
      max_duration_seconds: 120
```

### Canvas

```yaml
tool: canvas
api_method: create_module_with_items
parameters:
  course_id: "from-style-guide"
  module_name: "Module 1: Economic Reality"
  items:
    - type: page
      title: "Introduction"
      body: "content..."
    - type: quiz
      title: "Knowledge Check"
style_guide_overrides:
  publish_immediately: false
expected_outputs:
  - type: module
    format: json
    validation_rules:
      item_count: 2
      items_types: [page, quiz]
```

## Agent Responsibility

During STUDY, the agent:
1. Examines the exemplar source artifacts
2. Reads the brief to understand intent and quality markers
3. **Derives** this spec — determining which parameters will reproduce the exemplar
4. Saves the spec for use in REPRODUCE and regression runs

The spec is the agent's hypothesis about how to recreate the exemplar. If reproduction fails, the agent refines the spec (up to 3 attempts).
