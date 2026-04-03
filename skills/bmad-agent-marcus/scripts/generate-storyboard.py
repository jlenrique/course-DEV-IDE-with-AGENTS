# /// script
# requires-python = ">=3.10"
# ///
"""Build a static HTML + JSON storyboard from Gary's dispatch payload.

Emits ``storyboard/storyboard.json`` and ``storyboard/index.html`` under
``--out-dir``. Use ``summarize`` to print a manifest-derived recap for
conversational approval (Marcus + operator).

**Before Irene (Pass 2):** Gary dispatch only — each row shows the slide;
the script column is *Pending (pre–Pass 2)*.

**After Irene:** pass ``--segment-manifest`` (YAML) with ``segments[]`` entries
that include ``gary_slide_id`` (or ``slide_id``) and ``narration_text`` per
``template-segment-manifest.md`` — the same row shows slide preview + script.
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger("generate_storyboard")


def _log_run_suffix(run_id: str | None) -> str:
    """Optional APP run correlation for log messages."""
    if run_id is None or not str(run_id).strip():
        return ""
    return f" run_id={str(run_id).strip()}"

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


def _resolve_asset_ref(
    raw_ref: str,
    *,
    storyboard_dir: Path,
    asset_base: Path,
) -> tuple[str, str]:
    """Resolve an asset/file reference to HTML-friendly path + status.

    Returns tuple: (html_asset_ref, asset_status).
    """
    raw_ref = raw_ref.strip()
    if not raw_ref:
        return "", "missing"
    if _is_remote_ref(raw_ref):
        return raw_ref, "remote"

    try:
        abs_candidate = (asset_base / raw_ref).resolve()
        if abs_candidate.is_file():
            rel = Path(os.path.relpath(abs_candidate, storyboard_dir)).as_posix()
            return rel, "present"
    except OSError:
        return raw_ref, "missing"
    return raw_ref, "missing"


def load_narration_by_slide_id(path: Path) -> dict[str, str]:
    """Load segment manifest YAML; map gary_slide_id/slide_id → narration_text.

    Multiple segments per slide_id are joined with a horizontal rule separator.
    """
    if yaml is None:
        raise RuntimeError("PyYAML is required for --segment-manifest (YAML) files")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Segment manifest top level must be a mapping")
    segments = raw.get("segments")
    if segments is None:
        return {}
    if not isinstance(segments, list):
        raise ValueError("segments must be a list")

    chunks: dict[str, list[str]] = {}
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        sid_raw = seg.get("gary_slide_id") or seg.get("slide_id")
        if not isinstance(sid_raw, str) or not sid_raw.strip():
            continue
        sid = sid_raw.strip()
        nt = seg.get("narration_text")
        if nt is None or not str(nt).strip():
            continue
        chunks.setdefault(sid, []).append(str(nt).strip())

    return {k: "\n\n---\n\n".join(v) for k, v in chunks.items()}


def load_related_assets(
    path: Path,
    *,
    storyboard_dir: Path,
    asset_base: Path,
) -> list[dict[str, Any]]:
    """Load optional non-slide related assets from JSON or YAML.

    Supported top-level shapes:
    - list[object]
    - {"related_assets": list[object]} (also accepts assets/items)
    """
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yml", ".yaml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML related assets")
        data: Any = yaml.safe_load(text)
    else:
        data = json.loads(text)

    entries: Any = data
    if isinstance(data, dict):
        entries = data.get("related_assets")
        if entries is None:
            entries = data.get("assets")
        if entries is None:
            entries = data.get("items")
    if not isinstance(entries, list):
        raise ValueError("related assets must be a list or an object containing related_assets")

    out: list[dict[str, Any]] = []
    for idx, item in enumerate(entries, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"related_assets[{idx}] must be an object")

        label = str(item.get("label", "")).strip()
        if not label:
            raise ValueError(f"related_assets[{idx}].label is required")

        link_raw = str(
            item.get("link")
            or item.get("href")
            or item.get("file_path")
            or ""
        ).strip()
        if not link_raw:
            raise ValueError(f"related_assets[{idx}].link is required")

        html_asset_ref, asset_status = _resolve_asset_ref(
            link_raw,
            storyboard_dir=storyboard_dir,
            asset_base=asset_base,
        )
        out.append(
            {
                "row_kind": "related_asset",
                "sequence": idx,
                "asset_type": str(item.get("asset_type") or item.get("type") or "other").strip(),
                "label": label,
                "link": link_raw,
                "source_ref": str(item.get("source_ref") or "").strip(),
                "stage": str(item.get("stage") or "").strip(),
                "asset_status": asset_status,
                "html_asset_ref": html_asset_ref,
            }
        )
    return out


def build_manifest(
    payload: dict[str, Any],
    *,
    payload_path: Path,
    storyboard_dir: Path,
    asset_base: Path,
    narration_by_slide_id: dict[str, str] | None = None,
    segment_manifest_path: Path | None = None,
    related_assets: list[dict[str, Any]] | None = None,
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

        html_asset_ref, asset_status = _resolve_asset_ref(
            file_path_raw,
            storyboard_dir=storyboard_dir,
            asset_base=asset_base,
        )

        narration_text = ""
        narration_status = "pending"
        if narration_by_slide_id:
            matched = narration_by_slide_id.get(slide_id)
            if matched is not None and str(matched).strip():
                narration_text = str(matched).strip()
                narration_status = "present"

        slides_out.append(
            {
                "sequence": idx,
                "row_kind": "slide",
                "slide_id": slide_id,
                "fidelity": fidelity,
                "card_number": card_number,
                "source_ref": source_ref,
                "file_path": file_path_raw,
                "display_title": display_title,
                "asset_status": asset_status,
                "html_asset_ref": html_asset_ref,
                "narration_text": narration_text,
                "narration_status": narration_status,
            }
        )

    with_script_n = sum(
        1 for s in slides_out if isinstance(s, dict) and s.get("narration_status") == "present"
    )
    view = "slides_with_script" if with_script_n else "slides_only"
    related_assets = related_assets or []
    rows: list[dict[str, Any]] = [*slides_out]
    normalized_related_assets: list[dict[str, Any]] = []
    if related_assets:
        for idx, item in enumerate(related_assets, start=1):
            row = dict(item)
            row["sequence"] = len(slides_out) + idx
            row.setdefault("row_kind", "related_asset")
            normalized_related_assets.append(row)
            rows.append(row)

    out: dict[str, Any] = {
        "storyboard_version": 3,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_payload": payload_path.resolve().as_posix(),
        "asset_base": asset_base.resolve().as_posix(),
        "storyboard_view": view,
        "slides": slides_out,
        "related_assets": normalized_related_assets,
        "rows": rows,
    }
    if segment_manifest_path is not None:
        out["segment_manifest_source"] = segment_manifest_path.resolve().as_posix()
    return out


def format_summary(manifest: dict[str, Any]) -> str:
    """Human-facing lines derived only from manifest (for Marcus to read aloud)."""
    slides = manifest.get("slides")
    if not isinstance(slides, list) or not slides:
        return "Storyboard summary: zero slides in manifest."

    ids = [str(s.get("slide_id", "")) for s in slides if isinstance(s, dict)]
    if not ids:
        return "Storyboard summary: zero valid slide_id entries in manifest slides."
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

    view = str(manifest.get("storyboard_view") or "")
    narrated = sum(
        1
        for s in slides
        if isinstance(s, dict) and s.get("narration_status") == "present"
    )
    if view == "slides_with_script" or narrated:
        lines.append(
            f"Narration: {narrated}/{len(slides)} slide(s) have script text attached."
        )
    elif manifest.get("segment_manifest_source"):
        lines.append("Narration: segment manifest provided but no slide matched narration_text.")
    related = manifest.get("related_assets")
    if isinstance(related, list) and related:
        lines.append(f"Related assets: {len(related)} row(s) appended after slides.")
    return "\n".join(lines)


def render_index_html(manifest: dict[str, Any]) -> str:
    """Single-page table; view-only (no forms)."""
    rows_in = manifest.get("rows")
    if not isinstance(rows_in, list):
        rows_in = manifest.get("slides")
    if not isinstance(rows_in, list):
        rows_in = []
    rows: list[str] = []
    for s in rows_in:
        if not isinstance(s, dict):
            continue
        if str(s.get("row_kind") or "slide") == "related_asset":
            seq = html.escape(str(s.get("sequence", "")))
            asset_type = html.escape(str(s.get("asset_type") or "other"))
            label = html.escape(str(s.get("label") or ""))
            source_ref = html.escape(str(s.get("source_ref") or ""))
            link = html.escape(str(s.get("link") or ""))
            status = html.escape(str(s.get("asset_status") or "missing"))
            stage = html.escape(str(s.get("stage") or ""))
            href = str(s.get("html_asset_ref") or "")

            if href:
                preview = f'<a href="{html.escape(href, quote=True)}">open asset</a>'
            else:
                preview = '<strong class="missing">MISSING</strong>'

            script_cell = f"<span>{stage or 'N/A'}</span>"
            rows.append(
                "<tr>"
                f"<td>{seq}</td><td>(related)</td><td>{asset_type}</td><td></td>"
                f"<td>{preview}</td><td>{label}</td><td>{source_ref}</td>"
                f"<td>{link}</td><td>{status}</td><td>{script_cell}</td>"
                "</tr>"
            )
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

        nstat = str(s.get("narration_status") or "pending")
        ntext = str(s.get("narration_text") or "")
        if nstat == "present" and ntext.strip():
            script_cell = (
                f'<pre class="narration-text">{html.escape(ntext)}</pre>'
            )
        else:
            script_cell = (
                '<span class="pending-script">Pending (pre-Pass 2)</span>'
            )

        rows.append(
            "<tr>"
            f"<td>{seq}</td><td>{sid}</td><td>{fid}</td><td>{card}</td>"
            f"<td>{preview}</td><td>{title}</td><td>{sref}</td>"
            f"<td>{fpath}</td><td>{status}</td><td>{script_cell}</td>"
            "</tr>"
        )

    body_rows = "\n".join(rows) if rows else "<tr><td colspan='10'>No slides</td></tr>"
    gen_at = html.escape(str(manifest.get("generated_at", "")))
    view = html.escape(str(manifest.get("storyboard_view") or "slides_only"))
    cap = f"Storyboard (view-only) — {view} — generated {gen_at}"

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
    .pending-script {{ color: #666; font-style: italic; }}
    .narration-text {{
      white-space: pre-wrap; max-width: 36rem; max-height: 16rem;
      overflow: auto; margin: 0; font-family: inherit; font-size: 0.9rem;
    }}
    caption {{ text-align: left; font-weight: bold; margin-bottom: 0.5rem; }}
  </style>
</head>
<body>
  <table>
    <caption>{cap}</caption>
    <thead>
      <tr>
        <th>#</th><th>slide_id</th><th>fidelity</th><th>card</th>
        <th>preview</th><th>title</th><th>source_ref</th><th>file_path</th>
        <th>asset_status</th><th>narration (Pass 2)</th>
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
    run_id: str | None = getattr(args, "run_id", None)
    payload_path: Path = args.payload
    out_dir: Path = args.out_dir
    asset_base: Path = args.asset_base or payload_path.parent
    storyboard_dir = (out_dir / "storyboard").resolve()

    payload = load_payload(payload_path)
    segment_manifest_path: Path | None = getattr(args, "segment_manifest", None)
    narration_map: dict[str, str] | None = None
    if segment_manifest_path is not None:
        narration_map = load_narration_by_slide_id(segment_manifest_path)
    related_assets_path: Path | None = getattr(args, "related_assets", None)
    related_assets: list[dict[str, Any]] | None = None
    if related_assets_path is not None:
        related_assets = load_related_assets(
            related_assets_path,
            storyboard_dir=storyboard_dir,
            asset_base=asset_base.resolve(),
        )

    manifest = build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=asset_base.resolve(),
        narration_by_slide_id=narration_map,
        segment_manifest_path=segment_manifest_path,
        related_assets=related_assets,
    )
    write_bundle(manifest, storyboard_dir)

    missing = sum(
        1
        for s in manifest["slides"]
        if isinstance(s, dict) and s.get("asset_status") == "missing"
    )
    slide_count = len(manifest.get("slides", []))
    logger.info(
        "Storyboard bundle written: slides=%d missing=%d path=%s%s",
        slide_count,
        missing,
        storyboard_dir,
        _log_run_suffix(run_id),
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
    gen.add_argument(
        "--segment-manifest",
        type=Path,
        default=None,
        help=(
            "Irene Pass 2 segment manifest YAML "
            "(segments[].gary_slide_id + narration_text) to attach script per slide"
        ),
    )
    gen.add_argument(
        "--related-assets",
        type=Path,
        default=None,
        help=(
            "Optional JSON/YAML file with related_assets rows to append after slides "
            "(each entry requires label + link)."
        ),
    )
    gen.add_argument(
        "--run-id",
        default=None,
        help="Optional APP production run ID for Channel-C log correlation.",
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
