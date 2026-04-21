"""Marcus shim — Prompt 13 Quinn-R Pre-Composition QA.

Performs the §13 checks against the post-§12 assembly-bundle:
1. Narration WPM per segment vs expected band (advisory).
2. VTT cue monotonicity per caption file.
3. Segment coverage (every segment has audio + VTT, file exists, non-empty).
4. Motion duration vs narration_duration coherence for non-static segments.
5. Required asset existence (visuals, motion clips referenced by manifest).

Writes `quinnr-precomposition-receipt.json` at bundle root with status:
  pass | pass_with_advisories | fail
and per-check details. Operator GO is required to advance to §14.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

WPM_LOW = 130
WPM_HIGH = 175
MOTION_TOLERANCE_SECONDS = 0.50  # acceptable abs delta motion vs narration


def _probe_motion_duration_seconds(clip: Path) -> float | None:
    """Best-effort duration probe via ffmpeg -i stderr parse (no ffprobe needed)."""
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "_eops",
            Path(__file__).resolve().parents[2]
            / "skills"
            / "elevenlabs-audio"
            / "scripts"
            / "elevenlabs_operations.py",
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        ffmpeg_bin = mod.resolve_ffmpeg_binary()
    except Exception:
        return None
    try:
        out = subprocess.run(
            [ffmpeg_bin, "-i", str(clip)], capture_output=True, text=True, timeout=15
        )
    except Exception:
        return None
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", out.stderr)
    if not m:
        return None
    h, mm, s = m.groups()
    return int(h) * 3600 + int(mm) * 60 + float(s)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _parse_vtt_cues(vtt_text: str) -> list[tuple[float, float]]:
    cues: list[tuple[float, float]] = []
    cue_re = re.compile(
        r"(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2})\.(\d{3})"
    )
    for line in vtt_text.splitlines():
        m = cue_re.search(line)
        if not m:
            continue
        h1, m1, s1, ms1, h2, m2, s2, ms2 = (int(g) for g in m.groups())
        start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
        end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000
        cues.append((start, end))
    return cues


def _resolve(path_str: str, bundle: Path, fallback: Path | None) -> Path:
    """Resolve a manifest path: absolute → as-is; relative → bundle-rooted; empty → fallback."""
    if not path_str:
        return fallback if fallback is not None else bundle / "MISSING"
    p = Path(path_str)
    if p.is_absolute():
        return p
    candidate = bundle / p
    if candidate.exists():
        return candidate
    if fallback is not None and fallback.exists():
        return fallback
    return candidate


def _check_vtt_monotonic(cues: list[tuple[float, float]]) -> tuple[bool, str | None]:
    last_end = -1.0
    for i, (start, end) in enumerate(cues):
        if start < last_end - 1e-3:
            return False, f"cue {i} start {start:.3f} < prev end {last_end:.3f}"
        if end < start - 1e-3:
            return False, f"cue {i} end {end:.3f} < start {start:.3f}"
        last_end = end
    return True, None


def main() -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    args = parser.parse_args()

    bundle = Path(args.bundle).resolve()
    assembly = bundle / "assembly-bundle"
    manifest_path = assembly / "segment-manifest.yaml"
    audio_dir = assembly / "audio"
    captions_dir = assembly / "captions"
    receipt_path = bundle / "quinnr-precomposition-receipt.json"

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    segments: list[dict[str, Any]] = manifest.get("segments", [])

    wpm_findings: list[dict[str, Any]] = []
    vtt_findings: list[dict[str, Any]] = []
    coverage_findings: list[dict[str, Any]] = []
    motion_findings: list[dict[str, Any]] = []
    asset_findings: list[dict[str, Any]] = []

    blocking = 0
    advisories = 0

    print("── §13 Quinn-R Pre-Composition QA ──")
    print(f"bundle: {bundle}")
    print(f"manifest: {manifest_path}")
    print(f"segments: {len(segments)}")
    print("")

    for seg in segments:
        sid = seg.get("id", "?")
        narration_text = seg.get("narration_text") or ""
        narration_duration = float(seg.get("narration_duration") or 0.0)
        narration_file_str = seg.get("narration_file") or ""
        narration_vtt_str = seg.get("narration_vtt") or ""

        # 1. WPM check
        words = _word_count(narration_text)
        wpm = (words / narration_duration * 60) if narration_duration > 0 else 0
        wpm_status = "ok"
        if wpm < WPM_LOW:
            wpm_status = "slow_advisory"
            advisories += 1
        elif wpm > WPM_HIGH:
            wpm_status = "fast_advisory"
            advisories += 1
        wpm_findings.append(
            {
                "segment_id": sid,
                "words": words,
                "duration_seconds": round(narration_duration, 2),
                "wpm": round(wpm, 1),
                "status": wpm_status,
            }
        )

        # 3. Coverage + audio file existence
        audio_file = _resolve(narration_file_str, bundle, audio_dir / f"{sid}.mp3")
        coverage_entry = {"segment_id": sid, "audio_present": False, "vtt_present": False}
        if audio_file.exists() and audio_file.stat().st_size > 0:
            coverage_entry["audio_present"] = True
        else:
            coverage_findings.append(
                {"segment_id": sid, "issue": f"audio missing or empty: {audio_file}"}
            )
            blocking += 1

        # 2 + 3 cont. VTT existence + monotonicity
        vtt_file = _resolve(narration_vtt_str, bundle, captions_dir / f"{sid}.vtt")
        if vtt_file.exists() and vtt_file.stat().st_size > 0:
            coverage_entry["vtt_present"] = True
            vtt_text = vtt_file.read_text(encoding="utf-8", errors="replace")
            cues = _parse_vtt_cues(vtt_text)
            if not cues:
                vtt_findings.append(
                    {"segment_id": sid, "status": "fail", "reason": "no cues parsed"}
                )
                blocking += 1
            else:
                ok, reason = _check_vtt_monotonic(cues)
                if ok:
                    vtt_findings.append(
                        {"segment_id": sid, "status": "pass", "cue_count": len(cues)}
                    )
                else:
                    vtt_findings.append(
                        {"segment_id": sid, "status": "fail", "reason": reason}
                    )
                    blocking += 1
        else:
            coverage_findings.append(
                {"segment_id": sid, "issue": f"vtt missing or empty: {vtt_file}"}
            )
            blocking += 1

        # 4. Motion coherence (non-static only)
        motion_type = seg.get("motion_type") or "static"
        if motion_type != "static":
            motion_path_str = seg.get("motion_asset_path") or ""
            motion_path = _resolve(motion_path_str, bundle, None) if motion_path_str else None
            motion_dur = seg.get("motion_duration_seconds")
            entry = {
                "segment_id": sid,
                "motion_type": motion_type,
                "motion_asset_path": str(motion_path) if motion_path else None,
                "motion_duration_seconds": motion_dur,
                "narration_duration_seconds": round(narration_duration, 2),
            }
            if motion_path is None or not motion_path.exists():
                entry["status"] = "fail"
                entry["reason"] = "motion_asset_path missing or unreadable"
                blocking += 1
            elif motion_dur is None:
                # Probe the actual clip duration so we can produce edit guidance
                probed = _probe_motion_duration_seconds(motion_path)
                if probed is None:
                    entry["status"] = "advisory"
                    entry["reason"] = (
                        "motion_duration_seconds not set in manifest and ffprobe unavailable"
                    )
                    advisories += 1
                else:
                    motion_dur = probed
                    entry["motion_duration_seconds_probed"] = round(probed, 3)
                    entry["motion_duration_source"] = "ffmpeg_probe"
                    delta = float(motion_dur) - narration_duration
                    entry["delta_seconds"] = round(delta, 2)
                    if abs(delta) <= MOTION_TOLERANCE_SECONDS:
                        entry["status"] = "pass"
                    else:
                        entry["status"] = "advisory_with_edit_guidance"
                        if delta > 0:
                            entry["edit_guidance"] = (
                                f"motion clip is {delta:.2f}s LONGER than narration; "
                                f"trim to {narration_duration:.2f}s tail-out, or hold final frame"
                            )
                        else:
                            shortfall = abs(delta)
                            poster = seg.get("visual_file")
                            loops = int(round(narration_duration / motion_dur))
                            entry["edit_guidance_options"] = [
                                (
                                    f"OPTION A — play once + cross-fade to slide poster {poster} "
                                    f"for {shortfall:.2f}s "
                                    "(cleanest if poster is a strong card)"
                                ),
                                (
                                    f"OPTION B — loop the {motion_dur:.2f}s clip "
                                    f"~{loops}× to fill {narration_duration:.2f}s "
                                    "(works for continuous B-roll; obvious for storyline clips)"
                                ),
                                (
                                    "OPTION C — play once + freeze final frame "
                                    f"for {shortfall:.2f}s "
                                    "(simplest; depends on whether final frame is a 'good card')"
                                ),
                            ]
                            entry["recommended_option"] = "A"
                            entry["recommendation_reason"] = (
                                "motion+poster dual-binding already exists in manifest; "
                                "cross-fade preserves both Veo3 storytelling "
                                "AND clinical-card legibility"
                            )
                        advisories += 1
            else:
                delta = float(motion_dur) - narration_duration
                entry["delta_seconds"] = round(delta, 2)
                if abs(delta) <= MOTION_TOLERANCE_SECONDS:
                    entry["status"] = "pass"
                else:
                    # Per pack: video duration vs narration_duration mismatch is advisory
                    # if explicit edit guidance is produced (e.g., "loop", "trim", "extend").
                    # Marcus emits guidance here; not blocking by default.
                    entry["status"] = "advisory_with_edit_guidance"
                    if delta > 0:
                        entry["edit_guidance"] = (
                            f"motion clip is {delta:.2f}s LONGER than narration; "
                            f"trim to {narration_duration:.2f}s tail-out, or hold final frame"
                        )
                    else:
                        entry["edit_guidance"] = (
                            f"motion clip is {abs(delta):.2f}s SHORTER than narration; "
                            f"hold final frame for {abs(delta):.2f}s, or extend with poster frame"
                        )
                    advisories += 1
            motion_findings.append(entry)

        # 5. Visual / poster file existence
        visual_file_str = seg.get("visual_file") or ""
        if visual_file_str:
            vp = _resolve(visual_file_str, bundle, None)
            if not vp.exists():
                asset_findings.append(
                    {
                        "segment_id": sid,
                        "kind": "visual_file",
                        "path": str(vp),
                        "status": "fail",
                    }
                )
                blocking += 1

        # Optional asset paths to check if present
        for opt_field in ("sfx_file", "music_file"):
            opt_val = seg.get(opt_field)
            if opt_val:
                op = _resolve(opt_val, bundle, None)
                if not op.exists():
                    asset_findings.append(
                        {
                            "segment_id": sid,
                            "kind": opt_field,
                            "path": str(op),
                            "status": "fail",
                        }
                    )
                    blocking += 1

    overall_status = (
        "fail" if blocking > 0 else ("pass_with_advisories" if advisories > 0 else "pass")
    )

    receipt = {
        "status": overall_status,
        "prompt": 13,
        "run_id": "C1-M1-PRES-20260419B",
        "bundle_path": str(bundle),
        "checked_utc": datetime.now(UTC).isoformat(),
        "thresholds": {
            "wpm_low": WPM_LOW,
            "wpm_high": WPM_HIGH,
            "motion_tolerance_seconds": MOTION_TOLERANCE_SECONDS,
        },
        "summary": {
            "segments_total": len(segments),
            "blocking_count": blocking,
            "advisory_count": advisories,
            "wpm_in_band": sum(1 for w in wpm_findings if w["status"] == "ok"),
            "vtt_pass": sum(1 for v in vtt_findings if v["status"] == "pass"),
            "audio_present": sum(
                1
                for s in segments
                if (audio_dir / f"{s.get('id')}.mp3").exists()
                and (audio_dir / f"{s.get('id')}.mp3").stat().st_size > 0
            ),
            "vtt_present": sum(
                1
                for s in segments
                if (captions_dir / f"{s.get('id')}.vtt").exists()
                and (captions_dir / f"{s.get('id')}.vtt").stat().st_size > 0
            ),
            "non_static_segments": sum(
                1 for s in segments if (s.get("motion_type") or "static") != "static"
            ),
        },
        "wpm_findings": wpm_findings,
        "vtt_findings": vtt_findings,
        "coverage_findings": coverage_findings,
        "motion_findings": motion_findings,
        "asset_findings": asset_findings,
        "downstream_gate": "prompt-14-compositor-assembly" if overall_status != "fail" else None,
    }

    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    # Print summary
    s = receipt["summary"]
    print(f"status:                  {overall_status.upper()}")
    print(f"blocking issues:         {blocking}")
    print(f"advisories:              {advisories}")
    print(
        f"audio present:           {s['audio_present']}/{s['segments_total']}   "
        f"vtt present: {s['vtt_present']}/{s['segments_total']}   "
        f"vtt monotonic pass: {s['vtt_pass']}/{s['segments_total']}"
    )
    print(f"wpm in band [{WPM_LOW},{WPM_HIGH}]: {s['wpm_in_band']}/{s['segments_total']}")
    print(f"non-static segments:     {s['non_static_segments']}")
    print(f"receipt: {receipt_path}")

    if wpm_findings:
        print("\nWPM findings (advisory only):")
        for w in wpm_findings:
            flag = "" if w["status"] == "ok" else f"  ⟵ {w['status']}"
            sid = w["segment_id"]
            words = w["words"]
            dur = w["duration_seconds"]
            wpm = w["wpm"]
            print(
                f"  {sid:55s}  words={words:3d}  "
                f"dur={dur:6.2f}s  wpm={wpm:6.1f}{flag}"
            )

    if motion_findings:
        print("\nMotion findings:")
        for m in motion_findings:
            print(f"  {m['segment_id']}: status={m['status']}  delta={m.get('delta_seconds')}")
            if m.get("edit_guidance"):
                print(f"    guidance: {m['edit_guidance']}")

    if coverage_findings or asset_findings:
        print("\nBlocking:")
        for entry in coverage_findings:
            print(f"  COVERAGE  {entry}")
        for entry in asset_findings:
            print(f"  ASSET     {entry}")

    return 0 if overall_status != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
