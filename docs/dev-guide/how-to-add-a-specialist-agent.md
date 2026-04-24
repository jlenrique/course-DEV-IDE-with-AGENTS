# How to add a specialist agent

**Audience:** developers adding a new leaf-specialist agent to the repo
(parallel to Irene / Kira / Enrique / Wanda).
**Predecessor recipes:**
[how-to-add-a-retrieval-provider.md](how-to-add-a-retrieval-provider.md),
[how-to-add-a-dispatch-edge.md](how-to-add-a-dispatch-edge.md) — the
"extend-the-system" sibling recipes for retrieval-shape and dispatch-only
extensions.
**Filed under:** Paige rider D4 (Sprint 2 Wanda story) — third recurring
extend-the-system pattern.

## What a specialist agent is

A specialist agent is a **leaf node** in the production-tier ensemble. It
wraps an existing API client (or a domain-specific helper) into a
dispatchable capability that Marcus can route to via the standard
[dispatch contract](../../marcus/dispatch/contract.py). A specialist agent:

- **Does** own execution quality for its domain (voice direction, motion
  production, podcast production, retrieval dispatch, etc.).
- **Does not** own flow control, orchestrator event emission, or Lesson Plan
  log writes.
- **Does** have a BMB sanctum at `_bmad/memory/bmad-agent-<name>/` that
  carries persistent persona + continuity artifacts.
- **Does not** subsume sibling specialists — if two engines serve the same
  domain (ElevenLabs + Wondercraft for audio), ship them as sibling
  specialists and let Marcus route between them.

Specialist agents follow the **Irene / Kira / Enrique / Wanda** template —
six references / six capability cards / one sanctum / one entry in the
Marcus dispatch registry.

## 1. Create the skill directory

Create `skills/bmad-agent-<name>/` with this shape:

```text
skills/bmad-agent-<name>/
├── SKILL.md               # specialist-tier, <=60 lines (Paige ceiling)
├── assets/
│   ├── INDEX-template.md
│   ├── PERSONA-template.md
│   ├── CREED-template.md
│   ├── BOND-template.md
│   ├── MEMORY-template.md
│   └── CAPABILITIES-template.md
├── references/
│   ├── init.md                       # activation routing
│   ├── first-breath.md               # first-run identity formation
│   ├── memory-system.md              # sanctum layout + batch-load
│   ├── save-memory.md                # session close discipline
│   ├── context-envelope-schema.md    # Marcus ↔ agent dispatch contract
│   └── capability-<code>-<name>.md   # one per capability card
└── scripts/
    ├── __init__.py
    └── init-sanctum.py               # thin forwarder (copy from sibling)
```

SKILL.md conventions:

- Frontmatter `name: bmad-agent-<name>` + a concise operator-facing `description`.
- H1 with persona name.
- Sections: Overview / Lane Responsibility / Identity / Principles / Does Not Do / On Activation / Capabilities (table) / Delegation Protocol.
- Stay **≤60 lines**. If it overflows, push detail into `references/`.

Capability cards — one file per card with YAML frontmatter:

```markdown
---
name: <kebab-case>
code: <2-letter code>
description: <short route description>
---

# Capability <CODE> — <snake_case_name>

## Inbound shape (input_packet)
## Dispatch logic
## Outbound shape
## Test coverage
```

The scaffold auto-discovers capability cards by scanning `code:` frontmatter
fields. Missing `code:` → capability not surfaced in CAPABILITIES.md.

## 2. Scaffold the sanctum

Copy `skills/bmad-agent-content-creator/scripts/init-sanctum.py` into your
new skill's `scripts/` directory (it's a thin forwarder to the shared
scaffold at `scripts/bmb_agent_migration/init_sanctum.py` — v0.2 as of
Epic 26). Then run:

```bash
python skills/bmad-agent-<name>/scripts/init-sanctum.py --dry-run  # preview
python skills/bmad-agent-<name>/scripts/init-sanctum.py             # execute
```

The scaffold:

1. Validates the skill directory shape (`assets/` + `references/` present).
2. Renders each `assets/*-template.md` to the sanctum with known-variable
   substitution (`{user_name}`, `{birth_date}`, `{project_root}`,
   `{sanctum_path}`, `{skill_name}`).
3. Copies `references/*.md` into the sanctum, except `first-breath.md`
   (which stays skill-side for first-run routing).
4. Copies `scripts/*.py` except the forwarder itself.
5. Auto-generates `CAPABILITIES.md` by scanning reference frontmatter.
6. Creates `sessions/` and `capabilities/` subdirectories.

Verify:

```bash
ls _bmad/memory/bmad-agent-<name>/
# Expect: BOND.md CAPABILITIES.md CREED.md INDEX.md MEMORY.md PERSONA.md
#         capabilities/ references/ scripts/ sessions/
```

## 3. Extend the dispatch contract

Add the new specialist to the closed enums in
[marcus/dispatch/contract.py](../../marcus/dispatch/contract.py):

