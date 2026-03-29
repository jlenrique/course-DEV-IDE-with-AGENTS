# Adversarial review: Stories 5.1, 5.4, 6.1 (Epics 5 & 6)

**Scope:** Planning quality, consistency, implementability, and alignment with the current repo.  
**Sources:** `_bmad-output/planning-artifacts/epics.md` (both Epic 5/6 sections), `_bmad-output/implementation-artifacts/sprint-status.yaml`, spot checks under `skills/`, `scripts/api_clients/`, `tests/`, `scripts/heartbeat_check.mjs`.  
**Date:** 2026-03-30

---

## Evidence note (repo vs planning)

- **`sprint-status.yaml`** still has **5.1, 5.4, 6.1 as `backlog`**, but the repo already contains **Vyond / Midjourney / Articulate** skills, **Botpress / Wondercraft** API clients (plus heartbeat + optional integration tests), and **`skills/bmad-agent-coursearc/`** (Cora). That **planning/implementation drift** is a major adversarial finding.
- **`epics.md` defines these stories twice** (rebaselined block ~1868–1937 and a **stale duplicate** after Epic 10 ~2028–2128) with **different paths and AC** (e.g. `skills/bmad-agent-*` vs `agents/*`, CapCut/Panopto in duplicate only).

---

## 1. Full evaluation account

### 1.1 Story 5.1 — Expanded tool specialist agents (Vyond, Midjourney, Articulate)

| Lens | Finding |
|------|---------|
| **Clarity** | Rebaselined story is clear: manual-tool pattern, three `skills/bmad-agent-*` agents, sidecars, Marcus registry, human-reviewed quality. |
| **Consistency** | **Duplicate Story 5.1** later in `epics.md` reintroduces **CapCut**, **`agents/*.md` paths**, and Story **3.7** as Canva reference while rebaselined text says **3.8** elsewhere — **conflicting source of truth**. |
| **Testability** | AC relies on **human review** for instruction quality — weak objective gates; “interaction test guides” need explicit completion criteria. |
| **Dependency risk** | “Marcus's specialist registry” must stay in sync with **conversation-mgmt** tables — easy drift if agents ship without routing updates. |
| **Implementation truth** | Repo already has `skills/bmad-agent-vyond/`, `bmad-agent-midjourney/`, `bmad-agent-articulate/` with references and quality-scan JSON under `skills/reports/`. **Sprint still says backlog** → risk of **never closing** the story or **missing** remaining AC (e.g. style guide sections, full Marcus table audit). |

### 1.2 Story 5.4 — Remaining Tier 2 API integrations (Botpress, Wondercraft)

| Lens | Finding |
|------|---------|
| **Clarity** | Rebaselined scope is narrow (only unbuilt Tier 2) — good after Kling/Panopto pull-forward. |
| **API realism** | AC names capabilities (“conversation management, NLU, bot deployment”; “podcast generation, episode management”) **without** binding to **specific API versions/endpoints** — risk of **over-claim** vs what `BotpressClient` / `WondercraftClient` actually implement. |
| **Testing** | AC says “integration tests verify API connectivity” — repo has **`tests/test_integration_botpress.py`** and **`test_integration_wondercraft.py`** with **env-gated skips** (`conftest.py`) — acceptable pattern but **not proof** CI always exercises them. |
| **Downstream** | Design note: **specialist agents are separate** — adversarial: **orphan clients** if no Marcus route, skill, or production plan step references Botpress/Wondercraft. |
| **Pre-flight** | `scripts/heartbeat_check.mjs` includes **Botpress** and **Wondercraft** checks — good alignment. |
| **Implementation truth** | `scripts/api_clients/botpress_client.py` and `wondercraft_client.py` **exist** and extend **BaseAPIClient**. **Sprint backlog** → same **closure/drift** issue as 5.1. |

### 1.3 Story 6.1 — CourseArc specialist agent & LTI integration

| Lens | Finding |
|------|---------|
| **Clarity** | Rebaselined AC: manual-tool, LTI guidance, SCORM **specs**, interactive blocks, WCAG — coherent for **no CourseArc REST**. |
| **Duplicate conflict** | Later **duplicate Story 6.1** demands **`agents/coursearc-specialist.md`**, **SCORM packaging scripts**, and “manages” LTI — contradicts rebaselined **`skills/bmad-agent-coursearc`** and **guidance-only** model. |
| **Testability** | “WCAG 2.1 AA compliance verification” without requiring **automated** checks or **evidence artifact** invites **checkbox completion**. |
| **Marcus integration** | `skills/bmad-agent-marcus/SKILL.md` lists `coursearc-specialist` as **active (Story 6.1)** — story is **partially operationalized in docs** while sprint says **backlog**. |
| **Implementation truth** | **`skills/bmad-agent-coursearc/SKILL.md`** (Cora), references (`lti13-canvas-embedding-checklist.md`, etc.), sidecar under `_bmad/memory/coursearc-specialist-sidecar/`, **`tests/agents/bmad-agent-coursearc/interaction-test-guide.md`** — strong evidence story is **largely delivered** but **not marked done** in `sprint-status.yaml`. |

