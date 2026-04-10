# Universal Perception Protocol

Every agent consuming a multimodal artifact must follow this five-step protocol.
No agent may act on an artifact it has not confirmed perceiving.

## The Five Steps

### 1. Receive

The agent receives the artifact file path in its context envelope or delegation input.

### 2. Perceive

The agent invokes the modality-appropriate sensory bridge:

```python
from skills.sensory_bridges.scripts.bridge_utils import perceive

result = perceive(
    artifact_path="path/to/slide.pptx",
    modality="pptx",
    gate="G3",
    requesting_agent="fidelity-assessor"
)
```

### 3. Confirm

The agent states what it perceived in structured format, including confidence level per the calibration rubric:

**Example confirmations:**

- `HIGH`: "I extracted 10 slides from the PPTX. Slide 3 contains text frames: ['The Three Macro Trends', 'Digital transformation...', 'Workforce evolution...', 'Payment model shift...']. All slides have text content."
- `MEDIUM`: "I extracted 10 slides. Slide 7 has no text frames — it may be an image-only slide. Confidence downgraded to MEDIUM."
- `LOW`: "PPTX file could not be parsed. Confidence LOW. Escalating to human."

The confirmation is visible in the agent's output — not silent.

### 4. Proceed

The agent proceeds with its task ONLY if confidence meets the gate-specific threshold (see `confidence-rubric.md`).

### 5. Escalate

If confidence is below threshold, the agent flags the artifact for human interpretation:

"I cannot confidently interpret [artifact]. Confidence: LOW. Reason: [rationale]. Escalating to Marcus for human review."

The agent does NOT guess. It does NOT proceed with a LOW-confidence interpretation in production mode.

## Confirmation Output Format

When an agent confirms perception, it includes this block in its response to the orchestrator:

```yaml
perception_confirmation:
  artifact: "{file path}"
  modality: "{modality}"
  confidence: "{HIGH|MEDIUM|LOW}"
  summary: "{what the agent perceived - 1-3 sentences}"
  gate: "{G0-G6}"
  action: "{proceeding|escalating}"
```

Bridges may also emit modality-specific advisory summaries when they help
downstream pacing or narration decisions:

- Image: `visual_complexity_level`, `visual_complexity_summary`
- Video: `temporal_event_density_level`, `temporal_event_density_summary`

These enrich perception. They do not weaken the requirement to escalate LOW
confidence artifacts.

## Who Must Follow This Protocol

- **Fidelity Assessor** — at every gate it evaluates
- **Quinn-R** — when reviewing PNGs, audio, or composed video
- **Irene (Pass 2)** — when viewing generated slide PNGs before writing narration
- **Gary** — when self-assessing generated slide output
- **Any future agent** consuming non-text artifacts
