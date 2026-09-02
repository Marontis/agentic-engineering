---
name: agentic-data-cracking
description: >
  How to adaptively structure unstructured data as a byproduct of
  agent reasoning, turning repeated document reads into cheap database
  lookups.  Covers cracking sub-agents, speculative structuring,
  and cost-accuracy trade-offs.
  Derived from "Token-Efficient Data Reasoning Agents" (arXiv:2608.31082).
---

# Agentic Data Cracking

Use this skill when building agents that repeatedly reason over
unstructured documents and you want to amortize the cost of
document reading across queries.

## When to Use

- Your agent answers multiple questions over the same document corpus
- Each question requires opening and reading large documents
- Token costs are a concern (millions of tokens per complex question)
- You want the system to get cheaper with use, not stay flat

## Core Insight

Agents that reason over unstructured data (PDFs, reports, web pages)
pay the full document-reading cost on every query.  But if the data
were already structured, the same query reduces to a cheap database
lookup.  **Agentic data cracking** structures data adaptively —
as a byproduct of reasoning itself — so that future queries are
progressively cheaper.

**Evidence**: On FanOutQA, reasoning over an ideal pre-structured
store is 28× cheaper.  Agentic data cracking achieves 53% cost
reduction while preserving accuracy, and runs 9× cheaper at the
10th percentile of per-question savings.

## Procedure

### Step 1: Identify the cracking opportunity

When the agent opens a document to answer a query, it loads the
full document context.  This is the cracking window — the document
is already in context, and extracting structured facts costs marginal
additional tokens.

### Step 2: Fork a cracking sub-agent

When the main agent opens a document:

1. Fork a cracking sub-agent from the same loaded context
2. The sub-agent extracts grounded structured facts (entities,
   relations, attributes) that are likely to serve future queries
3. Store extracted facts in a structured store (database, KG)

The cracking sub-agent operates at **marginal cost** because the
expensive document loading is already paid for by the main query.

### Step 3: Speculative extraction

The cracking sub-agent should extract beyond what the current query
needs:

- If the query asks about company X's revenue, also extract
  employee count, founding date, and other attributes visible
  in the same document
- If the query asks about character A's actions in chapter 3,
  also extract actions of characters B and C from the same chapter

The speculation is that related queries will follow.  Over-extraction
is cheap (marginal tokens); under-extraction means paying full
document-reading cost again later.

### Step 4: Query routing

For each incoming query:

1. **Check the structured store first**: Can the query be answered
   from already-extracted facts?
2. **If yes**: Answer from the store (cheap database lookup)
3. **If no**: Fall back to full document reading, and crack new
   structure while you're at it

Over time, an increasing share of queries hit the structured store
and skip document reading entirely.

### Step 5: Store schema evolution

Don't pre-define the schema.  Let it emerge from the queries:

- Early queries establish the initial entity types and relations
- Later queries may require new attributes or relations
- The schema evolves with the workload, not ahead of it

## Environment Caveats

- **Single-query workloads**: If each document is queried only once,
  cracking provides no amortization benefit.  The overhead of the
  sub-agent is pure cost.
- **Highly heterogeneous documents**: If every document has completely
  different structure, speculation is less effective because future
  queries are unpredictable.
- **Real-time requirements**: The cracking sub-agent adds latency to
  the first query.  If the first response must be fast, run cracking
  asynchronously.
- **Document updates**: If source documents change, the structured
  store becomes stale.  Implement invalidation based on document
  modification timestamps.

## Failure Modes

- **Hallucinated structure**: The cracking sub-agent may extract
  "facts" that aren't actually in the document.  Require source
  citations for every extracted fact.
- **Schema explosion**: Speculative extraction without constraints
  can produce an enormous, unwieldy schema.  Set limits on
  extraction breadth per document.
- **Stale cache**: Answers from the structured store may be outdated
  if the source documents have been updated.  Version-track the
  source-to-store mapping.

## Cross-References

- [`rag-evidence-triage`](../rag-evidence-triage/SKILL.md) —
  Evidence triage determines whether retrieved evidence is sufficient;
  data cracking ensures that evidence is pre-structured for cheap retrieval
- [`knowledge-compounding-loop`](../knowledge-compounding-loop/SKILL.md) —
  Both patterns accumulate knowledge over time; cracking focuses on
  structured facts, compounding on procedural knowledge

## Sources

- Token-Efficient Data Reasoning Agents via Adaptive Structuring of Unstructured Data (arXiv:2608.31082)
