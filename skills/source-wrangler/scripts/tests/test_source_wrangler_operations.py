"""Unit tests for source_wrangler_operations."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pypdf import PdfWriter

_MODULE_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = _MODULE_DIR.parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_SPEC = importlib.util.spec_from_file_location(
    "source_wrangler_operations",
    _MODULE_DIR / "source_wrangler_operations.py",
)
assert _SPEC and _SPEC.loader
sw = importlib.util.module_from_spec(_SPEC)
sys.modules["source_wrangler_operations"] = sw
_SPEC.loader.exec_module(sw)


def test_html_to_text_strips_tags() -> None:
    html = "<html><body><p>Hello <b>world</b></p><script>x</script></body></html>"
    assert "Hello" in sw.html_to_text(html)
    assert "world" in sw.html_to_text(html)
    assert "x" not in sw.html_to_text(html)


def test_build_extracted_markdown() -> None:
    md = sw.build_extracted_markdown(
        "Trial",
        [("Section A", "body a"), ("Section B", "body b")],
    )
    assert "# Source bundle: Trial" in md
    assert "## Section A" in md
    assert "body a" in md


def test_write_source_bundle(tmp_path: Path) -> None:
    prov = [
        sw.SourceRecord(kind="url", ref="https://example.com", note="test"),
    ]
    summary = sw.write_source_bundle(
        tmp_path / "b1",
        "My bundle",
        "# extracted\n",
        prov,
        raw_files={"sample.html": "<p>x</p>"},
    )
    assert Path(summary["extracted_md"]).exists()
    meta = json.loads((tmp_path / "b1" / "metadata.json").read_text())
    assert meta["title"] == "My bundle"
    assert (tmp_path / "b1" / "raw" / "sample.html").exists()


def test_wrangle_playwright_saved_html(tmp_path: Path) -> None:
    p = tmp_path / "capture.html"
    p.write_text("<html><body><h1>Title</h1><p>Para</p></body></html>", encoding="utf-8")
    title, text, rec = sw.wrangle_playwright_saved_html(p, source_url="https://gamma.app/x")
    assert rec.kind == "playwright_html"
    assert rec.ref == "https://gamma.app/x"
    assert "Para" in text


def test_is_gamma_app_docs_url() -> None:
    assert sw.is_gamma_app_docs_url("https://gamma.app/docs/abc?mode=doc")
    assert sw.is_gamma_app_docs_url("https://www.gamma.app/docs/x")
    assert not sw.is_gamma_app_docs_url("https://public-api.gamma.app/v1.0/themes")
    assert not sw.is_gamma_app_docs_url("https://example.com/")


def test_fetch_url_rejects_gamma_docs() -> None:
    with pytest.raises(sw.GammaDocsURLNotSupportedError):
        sw.fetch_url("https://gamma.app/docs/test-id")


@patch.object(sw.requests, "get")
def test_summarize_url_for_envelope(mock_get: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.content = b"<html><body><p>OK</p></body></html>"
    mock_resp.headers = {"Content-Type": "text/html; charset=utf-8"}
    mock_resp.encoding = "utf-8"
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp
    _title, text, rec = sw.summarize_url_for_envelope("https://example.org/doc")
    assert rec.kind == "url"
    assert "OK" in text


def test_list_box_files(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("x", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("y", encoding="utf-8")
    found = sw.list_box_files(tmp_path, max_files=20)
    assert len(found) == 2


def test_verify_and_require_local_sources(tmp_path: Path) -> None:
    existing = tmp_path / "a.txt"
    existing.write_text("ok", encoding="utf-8")
    missing = tmp_path / "gone.pdf"
    assert sw.verify_local_source_paths([existing]) == []
    assert sw.verify_local_source_paths([missing]) == [missing]
    sw.require_local_source_files([existing])
    with pytest.raises(FileNotFoundError, match="gone"):
        sw.require_local_source_files([missing])


def test_wrangle_local_pdf_blank_page(tmp_path: Path) -> None:
    pdf_path = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with pdf_path.open("wb") as f:
        writer.write(f)
    title, text, rec = sw.wrangle_local_pdf(pdf_path)
    assert title == "blank"
    assert rec.kind == "local_pdf"
    assert "pypdf" in rec.note
    assert isinstance(text, str)


def test_extract_pdf_text_sample_deck() -> None:
    sample = _REPO_ROOT / "course-content" / "staging" / "Diagnosis-Innovation.pdf"
    if not sample.is_file():
        pytest.skip("staging sample PDF not present")
    body, meta = sw.extract_pdf_text(sample, max_pages=2)
    assert meta["engine"] == "pypdf"
    assert meta["pages_total"] >= 1
    assert "Innovation" in body or "innovation" in body.lower()
