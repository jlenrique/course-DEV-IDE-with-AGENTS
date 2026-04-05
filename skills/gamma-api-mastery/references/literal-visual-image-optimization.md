# Literal-Visual Image Optimization for Gamma Template API

Reference for preparing source images that maximize success with the Gamma
`/generations/from-template` endpoint (template `g_gior6s13mvpk8ms`).

API reference: https://developers.gamma.app/llms-full.txt

## How Gamma Places Images in Templates

Gamma's AI automatically classifies images into one of two placement modes
when processing a template prompt. **This classification cannot be controlled
via the API** (confirmed by Gamma docs and live testing 2026-04-05).

| Mode | Fills card? | Opacity | Triggered by |
|------|------------|---------|-------------|
| **Background** | Yes (edge-to-edge) | Faded by default | Images with high visual density, dark tones, photographic content |
| **Accent** | No (cropped/positioned) | Full | Diagrammatic images, infographics, images with significant whitespace |

The anti-fade prompt ("at full opacity, not as background, not faded") can
override the opacity reduction for background-classified images but cannot
force accent-classified images into background placement.

## Optimal Image Attributes for Template Success

Images meeting these criteria are most likely to receive **background**
classification (full-bleed placement) from Gamma's AI:

### Dimensions and File Size

| Attribute | Recommended | Tested-Good | Tested-Fail |
|-----------|-------------|-------------|-------------|
| Width | 1376-1920 px | 1376 px | 2752 px |
| Height | 768-1080 px | 768 px | 1536 px |
| Megapixels | ~1-2 MP | 1.06 MP | 4.23 MP |
| File size | < 2 MB | 1.2 MB | 5.4 MB |
| Aspect ratio | 16:9 (1.778) | 1.792 | 1.792 |

Smaller images appear to receive more favorable classification, though
image content is the primary classification factor (see below).

### Visual Content Characteristics

**Favorable for background classification (full-bleed):**
- High visual density across the full frame
- Photographic or scene-based content
- Dark or medium tones
- Minimal whitespace at edges
- Strong edge-to-edge visual weight (content reaches all borders)

**Unfavorable (likely accent classification, cropped):**
- Diagrammatic / infographic style
- Significant whitespace or light margins
- Isolated graphic elements on white background
- Content concentrated in center with empty edges

### Format and Metadata

| Attribute | Requirement |
|-----------|-------------|
| Format | PNG (required by pipeline) |
| Color mode | RGB (no alpha channel) |
| DPI | Any (Gamma ignores DPI) |
| ICC profile | Not required |
| EXIF | No effect observed |

## Pipeline Behavior

The literal-visual dispatch in `gamma_operations.py` uses a
**best-effort template → composite fallback** strategy:

1. **Template attempt** (1 try): Dispatches to Gamma with the anti-fade
   prompt. If Gamma classifies the image as background and renders it
   full-bleed, the template export is used (preserves the Gamma "set").

2. **Fill validation**: `validate_visual_fill()` checks the exported PNG
   using two complementary signals:
   - **Edge-band sampling** (8px bands, 90% threshold) — detects blank borders
   - **Content variance** (`content_stddev`) — detects blank or faded slides
     even when edge content is light-colored. Thresholds: blank < 5,
     faded < 25, real content >= 25, infographic override > 40.

3. **Composite fallback**: `_composite_full_bleed()` scales and
   center-crops the source PNG to 2400x1350. Guaranteed full-bleed,
   full opacity, deterministic. When no local preintegration PNG is
   available, the system downloads from the hosted URL first. Output
   flows through the same pipeline (sorting, provenance, Irene handoff)
   as template-generated slides. Provenance tracked via
   `literal_visual_source` field: `template`, `composite-preintegration`,
   or `composite-download`.

## Preparing Images for Best Results

1. **Resize oversized images** to ≤ 1920x1080 before hosting.
2. **Minimize edge whitespace** — crop or extend content to reach borders.
3. **Prefer photographic or visually dense compositions** when creating
   literal-visual source assets.
4. **Test with the prompt harness** before committing to a production run:
   `pytest test_literal_visual_prompt_harness.py --run-live-e2e -v -s`

## Template Details

- **Template ID**: `g_gior6s13mvpk8ms` (Image Card, beta)
- **Image source**: `placeholder` (no AI image generation)
- **API limitation**: `imageOptions.source` is rejected by the template
  endpoint (HTTP 400). Only `imageOptions.model` and `imageOptions.style`
  are accepted, and only when the template uses `aiGenerated` source.
- **Anti-fade prompt**: "Replace the placeholder image with this image at
  full opacity (not as background, not faded). The image must be the
  primary visual element filling the entire card. No text overlay."
