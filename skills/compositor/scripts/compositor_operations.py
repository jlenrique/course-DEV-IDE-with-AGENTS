# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Generate a Descript Assembly Guide from a completed manifest."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


def load_manifest(manifest_path: str | Path) -> dict[str, Any]:
    """Load a manifest from disk."""
    manifest_path = Path(manifest_path)
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}


def find_repo_root(start: Path) -> Path:
    """Walk parents from ``start`` until a directory containing ``.git`` is found."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise FileNotFoundError(
        "Could not locate repository root (no .git directory in parents of "
        f"{start}). Pass repo_root explicitly if working outside a git clone."
    )


def sync_approved_visuals_to_assembly_bundle(
    manifest_path: str | Path,
    *,
    visuals_subdir: str = "visuals",
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Copy segment ``visual_file`` assets next to the manifest and rewrite paths.

    Approved slides often live under a Gary/Gamma export tree. For a completed
    assembly bundle (audio, captions, guide, summaries), copy those stills into
    ``<manifest_dir>/<visuals_subdir>/`` and update each segment's ``visual_file``
    to the new repo-relative path so Descript and reviewers use one folder.
    """
    manifest_path = Path(manifest_path).resolve()
    root = Path(repo_root).resolve() if repo_root else find_repo_root(manifest_path)
    manifest = load_manifest(manifest_path)
    segments = manifest.get("segments", [])
    if not segments:
        raise ValueError("Manifest has no segments.")

    dest_dir = (manifest_path.parent / visuals_subdir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    copies: list[dict[str, str]] = []
    for segment in segments:
        rel_visual = segment.get("visual_file")
        if not rel_visual:
            raise ValueError(f"Segment {segment.get('id', '<unknown>')} missing visual_file.")
        src = (root / rel_visual).resolve()
        if not src.is_file():
            raise FileNotFoundError(f"Visual not found for {segment.get('id')}: {src}")

        dest_file = dest_dir / src.name
        if dest_file.resolve() != src.resolve():
            shutil.copy2(src, dest_file)

        new_rel = (dest_file.relative_to(root)).as_posix()
        if rel_visual != new_rel:
            copies.append({"segment": segment["id"], "from": rel_visual, "to": new_rel})

    text = manifest_path.read_text(encoding="utf-8")
    for item in copies:
        old, new = item["from"], item["to"]
        occurrences = text.count(old)
        if occurrences != 1:
            raise ValueError(
                "Refusing manifest edit: path "
                f"{old!r} appears {occurrences} times in {manifest_path} (expected 1)."
            )
        text = text.replace(old, new)
    if copies:
        manifest_path.write_text(text, encoding="utf-8")

    return {
        "manifest_path": str(manifest_path),
        "visuals_dir": str(dest_dir),
        "copies": copies,
    }


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
    """Build CLI parser (subcommands + legacy two-arg guide mode)."""
    parser = argparse.ArgumentParser(
        description="Compositor: sync approved visuals into the assembly bundle and/or "
        "generate a Descript Assembly Guide."
    )
    sub = parser.add_subparsers(dest="command")

    guide = sub.add_parser("guide", help="Generate Descript Assembly Guide markdown.")
    guide.add_argument("manifest_path")
    guide.add_argument("output_path")

    sync = sub.add_parser(
        "sync-visuals",
        help="Copy approved visual_file assets next to the manifest; update manifest paths.",
    )
    sync.add_argument("manifest_path")
    sync.add_argument(
        "--subdir",
        default="visuals",
        help="Folder under the manifest directory for copied stills (default: visuals).",
    )
    sync.add_argument(
        "--repo-root",
        default=None,
        help="Repository root (defaults to parent chain containing .git).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    raw = list(sys.argv[1:] if argv is None else argv)
    if len(raw) >= 2 and raw[0] not in ("guide", "sync-visuals", "--help", "-h"):
        raw = ["guide", *raw]

    args = build_parser().parse_args(raw)
    try:
        if getattr(args, "command", None) is None:
            build_parser().print_help()
            return 2
        if args.command == "sync-visuals":
            summary = sync_approved_visuals_to_assembly_bundle(
                args.manifest_path,
                visuals_subdir=args.subdir,
                repo_root=args.repo_root,
            )
            print(yaml.dump(summary, default_flow_style=False, sort_keys=False).strip())
            return 0
        if args.command == "guide":
            output = generate_assembly_guide_file(args.manifest_path, args.output_path)
            print(str(output))
            return 0
        build_parser().print_help()
        return 2
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
