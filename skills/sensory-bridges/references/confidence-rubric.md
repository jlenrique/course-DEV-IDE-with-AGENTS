# Confidence Calibration Rubric

Operational definitions for HIGH, MEDIUM, and LOW confidence by modality.
Agents must use these definitions — not personal judgment — when assigning confidence.

## Image (PNG/JPG)

| Level | Criteria |
|-------|----------|
| **HIGH** | All text blocks extracted with ≥95% confidence; layout unambiguous; all visual elements identifiable |
| **MEDIUM** | Text extraction 80-95% confidence OR layout ambiguous (overlapping elements, complex diagrams) OR ≥1 visual element unidentifiable |
| **LOW** | Text extraction <80% confidence OR layout unparseable OR image corrupt/blank |

## Audio (MP3/WAV)

| Level | Criteria |
|-------|----------|
| **HIGH** | Estimated WER <5%; no unintelligible segments; medical terms recognized (per keyterm prompting) |
| **MEDIUM** | WER 5-15% estimated OR ≥1 unintelligible segment <3s OR ≥1 medical term unrecognized |
| **LOW** | WER >15% OR unintelligible segments >3s OR heavy background noise |

## PDF

| Level | Criteria |
|-------|----------|
| **HIGH** | All pages have machine-readable text (≥50 chars per page) |
| **MEDIUM** | ≥1 page detected as scanned (< 50 chars) but some text extracted via OCR heuristic |
| **LOW** | ≥1 page completely unreadable; fully scanned without usable text; corrupt file |

## PPTX

| Level | Criteria |
|-------|----------|
| **HIGH** | All slides parsed; all have text frames; valid PPTX structure |
| **MEDIUM** | ≥1 slide with extraction errors or no text frames (may be intentional image-only slide) |
| **LOW** | File corrupt or unparseable; no slides extracted |

## Video (MP4/WebM)

| Level | Criteria |
|-------|----------|
| **HIGH** | Keyframes extracted AND audio transcribed with HIGH audio confidence |
| **MEDIUM** | Partial extraction: keyframes OR audio succeeded but not both; or audio at MEDIUM confidence |
| **LOW** | Neither keyframes nor audio transcript produced; corrupt or unprocessable file |

## Gate-Specific Thresholds

Minimum confidence required to proceed (escalate to human if below):

| Production Mode | Minimum for Proceed |
|----------------|:---:|
| **Ad-hoc** | MEDIUM |
| **Production** | HIGH |
| **Regulated** | HIGH (all modalities, no exceptions) |

## Calibration Note

These thresholds are initial estimates. During early production runs, empirically calibrate
by comparing agent perception against human ground truth. Update the rubric and capture
calibration data in the Fidelity Assessor's memory sidecar.
