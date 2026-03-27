# Narration Script Template

**Pass 2 artifact** — produced after Gary's slides are approved at HIL Gate 2. Always paired with a segment manifest (`template-segment-manifest.md`). Segment IDs in this script must exactly match the manifest entries.

## Header

- **Lesson Plan Reference:** LP-{module_id}{lesson_id}
- **Script ID:** NS-{module_id}{lesson_id}-{sequence}
- **Paired Slide Brief:** SB-{module_id}{lesson_id}-{sequence}
- **Paired Segment Manifest:** `course-content/staging/{lesson_id}/manifest.yaml`
- **Learning Objective:** {specific objective this narration serves}
- **Bloom's Level:** {level}
- **Pass:** 2 (written after Gary's slides reviewed and approved)

## Script Body

For each slide/segment — segment IDs must match `[SEGMENT: seg-XX]` markers exactly:

---

[SEGMENT: seg-01]

**[Gary Slide: {gary_slide_id} — {visual_description from gary_slide_output}]**

**Stage Directions:**
- Tone: {conversational clinical | formal academic | empathetic narrative}
- Pacing: {measured/deliberate | conversational flow | building urgency}
- Emphasis: {key phrases to stress, marked with *asterisks*}

**Narration:**
{The actual narration text, written by Paige or Sophia, reviewed for pedagogical alignment.
Complement the visual — narrate the insight, not the structure. If Gary's slide shows a
three-column comparison, narrate "Notice how the revenue gap widens in each decade" not
"This slide shows three columns."}

**Transition to next segment:**
{How this segment connects to the next — pedagogical bridge}

---

[SEGMENT: seg-02]

**[Gary Slide: {gary_slide_id} — {visual_description}]** (or **[Kira B-roll: {description}]**)

...repeat for each segment...

---

## Downstream Consumption — ElevenLabs

- **Suggested Voice ID:** {voice from style guide or learned preference}
- **Estimated Duration:** {word count ÷ 150 wpm = minutes}
- **Pronunciation Guide:**
  | Term | Pronunciation |
  |------|--------------|
  | {medical term} | {phonetic guide} |
- **Audio Notes:** {voice style notes, SFX cues per segment, music bed direction}

## Downstream Consumption — Segment Manifest

Every `[SEGMENT: seg-XX]` marker must have a corresponding entry in the paired manifest.yaml.
Irene populates `narration_text` and `visual_cue` in the manifest from this script.
ElevenLabs writes back `narration_duration`, `narration_file`, `narration_vtt` after generation.
