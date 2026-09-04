# Potential-Guided Policy Optimization (PGPO) for Multi-Turn Agents

> **Paper**: [PGPO: Potential-Guided Policy Optimization for Multi-Turn Agentic Tasks](https://arxiv.org/pdf/2609.02236)
> **Praxis source**: src:2609-02236

## Why Not a Skill?

Reinforcement learning post-training objective modifying model parameters. The core principle of intermediate credit assignment across failed trajectories informs agent evaluation and reflection rules in `rules/recursive-improvement.md`.

---

## Core Concept

Group-based RL for agents (e.g., GRPO, GiGPO) often fails in multi-turn environments with sparse terminal rewards due to "failure-side credit degeneracy": all actions in a failed trajectory inherit negative returns, even if early actions were optimal. PGPO estimates empirical state potentials from anchor-state groups across rollouts and computes step-level advantages from potential differences between adjacent states, enabling cross-trajectory credit propagation.

### Key Finding

Evaluating on ALFWorld and WebShop, PGPO significantly outperforms existing group-based RL algorithms by successfully isolating valid exploratory steps inside failed trajectories from the fatal mistake step.

## Relevance to Praxis

- Directly mirrors the key-step monitoring principle: an agent system must not penalize all actions in a failed trajectory equally, but should isolate the point of failure from valid prerequisite actions.
