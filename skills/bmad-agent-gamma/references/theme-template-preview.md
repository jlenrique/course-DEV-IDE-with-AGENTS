# Theme/Template Preview (TP Capability)

Before generating any slide or deck, Gary can present available Gamma themes and registered project templates to the user (via Marcus) for selection. This ensures visual style alignment before credits are spent on generation.

**When to invoke TP:**
- `theme_selection_required: true` in context envelope (Marcus explicitly requests it)
- `deck_mode: true` with no `theme_id` specified (default for deck generation — themes matter more for multi-slide visual consistency)
- Interactive mode when the user asks "what themes are available?" or "let me pick a look"
- Any first production run for a new course or module (establish visual vocabulary)

**When NOT to invoke TP:**
- `parameters_ready: true` (fast-path — theme already decided)
- `template_id` already in envelope (user already specified)
- Woodshed/exemplar reproduction (uses precise parameter control, never templates)
- Rapid iteration where Gary is re-running with known parameters

---

## TP Workflow

### Step 1 — Fetch Available Themes

Invoke the `list_themes_and_templates` operation in `gamma-api-mastery`:

```python
# Via gamma-api-mastery skill:
# list_themes_and_templates(scope=module_lesson, content_type=content_type)
# Returns: themes (from API) + registered templates (from style_guide.yaml registry)
```

This combines:
- **Gamma API themes** — `GammaClient.list_themes()` → live themes from the user's Gamma account
- **Registered project templates** — `state/config/style_guide.yaml` → `tool_parameters.gamma.templates` registry, filtered by scope and content type

### Step 2 — Present to Marcus/User

Present in two sections:

**Registered Templates (if any match current scope + content type):**
```
📋 Registered Templates for {scope} / {content_type}:

1. [{template_name}] — {description}
   Scope: {scope} | Content type: {content_type}
   Gamma ID: {gamma_id}
   ✅ RECOMMENDED — best match for current scope

2. [Global fallback: {template_name}] — {description}
   Scope: * (all courses)
   Gamma ID: {gamma_id}
```

**Available Gamma Themes:**
```
🎨 Available Gamma Themes:

1. [{theme_name}] — {description or visual style summary}
   ID: {theme_id}
   ✅ RECOMMENDED — closest to JCPH brand palette

2. [{theme_name}] — {description}
   ID: {theme_id}

... (top 5-8 themes, most brand-relevant first)
```

Gary's recommendation with reasoning:
```
🎯 My recommendation: [{template_name}] registered template because it encodes the JCPH brand
visual standards and has been validated for this content type. If no template is registered,
I recommend [{theme_name}] theme as the closest match to the style bible palette.

Would you like to use the recommended option, choose from the list, or proceed without
a specific theme (Gary will use style guide defaults)?
```

### Step 3 — Capture Selection

Store the user/Marcus selection:
- If template selected: set `template_id` in parameters → route to from-template endpoint
- If theme selected: set `theme_id` in parameters → include in generation call
- If no selection: proceed with style guide defaults (Gary applies color/typography via `additionalInstructions`)

### Step 4 — Proceed with Generation

With theme/template resolved, proceed to standard generation flow (PR → SG merge → invoke → QA → return).

---

## Recommendation Logic

Gary ranks themes by brand alignment:

1. **First priority:** Registered templates in `style_guide.yaml` for the current scope/content type — these encode institutional visual standards
2. **Second priority:** Gamma themes with color palette closest to JCPH Navy (#1B2A4A) and Medical Teal (#2E8B8C)
3. **Third priority:** Clean, minimal themes suitable for data-rich medical content
4. **Avoid:** Consumer/casual themes, dark-on-dark palettes, heavy decorative elements

When no theme strongly matches, Gary recommends proceeding without `theme_id` and controlling visual style via `additionalInstructions` (color palette, font choices, layout constraints) — this is often more reliable than forcing an ill-fitting theme.

---

## Registering a New Template

When a successful generation uses a theme the user wants to reuse, Gary suggests saving it:

"This deck worked well with the [theme_name] theme — want me to register it for future [content_type] slides in [scope]? I'd add it to the template registry so it's always recommended for this context."

Registration: add entry to `state/config/style_guide.yaml` → `tool_parameters.gamma.templates` with scope, content_type, gamma_id, and description. Save via `production-coordination` → `manage_style_guide.py`.
