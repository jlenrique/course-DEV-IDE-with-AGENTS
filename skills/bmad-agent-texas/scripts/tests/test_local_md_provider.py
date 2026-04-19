"""Tests for the md provider wiring and Notion-Markdown normalization.

Covers the 2026-04-19 trial defect where Notion-exported .md files fell
through the `local_file` branch to raw `read_text_file` and produced
extracted.md full of backslash escapes and HTML entities.

Test names use the tokens `md_provider`, `local_md`, and `notion_md` so
the operator selector ``pytest -k "md_provider or local_md or notion_md"``
picks them up.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_MODULE_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = _MODULE_DIR.parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _load_source_wrangler_operations():
    spec = importlib.util.spec_from_file_location(
        "source_wrangler_operations_under_test",
        _MODULE_DIR / "source_wrangler_operations.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["source_wrangler_operations_under_test"] = module
    spec.loader.exec_module(module)
    return module


def _load_normalizer():
    spec = importlib.util.spec_from_file_location(
        "normalize_notion_md_under_test",
        _MODULE_DIR / "source_ops" / "normalize_notion_md.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["normalize_notion_md_under_test"] = module
    spec.loader.exec_module(module)
    return module


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "texas_run_wrangler_md_test", _MODULE_DIR / "run_wrangler.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["texas_run_wrangler_md_test"] = module
    spec.loader.exec_module(module)
    return module


sw = _load_source_wrangler_operations()
normalizer = _load_normalizer()
runner = _load_runner()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


NOTION_EXPORT_SAMPLE = (
    r"\# Module 1: Innovative Leadership"
    "\n\n\n"
    r"\## Learning Objectives"
    "\n\n"
    r"1\. Identify the four domains of innovation"
    "\n"
    r"2\. Analyze the M\&M of Innovation framework"
    "\n\n\n\n"
    r"\- \*\*Focus\*\* on the infographic\.  "
    "\n"
    r"\- Exclude appendix\."
    "\n\n"
    "&#x20;&#x20;&#x20;&#x20;Indented detail."
    "\n\n\n\n"
    r"Plain sentence with an escaped period at the end\."
    "\n"
)


CLEAN_EXPECTED_MARKERS = [
    "# Module 1: Innovative Leadership",
    "## Learning Objectives",
    "1. Identify the four domains of innovation",
    "2. Analyze the M&M of Innovation framework",
    "- **Focus** on the infographic.",
    "- Exclude appendix.",
    "Plain sentence with an escaped period at the end.",
]


@pytest.fixture
def notion_md_fixture(tmp_path: Path) -> Path:
    path = tmp_path / "c1m1-tejal-notion-export.md"
    path.write_text(NOTION_EXPORT_SAMPLE, encoding="utf-8")
    return path


def _write_directive(tmp_path: Path, body: dict) -> Path:
    path = tmp_path / "directive.yaml"
    path.write_text(yaml.safe_dump(body, sort_keys=False), encoding="utf-8")
    return path


def _assert_all_six_artifacts(bundle_dir: Path) -> dict[str, Path]:
    expected = {
        "extracted.md": bundle_dir / "extracted.md",
        "metadata.json": bundle_dir / "metadata.json",
        "manifest.json": bundle_dir / "manifest.json",
        "extraction-report.yaml": bundle_dir / "extraction-report.yaml",
        "ingestion-evidence.md": bundle_dir / "ingestion-evidence.md",
        "result.yaml": bundle_dir / "result.yaml",
    }
    for name, path in expected.items():
        assert path.is_file(), f"Missing artifact: {name}"
        assert path.stat().st_size > 0, f"Empty artifact: {name}"
    return expected


# ---------------------------------------------------------------------------
# normalize_notion_md — unit tests
# ---------------------------------------------------------------------------


def test_notion_md_normalize_strips_backslash_escapes() -> None:
    cleaned = normalizer.normalize_notion_markdown(r"\# Heading \*\*bold\*\* \-list")
    assert cleaned == "# Heading **bold** -list"


def test_notion_md_normalize_decodes_html_entities() -> None:
    cleaned = normalizer.normalize_notion_markdown(
        "&#x20;&#x20;indented &amp; escaped &lt;tag&gt;"
    )
    assert cleaned == "  indented & escaped <tag>"


def test_notion_md_normalize_collapses_excessive_blank_lines() -> None:
    cleaned = normalizer.normalize_notion_markdown("line one\n\n\n\n\nline two\n")
    assert cleaned == "line one\n\nline two\n"


def test_notion_md_normalize_is_idempotent() -> None:
    once = normalizer.normalize_notion_markdown(NOTION_EXPORT_SAMPLE)
    twice = normalizer.normalize_notion_markdown(once)
    assert once == twice


def test_notion_md_normalize_empty_input() -> None:
    assert normalizer.normalize_notion_markdown("") == ""


def test_notion_md_normalize_preserves_clean_markdown() -> None:
    clean = "# Already clean\n\nParagraph **bold**.\n"
    assert normalizer.normalize_notion_markdown(clean) == clean


def test_notion_md_normalize_full_sample_contains_expected_markers() -> None:
    cleaned = normalizer.normalize_notion_markdown(NOTION_EXPORT_SAMPLE)
    for marker in CLEAN_EXPECTED_MARKERS:
        assert marker in cleaned, f"Missing expected marker: {marker!r}"
    # No residual backslash escapes before markdown specials.
    assert "\\#" not in cleaned
    assert "\\*" not in cleaned
    assert "\\-" not in cleaned
    assert "\\." not in cleaned
    assert "&#x20;" not in cleaned
    assert "&amp;" not in cleaned


# ---------------------------------------------------------------------------
# wrangle_local_md — unit tests
# ---------------------------------------------------------------------------


def test_wrangle_local_md_returns_local_md_kind(notion_md_fixture: Path) -> None:
    title, body, rec = sw.wrangle_local_md(notion_md_fixture)
    assert rec.kind == "local_md"
    assert rec.ref == str(notion_md_fixture.resolve())
    assert "markdown normalize" in rec.note
    assert title == "c1m1-tejal-notion-export"


def test_wrangle_local_md_normalizes_notion_export(notion_md_fixture: Path) -> None:
    _title, body, _rec = sw.wrangle_local_md(notion_md_fixture)
    for marker in CLEAN_EXPECTED_MARKERS:
        assert marker in body, f"Missing expected marker after normalize: {marker!r}"
    assert "\\#" not in body
    assert "&#x20;" not in body


def test_wrangle_local_md_rejects_wrong_suffix(tmp_path: Path) -> None:
    bad = tmp_path / "not-markdown.txt"
    bad.write_text("plain text", encoding="utf-8")
    with pytest.raises(ValueError):
        sw.wrangle_local_md(bad)


def test_wrangle_local_md_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        sw.wrangle_local_md(tmp_path / "does-not-exist.md")


# ---------------------------------------------------------------------------
# run_wrangler integration — md provider end-to-end
# ---------------------------------------------------------------------------


# A Notion-export sample with enough real content (~250 words) to clear the
# validator's word-count floor without triggering the stub tripwire.
NOTION_EXPORT_FULL = (
    r"\# C1M1: Healthcare Innovation Leadership"
    "\n\n\n"
    r"\## Part 1 \- Framing Innovation"
    "\n\n"
    + "\n\n".join(
        [
            rf"Paragraph {i}\. Distinct narrative content about clinical "
            r"innovation across the organization\. Leaders must identify "
            r"opportunities where patient outcomes improve and operational "
            r"efficiency increases\. Framework elements include M\&M review "
            r"of Innovation, rapid cycle iteration, stakeholder alignment, "
            r"and post\-implementation evaluation\."
            for i in range(1, 11)
        ]
    )
    + "\n\n"
    r"\## Learning Objectives"
    "\n\n"
    r"1\. Identify four innovation domains in healthcare leadership"
    "\n"
    r"2\. Apply the M\&M of Innovation framework to case scenarios"
    "\n"
    r"3\. Evaluate implementation success using outcome metrics"
    "\n"
)


def test_md_provider_integration_scenario(tmp_path: Path) -> None:
    """Directive with ``provider: md`` runs end-to-end and yields a clean
    extracted.md with no Notion escape artefacts."""
    md_path = tmp_path / "notion-lesson.md"
    md_path.write_text(NOTION_EXPORT_FULL, encoding="utf-8")

    bundle = tmp_path / "bundle"
    directive = _write_directive(
        tmp_path,
        {
            "run_id": "TEST-MD-INT-001",
            "sources": [
                {
                    "ref_id": "md-primary",
                    "provider": "md",
                    "locator": str(md_path),
                    "role": "primary",
                    "description": "Notion-exported Markdown primary source",
                    "expected_min_words": 150,
                }
            ],
        },
    )

    exit_code = runner.main(
        ["--directive", str(directive), "--bundle-dir", str(bundle)]
    )
    assert exit_code == runner.EXIT_COMPLETE

    artifacts = _assert_all_six_artifacts(bundle)

    extracted = artifacts["extracted.md"].read_text(encoding="utf-8")
    # Clean headings (no leading backslash)
    assert "# C1M1: Healthcare Innovation Leadership" in extracted
    assert "## Part 1 - Framing Innovation" in extracted
    assert "## Learning Objectives" in extracted
    # No residual escapes that would have leaked through the raw text read path
    assert "\\#" not in extracted
    assert "\\*" not in extracted
    assert r"M\&M" not in extracted
    assert "M&M" in extracted
    assert "&#x20;" not in extracted

    metadata = json.loads(artifacts["metadata.json"].read_text(encoding="utf-8"))
    provenance = metadata["provenance"]
    assert len(provenance) == 1
    assert provenance[0]["kind"] == "md"  # dispatch-level provider
    assert provenance[0]["extractor_used"] == "markdown_unescape"
    assert provenance[0]["ref"] == str(md_path)


def test_local_md_suffix_routes_through_normalizer(tmp_path: Path) -> None:
    """Regression guard: a directive with ``provider: local_file`` and a
    ``.md`` locator must route through :func:`wrangle_local_md`, not the
    raw ``read_text_file`` fall-through. This catches the exact defect the
    2026-04-19 trial surfaced: Notion export hit the fall-through and
    preserved every backslash escape."""
    md_path = tmp_path / "notion-lesson.md"
    md_path.write_text(NOTION_EXPORT_FULL, encoding="utf-8")

    bundle = tmp_path / "bundle"
    directive = _write_directive(
        tmp_path,
        {
            "run_id": "TEST-MD-FALLBACK-001",
            "sources": [
                {
                    "ref_id": "md-via-local-file",
                    "provider": "local_file",
                    "locator": str(md_path),
                    "role": "primary",
                    "description": "Markdown source routed via local_file",
                    "expected_min_words": 150,
                }
            ],
        },
    )

    exit_code = runner.main(
        ["--directive", str(directive), "--bundle-dir", str(bundle)]
    )
    assert exit_code == runner.EXIT_COMPLETE

    artifacts = _assert_all_six_artifacts(bundle)
    extracted = artifacts["extracted.md"].read_text(encoding="utf-8")
    assert "\\#" not in extracted
    assert "\\&" not in extracted
    assert "M&M" in extracted

    metadata = json.loads(artifacts["metadata.json"].read_text(encoding="utf-8"))
    provenance = metadata["provenance"]
    # Dispatch-level provider is still local_file (directive-preserved) but
    # the extractor label must surface the normalization path so operators
    # can tell which read strategy actually ran.
    assert provenance[0]["kind"] == "local_file"
    assert provenance[0]["extractor_used"] == "markdown_unescape"


# ---------------------------------------------------------------------------
# normalize_notion_md — CLI tests
# ---------------------------------------------------------------------------


def _cli_entry_path() -> Path:
    return _MODULE_DIR / "source_ops" / "normalize_notion_md.py"


def test_notion_md_cli_stdout(tmp_path: Path) -> None:
    src = tmp_path / "in.md"
    src.write_text(r"\# Hello \*world\*", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(_cli_entry_path()), str(src)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout == "# Hello *world*"


def test_notion_md_cli_output_flag(tmp_path: Path) -> None:
    src = tmp_path / "in.md"
    src.write_text(r"\# Hello &amp; world", encoding="utf-8")
    out = tmp_path / "out.md"
    result = subprocess.run(
        [sys.executable, str(_cli_entry_path()), str(src), "--output", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert out.read_text(encoding="utf-8") == "# Hello & world"


def test_notion_md_cli_in_place(tmp_path: Path) -> None:
    src = tmp_path / "notion.md"
    src.write_text(r"\- one\. \- two\.", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(_cli_entry_path()), str(src), "--in-place"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert src.read_text(encoding="utf-8") == "- one. - two."


def test_notion_md_cli_missing_file_exits_nonzero(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(_cli_entry_path()), str(tmp_path / "nope.md")],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "error" in result.stderr.lower()
