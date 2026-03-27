# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Agent-level ElevenLabs operations wrapper.

Bridges the Voice Director's decisions and the ElevenLabs API client layer.
Handles style-guide loading, VTT generation, pronunciation dictionary authoring,
and structured result formatting for Marcus-mediated workflows.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
import xml.sax.saxutils as xml_utils

from dotenv import load_dotenv
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.api_clients.elevenlabs_client import ElevenLabsClient

load_dotenv(PROJECT_ROOT / ".env")

STYLE_GUIDE_PATH = PROJECT_ROOT / "state" / "config" / "style_guide.yaml"
STAGING_DIR = PROJECT_ROOT / "course-content" / "staging"


def load_style_guide_elevenlabs() -> dict[str, Any]:
    """Load ElevenLabs defaults from the mutable style guide."""
    if not STYLE_GUIDE_PATH.exists():
        return {}
    data = yaml.safe_load(STYLE_GUIDE_PATH.read_text(encoding="utf-8")) or {}
    return data.get("tool_parameters", {}).get("elevenlabs", {})


def merge_parameters(
    style_defaults: dict[str, Any],
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge style-guide defaults with per-request overrides."""
    merged: dict[str, Any] = {}
    for source in [style_defaults, overrides or {}]:
        for key, value in source.items():
            if value is not None and value != "":
                merged[key] = value
    return merged


def build_pronunciation_pls(
    terms: dict[str, str],
    *,
    alphabet: str = "ipa",
    locale: str = "en-US",
) -> str:
    """Build a minimal PLS document from grapheme -> pronunciation mappings."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<lexicon version="1.0"',
        '    xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"',
        '    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '    xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon',
        '        http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"',
        f'    alphabet="{alphabet}" xml:lang="{locale}">',
    ]
    for term, pronunciation in terms.items():
        lines.extend(
            [
                "<lexeme>",
                f"    <grapheme>{xml_utils.escape(term)}</grapheme>",
                f"    <phoneme>{xml_utils.escape(pronunciation)}</phoneme>",
                "</lexeme>",
            ]
        )
    lines.append("</lexicon>")
    return "\n".join(lines) + "\n"


def _format_vtt_timestamp(value: float) -> str:
    """Format seconds as a WebVTT timestamp."""
    total_ms = max(0, round(value * 1000))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


def alignment_to_vtt(alignment: dict[str, Any] | None) -> str:
    """Convert ElevenLabs character alignment to a word-level WebVTT track."""
    if not alignment:
        return "WEBVTT\n\n"

    characters = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    ends = alignment.get("character_end_times_seconds", [])
    cues: list[tuple[float, float, str]] = []
    current_chars: list[str] = []
    current_start: float | None = None
    current_end: float | None = None

    for char, start, end in zip(characters, starts, ends):
        if char.isspace():
            if current_chars and current_start is not None and current_end is not None:
                cues.append((current_start, current_end, "".join(current_chars)))
                current_chars = []
                current_start = None
                current_end = None
            continue

        if current_start is None:
            current_start = start
        current_end = end
        current_chars.append(char)

    if current_chars and current_start is not None and current_end is not None:
        cues.append((current_start, current_end, "".join(current_chars)))

    lines = ["WEBVTT", ""]
    for index, (start, end, text) in enumerate(cues, start=1):
        lines.append(str(index))
        lines.append(f"{_format_vtt_timestamp(start)} --> {_format_vtt_timestamp(end)}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def load_manifest(manifest_path: str | Path) -> dict[str, Any]:
    """Load a YAML segment manifest from disk."""
    manifest_path = Path(manifest_path)
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}


def save_manifest(manifest: dict[str, Any], manifest_path: str | Path) -> Path:
    """Save a YAML segment manifest back to disk."""
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )
    return manifest_path


