# Gamma image model menu — flat / editorial illustration (Gary)

**Client-approved exemplar (APC / HIL):** see **`CLIENT_EXEMPLAR_GAMMA_SETTINGS.md`** — **Recraft V3** + **Line drawing** + **Condense** + **Minimal text** + theme **2026 HIL APC**.

Use with `imageOptions.source: "aiGenerated"` and `imageOptions.model: "<string>"`.

**Target look (Juanl reference):** flat vector, editorial “corporate-medical,” cool navy / ice blue / white, simple clinician figure, abstract tech UI — **not** photorealistic, **not** 3D, **not** painterly.

## Gary’s recommended order for this aesthetic

| Pick | Model string | Credits/img | Why |
|------|----------------|-------------|-----|
| **A (default retry)** | `recraft-v4-svg` | 40 | **Vector output** — closest to clean flat illustration systems. |
| **B** | `recraft-v3-svg` | 40 | Same family; slightly different rendering. |
| **C** | `ideogram-v3-quality` | 45 | Strong typography-adjacent graphics; good for “designed” slides. |
| **D** | `ideogram-v3-turbo` | 10 | Faster/cheaper; flatter than default auto-pick, less “photo.” |
| **E** | `imagen-4-fast` | 10 | Often clean and restrained; can still skew realistic — pair with strict `imageOptions.style`. |
| **F** | `flux-2-pro` | 8 | General quality; use only with very explicit “flat vector only” style string. |

**Avoid for this brief (unless experimenting):** `dall-e-3`, `gpt-image-*`, photoreal-leaning Flux Max — tend toward wrong illustration genre.

**Omit `model`:** Gamma auto-selects (what likely produced the “wrong style” pass).

---

**Style line (paste into `imageOptions.style` or `additionalInstructions`):**

`Flat vector editorial illustration only: clean geometric shapes, limited palette navy cerulean ice blue white light gray, no photorealism no 3D no painterly brushstrokes, professional medical corporate-tech look, simple stylized clinician figures abstract monitors and data lines like modern editorial infographics.`

---

**Reference asset (human + Marcus):** workspace `assets/c__Users_juanl_AppData_Roaming_Cursor_User_workspaceStorage_e9704733d6441caf77330101e4df18be_images_image-f35d4890-e49c-498b-84fc-78b2f62dab9a.png` — use for eyeball comparison at Gate 2; Gamma API text generation cannot ingest local file without a public URL.
