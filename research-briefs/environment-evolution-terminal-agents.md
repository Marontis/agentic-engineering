# Environment Evolution for Terminal Agents

> **Paper**: [Environment Evolution for Terminal Agents](https://arxiv.org/abs/2609.04128)
> **Praxis source**: `src:2609-04128`

## Why Not a Skill?

This paper introduces an offline training-time environment synthesis harness and multi-turn reinforcement learning curriculum rather than an inference-time operational procedure for coding agents.

---

## Core Concept

Interactive environments with verifiable execution feedback are the cornerstone of training terminal coding agents. However, static benchmarks quickly saturate, while on-policy co-evolution methods (synthesizing tasks near the agent's current failure frontier) suffer from narrow distribution shift and fail to generalize as frontier models advance.

**Environment Evolution** addresses this limitation by systematically increasing environment difficulty **off-policy** along three formal evolution directions derived from the multi-turn learning objective:
1. **State Space Complexity**: Increasing filesystem depth, dependency trees, and noisy artifact interference.
2. **Action Horizon & Branching Factor**: Expanding required sequential command chains and intermediate tool choices.
3. **Verification Strictness**: Enhancing test suite sensitivity to detect surface-level symptom suppression and partial implementations.

These evolved environments are scheduled generation-by-generation during long-horizon RL training through a loop-engineered multi-agent harness.

### Key Findings

- **Consistent Hardness Scaling**: Rollout evaluations with Hy4 preview, Claude Opus 5, and GPT-5.6 Sol verify that the three evolution vectors reliably scale environment difficulty without producing unsolvable or ill-posed tasks.
- **Substantial Benchmark Gains**: Simple long-horizon RL fine-tuning on evolved environments improved Qwen3.6-27B by **14.4 percentage points** and Qwen3.6-35B-A3B by **18.0 percentage points** on the rigorous Terminal-Bench 2.1 benchmark.

---

## Relevance to Praxis

- Provides concrete axes for structuring agent evaluation sandboxes and synthetic benchmark generation.
- Reinforces that multi-step coding agent harnesses must evaluate long-horizon tool execution against deep environmental state rather than shallow single-file edits.
