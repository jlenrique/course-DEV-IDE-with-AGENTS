# Story 3.5: Compositor Skill (Descript Assembly Guide + Intent Fidelity Formalization)

Status: done

## Story

As a user,
I want a Compositor skill that reads a completed segment manifest and generates a Descript Assembly Guide,
so that assembling the final lesson video in Descript is fast, accurate, reproducible, and faithful to both the instructional purpose and the intended behavioral/affective impact.

## Acceptance Criteria

1. `skills/compositor/SKILL.md` exists with a clear assembly-guide generation workflow
2. `skills/compositor/scripts/compositor_operations.py` reads a completed manifest and generates a Descript Assembly Guide
3. The generated guide includes ordered asset list, track assignments, timing table, music cues, transition specs, and segment-by-segment assembly instructions
4. The guide also surfaces `behavioral_intent` / affective-direction information so the human assembler can preserve the intended impact during composition
5. `skills/compositor/scripts/tests/test_compositor_operations.py` covers manifest parsing and guide generation
6. Marcus references the Compositor as active and routes completed manifests to it after Quinn-R pre-composition validation
7. `behavioral_intent` is formalized in Irene’s upstream artifacts at the lesson-plan, slide-brief, narration-script, and manifest levels
8. Gary’s quality/self-assessment guidance explicitly checks whether the slide output matches the intended behavioral/affective effect
9. Quinn-R’s review protocol explicitly checks `intent_fidelity` / affective-goal alignment early enough to catch weak creative choices before the pipeline gets expensive
10. A proof-of-concept completed manifest and generated Descript Assembly Guide exist in staging for a real-ish lesson slice

## Tasks / Subtasks

