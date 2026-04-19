# Tracy Postures and Contracts

Tracy is a research agent that wraps retrieval.dispatcher to provide three postures for lesson plan enhancement: embellish, corroborate, and gap-fill. Each posture has a four-part contract defining input shape, output shape, success signal, and failure mode.

## Postures

### Embellish
**Purpose:** Add enrichment content to existing lesson plan elements.

**Input Shape:** Enrichment request with target element (plan_unit or event) and enrichment type (examples, analogies, background context).

**Output Shape:** Enrichment content structured as markdown sections with citations.

**Success Signal:** Content added to target element with provenance markers.

**Failure Mode:** No enrichment found - returns empty content with "no enrichment available" message.

### Corroborate
**Purpose:** Confirm or disconfirm claims using supporting/contrasting/mentioning classification from scite.ai.

**Input Shape:** Claim to verify with source context.

**Output Shape:** Evidence assessment with cross-references and confidence score.

**Success Signal:** Evidence found with classification (supporting/contrasting/mentioning).

**Failure Mode:** No evidence found - returns "insufficient evidence" with search terms used.

### Gap-Fill
**Purpose:** Fill knowledge gaps identified in lesson plan analysis.

**Input Shape:** Gap description with required content type and scope.

**Output Shape:** Filler content with sources and relevance score.

**Success Signal:** Gap filled with content meeting scope requirements.

**Failure Mode:** Gap cannot be filled - returns "gap unfillable" with reason.

## Contract Enforcement

All postures must:
- Use retrieval.dispatcher as the underlying mechanism
- Include provenance tracking for all sources
- Handle failure modes gracefully without breaking lesson flow
- Maintain operator-memory framing alignment (enrichment/gap-filling/evidence-bolster)