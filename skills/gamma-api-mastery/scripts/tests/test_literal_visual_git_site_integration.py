"""Integration tests for the preintegration literal-visual Git-site publish feature.

These tests cover the NEW behavior AFTER `publish_preintegration_literal_visuals`
is implemented.  They are integration tests that:

  * Post a real dummy PNG to ``jlenrique/jlenrique.github.io`` under
    ``assets/gamma/test-integration/tmp/``
  * Confirm the resulting GitHub Pages URL returns HTTP 200

NO MOCKING.  All network, git, and HTTP operations run for real.

Requirements
------------
* ``GITHUB_PAGES_TOKEN`` — Fine-grained GitHub personal access token for
    ``jlenrique/jlenrique.github.io`` with repository ``Contents: Read and write``.
* Internet access (git push + GitHub Pages CDN poll).
* ``git`` CLI on PATH.
* The function ``publish_preintegration_literal_visuals`` must exist in
  ``gamma_operations.py`` — tests skip automatically until it is implemented.

Marks
-----
``live_api_e2e`` — these tests are excluded from normal ``pytest`` runs.
Pass ``--run-live-e2e`` to enable them (see ``tests/conftest.py``).
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest
import requests

# ---------------------------------------------------------------------------
# Path bootstrap (consistent with other gamma test files)
# ---------------------------------------------------------------------------

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
_SCRIPTS_DIR = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, _SCRIPTS_DIR)

# ---------------------------------------------------------------------------
# Feature-presence guard: skip entire file until function is implemented
# ---------------------------------------------------------------------------

try:
    import gamma_operations  # noqa: E402
    publish_preintegration_literal_visuals = gamma_operations.publish_preintegration_literal_visuals
    _FEATURE_IMPLEMENTED = True
except (ImportError, AttributeError):
    gamma_operations = None  # type: ignore[assignment]
    publish_preintegration_literal_visuals = None  # type: ignore[assignment]
    _FEATURE_IMPLEMENTED = False

# ---------------------------------------------------------------------------
# Credential guard
# ---------------------------------------------------------------------------

_GITHUB_PAGES_TOKEN = (
    os.environ.get("GITHUB_PAGES_TOKEN", "")
    or os.environ.get("GH_PAGES_TOKEN", "")
)
_HAS_CREDS = bool(_GITHUB_PAGES_TOKEN)

requires_feature = pytest.mark.skipif(
    not _FEATURE_IMPLEMENTED,
    reason="publish_preintegration_literal_visuals not yet implemented in gamma_operations.py",
)
requires_token = pytest.mark.skipif(
    not _HAS_CREDS,
    reason="GITHUB_PAGES_TOKEN not set",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SITE_REPO_URL = "https://github.com/jlenrique/jlenrique.github.io"
_SITE_SUBDOMAIN = "https://jlenrique.github.io"
_TEST_MODULE_LESSON_PART = "test-integration/tmp"
_TEST_DUMMY_FILENAME = "integration_test_dummy.png"

# Tiny 1×1 red pixel PNG (exact bytes — no PIL required)
_DUMMY_PNG_BYTES = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR length + type
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  # bit-depth, color type
    0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT length + type
    0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,  # zlib compressed red pixel
    0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
    0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND
    0x44, 0xAE, 0x42, 0x60, 0x82,
])

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

def _expected_hosted_url() -> str:
    """Build the expected GitHub Pages URL for the test dummy image."""
    return (
        f"{_SITE_SUBDOMAIN}/assets/gamma/{_TEST_MODULE_LESSON_PART}/{_TEST_DUMMY_FILENAME}"
    )


def _poll_url_until_available(
    url: str,
    *,
    timeout_seconds: int = 180,
    poll_interval: int = 10,
) -> bool:
    """Poll a URL until it returns HTTP 200 or timeout is reached.

    Returns True if URL became available within the timeout, False otherwise.
    """
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            resp = requests.get(url, timeout=15, allow_redirects=True)
            if resp.status_code == 200:
                return True
        except requests.RequestException:
            pass
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(poll_interval, remaining))
    return False


# ------------------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------------------

@pytest.mark.live_api_e2e
@requires_feature
@requires_token
class TestPublishPreintegrationLiteralVisualsLive:
    """Live end-to-end tests: real git push → real GitHub Pages URL check."""

    def test_dummy_png_posted_and_url_accessible(self, tmp_path: Path) -> None:
        """Happy path: post a 1x1 dummy PNG to the site and confirm it is
        reachable at the GitHub Pages CDN URL within 3 minutes."""
        dummy_png_path = tmp_path / _TEST_DUMMY_FILENAME
        dummy_png_path.write_bytes(_DUMMY_PNG_BYTES)

        # card_number 1 maps to the dummy PNG
        preintegration_map = {1: dummy_png_path}

        result = publish_preintegration_literal_visuals(
            preintegration_map,
            _TEST_MODULE_LESSON_PART,
            site_repo_url=_SITE_REPO_URL,
            run_id="TEST-GIT-SITE-INTEGRATION-001",
            mode="default",
        )

        # Assert structural contract first (regardless of CDN propagation)
        assert result["preintegration_ready"] is True, (
            f"preintegration_ready should be True; got result: {result}"
        )
        assert result["pushed"] is True, (
            f"pushed should be True; got result: {result}"
        )
        assert result["copied_count"] == 1, (
            f"copied_count should be 1; got: {result['copied_count']}"
        )
        assert len(result.get("substituted_cards", [])) == 1

        # Confirm the URL that was returned is what we expect
        url_base = result.get("url_base", "")
        assert _TEST_MODULE_LESSON_PART in url_base, (
            f"url_base must reference the module_lesson_part path; got: {url_base}"
        )

        # Poll GitHub Pages CDN until the URL is live (up to 3 minutes)
        hosted_url = _expected_hosted_url()
        url_is_live = _poll_url_until_available(
            hosted_url,
            timeout_seconds=180,
            poll_interval=10,
        )

        # If the CDN hasn't propagated within 3 minutes, log a clear message
        # but still consider the test successful at the git-push level.
        # The separate assertion below requires CDN response.
        assert url_is_live, (
            f"GitHub Pages URL '{hosted_url}' did not return HTTP 200 within 180 seconds.\n"
            "GitHub Pages CDN propagation may be slow. Verify the file was pushed to the "
            f"repo at {_SITE_REPO_URL} under assets/gamma/{_TEST_MODULE_LESSON_PART}/."
        )

        # Final confirmation: the URL returns an image content type
        resp = requests.get(hosted_url, timeout=15)
        assert resp.status_code == 200
        assert "image" in resp.headers.get("content-type", "").lower(), (
            f"Expected image content-type from {hosted_url}; "
            f"got: {resp.headers.get('content-type')}"
        )

    def test_adhoc_mode_does_not_push(self, tmp_path: Path) -> None:
        """Ad-hoc mode must fail closed: no actual git push should occur,
        and pushed must be False in the result."""
        dummy_png_path = tmp_path / "adhoc_test_dummy.png"
        dummy_png_path.write_bytes(_DUMMY_PNG_BYTES)

        result = publish_preintegration_literal_visuals(
            {1: dummy_png_path},
            _TEST_MODULE_LESSON_PART,
            site_repo_url=_SITE_REPO_URL,
            run_id="TEST-GIT-SITE-ADHOC-001",
            mode="ad-hoc",
        )

        assert result["pushed"] is False, (
            "Ad-hoc mode must not push to the remote site; pushed should be False"
        )
        assert result["preintegration_ready"] is False, (
            "Ad-hoc mode should not signal preintegration_ready=True (no URL substitution)"
        )

    def test_skips_missing_source_paths(self, tmp_path: Path) -> None:
        """Missing PNG paths are skipped (non-fatal) and recorded in 'skipped'."""
        missing_path = tmp_path / "does_not_exist.png"
        # Do NOT create the file

        result = publish_preintegration_literal_visuals(
            {99: missing_path},
            _TEST_MODULE_LESSON_PART,
            site_repo_url=_SITE_REPO_URL,
            run_id="TEST-GIT-SITE-SKIP-001",
            mode="default",
        )

        assert result["copied_count"] == 0
        skipped = result.get("skipped", [])
        assert any(s.get("card_number") == 99 for s in skipped), (
            f"Card 99 should be in skipped with missing_local_path reason; got: {skipped}"
        )
        # No push should happen if there are no files to copy
        assert result["pushed"] is False


@pytest.mark.live_api_e2e
@requires_feature
@requires_token
class TestUrlSubstitutionInDiagramCards:
    """Confirm that after a successful publish, the hosted URLs are returned
    in a form that can be directly used to replace diagram_cards image_url
    fields — no mocking of git, requests, or URL validation."""

    def test_substituted_cards_contain_accessible_urls(self, tmp_path: Path) -> None:
        dummy_png_path = tmp_path / "substitution_test.png"
        dummy_png_path.write_bytes(_DUMMY_PNG_BYTES)

        result = publish_preintegration_literal_visuals(
            {5: dummy_png_path},
            _TEST_MODULE_LESSON_PART,
            site_repo_url=_SITE_REPO_URL,
            run_id="TEST-GIT-SITE-SUBST-001",
            mode="default",
        )

        assert result["pushed"] is True
        # The url_base must be an HTTPS GitHub Pages URL
        url_base = result.get("url_base", "")
        assert url_base.startswith("https://"), (
            f"url_base must be an HTTPS URL; got: {url_base}"
        )
        assert "jlenrique.github.io" in url_base

        # Substituted card numbers must include card 5
        assert 5 in result.get("substituted_cards", [])
