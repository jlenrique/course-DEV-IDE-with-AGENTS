"""Pre-packet construction — Marcus-Intake → Irene handoff at step 04/05.

Home of the ``prepare_irene_packet`` function lifted at Story 30-2a from
``scripts/utilities/prepare-irene-packet.py``.

Maya-facing note
----------------

Maya does not call this module. It is an internal bundle aggregator that
produces the ``irene-packet.md`` handoff artifact Irene consumes at the
step 04 → 05 boundary.

Developer discipline note
-------------------------

* **30-2a (this commit — refactor-only lift):** body lifted verbatim from
  the pre-30-2a CLI script at ``scripts/utilities/prepare-irene-packet.py``.
  Zero behavior change. The CLI script becomes a thin shim that imports
  and calls this function.
* **30-2b (next — emission feature):** adds the
  ``emit_pre_packet_snapshot`` call around this function's result so the
  Lesson Plan log captures the handoff event. Emission happens at the
  orchestrator layer via :mod:`marcus.orchestrator.write_api`; this
  module stays pure file-I/O.

Byte-identity invariant
-----------------------

The 30-1 Golden-Trace regression test at
``tests/test_marcus_golden_trace_regression.py`` pins the pre-refactor
envelope I/O against the committed fixture at
``tests/fixtures/golden_trace/marcus_pre_30-1/``. Any diff in the
normalized output (modulo the four locked normalization rules:
timestamps / UUID4 / SHA-256 / repo-root) fails the lift. R1 ruling
amendment 12 (Murat RED binding PDG).

Lift origin
-----------

* Pre-30-2a location: ``scripts/utilities/prepare-irene-packet.py``
  (lines 18-75 of the pre-30-2a file).
* Lift commit: 30-2a (see Story
  ``_bmad-output/implementation-artifacts/30-2a-pre-packet-extraction-lift.md``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

__all__: Final[tuple[str, ...]] = ("prepare_irene_packet",)


def prepare_irene_packet(
    bundle_dir: Path,
    run_id: str,
    output_path: Path,
) -> dict[str, Any]:
    """Generate irene-packet.md from bundle artifacts."""
    # Read inputs
    extracted_md = bundle_dir / "extracted.md"
    metadata_json = bundle_dir / "metadata.json"
    operator_directives = bundle_dir / "operator-directives.md"
    ingestion_receipt = bundle_dir / "ingestion-quality-gate-receipt.md"

    if not extracted_md.exists():
        raise FileNotFoundError(f"extracted.md not found in {bundle_dir}")
    if not metadata_json.exists():
        raise FileNotFoundError(f"metadata.json not found in {bundle_dir}")
    if not operator_directives.exists():
        raise FileNotFoundError(f"operator-directives.md not found in {bundle_dir}")

    extracted_content = extracted_md.read_text(encoding="utf-8")
    metadata = json.loads(metadata_json.read_text(encoding="utf-8"))
    directives_content = operator_directives.read_text(encoding="utf-8")

    ingestion_content = ""
    if ingestion_receipt.exists():
        ingestion_content = ingestion_receipt.read_text(encoding="utf-8")

    # Build packet sections
    packet_sections = [
        f"# Irene Packet for {run_id}",
        "",
        "## Source Bundle Summary",
        f"- Primary source: {metadata.get('primary_source', 'unknown')}",
        f"- Total sections: {metadata.get('total_sections', 'unknown')}",
        f"- Extraction confidence: {metadata.get('overall_confidence', 'unknown')}",
        "",
        "## Operator Directives",
        directives_content,
        "",
        "## Ingestion Quality Receipt",
        ingestion_content,
        "",
        "## Extracted Content",
        extracted_content,
    ]

    packet_content = "\n".join(packet_sections)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(packet_content, encoding="utf-8")

    return {
        "packet_path": str(output_path),
        "sections": len(packet_sections),
        "has_directives": bool(directives_content.strip()),
        "has_ingestion_receipt": bool(ingestion_content.strip()),
    }