```python
class DispatchKind(str, Enum):
    # ... existing kinds ...
    <NAME>_<CAPABILITY_A> = "<name>_<capability_a>"
    <NAME>_<CAPABILITY_B> = "<name>_<capability_b>"
    # ... one value per capability card ...

class SpecialistId(str, Enum):
    # ... existing ids ...
    <NAME> = "<name>"

DISPATCH_KIND_TO_SPECIALIST: Mapping[DispatchKind, SpecialistId] = {
    # ... existing mappings ...
    DispatchKind.<NAME>_<CAPABILITY_A>: SpecialistId.<NAME>,
    DispatchKind.<NAME>_<CAPABILITY_B>: SpecialistId.<NAME>,
}

_KIND_ALIASES: Mapping[str, DispatchKind] = {
    # ... existing aliases ...
    "<name>-<capability-a>": DispatchKind.<NAME>_<CAPABILITY_A>,
    "<name>-<capability-b>": DispatchKind.<NAME>_<CAPABILITY_B>,
}
```

Also update the schema-dump test at
[tests/marcus_dispatch/test_dispatch_contract.py](../../tests/marcus_dispatch/test_dispatch_contract.py)
so the closed-enum schema test reflects the new values (this is a
deliberate lockstep guard — extending the enum must be acknowledged in the
contract test).

## 4. Register dispatch-registry edges

Add one entry per capability card to
[skills/bmad-agent-marcus/references/dispatch-registry.yaml](../../skills/bmad-agent-marcus/references/dispatch-registry.yaml):

```yaml
  - dispatch_kind: <name>_<capability_a>
    specialist_id: <name>
    owner: marcus
    entrypoint: skills/bmad-agent-<name>/SKILL.md
    contract_module: marcus.dispatch.contract
    notes: "<one-line capability description>"
```

Bump `registry_version` to today's date.

Run the L1 lockstep check:

```bash
PYTHONPATH=. python scripts/validators/check_dispatch_registry_lockstep.py
```

Expect `exit=0` and a PASS trace under `reports/dev-coherence/`.

## 5. Add the portability guard test

Leaf specialists must not import `marcus.orchestrator.*` or
`marcus.dispatch.*` modules. They consume the dispatch contract via the
declarative envelope schema reference (`context-envelope-schema.md`), not
by importing the contract module. Add a test mirroring
[tests/wondercraft/test_specialist_dispatch.py](../../tests/wondercraft/test_specialist_dispatch.py):

```python
def test_no_marcus_orchestrator_or_dispatch_imports_in_<name>_scripts() -> None:
    import ast
    scripts_dir = Path("skills/bmad-agent-<name>/scripts")
    forbidden = ("marcus.orchestrator", "marcus.dispatch")
    # walk each .py, parse AST, check Import / ImportFrom nodes
    # assert offenders == []
```

Also guard against `lesson_plan.log` writes — specialist agents never
mutate the Lesson Plan log directly; they return receipts and let Marcus
decide what gets logged.

## 6. Pre-flight check integration

Add the agent's API-key / readiness row to
[skills/pre-flight-check/references/check-strategy-matrix.md](../../skills/pre-flight-check/references/check-strategy-matrix.md)
so the operator sees the readiness signal alongside other tool checks.

## 7. Cassette-backed tests + cost-gated live smoke

Unit tests for each capability use cassettes (see the Box / Notion-MCP
provider test pattern for the DI-substitution style). Live-smoke tests that
hit the real API are cost-gated — they run only with an explicit env var
(e.g., `WONDERCRAFT_LIVE_SMOKE=1`). Cassette-only is the default.

Live-smoke can be deferred to a follow-on story if cassette coverage is
sufficient for v1 (Murat Sprint 2 posture on Wanda: cassette-only pilot;
live-smoke follow-on gated on 2-week cassette stability).

## Checklist

- [ ] `skills/bmad-agent-<name>/` created with SKILL.md ≤60 lines.
- [ ] All 6 asset templates authored.
- [ ] All `N` capability card files authored with frontmatter (`code:` + `name:`).
- [ ] Sanctum scaffold executed; `_bmad/memory/bmad-agent-<name>/` exists
      with all 6 standard files.
- [ ] `DispatchKind` + `SpecialistId` + `DISPATCH_KIND_TO_SPECIALIST` +
      `_KIND_ALIASES` extended in `marcus/dispatch/contract.py`.
- [ ] Schema-dump test updated in `tests/marcus_dispatch/test_dispatch_contract.py`.
- [ ] `dispatch-registry.yaml` extended with one row per capability card;
      `registry_version` bumped.
- [ ] L1 lockstep check passes (`check_dispatch_registry_lockstep.py`).
- [ ] Portability guard test added.
- [ ] Pre-flight check-strategy-matrix row added.
- [ ] Cassette-backed tests for each capability card.
- [ ] Full regression passes; no new skips introduced.

## Reference implementations

- **Wanda** (this recipe's worked example) — [skills/bmad-agent-wondercraft/](../../skills/bmad-agent-wondercraft/), [tests/wondercraft/test_specialist_dispatch.py](../../tests/wondercraft/test_specialist_dispatch.py).
- **Kira** (motion) — [skills/bmad-agent-kling/](../../skills/bmad-agent-kling/).
- **Enrique** (voice) — [skills/bmad-agent-elevenlabs/](../../skills/bmad-agent-elevenlabs/).
- **Irene** (content) — [skills/bmad-agent-content-creator/](../../skills/bmad-agent-content-creator/) (domain specialist, not engine wrapper — slightly different shape but canonical sanctum template).
