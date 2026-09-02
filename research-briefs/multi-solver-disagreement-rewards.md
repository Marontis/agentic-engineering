# Beyond Uncertainty: Multi-Solver Disagreement Rewards for Self-Evolving Reasoning Curricula

> **Paper**: [Beyond Uncertainty: Multi-Solver Disagreement Rewards for Self-Evolving Reasoning Curricula](https://arxiv.org/abs/2608.30035)
> **Praxis source**: `src:2608-30035v1`

## Why Not a Skill?

Training procedure â€” tied to RL curriculum generation with specific model training architecture. Not a transferable subtask for agent engineering.

---

## Core Concept

Uses disagreement between multiple solver models as a reward signal for curriculum generation. Problems where solvers disagree get higher reward, automatically driving the training curriculum toward appropriately challenging problems. This creates a self-evolving difficulty curve without human curriculum design.

## Relevance to Praxis

- The disagreement-as-difficulty signal is analogous to how the iterative-instruction-refinement skill identifies which instructions need improvement
- Relevant to the self-improving-agent.spec template's curriculum design section
