# Drift-Aware LLM Routing with Sparse Contexts and Shared Budgets

> **Paper**: [Drift-Aware LLM Routing with Sparse Contexts and Shared Budgets](https://arxiv.org/abs/2609.00662)
> **Praxis source**: src:2609-00662v1

## Why Not a Skill?

Model routing and scheduling infrastructure pattern for production inference platforms, not an agent workflow skill.

---

## Core Concept

Production LLM portfolios contain diverse models (small local, frontier reasoning, specialized code). Routing queries across these models is non-stationary: query distributions drift over time, models undergo silent updates, and all requests share finite GPU, latency, and token budgets.

### Key Finding

Rolling sparse routing policies with contextual bandit meters retain 97–98% of clairvoyant optimal policy utility while remaining feasible under shared resource budgets, outperforming frozen offline routers when environment shifts occur.

## Relevance to Praxis

- Complements policy-centroid-routing with shared token and latency budget constraints.
- Informs multi-model routing architectures for cost-efficient agent pipelines.
