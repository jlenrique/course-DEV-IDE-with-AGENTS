"""Unit tests for source_wrangler_operations."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_MODULE_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = _MODULE_DIR.parents[2]
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
