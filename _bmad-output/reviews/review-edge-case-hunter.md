# Edge Case Hunter Review

You are the edge case hunter. Review the diff below and inspect the project as needed. Identify unhandled edge cases, boundary conditions, data validation gaps, and error handling pitfalls. Report findings as a list with file and line references when possible.

## Diff

```diff
diff --git a/docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md b/docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md
index ac8d85c..97d5f2f 100644
--- a/docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md
+++ b/docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md
@@ -702,6 +702,7 @@ Inputs:
 
 Required Marcus behavior:
 - delegate a preview-only request to the Voice Director; do not generate any new audio in this prompt
+- confirm the audio buffer (default 1.5s lead-in + 1.5s tail) and capture the operator-approved value for voice selection
 - provide the operator with exactly one of these review paths:
   - `continuity_preview` or `default_plus_alternatives`:
	- previously used voice for this presentation, if one exists
@@ -722,6 +723,7 @@ python skills/elevenlabs-audio/scripts/elevenlabs_operations.py voice-preview `
   --presentation-attributes-json "{...}" `
   [--previous-voice-receipt [BUNDLE_PATH]/voice-selection.json] `
   [--ideal-voice-description "..."] `
+  [--audio-buffer-seconds 1.5] `
   --output-path [BUNDLE_PATH]/voice-preview-options.json
 ```
 
@@ -738,7 +740,8 @@ python skills/elevenlabs-audio/scripts/elevenlabs_operations.py voice-select `
   --selected-voice-id [VOICE_ID] `
   --output-path [BUNDLE_PATH]/voice-selection.json `
   [--operator-notes "..."] `
-  [--override-reason "..."]
+  [--override-reason "..."] `
+  [--audio-buffer-seconds 1.5]
 ```
 
 Required fields in `voice-selection.json`:
@@ -748,6 +751,7 @@ Required fields in `voice-selection.json`:
 - `preview_url`
 - `selection_rationale`
 - `selected_from_rank`
+- `audio_buffer_seconds`
 - `locked_manifest_hash`
 - `locked_script_hash`
 - `override_reason` when the operator selects a non-primary candidate
@@ -790,6 +794,7 @@ Required outputs:
   - `narration_duration`
   - `narration_file`
   - `narration_vtt`
+  - `audio_buffer_seconds`
   - `sfx_file` where applicable
 
 Motion-specific rules:
@@ -809,12 +814,14 @@ Suggested command surface:
 python skills/elevenlabs-audio/scripts/elevenlabs_operations.py manifest `
   [BUNDLE_PATH]/assembly-bundle/segment-manifest.yaml `
   --output-dir [BUNDLE_PATH]/assembly-bundle `
-  --voice-selection [BUNDLE_PATH]/voice-selection.json
+  --voice-selection [BUNDLE_PATH]/voice-selection.json `
+  [--audio-buffer-seconds 1.5]
 ```
 
 The `--voice-selection` flag causes the tool to:
 - verify `locked_manifest_hash` and `locked_script_hash` against the Gate 3 locked artifacts before any ElevenLabs spend
 - auto-resolve `selected_voice_id` as the default synthesis voice (explicit `--default-voice-id` still overrides)
+- apply `audio_buffer_seconds` to each clip, offset VTT cues by the lead-in buffer, and update `narration_duration`
 - emit per-segment progress to stderr during synthesis
 
 Go/no-go:
diff --git a/skills/elevenlabs-audio/scripts/elevenlabs_operations.py b/skills/elevenlabs-audio/scripts/elevenlabs_operations.py
index 511d7b0..ed2545d 100644
--- a/skills/elevenlabs-audio/scripts/elevenlabs_operations.py
+++ b/skills/elevenlabs-audio/scripts/elevenlabs_operations.py
@@ -18,6 +18,7 @@ import hashlib
 import json
 from pathlib import Path
 import re
+import subprocess
 import sys
 from typing import Any
 import xml.sax.saxutils as xml_utils
@@ -30,6 +31,7 @@ if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))
 
 from scripts.api_clients.elevenlabs_client import ElevenLabsClient
+from scripts.utilities.ffmpeg import resolve_ffmpeg_binary
 
 load_dotenv(PROJECT_ROOT / ".env")
 
@@ -91,6 +93,7 @@ VOICE_CLARITY_HINTS = {
	"professional",
	"warm",
 }
