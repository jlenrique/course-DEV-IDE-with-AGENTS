"""Tests for doc_refresh.py."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "doc_refresh.py"
SPEC = importlib.util.spec_from_file_location("doc_refresh", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def sample_doc_sources() -> dict:
    return {
        "tool": "gamma",
        "agent": "bmad-agent-gamma",
        "doc_sources": [
            {"name": "Gamma API", "url": "https://developers.gamma.app", "type": "developer-docs"}
        ],
        "last_refreshed": None,
        "refresh_notes": None,
    }


class TestDocSourcesIO:
    def test_load_and_save_doc_sources(self, tmp_path: Path) -> None:
        path = tmp_path / "doc-sources.yaml"
        MODULE.save_doc_sources(sample_doc_sources(), path)
        loaded = MODULE.load_doc_sources(path)
        assert loaded["tool"] == "gamma"


class TestRefreshMetadata:
    def test_update_refresh_metadata(self, tmp_path: Path) -> None:
        path = tmp_path / "doc-sources.yaml"
        MODULE.save_doc_sources(sample_doc_sources(), path)
        updated = MODULE.update_refresh_metadata(path, refresh_notes="Checked changelog")
        assert updated["refresh_notes"] == "Checked changelog"
        assert updated["last_refreshed"] is not None


class TestReportGeneration:
    def test_build_refresh_report(self) -> None:
        report = MODULE.build_refresh_report(
            sample_doc_sources(),
            findings=[{"change": "new endpoint", "url": "https://example.com"}],
            refreshed_at="2026-03-27T00:00:00+00:00",
        )
        assert report["tool"] == "gamma"
        assert report["summary"]["total_findings"] == 1

    def test_write_report(self, tmp_path: Path) -> None:
        output = tmp_path / "report.json"
        MODULE.write_report({"tool": "gamma"}, output)
        assert json.loads(output.read_text(encoding="utf-8"))["tool"] == "gamma"


class TestSidecarAppend:
    def test_append_sidecar_discovery(self, tmp_path: Path) -> None:
        path = tmp_path / "patterns.md"
        MODULE.append_sidecar_discovery(path, tool="gamma", note="Reviewed llms.txt")
        content = path.read_text(encoding="utf-8")
        assert "gamma" in content
        assert "Reviewed llms.txt" in content
