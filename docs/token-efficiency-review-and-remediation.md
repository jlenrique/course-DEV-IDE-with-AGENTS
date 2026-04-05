# Token Efficiency: Review & Remediation Prescription

> Reference prompt for IDE-resident agents and human operators.
> Source: Nate's Newsletter analysis ("Your Claude Sessions Cost 10x What They Should"), expanded with transcript detail and applied to this project's measured footprint.
> Last measured: 2026-04-02.

---

## Why This Matters Now

The next generation of frontier models (Claude Mythos, GPT next, Gemini next) will be **significantly more expensive** because they are trained on next-generation chips (NVIDIA GB300 series). Pricing could move from the current Opus range ($5 in / $25 out per million tokens) to potentially $50 in / $250 out — a 10x increase.

**Your mistakes scale with the price of intelligence.** Habits that cost $8 today could cost $80 on the next model. The "ambient compute" layer (cheap, capable-enough models) will be the smaller models. If you want cutting-edge reasoning, you must stop burning tokens on waste and spend them on actual work.

Real-world proof this is solvable: a production AI pipeline that ingests multiple long-form conversations per user, runs analysis across dozens of dimensions, and generates fully personalized output on the most expensive models available — **costs less than $0.25 per user.** Frontier AI is absurdly cheap when you know what you're doing. The models are not expensive. Your habits are.

---

## The Core Problem

Every Claude Code session loads context **before you type a single character**: system prompt, CLAUDE.md, skill manifests, MCP tool schemas, deferred tool lists, memory files, and git status. In a project this size, that overhead is substantial — and every follow-up message re-sends the full conversation history plus that base context.

**Rough token math** (1 token ~ 4 bytes of English text):

| Context Source | Bytes | Est. Tokens | Loads When |
|---------------|------:|------------:|------------|
| System prompt + model instructions | ~12,000 | ~3,000 | Every message |
| Parent CLAUDE.md | 5,945 | ~1,500 | Every message |
| Skill manifest (56 SKILL.md summaries in system prompt) | ~8,000 | ~2,000 | Every message |
| Deferred tool list (~60+ tools: MCP + built-in) | ~4,000 | ~1,000 | Every message |
| Git status snapshot | ~500 | ~125 | Every message |
| Memory (MEMORY.md + files) | ~600 | ~150 | Every message |
| **Baseline per-message overhead** | **~31,000** | **~8,000** | **Always** |

And that's *before* any conversation content, tool results, or file reads.

---

## The Four Levels of Token Waste

### Level 1: Rookie — Document Ingestion

The most wasteful and easiest to fix. Dragging three PDFs into a conversation — even modest ones at 1,500 words each (4,500 words total) — can produce **100,000+ tokens** because the model processes the raw binary structure: headers, footers, embedded fonts, layout metadata, the entire binary encoding.

**The fix is trivial:** Convert to markdown first. Those same 4,500 words become 4,000–6,000 tokens in clean markdown. That's a **20x savings** on input alone. And it compounds — those 100,000 tokens ride in your conversation history for every subsequent turn, bouncing back and forth, filling your context window.

**Screenshots are equally wasteful.** An image token-encoded is far more expensive than the text it contains. Copy-paste the text. Convert to markdown. Always.

Markdown conversion options:
- Ask Claude to convert the document in a separate quick session
- Use any free web-based markdown converter
- Use a dedicated file-transform plugin or skill
- The key principle: file formats are designed to be *human-readable*, not *AI-readable*. Strip away everything the model doesn't need.

### Level 2: Intermediate — Conversation Sprawl

If you're doing 20, 30, 40 turns on a single conversation, **no AI was trained or designed to handle that sprawl.** You're compressing the ratio where original instructions live, filling the context window with cruft, and wasting tokens re-transmitting everything.

**Separate your two modes:**
- **Research mode:** Gather information, explore, iterate. This might span multiple models (Grok for social sentiment, ChatGPT thinking mode for reports, Perplexity for research, Claude Opus for targeted web search). Each is a separate conversation. The goal is to arrive at clarity.
- **Execution mode:** You have all the context needed. You bring it to one focused session. The instruction is so clear the AI just goes and does the work. **Your objective should be to be so clear that the AI needs to do nothing else.**

Do not mix these modes. That is how you burn tokens and confuse the model. When you need a long-evolving exchange, mark it explicitly at the top ("our goal is to evolve and reach a conclusion together"), keep it light, and end with "please summarize this" — then take the summary to a fresh execution session.

**Models drift over long conversations.** The number of people who keep conversations going forever is highly correlated with those who experience symptoms of "LLM psychosis" — degraded coherence and instruction-following. Start fresh every 10–15 turns.