def generate_narration(
    text: str,
    *,
    output_dir: str | Path | None = None,
    filename_stem: str = "narration",
    voice_id: str | None = None,
    parameter_overrides: dict[str, Any] | None = None,
    pronunciation_dictionary_locators: list[dict[str, str]] | None = None,
    previous_request_ids: list[str] | None = None,
    next_request_ids: list[str] | None = None,
    client: ElevenLabsClient | None = None,
) -> dict[str, Any]:
    """Generate narration audio + VTT using style-guide defaults and overrides."""
    if client is None:
        client = ElevenLabsClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    merged = merge_parameters(load_style_guide_elevenlabs(), parameter_overrides)
    resolved_voice_id = voice_id or merged.get("default_voice_id")
    if not resolved_voice_id:
        raise ValueError("No ElevenLabs voice_id available from args or style guide.")

    audio_path = output_dir / f"{filename_stem}.mp3"
    vtt_path = output_dir / f"{filename_stem}.vtt"
    result = client.text_to_speech_with_timestamps_file(
        text,
        resolved_voice_id,
        audio_path,
        model_id=merged.get("model_id", "eleven_multilingual_v2"),
        stability=merged.get("stability", 0.5),
        similarity_boost=merged.get("similarity_boost", 0.75),
        style=merged.get("style", 0.0),
        output_format=merged.get("output_format", "mp3_44100_128"),
        pronunciation_dictionary_locators=pronunciation_dictionary_locators,
        previous_request_ids=previous_request_ids,
        next_request_ids=next_request_ids,
    )
    vtt_path.write_text(
        alignment_to_vtt(result.get("normalized_alignment") or result.get("alignment")),
        encoding="utf-8",
    )
    alignment = result.get("normalized_alignment") or result.get("alignment") or {}
    ends = alignment.get("character_end_times_seconds", [])
    duration_seconds = ends[-1] if ends else 0.0
    return {
        "status": "success",
        "voice_id": resolved_voice_id,
        "audio_path": str(audio_path),
        "vtt_path": str(vtt_path),
        "request_id": result.get("request_id"),
        "narration_duration": duration_seconds,
        "output_format": result.get("output_format"),
    }


