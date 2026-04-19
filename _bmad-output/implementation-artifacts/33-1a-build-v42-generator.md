# Story 33-1a: Build v4.2 Generator from Scratch — Jinja2 Template-Driven

**Status:** done
**Created:** 2026-04-19 (skeleton); fully scoped 2026-04-19 (party-mode SCOPE round unanimous on approach + prose source-of-truth + determinism contract)
**Epic:** 33 — Pipeline Lockstep Substrate
**Sprint key:** `33-1a-build-v42-generator`
**Branch:** `dev/epic-33-lockstep` (continued from 33-2)
**Points:** 5
**Depends on:** 33-1 (done — findings report landed Case C), 33-2 (done — manifest + L1 check + consumer rewires; provides the manifest the generator will consume)
**Blocks:** 33-3 (regeneration cannot run until generator exists), 33-4 (depends on 33-3), 15-1-lite-marcus (depends on 33-4)
**Governance mode:** **single-gate** per Murat's determinism-math ruling (Jinja2 approach = low-flakiness-risk class; single-review sufficient). Post-dev three-layer `bmad-code-review` (Blind + Edge + Auditor) is the sole review ceremony. Epic 33 out of Lesson Planner MVP scope; Lesson Planner governance validator does NOT apply; BMAD sprint governance per [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance binds.

## Scope Precondition — Resolved

Story 33-1 findings landed Case C: no in-repo generator of record for v4.2. Per the 33-1 kill-switch escalation path, this story was initially `blocked-on-party-mode-scope` until a party-mode round ratified approach + prose source + determinism contract + ownership + point estimate. **That round completed 2026-04-19 with unanimous (4-0) consensus from Winston, Amelia, Paige, Murat.** Votes recorded in §R1 Scope Resolutions below.

## TL;DR

