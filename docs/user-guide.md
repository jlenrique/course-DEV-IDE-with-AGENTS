# User Guide — Course Content Production System

**Audience:** Course creators and instructional designers using the system to produce educational content.
**Last Updated:** 2026-03-28 | **Project Phase:** 4-Implementation (Epic 3: 8/11 stories done; Epic 2A fidelity stack complete; **Epic 4A** governance next on the roadmap)

---

## Quick Start

Get from zero to your first content artifact in under 15 minutes.

### Prerequisites

- **Cursor IDE** installed with this repository open
- API keys configured (ask your admin — see the [Admin Guide](admin-guide.md) for setup)
- Pre-flight check passed (green status for your target tools)

### Your First Session

1. **Open Cursor IDE** and open a new agent chat (Cmd/Ctrl+L)
2. **Activate Marcus** — type: *"Talk to Marcus"* or *"I'd like to produce some content"*
3. Marcus greets you by name, reports system status, and asks what you'd like to create
4. **Tell Marcus what you need** — for example:
   - *"Create a presentation for Module 2, Lesson 3 on clinical trial design"*
   - *"Draft a knowledge check quiz for the pharmacology module"*
   - *"Help me plan the assessment strategy for Module 4"*
5. Marcus handles the rest — tool selection, specialist coordination, quality checks — and presents you with work at **checkpoint gates** for your review and approval
6. **Review and approve** — Marcus stages all drafts in `course-content/staging/` for your review before anything goes to `course-content/courses/`

That's it. Everything else is depth you discover as you work with Marcus.

---

## How the System Works (What You Need to Know)

### Marcus is Your Single Point of Contact

Marcus is a veteran executive producer for medical education content. You talk to Marcus; Marcus handles everything else. You never need to think about which tools, APIs, or agents are involved — Marcus coordinates all of that behind the scenes.

Think of Marcus as your **general contractor**: you describe what you want built, Marcus assembles the right specialists, manages the work, and brings you results for approval at every stage.

### Two Modes: Default and Ad-Hoc

| Mode | Purpose | Assets Go To | State Tracking |
|------|---------|-------------|----------------|
| **Default** | Full production runs | `course-content/staging/` → your review → `course-content/courses/` | Full — preferences learned, patterns captured |
| **Ad-Hoc** | Experimentation and quick exploration | Scratch/staging area | Paused — nothing permanent saved |

Switch modes by telling Marcus:
- *"Switch to ad-hoc mode"* — for experimenting without committing
- *"Switch to default mode"* — for production work
- *"What mode am I in?"* — Marcus confirms your current mode

**Quality checks always run in both modes.** The difference is only whether the system remembers your preferences for next time.

### The Content Workflow

Every piece of content follows this path:

```
Your Intent → Marcus Plans → Specialists Create → Fidelity + Quality Review → Your Approval → Published
```

