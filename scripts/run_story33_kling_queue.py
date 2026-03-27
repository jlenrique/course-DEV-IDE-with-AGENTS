"""Run Story 3.3 Kling validation clips in a serialized queue.

This helper is intentionally operational: Kling enforces a concurrency limit,
so the safe path is one submission at a time with polling, download, and
manifest logging before the next request.
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.api_clients.kling_client import KlingClient

load_dotenv()

OUTDIR = Path("course-content/staging/story-3.3-samples")
OUTDIR.mkdir(parents=True, exist_ok=True)
MANIFEST = OUTDIR / "generation-manifest.csv"
NEG = (
    "text overlays, watermarks, cartoon style, chaotic camera movement, "
    "irrelevant background subjects"
)


JOBS = [
    {
        "name": "V1-hospital-broll",
        "filename": "V1-hospital-broll__kling-v2-6_std_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "std",
        "duration": "5",
        "prompt": (
            "Professional hospital corridor with clinicians moving through frame, "
            "soft natural light, shallow depth of field, subtle camera drift, "
            "cool medical blues and clean whites, urgency but professionalism."
        ),
        "sound": False,
    },
    {
        "name": "V2-clinical-to-innovator-pathway",
        "filename": "V2-clinical-to-innovator-pathway__kling-v2-6_std_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "std",
        "duration": "5",
        "prompt": (
            "A clean animation on dark navy background showing a traditional "
            "clinical pathway with medical cross icons that diverges into a new "
            "streamlined innovator pathway with glowing teal nodes. Smooth "
            "restrained corporate healthcare motion design, highly legible, "
            "professional medical aesthetic."
        ),
        "sound": None,
        "existing_task_id": "866382527034957896",
    },
    {
        "name": "V3-heros-journey-roadmap",
        "filename": "V3-heros-journey-roadmap__kling-v2-6_std_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "std",
        "duration": "5",
        "prompt": (
            "A clean modern corporate infographic style animation of a "
            "horizontal winding roadmap titled The Innovators Journey, with "
            "three waypoints: Sparking Innovation, Building the Solution, and "
            "Driving Impact. Professional healthcare palette of navy blue, teal, "
            "and white. Minimalist flat vector style. Subtle motion along the "
            "roadmap path."
        ),
        "sound": None,
    },
    {
        "name": "V4-knowledge-explosion-timeline",
        "filename": "V4-knowledge-explosion-timeline__kling-v2-6_std_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "std",
        "duration": "5",
        "prompt": (
            "A minimalist data-driven animation showing medical knowledge "
            "doubling from 50 years in 1950 to 73 days in 2026. The timeline "
            "compresses visually over time, starting slow and accelerating "
            "rapidly. Clean sans-serif typography, dark background, teal "
            "accents, highly legible educational motion graphics."
        ),
        "sound": None,
    },
    {
        "name": "V5-physician-innovator-lineage",
        "filename": "V5-physician-innovator-lineage__kling-v2-6_std_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "std",
        "duration": "5",
        "prompt": (
            "A polished split-screen montage showing diverse physician "
            "innovators across process innovation, device innovation, "
            "technological innovation, and organizational innovation. "
            "Professional medical aesthetic, four-quadrant composition, subtle "
            "camera movement and transitions between quadrants, respectful and "
            "authoritative tone."
        ),
        "sound": None,
    },
    {
        "name": "V6-module-bridge-transition",
        "filename": "V6-module-bridge-transition__kling-v2-6_std_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "std",
        "duration": "5",
        "prompt": (
            "A clean closing transition for a medical education module. Dark "
            "navy background, bridge graphic connecting Module 1 Mindset to "
            "Module 2 Leadership Identity, restrained teal motion sweep, "
            "polished healthcare brand aesthetic, concise and elegant visual "
            "bridge."
        ),
        "sound": False,
    },
    {
        "name": "V1-hospital-broll",
        "filename": "V1-hospital-broll__kling-v2-6_pro_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "pro",
        "duration": "5",
        "prompt": (
            "Professional hospital corridor with clinicians moving through frame, "
            "soft natural light, shallow depth of field, subtle camera drift, "
            "cool medical blues and clean whites, urgency but professionalism. "
            "Natural footsteps and soft corridor ambience if supported."
        ),
        "sound": True,
    },
    {
        "name": "V2-clinical-to-innovator-pathway",
        "filename": "V2-clinical-to-innovator-pathway__kling-v2-6_pro_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "pro",
        "duration": "5",
        "prompt": (
            "A clean animation on dark navy background showing a traditional "
            "clinical pathway with medical cross icons that diverges into a new "
            "streamlined innovator pathway with glowing teal nodes. Smooth "
            "restrained corporate healthcare motion design, highly legible, "
            "professional medical aesthetic."
        ),
        "sound": None,
    },
    {
        "name": "V3-heros-journey-roadmap",
        "filename": "V3-heros-journey-roadmap__kling-v2-6_pro_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "pro",
        "duration": "5",
        "prompt": (
            "A clean modern corporate infographic style animation of a "
            "horizontal winding roadmap titled The Innovators Journey, with "
            "three waypoints: Sparking Innovation, Building the Solution, and "
            "Driving Impact. Professional healthcare palette of navy blue, teal, "
            "and white. Minimalist flat vector style. Subtle motion along the "
            "roadmap path."
        ),
        "sound": None,
    },
    {
        "name": "V4-knowledge-explosion-timeline",
        "filename": "V4-knowledge-explosion-timeline__kling-v2-6_pro_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "pro",
        "duration": "5",
        "prompt": (
            "A minimalist data-driven animation showing medical knowledge "
            "doubling from 50 years in 1950 to 73 days in 2026. The timeline "
            "compresses visually over time, starting slow and accelerating "
            "rapidly. Clean sans-serif typography, dark background, teal "
            "accents, highly legible educational motion graphics."
        ),
        "sound": None,
    },
    {
        "name": "V5-physician-innovator-lineage",
        "filename": "V5-physician-innovator-lineage__kling-v2-6_pro_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "pro",
        "duration": "5",
        "prompt": (
            "A polished split-screen montage showing diverse physician "
            "innovators across process innovation, device innovation, "
            "technological innovation, and organizational innovation. "
            "Professional medical aesthetic, four-quadrant composition, subtle "
            "camera movement and transitions between quadrants, respectful and "
            "authoritative tone."
        ),
        "sound": None,
    },
    {
        "name": "V6-module-bridge-transition",
        "filename": "V6-module-bridge-transition__kling-v2-6_pro_5s.mp4",
        "model_name": "kling-v2-6",
        "mode": "pro",
        "duration": "5",
        "prompt": (
            "A clean closing transition for a medical education module. Dark "
            "navy background, bridge graphic connecting Module 1 Mindset to "
            "Module 2 Leadership Identity, restrained teal motion sweep, "
            "polished healthcare brand aesthetic, concise and elegant visual "
            "bridge. Subtle ambient transition audio if supported."
        ),
        "sound": True,
    },
    {
        "name": "V2-clinical-to-innovator-pathway",
        "filename": "V2-clinical-to-innovator-pathway__kling-v3-0_pro_5s.mp4",
        "model_name": "kling-v3-0",
        "mode": "pro",
        "duration": "5",
        "prompt": (
            "A clean animation on dark navy background showing a traditional "
            "clinical pathway with medical cross icons that diverges into a new "
            "streamlined innovator pathway with glowing teal nodes. Smooth "
            "restrained corporate healthcare motion design, highly legible, "
            "professional medical aesthetic."
        ),
        "sound": True,
    },
]


def write_manifest(rows: list[dict[str, str]]) -> None:
    """Write the current generation manifest to disk."""
    fieldnames = [
        "clip",
        "filename",
        "model_name",
        "mode",
        "duration",
        "status",
        "task_id",
        "notes",
    ]
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_manifest() -> list[dict[str, str]]:
    """Load existing manifest if present."""
    if not MANIFEST.exists():
        return []
    with MANIFEST.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def submit_with_backoff(client: KlingClient, job: dict[str, object]) -> tuple[str, str]:
    """Submit a job with concurrency backoff and optional audio fallback."""
    delay = 2
    current_job = dict(job)
    while True:
        if current_job.get("existing_task_id"):
            return str(current_job["existing_task_id"]), "existing task reused"
        try:
            result = client.text_to_video(
                str(current_job["prompt"]),
                model_name=str(current_job["model_name"]),
                duration=str(current_job["duration"]),
                mode=str(current_job["mode"]),
                aspect_ratio="16:9",
                negative_prompt=NEG,
                sound=current_job.get("sound"),
            )
            return str(result["data"]["task_id"]), "submitted"
        except Exception as exc:  # pragma: no cover - network/runtime path
            body = getattr(exc, "response_body", {}) or {}
            code = body.get("code")
            if current_job.get("sound") is not None and code == 1201:
                print(f"FALLBACK_NO_SOUND {current_job['filename']} {body}", flush=True)
                current_job["sound"] = None
                continue
            if code == 1303:
                print(
                    f"BACKOFF {current_job['filename']} concurrency limit; sleeping {delay}s",
                    flush=True,
                )
                time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            raise


def poll_and_download(
    client: KlingClient,
    task_id: str,
    filename: str,
) -> tuple[str, str]:
    """Poll a task to completion and download the result."""
    while True:
        data = client.get_task_status(task_id, task_type="text2video")
        status = data.get("data", {}).get("task_status", "")
        print(f"STATUS {filename} {status}", flush=True)
        if status == "succeed":
            videos = data.get("data", {}).get("task_result", {}).get("videos", [])
            if not videos:
                return "no_video_url", "No videos in task_result"
            url = videos[0].get("url")
            client.download_video(url, OUTDIR / filename)
            return "downloaded", f"downloaded {filename}"
        if status == "failed":
            message = data.get("data", {}).get("task_status_msg", "")
            return "failed", message or "task failed"
        time.sleep(10)


def main() -> int:
    """Run the serialized validation queue."""
    client = KlingClient()
    rows: list[dict[str, str]] = load_manifest()
    if not rows:
        baseline_file = OUTDIR / "V1-hospital-broll__kling-v1-6_std_5s.mp4"
        if baseline_file.exists():
            rows.append(
                {
                    "clip": "V1-hospital-broll",
                    "filename": baseline_file.name,
                    "model_name": "kling-v1-6",
                    "mode": "std",
                    "duration": "5",
                    "status": "downloaded",
                    "task_id": "",
                    "notes": "initial live validation clip",
                }
            )
        write_manifest(rows)

    existing_by_filename = {row["filename"]: row for row in rows}

    for job in JOBS:
        filename = str(job["filename"])
        existing = existing_by_filename.get(filename)
        if existing and existing.get("status") == "downloaded":
            print(f"SKIP {filename} already downloaded", flush=True)
            continue
        print(
            f"START {filename} model={job['model_name']} mode={job['mode']} duration={job['duration']} sound={job.get('sound')}",
            flush=True,
        )
        try:
            if existing and existing.get("status") == "submitted" and existing.get("task_id"):
                task_id = existing["task_id"]
                note = existing.get("notes", "resuming submitted task")
                print(f"RESUME {filename} task_id={task_id}", flush=True)
            else:
                task_id, note = submit_with_backoff(client, job)
                row = {
                    "clip": str(job["name"]),
                    "filename": filename,
                    "model_name": str(job["model_name"]),
                    "mode": str(job["mode"]),
                    "duration": str(job["duration"]),
                    "status": "submitted",
                    "task_id": task_id,
                    "notes": note,
                }
                rows.append(row)
                existing_by_filename[filename] = row
                write_manifest(rows)
            status, status_note = poll_and_download(client, task_id, filename)
            existing_by_filename[filename]["status"] = status
            existing_by_filename[filename]["notes"] = status_note
            write_manifest(rows)
            print(f"DONE_ITEM {filename} {status} {status_note}", flush=True)
        except Exception as exc:
            note = f"{type(exc).__name__}: {exc}"
            if filename not in existing_by_filename:
                row = {
                    "clip": str(job["name"]),
                    "filename": filename,
                    "model_name": str(job["model_name"]),
                    "mode": str(job["mode"]),
                    "duration": str(job["duration"]),
                    "status": "failed",
                    "task_id": "",
                    "notes": note,
                }
                rows.append(row)
                existing_by_filename[filename] = row
            else:
                existing_by_filename[filename]["status"] = "failed"
                existing_by_filename[filename]["notes"] = note
            write_manifest(rows)
            print(f"FAILED_ITEM {filename} {note}", flush=True)
        time.sleep(15)

    print("ALL_DONE", flush=True)
    write_manifest(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
