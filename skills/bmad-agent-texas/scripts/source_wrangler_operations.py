"""Source bundle construction: URLs, local files, Notion, Box, Playwright HTML, PDF, DOCX."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from docx import Document as _DocxDocument
from docx.oxml.ns import qn as _docx_qn
from docx.table import Table as _DocxTable
from docx.text.paragraph import Paragraph as _DocxParagraph

from scripts.api_clients.notion_client import NotionClient


class GammaDocsURLNotSupportedError(ValueError):
    """Hosted Gamma doc URLs cannot be fetched via HTTP.

    Use Gary / Gamma API or Playwright capture instead.
    """


def is_gamma_app_docs_url(url: str) -> bool:
    """True for gamma.app viewer URLs (Cloudflare / JS); never use plain GET for these."""
    parsed = urlparse(url.strip())
    host = (parsed.netloc or "").lower()
    if ":" in host:
        host = host.split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    path_lower = (parsed.path or "").lower()
    return host == "gamma.app" and "/docs/" in path_lower


def _reject_gamma_docs_url(url: str) -> None:
    if is_gamma_app_docs_url(url):
        raise GammaDocsURLNotSupportedError(
            "gamma.app/docs URLs are not supported for HTTP fetch (Cloudflare). "
            "Use Gary + gamma-api-mastery / Gamma MCP to export the deck, then "
            "wrangle_local_pdf() on the export; or save HTML via Playwright and "
            "wrangle_playwright_saved_html()."
        )


def verify_local_source_paths(paths: Sequence[str | Path]) -> list[Path]:
    """Return paths that are missing or not files (preflight before bundles)."""
    missing: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if not p.is_file():
            missing.append(p)
    return missing


def require_local_source_files(paths: Sequence[str | Path]) -> None:
    """Raise FileNotFoundError if any expected local source file is absent."""
    missing = verify_local_source_paths(paths)
    if missing:
        joined = ", ".join(str(p) for p in missing)
        raise FileNotFoundError(
            f"Expected source file(s) missing for bundle / preflight: {joined}"
        )


def extract_pdf_text(
    path: str | Path,
    *,
    max_pages: int | None = 120,
    max_chars: int | None = 600_000,
) -> tuple[str, dict[str, Any]]:
    """Extract text from a text-based PDF using pypdf.

    Args:
        path: Path to the PDF.
        max_pages: Cap pages read (None = all).
        max_chars: Cap total extracted characters (None = unlimited).

    Returns:
        (text, meta) where meta includes pages_total, pages_extracted, truncated, engine.
    """
    from pypdf import PdfReader

    p = Path(path)
    reader = PdfReader(str(p))
    total = len(reader.pages)
    limit = total if max_pages is None else min(total, max_pages)

    parts: list[str] = []
    used_chars = 0
    truncated = False
    for i in range(limit):
        chunk = (reader.pages[i].extract_text() or "").strip()
        if not chunk:
            continue
        if max_chars is not None:
            remaining = max_chars - used_chars
            if remaining <= 0:
                truncated = True
                break
            if len(chunk) > remaining:
                chunk = chunk[:remaining]
                truncated = True
            used_chars += len(chunk)
        parts.append(f"### Page {i + 1}\n\n{chunk}")
        if truncated:
            break

    text = "\n\n".join(parts).strip()
    meta: dict[str, Any] = {
        "engine": "pypdf",
        "pages_total": total,
        "pages_scanned": limit,
        "truncated": truncated,
    }
    return text, meta


class _StripHTMLParser(HTMLParser):
    """Extract visible text; skip script/style/nav/footer."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        elif tag in {"br", "p", "div", "li", "tr", "h1", "h2", "h3"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag in {"p", "div", "li", "h1", "h2", "h3"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._chunks.append(data)

    def text(self) -> str:
        raw = "".join(self._chunks)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return re.sub(r"[ \t]+", " ", raw).strip()


def html_to_text(html: str) -> str:
    """Convert HTML string to plain text (best-effort)."""
    parser = _StripHTMLParser()
    parser.feed(html)
    parser.close()
    return parser.text()