### Level 3: Intermediate-Advanced — Plugin and Connector Tax

Every plugin, connector, MCP server, and skill you have enabled loads into your context window before you type. One user shared they were **over 50,000 tokens in before typing a single word** because of loaded plugins and connectors.

**The workshop analogy:** It's like walking into a fully-equipped workshop and instead of leaving tools on the walls, you pull every single one off and lay them all on the workbench before deciding what to build. You probably need 5 tools, not 200.

We hear about a new plugin, add it because it's cool, and forget it's there. It becomes a **barnacle on the ship** — silently burning 1,000–2,000 tokens on every conversation forever, confusing the model about which tools to use, and degrading performance.

**Audit your plugins regularly.** If you enabled Google Drive months ago and never use it — drop it. If you have MCP servers configured that you only use once a month — disable them for daily work.

### Level 4: Advanced — Large-Project Architecture Mistakes

If you're technical enough to manage system prompts, agent architectures, and GitHub repos, you have the most leverage *and* the most expensive mistakes — hundreds of thousands to millions of tokens when you get it wrong.

**The key insight for 2026:** As models get more intelligent, you should be **leaning out your context window.** In 2025, dumber models needed heavy front-loading of context. In 2026, smarter models retrieve better on their own. Let the gains in model intelligence reduce your context overhead.

If you haven't pruned your system prompt in weeks — do it now. If lines have been there since GPT-3.5 era — remove them. If you're loading an entire repo into context "because it seemed to work two generations ago" — test whether you still need to. This is preparation for the next model generation.

---

## Six Diagnostic Questions (The Stupid Button)

These are the six questions from Nate's diagnostic tool. Answer honestly — each "yes" is a remediation target.

### Q1: Are you feeding raw PDFs, images, or screenshots when all you need is text?

**The waste:** Raw PDF binary encoding can inflate 4,500 words of content to 100,000+ tokens. Screenshots are similarly expensive compared to the text they contain.

**Remediation:**
- Convert everything to markdown before ingestion. Always. No exceptions.
- If you need to reason about visual styling of a PDF, keep the original. 99% of the time you just want the text.
- Use the source-wrangler skill or any markdown converter — this should take 10 seconds.
- In Claude Code: use `Read` tool for files (it handles format efficiently). Never paste raw content.

### Q2: When was the last time you started a fresh conversation?

**The waste:** Every turn re-sends the entire conversation. A 30-turn conversation on Opus with accumulated context can run 800,000–1,000,000 input tokens with 150,000–200,000 output tokens. That's **$8–$10 of compute** for one session.

**The clean alternative:** Same work, but convert docs to markdown first, start fresh every 10–15 turns, tier your model usage, and scope context to what's needed. Result: 100,000–150,000 input tokens, 50,000–80,000 output tokens. **Cost: ~$1.** Same output, 8–10x cheaper.

**Remediation:**
- One session, one objective. Use file-based handoff (next-session-start-here.md, SESSION-HANDOFF.md) instead of keeping the conversation alive.
- When a session is getting long, ask for a summary, then start fresh.
- **Scaling math:** Sloppy user = $40–50/week in compute. Clean user = $5–7/week. Across a 10-person team on API: $2,000/month vs $250/month for the same results. On subscription plans: the difference between hitting daily limits and forgetting limits exist.

### Q3: Are you using the most expensive model for everything?

**The waste:** Using Opus or GPT Pro mode for formatting, proofreading, or simple transformations when Sonnet or Haiku would produce identical results at a fraction of the cost.

**Remediation — tier your model usage:**
- **Opus/frontier:** Reasoning, complex analysis, architecture decisions, novel problem-solving
- **Sonnet/mid-tier:** Execution, code implementation, structured generation
- **Haiku/small:** Formatting, proofreading, simple transformations, classification
- Don't bring a Ferrari to the grocery store.

### Q4: Do you know what's loading in context before you type?

**The waste:** Tens of thousands of tokens in plugins, connectors, MCP servers, skills, and system prompt content you've accumulated and never audited. One person had 50,000+ tokens loaded before typing.

**Remediation:**
- In Claude Code: check the system-reminder tags in conversation start — they list every loaded MCP, skill, and deferred tool.
- Audit: for each plugin/connector/MCP server — when did you last actually use it? If you can't remember, disable it.
- Think of unused plugins as barnacles on a ship. They slow you down, burn tokens, and may confuse the model about which tools to use.

**This project's measured load:**
- 56 skills in manifest (~2,000 tokens/message)
- 3 MCP servers, ~79 tools (~1,000 tokens/message)
- These ride along on *every single message* whether you use them or not

