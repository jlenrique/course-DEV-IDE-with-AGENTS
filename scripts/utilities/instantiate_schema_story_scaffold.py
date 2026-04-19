"""Instantiate the schema-story scaffold into canonical repo locations.

Stamps the schema-story template bundle at
``docs/dev-guide/scaffolds/schema-story/`` into per-story target paths, doing
the 3-step manual procedure (cp → sed → move) documented in the scaffold
README as a single command. Substitutes all 15 active tokens, renames
``.tmpl`` → the correct extension, and places files at their canonical repo
locations.

Compounds on schema-shape stories 31-3, 29-1, 32-2 (and any future story
whose deliverable is a Pydantic-v2 model family + emitted JSON Schema +
shape-pin tests). Target paths:

    story spec      → _bmad-output/specs/pre-seed-drafts/{STORY_KEY}-PRE-SEED.md
                      (default — Cursor's ``bmad-create-story`` writes the
                      authoritative spec at ``_bmad-output/implementation-
                      artifacts/{STORY_KEY}.md``; this pre-seed lands in the
                      non-authoritative directory so the two don't collide)
                      OR with --spec-target=authoritative → goes directly to
                      _bmad-output/implementation-artifacts/{STORY_KEY}.md
                      (use only when you are the authoritative author)
    schema module   → {RELATIVE_FILE_PATH}  (e.g. marcus/lesson_plan/log.py)
    digest module   → {RELATIVE_FILE_PATH with _digest suffix}  (optional;
                      omit with --no-digest for stories with no canonical
                      serialization surface)
    shape test      → tests/contracts/test_{schema_name}_shape_stable.py
    parity test     → tests/contracts/test_{schema_name}_json_schema_parity.py
    facade-leak test → tests/contracts/test_no_intake_orchestrator_leak_{schema_name}.py
    CHANGELOG entry → stdout for operator paste into
                      _bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md

The script NEVER overwrites an existing file — if any target path is already
occupied it aborts with an error listing all collisions. Use ``--force`` to
override, or ``--skip-story-spec`` when a non-authoritative pre-seed already
exists and you only want the scaffolded source / test files.

Token derivation:

    Required user inputs (3):
      --story-key       {{STORY_KEY}}        e.g. 31-2-lesson-plan-log
      --schema-name     {{SCHEMA_NAME}}      e.g. LessonPlanLog (PascalCase)
      --module-path     {{MODULE_PATH}}      e.g. marcus.lesson_plan.log

    Derived automatically (5):
      {{schema_name}}          PascalCase → snake_case (LessonPlanLog
                               → lesson_plan_log)
      {{SCHEMA_NAME_UPPER}}    snake_case.upper()
                               (LESSON_PLAN_LOG)
      {{RELATIVE_FILE_PATH}}   MODULE_PATH with dots → slashes + .py
                               (marcus/lesson_plan/log.py)
      {{MODULE_PATH_AS_PATH}}  MODULE_PATH with dots → slashes, no .py
                               (marcus/lesson_plan/log)
      {{DATE}}                 today (UTC), ISO-8601

    Optional CLI args with defaults (7):
      --story-slug         {{STORY_SLUG}}      default: derived from STORY_KEY
                                              (strip leading NN-N- prefix,
                                               hyphens → spaces, title-case)
      --epic-number        {{EPIC_NUMBER}}     default: first segment of
                                              STORY_KEY before the first '-'
      --points             {{POINTS}}          default: TBD
      --predecessors       {{PREDECESSORS}}    default: TBD
      --schema-version     {{SCHEMA_VERSION}}  default: 1.0
      --prev-version       {{PREV_VERSION}}    default: N/A (for new primitives)
      --k-floor            {{K_FLOOR}}         default: TBD

Example (Story 31-3, Registries):

    python -m scripts.utilities.instantiate_schema_story_scaffold \\
        --story-key 31-3-registries \\
        --schema-name Registries \\
        --module-path marcus.registries \\
        --points 6 \\
        --predecessors 31-1,31-2 \\
        --k-floor 12

This writes 5 files (story spec pre-seed + schema.py + 3 contract tests),
prints the CHANGELOG snippet to stdout, and emits a summary listing each
written path. The dev agent then extends the stubs during ``bmad-dev-story``
rather than re-deriving from the 31-1 precedent.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo-relative paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD_ROOT = REPO_ROOT / "docs" / "dev-guide" / "scaffolds" / "schema-story"

# Template → target-path-pattern map. Target patterns use the derived-token
# substitutions. The story-spec target is chosen at runtime based on
# --spec-target (pre-seed vs authoritative).
TEMPLATES: list[dict[str, str]] = [
    {
        "template": "src/schema.py.tmpl",
        "target": "{RELATIVE_FILE_PATH}",
        "kind": "schema",
    },
    {
        "template": "src/digest.py.tmpl",
        "target": "{MODULE_PATH_AS_PATH}_digest.py",
        "kind": "digest",
    },
    {
        "template": "tests/test_shape_stable.py.tmpl",
        "target": "tests/contracts/test_{schema_name}_shape_stable.py",
        "kind": "test_shape",
    },
    {
        "template": "tests/test_json_schema_parity.py.tmpl",
        "target": "tests/contracts/test_{schema_name}_json_schema_parity.py",
        "kind": "test_parity",
    },
    {
        "template": "tests/test_no_intake_orchestrator_leak.py.tmpl",
        "target": "tests/contracts/test_no_intake_orchestrator_leak_{schema_name}.py",
        "kind": "test_facade",
    },
]

STORY_SPEC_TEMPLATE = "story-spec.md.tmpl"
STORY_SPEC_PRE_SEED_TARGET = (
    "_bmad-output/specs/pre-seed-drafts/{STORY_KEY}-PRE-SEED.md"
)
STORY_SPEC_AUTHORITATIVE_TARGET = (
    "_bmad-output/implementation-artifacts/{STORY_KEY}.md"
)

CHANGELOG_TEMPLATE = "CHANGELOG-entry.md.tmpl"


# ---------------------------------------------------------------------------
# Token derivation
# ---------------------------------------------------------------------------

_PASCAL_CASE_RE = re.compile(r"(?<!^)(?=[A-Z])")


def pascal_to_snake(pascal: str) -> str:
    """Convert PascalCase → snake_case.

    Examples:
        LessonPlanLog → lesson_plan_log
        SourceQualityReport → source_quality_report
        UUID4Token → uuid4_token  (acronyms kept intact — one boundary per
                                   transition to uppercase)
    """
    return _PASCAL_CASE_RE.sub("_", pascal).lower()


def derive_story_slug(story_key: str) -> str:
    """Derive human-readable slug from story key.

    Strips leading ``NN-N-`` prefix, replaces hyphens with spaces, title-cases.
    Example: ``31-2-lesson-plan-log`` → ``Lesson Plan Log``.
    """
    # Strip leading NN-N- or NN.N- prefix.
    stripped = re.sub(r"^\d+[-.]\d+[-.]", "", story_key)
    return stripped.replace("-", " ").title()


def derive_epic_number(story_key: str) -> str:
    """Pull the first numeric segment off the story key.

    Example: ``31-2-lesson-plan-log`` → ``31``.
    """
    match = re.match(r"^(\d+)", story_key)
    return match.group(1) if match else "TBD"


def module_path_to_relative_file(module_path: str) -> str:
    """Convert ``marcus.lesson_plan.log`` → ``marcus/lesson_plan/log.py``."""
    return module_path.replace(".", "/") + ".py"


def module_path_as_path(module_path: str) -> str:
    """Convert ``marcus.lesson_plan.log`` → ``marcus/lesson_plan/log`` (no ext)."""
    return module_path.replace(".", "/")


def build_token_map(args: argparse.Namespace) -> dict[str, str]:
    """Build the full {token: replacement} map from parsed CLI args."""
    schema_name_snake = pascal_to_snake(args.schema_name)
    story_slug = args.story_slug or derive_story_slug(args.story_key)
    epic_number = args.epic_number or derive_epic_number(args.story_key)

    return {
        # Required inputs
        "{{STORY_KEY}}": args.story_key,
        "{{SCHEMA_NAME}}": args.schema_name,
        "{{MODULE_PATH}}": args.module_path,
        # Derived
        "{{schema_name}}": schema_name_snake,
        "{{SCHEMA_NAME_UPPER}}": schema_name_snake.upper(),
        "{{RELATIVE_FILE_PATH}}": module_path_to_relative_file(args.module_path),
        "{{MODULE_PATH_AS_PATH}}": module_path_as_path(args.module_path),
        "{{DATE}}": datetime.now(UTC).strftime("%Y-%m-%d"),
        # Optional with defaults
        "{{STORY_SLUG}}": story_slug,
        "{{EPIC_NUMBER}}": epic_number,
        "{{POINTS}}": args.points,
        "{{PREDECESSORS}}": args.predecessors,
        "{{SCHEMA_VERSION}}": args.schema_version,
        "{{PREV_VERSION}}": args.prev_version,
        "{{K_FLOOR}}": args.k_floor,
    }


# ---------------------------------------------------------------------------
# Substitution + file writing
# ---------------------------------------------------------------------------


def substitute(text: str, tokens: dict[str, str]) -> str:
    """Replace every ``{{TOKEN}}`` occurrence in text with its mapped value.

    Ordered so that more-specific tokens substitute before less-specific
    substrings. Since all our tokens are distinct identifiers bracketed by
    ``{{`` and ``}}``, simple replace() suffices.
    """
    for token, value in tokens.items():
        text = text.replace(token, value)
    return text


def format_target_path(pattern: str, tokens: dict[str, str]) -> str:
    """Resolve a target-path pattern using the derived-token dictionary.

    Target patterns use unbracketed tokens (``{SCHEMA_NAME}``) because
    they're ``str.format``-style, whereas template bodies use
    ``{{SCHEMA_NAME}}``. We map from the ``{{TOKEN}}`` dict into the flat
    format-kwargs here.
    """
    format_kwargs = {
        key.strip("{}"): value for key, value in tokens.items()
    }
    return pattern.format(**format_kwargs)


def resolve_target_paths(
    tokens: dict[str, str],
    spec_target: str,
    include_digest: bool,
    include_story_spec: bool,
) -> list[dict[str, Path]]:
    """Return a list of {template_path, target_path, kind} dicts."""
    resolved: list[dict[str, Path]] = []

    # Story spec — target depends on --spec-target
    if include_story_spec:
        spec_pattern = (
            STORY_SPEC_AUTHORITATIVE_TARGET
            if spec_target == "authoritative"
            else STORY_SPEC_PRE_SEED_TARGET
        )
        resolved.append(
            {
                "template_path": SCAFFOLD_ROOT / STORY_SPEC_TEMPLATE,
                "target_path": REPO_ROOT / format_target_path(spec_pattern, tokens),
                "kind": "story_spec",
            }
        )

    # Schema + digest + tests
    for entry in TEMPLATES:
        if entry["kind"] == "digest" and not include_digest:
            continue
        resolved.append(
            {
                "template_path": SCAFFOLD_ROOT / entry["template"],
                "target_path": REPO_ROOT / format_target_path(entry["target"], tokens),
                "kind": entry["kind"],
            }
        )

    return resolved


def check_collisions(
    targets: list[dict[str, Path]],
    force: bool,
) -> list[Path]:
    """Return list of target paths that already exist.

    If ``force`` is True the list is still computed so caller can warn, but
    overwriting is allowed. If False, an occupied target is a hard error.
    """
    collisions = [t["target_path"] for t in targets if t["target_path"].exists()]
    return collisions


def write_files(
    targets: list[dict[str, Path]],
    tokens: dict[str, str],
    dry_run: bool,
) -> list[Path]:
    """Substitute every template and write to the target path.

    Creates parent directories as needed. Returns the list of paths written
    (or that would be written, in dry-run).
    """
    written: list[Path] = []

    for entry in targets:
        template_text = entry["template_path"].read_text(encoding="utf-8")
        rendered = substitute(template_text, tokens)

        target = entry["target_path"]
        if dry_run:
            print(f"[dry-run] would write {target.relative_to(REPO_ROOT)} "
                  f"({len(rendered)} bytes)", file=sys.stderr)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
            print(f"wrote {target.relative_to(REPO_ROOT)} "
                  f"({len(rendered)} bytes)", file=sys.stderr)
        written.append(target)

    return written


def render_changelog_snippet(tokens: dict[str, str]) -> str:
    """Render the CHANGELOG-entry template and return it for stdout paste."""
    template_text = (SCAFFOLD_ROOT / CHANGELOG_TEMPLATE).read_text(encoding="utf-8")
    return substitute(template_text, tokens)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="instantiate_schema_story_scaffold",
        description=(
            "Stamp the schema-story scaffold into canonical repo target paths. "
            "Compounds on schema-shape stories (31-3, 29-1, 32-2, and future "
            "equivalents). See docs/dev-guide/scaffolds/schema-story/README.md."
        ),
    )

    # Required
    parser.add_argument(
        "--story-key",
        required=True,
        help="Sprint-status key, e.g. 31-3-registries.",
    )
    parser.add_argument(
        "--schema-name",
        required=True,
        help="PascalCase model family root, e.g. Registries or LessonPlanLog.",
    )
    parser.add_argument(
        "--module-path",
        required=True,
        help="Python import path, e.g. marcus.registries or marcus.lesson_plan.log.",
    )

    # Optional with defaults
    parser.add_argument(
        "--story-slug",
        default="",
        help="Human-readable slug (default: derived from --story-key).",
    )
    parser.add_argument(
        "--epic-number",
        default="",
        help="Epic number (default: derived as first segment of --story-key).",
    )
    parser.add_argument("--points", default="TBD", help="Story points (default: TBD).")
    parser.add_argument(
        "--predecessors",
        default="TBD",
        help="Comma-separated predecessor story keys (default: TBD).",
    )
    parser.add_argument(
        "--schema-version",
        default="1.0",
        help="Initial SCHEMA_VERSION (default: 1.0).",
    )
    parser.add_argument(
        "--prev-version",
        default="N/A",
        help='Previous version for "since vX.Y" clauses (default: N/A).',
    )
    parser.add_argument(
        "--k-floor",
        default="TBD",
        help="K-floor (new-tests-added minimum) for the story (default: TBD).",
    )

    # Behavior toggles
    parser.add_argument(
        "--spec-target",
        choices=["pre-seed", "authoritative"],
        default="pre-seed",
        help=(
            "Where to write the story spec. 'pre-seed' (default) lands it at "
            "_bmad-output/specs/pre-seed-drafts/{STORY_KEY}-PRE-SEED.md to avoid "
            "collision with Cursor's authoritative bmad-create-story write. "
            "'authoritative' lands it at _bmad-output/implementation-artifacts/"
            "{STORY_KEY}.md — use ONLY if you are the authoritative author."
        ),
    )
    parser.add_argument(
        "--no-digest",
        action="store_true",
        help=(
            "Omit the digest.py stub (for stories with no canonical "
            "serialization surface, e.g. pure enum/registry shapes)."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Overwrite any existing target files. Without this flag, the "
            "script aborts if any target path is already occupied."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Print what would be written without modifying the filesystem. "
            "Useful for previewing token substitution."
        ),
    )
    parser.add_argument(
        "--skip-story-spec",
        action="store_true",
        help=(
            "Do not write the story-spec file. Useful when a non-authoritative "
            "pre-seed already exists and you only want scaffolded source / test files."
        ),
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # Sanity check on scaffold root.
    if not SCAFFOLD_ROOT.exists():
        print(
            f"ERROR: scaffold directory not found: "
            f"{SCAFFOLD_ROOT.relative_to(REPO_ROOT)}",
            file=sys.stderr,
        )
        return 2

    tokens = build_token_map(args)
    targets = resolve_target_paths(
        tokens,
        spec_target=args.spec_target,
        include_digest=not args.no_digest,
        include_story_spec=not args.skip_story_spec,
    )

    # Collision check
    collisions = check_collisions(targets, args.force)
    if collisions and not args.force:
        print(
            "ERROR: the following target paths already exist. "
            "Refusing to overwrite. Use --force to override.",
            file=sys.stderr,
        )
        for path in collisions:
            print(f"  - {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 3

    if collisions and args.force:
        print(
            "WARNING: --force specified; the following existing files will be "
            "overwritten:",
            file=sys.stderr,
        )
        for path in collisions:
            print(f"  - {path.relative_to(REPO_ROOT)}", file=sys.stderr)

    # Write files
    written = write_files(targets, tokens, args.dry_run)

    # Render CHANGELOG snippet
    changelog_snippet = render_changelog_snippet(tokens)

    # Summary
    print("", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    if args.dry_run:
        print(f"DRY-RUN SUMMARY for story {args.story_key}", file=sys.stderr)
    else:
        print(f"INSTANTIATION SUMMARY for story {args.story_key}", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    print(f"Files written (or would-be, in dry-run): {len(written)}", file=sys.stderr)
    for path in written:
        print(f"  - {path.relative_to(REPO_ROOT)}", file=sys.stderr)

    print("", file=sys.stderr)
    print(
        "CHANGELOG entry follows on stdout. Paste it into "
        "_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md under a new "
        "heading (one entry per shape family per R2 AM-1 / 31-1).",
        file=sys.stderr,
    )
    print("", file=sys.stderr)

    # The changelog snippet is the ONLY thing on stdout — makes it easy to
    # pipe to pbcopy / xclip / etc.
    print(changelog_snippet)

    if args.spec_target == "pre-seed" and not args.skip_story_spec:
        print("", file=sys.stderr)
        print(
            "NOTE: story spec written as pre-seed. Cursor's bmad-create-story "
            "will write the authoritative spec at "
            f"_bmad-output/implementation-artifacts/{args.story_key}.md. "
            "The pre-seed is input material for that authoring pass, not "
            "authoritative.",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
