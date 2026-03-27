# Gary — image model notes (pilot: C1M1 physician innovator)

## `recraft-v4-svg` (attempt 2 — 2026-03-27)

- **Outcome:** Visually interesting and polished; team liked the quality in isolation.
- **Client alignment:** Does **not** match the **client-approved look and feel** (flat vector editorial / APC reference screenshot).
- **Disposition:** **Shelf for other projects** where vector-forward or Recraft’s aesthetic is on-brief — not the default for this client’s brand-locked decks.

## Attempt 3

- **Model:** `flux-2-pro` (menu option **F**), with strict flat-vector `imageOptions.style` + `additionalInstructions` to counter Flux’s photoreal bias.
- **Outcome:** Again **very strong** visually — but still **not** the client-approved APC exemplar look.
- **Disposition:** **Note for reuse** on briefs where Flux editorial fits; **not** the default for this client until matched to exemplar UI.
- **Artifacts:** `v3-flux-2-pro/` (PNG zip + extracted `png/`), Gamma doc https://gamma.app/docs/z3m2pde2pa6hpi5 — **78 credits** deducted (run zdNGiNhBvvKPttO6JqmhJ).

## Client exemplar (ground truth)

Screenshot-captured **exact** Gamma UI settings are recorded in:

`CLIENT_EXEMPLAR_GAMMA_SETTINGS.md`

**Headline differences vs attempts 1–3:** exemplar uses **`textMode: condense`**, **minimal text**, **`recraft-v3`** (not v4 SVG), and **Line drawing** art style — not `generate` + `flux-2-pro` / `recraft-v4-svg`.

## Attempt 4 (API run matched to exemplar controls)

- **Settings:** `textMode: condense`, `textOptions.amount: brief`, `textOptions.language: en`, `themeId: njim9kuhfnljvaa`, `imageOptions.model: recraft-v3`, `imageOptions.style` = explicit line-drawing brief (UI tile “Line drawing” may use an internal preset ID — compare visually to exemplar).
- **Artifacts:** `v4-exemplar-aligned-recraft-v3/` — Gamma https://gamma.app/docs/oz0jooxmkdwqx6r — **150 credits** (generation `jnjWAjKxUdV97uEZHajya`).
- **Purpose:** First pass using **same control mix as client screenshot**; Gate 2 decides if line-art preset needs in-app tweak or different `imageOptions.style` string.