1. **Intent** — You describe what you want: learning objectives, audience, constraints, content type
2. **Planning** — Marcus consults the style bible, checks exemplars, and builds a production plan
3. **Creation** — Specialist agents generate content (slides, audio, assessments, etc.)
4. **Fidelity check (Vera)** — For pipeline artifacts, the **Fidelity Assessor (Vera)** checks whether outputs stay faithful to their source of truth (traceability; omissions, inventions, and alterations). Serious issues can stop the run before routine quality review.
5. **Quality review (Quinn-R)** — The **Quality Guardian (Quinn-R)** checks brand, accessibility, instructional soundness, learner-effect alignment, and related quality dimensions. This is separate from source-faithfulness.
6. **Your review** — Marcus presents the work at a checkpoint gate. You approve, request changes, or redirect
7. **Staging** — Drafts land in `course-content/staging/` for your edit and signoff
8. **Promotion** — You (or Marcus at your direction) move approved content to `course-content/courses/`
9. **Publishing** — Content is deployed to Canvas, CourseArc, or other platforms (some platform specialists are still on the roadmap; see [Tools in the Ecosystem](#tools-in-the-ecosystem))

Gate order and automated assessment flow are summarized in [`docs/fidelity-gate-map.md`](fidelity-gate-map.md). Which role may judge what (orchestration, pedagogy, tool execution, fidelity) is summarized in [`docs/lane-matrix.md`](lane-matrix.md).

### Production run authority (baton)

When Marcus is running a **production run**, the system may hold an active **run baton** (a small JSON file under `state/runtime/`). If you open a **specialist agent directly** (for example Gary or Irene) while that run is active, the specialist should prompt you: continue with Marcus for the run, or enter **standalone consult mode** for a side conversation that does not change the active run. You do not need to edit baton files yourself; Marcus and the specialists follow the contract in the implementation skills.

### Checkpoint Gates (Human-in-the-Loop)

You stay the instructor of record. Marcus **never** publishes content without your approval. At every significant production stage, Marcus pauses and presents:

- What was created
- How it aligns with learning objectives
- Fidelity findings (when Vera has run) and quality findings (when Quinn-R has run), when relevant
- Any quality concerns or decisions that need your input
- A clear recommendation with rationale

You can:
- **Approve** — move forward
- **Request changes** — Marcus sends it back to the specialist with your feedback
- **Redirect** — change direction entirely
- **Override** — Marcus respects your creative judgment even when it differs from standard patterns

### Source Materials

Marcus can pull your reference materials into the production context:

- **Notion** — Course development notes, syllabi, design documents. Tell Marcus: *"Pull my Module 3 notes from Notion"*
- **Box Drive** — Locally synced files. Tell Marcus: *"Check Box Drive for the pharmacology references"*
- **Web exemplars** — Share a URL, or save a page with Playwright in Cursor and point Marcus at the HTML file; the **source-wrangler** skill turns captures into `extracted.md` bundles for Irene and Gary

Marcus proactively offers to pull source materials before starting production tasks. Context enrichment before creation beats revision after.

---

## What You Can Ask Marcus To Do

### Content Creation
- *"Create a presentation on [topic] for [module/lesson]"*
- *"Draft a knowledge check for [learning objective]"*
- *"Generate a voiceover script for [presentation]"*
- *"Build a discussion board prompt for [topic]"*

### Planning and Strategy
- *"Help me plan the content for Module 5"*
- *"What's the best content type for teaching [concept]?"*
- *"Show me how this lesson maps to course learning objectives"*

### Review and Quality
- *"Review [content] for accessibility compliance"*
- *"Check brand consistency on these slides"*
- *"Run an editorial review on the Module 2 lesson plan"*

### System Operations
- *"Run a pre-flight check"* — verify all tools are working
- *"What's the status of the current production run?"*
- *"Switch to ad-hoc mode"*
- *"Show me what's in staging"*
- *"Refresh tool knowledge"* — ask Marcus to refresh current API/tool documentation before a production task

### Source Materials
- *"Pull my notes from Notion for this module"*
- *"Check Box Drive for the case study files"*

---

## Content Standards

### Style Bible

All content follows the standards in your **Master Style Bible** (`resources/style-bible/master-style-bible.md`). This is human-curated — you control it. Marcus and all specialists read it fresh for every task. Key elements:

- **Brand colors:** JCPH Navy (#1e3a5f), Medical Teal (#4a90a4)
- **Typography:** Montserrat (headlines), Open Sans (body), Source Sans Pro (data)
- **Voice:** Clear, direct, respectful of physician expertise, evidence-based
- **Accessibility:** WCAG 2.1 AA compliance, 4.5:1 contrast ratio, alt text on all visuals

To update the style bible, edit the file directly. Changes take effect on the next production task — no restart needed.

### Run Presets

Marcus uses run presets that control how strictly quality is enforced:

| Preset | When to Use | Human Review | Quality Level |
|--------|------------|:------------:|:-------------:|
| **explore** | Quick experiments, idea generation | No | Minimal |
| **draft** | Working drafts, iterative development | Yes | Standard |
| **production** | Publication-ready content | Yes | Full pipeline |
| **regulated** | Compliance-grade (accreditation) | Yes | Strictest + audit trail |

The default is **draft**. Tell Marcus to switch: *"Use production preset for this run."*

---

## Content Organization

### Where Your Content Lives

```
course-content/
├── staging/              ← Agent drafts awaiting your review
│   └── m03-intro-ai/    ← One folder per module in progress
├── courses/              ← Approved, published content
│   └── course-slug/
│       └── module-01-topic/
│           ├── lessons/          ← Narrative Markdown
│           ├── presentations/    ← Slide source files
│           └── assets/           ← Images, diagrams
└── _templates/           ← Reusable outlines and scaffolds
```

### The Staging → Courses Workflow

1. Agents always write to `course-content/staging/`
2. You review and edit for accuracy, examples, and institutional policy
3. You promote approved material to `course-content/courses/`
4. Platform publishing follows from the `courses/` directory

**Never edit directly in `courses/` during production.** Use staging as your review buffer.

### Definition of Done (per lesson or deck)

Before promoting content from staging:

- [ ] Learning objectives stated and aligned to activities
- [ ] You personally verified facts and institution-specific policy
- [ ] Accessibility checklist considered (contrast, alt text, captions)
- [ ] Visible in target platform (Canvas page / LTI link) in preview mode

### Narrated slide assembly (Descript)

For narrated slide packs, the team assembles in **Descript** using a single **assembly bundle** folder under `course-content/staging/…`: segment manifest, narration audio and WebVTT captions, ElevenLabs summaries, the Descript Assembly Guide, and **copies** of Gate-approved slide stills under `visuals/`. Automation runs **`sync-visuals`** on the manifest so those PNGs sit beside the other assets (not only under the Gary export tree) before you import into Descript. You normally do not run commands yourself—Marcus or the developer does; exact steps live in the [Developer guide — Compositor assembly bundle CLI](dev-guide.md#compositor-assembly-bundle-cli).

---

## Tools in the Ecosystem

You don't need to know how these tools work — Marcus and the specialist agents handle them. But here's what's available:

| What | Tool | How It's Used |
|------|------|--------------|
| **Slides/Presentations** | Gamma | AI-generated professional slides (specialist **Gary**) |
| **Voiceover/Audio** | ElevenLabs | Natural-sounding narration synthesis (Voice Director specialist) |
| **Video** | Kling | Text/image-to-video and related flows (specialist **Kira**) |
| **LMS Management** | Canvas LMS | Course structure, modules, assignments, quizzes (API + MCP in repo; **Canvas specialist agent** story is **deferred** on the current roadmap — workflows may use scripts or manual steps until that ships) |
| **Surveys/Assessments** | Qualtrics | Professional survey and assessment creation (**Qualtrics specialist** story **deferred**) |
| **Course Dev Notes** | Notion | Pull reference materials into production context (source wrangler + API) |
| **Source Files** | Box Drive | Access locally synced cloud files |
| **Design/Graphics** | Canva | Design-guidance pattern; full programmatic specialist **deferred** (API limits) |
| **Composition** | Descript (manual) | Final assembly of narrated decks; compositor skill produces assembly guides and syncs stills |
| **Hosting** | Panopto | Video hosting (API client in repo; credential-dependent) |

Some tools (Vyond, CourseArc, Articulate) require manual operation — Marcus provides detailed specs and you execute in the tool's own interface.

**Roadmap note:** Epic 3 still includes Canvas, Qualtrics, and Canva specialist agents, but those stories are **deferred** while governance (**Epic 4A**) and other foundations proceed. Ask Marcus what path is supported today for your institution.

---

## Tips for Working with Marcus

1. **Be specific about learning objectives** — Marcus uses them to align everything. "Create slides about pharmacology" is okay; "Create slides covering drug interaction mechanisms aligned to CLO-3 at Bloom's application level" is much better.

2. **Front-load your constraints** — Tell Marcus early about time limits, modality requirements, platform targets, or special audience considerations.

3. **Use ad-hoc mode for exploration** — When you're brainstorming or trying ideas, switch to ad-hoc. Switch back to default when you're ready to produce.

4. **Review checkpoint outputs carefully** — Your domain expertise is irreplaceable. Marcus handles production quality; you handle instructional accuracy and clinical correctness.

5. **Update the style bible when standards evolve** — If you decide Medical Teal should be used differently, or you want a new voice style for a specific audience, update `resources/style-bible/master-style-bible.md` directly.

6. **Trust the staging workflow** — Resist the urge to edit published content directly. Staging exists to protect your students from seeing in-progress work.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Marcus says a tool isn't responding | Ask: *"Run pre-flight check"* — Marcus will diagnose and suggest fixes |
| Content doesn't match your style expectations | Check `resources/style-bible/master-style-bible.md` — is it up to date? |
| Quality review flags something you disagree with | You can override any quality decision — tell Marcus your reasoning |
| Marcus seems to have forgotten context | Sessions are independent. Start with: *"Here's where we left off..."* |
| Staging content looks wrong in Canvas | Run a platform smoke test first — *"Preview this in Canvas student view"* |

For system setup issues, see the [Admin Guide](admin-guide.md). For technical questions, see the [Developer Guide](dev-guide.md).

---

## Glossary

| Term | Meaning |
|------|---------|
| **APP** | **Agentic Production Platform** — this environment: IDE-hosted agents, tools, memory, and governance together |
| **Marcus** | The master orchestrator agent — your single point of contact |
| **Vera** | The **Fidelity Assessor** — source-faithfulness and provenance checks (typically before Quinn-R on pipeline artifacts) |
| **Quinn-R** | The **Quality Guardian** — brand, accessibility, instructional soundness, learner-effect quality, and related standards |
| **Checkpoint gate** | A pause point where Marcus presents work for your review |
| **Style bible** | The authoritative brand and content standards document |
| **Staging** | The review area where agent-created content waits for your approval |
| **Run preset** | A quality enforcement level (explore, draft, production, regulated) |
| **Ad-hoc mode** | Experimental mode — assets go to scratch, state tracking paused |
| **Default mode** | Production mode — full state tracking and learning |
| **HIL** | Human-in-the-loop — you review and approve before publication |
| **Specialist agent** | A focused expert (e.g. Gary for Gamma, Irene for instructional design) that Marcus delegates to |
| **Memory sidecar** | Where agents remember preferences and patterns between sessions |
| **Woodshed** | Exemplar-driven practice workflow agents use to prove tool mastery (optional unless you choose to run it) |