+DEFAULT_AUDIO_BUFFER_SECONDS = 1.5
 
 
 def load_style_guide_elevenlabs() -> dict[str, Any]:
@@ -121,6 +124,34 @@ def merge_parameters(
	return merged
 
 
+def _coerce_audio_buffer_seconds(value: Any | None) -> float | None:
+    if value is None or value == "":
+        return None
+    try:
+        resolved = float(value)
+    except (TypeError, ValueError) as exc:
+        raise ValueError("audio_buffer_seconds must be a number.") from exc
+    if resolved < 0:
+        raise ValueError("audio_buffer_seconds must be non-negative.")
+    return resolved
+
+
+def _resolve_audio_buffer_seconds(
+    value: Any | None,
+    *,
+    style_defaults: dict[str, Any] | None = None,
+    fallback: float = DEFAULT_AUDIO_BUFFER_SECONDS,
+) -> float:
+    resolved = _coerce_audio_buffer_seconds(value)
+    if resolved is not None:
+        return resolved
+    style_defaults = style_defaults or {}
+    resolved = _coerce_audio_buffer_seconds(style_defaults.get("audio_buffer_seconds"))
+    if resolved is not None:
+        return resolved
+    return fallback
+
+
 def _merge_unique_terms(*groups: list[str] | tuple[str, ...] | set[str] | None) -> list[str]:
	"""Merge string terms while preserving first-seen order."""
	merged: list[str] = []
@@ -410,6 +441,7 @@ def preview_voice_options(
	previous_voice_receipt_path: str | Path | None = None,
	ideal_voice_description: str | None = None,
	style_defaults: dict[str, Any] | None = None,
+    audio_buffer_seconds: float | None = None,
	locked_manifest_path: str | Path | None = None,
	locked_script_path: str | Path | None = None,
	output_path: str | Path | None = None,
@@ -423,6 +455,9 @@ def preview_voice_options(
	if client is None:
	    client = ElevenLabsClient()
	style_defaults = style_defaults or load_style_guide_elevenlabs()
+    resolved_audio_buffer_seconds = _resolve_audio_buffer_seconds(
+        audio_buffer_seconds, style_defaults=style_defaults
+    )
	voices = client.list_voices()
	voice_map = {
	    str(voice.get("voice_id") or "").strip(): voice
@@ -539,6 +574,7 @@ def preview_voice_options(
		   "presentation_context": context_chunks,
		   "candidate_voices": recommendations,
		   "catalog_voice_count": len(voices),
+            "audio_buffer_seconds": resolved_audio_buffer_seconds,
		   "selected_voice_id": None,
		   "selected_voice_name": None,
		   "selected_from_rank": None,
@@ -670,6 +706,7 @@ def preview_voice_options(
	    "presentation_context": context_chunks,
	    "candidate_voices": candidate_voices,
	    "catalog_voice_count": len(voices),
+        "audio_buffer_seconds": resolved_audio_buffer_seconds,
	    "selected_voice_id": None,
	    "selected_voice_name": None,
	    "selected_from_rank": None,
@@ -696,6 +733,7 @@ def finalize_voice_selection(
	output_path: str | Path | None = None,
	operator_notes: str | None = None,
	override_reason: str | None = None,
+    audio_buffer_seconds: float | None = None,
 ) -> dict[str, Any]:
	"""Persist the operator's selected voice from a preview receipt."""
	receipt = _load_json_file(preview_receipt_path)
@@ -717,6 +755,11 @@ def finalize_voice_selection(
		   "override_reason is required when selecting a non-primary preview candidate."
	    )
 
+    resolved_audio_buffer_seconds = _resolve_audio_buffer_seconds(
+        audio_buffer_seconds if audio_buffer_seconds is not None else receipt.get("audio_buffer_seconds"),
+        style_defaults=load_style_guide_elevenlabs(),
+    )
+
	decision = dict(receipt)
	decision.update(
	    {
@@ -727,6 +770,7 @@ def finalize_voice_selection(
		   "selected_from_rank": selected_rank,
		   "preview_url": selected_candidate.get("preview_url"),
		   "selection_rationale": selected_candidate.get("rationale"),
+            "audio_buffer_seconds": resolved_audio_buffer_seconds,
		   "operator_notes": operator_notes,
		   "override_reason": override_reason,
		   "voice_preview_receipt_path": str(Path(preview_receipt_path)),
@@ -777,6 +821,14 @@ def _format_vtt_timestamp(value: float) -> str:
	return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
 
 
+def _parse_vtt_timestamp(value: str) -> float:
+    match = re.match(r"^(\d{2}):(\d{2}):(\d{2})\.(\d{3})$", value.strip())
+    if not match:
+        raise ValueError(f"Invalid VTT timestamp: {value}")
+    hours, minutes, seconds, milliseconds = (int(part) for part in match.groups())
+    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
+
+
 def alignment_to_vtt(alignment: dict[str, Any] | None) -> str:
	"""Convert ElevenLabs character alignment to a word-level WebVTT track."""
	if not alignment:
@@ -816,6 +868,70 @@ def alignment_to_vtt(alignment: dict[str, Any] | None) -> str:
	return "\n".join(lines)
 
 
+def offset_vtt_timestamps(vtt_text: str, offset_seconds: float) -> str:
+    if offset_seconds <= 0:
+        return vtt_text
+    lines = vtt_text.splitlines()
+    updated: list[str] = []
+    for line in lines:
+        if "-->" not in line:
+            updated.append(line)
+            continue
+        start_text, end_text = (part.strip() for part in line.split("-->", 1))
+        try:
+            start = _parse_vtt_timestamp(start_text) + offset_seconds
+            end = _parse_vtt_timestamp(end_text) + offset_seconds
+        except ValueError:
+            updated.append(line)
+            continue
+        updated.append(f"{_format_vtt_timestamp(start)} --> {_format_vtt_timestamp(end)}")
+    suffix = "\n" if vtt_text.endswith("\n") else ""
+    return "\n".join(updated) + suffix
+
+
+def _apply_audio_buffer(
+    audio_path: Path,
+    *,
+    lead_seconds: float,
+    tail_seconds: float,
+    base_duration: float,
+    ffmpeg_path: str | None = None,
+) -> None:
+    if lead_seconds <= 0 and tail_seconds <= 0:
+        return
+    if lead_seconds < 0 or tail_seconds < 0:
+        raise ValueError("audio_buffer_seconds must be non-negative.")
+    ffmpeg = resolve_ffmpeg_binary(ffmpeg_path)
+    temp_path = audio_path.with_name(f"{audio_path.stem}-buffered{audio_path.suffix}")
+    filter_parts: list[str] = []
+    if lead_seconds > 0:
+        lead_ms = int(round(lead_seconds * 1000))
+        filter_parts.append(f"adelay={lead_ms}:all=1")
+    if tail_seconds > 0:
+        filter_parts.append(f"apad=pad_dur={tail_seconds}")
+    filter_str = ",".join(filter_parts) if filter_parts else "anull"
+    target_duration = max(0.0, base_duration + lead_seconds + tail_seconds)
+    command = [
+        ffmpeg,
+        "-y",
+        "-i",
+        str(audio_path),
+        "-af",
+        filter_str,
+        "-t",
+        f"{target_duration:.3f}",
+        str(temp_path),
+    ]
+    completed = subprocess.run(command, capture_output=True, text=True, check=False)
+    if completed.returncode != 0:
+        detail = (completed.stderr or completed.stdout or "").strip()
+        message = "ffmpeg failed while applying audio buffer."
+        if detail:
+            message = f"{message} {detail}"
+        raise RuntimeError(message)
+    temp_path.replace(audio_path)
+
+
 def load_manifest(manifest_path: str | Path) -> dict[str, Any]:
	"""Load a YAML segment manifest from disk."""
	manifest_path = Path(manifest_path)
@@ -939,6 +1055,7 @@ def generate_manifest_narration(
	parameter_overrides: dict[str, Any] | None = None,
	default_voice_id: str | None = None,
	voice_selection_path: str | Path | None = None,
+    audio_buffer_seconds: float | None = None,
	progress_callback: Any | None = None,
	client: ElevenLabsClient | None = None,
 ) -> dict[str, Any]:
@@ -986,6 +1103,16 @@ def generate_manifest_narration(
	if not resolved_default_voice_id:
	    raise ValueError("No ElevenLabs default voice available for manifest processing.")
 
+    resolved_audio_buffer_seconds = _resolve_audio_buffer_seconds(
+        audio_buffer_seconds
+        if audio_buffer_seconds is not None
+        else (vs_data or {}).get("audio_buffer_seconds"),
+        style_defaults=merged,
+    )
+    ffmpeg_path = None
+    if resolved_audio_buffer_seconds > 0:
+        ffmpeg_path = resolve_ffmpeg_binary()
+
	segments = manifest.get("segments", [])
	total_segments = len(segments)
	previous_request_ids: list[str] = []
@@ -997,6 +1124,7 @@ def generate_manifest_narration(
		   segment["narration_duration"] = 0.0
		   segment["narration_file"] = None
		   segment["narration_vtt"] = None
+            segment["audio_buffer_seconds"] = 0.0
		   segment.setdefault("sfx_file", None)
		   if progress_callback:
			  progress_callback(segment_id, seg_index, total_segments)
@@ -1025,9 +1153,27 @@ def generate_manifest_narration(
		   )
		   generated_vtt_path.unlink()
 
-        segment["narration_duration"] = result["narration_duration"]
+        buffer_seconds = resolved_audio_buffer_seconds
+        narration_duration = result["narration_duration"]
+        if buffer_seconds > 0:
+            _apply_audio_buffer(
+                audio_path,
+                lead_seconds=buffer_seconds,
+                tail_seconds=buffer_seconds,
+                base_duration=narration_duration,
+                ffmpeg_path=ffmpeg_path,
+            )
+            updated_vtt = offset_vtt_timestamps(
+                final_vtt_path.read_text(encoding="utf-8"),
+                buffer_seconds,
+            )
+            final_vtt_path.write_text(updated_vtt, encoding="utf-8")
+            narration_duration += buffer_seconds * 2
+
+        segment["narration_duration"] = narration_duration
	    segment["narration_file"] = str(audio_path)
	    segment["narration_vtt"] = str(final_vtt_path)
+        segment["audio_buffer_seconds"] = buffer_seconds
	    segment.setdefault("sfx_file", None)
 
	    sfx_cue = segment.get("sfx")
@@ -1048,9 +1194,10 @@ def generate_manifest_narration(
			  "segment_id": segment_id,
			  "voice_id": voice_id,
			  "request_id": result.get("request_id"),
-                "narration_duration": result["narration_duration"],
+                "narration_duration": narration_duration,
			  "narration_file": segment["narration_file"],
			  "narration_vtt": segment["narration_vtt"],
+                "audio_buffer_seconds": buffer_seconds,
			  "sfx_file": segment.get("sfx_file"),
		   }
	    )
@@ -1190,6 +1337,7 @@ def build_parser() -> argparse.ArgumentParser:
	    "--voice-selection",
	    help="Path to voice-selection.json; verifies hashes before synthesis",
	)
+    manifest.add_argument("--audio-buffer-seconds", type=float)
 
	voice_preview = subparsers.add_parser(
	    "voice-preview",
@@ -1204,6 +1352,7 @@ def build_parser() -> argparse.ArgumentParser:
	voice_preview.add_argument("--previous-voice-id")
	voice_preview.add_argument("--previous-voice-receipt")
	voice_preview.add_argument("--ideal-voice-description")
+    voice_preview.add_argument("--audio-buffer-seconds", type=float)
	voice_preview.add_argument("--locked-manifest")
	voice_preview.add_argument("--locked-script")
	voice_preview.add_argument("--output-path")
@@ -1217,6 +1366,7 @@ def build_parser() -> argparse.ArgumentParser:
	voice_select.add_argument("--output-path")
	voice_select.add_argument("--operator-notes")
	voice_select.add_argument("--override-reason")
+    voice_select.add_argument("--audio-buffer-seconds", type=float)
 
	return parser
 
@@ -1253,6 +1403,7 @@ def main(argv: list[str] | None = None) -> int:
			  output_dir=args.output_dir,
			  default_voice_id=args.default_voice_id,
			  voice_selection_path=getattr(args, "voice_selection", None),
+                audio_buffer_seconds=getattr(args, "audio_buffer_seconds", None),
			  progress_callback=_cli_progress,
		   )
	    elif args.command == "voice-preview":
@@ -1267,6 +1418,7 @@ def main(argv: list[str] | None = None) -> int:
			  previous_voice_id=args.previous_voice_id,
			  previous_voice_receipt_path=args.previous_voice_receipt,
			  ideal_voice_description=args.ideal_voice_description,
+                audio_buffer_seconds=args.audio_buffer_seconds,
			  locked_manifest_path=args.locked_manifest,
			  locked_script_path=args.locked_script,
			  output_path=args.output_path,
@@ -1278,6 +1430,7 @@ def main(argv: list[str] | None = None) -> int:
			  output_path=args.output_path,
			  operator_notes=args.operator_notes,
			  override_reason=args.override_reason,
+                audio_buffer_seconds=args.audio_buffer_seconds,
		   )
	    else:
		   result = generate_sound_effect(
@@ -7,6 +7,8 @@ import json
 from pathlib import Path
 from unittest.mock import Mock, patch
 
+import pytest
+
 MODULE_PATH = Path(__file__).resolve().parents[1] / "elevenlabs_operations.py"
 SPEC = importlib.util.spec_from_file_location("elevenlabs_operations", MODULE_PATH)
 MODULE = importlib.util.module_from_spec(SPEC)
@@ -279,6 +281,56 @@ class TestVoicePreviewFlow:
	    assert result["selection_mode"] == "description_recommendation"
	    assert len(result["candidate_voices"]) == 3
	    assert result["candidate_voices"][0]["voice_id"] == "voice-a"
+
+
+class TestAudioBufferHandling:
+    def test_preview_voice_options_rejects_negative_buffer(self) -> None:
+        client = Mock()
+        client.list_voices.return_value = []
+
+        with pytest.raises(ValueError):
+            MODULE.preview_voice_options(
+                mode="default_plus_alternatives",
+                audio_buffer_seconds=-0.5,
+                client=client,
+            )
+
+    def test_finalize_voice_selection_preserves_audio_buffer(self, tmp_path: Path) -> None:
+        receipt = {
+            "status": "selection_required",
+            "audio_buffer_seconds": 0.75,
+            "candidate_voices": [
+                {
+                    "voice_id": "voice-1",
+                    "name": "Example Voice",
+                    "source": "style_guide_default",
+                    "preview_url": "https://samples/voice.mp3",
+                    "rationale": "Baseline",
+                    "rank": 1,
+                }
+            ],
+        }
+        preview_path = tmp_path / "voice-preview.json"
+        output_path = tmp_path / "voice-selection.json"
+        preview_path.write_text(json.dumps(receipt), encoding="utf-8")
+
+        decision = MODULE.finalize_voice_selection(
+            preview_path,
+            selected_voice_id="voice-1",
+            output_path=output_path,
+        )
+
+        assert decision["audio_buffer_seconds"] == 0.75
+        assert output_path.exists()
+
+    def test_offset_vtt_timestamps_applies_buffer(self) -> None:
+        vtt = "WEBVTT\n\n1\n00:00:00.000 --> 00:00:01.000\nHello\n"
+        shifted = MODULE.offset_vtt_timestamps(vtt, 1.5)
+        assert "00:00:01.500 --> 00:00:02.500" in shifted
+
+    def test_offset_vtt_timestamps_no_change_when_zero(self) -> None:
+        vtt = "WEBVTT\n\n1\n00:00:00.000 --> 00:00:01.000\nHello\n"
+        assert MODULE.offset_vtt_timestamps(vtt, 0.0) == vtt
	    assert all(item["preview_url"] for item in result["candidate_voices"])
	    assert all(item["source"] == "description_recommendation" for item in result["candidate_voices"])
	    assert result["locked_manifest_hash"]
@@ -34,6 +34,7 @@ tool_parameters:
	style: 0.0
	model_id: ""            # e.g. "eleven_multilingual_v2"
	output_format: "mp3_44100_128"
+    audio_buffer_seconds: 1.5
 
   canvas:
	default_course_id: ""
```

```
diff --git "a/_bmad-output\\implementation-artifacts\\spec-elevenlabs-audio-buffer-padding.md" "b/_bmad-output\\implementation-artifacts\\spec-elevenlabs-audio-buffer-padding.md"
new file mode 100644
index 0000000..2f73f9a
--- /dev/null
+++ "b/_bmad-output\\implementation-artifacts\\spec-elevenlabs-audio-buffer-padding.md"
@@ -0,0 +1,69 @@
+---
+title: 'ElevenLabs audio buffer padding'
+type: 'feature'
+created: '2026-04-09'
+status: 'in-review'
+baseline_commit: '56b696132fdce01080d5390bff8f609b884220b0'
+context: ['docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md']
+---
+
+<frozen-after-approval reason="human-owned intent -- do not modify unless human renegotiates">
+
+## Intent
+
+**Problem:** ElevenLabs narration clips are generated without a configurable lead-in or lead-out buffer, and the operator cannot confirm or adjust padding before synthesis.
+
+**Approach:** Add a governed audio buffer option (default 1.5s on both ends), surface it during voice preview and selection, and apply it to each narrated clip during manifest synthesis with VTT cue offsets and duration updates.
+
+## Boundaries & Constraints
+
+**Always:** Preserve narration text and voice selection logic; apply buffering post-synthesis using ffmpeg; default to 1.5s unless the operator overrides; store the operator-confirmed buffer in the voice selection output; offset VTT cues by the lead-in buffer; update `narration_duration` to include lead-in and tail padding.
+
+**Ask First:** Change the default buffer away from 1.5s, introduce asymmetric start/end buffers, or apply buffering to non-narration audio (SFX, music, or final mixes).
+
+**Never:** Regenerate narration text, reorder segments, skip buffering when a non-zero buffer is requested, or bypass hash verification in the voice selection workflow.
+
+## I/O & Edge-Case Matrix
+
+| Scenario | Input / State | Expected Output / Behavior | Error Handling |
+|----------|--------------|---------------------------|----------------|
+| Default buffer | No override provided | Each clip gets 1.5s lead-in and 1.5s tail; VTT cues offset by +1.5s; `narration_duration` includes buffers | N/A |
+| Operator override | `--audio-buffer-seconds 0.75` or value chosen in voice selection | Buffer uses override for all clips; VTT offset by 0.75s; duration reflects override | N/A |
+| Zero buffer | `--audio-buffer-seconds 0` | No padding applied; VTT and duration unchanged | N/A |
+| Invalid buffer | Negative buffer value | Abort before synthesis and do not write audio or VTT | Fail closed with ValueError |
+| Missing ffmpeg | Buffer requested and ffmpeg not resolvable | Abort before processing any clip | Fail closed with clear error |
+
+</frozen-after-approval>
+
+## Code Map
+
+- `skills/elevenlabs-audio/scripts/elevenlabs_operations.py` -- CLI args, voice preview/selection, manifest narration generation, VTT writing; add buffer validation and post-processing
+- `skills/elevenlabs-audio/scripts/tests/test_elevenlabs_operations.py` -- unit tests for buffer validation and VTT offset behavior
+- `state/config/style_guide.yaml` -- ElevenLabs defaults; add `audio_buffer_seconds`
+- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` -- Prompt 11/12 operator guidance; add buffer confirmation and CLI flag
+- `scripts/utilities/ffmpeg.py` -- ffmpeg resolution utility used by buffer padding
+
+## Tasks & Acceptance
+
+**Execution:**
+- [x] `skills/elevenlabs-audio/scripts/elevenlabs_operations.py` -- add `audio_buffer_seconds` handling for voice preview, voice selection output, and manifest synthesis; validate non-negative values; apply ffmpeg padding; offset VTT cues; update `narration_duration` -- ensures operator-confirmed buffers are enforced end to end
+- [x] `state/config/style_guide.yaml` -- add `audio_buffer_seconds: 1.5` under ElevenLabs tool defaults -- establishes governed default
+- [x] `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` -- add operator confirmation step for buffer and include `--audio-buffer-seconds` in Prompt 11/12 guidance -- codifies HIL requirement
+- [x] `skills/elevenlabs-audio/scripts/tests/test_elevenlabs_operations.py` -- add tests for negative buffer validation, zero-buffer no-op, and VTT offset with buffer -- protects regressions
+
+**Acceptance Criteria:**
+- Given the operator confirms a buffer during voice selection, when manifest synthesis runs with `--voice-selection`, then the buffer in `voice-selection.json` is used for all clips and recorded in updated manifest fields.
+- Given no override is provided, when voice selection is created, then `audio_buffer_seconds` defaults to 1.5 and is preserved through synthesis.
+- Given a non-zero buffer, when narration is generated, then audio files are padded and VTT cues are shifted by the lead-in buffer.
+- Given a negative buffer, when any ElevenLabs command is executed, then the run fails before any synthesis or file writes.
+
+## Spec Change Log
+
+## Design Notes
+
+Use `scripts.utilities.ffmpeg.resolve_ffmpeg_binary` to add silence before and after each clip. Apply padding after ElevenLabs returns audio and alignment, then update VTT cues by the lead-in seconds only. Update `narration_duration` by adding lead-in and tail seconds to the original duration.
+
+## Verification
+
+**Commands:**
+- `c:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/.venv/Scripts/python.exe -m pytest skills/elevenlabs-audio/scripts/tests/test_elevenlabs_operations.py` -- expected: PASS
```
