# /// script
# requires-python = ">=3.10"
# ///
"""Build a static HTML + JSON storyboard from Gary's dispatch payload.

Emits ``storyboard/storyboard.json`` and ``storyboard/index.html`` under
``--out-dir``. Use ``summarize`` to print a manifest-derived recap for
conversational approval (Marcus + operator).
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import yaml
except ImportError:  # pragma: no cover - optional for yaml input
    yaml = None  # type: ignore[assignment]


def load_payload(path: Path) -> dict[str, Any]:
    """Load Gary dispatch JSON or YAML."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yml", ".yaml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML payload files")
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Payload top level must be an object")
    return data


def _is_remote_ref(ref: str) -> bool:
    ref = ref.strip()
    if not ref:
        return False
    parsed = urlparse(ref)
    return parsed.scheme in {"http", "https"}


def build_manifest(
    payload: dict[str, Any],
    *,
    payload_path: Path,
    storyboard_dir: Path,
    asset_base: Path,
) -> dict[str, Any]:
    """Return manifest dict and do not write files."""
    slides_in = payload.get("gary_slide_output")
    if not isinstance(slides_in, list):
        raise ValueError("gary_slide_output must be a list")
    storyboard_dir = storyboard_dir.resolve()
    slides_out: list[dict[str, Any]] = []

    for idx, raw in enumerate(slides_in, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"gary_slide_output[{idx}] must be an object")
        slide_id = str(raw.get("slide_id", "")).strip()
        if not slide_id:
            raise ValueError(f"gary_slide_output[{idx}].slide_id is required")
        fidelity = str(raw.get("fidelity", "creative") or "creative").strip()
        card_number = raw.get("card_number")
        source_ref = str(raw.get("source_ref", "") or "").strip()
        file_path_raw = str(raw.get("file_path", "") or "").strip()
        display_title = str(raw.get("title") or raw.get("display_title") or slide_id).strip()

        html_asset_ref = ""
        asset_status = "missing"

        if not file_path_raw:
            asset_status = "missing"
        elif _is_remote_ref(file_path_raw):
            html_asset_ref = file_path_raw
            asset_status = "remote"
        else:
            abs_candidate = (asset_base / file_path_raw).resolve()
            if abs_candidate.is_file():
                html_asset_ref = Path(os.path.relpath(abs_candidate, storyboard_dir)).as_posix()
                asset_status = "present"
            else:
                html_asset_ref = file_path_raw
                asset_status = "missing"

        slides_out.append(
            {
                "sequence": idx,
                "slide_id": slide_id,
                "fidelity": fidelity,
                "card_number": card_number,
                "source_ref": source_ref,
                "file_path": file_path_raw,
                "display_title": display_title,
                "asset_status": asset_status,
                "html_asset_ref": html_asset_ref,
            }
        )

    return {
        "storyboard_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_payload": payload_path.resolve().as_posix(),
        "asset_base": asset_base.resolve().as_posix(),
        "slides": slides_out,
    }


def format_summary(manifest: dict[str, Any]) -> str:
    """Human-facing lines derived only from manifest (for Marcus to read aloud)."""
    slides = manifest.get("slides")
    if not isinstance(slides, list) or not slides:
        return "Storyboard summary: zero slides in manifest."

    ids = [str(s.get("slide_id", "")) for s in slides if isinstance(s, dict)]
    fids = [
        str(s.get("fidelity", "unknown"))
        for s in slides
        if isinstance(s, dict)
    ]
    counts = Counter(fids)
    lines = [
        f"Storyboard summary: {len(slides)} slide(s).",
        f"First slide_id: {ids[0]!r}; last slide_id: {ids[-1]!r}.",
        "Fidelity counts: "
        + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
    ]
    missing_n = sum(
        1
        for s in slides
        if isinstance(s, dict) and s.get("asset_status") == "missing"
    )
    if missing_n:
        lines.append(f"Warning: {missing_n} slide(s) have missing local assets.")
    return "\n".join(lines)


