# Interstitial Brief Specification Standard

**Purpose:** This document defines the strict contract for interstitial briefs sent to Gary during cluster production. Interstitials are supporting slides that remove, isolate, enlarge, or simplify content from the head slide rather than introducing new imagery or concepts. This standard ensures Gamma receives constrained, coherent instructions that preserve head-slide lineage.

**Scope:** Applies to all cluster interstitial briefs in C1M1 MVP and future cluster implementations. This is the authoritative contract that Gary dispatch work (Epic 21) and cluster narration (Epic 23) must honor.

## Required Brief Fields

Every interstitial brief must specify all six fields with concrete, actionable values. Vague or missing fields render the brief unusable.

### 1. `interstitial_type`
**Acceptable Values:** "isolate", "remove", "enlarge", "simplify", "reframe"

**Intent:** Specifies the primary visual operation to perform on head slide content.

**Quality Bar:** Must be one of the enumerated operations, not generic terms like "improve" or "enhance".

**Failure Example:** "Make it better" - too vague, allows Gamma to add decorative elements.

### 2. `isolation_target`
**Acceptable Values:** Specific string description of element/concept from head slide (e.g., "the central diagram", "the key equation", "process step 3").

**Intent:** Identifies the exact content from the head slide to focus on.

**Quality Bar:** Must point to actual content present in the head brief or head slide concept.

**Failure Example:** "The important part" - generic, doesn't specify which element.

### 3. `visual_register_constraint`
**Acceptable Values:** String list of specific elements to remove/suppress/deemphasize (e.g., "remove background text", "suppress secondary icons").

**Intent:** Defines what must be eliminated to achieve the interstitial's purpose.

**Quality Bar:** Must list specific elements, not vague instructions.

**Failure Example:** "Clean it up" - doesn't specify what to remove.

### 4. `content_scope`
**Acceptable Values:** "minimal" (1-2 elements), "focused" (3-4 elements), "reduced" (simplified head version).

**Intent:** Limits maximum on-screen content burden.

**Quality Bar:** Must specify scope level, preventing overcrowding.

**Failure Example:** Undefined - allows unlimited elements, defeating interstitial purpose.

### 5. `narration_burden`
**Acceptable Values:** "high" (visuals carry most meaning), "medium" (balanced), "low" (narration carries most meaning).

**Intent:** Determines visual-audio explanatory division.

**Quality Bar:** Must specify balance to guide slide design.

**Failure Example:** Unspecified - leaves visual-audio balance ambiguous.

### 6. `relationship_to_head`
**Acceptable Values:** "zoom" (closer view), "isolate" (extract element), "simplify" (remove distractions), "reframe" (different angle), "rest" (complementary view).

**Intent:** Describes interstitial's role in cluster sequence.

**Quality Bar:** Must specify relationship, ensuring coherent progression.

**Failure Example:** "Continue the topic" - doesn't define the specific relationship.

## Interstitial Principles

- **Lineage Preservation:** Interstitials transform existing head content; they do not introduce new concepts, imagery, or iconography.
- **Simplification Focus:** Operations are subtractive (remove/isolate) or focused (enlarge/simplify/reframe), not additive.
- **Pedagogical Intent:** Each interstitial must serve a clear explanatory purpose in the cluster sequence.

## Examples

### Pass/Fail Examples by Type

#### Isolate Type
**Pass:** `interstitial_type: "isolate"`, `isolation_target: "the central workflow diagram"`, `visual_register_constraint: ["remove surrounding text", "suppress title"]`, `content_scope: "minimal"`, `narration_burden: "high"`, `relationship_to_head: "zoom"`

**Fail:** `interstitial_type: "isolate"`, `isolation_target: "the good stuff"`, `visual_register_constraint: ["make it nice"]` - target too vague, constraints generic.

#### Remove Type
**Pass:** `interstitial_type: "remove"`, `isolation_target: "the detailed process steps"`, `visual_register_constraint: ["eliminate step 2-4 details", "remove supporting icons"]`, `content_scope: "reduced"`, `narration_burden: "medium"`, `relationship_to_head: "simplify"`

**Fail:** `interstitial_type: "remove"`, `isolation_target: "everything confusing"` - target not specific to head content.

#### Enlarge Type
**Pass:** `interstitial_type: "enlarge"`, `isolation_target: "the key equation"`, `visual_register_constraint: ["remove all other text"]`, `content_scope: "minimal"`, `narration_burden: "high"`, `relationship_to_head: "zoom"`

**Fail:** `interstitial_type: "enlarge"`, `isolation_target: "something important"` - target not concrete.

#### Simplify Type
**Pass:** `interstitial_type: "simplify"`, `isolation_target: "the complex diagram"`, `visual_register_constraint: ["remove labels", "suppress colors"]`, `content_scope: "focused"`, `narration_burden: "low"`, `relationship_to_head: "reframe"`

**Fail:** `interstitial_type: "simplify"`, `visual_register_constraint: ["add clarity"]` - constraint not subtractive.

#### Reframe Type
**Pass:** `interstitial_type: "reframe"`, `isolation_target: "the process overview"`, `visual_register_constraint: ["change layout to vertical", "remove timeline"]`, `content_scope: "reduced"`, `narration_burden: "medium"`, `relationship_to_head: "reframe"`

**Fail:** `interstitial_type: "reframe"`, `isolation_target: "the slide"` - target too broad.

### C1M1 MVP Example

**Head Slide Context:** C1M1 slide showing a complex agent interaction diagram with multiple components, labels, and connecting arrows.

**Interstitial Brief:**
- `interstitial_type`: "isolate"
- `isolation_target`: "the central agent communication loop"
- `visual_register_constraint`: ["remove all component labels", "suppress peripheral agents", "eliminate connecting arrows"]
- `content_scope`: "minimal"
- `narration_burden`: "high"
- `relationship_to_head`: "zoom"

**Purpose:** Focuses Storyboard A review on the core interaction pattern without visual overload, helping viewers understand the fundamental communication mechanism before adding complexity in subsequent slides.

## Implementation Contract

This standard is binding for:
- Gary dispatch contract extensions (Epic 21)
- Cluster coherence validation (Epic 21)
- Irene Pass 2 narration integration (Epic 23)
- All future cluster implementations

Any deviation requires explicit approval and standard updates.