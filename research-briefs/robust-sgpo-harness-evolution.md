# RobustSGPO: Search-Space Control for Agent Harness Evolution

> **Paper**: [RobustSGPO](https://arxiv.org/abs/2609.09646)
> **Praxis source**: `src:2609-09646v1`

## Why Not a Skill?

Analysis â€” provides search-space control strategies for harness evolution but the procedures are too tightly coupled to the SGPO framework to transfer as a standalone skill.

---

## Core Concept

Agent harness evolution (automatically improving the agent's scaffolding, prompts, and tools) can diverge if the search space is too large. RobustSGPO constrains the search space through structural controls: limiting which components can evolve simultaneously, bounding mutation magnitude, and requiring monotonic improvement on held-out tasks.

### Key Insight

Unconstrained harness evolution is worse than no evolution â€” the search space is too large and the agent regresses. Constraints make evolution tractable without eliminating beneficial mutations.

## Relevance to Praxis

- Complements the `reference-trajectory-harness-evolution` skill â€” RobustSGPO adds search-space controls
- Connects to the `stable-skill-evolution` skill â€” both address stability during iterative improvement
