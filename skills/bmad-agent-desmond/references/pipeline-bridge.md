# APP pipeline ↔ Descript semantics

Use this bridge when translating **compositor** language into **Descript** language. Exact UI labels change by version — **always prefer** the team’s cached docs + `MEMORY.md` over this table when they conflict.

| APP / compositor concept | Typical Descript-facing meaning |
|--------------------------|----------------------------------|
| Segment order in manifest | Same chronological order in the **timeline** / **sequence** (no reordering). |
| `A1` narration | Primary dialogue / voice track (owner may label “VO” or “A1”). |
| `V1` still visual | Image on **video/visual** lane or pinned still; match team convention. |
| Motion / `motion_asset_path` | **Video** clip for playback for stated duration; still is **reference/poster**. |
| `narration_vtt` | Import captions/subtitles aligned to VO; verify timing against rendered audio. |
| Behavioral intent | Editorial pacing/transition feel — not permission to change words. |
| Quinn-R / quality notes | Technical QA context; finishing may address sync without altering instructional intent. |

**Invariant:** The **locked narration script** and **approved assets** are authoritative. Descript operations explain **how to assemble**, not **what to teach**.