---

## 2. Narrative summary

These three stories are **directionally sound** for the APP (manual-tool expansion, Tier 2 APIs, CourseArc/LTI guidance), but the **backlog is not trustworthy**: substantial work for **5.1, 5.4, and 6.1 already lives in the tree** while **sprint-status** still shows **backlog**. That creates **false priority**, **duplicate work**, and **audit gaps** (AC never formally signed off).

The **single largest process failure** is **`epics.md` duplication**: two incompatible versions of **5.1, 5.4, 5.2, 5.3, 6.1, 6.2** after Epic 10 inject **wrong file paths**, **CapCut**, **Panopto in 5.4**, and **SCORM scripts** for CourseArc. Any dev following the **wrong section** will build the **wrong artifact**.

**Story 5.1** is vulnerable to **subjective “done”** (human review only) unless you add **structured rubrics or interaction scenarios**. **Story 5.4** is vulnerable to **orphan integrations** without agents/skills and production-plan hooks. **Story 6.1** is vulnerable to **claiming WCAG compliance** without defined **evidence** (checklist sign-off, optional axe/manual protocol).

---

## 3. Actionable tickets (remediation backlog)

| ID | Title | Severity | Action |
|----|--------|----------|--------|
| **REM-E5-01** | Reconcile sprint-status with repo for 5.1 / 5.4 / 6.1 | **Critical** | Run AC-by-AC audit; set stories to `done` or `in-progress` with explicit remaining tasks; remove “ghost backlog.” |
| **REM-E5-02** | Delete or archive duplicate Epic 5/6 block in `epics.md` | **Critical** | Keep one canonical section (rebaselined ~L1868+); remove stale duplicate (~L2028+) or mark “ARCHIVED — DO NOT USE.” |
| **REM-E5-03** | Align manual-tool pattern references (Canva story 3.7 vs 3.8) | **Medium** | Single citation across epics + agent docs. |
| **REM-5.1-01** | Define objective acceptance for “human-reviewed instruction quality” | **Medium** | Rubric + signed interaction-test completion or Party Mode sign-off record. |
| **REM-5.1-02** | Verify Marcus routing for Vyond / Midjourney / Articulate | **Medium** | `conversation-mgmt.md` + `SKILL.md` tables match deployed skill names and content types. |
| **REM-5.1-03** | Style guide sections for three tools (per AC) | **Low–Medium** | Confirm `state/config/style_guide.yaml` or style-bible pointers exist or explicitly defer with FR trace. |
| **REM-5.4-01** | Map clients to real API surface | **Medium** | Docstring or `references/api-surface.md` per client listing implemented endpoints vs story verbs. |
| **REM-5.4-02** | Botpress / Wondercraft specialist or Marcus workflow step | **Medium** | Avoid orphan clients: skill stub or explicit “invoke via script X” in production plan. |
| **REM-5.4-03** | Pre-flight / CI policy for env-gated integration tests | **Low** | Document when `requires_botpress` / `requires_wondercraft` runs (nightly vs local). |
| **REM-6.1-01** | Resolve duplicate AC: scripts vs guidance-only | **High** | Canonical: no SCORM **scripts** unless new story; update duplicate text to match Cora. |
| **REM-6.1-02** | WCAG verification evidence model | **Medium** | Require completed checklist artifact path or link in run envelope; forbid vague “verified.” |
| **REM-6.1-03** | Close 6.1 or list gaps | **High** | If Cora + refs + sidecar + test guide satisfy AC, mark **done** and list any missing WCAG reference file if absent. |

---

## 4. References (canonical story text)

- Epic 5 rebaseline + Stories **5.1**, **5.4**: `epics.md` ~L1868–L1913  
- Epic 6 rebaseline + Story **6.1**: `epics.md` ~L1916–L1937  
- Sprint keys: `5-1-expanded-tool-specialist-agents`, `5-4-remaining-tier2-api-integrations`, `6-1-coursearc-specialist-agent` in `sprint-status.yaml`

---

*End of report.*
