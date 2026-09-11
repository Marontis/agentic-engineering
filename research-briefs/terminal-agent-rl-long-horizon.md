# T1: Terminal Agent Reinforcement Learning for Long-Horizon Tasks

> **Paper**: [T1](https://arxiv.org/abs/2609.11042)
> **Praxis source**: `src:2609-11042v1`

## Why Not a Skill?

RL training method â€” architecture-specific training approach for terminal-based agent tasks. The procedure is tightly coupled to the reward model and training infrastructure.

---

## Core Concept

Trains terminal agents (command-line agents) using RL with task-specific reward shaping for long-horizon tasks. The key challenge is credit assignment across 50+ sequential tool calls where early actions (e.g., environment setup) don't produce immediate rewards but are critical for later success.

### Key Insight

Long-horizon terminal tasks require hierarchical reward decomposition â€” rewarding sub-goal completion at intermediate checkpoints rather than only at task completion.

## Relevance to Praxis

- Relevant to the `reference-trajectory-harness-evolution` skill â€” reference trajectories could serve as intermediate reward signals
- Connects to agent benchmark design for terminal/CLI agents