### Q5: (API/Production) Are you caching stable context?

**The waste:** Prompt caching gives a **90% discount** on repeated content. Cache hits on Opus cost $0.50/million vs $5/million standard. If your system prompt, tool definitions, and reference documents aren't cached — you're paying 10x what you should on every call.

**Remediation:**
- Cache everything stable: system prompts, tool definitions, persona instructions, reference material.
- For agent architectures making thousands of calls/day, this is the lowest-effort, highest-impact optimization available.
- This is not advanced technique in 2026. It should be default practice.

### Q6: How are you handling web search?

**The waste:** Letting Claude do web research natively tends to be expensive in tokens. A dedicated search MCP (e.g., Perplexity) can save **10,000–50,000 tokens per search**, be 5x faster, and provide structured citations.

**Remediation:**
- Use dedicated search MCPs for research-heavy sessions rather than native model search.
- The larger principle: any operation that can be handled by a cheaper specialized service should be — don't pay frontier-model token prices for commodity search.

---

## Five KISS Commandments for Agents

For anyone building or operating agentic systems — these are million-token decisions.

### 1. Index your references

If an agent is receiving raw documents instead of relevant chunks, you've already failed. The entire point of retrieval is to scope what the model sees to what it needs. Dumping a full document set into the window on every agent call is irresponsible. Don't make the agent do work it doesn't need to do.

**In this project:** When Marcus delegates to specialists, the context envelope should contain only what the specialist needs, not the full project state.

### 2. Prepare context for consumption

Pre-process, pre-summarize, pre-chunk. A reference document should arrive in an agent's context **ready to be used**, not ready to be read or processed. If the model's first several thousand tokens of reasoning are spent dealing with badly pre-processed input, you're wasting the most expensive part of the pipeline.

**In this project:** The distillator skill exists for this. Source-wrangler produces extracted.md bundles. Use them — don't feed raw HTML or full Notion pages to agents.

### 3. Cache your stable context

System prompts, tool definitions, persona instructions, reference material — anything stable should be cached. At a 90% discount on cache hits, this is the lowest-effort, highest-impact optimization on the table. If you're making thousands of agent calls a day without caching, you're pouring money away.

### 4. Scope every agent's context to the minimum it needs

A planning agent does not need your full codebase. An editing agent doesn't need your project roadmap. Passing everything to every agent is **architectural laziness** with real costs — both in tokens burned and in degraded agent performance. Models perform worse when drowning in irrelevant context.

If you're unsure what the agent will need — give it a **searchable, pre-processed repository** so it can retrieve the relevant slice on demand. Don't dump everything in hoping the model sorts it out.

**In this project:** The lane-matrix.md defines what each agent owns and explicitly what they don't. Respect those boundaries in context loading too.

### 5. Measure what you burn

If you don't know your per-call token cost, you're optimizing blind. Instrument your agent calls. Track input tokens, output tokens, model mix, and cost ratio. You cannot improve what you do not measure.

Most teams building agentic systems focus on semantic correctness and system prompt optimization. They don't think about model cost because at current prices, the per-run cost doesn't make or break the project. **Plan for a world where models are more expensive.** Plan for scale. Instrument now.

---

## Project-Specific Audit: This Repo

### Finding 1: 1.7MB of skill files (287 markdown files across 56 skills)

Skills are loaded on-demand (only when invoked), but the **skill manifest** listing all 56 skills is injected into the system prompt of every message (~2,000 tokens). When a skill is invoked, its workflow.md + step files load into context (3,000–15,000 tokens per skill).

**Remediation options:**
- Audit whether all 56 skills are needed in every session. Planning-phase skills (bmad-create-prd, bmad-create-ux-design, bmad-create-architecture) could be disabled during production operations. The project is past phase 4 — many of these skills won't fire again.
- The top 10 skills by size account for ~1MB. Be intentional about which skills you invoke — don't invoke heavy exploratory skills in a session that's already deep.

### Finding 2: 3 MCP servers = ~79 advertised tools

Gamma (3 tools), Canvas LMS (54 tools), and Notion (22 tools) contribute ~79 tool names to every system prompt. Most sessions don't use Canvas or Notion tools at all.

**Remediation options:**
- For sessions focused on storyboard/content work, Canvas and Notion tools are noise. Consider MCP server profiles or disabling unused servers in `.mcp.json` for specific session types.
- Deferred tool schemas help (loaded only on call) but tool *names* still ride along in every message.

### Finding 3: Session protocol files are large

