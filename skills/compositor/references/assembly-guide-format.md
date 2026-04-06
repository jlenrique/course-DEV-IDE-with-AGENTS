# Assembly Guide Format

The generated guide should contain these sections in order:

1. **Summary**
   - lesson id / title
   - manifest path
   - total runtime
   - composition assumptions

2. **Asset Inventory**
   - every referenced narration, visual, SFX, and music asset
   - intended track assignment

3. **Timeline Table**
   - segment id
   - start time
   - narration duration
   - visual duration
   - transition in/out
   - behavioral intent

4. **Segment-by-Segment Assembly Instructions**
   - what to place on V1/A1/A2/A3
   - trim/hold guidance
   - intent-preservation note
   - visual reference cues (Story 13.3): for each `visual_references[]` entry, note the `narration_cue` phrase and `location_on_slide` so the human editor can verify the visual element is visible when that narration phrase plays

5. **Final Check**
   - confirm cues before export