def render_index_html(manifest: dict[str, Any]) -> str:
    """Single-page table; view-only (no forms)."""
    slides = manifest.get("slides")
    if not isinstance(slides, list):
        slides = []
    rows: list[str] = []
    for s in slides:
        if not isinstance(s, dict):
            continue
        seq = html.escape(str(s.get("sequence", "")))
        sid = html.escape(str(s.get("slide_id", "")))
        fid = html.escape(str(s.get("fidelity", "")))
        card = html.escape(str(s.get("card_number", "")))
        title = html.escape(str(s.get("display_title", "")))
        sref = html.escape(str(s.get("source_ref", "")))
        fpath = html.escape(str(s.get("file_path", "")))
        status = html.escape(str(s.get("asset_status", "")))
        ref = str(s.get("html_asset_ref", "") or "")

        if s.get("asset_status") == "present" and ref:
            preview = (
                f'<img src="{html.escape(ref, quote=True)}" '
                'alt="" style="max-width:120px;max-height:80px;object-fit:contain;" />'
            )
        elif s.get("asset_status") == "remote" and ref:
            preview = (
                f'<a href="{html.escape(ref, quote=True)}">open URL</a><br/>'
                f'<img src="{html.escape(ref, quote=True)}" '
                'alt="" style="max-width:120px;max-height:80px;object-fit:contain;" />'
            )
        else:
            preview = '<strong class="missing">MISSING</strong>'

        rows.append(
            "<tr>"
            f"<td>{seq}</td><td>{sid}</td><td>{fid}</td><td>{card}</td>"
            f"<td>{preview}</td><td>{title}</td><td>{sref}</td>"
            f"<td>{fpath}</td><td>{status}</td>"
            "</tr>"
        )

    body_rows = "\n".join(rows) if rows else "<tr><td colspan='9'>No slides</td></tr>"
    gen_at = html.escape(str(manifest.get("generated_at", "")))
    cap = f"Storyboard (view-only) — generated {gen_at}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Storyboard review</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 1rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 0.35rem 0.5rem; vertical-align: top; }}
    th {{ background: #f4f4f4; text-align: left; }}
    .missing {{ color: #b00020; }}
    caption {{ text-align: left; font-weight: bold; margin-bottom: 0.5rem; }}
  </style>
</head>
<body>
  <table>
    <caption>{cap}</caption>
    <thead>
      <tr>
        <th>#</th><th>slide_id</th><th>fidelity</th><th>card</th>
        <th>preview</th><th>title</th><th>source_ref</th><th>file_path</th><th>asset_status</th>
      </tr>
    </thead>
    <tbody>
{body_rows}
    </tbody>
  </table>
</body>
</html>
"""


def write_bundle(
    manifest: dict[str, Any],
    storyboard_dir: Path,
) -> None:
    storyboard_dir.mkdir(parents=True, exist_ok=True)
    json_path = storyboard_dir / "storyboard.json"
    html_path = storyboard_dir / "index.html"
    json_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    html_path.write_text(render_index_html(manifest), encoding="utf-8")


def cmd_generate(args: argparse.Namespace) -> int:
    payload_path: Path = args.payload
    out_dir: Path = args.out_dir
    asset_base: Path = args.asset_base or payload_path.parent
    storyboard_dir = (out_dir / "storyboard").resolve()

    payload = load_payload(payload_path)
    manifest = build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=asset_base.resolve(),
    )
    write_bundle(manifest, storyboard_dir)

    missing = sum(
        1
        for s in manifest["slides"]
        if isinstance(s, dict) and s.get("asset_status") == "missing"
    )
    print(f"Wrote {storyboard_dir / 'storyboard.json'}")
    print(f"Wrote {storyboard_dir / 'index.html'}")
    if args.print_summary:
        print()
        print(format_summary(manifest))
    if args.strict and missing:
        print(f"Strict mode: {missing} missing asset(s).", file=sys.stderr)
        return 1
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    path: Path = args.manifest
    data = json.loads(path.read_text(encoding="utf-8"))
    print(format_summary(data))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Gary dispatch → static storyboard bundle")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Build storyboard.json + index.html")
    gen.add_argument("--payload", type=Path, required=True, help="Gary dispatch JSON/YAML")
    gen.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory under which storyboard/ will be created",
    )
    gen.add_argument(
        "--asset-base",
        type=Path,
        default=None,
        help="Resolve relative file_path against this directory (default: payload parent)",
    )
    gen.add_argument(
        "--print-summary",
        action="store_true",
        help="After write, print manifest-derived summary to stdout",
    )
    gen.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any slide has asset_status missing",
    )
    gen.set_defaults(func=cmd_generate)

    summ = sub.add_parser("summarize", help="Print summary from existing storyboard.json")
    summ.add_argument("--manifest", type=Path, required=True)
    summ.set_defaults(func=cmd_summarize)

    args = parser.parse_args()
    try:
        return int(args.func(args))
    except Exception as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
