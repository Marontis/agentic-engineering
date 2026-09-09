# Building a Research-Software Catalog with a Coding Agent

> **Paper**: [Building a research-software catalog with a coding agent: from hackathon prototype to public deployment](https://arxiv.org/abs/2609.04711)
> **Praxis source**: src:2609-04711

## Why Not a Skill?

This is an experience report documenting lessons from deploying a coding-agent-built research software catalog. It provides valuable qualitative observations about coding agent failure modes but no standalone transferable procedure—the findings are descriptive rather than prescriptive.

---

## Core Concept

The paper describes developing a research software repository catalog during a three-day hackathon using coding agents, then examining the engineering required for public deployment: adversarial review, data-quality checks, browser-level validation, and publication safeguards. A retrieval agent for the MateriApps portal combines curated metadata, external documentation, vector search, and local LLM generation. Implementation with coding agents was rapid, but reliable operation required substantial additional engineering.

### Key Finding

- **Primary Result**: The most consequential problems with coding-agent-built systems were **not crashes but silent failures** that produced plausible yet incomplete or incorrect outputs—arising from incomplete data acquisition, misleading assessments, and retrieval/preprocessing failures.
- **Secondary Result**: Rapid prototyping with coding agents (3-day hackathon) is viable, but the gap between "working prototype" and "reliable public deployment" requires adversarial review, data-quality validation, and browser-level testing that the agent does not naturally produce.

## Relevance to Praxis

- **Silent failure taxonomy**: The "plausible but incorrect output" failure mode is the same pattern documented in the `harness-tampering-audit` and `counterexample-guided-repair` skills. Reinforces the need for behavioral verification beyond surface-level checks.
- **Agent-to-production gap**: Quantifies the engineering gap between agent-generated prototypes and production-ready systems—relevant to any workflow using agents for code generation.
- **Retrieval agent architecture**: The metadata + vector search + local LLM generation pattern for the MateriApps retrieval agent is similar to Praxis's own hybrid search architecture.
