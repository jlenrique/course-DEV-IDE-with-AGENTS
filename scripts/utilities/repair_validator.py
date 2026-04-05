"""One-shot repair script for the corrupted validate-gary-dispatch-ready.py file."""
import ast
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGET = PROJECT_ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "validate-gary-dispatch-ready.py"

lines = TARGET.read_text(encoding="utf-8").splitlines()

# --------------------------------------------------------------------------
# Fix 1: De-indent the _PLANNING_DIRECTIVE_PATTERNS and
#         _validate_literal_text_content_bearing block at lines 94-169
#         (1-indexed) = [93:169] (0-indexed).  They are 4-space indented
#         inside _load_diagram_cards and must be module-level.
# --------------------------------------------------------------------------
fixed = list(lines)
for i in range(93, 169):
    line = fixed[i]
    if line.startswith("    "):
        fixed[i] = line[4:]
    # blank lines stay blank

# --------------------------------------------------------------------------
# Fix 2: The _validate_preintegration_publish_receipt function was corrupted:
#         the closing ).strip() of `invocation_mode = str(...)` was removed,
#         and content from validate_gary_dispatch_ready was spliced in.
#
#  Corrupt span starts at line 305 (1-indexed) = index 304 (0-indexed):
#      "    invocation_mode = str("
#  and runs through line 314 (1-indexed) = index 313 (0-indexed):
#      "    bundle_dir = payload_path.parent if payload_path is not None else None"
#  (line 315 = index 314, "    if isinstance(slides, list):" belongs in
#   validate_gary_dispatch_ready and IS already present later in the file)
#
#  We replace [304:314] with the correct tail of
#  _validate_preintegration_publish_receipt PLUS the correct beginning of
#  validate_gary_dispatch_ready (up to and including "    missing_local_png_for: list").
# --------------------------------------------------------------------------

# Locate the corruption start (after Fix 1 the indices shifted slightly because
# we only removed spaces, not lines, so the count is the same).
corrupt_start = None
for i, l in enumerate(fixed):
    if l == "    invocation_mode = str(":
        corrupt_start = i
        break

if corrupt_start is None:
    raise RuntimeError("Could not find corrupt_start marker -- file may already be fixed.")

# The corrupt region ends just before "    if isinstance(slides, list):"
# which belongs as the FIRST line kept from validate_gary_dispatch_ready's
# loop.  But we need to insert the missing header of validate_gary_dispatch_ready
# BEFORE that line.  So we:
#  a) cut out [corrupt_start : corrupt_start+9] (the 9-line corrupt blob)
#  b) insert the correct replacement lines

replacement = [
    "    invocation_mode = str(",
    '        dispatch_metadata.get("invocation_mode")',
    '        or payload.get("mode")',
    '        or payload.get("execution_mode")',
    "    ).strip()",
    '    if invocation_mode == "ad-hoc":',
    "        errors.append(",
    '            "Local preintegration paths are not allowed in ad-hoc mode; "',
    '            "use a full deployment run with site_repo_url"',
    "        )",
    "",
    "    return errors",
    "",
    "",
    "def validate_gary_dispatch_ready(",
    "    payload: dict[str, Any],",
    "    *,",
    "    payload_path: Path | None = None,",
    ") -> dict[str, Any]:",
    '    """Validate dispatch payload for Gate 2 readiness."""',
    "    errors: list[str] = []",
    "",
    '    slides = payload.get("gary_slide_output")',
    "    if not isinstance(slides, list):",
    '        errors.append("gary_slide_output must be an array")',
    "        slides = []",
    "",
    "    if isinstance(slides, list) and len(slides) == 0:",
    '        errors.append("gary_slide_output must contain at least one slide for Gate 2 review")',
    "",
    "    try:",
    "        validate_dispatch_ready(payload)",
    "    except ValueError as exc:",
    "        errors.append(str(exc))",
    "",
    "    missing_local_png_for: list[str] = []",
    "    invalid_non_png_for: list[str] = []",
]

# How many lines to cut? The corrupt span = from corrupt_start up to (but not
# including) the first "    if isinstance(slides, list):" line
cut_end = corrupt_start
for i in range(corrupt_start, len(fixed)):
    if fixed[i] == "    if isinstance(slides, list):":
        cut_end = i
        break

print(f"Cutting lines {corrupt_start+1}-{cut_end} (1-indexed), replacing with {len(replacement)} lines")
print(f"First cut line: {repr(fixed[corrupt_start])}")
print(f"First kept line after cut: {repr(fixed[cut_end])}")

fixed = fixed[:corrupt_start] + replacement + fixed[cut_end:]

# --------------------------------------------------------------------------
# Write and verify
# --------------------------------------------------------------------------
result = "\n".join(fixed) + "\n"
try:
    ast.parse(result)
    print("Syntax OK")
except SyntaxError as e:
    raise RuntimeError(f"Syntax error after repair at line {e.lineno}: {e.msg}") from e

TARGET.write_text(result, encoding="utf-8")
print(f"Written {len(fixed)} lines to {TARGET}")
