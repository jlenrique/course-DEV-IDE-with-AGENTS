# Interstitial Cluster MVP - C1M1 Storyboard A Plan

Status: Draft for execution
Date: 2026-04-11
Source: Party Mode working consensus on `epics-interstitial-clusters.md`
Testbed: C1M1, part 1 of the APC course project, using the existing production-proven presentation path as baseline

## Objective

Prove that interstitial slide clusters improve narrated-slide production quality for a real lesson before extending the workflow downstream.

This MVP does **not** try to complete the full clustered production pipeline. It proves the first meaningful product shape:

- one real presentation
- exactly 3 clusters
- clear beginning, middle, and end
- output stopped and judged at **Storyboard A**

Storyboard B, clustered narration, and downstream assembly remain locked until Storyboard A passes human review.

## BMAD Workflow Framing

This planning pass is intentionally staged to preserve design quality and implementation order:

1. Design the cluster contract and planning logic.
2. Implement the minimum C1M1 three-cluster planning and dispatch path.
3. Evaluate the result at Storyboard A with an explicit HIL gate.
4. Only then authorize Storyboard B and later downstream work.

The first bottleneck is not downstream narration. It is **Irene's cluster production plan for Gamma**.

## MVP Scope

### Included Epic 19-21 stories

The first Storyboard-A MVP includes:

- `19.1` Segment Manifest Cluster Schema Extension
- `19.2` Gary Dispatch Contract Extensions
- `19.3` only for **cluster-aware G2/G3 carve-outs** needed by the MVP
- `19.4` Validator Hardening for Cluster-Aware Payloads
- `20a.1` Cluster Decision Criteria
- `20a.2` Interstitial Brief Specification Standard
- `20a.3` Cluster Narrative Arc Schema
- `20a.4` Operator Cluster Density Controls
- `20b.1` Irene Pass 1 Cluster Planning Implementation
- `20b.2` Cluster Plan Quality Gate (G1.5)
- `21.1` Visual Design Constraint Library
- `21.2` Cluster-Aware Prompt Engineering
- `21.3` Cluster Dispatch Sequencing
- `21.4` Cluster Coherence Validation (G2.5)

### Deferred from the MVP

These stay out of the first Storyboard-A spike:

- `20a.5` Retrofit Exemplar Library
- `20b.3` Narration Script Parameters Extension for Clusters
- `21.5` Interstitial Re-dispatch Protocol
- all of `Epic 22`
- all of `Epic 23`
- all of `Epic 24`
- double-dispatch for clustered runs
- generalized multi-presentation learning or optimization

## Why This Slice

This is the minimum end-to-end set that can answer the real question:

Can Irene produce a coherent three-cluster plan for C1M1, and can Gary realize it into a visually coherent Storyboard A that improves pacing over the current flat-slide pattern?

Everything deferred is either:

- downstream consumption of the clusterized artifact,
- recovery/hardening for a pattern not yet proven, or
- reference-building that is useful but not necessary for the first proof.

## Storyboard-A MVP Definition

The MVP run must produce:

- one C1M1 clustered presentation candidate
- exactly 3 clusters
- each cluster contains 1 head slide and 1-3 interstitials
- the 3-cluster sequence functions as beginning, middle, and end
- all cluster outputs are reviewable in **Storyboard A**

The MVP stops here. No Storyboard B work begins until the Storyboard A gate passes.

## Human Review Gate for Storyboard A

Storyboard A passes only if all of the following are true:

### 1. Structural completeness

- Exactly 3 clusters are present.
- Each cluster has one clear head slide.
- Each cluster has the planned 1-3 interstitials.
- The overall sequence reads as beginning, middle, and end rather than three disconnected mini-decks.

### 2. Cluster logic quality

- Each interstitial only reveals, emphasizes, simplifies, or reframes content already present in the head slide.
- No interstitial introduces a new concept that the head slide did not establish.
- Each cluster has a visible internal arc rather than repeated restatement.

### 3. Visual coherence

- Head and interstitials within a cluster read as one visual family.
- Palette, typography, background treatment, and composition remain coherent within the cluster.
- No cluster shows obvious decorative drift, random style breaks, or invented visual motifs detached from the head.

### 4. Pacing improvement

- The visual rhythm improves the current static-slide dwell problem.
- Visual changes feel earned by the concept, not triggered by a timer alone.
- The presentation feels easier to follow, not more fragmented.

### 5. Skim test

- A reviewer can skim the clustered storyboard without narration and still understand the intended conceptual progression.
- If the reviewer has to mentally reconstruct missing intent, the cluster plan fails.

### 6. Gamma-plan fidelity

- The resulting visuals map cleanly back to Irene's cluster brief.
- Isolation targets, suppression rules, and cluster boundaries are visible in the output.
- Major invention, omission, or style drift fails the gate.

## Go/No-Go Rule

### Go to Storyboard B only if:

- Storyboard A passes all review criteria above
- the reviewer judges the pacing improvement to be obvious
- the reviewer judges the three-cluster sequence to be structurally and pedagogically usable

### No-Go to Storyboard B if:

- any cluster is bloated, repetitive, or visually incoherent
- any interstitial behaves like decoration instead of progressive disclosure
- the three-cluster arc does not read as beginning, middle, and end
- the reviewer must compensate for weak cluster logic by interpretation

## Immediate Next BMAD Step

Convert this MVP scope into execution-ready story work for the included `19.x`, `20a.x`, `20b.x`, and `21.x` items only, then select the specific three cluster candidates inside C1M1 for the first run.
