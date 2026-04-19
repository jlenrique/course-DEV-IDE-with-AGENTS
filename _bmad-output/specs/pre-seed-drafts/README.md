# Pre-seed drafts

**Purpose.** This directory holds **non-authoritative pre-seed skeletons** for BMAD
stories — mid-flight input material produced by one workflow session to save cycle
time for a subsequent, authoritative authoring pass run via the real
`bmad-create-story` workflow.

## Why this directory exists

The real `bmad-create-story` skill writes authored story specs to
`_bmad-output/implementation-artifacts/{story_key}.md`. If a Cowork-side session
pre-fills a story skeleton at that target path before Cursor runs
`bmad-create-story` as Amelia, the Cursor-side write will collide with or overwrite
the pre-seed. Relocating pre-seeds here keeps the implementation-artifacts/
directory clean for the authoritative specs and avoids accidental mixing of
neutral-voice skeletons with real Amelia-authored BMAD specs.

## What belongs here

- Skeletons authored in any voice other than the real Amelia-via-`bmad-create-story`
  path (for example, neutral orchestrator voice from a Cowork-side session).
- Architecture sketches, AC candidates, T-task candidates, file-impact tables, and
  K-floor proposals assembled from plan documents and precedent stories, intended
  to be consumed as input material by the authoritative authoring run.
- Mid-flight memos pointing the downstream authoring session at relevant dev-guide
  references (checklists, anti-patterns catalogs, scaffolds).

## What does NOT belong here

- Authoritative story specs (those land in `_bmad-output/implementation-artifacts/`).
- R2-reviewed specs (those are authoritative).
- Specs with a sprint-status.yaml entry pointing to them as the active target.

## Naming convention

`{story-key}-PRE-SEED.md` — the `-PRE-SEED` suffix makes the non-authoritative
nature unambiguous to any reader, automated or human.

## Lifecycle

1. Pre-seed lands here with a prominent `⚠️ PRE-SEED DRAFT — NOT AUTHORITATIVE ⚠️`
   banner at the top.
2. Cursor + Claude-Code side runs `bmad-create-story` as Amelia, producing the
   authoritative spec at `_bmad-output/implementation-artifacts/{story-key}.md`.
3. The pre-seed becomes historical reference only. It may be deleted at the
   authoring session's discretion, or retained as a "what the Cowork side
   proposed" breadcrumb for the story retrospective.
4. Sprint-status.yaml authority for the story is driven by the authoritative spec
   at the implementation-artifacts/ path, never by the pre-seed here.

## Relationship to scaffolds

Pre-seeds are **story-specific** — one pre-seed per story. Scaffolds
(`docs/dev-guide/scaffolds/`) are **story-class templates** — one scaffold per
recurring story shape (for example, the schema-story scaffold covers 31-3, 29-1,
32-2). Pre-seeds may cite the scaffold they build on; scaffolds do not cite
pre-seeds.

## Current contents

See filesystem listing. Each pre-seed carries its own banner at the top with its
relocation history, the authoritative-path pointer, and the reason it was
produced as a pre-seed rather than authored via `bmad-create-story` directly.
