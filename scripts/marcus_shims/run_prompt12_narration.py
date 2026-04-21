"""Marcus shim — Prompt 12 ElevenLabs narration synthesis.

Invokes `elevenlabs_operations.generate_manifest_narration()` with
`parameter_overrides` drawn from `voice-selection.json::voice_direction_overrides`.
Used for trial run C1-M1-PRES-20260419B pending CLI canonicalization
(follow-on filed in deferred-inventory.md).

Run with:
    python scripts/marcus_shims/run_prompt12_narration.py \
        --bundle course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv


def _load_operations_module() -> object:
    ops_path = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "elevenlabs-audio"
        / "scripts"
        / "elevenlabs_operations.py"
    )
    spec = importlib.util.spec_from_file_location("elevenlabs_operations", ops_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bundle",
        required=True,
        help="Path to the bundle containing assembly-bundle/ and voice-selection.json",
    )
    parser.add_argument(
        "--receipt-path",
        default=None,
        help=(
            "Where to write the synthesis receipt JSON "
            "(default: <bundle>/prompt12-synthesis-receipt.json)"
        ),
    )
    args = parser.parse_args()

    load_dotenv()
    if not os.environ.get("ELEVENLABS_API_KEY"):
        print("ERROR: ELEVENLABS_API_KEY not found in environment.")
        return 2

    bundle = Path(args.bundle).resolve()
    assembly = bundle / "assembly-bundle"
    manifest_path = assembly / "segment-manifest.yaml"
    voice_selection_path = bundle / "voice-selection.json"
    receipt_path = (
        Path(args.receipt_path).resolve()
        if args.receipt_path
        else bundle / "prompt12-synthesis-receipt.json"
    )

    for required in (manifest_path, voice_selection_path):
        if not required.exists():
            print(f"ERROR: missing required artifact: {required}")
            return 2

    vs = json.loads(voice_selection_path.read_text(encoding="utf-8"))
    overrides = vs.get("voice_direction_overrides") or {}
    if not overrides:
        print("ERROR: voice-selection.json missing voice_direction_overrides block.")
        return 2

    parameter_overrides = {
        k: v
        for k, v in overrides.items()
        if k
        in {
            "stability",
            "similarity_boost",
            "style",
            "speed",
            "use_speaker_boost",
            "emotional_variability",
            "pace_variability",
        }
    }

    print("── §12 ElevenLabs synthesis — dials-only amp-up ──")
    print(f"bundle:               {bundle}")
    print(f"manifest:             {manifest_path}")
    print(f"voice_selection:      {voice_selection_path}")
    print(f"parameter_overrides:  {parameter_overrides}")
    print(f"audio_buffer_seconds: {vs.get('audio_buffer_seconds')}")
    print(f"default_voice_id:     {vs.get('selected_voice_id')}")
    print("")

    ops = _load_operations_module()

    segments_completed: list[dict] = []

    def progress(segment_id: str, index: int, total: int) -> None:
        stamp = datetime.now(UTC).strftime("%H:%M:%S")
        print(f"  [{stamp}] {index:2d}/{total} done  {segment_id}")
        segments_completed.append(
            {"segment_id": segment_id, "index": index, "total": total, "utc": stamp}
        )

    started_utc = datetime.now(UTC).isoformat()
    ops.generate_manifest_narration(
        manifest_path,
        output_dir=assembly,
        parameter_overrides=parameter_overrides,
        voice_selection_path=voice_selection_path,
        progress_callback=progress,
    )
    finished_utc = datetime.now(UTC).isoformat()

    manifest_after = yaml.safe_load(Path(manifest_path).read_text(encoding="utf-8"))
    segs = manifest_after.get("segments", [])
    audio_files = [s.get("narration_file") for s in segs if s.get("narration_file")]
    total_duration = sum(float(s.get("narration_duration") or 0.0) for s in segs)

    receipt = {
        "status": "complete",
        "prompt": 12,
        "run_id": "C1-M1-PRES-20260419B",
        "bundle_path": str(bundle),
        "manifest_path": str(manifest_path),
        "voice_selection_path": str(voice_selection_path),
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "segments_total": len(segs),
        "segments_with_audio": len(audio_files),
        "total_narration_duration_seconds": round(total_duration, 3),
        "default_voice_id": vs.get("selected_voice_id"),
        "default_voice_name": vs.get("selected_voice_name"),
        "audio_buffer_seconds": vs.get("audio_buffer_seconds"),
        "parameter_overrides_applied": parameter_overrides,
        "locked_manifest_hash": vs.get("locked_manifest_hash"),
        "locked_script_hash": vs.get("locked_script_hash"),
        "audio_dir": str(assembly / "audio"),
        "captions_dir": str(assembly / "captions"),
        "progress_log": segments_completed,
        "downstream_gate": "prompt-13-assembly",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print("")
    print(f"receipt written: {receipt_path}")
    print(
        f"segments_with_audio: {len(audio_files)}/{len(segs)}  "
        f"total_narration_duration_seconds: {total_duration:.2f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
