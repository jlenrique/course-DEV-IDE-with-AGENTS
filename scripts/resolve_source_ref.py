"""Resolve source_ref provenance annotations to content slices.

Implements the grammar defined in docs/source-ref-grammar.md:
    {filename}#{path_expression}

Path expressions:
    - Heading hierarchy: "Section > Subsection > ..."
    - Line range: "L{start}-L{end}"
    - Heading anchor: "## Heading Text"
"""

import re
from pathlib import Path


def resolve_source_ref(
    source_ref: str, base_path: str
) -> tuple[str, str]:
    """Parse and resolve a source_ref string.

    Args:
        source_ref: The source_ref string (e.g., "extracted.md#Chapter 2 > Knowledge Check")
        base_path: Base directory for resolving relative filenames.

    Returns:
        (resolved_content_slice, confidence) where confidence is "exact" | "approximate" | "broken"
    """
    if "#" not in source_ref:
        filepath = Path(base_path) / source_ref
        if filepath.exists():
            return filepath.read_text(encoding="utf-8"), "exact"
        return "", "broken"

    filename, path_expr = source_ref.split("#", 1)
    filepath = Path(base_path) / filename.strip()

    if not filepath.exists():
        return "", "broken"

    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    line_range_match = re.match(r"L(\d+)-L(\d+)", path_expr.strip())
    if line_range_match:
        start = int(line_range_match.group(1)) - 1
        end = int(line_range_match.group(2))
        if 0 <= start < len(lines) and start < end <= len(lines):
            return "\n".join(lines[start:end]), "exact"
        return "", "broken"

    if path_expr.strip().startswith("##"):
        target_heading = path_expr.strip()
        return _extract_heading_section(lines, target_heading)

    if " > " in path_expr:
        return _extract_heading_hierarchy(lines, path_expr.strip())

    return _extract_heading_section(lines, f"## {path_expr.strip()}")


def _extract_heading_section(
    lines: list[str], target_heading: str
) -> tuple[str, str]:
    """Extract content under a specific heading until the next heading of same or higher level."""
    target_clean = target_heading.lstrip("#").strip()
    target_level = len(target_heading) - len(target_heading.lstrip("#"))
    if target_level == 0:
        target_level = 2

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        heading_text = stripped.lstrip("#").strip()
        if heading_text.lower() == target_clean.lower():
            section_lines = []
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line.startswith("#"):
                    next_level = len(next_line) - len(next_line.lstrip("#"))
                    if next_level <= target_level:
                        break
                section_lines.append(lines[j])
            result = "\n".join(section_lines).strip()
            return (result, "exact") if result else ("", "approximate")

    return "", "broken"


def _extract_heading_hierarchy(
    lines: list[str], hierarchy: str
) -> tuple[str, str]:
    """Resolve heading hierarchy like 'Chapter 2 > Knowledge Check > Item 3'."""
    parts = [p.strip() for p in hierarchy.split(">")]

    current_start = 0
    current_end = len(lines)

    for depth, part in enumerate(parts):
        found = False
        for i in range(current_start, current_end):
            stripped = lines[i].strip()
            if not stripped.startswith("#"):
                continue
            heading_text = stripped.lstrip("#").strip()
            if heading_text.lower() == part.lower():
                heading_level = len(stripped) - len(stripped.lstrip("#"))
                section_end = current_end
                for j in range(i + 1, current_end):
                    next_line = lines[j].strip()
                    if next_line.startswith("#"):
                        next_level = len(next_line) - len(next_line.lstrip("#"))
                        if next_level <= heading_level:
                            section_end = j
                            break
                current_start = i + 1
                current_end = section_end
                found = True
                break

        if not found:
            if depth > 0:
                result = "\n".join(lines[current_start:current_end]).strip()
                return (result, "approximate") if result else ("", "broken")
            return "", "broken"

    result = "\n".join(lines[current_start:current_end]).strip()
    return (result, "exact") if result else ("", "broken")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python resolve_source_ref.py <source_ref> <base_path>")
        sys.exit(1)
    content, confidence = resolve_source_ref(sys.argv[1], sys.argv[2])
    print(f"Confidence: {confidence}")
    print(f"Content ({len(content)} chars):")
    print(content[:500] if content else "(empty)")