def read_text_file(path: str | Path, encoding: str = "utf-8") -> str:
    """Read .md, .txt, or decode as utf-8 with replacement."""
    p = Path(path)
    return p.read_text(encoding=encoding, errors="replace")


def read_html_file(path: str | Path) -> tuple[str, str]:
    """Return (raw_html, extracted_text)."""
    raw = read_text_file(path)
    return raw, html_to_text(raw)


def fetch_url(
    url: str,
    timeout: int = 30,
    max_bytes: int = 5_000_000,
) -> tuple[str, str, str]:
    """GET url; return (content_type, raw_text, extracted_text).

    For HTML, extracted_text is html_to_text; for other types, raw in both.
    """
    _reject_gamma_docs_url(url)
    headers = {
        "User-Agent": "course-DEV-IDE-with-AGENTS-source-wrangler/1.0",
        "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8",
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    raw_bytes = resp.content[:max_bytes]
    ctype = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()
    charset = resp.encoding or "utf-8"
    raw_text = raw_bytes.decode(charset, errors="replace")
    if "html" in ctype:
        return ctype, raw_text, html_to_text(raw_text)
    return ctype, raw_text, raw_text.strip()


def list_box_files(
    box_root: str | Path,
    glob_pattern: str = "**/*",
    max_files: int = 50,
    extensions: frozenset[str] | None = None,
) -> list[Path]:
    """List files under BOX_DRIVE_PATH (bounded)."""
    root = Path(box_root)
    if not root.is_dir():
        raise FileNotFoundError(f"BOX_DRIVE_PATH is not a directory: {root}")
    exts = extensions or frozenset(
        {".md", ".txt", ".pdf", ".docx", ".html", ".htm"}
    )
    out: list[Path] = []
    for p in root.glob(glob_pattern):
        if len(out) >= max_files:
            break
        if p.is_file() and p.suffix.lower() in exts:
            out.append(p)
    return sorted(out)


@dataclass
class SourceRecord:
    """One provenance entry."""

    kind: str
    ref: str
    note: str = ""
    fetched_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "ref": self.ref,
            "note": self.note,
            "fetched_at": self.fetched_at,
        }


def wrangle_local_pdf(
    path: str | Path,
    *,
    max_pages: int | None = 120,
    max_chars: int | None = 600_000,
) -> tuple[str, str, SourceRecord]:
    """Read a local PDF; return (title_guess, extracted_text, provenance)."""
    p = Path(path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"PDF not found: {p}")
    if p.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {p}")

    body, meta = extract_pdf_text(p, max_pages=max_pages, max_chars=max_chars)
    title = p.stem.replace("_", " ")
    note = (
        f"pypdf scanned={meta['pages_scanned']}/{meta['pages_total']}"
        f"{' truncated' if meta.get('truncated') else ''}"
    )
    rec = SourceRecord(kind="local_pdf", ref=str(p), note=note)
    return title, body, rec


# ---------------------------------------------------------------------------
# Story 27-1: DOCX provider wiring
#
# Mirrors wrangle_local_pdf signature. Uses body-order iteration over
# doc.element.body so tables and paragraphs interleave correctly in output
# (Murat's AC-T.1 iteration-order guard). Heading 1..6 styles render as
# markdown `#`..`######`. Tables render as pipe-separated rows. Known losses
# per transform-registry.md: style/formatting beyond headings, cell-merge /
# vertical-align on tables, inline images, footnotes, comments, tracked
# changes. Malformed DOCX raises python-docx's PackageNotFoundError which
# run_wrangler._wrangle_source() catches and maps to FAILED SourceOutcome
# with error_kind="docx_extraction_failed" (AC-B.3 / AC-T.2b).
# ---------------------------------------------------------------------------


_HEADING_STYLE_RE = re.compile(r"^Heading (\d+)$")


