# Source Reference Grammar (`source_ref`)

Defines the syntax and resolution rules for `source_ref` provenance annotations used across all artifact schemas in the APP pipeline.

## Format

```
{filename}#{path_expression}
```

### `filename`

Relative path from project root to the source artifact file.

Examples:
- `course-content/staging/ad-hoc/source-bundles/trial2-macro-trends/extracted.md`
- `lesson-plan.md` (short form when the file is in the same production context)

### `path_expression`

One of three forms:

| Form | Syntax | Example | Resolution |
|------|--------|---------|-----------|
| **Heading hierarchy** | `Section > Subsection > ...` | `Chapter 2 > Knowledge Check > Item 3` | Match top-level heading, then sub-heading, then sub-sub-heading. `>` is the delimiter. |
| **Line range** | `L{start}-L{end}` | `L45-L62` | Extract lines start through end (inclusive, 1-based). Stable within a versioned artifact. |
| **Heading anchor** | `## Heading Text` | `## Macro Trends Overview` | Match the markdown heading with that exact text. |

### Combined examples

```
extracted.md#Chapter 1 > Macro Trends Overview
lesson-plan.md#Block 3
slide-brief.md#Slide 7
narration-script.md#seg-04
```

## Resolver specification

```python
def resolve_source_ref(source_ref: str, base_path: str) -> tuple[str, str]:
    """Parse and resolve a source_ref string.

    Args:
        source_ref: The source_ref string (e.g., "extracted.md#Chapter 2 > Knowledge Check")
        base_path: Base directory for resolving relative filenames.

    Returns:
        (resolved_content_slice, confidence) where confidence is "exact" | "approximate" | "broken"
    """
```

Resolution rules:
1. Split on first `#` — left side is filename, right side is path expression
2. Resolve filename relative to `base_path`
3. If file not found → return `("", "broken")`
4. Parse path expression by form:
   - If starts with `L` and matches `L\d+-L\d+` → line range extraction
   - If starts with `#` → heading anchor search
   - Otherwise → heading hierarchy, split on ` > ` and match top-down
5. If expression matches → return `(content_slice, "exact")`
6. If partial match → return `(best_match, "approximate")`
7. If no match → return `("", "broken")`

Implementation deferred to Story 2A-8 (cumulative drift tracking).

## Evidence retention

When the Fidelity Assessor resolves a `source_ref`, the resolved content slice is captured in the Fidelity Trace Report as:

```yaml
evidence:
  source_ref: "extracted.md#Chapter 2 > Knowledge Check"
  resolved_source_slice: "The 10 knowledge check topics are: 1. Digital transformation..."
  output_slice: "Topics covered: Digital transformation, Workforce evolution..."
  resolution_confidence: "exact"
  comparison_result: "omission"  # 3 of 10 topics missing
```

This creates a self-contained, auditable comparison record.

## Provenance chain

A `source_ref` from any downstream artifact can be traced backward:

```
Segment manifest seg-03.source_ref → lesson-plan.md#Block 3
  Slide brief Slide 5.source_ref → lesson-plan.md#Block 3
    Lesson plan Block 3.source_ref → extracted.md#Chapter 2 > Knowledge Check
      Source bundle → Original SME materials
```

Maximum hops from any artifact to the original source: **3**.
