#!/usr/bin/env python3
"""Run a direct STT heartbeat for Marcus-compatible transcription providers."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run STT heartbeat against one audio file and print normalized result."
    )
    parser.add_argument(
        "--audio-path",
        type=Path,
        required=True,
        help="Path to audio clip (.wav/.mp3/etc.) used for heartbeat.",
    )
    parser.add_argument(
        "--provider",
        choices=("auto", "elevenlabs", "openai"),
        default="auto",
        help="STT provider strategy. auto = ElevenLabs primary + OpenAI fallback.",
    )
    parser.add_argument(
        "--keyterm",
        action="append",
        default=[],
        help="Optional keyterm bias for ElevenLabs provider (repeatable).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    from marcus.orchestrator.voice_interface import build_chunk_transcriber

    args = _build_parser().parse_args(argv)
    if not args.audio_path.exists():
        print(f"audio file not found: {args.audio_path}", file=sys.stderr)
        return 2

    transcriber = build_chunk_transcriber(
        args.provider,
        keyterms=list(args.keyterm),
    )
    result = transcriber.transcribe_chunk(args.audio_path)

    print(
        json.dumps(
            {
                "provider": args.provider,
                "audio_path": str(args.audio_path),
                "confidence": result.confidence,
                "transcript_text": result.transcript_text,
                "confidence_rationale": result.confidence_rationale,
            },
            indent=2,
        )
    )
    return 0 if result.transcript_text.strip() else 1


if __name__ == "__main__":
    raise SystemExit(main())

