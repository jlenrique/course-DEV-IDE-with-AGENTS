"""AC-T.10 — Locator-shape directory ↔ classification-dict lockstep.

Every locator-shape `ProviderInfo` declared in `provider_directory._LOCATOR_SHAPE_DIRECTORY`
must appear in the `LOCATOR_SHAPE_PROVIDERS` classification dict in
`test_transform_registry_lockstep.py`, and vice versa. Bidirectional lockstep
encoded in code, not docstrings — a drift in either direction fails loudly.
"""

from __future__ import annotations

from retrieval import list_providers

# The canonical locator-shape classification dict. Touched in lockstep with
# provider_directory._LOCATOR_SHAPE_DIRECTORY. Used by the dispatcher routing
# to decide which directive shapes pass through the degenerate-case transform.
LOCATOR_SHAPE_PROVIDERS: dict[str, str] = {
    "local_file": "Generic local text-file read",
    "pdf": "pypdf / pdfplumber",
    "docx": "python-docx",
    "md": "Direct read + normalization",
    "html": "requests + HTML-to-text",
    "playwright_html": "Saved HTML re-extract",
    "notion": "Notion direct REST API",
    "box": "Box Drive local FS",
    "notion_mcp": "Story 27-5 ratified",
    "box_api": "Story 27-6 ratified",
    "playwright_mcp": "Story 27-7 ratified",
}


RETRIEVAL_SHAPE_PROVIDERS: dict[str, str] = {
    "fake": "Reference adapter (27-0 foundation tests)",
    "scite": "Story 27-2 ratified (first retrieval-shape adapter)",
    "consensus": "Story 27-2.5 ratified (cross-val partner to scite)",
    "image": "Story 27-3 ratified (sensory-bridges integration)",
    "youtube": "Story 27-4 ratified (three-asset output)",
    "openai_chatgpt": "Backlog — operator-directed forward placeholder",
}


def test_every_locator_in_directory_has_classification() -> None:
    directory_locator_ids = {p.id for p in list_providers(shape="locator")}
    missing = directory_locator_ids - set(LOCATOR_SHAPE_PROVIDERS)
    assert not missing, (
        f"provider_directory lists locator-shape IDs not in LOCATOR_SHAPE_PROVIDERS: "
        f"{missing}. Add them here or to the directory — lockstep."
    )


def test_every_classification_locator_is_in_directory() -> None:
    directory_locator_ids = {p.id for p in list_providers(shape="locator")}
    missing = set(LOCATOR_SHAPE_PROVIDERS) - directory_locator_ids
    assert not missing, (
        f"LOCATOR_SHAPE_PROVIDERS names IDs not in provider_directory: "
        f"{missing}. Add them to _LOCATOR_SHAPE_DIRECTORY — lockstep."
    )


def test_every_retrieval_classification_is_in_directory() -> None:
    """Directory and RETRIEVAL_SHAPE_PROVIDERS must agree on retrieval-shape IDs.

    Scope note: backlog entries (`openai_chatgpt`) are counted here — the
    directory is the roster of "what Texas intends to work with," regardless
    of whether an adapter class exists yet.
    """
    directory_retrieval_ids = {p.id for p in list_providers(shape="retrieval")}
    missing = set(RETRIEVAL_SHAPE_PROVIDERS) - directory_retrieval_ids
    assert not missing, (
        f"RETRIEVAL_SHAPE_PROVIDERS names IDs not in provider_directory: "
        f"{missing}."
    )


def test_no_shape_overlap() -> None:
    """A provider ID cannot appear as BOTH retrieval-shape and locator-shape."""
    r_ids = set(RETRIEVAL_SHAPE_PROVIDERS)
    l_ids = set(LOCATOR_SHAPE_PROVIDERS)
    overlap = r_ids & l_ids
    assert not overlap, (
        f"Provider IDs appear in both shapes: {overlap}. "
        f"The distinction lives in the input-origin axis — a provider cannot "
        f"be both retrieval-shape (remote query DSL) and locator-shape (local path)."
    )