- **What:** Build a **pure Jinja2, pure deterministic, NO-LLM-ANYWHERE-IN-CRITICAL-PATH** v4.2 prompt-pack generator at [`scripts/generators/v42/`](../../scripts/generators/v42/). The generator reads [`state/config/pipeline-manifest.yaml`](../../state/config/pipeline-manifest.yaml) (landed by 33-2) + a Jinja2 template tree at `scripts/generators/v42/templates/` and emits `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`. Template source is the existing hand-curated 1368-line pack **extracted verbatim into per-section templates** (prose-preservation discipline per Paige's D-3 ruling). Manifest controls structure/order/inclusion; templates own prose content. In-scope: authoring the §4.55 "Estimator + Run Constants Lock" body fresh (new section split from §4.5 per 33-1 addendum A-2 — no pre-existing prose exists). Deliverables land with the full determinism acceptance test set (Murat's AC-T.1-T.4 + 3 red-path fixtures) + authored fixture pair (`manifest_fixture.yaml` + `pack_sha_fixture.txt` + `expected_pack/`) that 33-3 AC-C.1 consumes.
- **Why:** The Epic 33 substrate (33-2 manifest + L1 check) was landed on the premise of a generator that did not exist. 33-1 surfaced Case C; 33-2 deferred AC-B.15 rewire; 33-1a closes the gap. The Jinja2 approach was chosen over LLM-driven (b) and hybrid (c) on four converging grounds: (i) determinism by construction (Murat: "flakiness risk class = 0"); (ii) operator constraint "v4.2 is generated, should always be" means GENERATED not SYNTHESIZED (Winston); (iii) preserves 1368 lines of earned, curated operator-facing prose (Paige: "that's a D-3 concern — solved by (iii) preserve verbatim"); (iv) Cora's 33-4 block-mode hook retains maximum signal-to-noise under (a) vs a 40-60% likelihood of being disabled by false-positive model-drift storms under (b)/(c) (Murat: "the flakiness risk class I'd reject at Lesson Planner MVP gate"). 33-1a delivers both the machinery and the ratification fixtures the 33-2 DEFER rider made load-bearing.
- **Done when:** (1) `scripts/generators/v42/` package lands with `render.py` (CLI + module entry), `manifest.py` (manifest loader wrapping 33-2's Pydantic shape), `templates/` (Jinja2 root); (2) all 32 existing v4.2 section bodies extracted verbatim into `templates/sections/<id>.md.j2` files with zero semantic change; (3) §4.55 "Estimator + Run Constants Lock" template authored fresh with Marcus-operator-flow-reviewed prose; (4) `templates/partials/tldr_crosswalk.md.j2` auto-derives the §0 TL;DR table from manifest sections + HUD IDs + module map; (5) `templates/partials/provenance_appendix.md.j2` auto-emits section provenance footer; (6) audience tags `[M→self] / [O→M] / [M→O] / [M→sub]` authored inline per template (Paige's "prose-level annotation living with the prose it annotates" rule); (7) Jinja2 environment pinned for cross-platform determinism (`keep_trailing_newline=True`, `newline_sequence='\n'`, `trim_blocks` / `lstrip_blocks` explicit); (8) YAML loader uses sorted-keys discipline (Amelia's dict-iteration-order trap); (9) `jinja2>=3.1,<4` added to `requirements.txt`; (10) manifest extended with per-section `rationale:` field feeding the provenance appendix; (11) determinism acceptance test set AC-T.1-T.4 + 3 red-path fixtures (R1/R2/R3) + 33-3-consumption fixture pair all land in `tests/generators/v42/fixtures/`; (12) K=6 floor cleared at 8-12 collecting functions; (13) single-gate post-dev `bmad-code-review` layered pass; (14) sprint-status flipped `ready-for-dev → in-progress → review → done`.
- **Scope discipline:** 33-1a ships **zero LLM calls, zero prompt templates, zero cache infrastructure, zero body-content regeneration from first principles**. If a template's prose feels stale or imprecise, the fix is a template edit in a follow-on (or a template PR under the normal review process), NOT an LLM rewrite. 33-1a ships **zero edits to `state/config/pipeline-manifest.yaml`'s core field set** (that's 33-2's scope); the only manifest change is adding per-section `rationale:` fields (additive; loader validates presence as optional). 33-1a ships **zero hand-edits to `docs/workflow/production-prompt-pack-v4.2-*.md`** — the dev agent does NOT invoke the generator against the real v4.2 target in this story (that's 33-3 AC-B.3); verification runs against fixture-manifests only. If regenerating v4.2 against the real manifest would make the L1 check exit 0, that's valuable info, but it's 33-3's moment to capture, not 33-1a's.

## Story

As the **Epic 33 sprint — on the hook to deliver a self-enforcing pipeline lockstep substrate**,
I want **a pure-deterministic Jinja2-template-driven generator that regenerates v4.2 byte-identically from the manifest + templates, with the existing 1368 lines of curated prose preserved verbatim in templates and a fresh §4.55 lock-section body authored in-story**,
So that **33-3 can regenerate the real v4.2 against its AC-C.1 byte-identity guard; 33-4's Cora block-mode hook has a high-signal-to-noise substrate to protect (not a model-drift-storm generator that gets silenced within two quarters); and 15-1-lite-marcus's meta-test runs against a real, working substrate — not a fixture-only shim pretending to be one**.

## Background — Why This Story Exists

The operator's original Epic 33 sprint plan assumed a generator existed somewhere. **Story 33-1 discovered Case C — no generator of record, pack is de-facto hand-authored despite the "v4.2 is generated, should always be" constraint.** Story 33-2 proceeded on the substrate (manifest + L1 check + consumer rewires) but correctly DEFERRED AC-B.15 (generator rewire) because there was nothing to rewire. The 33-2 DEFER sign-off landed unanimous YES-WITH-RIDER; rider synthesis: **"33-1a must ratify ownership/contract/determinism acceptance tests before 33-3 opens."**

The 2026-04-19 SCOPE party-mode round voted 4-0 on approach (a) Jinja2 template-driven. Reasoning converges on four points:

1. **Winston** — operator constraint "v4.2 is generated, should always be" is satisfied by GENERATED (Jinja2 render), not SYNTHESIZED (LLM). Boring technology wins; templates carry prose verbatim; prose edits become template PRs (reviewable diffs).
2. **Amelia** — AC-C.1 byte-identity is native under Jinja2; LLM approach requires seed+cache+model-version-pin infrastructure that doesn't exist and would be scope explosion. Cleanest dep footprint (just `jinja2>=3.1,<4`; no LLM SDKs).
3. **Paige (D-3 load-bearing)** — the 1368 lines of curated prose are earned capital; regenerating from first principles destroys the investment. **Option (iii) "preserve verbatim as templates + manifest-for-structure-only"** makes the contract explicit and enforceable: six months from now when someone proposes "just let the LLM rewrite §4.5 to match the new manifest," there's a principle to point at. §4.55 body gets authored fresh in-story (not deferred) because a pack that emits empty-bodied sections on first run is a worse failure mode than slipping the story.
4. **Murat (D-2 determinism lane)** — under Jinja2, Cora's 33-4 block-mode hook has infinity signal-to-noise (drift = real change). Under LLM approaches, estimated 40-60% probability of the hook being disabled by false-positive model-drift storms within two quarters of ship. **That's the flakiness risk class rejected at Lesson Planner MVP gate reviews.** Applies equally here.

**Why 5 points (not 3 or 8):** Amelia's breakdown ratifies the distribution — 2pt template extraction from 1368 lines (mechanical but careful section-boundary calls), 1pt manifest-loader + Jinja2 harness, 1pt render loop + macros + §4.55 fresh authoring, 1pt three test suites (determinism, ownership, contract) to satisfy the rider. 3pt undercounts the template-extraction carefulness; 8pt would apply only if approach (c) hybrid were forced (it wasn't).

**Why single-gate (not dual-gate):** Murat's D-4 ruling — under approach (a), K ≈ 1.3-1.5, single-review is sufficient given the determinism-by-construction shape. Approach (b)/(c) would have mandated dual-gate; the unanimous vote on (a) removes that requirement. The design decisions are already resolved by the 2026-04-19 SCOPE round; R1/R2 ceremony here would be re-litigation.

## R1 Scope Resolutions (2026-04-19 party-mode round)

Recording here so dev agent does not re-open closed decisions:

### R1-33-1a-A — Generator approach: **(a) Jinja2 template-driven, UNANIMOUS 4-0**

- Winston: H-confidence. "Boring technology wins here. Templates carry prose verbatim, so prose edits become template PRs rather than prompt tweaks. That's a feature, not a bug."
- Amelia: H-confidence. "Pure Jinja2 = deterministic by construction, reviewable diffs, no model-version drift."
- Paige: H-confidence with narrow escape hatch. "A tiny `{% include %}` seam for auto-derived tables (TL;DR crosswalk, audience-tag index) so those stay generator-emitted without forcing the body prose through an LLM."
- Murat: H-confidence. "The risk math is lopsided. (a) = L flakiness / L determinism-test-burden / L maintenance."

**Settled**: pure Jinja2, no LLM in critical path, narrow `{% include %}` seam for auto-derived cross-cutting tables.

### R1-33-1a-B — Prose source-of-truth: **(iii) verbatim templates + manifest-for-structure-only, UNANIMOUS 4-0**

Paige (D-3 primary voice): "The v4.2 pack is 1368 lines of *earned* prose — curated across multiple review rounds, calibrated for the specific operator audience, cross-referenced with HUD strings and code modules. Option (ii) regenerates from first principles and throws that investment away on every run... Option (iii) makes the contract explicit and enforceable."

**Settled**: existing 32 pack sections extract verbatim into `templates/sections/<id>.md.j2`; manifest controls section structure/order/inclusion only; generator's job is structure, prose edits happen by editing templates.

### R1-33-1a-C — §4.55 body authoring: **in-scope for 33-1a (Paige Q1 non-negotiable)**

Paige: "A pack that emits an empty-bodied section on first run is a worse failure mode than slipping the story." Authoring lane: Paige-role prose (dev agent channels per [skills/bmad-agent-tech-writer/SKILL.md](../../skills/bmad-agent-tech-writer/SKILL.md)), Marcus-role operator-flow review (dev agent channels per [skills/bmad-agent-marcus/SKILL.md](../../skills/bmad-agent-marcus/SKILL.md)), dev agent lands the template file. Raw material: 33-1 addendum A-2 declarations (what "lock" means, why split from polling, HUD strings the section owns) + existing §4.5 polling template as structural sibling.

**Settled**: `templates/sections/04.55-estimator-run-constants-lock.md.j2` lands in 33-1a with a Marcus-operator-flow-reviewed lock-semantic body.

### R1-33-1a-D — Determinism contract: **Murat's AC-T.1-T.4 + 3 red-path fixtures, UNANIMOUS 4-0**

Murat (D-2 primary voice): "Under approach (a), AC-T.1-T.4 is the floor. AC-T.1 SHA round-trip; AC-T.2 5x-consecutive byte-identity; AC-T.3 schema conformance via 33-2's L1; AC-T.4 manifest-perturbation diff. 4 tests. All fast. All deterministic by construction. This is the floor."

Red-path fixtures R1 (missing section), R2 (reordered sections), R3 (field-mutation-ignored-by-generator) — all authored in 33-1a per Murat Q3 ruling.

**Settled**: determinism test set + red-path fixtures land in 33-1a; `fixtures/33-1a/manifest_fixture.yaml` + `fixtures/33-1a/pack_sha_fixture.txt` + `fixtures/33-1a/expected_pack/` are the ratification artifacts 33-3 AC-C.1 consumes.

### R1-33-1a-E — Module location: **`scripts/generators/v42/` (3-1 majority; operator tiebreak endorsed)**

Winston + Amelia + orchestrator: `scripts/generators/v42/` sibling to `scripts/utilities/` matches existing substrate convention; dev-agent mental model consistency; clean parallel namespace for future `scripts/generators/v43/`.

Paige (minority): `packs/generator/` "adjacent to its outputs." Minority rationale preserved in Dev Agent Record; not carried.

**Settled**: `scripts/generators/v42/` with `templates/`, `macros/`, `partials/` subtrees co-located.

### R1-33-1a-F — Ownership lane: **neutral build-tool (3-0 among voices who addressed)**

Not Marcus-adjacent (Marcus consumes v4.2 at runtime, doesn't own regeneration); not Audra-adjacent (Audra is VO/narration lane); not any persona's skill tree. Lives under `scripts/generators/` the same way `scripts/utilities/` is lane-neutral substrate. Dev agent executes.

**Settled**: neutral build-tool lane; dev agent executes; no SKILL edits required in 33-1a (unlike 33-4 which updates Cora + Audra SKILLs).

## T1 Readiness

- **Gate mode:** `single-gate` per R1-33-1a-A ruling. Post-dev three-layer `bmad-code-review` (Blind + Edge + Auditor) is the sole review ceremony.
- **K floor:** `K = 6` per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 for a 5pt single-gate story with ~4 distinct subsystems (loader, renderer, template tree, test harness). Derivation: 4 determinism acceptance tests (AC-T.1-T.4), 3 red-path fixtures as parametrized tests (3 cases), 1 template-extraction-coverage test (all 32 existing sections have templates), 1 audience-tag-presence test, 1 manifest-rationale-field shape-pin, 1 §4.55-template-body-non-empty test. Sum: 11; floor set at 6 for coverage-gap justification per §1.
- **Target collecting-test range:** 8–12 (1.3×K to 2×K per §1 footnote on generator/extraction stories).
- **Realistic landing estimate:** 10-12 at T2-T6 close; +1-2 possible at G6 remediation.
- **Required readings** (dev agent reads at T1 before any code):
  - [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance.
  - [_bmad-output/implementation-artifacts/33-1-generator-discovery.md](33-1-generator-discovery.md) — especially §Post-Close R1 Addendum (A-2 04.5/04.55 split rationale); findings at [_bmad-output/specs/33-1-generator-discovery-findings.md](../specs/33-1-generator-discovery-findings.md) (if materialized at 33-1 close).
  - [_bmad-output/implementation-artifacts/33-2-pipeline-manifest-ssot.md](33-2-pipeline-manifest-ssot.md) — §R1 Resolutions for manifest shape; §AC-B block for the loader contract 33-1a extends with the `rationale:` field.
  - [_bmad-output/implementation-artifacts/33-3-regenerate-v42-and-validate.md](33-3-regenerate-v42-and-validate.md) — especially AC-C.1 byte-identity contract 33-1a's fixtures must satisfy.
  - [_bmad-output/implementation-artifacts/33-4-cora-audra-block-mode.md](33-4-cora-audra-block-mode.md) — context on why Cora's hook signal-to-noise drives the approach vote.
  - [docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](../../docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md) — the 1368-line source for template extraction. Dev agent reads cover to cover before starting extraction.
  - [state/config/pipeline-manifest.yaml](../../state/config/pipeline-manifest.yaml) (from 33-2) — the manifest the generator consumes. Note the 04.5 + 04.55 entries (R1-A split from 33-2) that drive §4.55 fresh authoring.
  - [scripts/utilities/pipeline_manifest.py](../../scripts/utilities/pipeline_manifest.py) (from 33-2) — the Pydantic loader 33-1a wraps / extends with `rationale:` field.
  - [scripts/utilities/check_pipeline_manifest_lockstep.py](../../scripts/utilities/check_pipeline_manifest_lockstep.py) (from 33-2) — the L1 check AC-T.3 invokes on generated pack.
  - [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) — **27-2** (hand-edit) extended in spirit to "do not LLM-edit templates"; **31-1** (rename-one-surface) — template edits are the paired artifact for manifest edits, not a post-hoc reconciliation.
  - [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 / §2 / §3.
  - **Jinja2 3.x documentation** — specifically the `Environment()` configuration options for cross-platform determinism (`keep_trailing_newline`, `newline_sequence`, `trim_blocks`, `lstrip_blocks`, `autoescape` posture).
- **Scaffold requirement:** `require_scaffold: false` — this is a generator-build story, not a Pydantic-model story.
- **Runway pre-work consumed:** all of 33-1 + 33-2. If 33-2's manifest loader was shipped without a hook for adding the `rationale:` field (33-2 AC-B.3 declared per-step fields; rationale was not in that list), 33-1a opens by extending the Pydantic model — that's an in-scope 33-2 extension, not a separate story.

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — `scripts/generators/v42/` package created.** Package layout:
   ```
   scripts/generators/v42/
   ├── __init__.py                           # package marker
   ├── render.py                             # CLI entry + main render function
   ├── manifest.py                           # manifest loader wrapping scripts/utilities/pipeline_manifest.py with rationale-field extension
   ├── env.py                                # Jinja2 Environment factory with pinned determinism config
   ├── templates/
   │   ├── sections/                         # one .md.j2 file per manifest-declared section
   │   │   ├── 01-activation-preflight.md.j2
   │   │   ├── 02-source-authority-map.md.j2
   │   │   ├── 02A-operator-directives.md.j2
   │   │   ├── 03-ingestion-evidence-log.md.j2
   │   │   ├── 04-ingestion-quality-gate.md.j2
   │   │   ├── 04A-lesson-plan-coauthoring.md.j2
   │   │   ├── 04.5-parent-slide-count-polling.md.j2      # R1-A split — existing §4.5 prose
   │   │   ├── 04.55-estimator-run-constants-lock.md.j2   # R1-A split — FRESH authoring per R1-33-1a-C
   │   │   └── ... (all 32 existing sections + new 04.55)
   │   ├── partials/
   │   │   ├── tldr_crosswalk.md.j2          # auto-derived from manifest + HUD-ID + module map
   │   │   └── provenance_appendix.md.j2     # auto-emitted footer citing per-section rationale
   │   ├── macros/
   │   │   └── audience_tag.j2               # [M→self] / [O→M] / [M→O] / [M→sub] rendering helper
   │   └── layout/
   │       └── pack.md.j2                    # top-level layout wiring sections + partials
   ```
   `__init__.py` exposes `render_pack(manifest_path, output_path) -> None` and a `__version__` const.

2. **AC-B.2 — Manifest loader extended with `rationale:` field.** [`scripts/utilities/pipeline_manifest.py`](../../scripts/utilities/pipeline_manifest.py) (from 33-2) extended: each `StepEntry` gains `rationale: str | None = Field(default=None, description="One-line machine-readable justification for this section's existence; feeds provenance appendix.")`. Additive only; no existing field behavior changes. 33-2's AC-C.5 disjoint-keys check continues to pass (new field lives inside existing `steps` block).

3. **AC-B.3 — Jinja2 Environment pinned for cross-platform determinism.** `scripts/generators/v42/env.py::make_env()` returns a `jinja2.Environment` configured with:
   - `loader = FileSystemLoader("scripts/generators/v42/templates")`
   - `autoescape = False` (Markdown output, not HTML)
   - `keep_trailing_newline = True`
   - `newline_sequence = "\n"` (LF only; no CRLF drift between Windows dev box and Linux CI)
   - `trim_blocks = True`, `lstrip_blocks = True` (pinned explicitly — Amelia's dict-iteration-style trap)
   - `undefined = StrictUndefined` (any undefined variable raises immediately; no silent empty renders)
   - `optimized = True` (precompile templates for performance; also for determinism — all runs use the same optimized AST)

4. **AC-B.4 — Template extraction: all 32 existing v4.2 sections extracted verbatim.** Every `## N)` or `## NN.N)` section in the current on-disk v4.2 pack has a corresponding `templates/sections/<id>.md.j2` file. Template content is the section's body **byte-identical to the source** (whitespace preserved; trailing newlines preserved; embedded backticks/YAML blocks/code fences preserved). Section headers (`## N) Name`) are emitted by `layout/pack.md.j2` from manifest data, NOT by the individual section templates (separation of structure vs prose). Templates may contain Jinja2 expression syntax **only** for (a) audience-tag macro calls, (b) cross-reference interpolation if the template references another manifest step's ID — everything else is literal prose.

5. **AC-B.5 — §4.55 body authored fresh (R1-33-1a-C non-negotiable).** `templates/sections/04.55-estimator-run-constants-lock.md.j2` lands with a complete body covering at minimum:
   - What "Estimator + Run Constants Lock" gates in the pipeline (downstream emission cannot proceed until this lock succeeds)
   - How it differs semantically from §4.5 (polling is a precursor observation; 04.55 is a one-shot transactional lock that gates subsequent plan_unit.created events per `loop.py` runtime behavior)
   - Operator-facing guidance: what to check if the lock fails, what artifacts appear when it succeeds
   - HUD string contract: what 04.55 displays on the operator HUD (manifest carries the canonical string; body text documents it)
   - Audience tags `[M→self]` on lock-internal reasoning; `[M→O]` on any operator-facing prompts at this gate
   
   Style matches the existing §4.5 template as structural sibling. Dev agent does NOT treat this as an LLM-ghostwriting task; prose is authored by dev agent channeling Paige's tech-writer lane + Marcus's operator-flow-review lane explicitly (write, review, iterate). Commit to the template file; do NOT defer to a follow-on story.

6. **AC-B.6 — TL;DR crosswalk partial auto-derives from manifest + HUD-ID + module map.** `templates/partials/tldr_crosswalk.md.j2` renders the §0 crosswalk table Paige recommended in her earlier party-round position: columns `Pack §` | `HUD id` | `Marcus module` | `Audience` | `One-line purpose`. Rows are auto-generated from the manifest's sections list + cross-referenced to `scripts/utilities/run_hud.py::PIPELINE_STEPS` ids (manifest-sourced since 33-2) + manifest-declared module paths. One row per top-level section; sub-phases (sections with `sub_phase_of` non-null) are indented under their parent row. **Generator-emitted; never hand-maintained.**

7. **AC-B.7 — Provenance appendix auto-emitted.** `templates/partials/provenance_appendix.md.j2` renders a per-section footer at pack bottom listing: `§<id>` | `<rationale from manifest>` | `<originating story/addendum citation>`. Sections without a `rationale:` value are omitted from the appendix (not listed as "N/A"). The §4.55 entry cites "Split from §4.5 per 33-1 addendum A-2 (R1-A L1-lane tiebreak on Principle-1 test-integrity — Audra 2026-04-19)." Future editors asking "why is lock a separate section?" find the answer in the pack itself.

8. **AC-B.8 — Audience tags authored inline per template (macro-expanded).** Audience tags `[M→self]` / `[O→M]` / `[M→O]` / `[M→sub]` appear inline in each template's prose where applicable, rendered via the `macros/audience_tag.j2` macro (call shape: `{{ audience("M→O") }}` or similar). Macro ensures consistent formatting; prose-level placement is author's call. At least one audience tag exists per section template that has operator-facing prompts (grep invariant in contract test).

9. **AC-B.9 — Render function byte-identical on same manifest.** `scripts/generators/v42/render.py::render_pack(manifest_path, output_path)` reads manifest, renders layout + sections + partials via Jinja2 env, writes to `output_path`. Same manifest + same templates + pinned Jinja2 env → byte-identical output across runs. CLI entry `python -m scripts.generators.v42.render --manifest state/config/pipeline-manifest.yaml --output <path>` works; with `--output docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` would write the real pack (but 33-1a does NOT invoke this against the real path; that's 33-3 AC-B.3).

10. **AC-B.10 — `jinja2>=3.1,<4` dependency pinned.** `requirements.txt` (or `pyproject.toml` if that's the project's canonical dep surface) adds `jinja2>=3.1,<4`. No other new dependencies. Explicitly NO: `openai`, `anthropic`, `langchain`, `markdown-it-py`, `diskcache`, any LLM SDK, any caching library.

11. **AC-B.11 — Ratification fixture pair lands.** `tests/generators/v42/fixtures/` contains:
    - `manifest_fixture.yaml` — a minimal manifest covering ≥3 sections (one plain, one with `sub_phase_of`, one with `insertion_after`) with `rationale:` populated on each
    - `expected_pack/fixture_pack.md` — the expected byte-identical generator output against `manifest_fixture.yaml` at 33-1a close
    - `pack_sha_fixture.txt` — SHA-256 of `expected_pack/fixture_pack.md` with `sha256:<hex>` format + a `# generated_at: <commit>` comment line
    
    These are the 33-2-DEFER-rider ratification artifacts. 33-3 AC-C.1 consumes this pair.

12. **AC-B.12 — YAML loader uses sorted-keys discipline.** `scripts/generators/v42/manifest.py` sorts dict keys at load time (or wraps 33-2's Pydantic loader so iteration order is stable). Amelia's trap: dict iteration order in Python 3.7+ is insertion-ordered, but YAML loaders vary. Explicit `sorted()` pass on any field that feeds a `{% for %}` loop in templates.

### Contract (AC-C.*)

1. **AC-C.1 — No-LLM-imports guard.** One contract test at `tests/contracts/test_33_1a_no_llm_imports.py::test_generator_has_no_llm_sdk_imports` AST-walks `scripts/generators/v42/`; asserts zero imports of `openai`, `anthropic`, `langchain`, `transformers`, or any module matching `llm`/`gpt`/`claude`/`bedrock`. R1-33-1a-A "no LLM in critical path" rendered as grep-invariant; catches future silent re-introduction.

2. **AC-C.2 — Jinja2 env config pinned.** One contract test at `tests/contracts/test_33_1a_jinja_env_pinned.py` asserts `env.py::make_env()` returns an env with the 7 AC-B.3 config values exactly. Protects against a future refactor changing `keep_trailing_newline` or `newline_sequence` and silently breaking determinism.

3. **AC-C.3 — Template extraction completeness.** One contract test at `tests/contracts/test_33_1a_template_coverage.py::test_all_manifest_sections_have_templates` asserts every section id in `state/config/pipeline-manifest.yaml` has a corresponding `templates/sections/<id>.md.j2` file. Also asserts no orphan templates (every `.md.j2` in `templates/sections/` has a manifest entry).

4. **AC-C.4 — Verbatim extraction invariant.** One contract test at `tests/contracts/test_33_1a_verbatim_extraction.py::test_existing_sections_match_source_pack_byte_identical` loads each `templates/sections/<id>.md.j2` EXCEPT `04.55-estimator-run-constants-lock.md.j2` (fresh-authored, no source); strips any Jinja2 expressions via AST; asserts the remaining literal prose appears byte-identical in `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`. Catches extraction drift where an editor "improves" prose during extraction — R1-33-1a-B verbatim discipline rendered as a contract.

### Test (AC-T.*) — Murat's D-2 set (R1-33-1a-D non-negotiable)

1. **AC-T.1 — SHA round-trip (primary determinism gate).** `tests/generators/v42/test_determinism.py::test_sha_round_trip_fixture_manifest` reads `manifest_fixture.yaml`, invokes `render_pack()`, computes SHA-256 of output, asserts equality with contents of `pack_sha_fixture.txt`. THIS is the test 33-3 AC-C.1 mirrors in miniature.

2. **AC-T.2 — 5x-consecutive byte-identity.** `tests/generators/v42/test_determinism.py::test_5x_consecutive_byte_identity_fixture_manifest` invokes `render_pack()` 5 times against the same fixture manifest; computes SHA-256 of each output; asserts all 5 are byte-identical. Catches nondeterministic `set()` / `dict` iteration, timestamp leakage, `datetime.now()` smuggling, env-var-dependent rendering.

3. **AC-T.3 — Schema conformance on generated output.** `tests/generators/v42/test_determinism.py::test_generated_pack_parses_through_l1_check` invokes `render_pack()`, writes to scratch path, pipes through 33-2's `check_pipeline_manifest_lockstep.py` (the new scratch pack must also be in lockstep with the fixture manifest — trivially so by construction). Catches gross-structural regressions (missing section, reordered sections) that might SHA-equal by luck but fail semantic lockstep.

4. **AC-T.4 — Manifest-perturbation diff.** `tests/generators/v42/test_determinism.py::test_manifest_mutation_produces_localized_diff` starts from `manifest_fixture.yaml`, mutates one field (e.g., change a section's `label`), regenerates, asserts (a) SHA differs from baseline; (b) diff is localized to the expected section (i.e., only the label change appears; no spurious reordering elsewhere). Guards against "generator ignores manifest" silent-passthrough regressions where a baked-in pack would otherwise pass AC-T.1 and AC-T.2 trivially.

5. **AC-T.5 — Red-path fixture R1 (missing section).** `tests/generators/v42/test_red_path_fixtures.py::test_red_path_missing_section` parametrized over a fixture where the manifest demands section X that doesn't exist in `templates/sections/`. Asserts render raises `TemplateNotFound` or equivalent (with `StrictUndefined` + optimized=True, this surfaces cleanly); asserts the error message names the missing section id.

6. **AC-T.6 — Red-path fixture R2 (template with reordering smuggle).** `tests/generators/v42/test_red_path_fixtures.py::test_red_path_reordered_layout_fails_sha_check` parametrized over a modified `layout/pack.md.j2` that reorders the section-rendering loop. Asserts SHA differs from `pack_sha_fixture.txt`. This test documents the guard shape; actual repo layout is not mutated at rest.

7. **AC-T.7 — Red-path fixture R3 (hardcoded field ignoring manifest).** `tests/generators/v42/test_red_path_fixtures.py::test_red_path_hardcoded_body_ignores_manifest_mutation` tests a synthesized "bug" where a template hardcodes a field value (e.g., `lesson_count: 3` baked in) instead of pulling from manifest. Asserts that mutating the manifest's field value and regenerating produces the WRONG SHA (the bug would pass AC-T.1 / AC-T.2 but fail AC-T.4).

8. **AC-T.8 — Template extraction coverage (positive).** One test that iterates manifest step-ids; for each, asserts the corresponding `templates/sections/<id>.md.j2` file exists and is non-empty. §4.55 specifically asserts a minimum body length (e.g., ≥200 chars of prose content excluding macro calls) to prevent a stubbed-out empty template passing AC-B.5.

9. **AC-T.9 — `rationale:` field shape-pin on manifest.** One test at `tests/test_pipeline_manifest_loader.py` (extends 33-2's loader tests): load manifest with populated `rationale:` field; assert loader accepts; load manifest without `rationale:` field (backward compat); assert loader accepts with `rationale=None`.

10. **AC-T.10 — Audience-tag presence per operator-facing section.** One test that reads each section template; identifies sections flagged as operator-facing in manifest (e.g., has at least one non-empty HUD string or is tagged `audience: [M→O]` in manifest); asserts the section template contains at least one `{{ audience(...) }}` macro call. Catches regressions where a section is extracted without its audience tags.

## Tasks / Subtasks

### T1 — Readiness gate (before any code)

- [x] Confirm 33-2 is `done` in [sprint-status.yaml](sprint-status.yaml).
- [x] Read all required readings enumerated in §T1 Readiness.
- [x] Confirm the current v4.2 pack SHA-256 matches the value recorded in 33-1 findings §Generator Outputs (verifies pack hasn't drifted since 33-1 close).
- [x] Confirm `jinja2` is NOT already in `requirements.txt` at an incompatible version; if present at ≥3.1 <4, no change needed at T2; if present at 2.x, explicit upgrade required.

### T2 — Package scaffolding + loader extension (AC-B.1, AC-B.2, AC-B.3, AC-B.10, AC-B.12, AC-T.9)

- [x] Create `scripts/generators/v42/` package with `__init__.py`, empty stub files for `render.py`, `manifest.py`, `env.py`.
- [x] Create `scripts/generators/v42/templates/sections/`, `templates/partials/`, `templates/macros/`, `templates/layout/` directories.
- [x] Extend `scripts/utilities/pipeline_manifest.py::StepEntry` with `rationale: str | None = Field(default=None, ...)`.
- [x] Add `jinja2>=3.1,<4` to `requirements.txt`.
- [x] Implement `env.py::make_env()` with the 7 pinned config values.
- [x] Implement `manifest.py` wrapping 33-2's loader with sorted-keys discipline on iteration-fed fields.
- [x] Land AC-T.9 shape-pin test for the new `rationale:` field.
- [x] Land AC-C.1 no-LLM-imports contract test (enforces the discipline from T2 onward).
- [x] Land AC-C.2 Jinja2 env-config pin contract test.

### T3 — Template extraction (AC-B.4, AC-B.8, AC-T.8, AC-C.3, AC-C.4)

- [x] For each of the 32 existing v4.2 sections: extract body verbatim into `templates/sections/<id>.md.j2`. Section IDs match manifest declarations exactly.
- [x] Author `macros/audience_tag.j2` with the 4-value macro.
- [x] Inline audience-tag macro calls in each section template per Paige's "prose-level annotation" rule — find the existing audience indicators in the v4.2 pack prose and map them to macro calls.
- [x] Author `layout/pack.md.j2` as the top-level template wiring sections (in manifest-declared order) + section headers (emitted from manifest data) + partials.
- [x] Land AC-C.3 template-coverage contract test.
- [x] Land AC-C.4 verbatim-extraction invariant contract test — **this is the guard that prevents prose drift during extraction**.
- [x] Land AC-T.8 template-extraction-coverage test.
- [x] Land AC-T.10 audience-tag-presence test.

### T4 — §4.55 fresh authoring (AC-B.5)

- [x] Read 33-1 addendum A-2 declarations on the 04.5/04.55 split + `loop.py` emission-boundary cut-line.
- [x] Read the existing `templates/sections/04.5-parent-slide-count-polling.md.j2` (from T3 extraction) as the structural sibling.
- [x] Author `templates/sections/04.55-estimator-run-constants-lock.md.j2` per AC-B.5 content requirements (what, why-split-from-polling, operator guidance, HUD string contract, audience tags). Style matches §4.5 sibling.
- [x] Self-review: dev agent channels Paige (tech-writer) lane — is the prose operator-readable, cross-referenced, concise?
- [x] Self-review: dev agent channels Marcus (operator-flow) lane — does the prose name the right gate behaviors, surface the right failure modes, guide the right operator action?
- [x] If self-review surfaces ambiguity on lock semantics, escalate to party-mode rather than guess — wrong prose at §4.55 is operational risk.

### T5 — Renderer + partials + provenance appendix (AC-B.6, AC-B.7, AC-B.9)

- [x] Implement `render.py::render_pack(manifest_path, output_path)`.
- [x] Implement CLI entry (`python -m scripts.generators.v42.render --manifest <path> --output <path>`).
- [x] Author `templates/partials/tldr_crosswalk.md.j2` — auto-derives TL;DR table from manifest sections + HUD-ID cross-ref + module map. Rows auto-generated; no hand-maintained list.
- [x] Author `templates/partials/provenance_appendix.md.j2` — iterates manifest sections; renders rows for sections with non-empty `rationale:`; skips sections with null rationale.
- [x] Populate `rationale:` in the fixture manifest entries (will be populated in the real manifest as a follow-on extraction pass; 33-1a doesn't need to backfill every real-manifest rationale — fixture coverage suffices).

### T6 — Determinism test suite + ratification fixtures (AC-B.11, AC-T.1, AC-T.2, AC-T.3, AC-T.4)

- [x] Author `tests/generators/v42/fixtures/manifest_fixture.yaml` covering ≥3 sections (plain / sub_phase_of / insertion_after) with `rationale:` populated.
- [x] Author `tests/generators/v42/fixtures/expected_pack/fixture_pack.md` as the expected byte-identical render output.
- [x] Generate `tests/generators/v42/fixtures/pack_sha_fixture.txt` via `sha256sum` on `fixture_pack.md`; commit with `generated_at: <commit-sha>` comment.
- [x] Land `tests/generators/v42/test_determinism.py` with AC-T.1 + AC-T.2 + AC-T.3 + AC-T.4.
- [x] Verify 5 consecutive runs of `test_5x_consecutive_byte_identity_fixture_manifest` all pass on local dev box; if any run differs, stop and root-cause before proceeding (classic nondeterminism bug — likely env config or sorted-keys miss).

### T7 — Red-path fixtures (AC-T.5, AC-T.6, AC-T.7)

- [x] Land `tests/generators/v42/test_red_path_fixtures.py` with the three parametrized red-path tests.
- [x] Red-path fixtures live as code / inline fixtures within the test file (no on-disk fixture files needed since the "bug" scenarios are synthesized in-test).

### T8 — Close

- [x] Focused 33-1a suite: `python -m pytest scripts/generators/v42/ tests/generators/v42/ tests/contracts/test_33_1a_*.py -p no:cacheprovider` — expect green.
- [x] Full regression: `python -m pytest -p no:cacheprovider` — expect no new failures vs the 33-2-close baseline.
- [x] Ruff clean on `scripts/generators/v42/` + all new tests.
- [x] Pre-commit clean on all touched files (including `requirements.txt`).
- [x] Layered post-dev `bmad-code-review` (Blind + Edge + Auditor) per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §3. Expected shape for 5pt single-gate generator-build story: 0-3 PATCH / ≤3 DEFER / several DISMISS. The verbatim-extraction contract (AC-C.4) is the high-risk area — reviewer should walk all 32 extracted sections for drift.
- [x] Update [sprint-status.yaml](sprint-status.yaml) — 33-1a status `ready-for-dev → in-progress → review → done`; update 33-3 entry to note dependency satisfied.
- [x] Update [SCHEMA_CHANGELOG.md](SCHEMA_CHANGELOG.md) with the new `rationale:` field + new generator package.
- [x] Log any DEFER decisions to [_bmad-output/maps/deferred-work.md](../maps/deferred-work.md) §33-1a.
- [x] Update this spec's §Dev Agent Record + §Post-Dev Review Record sections.
- [x] Confirm fixture pair (`manifest_fixture.yaml` + `pack_sha_fixture.txt` + `expected_pack/`) is available for 33-3 AC-C.1 consumption. This is the rider satisfaction evidence.

## Known Risks + Kill-Switches

Dev agent STOPS and escalates (does not silently patch) if:

1. **Jinja2 rendering produces different SHAs on different OSes at T6 despite the pinned env config.** Root-cause: line-ending handling, encoding, locale. If encountered, do NOT just normalize the output — the pinned env config is supposed to handle this. Escalate for party-mode review; the fix may route back to env.py or expose a Python/OS-specific Jinja2 bug we didn't anticipate.

2. **Verbatim extraction surfaces a section whose source prose contains structures Jinja2 would interpret** (e.g., a `{{ }}` in a code fence, a `{% block %}` in an operator example). Escape mechanism: use `{% raw %}...{% endraw %}` blocks around such content. Document the occurrence in Completion Notes; this is a template-extraction artifact.

3. **§4.55 authoring stalls on lock-semantic ambiguity.** Do NOT guess — escalate. Dev agent channeling Paige + Marcus lanes is the intended path; if channeling yields uncertainty, convene a real party round on the §4.55 prose before closing 33-1a.

4. **Manifest's `rationale:` field addition breaks 33-2's L1 check or existing tests.** 33-2's Pydantic loader uses `ConfigDict(extra="forbid")` — a new optional field is additive and should pass. If L1 check breaks, root-cause lives in 33-2's shape validator (the `extra` rule may be too strict). Scope-creep risk; escalate rather than patching 33-2 from within 33-1a.

5. **Template-coverage contract test (AC-C.3) shows orphan templates or missing templates at T3 close.** Orphan templates (.md.j2 with no manifest entry) suggest extraction targeted a section the manifest doesn't declare — either the manifest has a gap (33-2 reopen candidate) or the extraction over-shot (remove the orphan). Missing templates (manifest entry with no .md.j2) is an extraction miss — complete the extraction. DO NOT defer either to 33-3 or a follow-on; this story's job is to close the coverage.

6. **LLM-smuggling temptation at T4 §4.55 authoring.** "I'll just have an LLM draft this and clean it up." NO. The R1-33-1a-A ruling was explicit: no LLM in critical path, and §4.55 authoring IS in the critical path for the operator-facing pack. Draft by hand; iterate by hand; commit by hand. This is the bright line R1-33-1a-A drew.

## Dev Notes

### Project Structure Notes

- `scripts/generators/v42/` is a new top-level directory under `scripts/generators/`. If `scripts/generators/` doesn't exist, create it with an empty `__init__.py`. Future v4.3 / v5 generators will live at `scripts/generators/v43/` / `scripts/generators/v5/` as clean parallel namespaces.
- Templates live inside the package (`scripts/generators/v42/templates/`) NOT at a top-level `templates/` directory. Co-location reduces discoverability cost (template tree is inside the generator that renders it).
- Tests live under `tests/generators/v42/` (mirrors `tests/` top-level + the generator-subpath convention). Contract tests live under `tests/contracts/` per project convention.

### Alignment Notes

- 33-1a does NOT touch `docs/workflow/production-prompt-pack-v4.2-*.md`. Verification runs against fixture manifests only. 33-3 is the story that invokes the generator against the real manifest-to-pack target.
- The verbatim-extraction contract (AC-C.4) is the risk concentration. Dev agent should batch the 32 extractions + run AC-C.4 against each incrementally rather than extracting all 32 then running a single assertion — iterative feedback surfaces drift early.
- Paige's "if it's worth reading, it's worth generating" principle is materialized by AC-B.6 (TL;DR crosswalk) + AC-B.7 (provenance appendix). Both are generator-emitted connective tissue that a future editor inherits for free.

### References

- [33-1-generator-discovery.md](33-1-generator-discovery.md) + §Post-Close R1 Addendum — the Case C escalation that created this story; addendum A-2 documents the 04.5/04.55 split that drives AC-B.5.
- [33-2-pipeline-manifest-ssot.md](33-2-pipeline-manifest-ssot.md) — manifest shape this story's loader wraps + extends.
- [33-3-regenerate-v42-and-validate.md](33-3-regenerate-v42-and-validate.md) — consumer of the fixture pair this story lands (AC-C.1).
- [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance.
- [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) — 27-2 / 31-1 / LLM-smuggling (new pattern documented by 33-1a's kill-switch #6).
- [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md).
- **Epic 33 SCOPE party-mode consensus 2026-04-19** — R1-33-1a-A through R1-33-1a-F rulings recorded in §R1 Scope Resolutions above.

## Dev Agent Record

### Agent Model Used

Codex 5.3

### Debug Log References

- `.\venv\Scripts\python -m pytest tests/contracts/test_33_1a_no_llm_imports.py tests/contracts/test_33_1a_jinja_env_pinned.py tests/contracts/test_33_1a_template_coverage.py tests/contracts/test_33_1a_verbatim_extraction.py tests/generators/v42/test_determinism.py tests/generators/v42/test_red_path_fixtures.py tests/test_pipeline_manifest_loader.py -q`
- `.\venv\Scripts\python -m pytest -q`
- `.\venv\Scripts\python -m pre_commit run --files requirements.txt scripts/generators/v42/__init__.py scripts/generators/v42/env.py scripts/generators/v42/manifest.py scripts/generators/v42/render.py scripts/utilities/pipeline_manifest.py state/config/pipeline-manifest.yaml tests/contracts/test_33_1a_jinja_env_pinned.py tests/contracts/test_33_1a_no_llm_imports.py tests/contracts/test_33_1a_template_coverage.py tests/contracts/test_33_1a_verbatim_extraction.py tests/generators/v42/test_determinism.py tests/generators/v42/test_red_path_fixtures.py tests/test_pipeline_manifest_loader.py`
- `.\venv\Scripts\python -m ruff check scripts/generators/v42 tests/generators/v42 tests/contracts/test_33_1a_no_llm_imports.py tests/contracts/test_33_1a_jinja_env_pinned.py tests/contracts/test_33_1a_template_coverage.py tests/contracts/test_33_1a_verbatim_extraction.py tests/test_pipeline_manifest_loader.py`

### Completion Notes List

- Template extraction count: 32 / 32 sections extracted verbatim; AC-C.4 contract green.
- §4.55 body word count: 108 words; semantically aligned to 04.5 split and lock semantics.
- Jinja2 determinism: 5x-consecutive byte-identity green on fixture manifest.
- Fixture pair SHA: `3c1dfb7a02b685d998861974a449f6f75184a91ed716ac95a09f7ecafe1702d8` handed to 33-3 AC-C.1.
- AC-T.1-T.4: all green after manifest/template resolution hardening.
- Red-path fixtures R1/R2/R3: all fire correctly.
- New dependency: `jinja2>=3.1,<4`; no LLM SDK dependencies added.
- No-LLM-imports guard (AC-C.1): green, no forbidden imports detected.
- §4.55 authoring approach: channeled Paige + Marcus lanes; no ambiguity requiring escalation.
- K-floor verdict: 16 collecting tests vs K=6 floor (target 8-12); overage justified by contract hardening and loader compatibility pins.
- G6 layered triage: PATCH=3 / DEFER=0 / DISMISS=3.
- DEFER log: none for 33-1a; no deferred findings required additional map entries.

### File List

_(populated at closure — minimum entries:)_
- `scripts/generators/v42/__init__.py` (new)
- `scripts/generators/v42/render.py` (new)
- `scripts/generators/v42/manifest.py` (new)
- `scripts/generators/v42/env.py` (new)
- `scripts/generators/v42/templates/layout/pack.md.j2` (new)
- `scripts/generators/v42/templates/sections/*.md.j2` (new — 32 files extracted verbatim + 1 fresh = 33 total)
- `scripts/generators/v42/templates/partials/tldr_crosswalk.md.j2` (new)
- `scripts/generators/v42/templates/partials/provenance_appendix.md.j2` (new)
- `scripts/generators/v42/templates/macros/audience_tag.j2` (new)
- `scripts/utilities/pipeline_manifest.py` (modified — `rationale:` field added to StepEntry)
- `requirements.txt` (modified — `jinja2>=3.1,<4` added)
- `tests/generators/v42/test_determinism.py` (new)
- `tests/generators/v42/test_red_path_fixtures.py` (new)
- `tests/generators/v42/fixtures/manifest_fixture.yaml` (new)
- `tests/generators/v42/fixtures/expected_pack/fixture_pack.md` (new)
- `tests/generators/v42/fixtures/pack_sha_fixture.txt` (new)
- `tests/contracts/test_33_1a_no_llm_imports.py` (new)
- `tests/contracts/test_33_1a_jinja_env_pinned.py` (new)
- `tests/contracts/test_33_1a_template_coverage.py` (new)
- `tests/contracts/test_33_1a_verbatim_extraction.py` (new)
- `tests/test_pipeline_manifest_loader.py` (modified — AC-T.9 rationale-field shape-pin)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (updated — 33-1a status transitions)
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` (updated — rationale field + generator package)

## Post-Dev Review Record

### Layered `bmad-code-review` Pass

Self-conducted layered post-dev `bmad-code-review` (single-gate closure):

- **Blind Hunter:** PATCH=1 / DEFER=0 / DISMISS=1. Findings: fixed malformed newline literals in generator env/render paths; dismissed cosmetic prose nits in extracted templates.
- **Edge Case Hunter:** PATCH=1 / DEFER=0 / DISMISS=1. Walked CRLF/LF determinism, template lookup on mutated labels, and fixture manifest ordering behavior; patched template resolution to key by step-id file prefix to prevent label-change template misses.
- **Acceptance Auditor:** PATCH=1 / DEFER=0 / DISMISS=1. Verified AC coverage across generator package, contract tests, fixture pair, and rationale-field compatibility; patched loader-test YAML indentation for valid parse-path contract.
- **Orchestrator triage:** PATCH=3 landed, DEFER=0, DISMISS=3 (non-blocking stylistic concerns).

### Closure Verdict

CLEAN-CLOSE
