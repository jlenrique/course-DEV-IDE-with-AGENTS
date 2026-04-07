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

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif"}


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


def _inspect_local_image_metadata(path: Path) -> dict[str, Any]:
    """Inspect local image metadata for storyboard review."""
    meta: dict[str, Any] = {
        "orientation": "unknown",
        "dimensions": None,
        "aspect_ratio": None,
    }
    from PIL import Image

    try:
        with Image.open(path) as img:
            width, height = img.size
    except Exception:  # pragma: no cover - defensive
        return meta

    if width > 0 and height > 0:
        meta["dimensions"] = {"width": width, "height": height}
        meta["aspect_ratio"] = f"{width}:{height}"
        if width > height:
            meta["orientation"] = "landscape"
        elif height > width:
            meta["orientation"] = "portrait"
        else:
            meta["orientation"] = "square"
    return meta


def _build_slide_row_id(slide_id: str, dispatch_variant: str | None, sequence: int) -> str:
    safe_slide_id = "".join(ch if ch.isalnum() else "-" for ch in slide_id).strip("-").lower()
    if not safe_slide_id:
        safe_slide_id = f"slide-{sequence}"
    if dispatch_variant:
        return f"slide-{safe_slide_id}-{dispatch_variant.lower()}"
    return f"slide-{safe_slide_id}"


