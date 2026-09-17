# EvoOntology: A Self-Evolving Ontology Layer for Data Agents

> **Paper**: [EvoOntology: A Self-Evolving Ontology Layer for Data Agents](https://arxiv.org/abs/2609.15779)
> **Praxis source**: `src:2609-15779v1`
> **Primary topic**: Agent Architecture, Protocols & Interoperability / Self-Improvement

## Why Not a Skill?

EvoOntology describes an end-to-end ontology infrastructure and MCP server implementation for enterprise data querying. Because it requires setting up a tripartite MCP server and paired evaluation pipelines across database backbones, it constitutes an architectural pattern rather than an isolated subtask skill.

---

## Core Concept

Data agents must fulfill natural language analytical instructions over heterogeneous data stores (SQL databases, tabular spreadsheets, file collections). They face a persistent **agent-data gap**: the data lives externally in diverse formats, and agents can only inspect it through generic exploratory tools (like `SELECT * LIMIT 5` or file head commands). Manually authored semantic layers in prompts are brittle and fail to scale to large schemas.

**EvoOntology** introduces an autonomous, self-evolving semantic layer encapsulated as a standard **Model Context Protocol (MCP)** server:

```
┌────────────────────────────────────────────────────────┐
│                   Data Agent Pipeline                  │
└───────────────────────────▲────────────────────────────┘
                            │ MCP Tools & Resources
┌───────────────────────────▼────────────────────────────┐
│              EvoOntology MCP Server                    │
│  ├── Schema Layer (Entities, Relations, Constraints)   │
│  ├── Content Layer (Value Profiles, Embeddings, Gloss) │
│  └── Tool Layer (Domain-Specific SQL & Query Shims)    │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────┐
│              Autonomous Self-Evolution Loop            │
│  ├── Builder Agent: Initial schema & graph synthesis   │
│  ├── Attribution Analysis: Pinpoints failed queries    │
│  └── Paired Evaluation Gate: Accepts typed edits only   │
│      if benchmark accuracy improves on target LLM      │
└────────────────────────────────────────────────────────┘
```

### Key Components & Findings

- **MCP Standardization**: Encapsulating the ontology inside an MCP server enables seamless integration with standard agent harnesses without requiring custom API clients.
- **Attribution-Guided Typed Edits**: When an agent query fails due to ambiguous column aliases, missing join paths, or semantic terminology mismatches, the builder agent applies typed edits (e.g., `AddSynonym`, `DefineJoinConstraint`, `AddDerivedMetric`).
- **Backbone-Conditional Paired Evaluation**: Edits are tested against a validation set using the target LLM backbone. Proposed mutations are committed only if they provide a net positive delta, preventing regression.
- **Benchmark Evaluation**: Across three standard data-agent benchmarks with four LLM backbones, EvoOntology consistently outperforms static semantic layers and zero-shot exploration.

## Relevance to Praxis

- Provides a clean reference model for building self-evolving MCP servers.
- Connects directly to [`mcp-server-design`](../skills/mcp-server-design/SKILL.md) and [`governed-knowledge-graph`](../skills/governed-knowledge-graph/SKILL.md).
- Demonstrates attribution-guided gated commit criteria for persistent knowledge layers.