def generate_manifest_narration(
    manifest_path: str | Path,
    *,
    output_dir: str | Path | None = None,
    parameter_overrides: dict[str, Any] | None = None,
    default_voice_id: str | None = None,
    client: ElevenLabsClient | None = None,
) -> dict[str, Any]:
    """Generate narration for each manifest segment and write results back.

    This is the pipeline bridge used by Marcus:
    Irene manifest -> ElevenLabs narration assets -> updated manifest.
    """
    if client is None:
        client = ElevenLabsClient()
    manifest = load_manifest(manifest_path)
    lesson_id = manifest.get("lesson_id", "lesson")
    base_output_dir = Path(output_dir) if output_dir else STAGING_DIR / lesson_id
    audio_dir = base_output_dir / "audio"
    captions_dir = base_output_dir / "captions"
    audio_dir.mkdir(parents=True, exist_ok=True)
    captions_dir.mkdir(parents=True, exist_ok=True)

    merged = merge_parameters(load_style_guide_elevenlabs(), parameter_overrides)
    resolved_default_voice_id = default_voice_id or merged.get("default_voice_id")
    if not resolved_default_voice_id:
        raise ValueError("No ElevenLabs default voice available for manifest processing.")

    previous_request_ids: list[str] = []
    outputs: list[dict[str, Any]] = []
    for segment in manifest.get("segments", []):
        segment_id = segment.get("id", "segment")
        narration_text = (segment.get("narration_text") or "").strip()
        if not narration_text:
            segment["narration_duration"] = 0.0
            segment["narration_file"] = None
            segment["narration_vtt"] = None
            segment.setdefault("sfx_file", None)
            continue

        voice_id = segment.get("voice_id") or resolved_default_voice_id
        result = generate_narration(
            narration_text,
            output_dir=audio_dir,
            filename_stem=segment_id,
            voice_id=voice_id,
            parameter_overrides=parameter_overrides,
            previous_request_ids=previous_request_ids or None,
            client=client,
        )

        # Move the generated VTT into the captions folder while keeping the API of
        # generate_narration simple for single-file usage.
        audio_path = Path(result["audio_path"])
        generated_vtt_path = Path(result["vtt_path"])
        final_vtt_path = captions_dir / f"{segment_id}.vtt"
        if generated_vtt_path != final_vtt_path:
            final_vtt_path.write_text(
                generated_vtt_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            generated_vtt_path.unlink()

        segment["narration_duration"] = result["narration_duration"]
        segment["narration_file"] = str(audio_path)
        segment["narration_vtt"] = str(final_vtt_path)
        segment.setdefault("sfx_file", None)

        sfx_cue = segment.get("sfx")
        if sfx_cue:
            sfx_result = generate_sound_effect(
                sfx_cue,
                output_dir=audio_dir,
                filename=f"{segment_id}-sfx.mp3",
                client=client,
            )
            segment["sfx_file"] = sfx_result["sfx_path"]

        if result.get("request_id"):
            previous_request_ids = [result["request_id"]]

        outputs.append(
            {
                "segment_id": segment_id,
                "voice_id": voice_id,
                "request_id": result.get("request_id"),
                "narration_duration": result["narration_duration"],
                "narration_file": segment["narration_file"],
                "narration_vtt": segment["narration_vtt"],
                "sfx_file": segment.get("sfx_file"),
            }
        )

    saved_path = save_manifest(manifest, manifest_path)
    return {
        "status": "success",
        "manifest_path": str(saved_path),
        "narration_outputs": outputs,
    }


def create_pronunciation_dictionary(
    name: str,
    terms: dict[str, str],
    *,
    output_dir: str | Path | None = None,
    description: str | None = None,
    client: ElevenLabsClient | None = None,
) -> dict[str, Any]:
    """Create a PLS file locally and upload it to ElevenLabs."""
    if client is None:
        client = ElevenLabsClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pls_path = output_dir / f"{name}.pls"
    pls_path.write_text(build_pronunciation_pls(terms), encoding="utf-8")
    created = client.create_pronunciation_dictionary_from_file(
        name,
        pls_path,
        description=description,
    )
    created["local_pls_path"] = str(pls_path)
    return created


def generate_sound_effect(
    text: str,
    *,
    output_dir: str | Path | None = None,
    filename: str = "sfx.mp3",
    client: ElevenLabsClient | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate a sound effect and save it locally."""
    if client is None:
        client = ElevenLabsClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_path = Path(output_dir) / filename
    client.text_to_sound_effect_file(text, output_path, **kwargs)
    return {"status": "success", "sfx_path": str(output_path)}


def generate_dialogue(
    inputs: list[dict[str, str]],
    *,
    output_dir: str | Path | None = None,
    filename: str = "dialogue.mp3",
    client: ElevenLabsClient | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate multi-speaker dialogue and save it locally."""
    if client is None:
        client = ElevenLabsClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_path = Path(output_dir) / filename
    client.text_to_dialogue_file(inputs, output_path, **kwargs)
    return {"status": "success", "dialogue_path": str(output_path)}


def generate_music(
    *,
    output_dir: str | Path | None = None,
    filename: str = "music.mp3",
    client: ElevenLabsClient | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate background music and save it locally."""
    if client is None:
        client = ElevenLabsClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_path = Path(output_dir) / filename
    client.generate_music_file(output_path, **kwargs)
    return {"status": "success", "music_path": str(output_path)}


def build_parser() -> argparse.ArgumentParser:
    """Build a CLI for agent-driven execution and smoke checks."""
    parser = argparse.ArgumentParser(
        description="Run ElevenLabs operations and return structured JSON."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    narration = subparsers.add_parser("narration", help="Generate narration + VTT")
    narration.add_argument("text")
    narration.add_argument("--voice-id")
    narration.add_argument("--output-dir")
    narration.add_argument("--filename-stem", default="narration")

    dictionary = subparsers.add_parser(
        "dictionary", help="Create pronunciation dictionary from JSON terms"
    )
    dictionary.add_argument("name")
    dictionary.add_argument("terms_json")
    dictionary.add_argument("--output-dir")
    dictionary.add_argument("--description")

    sfx = subparsers.add_parser("sfx", help="Generate sound effect")
    sfx.add_argument("text")
    sfx.add_argument("--output-dir")
    sfx.add_argument("--filename", default="sfx.mp3")

    manifest = subparsers.add_parser(
        "manifest", help="Generate narration for all manifest segments"
    )
    manifest.add_argument("manifest_path")
    manifest.add_argument("--output-dir")
    manifest.add_argument("--default-voice-id")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "narration":
            result = generate_narration(
                args.text,
                output_dir=args.output_dir,
                filename_stem=args.filename_stem,
                voice_id=args.voice_id,
            )
        elif args.command == "dictionary":
            result = create_pronunciation_dictionary(
                args.name,
                json.loads(args.terms_json),
                output_dir=args.output_dir,
                description=args.description,
            )
        elif args.command == "manifest":
            result = generate_manifest_narration(
                args.manifest_path,
                output_dir=args.output_dir,
                default_voice_id=args.default_voice_id,
            )
        else:
            result = generate_sound_effect(
                args.text,
                output_dir=args.output_dir,
                filename=args.filename,
            )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - CLI path
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
