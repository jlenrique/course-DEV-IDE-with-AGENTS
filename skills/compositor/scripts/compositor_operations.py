# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Generate a Descript Assembly Guide from a completed manifest."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def load_manifest(manifest_path: str | Path) -> dict[str, Any]:
    """Load a manifest from disk."""
    manifest_path = Path(manifest_path)
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}


def save_markdown(content: str, output_path: str | Path) -> Path:
    """Write the generated guide to disk."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def format_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS.mmm."""
    total_ms = round(seconds * 1000)
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"


def behavioral_note(intent: str | None) -> str:
    """Convert behavioral intent into a practical composition note."""
    notes = {
        "credible": "Keep the pacing restrained and the visual treatment clean and authoritative.",
        "alarming": "Preserve tension through sharper emphasis and avoid softening the transition impact.",
        "moving": "Allow emotional breathing room with slightly longer holds and gentle transitions.",
        "attention-reset": "Use this beat to simplify the frame and reset learner focus before the next idea.",
        "reflective": "Favor quiet pacing and avoid clutter that would break reflective attention.",
        "provocative": "Let the cut and emphasis create productive friction without feeling sensationalized.",
        "urgent": "Keep momentum tight and avoid dead air or overly decorative holds.",
        "clear-guidance": "Optimize for clarity and confidence; avoid unnecessary dramatic treatment.",
        "attention-grabbing": "Open strong and clean so the learner's focus is captured immediately.",
    }
    if not intent:
        return "Preserve the approved instructional tone without adding unnecessary dramatic treatment."
    return notes.get(
        intent,
        f"Preserve the intended `{intent}` effect consistently through pacing, transitions, and emphasis.",
    )


def validate_manifest(manifest: dict[str, Any]) -> None:
    """Fail fast when the manifest is not ready for composition."""
    segments = manifest.get("segments", [])
    if not segments:
        raise ValueError("Manifest has no segments.")
    for segment in segments:
        missing = [
            field
            for field in ("id", "narration_duration", "narration_file", "visual_file")
            if not segment.get(field)
        ]
        if missing:
            raise ValueError(
                f"Segment {segment.get('id', '<unknown>')} missing required fields: {', '.join(missing)}"
            )


def build_timeline_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Build ordered timeline rows with cumulative start times."""
    current_start = 0.0
    rows: list[dict[str, Any]] = []
    for segment in manifest.get("segments", []):
        narration_duration = float(segment["narration_duration"])
        visual_duration = (
            float(segment["visual_duration"])
            if segment.get("visual_duration") is not None
            else narration_duration
        )
        rows.append(
            {
                "id": segment["id"],
                "start": current_start,
                "narration_duration": narration_duration,
                "visual_duration": visual_duration,
                "transition_in": segment.get("transition_in", "none"),
                "transition_out": segment.get("transition_out", "none"),
                "behavioral_intent": segment.get("behavioral_intent"),
                "narration_file": segment["narration_file"],
                "visual_file": segment["visual_file"],
                "sfx_file": segment.get("sfx_file"),
                "music": segment.get("music"),
                "visual_mode": segment.get("visual_mode"),
            }
        )
        current_start += narration_duration
    return rows


def generate_assembly_guide(manifest: dict[str, Any], manifest_path: str | Path) -> str:
    """Generate the human-readable Descript Assembly Guide."""
    validate_manifest(manifest)
    rows = build_timeline_rows(manifest)
    total_runtime = rows[-1]["start"] + rows[-1]["narration_duration"]
    lesson_id = manifest.get("lesson_id", "lesson")
    title = manifest.get("title", lesson_id)

    lines = [
        f"# Descript Assembly Guide — {title}",
        "",
        "## Summary",
        "",
        f"- Lesson ID: `{lesson_id}`",
        f"- Manifest: `{manifest_path}`",
        f"- Total runtime: `{format_timestamp(total_runtime)}`",
        "- Track plan: `V1` visuals, `A1` narration, `A2` music, `A3` SFX",
        "",
        "## Asset Inventory",
        "",
        "| Asset | Track | Segment | Path |",
        "|-------|-------|---------|------|",
    ]
    for row in rows:
        lines.append(f"| Narration | A1 | `{row['id']}` | `{row['narration_file']}` |")
        lines.append(f"| Visual | V1 | `{row['id']}` | `{row['visual_file']}` |")
        if row.get("sfx_file"):
            lines.append(f"| SFX | A3 | `{row['id']}` | `{row['sfx_file']}` |")
    lines.extend(
        [
            "",
            "## Timeline Table",
            "",
            "| Segment | Start | Narration | Visual | Transitions | Behavioral Intent |",
            "|---------|-------|-----------|--------|-------------|-------------------|",
        ]
    )
    for row in rows:
        transitions = f"{row['transition_in']} -> {row['transition_out']}"
        lines.append(
            f"| `{row['id']}` | `{format_timestamp(row['start'])}` | "
            f"`{row['narration_duration']:.2f}s` | `{row['visual_duration']:.2f}s` | "
            f"`{transitions}` | `{row.get('behavioral_intent') or 'none'}` |"
        )

    lines.extend(["", "## Segment-by-Segment Assembly Instructions", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['id']}",
                f"- Start at `{format_timestamp(row['start'])}`",
                f"- Place `{row['visual_file']}` on `V1`",
                f"- Place `{row['narration_file']}` on `A1`",
                f"- Set segment duration to `{row['narration_duration']:.2f}s`",
                f"- Transition in/out: `{row['transition_in']}` / `{row['transition_out']}`",
                f"- Behavioral intent: `{row.get('behavioral_intent') or 'none'}`",
                f"- Intent note: {behavioral_note(row.get('behavioral_intent'))}",
            ]
        )
        if row["visual_mode"] == "static-hold":
            lines.append("- Hold the still visual for the full narration duration.")
        elif row["visual_duration"] != row["narration_duration"]:
            lines.append(
                f"- Adjust or hold the visual so it lands cleanly against the `{row['narration_duration']:.2f}s` narration."
            )
        if row.get("music"):
            lines.append(f"- Music cue: `{row['music']}` on `A2`.")
        if row.get("sfx_file"):
            lines.append(f"- Add `{row['sfx_file']}` on `A3` at the segment start or cue point.")
        lines.append("")

    lines.extend(
        [
            "## Final Check",
            "",
            "- Verify every narration clip starts at the listed timestamp.",
            "- Confirm visual pacing supports the segment's behavioral intent.",
            "- Confirm caption export matches the ElevenLabs VTT timing.",
            "- Export final MP4 + VTT for Quinn-R post-composition review.",
            "",
        ]
    )
    return "\n".join(lines)


def generate_assembly_guide_file(
    manifest_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Generate and save a Descript Assembly Guide from a manifest path."""
    manifest = load_manifest(manifest_path)
    content = generate_assembly_guide(manifest, manifest_path)
    return save_markdown(content, output_path)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(
        description="Generate a Descript Assembly Guide from a completed manifest."
    )
    parser.add_argument("manifest_path")
    parser.add_argument("output_path")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    args = build_parser().parse_args(argv)
    try:
        output = generate_assembly_guide_file(args.manifest_path, args.output_path)
        print(str(output))
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
