"""Final clean patch: restore validator from git baseline, insert new function at module scope."""
import ast
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
ORIG = PROJECT_ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "validate-gary-dispatch-ready.py.orig"
TARGET = PROJECT_ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "validate-gary-dispatch-ready.py"

# Read clean baseline
src = ORIG.read_text(encoding="utf-8-sig")
lines = src.splitlines()
ast.parse(src)  # sanity check

# Find insertion point just before def _infer_gamma_asset_family
insert_before = None
for i, l in enumerate(lines):
    if l.startswith("def _infer_gamma_asset_family("):
        insert_before = i
        break

if insert_before is None:
    raise RuntimeError("Could not find _infer_gamma_asset_family insertion point")

new_block = [
    "_PLANNING_DIRECTIVE_PATTERNS: list[re.Pattern[str]] = [",
    '    re.compile(r"instructional content aligned to", re.IGNORECASE),',
    "]",
    "",
    "",
    "def _validate_literal_text_content_bearing(",
    "    bundle_dir: Path,",
    "    dispatch_metadata: dict[str, Any],",
    ") -> list[str]:",
    '    """Check that literal-text slides in gary-slide-content.json contain real',
    "    source text, not Irene planning directives.",
    "",
    "    Requires both gary-slide-content.json (via dispatch_metadata) and",
    "    gary-fidelity-slides.json to be present. If either is absent the check",
    "    is skipped gracefully so older run artifacts are not broken.",
    "",
    "    Returns a list of error strings (empty = pass).",
    '    """',
    "    errors: list[str] = []",
    "",
    '    fidelity_path = bundle_dir / "gary-fidelity-slides.json"',
    "    if not fidelity_path.exists():",
    "        return errors  # graceful skip -- older run without fidelity file",
    "",
    "    slides_content_json_path = str(",
    '        dispatch_metadata.get("slides_content_json_path") or ""',
    "    ).strip()",
    "    if not slides_content_json_path:",
    "        return errors  # already caught by dispatch_metadata check",
    "",
    "    content_path = (bundle_dir / slides_content_json_path).resolve()",
    "    if not content_path.is_file():",
    "        # Try relative to project root",
    "        content_path = (PROJECT_ROOT / slides_content_json_path).resolve()",
    "    if not content_path.is_file():",
    "        return errors  # file missing -- structural check already handles absence",
    "",
    "    try:",
    "        fidelity_data = json.loads(fidelity_path.read_text(encoding='utf-8'))",
    "        content_data = json.loads(content_path.read_text(encoding='utf-8'))",
    "    except (json.JSONDecodeError, OSError):",
    "        return errors  # parse failures are separate concerns",
    "",
    "    fidelity_slides: list[dict[str, Any]] = fidelity_data.get('slides', [])",
    "    literal_text_numbers: set[int] = {",
    '        int(s["slide_number"])',
    "        for s in fidelity_slides",
    "        if isinstance(s, dict)",
    "        and str(s.get('fidelity', '')).strip().lower() == 'literal-text'",
    "        and isinstance(s.get('slide_number'), int)",
    "    }",
    "",
    "    if not literal_text_numbers:",
    "        return errors",
    "",
    "    content_slides: list[dict[str, Any]] = content_data.get('slides', [])",
    "    for slide in content_slides:",
    "        if not isinstance(slide, dict):",
    "            continue",
    "        slide_number = slide.get('slide_number')",
    "        if not isinstance(slide_number, int) or slide_number not in literal_text_numbers:",
    "            continue",
    "        content_field = str(slide.get('content') or '').strip()",
    "        for pattern in _PLANNING_DIRECTIVE_PATTERNS:",
    "            if pattern.search(content_field):",
    "                errors.append(",
    '                    f"gary-slide-content.json slide {slide_number} (literal-text) "',
    '                    f"content field contains a planning directive rather than actual "',
    '                    f"source text (matched pattern: {pattern.pattern!r}). "',
    '                    f"For textMode=preserve, Gamma renders this text verbatim on screen. "',
    '                    f"Replace with the extracted source text from extracted.md anchor."',
    "                )",
    "                break  # one error per slide is sufficient",
    "",
    "    return errors",
    "",
    "",
]

# Also need to wire the call into validate_gary_dispatch_ready.
# Find the wiring spot: after _validate_preintegration_publish_receipt call
wire_after = None
for i, l in enumerate(lines):
    if "_validate_preintegration_publish_receipt(payload," in l:
        wire_after = i
        break

if wire_after is None:
    raise RuntimeError("Could not find _validate_preintegration_publish_receipt wiring point")

# The call to _validate_preintegration_publish_receipt spans a few lines, find closing )
close_paren = wire_after
for i in range(wire_after, wire_after + 5):
    if lines[i].strip() == ")":
        close_paren = i
        break

wire_lines = [
    "        if isinstance(dispatch_metadata, dict):",
    "            errors.extend(",
    "                _validate_literal_text_content_bearing(",
    "                    payload_path.parent, dispatch_metadata",
    "                )",
    "            )",
]

print(f"Insert new block before line {insert_before+1}")
print(f"Insert wiring after line {close_paren+1}")

# Build the new file
# 1. Insert new_block before insert_before
# 2. Insert wire_lines after close_paren (adjusted by the offset from step 1)
result_lines = list(lines)
result_lines = result_lines[:insert_before] + new_block + result_lines[insert_before:]

# Adjust close_paren index for the inserted block
adjusted_close_paren = close_paren + len(new_block)
result_lines = result_lines[:adjusted_close_paren + 1] + wire_lines + result_lines[adjusted_close_paren + 1:]

result = "\n".join(result_lines) + "\n"
try:
    ast.parse(result)
    print("Syntax OK")
except SyntaxError as e:
    # Show context
    ctx = result_lines[max(0, e.lineno-3):e.lineno+2]
    for li, l in enumerate(ctx, max(1, e.lineno-2)):
        print(f"  {li}: {repr(l)}")
    raise

TARGET.write_text(result, encoding="utf-8")
print(f"Written {len(result_lines)} lines to {TARGET.name}")
