---
name: governed-knowledge-graph
description: >
  How to build knowledge graphs with explicit governance — provenance
  tracking, domain ownership, admission review, and audit metadata.
  Covers the MAGG multi-agent framework for governed KG construction.
  Derived from "From Extraction to Governed Memory" (arXiv:2608.28642).
---

# Governed Knowledge Graph Construction

Use this skill when building knowledge graphs for agentic systems
and you need every fact to have provenance, ownership, and a
governance decision.

## When to Use

- Your agent system uses a knowledge graph and you can't trace
  where facts came from
- You need to know who owns each fact and why it was admitted
- You're building a multi-agent system where different agents
  contribute knowledge and you need quality control
- You want to route queries to domain-specific experts rather
  than searching the entire graph

## Core Insight

Knowledge graphs for agentic systems are typically treated as flat
stores of extracted triples — no record of who owns a fact, why it
was admitted, or how it should be used.  **Governed knowledge graphs**
add an explicit governance layer: every triple has provenance,
an owner, a review decision, and audit metadata.

**Evidence**: On SciERC, governed construction (MAGG) improves strict
triple F1 by 47% and mapped triple F1 by 51% over flat insertion.
In a blinded review of 120 triples, governed-only triples are more
often source-supported, and revised triples are supported in 100%
of cases.

## Procedure

### Step 1: Induce entity and relation types from content

Don't use a fixed schema.  Let the domain classifier discover entity
types and relation types directly from the document content:

1. Feed document text to a domain classifier agent
2. The classifier proposes entity types (Person, Organization,
   Method, Metric, etc.) and relation types (authored_by, uses,
   outperforms, etc.)
3. These become the schema for this domain

This enables operation in **open-world settings** without
pre-defining what types of knowledge to extract.

### Step 2: Extract candidate triples

From each source document, extract candidate (subject, predicate,
object) triples:

- Each triple must cite its source span in the document
- Each triple includes a confidence score from the extractor
- Triples are candidates, not admitted facts

### Step 3: Assign domain ownership

Route each candidate triple to a domain owner:

- Domain owners are specialized agents (or humans) responsible
  for a knowledge area
- A triple about "model accuracy on SWE-bench" goes to the
  "evaluation" domain owner
- A triple about "HTTP interception architecture" goes to the
  "security" domain owner

Ownership determines who reviews and who answers queries about
this knowledge.

### Step 4: Review against supporting evidence

The domain owner reviews each candidate triple:

1. **Check source support**: Does the cited source span actually
   support this triple?
2. **Check consistency**: Does this triple contradict existing
   knowledge in the graph?
3. **Decide**: Admit, revise, or reject

Store the decision with audit metadata: who reviewed, when,
what evidence was cited, what the original extraction was.

### Step 5: Store with governance metadata

Every admitted triple is stored with:

| Metadata Field | Purpose |
|:--------------|:--------|
| **Source document** | Where this fact came from |
| **Source span** | The specific text that supports it |
| **Domain owner** | Who is responsible for this fact |
| **Reviewer** | Who admitted it |
| **Review decision** | Admitted, revised, or rejected |
| **Confidence** | Extraction confidence score |
| **Timestamp** | When it was admitted |
| **Version** | For tracking updates |

### Step 6: Query routing via domain experts

When answering queries:

1. Classify the query into one or more domains
2. Route to the domain-specific subgraph
3. The domain expert answers from its owned subgraph
4. This avoids the "undifferentiated retrieval" problem where
   the system searches everything and returns noise

## Environment Caveats

- **Single-agent systems**: Even without multiple agents, the
  governance pattern (provenance + review) prevents the graph
  from accumulating unsourced or contradictory facts.
- **High-volume ingestion**: If you're ingesting thousands of
  documents, consider batch review with sampling rather than
  reviewing every triple individually.
- **Evolving domains**: When new domains emerge from new
  documents, the system must create new domain owners dynamically.

## Failure Modes

- **Review bottleneck**: If every triple requires human review,
  the pipeline stalls.  Automate review for high-confidence
  triples and flag only low-confidence or contradictory ones.
- **Domain misrouting**: If triples are routed to the wrong
  domain owner, they may be incorrectly rejected or admitted
  without proper expertise.
- **Provenance loss**: If source spans aren't preserved, the
  governance metadata becomes meaningless — you can't verify
  the decision after the fact.

## Cross-References

- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) —
  Compounding accumulates procedural knowledge; governance ensures
  the accumulated knowledge is trustworthy
- [`skill-evolution-defense`](../skill-evolution-defense/SKILL.md) —
  Skill provenance validation is a specific case of the general
  governance pattern for knowledge admission

## Sources

- From Extraction to Governed Memory: Multi-Agent Knowledge Graph Construction with Domain-Expert Review (arXiv:2608.28642)
