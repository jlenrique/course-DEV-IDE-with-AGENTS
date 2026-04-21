# /// script
# requires-python = ">=3.10"
# ///
"""Pre-dispatch gate for literal-visual diagram cards (§06B enforcement).

Reads ``gary-outbound-envelope.yaml`` and blocks Gary dispatch (§07) if:
- Any required diagram card has no resolved ``image_url`` and no valid local
  ``preintegration_png_path`` on disk (tracked mode only).
- ``literal-visual-operator-packet.md`` is absent when required cards exist.

Exits 0 (pass) when:
- ``diagram_cards`` is absent or empty — no literal-visual source assets this run.
- All required cards have a resolved image URL or a staged local preintegration path.
- The operator packet is present confirming HIL sign-off.

Boundary with post-dispatch validator (``validate-gary-dispatch-ready.py``):
- THIS gate: checks image resolution BEFORE Gary is invoked.
- POST-dispatch gate: checks ``literal_visual_publish`` receipt AFTER Gary runs.
They are NOT redundant — both must exist.

Exit codes:
    0 — gate passed or skipped (no diagram cards)
    1 — one or more blocking issues found
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# Project root — for resolving repo-relative preintegration paths (same pattern
# as _resolve_existing_local_path in validate-gary-dispatch-ready.py)
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

ENVELOPE_FILENAME = "gary-outbound-envelope.yaml"
OPERATOR_PACKET_FILENAME = "literal-visual-operator-packet.md"


def _is_remote_http_ref(value: str) -> bool:
    """Return True if value is a valid public HTTPS/HTTP URL."""
    parsed = urlparse(str(value).strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_ad_hoc_mode(envelope: dict[str, Any]) -> bool:
    """Return True if the envelope indicates ad-hoc execution mode."""
    mode = str(
        envelope.get("run_mode")
        or envelope.get("execution_mode")
        or ""
    ).strip().lower()
    return mode in {"ad-hoc", "adhoc"}


def validate_literal_visual_pre_dispatch(
    bundle_dir: Path,
    *,
    envelope_path: Path | None = None,
) -> list[str]:
    """Validate literal-visual diagram card readiness before Gary dispatch.

    Args:
        bundle_dir: Bundle directory containing ``gary-outbound-envelope.yaml``
            and ``literal-visual-operator-packet.md``.
        envelope_path: Override path to the outbound envelope (testing only).

    Returns:
        List of error strings. Empty list means gate passes.
    """
    if yaml is None:  # pragma: no cover
        return ["pyyaml is required to parse gary-outbound-envelope.yaml"]

    resolved_envelope = envelope_path or (bundle_dir / ENVELOPE_FILENAME)
    if not resolved_envelope.is_file():
        return [f"gary-outbound-envelope.yaml not found in {bundle_dir}"]

    try:
        raw = yaml.safe_load(resolved_envelope.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            return [f"gary-outbound-envelope.yaml must be a YAML mapping, got {type(raw).__name__}"]
        envelope: dict[str, Any] = raw
    except Exception as exc:
        return [f"Could not parse gary-outbound-envelope.yaml: {exc}"]

    diagram_cards: list[Any] = envelope.get("diagram_cards") or []

    # AC-1 Check 1: skip entirely when no diagram cards
    if not diagram_cards:
        return []

    ad_hoc = _is_ad_hoc_mode(envelope)
    errors: list[str] = []
    has_required_card = False

    for card in diagram_cards:
        if not isinstance(card, dict):
            continue

        required = card.get("required", False)
        if not required:
            continue

        has_required_card = True
        card_number = card.get("card_number", "?")
        slide_id = card.get("slide_id", "?")
        image_url = str(card.get("image_url") or "").strip()
        preintegration_path = str(card.get("preintegration_png_path") or "").strip()

        # Resolve the card
        if image_url and _is_remote_http_ref(image_url):
            # Valid public HTTPS URL — card is resolved
            continue

        if preintegration_path:
            if ad_hoc:
                # AC-1 mode check: ad-hoc cannot use local preintegration paths
                errors.append(
                    f"Card {card_number} (slide {slide_id}): local preintegration_png_path "
                    "is not permitted in ad-hoc mode — provide a hosted HTTPS image_url"
                )
                continue
            # Resolve: absolute → direct; relative → try bundle-dir first,
            # then project-root (repo-relative paths like "course-content/..."
            # live at the project root, not inside the bundle directory).
            if Path(preintegration_path).is_absolute():
                resolved: Path | None = Path(preintegration_path)
            else:
                bundle_candidate = bundle_dir / preintegration_path
                root_candidate = _PROJECT_ROOT / preintegration_path
                if bundle_candidate.is_file():
                    resolved = bundle_candidate
                elif root_candidate.is_file():
                    resolved = root_candidate
                else:
                    resolved = None
            if resolved is not None and resolved.is_file():
                continue
            errors.append(
                f"Card {card_number} (slide {slide_id}): preintegration_png_path "
                f"{preintegration_path!r} declared but file not found "
                f"(checked bundle-relative and repo-root-relative)"
            )
            continue

        # Neither image_url nor usable preintegration path
        errors.append(
            f"Card {card_number} (slide {slide_id}): image_url is null/empty and no "
            "valid preintegration_png_path — operator must publish asset or supply a "
            "hosted HTTPS URL before Gary dispatch"
        )

    # AC-1 Check 3: operator packet required when any required card exists
    if has_required_card:
        packet_path = bundle_dir / OPERATOR_PACKET_FILENAME
        if not packet_path.is_file():
            errors.append(
                f"{OPERATOR_PACKET_FILENAME} is absent — operator must confirm "
                "literal-visual assets are staged before Gary dispatch"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    if yaml is None:  # pragma: no cover
        print("FAIL: pyyaml is required")
        return 1

    parser = argparse.ArgumentParser(
        description="Pre-dispatch gate: validate literal-visual diagram card image readiness."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Bundle directory containing gary-outbound-envelope.yaml",
    )
    args = parser.parse_args(argv)

    bundle_dir = Path(args.bundle_dir).resolve()
    errors = validate_literal_visual_pre_dispatch(bundle_dir)

    if not errors:
        print("PASS — literal-visual pre-dispatch gate (all diagram cards resolved)")
        return 0

    print(f"FAIL — literal-visual pre-dispatch gate ({len(errors)} issue(s)):")
    for err in errors:
        print(f"  • {err}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