def _resolve_preview_metadata(
    *,
    file_path_raw: str,
    html_asset_ref: str,
    asset_status: str,
    asset_base: Path,
) -> dict[str, Any]:
    preview_kind = "missing"
    preview_href = html_asset_ref
    orientation = "unknown"
    dimensions = None
    aspect_ratio = None

    suffix = Path(file_path_raw).suffix.lower()
    if asset_status == "missing":
        preview_kind = "missing"
    elif asset_status == "remote":
        preview_kind = "image" if suffix in _IMAGE_SUFFIXES else "link"
    elif suffix in _IMAGE_SUFFIXES:
        preview_kind = "image"
        local_path = (asset_base / file_path_raw).resolve()
        meta = _inspect_local_image_metadata(local_path)
        orientation = str(meta.get("orientation") or "unknown")
        dimensions = meta.get("dimensions")
        aspect_ratio = meta.get("aspect_ratio")
    else:
        preview_kind = "other"

    return {
        "preview_kind": preview_kind,
        "preview_href": preview_href,
        "orientation": orientation,
        "dimensions": dimensions,
        "aspect_ratio": aspect_ratio,
    }


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
    run_id: str | None = None,
) -> dict[str, Any]:
    """Return manifest dict and do not write files."""
    slides_in = payload.get("gary_slide_output")
    if not isinstance(slides_in, list):
        raise ValueError("gary_slide_output must be a list")
    storyboard_dir = storyboard_dir.resolve()
    slides_out: list[dict[str, Any]] = []
    pair_map: dict[str, dict[str, Any]] = {}

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
        dispatch_variant = str(raw.get("dispatch_variant") or "").strip().upper() or None
        selected = bool(raw.get("selected", False))
        vera_score = raw.get("vera_score")
        quinn_score = raw.get("quinn_score")
        findings = raw.get("findings") if isinstance(raw.get("findings"), list) else []
        visual_description = str(raw.get("visual_description") or "").strip()
        literal_visual_source = str(raw.get("literal_visual_source") or "").strip() or None

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
            else:
                narration_status = "no_match" if segment_manifest_path is not None else "pending"

        preview_meta = _resolve_preview_metadata(
            file_path_raw=file_path_raw,
            html_asset_ref=html_asset_ref,
            asset_status=asset_status,
            asset_base=asset_base.resolve(),
        )
        script_notes_parts: list[str] = []
        if visual_description:
            script_notes_parts.append(visual_description)
        if findings:
            script_notes_parts.append("Findings:\n- " + "\n- ".join(str(f) for f in findings))
        script_notes = "\n\n".join(part for part in script_notes_parts if part.strip())

        issue_flags: list[str] = []
        if asset_status == "missing":
            issue_flags.append("missing_asset")
        if narration_status == "no_match":
            issue_flags.append("no_match")
        if findings:
            issue_flags.append("has_findings")

        row_id = _build_slide_row_id(slide_id, dispatch_variant, idx)

        slides_out.append(
            {
                "sequence": idx,
                "row_id": row_id,
                "row_kind": "slide",
                "slide_id": slide_id,
                "fidelity": fidelity,
                "dispatch_variant": dispatch_variant,
                "selected": selected,
                "card_number": card_number,
                "source_ref": source_ref,
                "file_path": file_path_raw,
                "display_title": display_title,
                "asset_status": asset_status,
                "html_asset_ref": html_asset_ref,
                "preview_kind": preview_meta["preview_kind"],
                "preview_href": preview_meta["preview_href"],
                "orientation": preview_meta["orientation"],
                "dimensions": preview_meta["dimensions"],
                "aspect_ratio": preview_meta["aspect_ratio"],
                "vera_score": vera_score,
                "quinn_score": quinn_score,
                "findings": findings,
                "visual_description": visual_description,
                "literal_visual_source": literal_visual_source,
                "narration_text": narration_text,
                "narration_status": narration_status,
                "script_notes": script_notes,
                "issue_flags": issue_flags,
            }
        )

        if dispatch_variant:
            pair_key = str(card_number if card_number is not None else slide_id)
            pair = pair_map.setdefault(
                pair_key,
                {
                    "pair_key": pair_key,
                    "slide_id": slide_id,
                    "card_number": card_number,
                    "selected_variant": None,
                    "variants": {"A": None, "B": None},
                },
            )
            if dispatch_variant in {"A", "B"}:
                pair["variants"][dispatch_variant] = slides_out[-1]
            if selected:
                pair["selected_variant"] = dispatch_variant

    with_script_n = sum(
        1 for s in slides_out if isinstance(s, dict) and s.get("narration_status") == "present"
    )
    view = "slides_with_script" if with_script_n else "slides_only"
    checkpoint_label = "Storyboard B" if view == "slides_with_script" else "Storyboard A"
    related_assets = related_assets or []
    rows: list[dict[str, Any]] = [*slides_out]
    normalized_related_assets: list[dict[str, Any]] = []
    if related_assets:
        for idx, item in enumerate(related_assets, start=1):
            row = dict(item)
            row["sequence"] = len(slides_out) + idx
            row["row_id"] = f"related-{idx}"
            row.setdefault("row_kind", "related_asset")
            normalized_related_assets.append(row)
            rows.append(row)

    missing_assets = sum(1 for s in slides_out if s.get("asset_status") == "missing")
    remote_assets = sum(1 for s in slides_out if s.get("asset_status") == "remote")
    pending_narration = sum(
        1 for s in slides_out if s.get("narration_status") in {"pending", "no_match"}
    )
    with_findings = sum(1 for s in slides_out if s.get("findings"))
    fidelity_counts = dict(Counter(str(s.get("fidelity", "unknown")) for s in slides_out))
    first_slide_id = slides_out[0]["slide_id"] if slides_out else None
    last_slide_id = slides_out[-1]["slide_id"] if slides_out else None

    out: dict[str, Any] = {
        "storyboard_version": 3,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_payload": payload_path.resolve().as_posix(),
        "asset_base": asset_base.resolve().as_posix(),
        "storyboard_view": view,
        "checkpoint_label": checkpoint_label,
        "slides": slides_out,
        "related_assets": normalized_related_assets,
        "run_id": run_id,
        "rows": rows,
        "review_meta": {
            "total_slides": len(slides_out),
            "missing_assets": missing_assets,
            "remote_assets": remote_assets,
            "slides_with_narration": with_script_n,
            "pending_narration": pending_narration,
            "related_asset_count": len(normalized_related_assets),
            "double_dispatch_enabled": bool(pair_map),
            "slides_with_findings": with_findings,
            "fidelity_counts": fidelity_counts,
            "first_slide_id": first_slide_id,
            "last_slide_id": last_slide_id,
        },
    }

    if pair_map:
        variant_pairs = [pair_map[k] for k in sorted(pair_map.keys(), key=lambda x: int(x) if x.isdigit() else x)]
        selected_pairs = sum(1 for pair in variant_pairs if pair.get("selected_variant"))
        out["double_dispatch"] = {
            "enabled": True,
            "selection_progress": {
                "selected": selected_pairs,
                "total": len(variant_pairs),
            },
            "variant_pairs": variant_pairs,
        }

        selected_preview: list[dict[str, Any]] = []
        for pair in variant_pairs:
            chosen = pair["selected_variant"]
            if chosen in {"A", "B"}:
                winner = pair["variants"].get(chosen)
                if isinstance(winner, dict):
                    selected_preview.append(winner)
        out["selected_full_deck_preview"] = selected_preview
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
    review_meta = manifest.get("review_meta") if isinstance(manifest.get("review_meta"), dict) else {}
    counts = Counter(fids)
    checkpoint_label = str(manifest.get("checkpoint_label") or "Storyboard")
    lines = [
        f"{checkpoint_label} summary: {len(slides)} slide(s).",
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
    generated_at = str(manifest.get("generated_at") or "").strip()
    if generated_at:
        lines.append(f"Generated at: {generated_at}")
    if review_meta:
        lines.append(
            "Review status: "
            f"missing_assets={review_meta.get('missing_assets', 0)}, "
            f"pending_narration={review_meta.get('pending_narration', 0)}, "
            f"slides_with_findings={review_meta.get('slides_with_findings', 0)}"
        )
    return "\n".join(lines)


def render_index_html(manifest: dict[str, Any]) -> str:
    """Single-page table; view-only (no forms)."""
    return render_index_html_v2(manifest)
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
        variant = html.escape(str(s.get("dispatch_variant") or ""))
        card = html.escape(str(s.get("card_number", "")))
        title = html.escape(str(s.get("display_title", "")))
        sref = html.escape(str(s.get("source_ref", "")))
        fpath = html.escape(str(s.get("file_path", "")))
        status = html.escape(str(s.get("asset_status", "")))
        selected_badge = "<strong>yes</strong>" if bool(s.get("selected")) else ""
        quality_text = html.escape(
            f"Vera={s.get('vera_score', 'n/a')} | Quinn={s.get('quinn_score', 'n/a')}"
        )
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
            f"<td>{seq}</td><td>{sid}</td><td>{fid}</td><td>{variant}</td><td>{card}</td>"
            f"<td>{preview}</td><td>{title}</td><td>{sref}</td>"
            f"<td>{fpath}</td><td>{status}</td><td>{quality_text}</td><td>{selected_badge}</td><td>{script_cell}</td>"
            "</tr>"
        )

    body_rows = "\n".join(rows) if rows else "<tr><td colspan='13'>No slides</td></tr>"
    pair_section_rows: list[str] = []
    dd = manifest.get("double_dispatch") if isinstance(manifest.get("double_dispatch"), dict) else {}
    for pair in dd.get("variant_pairs", []) if isinstance(dd, dict) else []:
        if not isinstance(pair, dict):
            continue
        var_a = pair.get("variants", {}).get("A") if isinstance(pair.get("variants"), dict) else None
        var_b = pair.get("variants", {}).get("B") if isinstance(pair.get("variants"), dict) else None
        if not isinstance(var_a, dict) or not isinstance(var_b, dict):
            continue

        def _pair_preview(row: dict[str, Any]) -> str:
            href = str(row.get("html_asset_ref") or "")
            if href:
                return (
                    f'<img src="{html.escape(href, quote=True)}" '
                    'alt="" style="max-width:260px;max-height:150px;object-fit:contain;" />'
                )
            return '<strong class="missing">MISSING</strong>'

        pair_section_rows.append(
            "<tr>"
            f"<td>{html.escape(str(pair.get('card_number', '')))}</td>"
            f"<td>{_pair_preview(var_a)}</td>"
            f"<td>{_pair_preview(var_b)}</td>"
            f"<td>Vera={html.escape(str(var_a.get('vera_score', 'n/a')))}<br/>Quinn={html.escape(str(var_a.get('quinn_score', 'n/a')))}</td>"
            f"<td>Vera={html.escape(str(var_b.get('vera_score', 'n/a')))}<br/>Quinn={html.escape(str(var_b.get('quinn_score', 'n/a')))}</td>"
            f"<td>{html.escape(str(pair.get('selected_variant') or 'pending'))}</td>"
            "</tr>"
        )

    pair_section_html = ""
    if pair_section_rows:
        pair_section_html = (
            "<h2>Variant Selection (A/B side-by-side)</h2>"
            "<table><thead><tr>"
            "<th>card</th><th>variant A</th><th>variant B</th><th>A scores</th><th>B scores</th><th>selected</th>"
            "</tr></thead><tbody>"
            + "\n".join(pair_section_rows)
            + "</tbody></table>"
        )

    selected_preview_rows: list[str] = []
    for item in manifest.get("selected_full_deck_preview", []) if isinstance(manifest.get("selected_full_deck_preview"), list) else []:
        if not isinstance(item, dict):
            continue
        href = str(item.get("html_asset_ref") or "")
        preview = (
            f'<img src="{html.escape(href, quote=True)}" alt="" style="max-width:320px;max-height:180px;object-fit:contain;" />'
            if href
            else '<strong class="missing">MISSING</strong>'
        )
        selected_preview_rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('card_number', '')))}</td>"
            f"<td>{html.escape(str(item.get('slide_id', '')))}</td>"
            f"<td>{preview}</td>"
            "</tr>"
        )

    selected_preview_html = ""
    if selected_preview_rows:
        selected_preview_html = (
            "<h2>Full-Deck Preview (selected variants)</h2>"
            "<table><thead><tr><th>card</th><th>slide_id</th><th>preview</th></tr></thead><tbody>"
            + "\n".join(selected_preview_rows)
            + "</tbody></table>"
        )
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
    {pair_section_html}
    {selected_preview_html}
    <table>
    <caption>{cap}</caption>
    <thead>
      <tr>
                <th>#</th><th>slide_id</th><th>fidelity</th><th>variant</th><th>card</th>
        <th>preview</th><th>title</th><th>source_ref</th><th>file_path</th>
                <th>asset_status</th><th>quality</th><th>selected</th><th>narration (Pass 2)</th>
      </tr>
    </thead>
    <tbody>
{body_rows}
    </tbody>
  </table>
