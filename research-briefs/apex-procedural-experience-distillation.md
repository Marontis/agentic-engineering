# APEx: Distillation of Agent Procedural Experience for Deep Research

> **Paper**: [APEx: Distillation of Agent Procedural Experience for Adaptive Deep Research Question Answering](https://arxiv.org/abs/2609.02253)
> **Praxis source**: src:2609-02253v1

## Why Not a Skill?

End-to-end multi-agent deep research architecture coupled with a 3-stage alternating GRPO training paradigm. The core skill extraction principles align with `procedural-family-skill-consolidation`.

---

## Core Concept

Deep research agents operate over long horizons requiring multi-step tool orchestration and multi-source synthesis. Storing verbose raw interaction traces bloats context, while fixed prompt skills fail to adapt to downstream tasks. APEx introduces a hierarchical experience architecture:
1. **Instance-level trajectory memories**: Storing specific past retrieval successes.
2. **Category-level procedural skills**: Abstract solving guidelines.
3. **Executor-Distiller-Planner closed loop**: Optimized via alternating GRPO, using distilled skills as priors for test-time reinforcement learning with skill-alignment regularization to prevent policy drift.

### Key Finding

On seven complex research benchmarks, APEx surpasses GPT-5.4 by **14.7 points** and outperforms the strongest memory-augmented agent baseline by **3.0 points**.

## Relevance to Praxis

- Validates the two-tier skill hierarchy (abstract procedural skills + localized trajectory context) as the optimal representation for long-horizon research agents.