def extract_docx_text(
    path: str | Path,
    *,
    max_chars: int | None = 600_000,
) -> tuple[str, dict[str, Any]]:
    """Extract markdown body + structural counts from a DOCX via python-docx.

    Returns (body, meta). meta keys: paragraphs, headings, tables, truncated.

    Body-order iteration walks doc.element.body so tables appear inline at
    their document position instead of clustered. Each rendered block
    (heading / paragraph / table) is separated by a blank line so the
    output matches markdown paragraph convention (which extraction_validator
    _assess_structural_fidelity relies on via `\\n\\n` detection).
    Heading-styled paragraphs (style name "Heading 1".."Heading 6") render
    as markdown `#`..`######`. Tables render as `| cell | cell |` rows,
    one line per row. Character budget (`max_chars`) truncates at item
    boundaries; the trailing `[...truncated]` marker is appended when the
    cap fires.

    Raises docx.opc.exceptions.PackageNotFoundError on malformed-ZIP / non-DOCX
    input — caller is responsible for catching + FAILED-outcome synthesis
    (run_wrangler._wrangle_source handles this).
    """
    doc = _DocxDocument(str(path))
    blocks: list[str] = []  # Each element is a rendered block; joined with "\n\n".
    counts = {"paragraphs": 0, "headings": 0, "tables": 0}
    truncated = False
    running_chars = 0
    # Note: doc.element.body + python-docx qname constants are community-
    # canonical workarounds for python-docx's split paragraphs/tables
    # surfaces (the library's public API exposes these as two flat
    # collections, which would lose body-order). Validated against
    # python-docx 1.1-1.2; the `<2` upper pin in pyproject guards against
    # an unannounced 2.x rename of these internals.
    p_tag = _docx_qn("w:p")
    tbl_tag = _docx_qn("w:tbl")

    def _append_block(block: str) -> bool:
        """Append block respecting max_chars; return False when truncated."""
        nonlocal running_chars
        add_len = len(block) + 2  # account for "\n\n" separator
        if max_chars is not None and running_chars + add_len > max_chars:
            return False
        blocks.append(block)
        running_chars += add_len
        return True

    for child in doc.element.body.iterchildren():
        tag = child.tag
        if tag == p_tag:
            para = _DocxParagraph(child, doc)
            text = (para.text or "").rstrip()
            style_name = para.style.name if para.style is not None else ""
            m = _HEADING_STYLE_RE.match(style_name or "")
            # Counter semantics (code-review Blind+Auditor, 2026-04-17): count
            # only content that is actually rendered to the body, so rec.note
            # counts match what a reader of extracted.md sees — not the raw
            # python-docx element count (which inflates on layout-spacer
            # empty paragraphs and would-be-empty headings).
            if m:
                if not text:
                    continue  # empty heading — skip, do not count
                level = min(int(m.group(1)), 6)
                rendered = f"{'#' * level} {text}".rstrip()
                counts["headings"] += 1
                counts["paragraphs"] += 1
                if not _append_block(rendered):
                    truncated = True
                    break
            else:
                if not text:
                    continue  # empty paragraph (layout spacer) — skip, do not count
                counts["paragraphs"] += 1
                if not _append_block(text):
                    truncated = True
                    break
        elif tag == tbl_tag:
            table = _DocxTable(child, doc)
            counts["tables"] += 1
            table_rows: list[str] = []
            for row in table.rows:
                # De-duplicate consecutive _tc references per row: python-docx's
                # row.cells returns the SAME _Cell object for each logical grid
                # position a horizontally-merged cell spans, producing duplicate
                # text in pipe-rows (code-review Blind+Edge Hunter, 2026-04-17).
                # Track the underlying <w:tc> element identity to render each
                # physical cell exactly once.
                unique_cells: list[str] = []
                seen_tc_ids: set[int] = set()
                for cell in row.cells:
                    tc_id = id(cell._tc)
                    if tc_id in seen_tc_ids:
                        continue
                    seen_tc_ids.add(tc_id)
                    unique_cells.append(cell.text.replace("\n", " ").strip())
                table_rows.append("| " + " | ".join(unique_cells) + " |")
            rendered = "\n".join(table_rows)
            if not _append_block(rendered):
                truncated = True
                break

    body = "\n\n".join(blocks).strip()
    if body:
        body = body + "\n"
    if truncated:
        body = (body + "[...truncated]\n") if body else "[...truncated]\n"

    meta: dict[str, Any] = {**counts, "truncated": truncated}
    return body, meta