</body>
</html>
"""


def render_index_html_v2(manifest: dict[str, Any]) -> str:
    """Reviewer-friendly storyboard surface with static progressive enhancement."""
    slides = manifest.get("slides") if isinstance(manifest.get("slides"), list) else []
    related_assets = manifest.get("related_assets") if isinstance(manifest.get("related_assets"), list) else []
    review_meta = manifest.get("review_meta") if isinstance(manifest.get("review_meta"), dict) else {}
    dd = manifest.get("double_dispatch") if isinstance(manifest.get("double_dispatch"), dict) else {}
    actionable_issue_count = sum(
        1
        for slide in slides
        if isinstance(slide, dict)
        and isinstance(slide.get("issue_flags"), list)
        and len(slide.get("issue_flags")) > 0
    )
    issue_controls_disabled = actionable_issue_count == 0
    issue_checkbox_attrs = ' disabled aria-disabled="true"' if issue_controls_disabled else ""
    issue_button_attrs = ' disabled aria-disabled="true"' if issue_controls_disabled else ""
    issue_button_label = "No issues" if issue_controls_disabled else "Next issue"
    issue_label_class = "toolbar-label disabled" if issue_controls_disabled else "toolbar-label"

    def _preview_markup(item: dict[str, Any], *, size: str = "card") -> str:
        href = str(item.get("preview_href") or item.get("html_asset_ref") or "")
        preview_kind = str(item.get("preview_kind") or "missing")
        row_id = html.escape(str(item.get("row_id") or "preview"), quote=True)
        title = html.escape(str(item.get("display_title") or item.get("label") or item.get("slide_id") or "Preview"))
        img_class = "slide-thumbnail" if size == "card" else "variant-thumbnail"
        if preview_kind == "image" and href:
            escaped_href = html.escape(href, quote=True)
            return (
                f'<a class="preview-link" data-role="preview-link" data-row-id="{row_id}" '
                f'data-preview-src="{escaped_href}" href="{escaped_href}" target="_blank" rel="noopener noreferrer">'
                f'<img class="{img_class}" src="{escaped_href}" alt="{title} preview" loading="lazy" />'
                '<span class="expand-cue" aria-hidden="true">[+]</span>'
                "</a>"
            )
        if preview_kind in {"link", "other"} and href:
            escaped_href = html.escape(href, quote=True)
            return (
                f'<a class="preview-link preview-link-text" data-role="preview-link" data-row-id="{row_id}" '
                f'href="{escaped_href}" target="_blank" rel="noopener noreferrer">Open asset</a>'
            )
        return '<div class="preview-missing">Preview unavailable</div>'

    pair_section_rows: list[str] = []
    for pair in dd.get("variant_pairs", []) if isinstance(dd, dict) else []:
        if not isinstance(pair, dict):
            continue
        var_a = pair.get("variants", {}).get("A") if isinstance(pair.get("variants"), dict) else None
        var_b = pair.get("variants", {}).get("B") if isinstance(pair.get("variants"), dict) else None
        if not isinstance(var_a, dict) or not isinstance(var_b, dict):
            continue
        pair_section_rows.append(
            "<tr>"
            f"<td>{html.escape(str(pair.get('card_number', '')))}</td>"
            f"<td>{_preview_markup(var_a, size='variant')}</td>"
            f"<td>{_preview_markup(var_b, size='variant')}</td>"
            f"<td>Vera={html.escape(str(var_a.get('vera_score', 'n/a')))}<br/>Quinn={html.escape(str(var_a.get('quinn_score', 'n/a')))}</td>"
            f"<td>Vera={html.escape(str(var_b.get('vera_score', 'n/a')))}<br/>Quinn={html.escape(str(var_b.get('quinn_score', 'n/a')))}</td>"
            f"<td>{html.escape(str(pair.get('selected_variant') or 'pending'))}</td>"
            "</tr>"
        )
    pair_section_html = ""
    if pair_section_rows:
        pair_section_html = (
            '<section class="variant-section">'
            "<h2>Variant Selection</h2>"
            '<table class="variant-table"><thead><tr>'
            "<th>card</th><th>variant A</th><th>variant B</th><th>A scores</th><th>B scores</th><th>selected</th>"
            "</tr></thead><tbody>"
            + "\n".join(pair_section_rows)
            + "</tbody></table></section>"
        )

    selected_preview_rows: list[str] = []
    for item in manifest.get("selected_full_deck_preview", []) if isinstance(manifest.get("selected_full_deck_preview"), list) else []:
        if not isinstance(item, dict):
            continue
        selected_preview_rows.append(
            '<div class="selected-card">'
            f'<div class="selected-card-meta">Card {html.escape(str(item.get("card_number", "")))} | {html.escape(str(item.get("slide_id", "")))}</div>'
            f'{_preview_markup(item, size="variant")}'
            "</div>"
        )
    selected_preview_html = ""
    if selected_preview_rows:
        selected_preview_html = (
            '<section class="selected-preview-section">'
            "<h2>Authorized Deck Preview</h2>"
            '<div class="selected-preview-grid">'
            + "\n".join(selected_preview_rows)
            + "</div></section>"
        )

    slide_cards: list[str] = []
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        issue_flags = slide.get("issue_flags") if isinstance(slide.get("issue_flags"), list) else []
        findings = slide.get("findings") if isinstance(slide.get("findings"), list) else []
        findings_markup = (
            '<ul class="finding-list">'
            + "".join(f"<li>{html.escape(str(finding))}</li>" for finding in findings)
            + "</ul>"
        ) if findings else '<p class="empty-state">No findings attached.</p>'

        narration_status = str(slide.get("narration_status") or "pending")
        narration_label = {
            "present": "Attached",
            "no_match": "No match",
            "pending": "Pending (pre-Pass 2)",
        }.get(narration_status, narration_status)
        narration_text = str(slide.get("narration_text") or "").strip()
        script_markup = (
            f'<pre class="script-text">{html.escape(narration_text)}</pre>'
            if narration_text
            else f'<div class="script-state">{html.escape(narration_label)}</div>'
        )
        script_notes = str(slide.get("script_notes") or "").strip()
        script_notes_markup = (
            f'<pre class="script-notes">{html.escape(script_notes)}</pre>'
            if script_notes
            else '<div class="script-state">No script notes attached.</div>'
        )

        fidelity = html.escape(str(slide.get("fidelity") or "unknown"))
        variant = html.escape(str(slide.get("dispatch_variant") or ""))
        orientation = html.escape(str(slide.get("orientation") or "unknown"))
        row_id = html.escape(str(slide.get("row_id") or slide.get("slide_id") or ""), quote=True)
        slide_id = html.escape(str(slide.get("slide_id") or ""))
        title = html.escape(str(slide.get("display_title") or slide.get("slide_id") or ""))
        sequence = html.escape(str(slide.get("sequence") or ""))
        card_number = html.escape(str(slide.get("card_number") or ""))
        source_ref = html.escape(str(slide.get("source_ref") or ""))
        file_path = html.escape(str(slide.get("file_path") or ""))
        asset_status = html.escape(str(slide.get("asset_status") or "unknown"))
        literal_visual_source = html.escape(str(slide.get("literal_visual_source") or "n/a"))
        dimensions = slide.get("dimensions") if isinstance(slide.get("dimensions"), dict) else {}
        dimensions_text = ""
        if dimensions:
            dimensions_text = f"{dimensions.get('width', '?')}×{dimensions.get('height', '?')}"
        dimensions_markup = html.escape(dimensions_text or "unknown")
        selected_markup = '<span class="badge badge-selected">selected</span>' if bool(slide.get("selected")) else ""
        issue_badges = "".join(f'<span class="badge badge-issue">{html.escape(str(flag))}</span>' for flag in issue_flags)
        variant_badge = f'<span class="badge">variant {variant}</span>' if variant else ""
        quality_text = html.escape(f"Vera {slide.get('vera_score', 'n/a')} | Quinn {slide.get('quinn_score', 'n/a')}")
        issue_attr = html.escape(" ".join(str(flag) for flag in issue_flags), quote=True)

        slide_cards.append(
            f'<article class="slide-card" id="{row_id}" data-role="slide-card" data-slide-id="{slide_id}" '
            f'data-fidelity="{fidelity}" data-orientation="{orientation}" data-issues="{issue_attr}">'
            '<header class="slide-card-header">'
            '<div class="slide-card-title-group">'
            f'<div class="sequence-pill">#{sequence}</div>'
            '<div>'
            f'<h2 class="slide-card-title">{title}</h2>'
            f'<div class="slide-card-subtitle">{slide_id}</div>'
            '</div></div>'
            '<div class="badge-row">'
            f'<span class="badge badge-fidelity">{fidelity}</span>'
            f'{variant_badge}'
            f'<span class="badge">card {card_number or "n/a"}</span>'
            f'<span class="badge">orientation {orientation}</span>'
            f'{selected_markup}{issue_badges}'
            '</div></header>'
            '<div class="slide-card-body">'
            '<section class="slide-preview-panel">'
            '<div class="panel-label">Slide preview</div>'
            f'{_preview_markup(slide)}'
            f'<div class="preview-caption">Asset status: <strong>{asset_status}</strong> | Dimensions: <strong>{dimensions_markup}</strong></div>'
            '</section>'
            '<section class="slide-script-panel">'
            '<div class="panel-grid">'
            '<div class="panel">'
            '<h3>Script</h3>'
            f'<div class="script-status">Status: {html.escape(narration_label)}</div>'
            f'{script_markup}'
            '</div>'
            '<div class="panel">'
            '<h3>Script notes</h3>'
            f'{script_notes_markup}'
            '</div>'
            '</div>'
            '<details class="evidence-panel"><summary>Evidence & provenance</summary>'
            '<dl class="evidence-list">'
            f'<div><dt>Source ref</dt><dd>{source_ref or "n/a"}</dd></div>'
            f'<div><dt>File path</dt><dd>{file_path or "n/a"}</dd></div>'
            f'<div><dt>Created</dt><dd>{html.escape(str(manifest.get("generated_at") or ""))}</dd></div>'
            f'<div><dt>Literal-visual source</dt><dd>{literal_visual_source}</dd></div>'
            f'<div><dt>Quality</dt><dd>{quality_text}</dd></div>'
            '</dl>'
            '<div class="findings-block">'
            '<h4>Findings</h4>'
            f'{findings_markup}'
            '</div>'
            '</details></section></div></article>'
        )

    related_markup = ""
    if related_assets:
        related_rows: list[str] = []
        for asset in related_assets:
            if not isinstance(asset, dict):
                continue
            related_rows.append(
                '<article class="related-card" data-role="related-asset">'
                f'<div class="related-meta">#{html.escape(str(asset.get("sequence") or ""))} | {html.escape(str(asset.get("asset_type") or "other"))}</div>'
                f'<h3>{html.escape(str(asset.get("label") or ""))}</h3>'
                f'<div class="related-stage">{html.escape(str(asset.get("stage") or "N/A"))}</div>'
                f'<div class="related-link">{_preview_markup(asset)}</div>'
                f'<div class="related-source">{html.escape(str(asset.get("source_ref") or "n/a"))}</div>'
                '</article>'
            )
        related_markup = (
            '<section class="related-assets-section">'
            '<h2>Related assets</h2>'
            '<div class="related-assets-grid">'
            + "\n".join(related_rows)
            + "</div></section>"
        )

    generated_at = html.escape(str(manifest.get("generated_at") or ""))
    view = html.escape(str(manifest.get("storyboard_view") or "slides_only"))
    checkpoint_label = html.escape(str(manifest.get("checkpoint_label") or "Storyboard"))
    run_id = html.escape(str(manifest.get("run_id") or "unbound"))
    meta_badges = [
        f'<span class="meta-pill">Run {run_id}</span>',
        f'<span class="meta-pill">{checkpoint_label}</span>',
        f'<span class="meta-pill">View {view}</span>',
        f'<span class="meta-pill">Slides {review_meta.get("total_slides", len(slides))}</span>',
        f'<span class="meta-pill">Narrated {review_meta.get("slides_with_narration", 0)}</span>',
        f'<span class="meta-pill">Missing assets {review_meta.get("missing_assets", 0)}</span>',
    ]
    if review_meta.get("double_dispatch_enabled"):
        meta_badges.append('<span class="meta-pill">Double dispatch</span>')
    fidelity_counts = review_meta.get("fidelity_counts") if isinstance(review_meta.get("fidelity_counts"), dict) else {}
    fidelity_markup = " | ".join(f"{html.escape(str(key))}: {html.escape(str(value))}" for key, value in sorted(fidelity_counts.items())) or "No fidelity counts"
    first_slide = html.escape(str(review_meta.get("first_slide_id") or "n/a"))
    last_slide = html.escape(str(review_meta.get("last_slide_id") or "n/a"))
    slides_markup = "\n".join(slide_cards) if slide_cards else '<div class="empty-state">No slides</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{checkpoint_label} review</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f6f8;
      --panel: #ffffff;
      --ink: #111827;
      --muted: #5b6472;
      --line: #d8dee8;
      --accent: #143b5d;
      --accent-soft: #dce8f4;
      --warning: #8a5300;
      --warning-soft: #fff3d6;
      --danger: #9b1c1c;
      --success-soft: #dff6e8;
      --shadow: 0 10px 25px rgba(17, 24, 39, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Segoe UI", system-ui, sans-serif; background: var(--bg); color: var(--ink); line-height: 1.5; }}
    a {{ color: var(--accent); }}
    .page {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}
    .summary-banner {{ background: linear-gradient(135deg, #0f2740, #1b4e73); color: #fff; border-radius: 20px; padding: 24px; box-shadow: var(--shadow); margin-bottom: 18px; }}
    .summary-banner h1 {{ margin: 0 0 8px 0; font-size: 1.9rem; }}
    .summary-banner p {{ margin: 0 0 14px 0; color: rgba(255,255,255,0.82); }}
    .meta-pill-row, .badge-row {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .meta-pill, .badge {{ display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 6px 12px; font-size: 0.86rem; font-weight: 600; }}
    .meta-pill {{ background: rgba(255,255,255,0.14); color: #fff; }}
    .summary-grid {{ display: grid; grid-template-columns: 1.3fr 1fr; gap: 18px; margin-top: 18px; }}
    .summary-panel {{ background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.14); border-radius: 16px; padding: 16px; }}
    .summary-panel h2 {{ margin: 0 0 10px 0; font-size: 1rem; }}
    .summary-panel p {{ margin: 0; color: rgba(255,255,255,0.88); }}
    .summary-panel dl {{ margin: 0; display: grid; grid-template-columns: auto 1fr; gap: 8px 12px; }}
    .summary-panel dt {{ color: rgba(255,255,255,0.7); font-weight: 600; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 14px 16px; margin-bottom: 18px; box-shadow: var(--shadow); }}
    .toolbar input[type="search"] {{ min-width: 260px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); font: inherit; }}
    .toolbar label {{ display: inline-flex; align-items: center; gap: 8px; font-size: 0.92rem; color: var(--muted); }}
    .toolbar button {{ padding: 9px 12px; border-radius: 10px; border: 1px solid var(--line); background: #fff; cursor: pointer; font: inherit; }}
    .toolbar button.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    .toolbar .disabled, .toolbar button:disabled, .toolbar input:disabled {{ opacity: 0.5; cursor: not-allowed; }}
    .slides-section {{ display: grid; gap: 18px; }}
    .slide-card, .related-card, .variant-section, .selected-preview-section, .related-assets-section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 18px; box-shadow: var(--shadow); }}
    .slide-card {{ overflow: hidden; }}
    .slide-card[hidden] {{ display: none !important; }}
    .slide-card-header {{ display: flex; justify-content: space-between; gap: 16px; padding: 18px 20px 12px; border-bottom: 1px solid var(--line); align-items: flex-start; }}
    .slide-card-title-group {{ display: flex; gap: 14px; align-items: flex-start; }}
    .sequence-pill {{ min-width: 50px; height: 50px; display: grid; place-items: center; background: var(--accent-soft); color: var(--accent); border-radius: 14px; font-weight: 800; font-size: 1rem; }}
    .slide-card-title {{ margin: 0; font-size: 1.12rem; }}
    .slide-card-subtitle {{ color: var(--muted); margin-top: 4px; font-size: 0.92rem; }}
    .badge {{ background: #eef2f7; color: #27313f; }}
    .badge-fidelity {{ background: var(--accent-soft); color: var(--accent); }}
    .badge-selected {{ background: var(--success-soft); color: #14532d; }}
    .badge-issue {{ background: var(--warning-soft); color: var(--warning); }}
    .slide-card-body {{ display: grid; grid-template-columns: minmax(280px, 420px) minmax(0, 1fr); gap: 18px; padding: 18px 20px 20px; }}
    .panel-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-bottom: 14px; }}
    .panel, .summary-panel, .related-card {{ min-width: 0; }}
    .panel {{ background: #fafbfd; border: 1px solid var(--line); border-radius: 14px; padding: 14px; }}
    .panel-label, .panel h3, .evidence-panel summary, .variant-section h2, .selected-preview-section h2, .related-assets-section h2 {{ font-size: 0.98rem; font-weight: 700; margin: 0 0 10px 0; }}
    .slide-thumbnail, .variant-thumbnail {{ width: 100%; border-radius: 14px; border: 1px solid var(--line); background: #fff; box-shadow: 0 6px 18px rgba(17, 24, 39, 0.08); }}
    .slide-thumbnail {{ max-height: 280px; object-fit: contain; background: #f8fafc; }}
    .variant-thumbnail {{ max-width: 260px; max-height: 150px; object-fit: contain; }}
    .preview-link {{ display: block; text-decoration: none; position: relative; }}
    .preview-link-text {{ display: inline-flex; align-items: center; justify-content: center; min-height: 120px; width: 100%; border: 1px dashed var(--line); border-radius: 14px; background: #fafafa; color: var(--accent); font-weight: 600; }}
    .expand-cue {{ position: absolute; top: 10px; right: 10px; background: rgba(15, 23, 42, 0.78); color: #fff; border-radius: 999px; padding: 4px 8px; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.02em; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.22); }}
    .preview-caption, .script-status, .related-stage, .related-source {{ color: var(--muted); font-size: 0.9rem; margin-top: 8px; }}
    .script-text, .script-notes {{ white-space: pre-wrap; margin: 0; font: inherit; line-height: 1.55; }}
    .script-state, .empty-state {{ color: var(--muted); font-style: italic; }}
    .evidence-panel {{ border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px; background: #fff; }}
    .evidence-panel summary {{ cursor: pointer; list-style: none; display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
    .evidence-panel summary::after {{ content: "[+]"; color: var(--muted); font-size: 0.85rem; font-weight: 700; }}
    .evidence-panel[open] summary::after {{ content: "[-]"; }}
    .evidence-list {{ margin: 12px 0 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 16px; }}
    .evidence-list dt {{ color: var(--muted); font-size: 0.85rem; font-weight: 700; }}
    .evidence-list dd {{ margin: 4px 0 0; font-size: 0.92rem; overflow-wrap: anywhere; }}
    .findings-block {{ margin-top: 14px; }}
    .finding-list {{ margin: 8px 0 0 18px; padding: 0; }}
    .variant-section, .selected-preview-section, .related-assets-section {{ padding: 18px 20px; margin-bottom: 18px; }}
    .variant-table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    .variant-table th, .variant-table td {{ border-top: 1px solid var(--line); padding: 10px; text-align: left; vertical-align: top; }}
    .selected-preview-grid, .related-assets-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }}
    .selected-card, .related-card {{ padding: 14px; }}
    .selected-card-meta, .related-meta {{ color: var(--muted); font-size: 0.86rem; margin-bottom: 8px; }}
    .preview-missing {{ display: grid; place-items: center; min-height: 140px; border-radius: 14px; border: 1px dashed var(--line); background: #fafafa; color: var(--danger); font-weight: 700; }}
    dialog.preview-dialog {{ width: min(96vw, 1400px); border: none; border-radius: 18px; padding: 0; box-shadow: 0 24px 50px rgba(17, 24, 39, 0.35); }}
    dialog::backdrop {{ background: rgba(17, 24, 39, 0.72); }}
    .dialog-body {{ background: #0f172a; color: #fff; padding: 16px; }}
    .dialog-toolbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; }}
    .dialog-toolbar button {{ background: rgba(255,255,255,0.12); color: #fff; border: none; border-radius: 10px; padding: 8px 12px; cursor: pointer; }}
    .dialog-preview {{ width: 100%; max-height: 82vh; object-fit: contain; background: #020617; border-radius: 14px; }}
    .sr-only {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }}
    @media (max-width: 980px) {{
      .summary-grid, .slide-card-body, .panel-grid {{ grid-template-columns: 1fr; }}
      .slide-card-header {{ flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="summary-banner">
      <h1>{checkpoint_label} Review</h1>
      <p>Static storyboard review surface for human approval. The JSON manifest remains the source of truth; this page is a reviewer-friendly projection.</p>
      <div class="meta-pill-row">{''.join(meta_badges)}</div>
      <div class="summary-grid">
        <div class="summary-panel">
          <h2>Run summary</h2>
          <p>Generated at {generated_at}. Fidelity mix: {fidelity_markup}.</p>
        </div>
        <div class="summary-panel">
          <h2>Orientation data</h2>
          <dl>
            <div><dt>First slide</dt><dd>{first_slide}</dd></div>
            <div><dt>Last slide</dt><dd>{last_slide}</dd></div>
            <div><dt>Pending narration</dt><dd>{html.escape(str(review_meta.get("pending_narration", 0)))}</dd></div>
            <div><dt>Slides with findings</dt><dd>{html.escape(str(review_meta.get("slides_with_findings", 0)))}</dd></div>
          </dl>
        </div>
      </div>
    </section>

    {pair_section_html}
    {selected_preview_html}

    <section class="toolbar" aria-label="Storyboard controls">
      <label>
        <span class="sr-only">Search slides</span>
        <input id="search-box" type="search" placeholder="Search slide id, title, source ref" data-role="search" />
      </label>
      <button type="button" class="active" data-role="filter" data-filter="all">All</button>
      <button type="button" data-role="filter" data-filter="creative">Creative</button>
      <button type="button" data-role="filter" data-filter="literal-text">Literal-text</button>
      <button type="button" data-role="filter" data-filter="literal-visual">Literal-visual</button>
      <label class="{issue_label_class}"><input type="checkbox" id="issues-only" data-role="issues-only"{issue_checkbox_attrs} /> Show issues only</label>
      <button type="button" data-role="jump-next-issue"{issue_button_attrs}>{issue_button_label}</button>
    </section>

    <section class="slides-section" aria-label="Storyboard slides">
      {slides_markup}
    </section>

    {related_markup}
  </div>

  <dialog class="preview-dialog" id="preview-dialog">
    <div class="dialog-body">
      <div class="dialog-toolbar">
        <strong id="dialog-title">Preview</strong>
        <div>
          <a id="dialog-open" href="#" target="_blank" rel="noopener noreferrer">Open in new tab</a>
          <button type="button" id="dialog-close">Close</button>
        </div>
      </div>
      <img id="dialog-image" class="dialog-preview" alt="" />
    </div>
  </dialog>

  <script>
    (() => {{
      const cards = Array.from(document.querySelectorAll('[data-role="slide-card"]'));
      const filters = Array.from(document.querySelectorAll('[data-role="filter"]'));
      const searchBox = document.querySelector('[data-role="search"]');
      const issuesOnly = document.querySelector('[data-role="issues-only"]');
      const nextIssueBtn = document.querySelector('[data-role="jump-next-issue"]');
      const dialog = document.getElementById('preview-dialog');
      const dialogImage = document.getElementById('dialog-image');
      const dialogTitle = document.getElementById('dialog-title');
      const dialogOpen = document.getElementById('dialog-open');
      const dialogClose = document.getElementById('dialog-close');
      const actionableIssueCards = cards.filter(card => Boolean((card.getAttribute('data-issues') || '').trim()));
      let activeFilter = 'all';

      function applyFilters() {{
        const query = (searchBox?.value || '').toLowerCase().trim();
        const issues = Boolean(issuesOnly?.checked);
        for (const card of cards) {{
          const haystack = card.textContent.toLowerCase();
          const fidelity = card.getAttribute('data-fidelity') || '';
          const cardIssues = (card.getAttribute('data-issues') || '').trim();
          const matchesFilter = activeFilter === 'all' || fidelity === activeFilter;
          const matchesQuery = !query || haystack.includes(query);
          const matchesIssues = !issues || Boolean(cardIssues);
          card.hidden = !(matchesFilter && matchesQuery && matchesIssues);
        }}
      }}

      for (const button of filters) {{
        button.addEventListener('click', () => {{
          activeFilter = button.getAttribute('data-filter') || 'all';
          for (const peer of filters) peer.classList.toggle('active', peer === button);
          applyFilters();
        }});
      }}
      searchBox?.addEventListener('input', applyFilters);
      if (issuesOnly && actionableIssueCards.length === 0) {{
        issuesOnly.checked = false;
      }}
      issuesOnly?.addEventListener('change', applyFilters);
      nextIssueBtn?.addEventListener('click', () => {{
        if (actionableIssueCards.length === 0) return;
        const next = cards.find(card => !card.hidden && (card.getAttribute('data-issues') || '').trim());
        if (next) next.scrollIntoView({{behavior: 'smooth', block: 'center'}});
      }});

      for (const link of document.querySelectorAll('[data-role="preview-link"]')) {{
        link.addEventListener('click', (event) => {{
          const href = link.getAttribute('data-preview-src');
          if (!href || !dialog || typeof dialog.showModal !== 'function') return;
          event.preventDefault();
          dialogImage.src = href;
          dialogImage.alt = link.getAttribute('data-row-id') || 'Preview';
          dialogTitle.textContent = link.closest('[data-role="slide-card"]')?.getAttribute('data-slide-id') || 'Preview';
          dialogOpen.href = href;
          dialog.showModal();
        }});
      }}
      dialogClose?.addEventListener('click', () => dialog?.close());
      dialog?.addEventListener('click', (event) => {{
        const rect = dialog.getBoundingClientRect();
        const inBounds = rect.top <= event.clientY && event.clientY <= rect.top + rect.height &&
          rect.left <= event.clientX && event.clientX <= rect.left + rect.width;
        if (!inBounds) dialog.close();
      }});

      if (window.location.hash) {{
        const target = document.getElementById(window.location.hash.slice(1));
        if (target) target.scrollIntoView();
      }}
      applyFilters();
    }})();
  </script>
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
    html_path.write_text(render_index_html_v2(manifest), encoding="utf-8")


def cmd_generate(args: argparse.Namespace) -> int:
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

    run_id: str | None = getattr(args, "run_id", None)

    manifest = build_manifest(
        payload,
        payload_path=payload_path,
        storyboard_dir=storyboard_dir,
        asset_base=asset_base.resolve(),
        narration_by_slide_id=narration_map,
        segment_manifest_path=segment_manifest_path,
        related_assets=related_assets,
        run_id=run_id,
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
        type=str,
        default=None,
        help="Production run ID for traceability in manifest metadata and logs.",
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
