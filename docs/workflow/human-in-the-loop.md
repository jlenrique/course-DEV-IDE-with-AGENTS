# Human-in-the-loop: “vibe” course authoring

Goal: you stay the instructor of record; agents draft and refactor; you approve before students see anything.

## Stages

1. **Intent** — You describe outcomes, week structure, and constraints (time, modality, platform). Agents use `resources/style-bible/master-style-bible.md` as authoritative standards, with `config/content-standards.yaml` as fallback defaults.
2. **Draft in staging** — Agents write under `course-content/staging/<short-label>/` (e.g. `staging/m03-intro-ai/`). No direct edits to published `courses/` until you promote.
3. **Your pass** — You edit for accuracy, examples, and policy. Optionally run editorial / adversarial review skills on the staged path.
4. **Promote** — Move or copy approved material into `course-content/courses/<course-slug>/module-XX/...`.
5. **Publish** — Run or follow `integrations/canvas/` (or CourseArc export + LTI) procedures. Treat first module as a **smoke test** in Canvas preview/student view.

## Minimal conventions

- One folder per module under `courses/<course-slug>/module-NN-topic/`.
- `lessons/` for narrative Markdown; `presentations/` for slide source (Marp `.md`, reveal, or exported PDF/HTML notes in git if small).
- `assets/` for images, diagrams; large binaries can live in `course-content/courses/.../private/` (gitignored) if needed.

## When to branch git

- **Branch**: new module or risky rework. **Merge**: after your HIL sign-off on staging → courses promotion.

## Definition of done (per lesson or deck)

- [ ] Learning objectives stated and aligned to activities.
- [ ] You personally verified facts and institution-specific policy.
- [ ] Accessibility checklist from `content-standards.yaml` considered.
- [ ] Visible in target platform (Canvas page / LTI link) in preview mode.

## Production Checkpoints (Anti-Drift)

For tracked/default production prompt-pack runs, enforce these checkpoints in order:

1. Gate 1 approval after Irene Pass 1 artifacts.
2. Prompt 6B literal-visual operator packet and readiness confirmation before any Gary dispatch side effects.
3. Storyboard A review after Gary dispatch output, before Gate 2 approval.
4. Gate 2 approval before Irene Pass 2 delegation.
5. Storyboard B review after Irene Pass 2 script/manifest output, before downstream audio/script finalization.

These checkpoints are deterministic safeguards against fidelity drift between slide intent, generated visuals, and final narration/audio outputs.
