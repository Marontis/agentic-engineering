# AgentFactory: Automated Agentic System Design and Optimization

> **Paper**: [AgentFactory: Towards Automated Agentic System Design and Optimization](https://arxiv.org/abs/2609.01045)
> **Praxis source**: src:2609-01045v1

## Why Not a Skill?

Meta-optimization system that automates the generation and tuning of multi-agent topologies and model assignments, rather than a reusable coding procedure.

---

## Core Concept

Manual design of multi-agent systems (defining roles, communication graphs, and assigning models) is labor-intensive and sub-optimal. AgentFactory formalizes automated workflow discovery under real-world deployment constraints (accuracy, latency, token cost).

### Key Finding

Optimizing workflow topologies and model selection jointly explores a significantly richer solution space than fixed multi-agent frameworks (e.g., MetaGPT, ChatDev), producing architectures that achieve frontier-level task performance while reducing inference costs by delegating subtasks to specialized smaller models.

## Relevance to Praxis

- Informs dynamic multi-agent collaboration topologies.
- Emphasizes that role profiles and communication structures should be adapted to task difficulty and resource budgets.
