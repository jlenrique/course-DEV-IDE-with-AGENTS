"""Marcus capability registry — markdown frontmatter is authoritative.

The scaffold's capability-authoring convention (see
``skills/bmad-agent-marcus/references/capability-authoring.md``) declares that
capabilities live as ``<slug>.md`` files with ``name:`` + ``code:`` frontmatter
in ``skills/bmad-agent-marcus/capabilities/``. This registry parses those
files to produce a lookup table, and cross-checks against the supplementary
``registry.yaml`` index (fast programmatic access + explicit
``script_module``/``schema_path`` pointers).

``AC-T.9``: registry-schema cross-reference — every code listed in
``registry.yaml`` must have a matching frontmatter-declared capability
markdown file and a corresponding ``schemas/<code_slug>.yaml`` file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from scripts.utilities.file_helpers import project_root

CAPABILITIES_DIR = (
    project_root() / "skills" / "bmad-agent-marcus" / "capabilities"
)
SCHEMAS_DIR = CAPABILITIES_DIR / "schemas"
REGISTRY_YAML = CAPABILITIES_DIR / "registry.yaml"


class UnknownCapabilityError(KeyError):
    """Raised when a capability code is not registered (AC-T.8).

    Router-level error (Python), distinct from capability-execution errors
    (which go into the ReturnEnvelope.errors list per AC-C.3).
    """


# Back-compat alias (kept because tests and the package __init__ import
# ``UnknownCapability`` directly). Callers can use either name; both point
# at the same class.
UnknownCapability = UnknownCapabilityError


@dataclass(frozen=True)
class RegistryEntry:
    """One capability's registration data."""

    code: str
    name: str
    description: str
    script_module: str
    schema_path: str
    full_or_stub: str  # "full" | "stub"
    markdown_path: Path


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(md_path: Path) -> dict[str, Any] | None:
    """Return frontmatter dict or None if the file has no parseable frontmatter."""
    if not md_path.is_file():
        return None
    text = md_path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _scan_capabilities_dir() -> dict[str, RegistryEntry]:
    """Walk ``capabilities/*.md``, filter for frontmatter with name+code."""
    entries: dict[str, RegistryEntry] = {}
    if not CAPABILITIES_DIR.is_dir():
        return entries
    for md_file in sorted(CAPABILITIES_DIR.glob("*.md")):
        frontmatter = _parse_frontmatter(md_file)
        if not frontmatter:
            continue
        code = frontmatter.get("code")
        name = frontmatter.get("name")
        if not (isinstance(code, str) and isinstance(name, str)):
            continue  # scaffold convention: missing either → ignored
        description = str(frontmatter.get("description", "")).strip()
        script_module = str(frontmatter.get("script_module", "")).strip()
        schema_path = str(frontmatter.get("schema_path", "")).strip()
        full_or_stub = str(frontmatter.get("full_or_stub", "full")).strip().lower()
        entries[code] = RegistryEntry(
            code=code,
            name=name,
            description=description,
            script_module=script_module,
            schema_path=schema_path,
            full_or_stub=full_or_stub if full_or_stub in {"full", "stub"} else "full",
            markdown_path=md_file,
        )
    return entries


def _load_registry_yaml() -> dict[str, dict[str, Any]]:
    """Supplementary YAML index. Authoritative source is markdown frontmatter."""
    if not REGISTRY_YAML.is_file():
        return {}
    try:
        data = yaml.safe_load(REGISTRY_YAML.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return {}
    if not isinstance(data, dict):
        return {}
    caps = data.get("capabilities", {})
    if not isinstance(caps, dict):
        return {}
    return {code: entry for code, entry in caps.items() if isinstance(entry, dict)}


def _build_registry() -> dict[str, RegistryEntry]:
    """Scan + cross-check. Markdown frontmatter wins on conflict."""
    return _scan_capabilities_dir()


# Module-level registry, populated at import time.
CAPABILITY_REGISTRY: dict[str, RegistryEntry] = _build_registry()


def get(code: str) -> RegistryEntry:
    """Lookup a capability by code; raises ``UnknownCapability`` on miss (AC-T.8)."""
    if not code or code not in CAPABILITY_REGISTRY:
        raise UnknownCapability(
            f"Capability code {code!r} is not registered. Known: "
            f"{sorted(CAPABILITY_REGISTRY.keys())}"
        )
    return CAPABILITY_REGISTRY[code]


def cross_reference_audit() -> list[str]:
    """Return human-readable findings for registry↔schema↔markdown skew (AC-T.9).

    Empty list = clean.
    """
    findings: list[str] = []
    yaml_entries = _load_registry_yaml()

    # YAML codes must have a markdown capability
    for code in yaml_entries:
        if code not in CAPABILITY_REGISTRY:
            findings.append(
                f"registry.yaml declares code {code!r} but no matching "
                f"capabilities/<slug>.md frontmatter was found"
            )

    # Markdown codes must have a YAML entry
    for code in CAPABILITY_REGISTRY:
        if code not in yaml_entries:
            findings.append(
                f"capabilities/*.md declares code {code!r} but registry.yaml "
                f"does not list it"
            )

    # Every code must have a schema file
    for code, entry in CAPABILITY_REGISTRY.items():
        schema_path = SCHEMAS_DIR / f"{code.lower().replace('-', '_')}.yaml"
        if not schema_path.is_file():
            findings.append(
                f"capability {code!r} has no schema file at {schema_path}"
            )
        elif entry.schema_path and not (project_root() / entry.schema_path).is_file():
            findings.append(
                f"capability {code!r} frontmatter points schema_path at "
                f"{entry.schema_path!r} which does not exist"
            )

    return findings


__all__ = [
    "CAPABILITY_REGISTRY",
    "RegistryEntry",
    "UnknownCapability",
    "get",
    "cross_reference_audit",
]
