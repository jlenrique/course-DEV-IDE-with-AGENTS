# Schema-Story Scaffold

Repeatable file-structure recipe for a schema-shape story whose core deliverable
is a Pydantic v2 model family, emitted JSON Schema, and contract tests.

## When to use it

Use this scaffold when the story needs:
- a new Pydantic model family
- an emitted JSON Schema artifact
- shape-pin contract tests
- a `SCHEMA_CHANGELOG.md` entry

If the story is pure refactor or orchestration, use only the pieces that help.

## What it buys you

The scaffold front-loads the repeated structure from `31-1` and `31-2`:
- Pydantic v2 idioms already wired into the module stub
- contract test shells in canonical paths
- pre-seed story spec generation without stealing the authoritative write path
- a standard changelog snippet for schema-version work

## Existing pre-seed workflow

If a non-authoritative pre-seed already exists at
`_bmad-output/specs/pre-seed-drafts/{STORY_KEY}-PRE-SEED.md`, run:

```bash
python -m scripts.utilities.instantiate_schema_story_scaffold \
  --story-key <story-key> \
  --schema-name <SchemaName> \
  --module-path <module.path> \
  --skip-story-spec
```

That preserves the pre-seed while still generating the source and test scaffold.

## Dormant-by-default tests

Generated contract tests now include a module-level `pytest.mark.skip`. That is
intentional. The scaffold should create useful placeholders without breaking the
suite before the authoritative story pass fills in:
- real allowlists
- the committed schema artifact path
- story-specific no-leak scan targets

During the real story implementation, remove the scaffold skip from each test
module as soon as the file becomes story-real.

## What the scaffold does not do

- It does not write story-specific acceptance criteria.
- It does not decide the story's T1 readiness details.
- It does not activate the generated tests for you.
- It does not design the real schema body.

## Governance

- Treat scaffold edits as high-leverage changes because they propagate forward.
- When a new Pydantic v2 pitfall is found at G5/G6, update both the scaffold
  and `docs/dev-guide/pydantic-v2-schema-checklist.md`.
- The placeholder token vocabulary is effectively frozen; changing it requires
  coordinated updates across the bundle.