The production session start protocol reads 3 large context files (project-context.md, agent-environment.md, next-session-start-here.md) plus sprint-status.yaml and bmm-workflow-status.yaml — easily **15,000–20,000 tokens** loaded in the first few messages.

**Remediation options:**
- Now that all epics are complete, create a compact "operations-only" context file that replaces the full project-context.md for production sessions. The 200-line implementation history isn't needed for content runs.
- The bmm-workflow-status.yaml key_decisions section is 96 lines of historical decisions. Distill to a 10-line summary now that the project is stable.
- The session startup protocol itself could offer a "lite" mode that skips planning-artifact scans when the session objective is pure operations.

### Finding 4: Model tiering opportunity

This project currently defaults to a single model for all work. Production content runs, code review, file reads, and formatting all hit the same model tier.

**Remediation options:**
- Use Opus for reasoning-heavy work (architecture decisions, complex debugging, agent orchestration).
- Use Sonnet for execution (code implementation, structured generation, most session work).
- Use Haiku for polish (formatting, proofreading, simple classification).
- Claude Code supports model switching mid-session via `/model`.

---

## The Compounding Effect: A Concrete Example

**Sloppy session (same work):**
- Raw PDFs fed into context: ~100,000 tokens
- 30-turn conversation sprawl on Opus
- No model tiering
- 5-hour session result: ~800,000–1,000,000 input tokens, ~150,000–200,000 output tokens
- **Cost: $8–$10**

**Clean session (same work):**
- Documents converted to markdown: ~5,000 tokens
- Fresh conversations every 10–15 turns
- Opus for reasoning, Sonnet for execution, Haiku for polish
- Context scoped to what's needed
- Same result: ~100,000–150,000 input tokens, ~50,000–80,000 output tokens
- **Cost: ~$1**

**That's 8–10x savings per session.** Scale it:
- Sloppy user: $40–50/week
- Clean user: $5–7/week
- 10-person team on API: $2,000/month vs $250/month

**On next-gen pricing (estimated 10x current):**
- Sloppy: $80–100 per session
- Clean: $8–10 per session
- The gap becomes business-critical.

---

## Quick Reference: Token Cost Intuitions

| Action | Approximate Token Cost |
|--------|----------------------:|
| Your 10-word prompt | ~15 tokens |
| System overhead per message | ~8,000 tokens |
| Reading a 200-line file | ~1,500 tokens |
| Reading a 600-line file | ~4,500 tokens |
| Grep returning 50 matches | ~2,000 tokens |
| Agent subagent (isolated) | 0 in your context (paid separately) |
| Claude's 100-word response | ~150 tokens |
| Invoking a BMad skill (workflow.md + steps) | 3,000–15,000 tokens |
| Full session protocol startup | ~20,000 tokens |
| 30-message session history | ~100,000–200,000 tokens |
| Raw PDF (1,500 words) | ~30,000–50,000 tokens |
| Same content as markdown | ~2,000–3,000 tokens |
| Perplexity MCP search vs native | Saves 10,000–50,000 per search |
| Prompt cache hit (Opus) | $0.50/M vs $5/M (90% discount) |

---

## Periodic Audit Checklist

Run this quarterly (or when onboarding a new model generation):

- [ ] **Skills audit:** List all installed skills. Disable any not used in current project phase.
- [ ] **MCP/plugin audit:** List all configured servers and connectors. Disable any not used weekly.
- [ ] **CLAUDE.md audit:** How many lines? Can historical sections be archived to a reference file?
- [ ] **Memory audit:** Prune stale entries. Are old project memories still accurate?
- [ ] **System prompt audit:** Has the system prompt grown? Are there instructions from earlier model generations that smarter models no longer need?
- [ ] **Session protocol audit:** Can startup file reads be reduced? Are large context files still needed in full, or can they be distilled?
- [ ] **Anti-drift doc sync audit:** Ensure `production-prompt-pack-v4.1.md`, `trial-run-pass2-artifacts-contract.md`, `fidelity-gate-map.md`, and operator cards/checklists are aligned on Gate 6B and Storyboard A/B checkpoints.
- [ ] **Model tiering review:** Are you using the right model tier for each task type?
- [ ] **Caching review (API/production):** Is all stable context cached? Are you getting cache hits?

---

## The Cultural Principle

Burning tokens is not a badge of honor. Token consumption will go up — that's inevitable and desirable. The goal is **smart tokens, not more tokens.** Be bold and audacious about what you aim AI at. But be efficient about how you fuel it. Don't spend frontier-model prices on document conversion that markdown handles for free. Spend those tokens on the work that actually requires intelligence.

> "The models are not expensive. It's your habits that cost a lot."
