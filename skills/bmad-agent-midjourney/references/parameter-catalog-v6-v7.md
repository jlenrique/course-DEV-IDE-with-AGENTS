# Midjourney v6/v7 Parameter Catalog

Core parameters to tune in prompt specs:

- --ar (aspect ratio)
- --style (style strength)
- --chaos (variation spread)
- --stylize (stylization intensity)
- --seed (repeatability)
- --no (hard exclusions)
- --sref (style reference)
- --cref (character reference)

Guidance:

1. Use fixed seed for iterative review loops.
2. Use --no aggressively for prohibited artifacts (watermarks, labels, extra hands, etc.).
3. Use conservative chaos for medical visuals that require structure.
4. For comparative batches, vary one parameter at a time.
