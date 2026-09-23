# AkasicMEM: Governed Enterprise Memory for Agents

**Source**: Bae et al., "AkasicMEM: Governed Enterprise Memory for Agents"
(arXiv:2609.25563), Sep 2026.

## Key Findings

- Defines "Governed Enterprise Memory" as agent memory designed around
  three combined targets: source–memory integration, memory governance,
  and authorization continuity
- Authorization continuity: source restrictions remain effective
  throughout source-to-memory and memory-to-memory derivation chains
- Realized through transitive lineage, policy composition during memory
  formation, and policy re-evaluation during retrieval
- Built on AkasicDB (unified vector–graph–relational database) for
  joint optimization of lineage, policy, and retrieval operations

## Relevance to Agentic Engineering

AkasicMEM extends the governed knowledge graph pattern with a critical
insight: information that persists in memory across derivation chains
can bypass source restrictions. Authorization continuity via transitive
lineage is the key defensive property. Directly relevant to any agent
memory system that ingests from governed enterprise sources.

## Why Not a Skill?

Database-specific implementation (AkasicDB) with tightly coupled
storage and execution substrate. The authorization continuity concept
is the transferable insight, but the implementation requires specific
infrastructure. Better captured as a rule contribution to the governed
knowledge graph patterns.

> Source: arXiv:2609.25563