def wrangle_local_docx(
    path: str | Path,
    *,
    max_chars: int | None = 600_000,
) -> tuple[str, str, SourceRecord]:
    """Read a local DOCX; return (title_guess, extracted_text, provenance).

    Signature + return shape mirror wrangle_local_pdf. Title derives from
    Path(path).stem with underscores → spaces (Winston's PDF-parity note).
    `rec.kind == "local_docx"` (distinct from "local_file" for .md/.txt
    text reads). `rec.note` reports paragraph/heading/table counts.

    Raises FileNotFoundError if path is missing; ValueError on wrong suffix;
    python-docx PackageNotFoundError on malformed-ZIP / invalid-DOCX input
    (surfaces the library exception for adapter-layer classification —
    AC-B.3 / AC-T.2a).
    """
    p = Path(path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"DOCX not found: {p}")
    if p.suffix.lower() != ".docx":
        raise ValueError(f"Expected a .docx file, got: {p}")

    body, meta = extract_docx_text(p, max_chars=max_chars)
    title = p.stem.replace("_", " ")
    note_parts = [
        f"python-docx paragraphs={meta['paragraphs']}",
        f"headings={meta['headings']}",
        f"tables={meta['tables']}",
    ]
    if meta.get("truncated"):
        note_parts.append("truncated")
    note = " ".join(note_parts)
    rec = SourceRecord(kind="local_docx", ref=str(p), note=note)
    return title, body, rec


def build_extracted_markdown(
    title: str,
    sections: list[tuple[str, str]],
) -> str:
    """sections: (heading, body_markdown_or_text)."""
    lines = [f"# Source bundle: {title}", ""]
    for head, body in sections:
        lines.append(f"## {head}")
        lines.append("")
        lines.append(body.strip())
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def write_source_bundle(
    output_dir: str | Path,
    title: str,
    extracted_md: str,
    provenance: list[SourceRecord],
    raw_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Write bundle to disk; return summary paths.

    raw_files: optional basename -> content to place under raw/
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw_dir = out / "raw"
    if raw_files:
        raw_dir.mkdir(parents=True, exist_ok=True)
        for name, content in raw_files.items():
            safe = Path(name).name
            (raw_dir / safe).write_text(content, encoding="utf-8")

    (out / "extracted.md").write_text(extracted_md, encoding="utf-8")
    meta = {
        "title": title,
        "generated_at": datetime.now(UTC).isoformat(),
        "provenance": [p.to_dict() for p in provenance],
        "primary_consumption_path": str(out / "extracted.md"),
    }
    (out / "metadata.json").write_text(
        json.dumps(meta, indent=2),
        encoding="utf-8",
    )
    return {
        "bundle_dir": str(out.resolve()),
        "extracted_md": str((out / "extracted.md").resolve()),
        "metadata_json": str((out / "metadata.json").resolve()),
    }


def wrangle_notion_page(
    page_id: str,
    client: NotionClient | None = None,
) -> tuple[str, str, str]:
    """Return (title, markdown_body, page_id) from Notion."""
    c = client or NotionClient()
    title, body = c.page_to_markdown(page_id)
    return title, body, page_id.strip()


def wrangle_playwright_saved_html(
    html_path: str | Path,
    source_url: str | None = None,
) -> tuple[str, str, SourceRecord]:
    """Process HTML saved by Playwright MCP (or any save-as)."""
    raw, text = read_html_file(html_path)
    path = Path(html_path)
    ref = source_url or str(path.resolve())
    note = f"HTML capture file: {path.name}"
    rec = SourceRecord(kind="playwright_html", ref=ref, note=note)
    title = path.stem.replace("_", " ")
    return title, text, rec


def summarize_url_for_envelope(url: str) -> tuple[str, str, SourceRecord]:
    """Fetch URL and return title guess, extracted text, provenance."""
    parsed = urlparse(url)
    title = (parsed.netloc + parsed.path).strip("/") or url
    ctype, _raw, extracted = fetch_url(url)
    rec = SourceRecord(kind="url", ref=url, note=f"Content-Type: {ctype}")
    return title, extracted, rec