- [x] Task 1: Formalize behavioral/affective intent as a first-class contract (AC: #7, #8, #9)
  - [x] 1.1 Add a lesson/block-level behavioral-intent field to Irene’s lesson plan template
  - [x] 1.2 Add a slide-level behavioral-intent field to Irene’s slide brief template
  - [x] 1.3 Add a segment-level behavioral-intent field to Irene’s narration script template
  - [x] 1.4 Add a machine-readable `behavioral_intent` field to the segment manifest template
  - [x] 1.5 Update Gary’s quality-assessment guidance to check intent fidelity
  - [x] 1.6 Update Quinn-R’s review protocol to include intent-fidelity review alongside audio/composition checks
  - [x] 1.7 Update Marcus checkpoint guidance so HIL Gate 2 / Gate 3 surface intended effect explicitly

- [x] Task 2: Build the compositor skill (AC: #1, #2, #3, #4, #5)
  - [x] 2.1 Create `skills/compositor/SKILL.md`
  - [x] 2.2 Create `skills/compositor/references/assembly-guide-format.md`
  - [x] 2.3 Create `skills/compositor/references/manifest-interpretation.md`
  - [x] 2.4 Create `skills/compositor/scripts/compositor_operations.py`
  - [x] 2.5 Create `skills/compositor/scripts/tests/test_compositor_operations.py`

- [x] Task 3: Integrate compositor into Marcus-facing workflow docs (AC: #6)
  - [x] 3.1 Update Marcus skill/status references from planned -> active for compositor
  - [x] 3.2 Ensure Marcus delegation docs show completed manifest -> compositor -> Descript handoff

- [x] Task 4: Produce proof-of-concept output (AC: #10)
  - [x] 4.1 Create a completed sample manifest in staging with narration + visual + intent fields populated
  - [x] 4.2 Generate a Descript Assembly Guide from that manifest
  - [x] 4.3 Verify the guide is human-readable and preserves behavioral/affective intent in the instructions

- [x] Task 5: Validate and record Story 3.5 readiness (AC: #1-#10)
  - [x] 5.1 Run compositor unit tests
  - [x] 5.2 Run focused regression tests on updated templates/protocol files as appropriate
  - [x] 5.3 Update story/status artifacts to review state if validation passes

## Dev Notes

### Party Mode Consensus

- **Winston:** `behavioral_intent` should be a first-class production field, not an optional HIL comment.
- **Amelia:** `3.5` is the right slice to add that field end-to-end because the compositor is where intent has to survive final assembly.
- **Quinn:** early review needs an explicit `intent_fidelity` check so Gary and Quinn-R can catch “lame but technically correct” outputs before the expensive downstream steps.

### Design Direction

- Use a single machine-readable field name: `behavioral_intent`
- Irene owns the first authored/recommended value
- Marcus surfaces it at HIL gates so Juan can accept, revise, or override it
- Gary uses it as part of slide success criteria
- ElevenLabs uses it as a delivery-direction cue
- Quinn-R checks intent fidelity at review time
- Compositor surfaces it as assembly guidance for the human in Descript

### Existing Infrastructure To Reuse

| Component | Location | Reuse For |
|-----------|----------|-----------|
| Segment manifest contract | `skills/bmad-agent-content-creator/references/template-segment-manifest.md` | Extend with `behavioral_intent` |
| ElevenLabs manifest write-back path | `skills/elevenlabs-audio/scripts/elevenlabs_operations.py` | Existing completed-manifest producer |
| Marcus composition handoff docs | `skills/bmad-agent-marcus/references/conversation-mgmt.md` | Update compositor routing |
| Quinn-R review protocol | `skills/bmad-agent-quality-reviewer/references/review-protocol.md` | Add intent fidelity and keep protocol aligned with actual pipeline |
| Gary quality-assessment format | `skills/bmad-agent-gamma/references/quality-assessment.md` | Add intent-fidelity self-check |

### File Structure (Expected Output)

```
skills/
└── compositor/
    ├── SKILL.md
    ├── references/
    │   ├── assembly-guide-format.md
    │   └── manifest-interpretation.md
    └── scripts/
        ├── compositor_operations.py
        └── tests/
            └── test_compositor_operations.py
```

## Dev Agent Record

### Debug Log References

- Story created after party-mode consensus to fold `behavioral_intent` into the actual production contract before compositor work proceeds
- Party-mode consensus field name: `behavioral_intent`
- Compositor unit suite: `4 passed`
- Combined focused 3.4/3.5 suite: `31 passed`
- Proof-of-concept guide generated at `course-content/staging/C1-M1-L1/descript-assembly-guide.md`

### Completion Notes List

- Story initialized directly on `story3-4-elevenlabs-specialist` after 3.4 review closure
- Formalized `behavioral_intent` across Irene templates and the machine-readable segment manifest
- Updated Gary self-assessment guidance and Quinn-R review protocol to check intent fidelity explicitly
- Built the compositor skill and generated a Descript Assembly Guide from a completed manifest
- Activated compositor routing in Marcus references

### File List

**Created:**
- `_bmad-output/implementation-artifacts/3-5-compositor-skill.md`
- `skills/compositor/SKILL.md`
- `skills/compositor/references/assembly-guide-format.md`
- `skills/compositor/references/manifest-interpretation.md`
- `skills/compositor/scripts/compositor_operations.py`
- `skills/compositor/scripts/tests/test_compositor_operations.py`
- `course-content/staging/C1-M1-L1/manifest.yaml`
- `course-content/staging/C1-M1-L1/descript-assembly-guide.md`
- `course-content/staging/C1-M1-L1/visuals/seg-01.png`

**Modified:**
- `skills/bmad-agent-content-creator/references/template-lesson-plan.md`
- `skills/bmad-agent-content-creator/references/template-slide-brief.md`
- `skills/bmad-agent-content-creator/references/template-narration-script.md`
- `skills/bmad-agent-content-creator/references/template-segment-manifest.md`
- `skills/bmad-agent-gamma/references/quality-assessment.md`
- `skills/bmad-agent-quality-reviewer/SKILL.md`
- `skills/bmad-agent-quality-reviewer/references/review-protocol.md`
- `skills/bmad-agent-marcus/SKILL.md`
- `skills/bmad-agent-marcus/references/conversation-mgmt.md`
- `skills/bmad-agent-marcus/references/checkpoint-coord.md`

### Change Log

- 2026-03-27: Story file created and implementation started
- 2026-03-27: Story implemented, validated, and moved to review
